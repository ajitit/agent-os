"""
Stages 5–8 — Route, Classify, Aggregate, Result.

These four stages are grouped in a single module because they share the
agent registry from the existing ``backend.api.stores`` module and are
relatively self-contained.
"""

from __future__ import annotations

import logging
import re

from backend.api.stores import agent_get, agent_list
from backend.pipeline.base import BaseStage
from backend.pipeline.models import (
    AgentOutput,
    AggregateResult,
    ClassifyResult,
    PipelineContext,
    RouteDecision,
    RouteResult,
)

logger = logging.getLogger(__name__)


# ── Stage 5 — Route ───────────────────────────────────────────────────────────


class RouteStage(BaseStage):
    """Stage 5: select target agents based on entities and intent.

    Routing rules (in priority order):

    * If any entity maps to the ``healthcare`` ontology domain → prefer agents
      whose name/role contains "medical", "health", or "clinical".
    * If any entity maps to the ``finance`` domain → prefer "finance",
      "accounting", or "analyst".
    * If any entity maps to the ``technology`` domain → prefer "tech",
      "engineer", or "developer".
    * Fallback: route to all active agents, sorted alphabetically.

    Attributes:
        stage_name: Always ``"route"``.
    """

    stage_name = "route"

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Determine routing targets.

        Args:
            ctx: Current pipeline context.

        Returns:
            Context with ``route_result`` populated.
        """
        agents = agent_list()
        active = [a for a in agents if a.get("status") == "active"]

        # Derive domains from ontology mappings
        domains: set[str] = set()
        if ctx.map_result:
            for mapping in ctx.map_result.mappings:
                cid = mapping.ontology_id
                # Infer domain from concept ID prefix
                prefix = cid.split("_")[0] if "_" in cid else ""
                if prefix == "MED":
                    domains.add("healthcare")
                elif prefix == "FIN":
                    domains.add("finance")
                elif prefix == "TECH":
                    domains.add("technology")

        domain_keywords: dict[str, list[str]] = {
            "healthcare": ["medical", "health", "clinical", "nurse", "doctor"],
            "finance": ["finance", "accounting", "analyst", "banking", "audit"],
            "technology": ["tech", "engineer", "developer", "devops", "sre"],
        }

        targets: list[RouteDecision] = []
        priority = 0

        for domain in domains:
            keywords = domain_keywords.get(domain, [])
            for agent in active:
                name = (agent.get("name") or "").lower()
                role = (agent.get("role") or "").lower()
                if any(kw in name or kw in role for kw in keywords):
                    targets.append(
                        RouteDecision(
                            agent_id=agent["id"],
                            agent_name=agent.get("name", "Unknown"),
                            reason=f"Domain match: {domain}",
                            priority=priority,
                        )
                    )
                    priority += 1

        # Fallback: include all active agents not yet targeted
        targeted_ids = {t.agent_id for t in targets}
        for agent in active:
            if agent["id"] not in targeted_ids:
                targets.append(
                    RouteDecision(
                        agent_id=agent["id"],
                        agent_name=agent.get("name", "Unknown"),
                        reason="General routing (no domain match)",
                        priority=priority,
                    )
                )
                priority += 1

        # If no active agents, add a default placeholder
        if not targets:
            targets.append(
                RouteDecision(
                    agent_id="default",
                    agent_name="Default Agent",
                    reason="No active agents registered",
                    priority=0,
                )
            )

        return ctx.with_update(route_result=RouteResult(targets=targets))


# ── Stage 6 — Classify ────────────────────────────────────────────────────────


_INTENT_PATTERNS: list[tuple[str, str]] = [
    (r"(?i)\b(summarise|summarize|summary|tldr)\b", "summarise"),
    (r"(?i)\b(translate|translation|in \w+ language)\b", "translate"),
    (r"(?i)\b(analyse|analyze|analysis|evaluate|assess)\b", "analyse"),
    (r"(?i)\b(generate|create|write|draft|compose|produce)\b", "generate"),
    (r"(?i)\b(search|find|lookup|retrieve|get me)\b", "retrieve"),
    (r"(?i)\b(compare|versus|vs\.?|difference between)\b", "compare"),
    (r"(?i)\b(explain|how does|what is|define|meaning of)\b", "explain"),
    (r"(?i)\b(fix|debug|error|issue|problem|bug)\b", "debug"),
    (r"(?i)\b(schedule|book|arrange|calendar|appointment)\b", "schedule"),
]

_CATEGORY_PATTERNS: list[tuple[str, str, str]] = [
    # (category, subcategory, regex)
    (r"(?i)\b(medic|health|patient|clinical|diagnos|drug|hospital)\b", "healthcare", "clinical_query"),
    (r"(?i)\b(finance|payment|invoice|bank|transaction|budget|cost)\b", "finance", "financial_query"),
    (r"(?i)\b(code|bug|deploy|api|server|database|software|git)\b", "technology", "technical_query"),
    (r"(?i)\b(legal|contract|law|compliance|regulation|gdpr|policy)\b", "legal", "compliance_query"),
    (r"(?i)\b(marketing|brand|campaign|seo|social media|content)\b", "marketing", "marketing_query"),
]


class ClassifyStage(BaseStage):
    """Stage 6: classify intent, category, and sentiment.

    Uses fast regex heuristics.  In production, replace with an LLM call
    via the existing :class:`~backend.adapters.llm.base.BaseLLMAdapter`
    without touching this class — inject the adapter in ``__init__``.

    Attributes:
        stage_name: Always ``"classify"``.
    """

    stage_name = "classify"

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Classify the masked (or original) input text.

        Args:
            ctx: Current pipeline context.

        Returns:
            Context with ``classify_result`` populated.
        """
        text = ctx.mask_result.masked_text if ctx.mask_result else ctx.original_input

        # Detect intent
        intent = "general_query"
        for pattern, label in _INTENT_PATTERNS:
            if re.search(pattern, text):
                intent = label
                break

        # Detect category + subcategory
        category = "general"
        subcategory: str | None = None
        for pattern, cat, sub in _CATEGORY_PATTERNS:
            if re.search(pattern, text):
                category = cat
                subcategory = sub
                break

        # Simple sentiment heuristic
        positive_words = re.findall(r"(?i)\b(great|good|excellent|perfect|love|thanks|appreciate)\b", text)
        negative_words = re.findall(r"(?i)\b(bad|terrible|awful|hate|broken|failed|error|wrong)\b", text)
        if len(positive_words) > len(negative_words):
            sentiment: str = "positive"
        elif len(negative_words) > len(positive_words):
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Collect classification tags from entity types
        tags: list[str] = []
        if ctx.extract_result:
            for e in ctx.extract_result.entities:
                tag = e.entity_type.value.lower()
                if tag not in tags:
                    tags.append(tag)

        return ctx.with_update(
            classify_result=ClassifyResult(
                category=category,
                subcategory=subcategory,
                intent=intent,
                sentiment=sentiment,  # type: ignore[arg-type]
                confidence=0.75,
                tags=tags,
            )
        )


