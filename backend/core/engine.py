"""
Module: core/engine.py

WorkflowExecutionEngine — orchestrates multi-agent workflow execution via
LangGraph.  Converts visual graph definitions into executable StateGraphs,
streams execution events with full observability, and integrates the
supervisor planning layer so every run starts with a structured plan.

Architecture
------------
* ``WorkflowExecutionEngine`` is a single-responsibility class; planning is
  delegated to ``PlannerService`` from ``core.planning``.
* The supervisor node creates a plan *before* routing to agents — plan records
  are persisted via ``stores.plan_create / plan_task_add``.
* All agent activity is recorded via ``stores.audit_log``.
* LLM calls are routed through ``BaseLLMAdapter`` subclasses — never raw HTTP
  calls inside this module.
"""

from __future__ import annotations

import asyncio
import logging
import operator
import time
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Annotated, Any, TypedDict
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph

from backend.api.stores import (
    agent_get,
    agent_list,
    audit_log,
    plan_create,
    plan_task_add,
    plan_task_update,
    run_create,
    run_update,
    span_create,
    span_update,
)
from backend.core.config import get_settings
from backend.core.planning.planner import PlannerService

logger = logging.getLogger(__name__)


def _now() -> str:
    """Return current UTC time as ISO-8601 string."""
    return datetime.now(UTC).isoformat()


class AgentState(TypedDict):
    """Mutable LangGraph state passed between nodes.

    Attributes:
        messages: Accumulated conversation messages.
        next_node: Routing hint for conditional edges.
        results: Keyed results from each node.
        intent: Supervisor-determined intent string.
        assigned_to: ID of the agent chosen by the supervisor.
        subtasks: Optional subtask breakdown from the plan.
        plan_id: ID of the supervisor plan created for this run.
    """

    messages: Annotated[list[BaseMessage], operator.add]
    next_node: str | None
    results: dict[str, Any]
    intent: str | None
    assigned_to: str | None
    subtasks: list[dict[str, Any]] | None
    plan_id: str | None


def _mark_task(plan_id: str, step_number: int, task_status: str) -> None:
    """Update a plan task status by step number.

    Args:
        plan_id: Plan UUID.
        step_number: Step number to update.
        task_status: New status string.
    """
    try:
        from backend.api.stores import plan_task_list as _ptl
        tasks = _ptl(plan_id)
        for task in tasks:
            if task.get("stepNumber") == step_number:
                plan_task_update(plan_id, task["id"], {"status": task_status})
                return
    except Exception as exc:
        logger.debug("_mark_task plan_id=%s step=%d error=%s", plan_id, step_number, exc)


