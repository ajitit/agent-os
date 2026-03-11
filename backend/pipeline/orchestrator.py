"""
Pipeline orchestrator — wires all 9 stages and exposes a single
:meth:`PipelineOrchestrator.run` entry point.

The orchestrator:

1. Builds a :class:`~backend.pipeline.models.PipelineContext`.
2. Runs stages 1-8 in sequence via :meth:`BaseStage.safe_process`.
3. Optionally pauses at stage 9 (review) if ``require_review=True``.
4. Publishes structured events to the :class:`PipelineRunStore` for the
   Observability dashboard.

The orchestrator is stateless and thread-safe; all mutable state lives in
the per-run PipelineContext.
"""

from __future__ import annotations

import logging
from typing import Any
from uuid import uuid4

from backend.pipeline.memory.pattern_store import FilterPatternStore, MaskPatternStore
from backend.pipeline.models import (
    PipelineContext,
    PipelineStatus,
    ReviewFeedback,
)
from backend.pipeline.ontology.ontology_store import OntologyStore
from backend.pipeline.stages.extract_stage import ExtractStage
from backend.pipeline.stages.filter_stage import FilterStage
from backend.pipeline.stages.map_stage import MapStage
from backend.pipeline.stages.mask_stage import MaskStage
from backend.pipeline.stages.review_stage import ReviewLoopStage
from backend.pipeline.stages.routing_stages import (
    AggregateStage,
    ClassifyStage,
    ResultStage,
    RouteStage,
)

logger = logging.getLogger(__name__)


# ── Per-run record store ──────────────────────────────────────────────────────


class PipelineRunStore:
    """In-memory store for completed and in-progress pipeline run records.

    Provides a simple list + dict API used by the REST layer.
    """

    def __init__(self) -> None:
        self._runs: dict[str, dict[str, Any]] = {}

    def upsert(self, ctx: PipelineContext) -> None:
        """Persist (or update) a pipeline run record.

        Args:
            ctx: Context snapshot to store.
        """
        self._runs[ctx.run_id] = {
            "run_id": ctx.run_id,
            "user_id": ctx.user_id,
            "original_input": ctx.original_input,
            "status": ctx.status.value,
            "created_at": ctx.created_at.isoformat(),
            "filter_verdict": ctx.filter_result.verdict.value if ctx.filter_result else None,
            "filter_reason": ctx.filter_result.reason if ctx.filter_result else None,
            "entity_count": ctx.extract_result.entity_count if ctx.extract_result else 0,
            "category": ctx.classify_result.category if ctx.classify_result else None,
            "intent": ctx.classify_result.intent if ctx.classify_result else None,
            "mask_count": ctx.mask_result.mask_count if ctx.mask_result else 0,
            "route_primary": (
                ctx.route_result.primary.agent_name if ctx.route_result and ctx.route_result.primary else None
            ),
            "final_result": ctx.final_result,
            "stage_errors": ctx.stage_errors,
        }

    def get(self, run_id: str) -> dict[str, Any] | None:
        """Retrieve a run record by ID.

        Args:
            run_id: Pipeline run identifier.

        Returns:
            Dict record or None.
        """
        return self._runs.get(run_id)

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent run records.

        Args:
            limit: Maximum number of records to return.

        Returns:
            List of run record dicts, most recent first.
        """
        runs = list(self._runs.values())
        return runs[-limit:][::-1]


# ── Orchestrator ──────────────────────────────────────────────────────────────


class PipelineOrchestrator:
    """Wires all 9 pipeline stages and executes them in order.

    Args:
        filter_store: Filter pattern long-term memory.
        mask_store: Mask pattern long-term memory.
        ontology_store: Ontology concept store.
        review_stage: Human review loop stage instance.
        run_store: Optional run record store for observability.
    """

    def __init__(
        self,
        filter_store: FilterPatternStore,
        mask_store: MaskPatternStore,
        ontology_store: OntologyStore,
        review_stage: ReviewLoopStage,
        run_store: PipelineRunStore | None = None,
    ) -> None:
        self._filter = FilterStage(filter_store)
        self._extract = ExtractStage()
        self._map = MapStage(ontology_store)
        self._mask = MaskStage(mask_store)
        self._route = RouteStage()
        self._classify = ClassifyStage()
        self._aggregate = AggregateStage()
        self._result = ResultStage()
        self._review = review_stage
        self._run_store = run_store or PipelineRunStore()

    async def run(
        self,
        text: str,
        user_id: str = "anonymous",
        require_review: bool = False,
        run_id: str | None = None,
    ) -> PipelineContext:
        """Execute the full 9-stage pipeline.

        Stages 1–8 always run (unless blocked by Filter).  Stage 9 (review)
        only runs when ``require_review=True``.

        Args:
            text: Raw user input text.
            user_id: Originating user identifier.
            require_review: Whether to pause for human review after stage 8.
            run_id: Optional explicit run identifier (auto-generated if None).

        Returns:
            Final :class:`~backend.pipeline.models.PipelineContext` after all
            stages have completed.
        """
        ctx = PipelineContext(
            run_id=run_id or str(uuid4()),
            user_id=user_id,
            original_input=text,
            status=PipelineStatus.RUNNING,
        )

        logger.info(
            "pipeline=start run_id=%s user=%s require_review=%s",
            ctx.run_id,
            user_id,
            require_review,
        )

        # ── Stage 1: Filter ───────────────────────────────────────────────
        ctx = await self._filter.safe_process(ctx)
        self._run_store.upsert(ctx)

        if ctx.status == PipelineStatus.BLOCKED:
            logger.info("pipeline=blocked run_id=%s", ctx.run_id)
            return ctx

        # ── Stage 2: Extract ──────────────────────────────────────────────
        ctx = await self._extract.safe_process(ctx)

        # ── Stage 3: Map ──────────────────────────────────────────────────
        ctx = await self._map.safe_process(ctx)

        # ── Stage 4: Mask ──────────────────────────────────────────────────
        ctx = await self._mask.safe_process(ctx)

        # ── Stage 5: Route ────────────────────────────────────────────────
        ctx = await self._route.safe_process(ctx)

        # ── Stage 6: Classify ─────────────────────────────────────────────
        ctx = await self._classify.safe_process(ctx)

        # ── Stage 7: Aggregate ────────────────────────────────────────────
        ctx = await self._aggregate.safe_process(ctx)

        # ── Stage 8: Result ───────────────────────────────────────────────
        ctx = await self._result.safe_process(ctx)

        self._run_store.upsert(ctx)

        # ── Stage 9: Human review (optional) ──────────────────────────────
        if require_review:
            ctx = await self._review.safe_process(ctx)
        else:
            ctx = ctx.with_update(status=PipelineStatus.COMPLETE)

        self._run_store.upsert(ctx)

        logger.info(
            "pipeline=complete run_id=%s status=%s",
            ctx.run_id,
            ctx.status.value,
        )
        return ctx

    def resume_review(self, run_id: str, feedback: ReviewFeedback) -> bool:
        """Resume a paused human-review run.

        Args:
            run_id: Run to resume.
            feedback: Human reviewer decision.

        Returns:
            True if successfully unblocked.
        """
        return self._review.resume(run_id, feedback)

    def pending_reviews(self) -> list[dict[str, Any]]:
        """Return all runs currently awaiting human review.

        Returns:
            List of summary dicts.
        """
        return self._review.pending_reviews()

    @property
    def run_store(self) -> PipelineRunStore:
        """Expose the run store for the REST layer."""
        return self._run_store
