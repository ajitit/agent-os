"""
Stage 9 — Human Review Loop.

Implements the human-in-the-loop review workflow:

1. The stage sets the pipeline status to ``AWAITING_REVIEW`` and returns
   immediately — the orchestrator publishes the context to a review queue.
2. A human reviewer inspects the result via the review API, then submits
   :class:`~backend.pipeline.models.ReviewFeedback`.
3. The orchestrator calls :meth:`ReviewLoopStage.resume` with the feedback,
   which updates the context and sets the final status.

The review queue is an in-memory dict keyed by ``run_id``.  In production
replace with a Redis stream or PostgreSQL table without changing any stage code.
"""

from __future__ import annotations

import asyncio
import logging

from backend.pipeline.base import BaseStage
from backend.pipeline.models import (
    PipelineContext,
    PipelineStatus,
    ReviewFeedback,
)

logger = logging.getLogger(__name__)


class ReviewLoopStage(BaseStage):
    """Stage 9: pause pipeline and wait for human approval.

    The stage uses a per-run :class:`asyncio.Event` so the orchestrator can
    ``await`` it without polling.

    Attributes:
        stage_name: Always ``"review"``.
    """

    stage_name = "review"

    def __init__(self, timeout_seconds: float = 3600.0) -> None:
        """Initialise the stage.

        Args:
            timeout_seconds: Maximum seconds to wait for human review before
                the pipeline times out and is rejected automatically.
                Defaults to 1 hour.
        """
        self._timeout = timeout_seconds
        # run_id → asyncio.Event
        self._events: dict[str, asyncio.Event] = {}
        # run_id → ReviewFeedback (written by resume())
        self._feedback: dict[str, ReviewFeedback] = {}
        # run_id → PipelineContext snapshot at pause time
        self._paused: dict[str, PipelineContext] = {}

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Pause execution and wait for human review.

        Sets status to ``AWAITING_REVIEW``, stores the context, then
        awaits an asyncio Event that is set by :meth:`resume`.

        Args:
            ctx: Current pipeline context.

        Returns:
            Updated context after review decision.
        """
        event = asyncio.Event()
        self._events[ctx.run_id] = event
        self._paused[ctx.run_id] = ctx

        paused_ctx = ctx.with_update(status=PipelineStatus.AWAITING_REVIEW)
        self._paused[ctx.run_id] = paused_ctx

        logger.info(
            "review=paused run_id=%s timeout=%ss",
            ctx.run_id,
            self._timeout,
        )

        try:
            await asyncio.wait_for(event.wait(), timeout=self._timeout)
        except TimeoutError:
            logger.warning("review=timeout run_id=%s", ctx.run_id)
            self._cleanup(ctx.run_id)
            return paused_ctx.with_update(status=PipelineStatus.REJECTED)

        feedback = self._feedback.pop(ctx.run_id, None)
        self._cleanup(ctx.run_id)

        if not feedback:
            return paused_ctx.with_update(status=PipelineStatus.REJECTED)

        if not feedback.approved:
            logger.info(
                "review=rejected run_id=%s reviewer=%s",
                ctx.run_id,
                feedback.reviewer_id,
            )
            return paused_ctx.with_update(
                status=PipelineStatus.REJECTED,
                review_feedback=feedback,
            )

        # Apply modifications if any
        final_result = paused_ctx.final_result
        if feedback.modifications.get("final_result"):
            final_result = str(feedback.modifications["final_result"])

        logger.info(
            "review=approved run_id=%s reviewer=%s",
            ctx.run_id,
            feedback.reviewer_id,
        )
        return paused_ctx.with_update(
            status=PipelineStatus.APPROVED,
            review_feedback=feedback,
            final_result=final_result,
        )

    def resume(self, run_id: str, feedback: ReviewFeedback) -> bool:
        """Submit human feedback and unblock the waiting pipeline.

        Args:
            run_id: Pipeline run to resume.
            feedback: Human reviewer's decision.

        Returns:
            True if the run was found and unblocked, False if the run_id
            is unknown (already timed out or completed).
        """
        event = self._events.get(run_id)
        if not event:
            return False
        self._feedback[run_id] = feedback
        event.set()
        return True

    def pending_reviews(self) -> list[dict[str, str]]:
        """Return summary of all currently paused runs.

        Returns:
            List of dicts with ``run_id`` and ``paused_at`` keys.
        """
        return [
            {
                "run_id": run_id,
                "status": "awaiting_review",
                "summary": (
                    (ctx.final_result or "")[:200]
                    if (ctx := self._paused.get(run_id))
                    else ""
                ),
            }
            for run_id in self._events
        ]

    def _cleanup(self, run_id: str) -> None:
        """Remove all per-run tracking state.

        Args:
            run_id: Run ID to clean up.
        """
        self._events.pop(run_id, None)
        self._paused.pop(run_id, None)