# ── Stage 7 — Aggregate ───────────────────────────────────────────────────────


class AggregateStage(BaseStage):
    """Stage 7: collect results from all routed agents and synthesise.

    In this implementation the agent responses are *simulated* because
    actual execution requires async streaming (handled by the
    :class:`~backend.core.engine.WorkflowExecutionEngine`).

    When the engine produces real outputs, pass them into this stage via
    ``ctx.aggregate_result`` before calling the orchestrator.

    Attributes:
        stage_name: Always ``"aggregate"``.
    """

    stage_name = "aggregate"

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Aggregate agent outputs into a coherent summary.

        Args:
            ctx: Current pipeline context.

        Returns:
            Context with ``aggregate_result`` populated.
        """
        # If the engine already populated aggregate_result, pass through
        if ctx.aggregate_result and ctx.aggregate_result.agent_outputs:
            summary = self._synthesise(ctx.aggregate_result.agent_outputs)
            return ctx.with_update(
                aggregate_result=ctx.aggregate_result.model_copy(
                    update={"summary": summary}
                )
            )

        # Build synthetic output stubs from routing targets
        outputs: list[AgentOutput] = []
        if ctx.route_result:
            for target in ctx.route_result.targets[:3]:  # cap at 3 agents
                agent_cfg = agent_get(target.agent_id) if target.agent_id != "default" else None
                content = (
                    f"[{target.agent_name}] Ready to process: "
                    f"{ctx.mask_result.masked_text[:200] if ctx.mask_result else ctx.original_input[:200]}"
                )
                outputs.append(
                    AgentOutput(
                        agent_id=target.agent_id,
                        agent_name=target.agent_name,
                        content=content,
                        metadata={"agent_config": agent_cfg or {}},
                    )
                )

        if not outputs:
            outputs.append(
                AgentOutput(
                    agent_id="pipeline",
                    agent_name="Pipeline",
                    content=ctx.mask_result.masked_text if ctx.mask_result else ctx.original_input,
                )
            )

        summary = self._synthesise(outputs)

        return ctx.with_update(
            aggregate_result=AggregateResult(
                summary=summary,
                agent_outputs=outputs,
                consensus=len(outputs) <= 1,
            )
        )

    @staticmethod
    def _synthesise(outputs: list[AgentOutput]) -> str:
        """Produce a single-paragraph summary from multiple agent outputs.

        Args:
            outputs: List of agent output objects.

        Returns:
            Synthesised summary string.
        """
        if not outputs:
            return "No agent outputs to aggregate."
        if len(outputs) == 1:
            return outputs[0].content
        parts = "\n".join(f"• [{o.agent_name}]: {o.content}" for o in outputs)
        return f"Aggregated from {len(outputs)} agents:\n{parts}"


# ── Stage 8 — Result ──────────────────────────────────────────────────────────


class ResultStage(BaseStage):
    """Stage 8: compose the final pipeline result.

    Assembles a human-readable result from the aggregated summary, the
    classification, and the mask map (if any tokens were redacted).

    Attributes:
        stage_name: Always ``"result"``.
    """

    stage_name = "result"

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Compose ``ctx.final_result``.

        Args:
            ctx: Current pipeline context.

        Returns:
            Context with ``final_result`` populated.
        """
        parts: list[str] = []

        if ctx.aggregate_result:
            parts.append(ctx.aggregate_result.summary)

        if ctx.classify_result:
            cl = ctx.classify_result
            meta = (
                f"[Category: {cl.category}"
                + (f" / {cl.subcategory}" if cl.subcategory else "")
                + f" | Intent: {cl.intent} | Sentiment: {cl.sentiment}]"
            )
            parts.append(meta)

        if ctx.mask_result and ctx.mask_result.mask_count:
            parts.append(
                f"[{ctx.mask_result.mask_count} sensitive token(s) were redacted from your input.]"
            )

        if ctx.map_result and ctx.map_result.mappings:
            n = len(ctx.map_result.mappings)
            parts.append(f"[{n} entity concept(s) identified in your input.]")

        final = "\n\n".join(parts) if parts else "Processing complete."
        return ctx.with_update(final_result=final)
