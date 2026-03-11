"""
Module: core/planning/planner.py

Supervisor planning service.  Responsible for decomposing a free-text goal
into an ordered list of :class:`PlanStep` objects with agent/crew assignments.

Design decisions
----------------
* ``PlannerAdapter`` is an ``ABC`` so callers never depend on a concrete
  planner — the LLM-backed and rule-based implementations are swappable.
* ``RuleBasedPlanner`` is the default; ``LLMPlanner`` is used when an OpenAI
  or Anthropic key is present.
* The ``PlannerService`` picks the right adapter via a factory method that
  reads ``Settings``, satisfying the config-driven requirement.
* No imports from ``backend.api.*`` — this layer is pure domain logic.
"""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from backend.core.config import get_settings

logger = logging.getLogger(__name__)


# ── Value objects ─────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PlanStep:
    """One ordered step within a supervisor plan.

    Attributes:
        step_number: 1-based execution order.
        title: Short human-readable title.
        description: Detailed description of what this step does.
        assigned_type: Whether the step runs on an agent or a crew.
        assigned_id: ID of the target agent or crew (None = unassigned).
        depends_on: Step numbers that must complete before this one.
    """

    step_number: int
    title: str
    description: str
    assigned_type: str = "agent"  # "agent" | "crew"
    assigned_id: str | None = None
    depends_on: list[int] = field(default_factory=list)


@dataclass
class PlanDecomposition:
    """Result of decomposing a goal into steps.

    Attributes:
        goal: Original goal text.
        reasoning: Planner's reasoning for the breakdown.
        steps: Ordered list of plan steps.
        estimated_duration_minutes: Rough time estimate.
    """

    goal: str
    reasoning: str
    steps: list[PlanStep]
    estimated_duration_minutes: int = 5


# ── Adapter interface ─────────────────────────────────────────────────────────


class PlannerAdapter(ABC):
    """Abstract planner adapter.

    All concrete planners must implement :meth:`decompose`.
    """

    @abstractmethod
    async def decompose(
        self,
        goal: str,
        available_agents: list[dict[str, Any]],
    ) -> PlanDecomposition:
        """Decompose a goal into an ordered execution plan.

        Args:
            goal: Free-text goal description.
            available_agents: List of active agent dicts from the store.

        Returns:
            A :class:`PlanDecomposition` with at least one step.
        """


# ── Rule-based implementation (no LLM required) ───────────────────────────────


class RuleBasedPlanner(PlannerAdapter):
    """Deterministic rule-based planner.

    Uses keyword heuristics to derive a 2–4 step plan without any external
    API calls.  Always succeeds; provides a safe offline fallback.

    Args:
        None
    """

    _DOMAIN_KEYWORDS: dict[str, list[str]] = {
        "research": ["research", "find", "search", "look up", "discover", "investigate"],
        "analysis": ["analyse", "analyze", "evaluate", "assess", "review", "examine"],
        "generation": ["write", "draft", "create", "generate", "build", "produce"],
        "execution": ["run", "execute", "deploy", "send", "publish", "submit"],
        "summary": ["summarise", "summarize", "report", "recap", "overview"],
    }

    async def decompose(
        self,
        goal: str,
        available_agents: list[dict[str, Any]],
    ) -> PlanDecomposition:
        """Decompose using keyword heuristics.

        Args:
            goal: Goal text.
            available_agents: Active agents for assignment.

        Returns:
            PlanDecomposition with 2–4 heuristic steps.
        """
        lower = goal.lower()
        detected_domains: list[str] = []
        for domain, keywords in self._DOMAIN_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                detected_domains.append(domain)

        if not detected_domains:
            detected_domains = ["research", "generation"]

        steps: list[PlanStep] = []

        # Always start with analysis/planning
        steps.append(
            PlanStep(
                step_number=1,
                title="Understand & Plan",
                description=f"Break down the goal and identify required information: {goal[:100]}",
                assigned_type="agent",
                assigned_id=self._pick_agent(available_agents, "research"),
            )
        )

        # Add domain-specific middle steps
        for i, domain in enumerate(detected_domains[:2], start=2):
            title_map = {
                "research": "Research & Gather Information",
                "analysis": "Analyse Findings",
                "generation": "Generate Output",
                "execution": "Execute Task",
                "summary": "Summarise Results",
            }
            desc_map = {
                "research": "Search for relevant information and collect data needed for the goal.",
                "analysis": "Evaluate gathered data and derive insights.",
                "generation": "Produce the required artifact, document, or output.",
                "execution": "Execute the planned action or deployment.",
                "summary": "Compile and summarise all results into a final report.",
            }
            steps.append(
                PlanStep(
                    step_number=i,
                    title=title_map.get(domain, f"Step {i}"),
                    description=desc_map.get(domain, "Execute this phase of the plan."),
                    assigned_type="agent",
                    assigned_id=self._pick_agent(available_agents, domain),
                    depends_on=[i - 1],
                )
            )

        # Always end with a result/validation step
        last = len(steps) + 1
        steps.append(
            PlanStep(
                step_number=last,
                title="Validate & Deliver Result",
                description="Review output quality, apply any corrections, and deliver the final result.",
                assigned_type="agent",
                assigned_id=self._pick_agent(available_agents, "summary"),
                depends_on=[last - 1],
            )
        )

        reasoning = (
            f"Detected domains: {', '.join(detected_domains) or 'general'}. "
            f"Generated a {len(steps)}-step plan using rule-based decomposition."
        )
        logger.info(
            "planner=rule_based goal_len=%d steps=%d domains=%s",
            len(goal),
            len(steps),
            detected_domains,
        )
        return PlanDecomposition(
            goal=goal,
            reasoning=reasoning,
            steps=steps,
            estimated_duration_minutes=len(steps) * 3,
        )

    @staticmethod
    def _pick_agent(
        agents: list[dict[str, Any]], domain: str
    ) -> str | None:
        """Pick the most relevant agent for a domain.

        Args:
            agents: Available agent dicts.
            domain: Target domain string.

        Returns:
            Agent ID or None if no agents available.
        """
        for agent in agents:
            role = (agent.get("role") or "").lower()
            name = (agent.get("name") or "").lower()
            if domain in role or domain in name:
                return str(agent["id"])
        return str(agents[0]["id"]) if agents else None