class WorkflowExecutionEngine:
    """Orchestrates multi-agent workflow execution via LangGraph.

    Responsibilities:
    - Building and compiling LangGraph state graphs.
    - Running supervisor planning before routing.
    - Streaming execution events for SSE consumption.
    - Recording audit events for every significant action.
    """

    def __init__(self) -> None:
        """Initialise the engine with settings and planner."""
        self.settings = get_settings()
        self._pending_approvals: dict[str, asyncio.Event] = {}
        self._approval_decisions: dict[str, bool] = {}
        self._planner = PlannerService.from_settings()

    async def run(
        self,
        workflow_id: str,
        initial_input: str,
        config: dict[str, Any] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Execute the standard supervisor workflow with planning.

        Args:
            workflow_id: Identifier of the workflow definition.
            initial_input: Raw user input text.
            config: Optional run config (threadId, userId).

        Yields:
            SSE-compatible event dicts.
        """
        cfg = config or {}
        run_id: str = str(cfg.get("threadId") or uuid4())
        user_id: str = str(cfg.get("userId", "anonymous"))

        run_create({
            "runId": run_id, "workflowId": workflow_id, "userId": user_id,
            "status": "running", "startedAt": _now(), "totalTokens": 0,
        })
        audit_log({
            "actorType": "human", "actorId": user_id,
            "action": "run.started", "resourceType": "run", "resourceId": run_id,
            "details": {"workflowId": workflow_id, "inputLen": len(initial_input)},
            "outcome": "success",
        })

        try:
            plan_id = await self._create_plan(
                goal=initial_input, run_id=run_id, user_id=user_id, workflow_id=workflow_id,
            )
            yield {"type": "plan_created", "runId": run_id, "planId": plan_id, "timestamp": _now()}

            graph = self._build_supervisor_graph(run_id, workflow_id, user_id, plan_id)
            start = time.time()
            async for node_name, node_output in self._stream_graph(graph, initial_input, run_id):
                yield {
                    "type": "node_end", "runId": run_id, "nodeName": node_name,
                    "data": node_output, "timestamp": _now(),
                }
                for msg in node_output.get("messages", []):
                    if isinstance(msg, AIMessage):
                        yield {
                            "type": "message", "runId": run_id, "nodeName": node_name,
                            "message": msg.content, "timestamp": _now(),
                        }

            elapsed = int((time.time() - start) * 1000)
            run_update(run_id, {"status": "complete", "endedAt": _now(), "durationMs": elapsed, "planId": plan_id})
            audit_log({
                "actorType": "system", "actorId": run_id, "action": "run.completed",
                "resourceType": "run", "resourceId": run_id,
                "details": {"durationMs": elapsed, "planId": plan_id}, "outcome": "success",
            })
            yield {"type": "complete", "runId": run_id, "timestamp": _now()}

        except Exception as exc:
            logger.exception("engine=run_failed run_id=%s", run_id)
            run_update(run_id, {"status": "failed", "endedAt": _now(), "error": str(exc)})
            audit_log({
                "actorType": "system", "actorId": run_id, "action": "run.failed",
                "resourceType": "run", "resourceId": run_id,
                "details": {"error": str(exc)}, "outcome": "failure",
            })
            yield {"type": "error", "runId": run_id, "message": str(exc), "timestamp": _now()}

    async def run_visual_workflow(
        self,
        graph_definition: dict[str, Any],
        initial_input: str,
        config: dict[str, Any] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Execute a user-defined visual workflow graph.

        Args:
            graph_definition: Serialised visual workflow from the builder.
            initial_input: Raw user input text.
            config: Optional run configuration.

        Yields:
            SSE-compatible event dicts.
        """
        cfg = config or {}
        run_id: str = str(cfg.get("threadId") or uuid4())
        user_id: str = str(cfg.get("userId", "anonymous"))
        workflow_id: str = str(graph_definition.get("id", "visual"))

        run_create({
            "runId": run_id, "workflowId": workflow_id, "userId": user_id,
            "status": "running", "startedAt": _now(), "totalTokens": 0,
        })
        audit_log({
            "actorType": "human", "actorId": user_id,
            "action": "visual_run.started", "resourceType": "run", "resourceId": run_id,
            "details": {"workflowId": workflow_id}, "outcome": "success",
        })

        try:
            graph = self._compile_visual_graph(graph_definition, run_id, workflow_id, user_id)
            start = time.time()
            async for node_name, node_output in self._stream_graph(graph, initial_input, run_id):
                yield {
                    "type": "node_end", "runId": run_id, "nodeName": node_name,
                    "data": node_output, "timestamp": _now(),
                }
                for msg in node_output.get("messages", []):
                    if isinstance(msg, AIMessage):
                        yield {
                            "type": "message", "runId": run_id, "nodeName": node_name,
                            "message": msg.content, "timestamp": _now(),
                        }
            elapsed = int((time.time() - start) * 1000)
            run_update(run_id, {"status": "complete", "endedAt": _now(), "durationMs": elapsed})
            yield {"type": "complete", "runId": run_id, "timestamp": _now()}

        except Exception as exc:
            logger.exception("engine=visual_run_failed run_id=%s", run_id)
            run_update(run_id, {"status": "failed", "endedAt": _now(), "error": str(exc)})
            yield {"type": "error", "runId": run_id, "message": str(exc), "timestamp": _now()}

    def approve(self, thread_id: str, approved: bool) -> None:
        """Resume a paused human-approval checkpoint.

        Args:
            thread_id: Run/thread identifier.
            approved: True to approve, False to reject.
        """
        self._approval_decisions[thread_id] = approved
        event = self._pending_approvals.get(thread_id)
        if event:
            event.set()

    async def _create_plan(
        self, goal: str, run_id: str, user_id: str, workflow_id: str,
    ) -> str:
        """Create a supervisor plan for the given goal.

        Args:
            goal: User's raw goal text.
            run_id: Associated run ID.
            user_id: Originating user ID.
            workflow_id: Associated workflow ID.

        Returns:
            Created plan ID string.
        """
        agents = [a for a in agent_list() if a.get("status") == "active"]
        try:
            decomposition = await self._planner.plan(goal, agents)
        except Exception as exc:
            logger.warning("planner=failed reason=%s run_id=%s", exc, run_id)
            from backend.core.planning.planner import RuleBasedPlanner
            decomposition = await RuleBasedPlanner().decompose(goal, agents)

        plan = plan_create({
            "goal": goal, "userId": user_id, "workflowId": workflow_id, "runId": run_id,
            "status": "approved", "reasoning": decomposition.reasoning,
            "estimatedDurationMinutes": decomposition.estimated_duration_minutes,
            "steps": [s.title for s in decomposition.steps],
            "autoGenerated": True,
        })
        plan_id: str = plan["id"]

        for step in decomposition.steps:
            plan_task_add(plan_id, {
                "title": step.title, "description": step.description,
                "stepNumber": step.step_number, "assignedTo": step.assigned_id,
                "assignedType": step.assigned_type, "dependsOn": step.depends_on,
                "status": "pending",
            })

        audit_log({
            "actorType": "system", "actorId": run_id, "action": "plan.auto_created",
            "resourceType": "plan", "resourceId": plan_id,
            "details": {"steps": len(decomposition.steps), "reasoning": decomposition.reasoning[:200]},
            "outcome": "success",
        })
        logger.info("engine=plan_created plan_id=%s steps=%d run_id=%s", plan_id, len(decomposition.steps), run_id)
        return plan_id

    def _build_supervisor_graph(
        self, run_id: str, workflow_id: str, user_id: str, plan_id: str,
    ) -> Any:
        """Build the standard supervisor -> agent LangGraph.

        Args:
            run_id: Current run identifier.
            workflow_id: Workflow being executed.
            user_id: Originating user.
            plan_id: Pre-created plan ID.

        Returns:
            Compiled LangGraph runnable.
        """
        settings = self.settings
        builder: StateGraph = StateGraph(AgentState)

        async def supervisor_node(state: AgentState) -> dict[str, Any]:
            span_id = str(uuid4())
            span_create({
                "spanId": span_id, "runId": run_id, "nodeType": "supervisor",
                "nodeName": "supervisor", "startedAt": _now(),
                "input": {"messages": [m.content for m in state["messages"]]},
                "llmCalls": [], "toolCalls": [],
            })
            agents = agent_list()
            active = [a for a in agents if a.get("status") == "active"]
            chosen = active[0] if active else None
            agent_name = chosen["name"] if chosen else "DefaultAgent"
            intent = f"Route task to {agent_name}"
            span_update(span_id, {"endedAt": _now(), "output": {"intent": intent}})
            audit_log({
                "actorType": "agent", "actorId": "supervisor",
                "action": "supervisor.routed", "resourceType": "run", "resourceId": run_id,
                "details": {"assignedAgent": agent_name}, "outcome": "success",
            })
            if plan_id:
                _mark_task(plan_id, 1, "running")
            return {
                "intent": intent,
                "assigned_to": chosen["id"] if chosen else None,
                "plan_id": plan_id,
                "messages": [AIMessage(content=f"[Supervisor] Routing to {agent_name}…")],
            }

        async def agent_node(state: AgentState) -> dict[str, Any]:
            span_id = str(uuid4())
            span_create({
                "spanId": span_id, "runId": run_id, "nodeType": "agent",
                "nodeName": "agent", "startedAt": _now(),
                "input": {"messages": [m.content for m in state["messages"]]},
                "llmCalls": [], "toolCalls": [],
            })
            last_human = next(
                (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "",
            )
            agent_id: str | None = state.get("assigned_to")
            agent_cfg = agent_get(agent_id) if agent_id else None

            if settings.openai_api_key and agent_cfg:
                result_text = await WorkflowExecutionEngine._call_llm_agent(
                    agent_cfg=agent_cfg, user_input=last_human, api_key=settings.openai_api_key,
                )
            else:
                agent_label = agent_cfg["name"] if agent_cfg else "Agent"
                result_text = f"[{agent_label}] Task received: {last_human}"

            span_update(span_id, {"endedAt": _now(), "output": {"response": result_text}})
            audit_log({
                "actorType": "agent", "actorId": agent_id or "unknown",
                "action": "agent.executed", "resourceType": "run", "resourceId": run_id,
                "details": {"agentName": agent_cfg["name"] if agent_cfg else "unknown", "outputLen": len(result_text)},
                "outcome": "success",
            })
            if plan_id:
                _mark_task(plan_id, 1, "complete")
                _mark_task(plan_id, 2, "complete")
            return {"messages": [AIMessage(content=result_text)], "results": {"agent": "success"}}

        builder.add_node("supervisor", supervisor_node)
        builder.add_node("agent", agent_node)
        builder.set_entry_point("supervisor")
        builder.add_edge("supervisor", "agent")
        builder.add_edge("agent", END)
        return builder.compile()

    @staticmethod
    async def _call_llm_agent(
        agent_cfg: dict[str, Any], user_input: str, api_key: str,
    ) -> str:
        """Call an LLM-backed agent. User input is never placed in system prompt.

        Args:
            agent_cfg: Agent configuration dict.
            user_input: Raw user text.
            api_key: OpenAI API key.

        Returns:
            Agent response text.
        """
        try:
            from langchain_core.messages import SystemMessage
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model=agent_cfg.get("model", "gpt-4o-mini"),
                temperature=float(agent_cfg.get("temperature", 0.7)),
                api_key=api_key,
            )
            system_content = str(agent_cfg.get("system_prompt") or "You are a helpful AI agent.")
            resp = await llm.ainvoke([
                SystemMessage(content=system_content),
                HumanMessage(content=user_input),
            ])
            return str(resp.content)
        except Exception as exc:
            logger.warning("engine=llm_agent_error error=%s", exc)
            return f"[Agent error: {exc}] Echo: {user_input}"

    def _compile_visual_graph(
        self, graph_def: dict[str, Any], run_id: str, workflow_id: str, user_id: str,
    ) -> Any:
        """Compile a visual workflow graph definition into a LangGraph runnable.

        Args:
            graph_def: Serialised visual workflow.
            run_id: Current run identifier.
            workflow_id: Associated workflow ID.
            user_id: Originating user ID.

        Returns:
            Compiled LangGraph runnable.
        """
        nodes: list[dict[str, Any]] = graph_def.get("graph", {}).get("nodes", [])
        edges: list[dict[str, Any]] = graph_def.get("graph", {}).get("edges", [])
        settings = self.settings
        builder: StateGraph = StateGraph(AgentState)

        def _make_agent_fn(node_cfg: dict[str, Any]) -> Any:
            async def _fn(state: AgentState) -> dict[str, Any]:
                label = node_cfg.get("data", {}).get("label", node_cfg["id"])
                last_human = next(
                    (m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "",
                )
                agent_id: str | None = node_cfg.get("data", {}).get("agentId")
                agent_cfg = agent_get(agent_id) if agent_id else None
                if settings.openai_api_key and agent_cfg:
                    content = await WorkflowExecutionEngine._call_llm_agent(
                        agent_cfg=agent_cfg, user_input=last_human, api_key=settings.openai_api_key,
                    )
                else:
                    content = f"[{label}] processed: {last_human}"
                audit_log({
                    "actorType": "agent", "actorId": agent_id or label,
                    "action": "visual_node.executed", "resourceType": "run", "resourceId": run_id,
                    "details": {"node": label, "outputLen": len(content)}, "outcome": "success",
                })
                return {"messages": [AIMessage(content=content)]}
            return _fn

        def _make_passthrough(node_cfg: dict[str, Any]) -> Any:
            async def _fn(state: AgentState) -> dict[str, Any]:
                return {}
            return _fn

        node_ids: set[str] = set()
        for node in nodes:
            nid: str = node["id"]
            ntype: str = node.get("type", "AgentNode")
            node_ids.add(nid)
            if ntype in ("AgentNode", "CrewNode"):
                builder.add_node(nid, _make_agent_fn(node))
            else:
                builder.add_node(nid, _make_passthrough(node))

        input_nodes = [n for n in nodes if n.get("type") == "InputNode"]
        entry: str | None = (
            input_nodes[0]["id"] if input_nodes else (nodes[0]["id"] if nodes else None)
        )
        if entry:
            builder.set_entry_point(entry)

        for edge in edges:
            src: str | None = edge.get("source")
            tgt: str | None = edge.get("target")
            if src and tgt and src in node_ids:
                if tgt in node_ids:
                    builder.add_edge(src, tgt)
                elif tgt == "END":
                    builder.add_edge(src, END)

        for node in nodes:
            if node.get("type") == "OutputNode":
                builder.add_edge(node["id"], END)

        return builder.compile()

    @staticmethod
    async def _stream_graph(
        graph: Any, initial_input: str, run_id: str,
    ) -> AsyncGenerator[tuple[str, dict[str, Any]], None]:
        """Stream graph execution events.

        Args:
            graph: Compiled LangGraph runnable.
            initial_input: Initial user message.
            run_id: Current run ID.

        Yields:
            Tuples of (node_name, node_output_dict).
        """
        async for event in graph.astream({
            "messages": [HumanMessage(content=initial_input)],
            "results": {}, "next_node": None, "intent": None,
            "assigned_to": None, "subtasks": None, "plan_id": None,
        }):
            for node_name, node_output in event.items():
                yield node_name, node_output


_engine: WorkflowExecutionEngine | None = None


def get_engine() -> WorkflowExecutionEngine:
    """Return the application-wide engine singleton.

    Returns:
        Shared WorkflowExecutionEngine instance.
    """
    global _engine
    if _engine is None:
        _engine = WorkflowExecutionEngine()
    return _engine