# ── LLM-backed implementation ─────────────────────────────────────────────────


class LLMPlanner(PlannerAdapter):
    """LLM-backed planner using the configured adapter.

    Uses ``OpenAIAdapter`` when an OpenAI key is present; falls back to
    ``RuleBasedPlanner`` on any error so the system never hard-fails.

    Args:
        api_key: OpenAI API key string.
    """

    _SYSTEM_PROMPT: str = (
        "You are a supervisor agent that decomposes a goal into an ordered execution plan. "
        "Respond ONLY with valid JSON matching this schema exactly:\n"
        "{\n"
        "  \"reasoning\": \"string\",\n"
        "  \"estimated_duration_minutes\": integer,\n"
        "  \"steps\": [\n"
        "    {\"step_number\": 1, \"title\": \"string\", \"description\": \"string\", "
        "\"assigned_type\": \"agent\", \"depends_on\": []}\n"
        "  ]\n"
        "}\n"
        "Rules: 2–6 steps; no markdown; JSON only; never interpolate agent names into "
        "system prompts; assigned_type must be 'agent' or 'crew'."
    )

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._fallback = RuleBasedPlanner()

    async def decompose(
        self,
        goal: str,
        available_agents: list[dict[str, Any]],
    ) -> PlanDecomposition:
        """Decompose using an LLM call with JSON output.

        Falls back to :class:`RuleBasedPlanner` on any error.

        Args:
            goal: Goal text.
            available_agents: Active agents for context.

        Returns:
            PlanDecomposition from LLM or rule-based fallback.
        """
        try:
            import json as _json

            from backend.adapters.llm.base import LLMRequest
            from backend.adapters.llm.openai import OpenAIAdapter

            agent_summary = "; ".join(
                f"{a.get('name', 'Agent')} ({a.get('role', 'general')})"
                for a in available_agents[:5]
            )
            # NOTE: goal is never interpolated into system_prompt —
            # it goes only into the user prompt per security standards.
            user_prompt = (
                f"Available agents: {agent_summary or 'none'}\n\n"
                f"Goal: {goal}"
            )

            adapter = OpenAIAdapter(api_key=self._api_key)
            response = await adapter.generate(
                LLMRequest(
                    prompt=user_prompt,
                    system_prompt=self._SYSTEM_PROMPT,
                    model="gpt-4o-mini",
                    temperature=0.3,
                    max_tokens=1000,
                )
            )

            raw = response.content.strip()
            # Strip any accidental markdown fences
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            data = _json.loads(raw)

            raw_steps: list[dict[str, Any]] = data.get("steps", [])
            steps = [
                PlanStep(
                    step_number=int(s.get("step_number", i + 1)),
                    title=str(s.get("title", f"Step {i + 1}")),
                    description=str(s.get("description", "")),
                    assigned_type=str(s.get("assigned_type", "agent")),
                    depends_on=[int(d) for d in s.get("depends_on", [])],
                )
                for i, s in enumerate(raw_steps)
            ]

            logger.info(
                "planner=llm steps=%d model=gpt-4o-mini",
                len(steps),
            )
            return PlanDecomposition(
                goal=goal,
                reasoning=str(data.get("reasoning", "")),
                steps=steps,
                estimated_duration_minutes=int(
                    data.get("estimated_duration_minutes", len(steps) * 3)
                ),
            )

        except Exception as exc:
            logger.warning(
                "planner=llm_fallback reason=%s",
                exc,
            )
            return await self._fallback.decompose(goal, available_agents)


# ── Service factory ───────────────────────────────────────────────────────────


class PlannerService:
    """High-level planning service that picks the right adapter.

    Usage::

        service = PlannerService.from_settings()
        decomposition = await service.plan("Summarise Q3 report", agents)

    Args:
        adapter: Concrete :class:`PlannerAdapter` instance.
    """

    def __init__(self, adapter: PlannerAdapter) -> None:
        self._adapter = adapter

    @classmethod
    def from_settings(cls) -> PlannerService:
        """Create a PlannerService wired to the configured LLM adapter.

        Uses ``LLMPlanner`` when ``openai_api_key`` is set in settings;
        otherwise falls back to ``RuleBasedPlanner``.

        Returns:
            Configured PlannerService instance.
        """
        settings = get_settings()
        adapter: PlannerAdapter
        if settings.openai_api_key:
            adapter = LLMPlanner(api_key=settings.openai_api_key)
        else:
            adapter = RuleBasedPlanner()
        return cls(adapter=adapter)

    async def plan(
        self,
        goal: str,
        available_agents: list[dict[str, Any]],
    ) -> PlanDecomposition:
        """Decompose a goal into an execution plan.

        Args:
            goal: Free-text goal.
            available_agents: Active agent dicts from the store.

        Returns:
            PlanDecomposition with ordered steps.
        """
        return await self._adapter.decompose(goal, available_agents)
