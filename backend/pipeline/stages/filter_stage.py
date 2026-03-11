"""
Stage 1 — Filter.

Scans user input against the :class:`~backend.pipeline.memory.pattern_store.FilterPatternStore`
long-term memory.  If a pattern matches, the pipeline is halted with an
appropriate verdict and a user-facing message; otherwise the context is passed
through unchanged with ``FilterVerdict.PASS``.
"""

from __future__ import annotations

import logging

from backend.pipeline.base import BaseStage
from backend.pipeline.memory.pattern_store import FilterPatternStore
from backend.pipeline.models import FilterResult, FilterVerdict, PipelineContext, PipelineStatus

logger = logging.getLogger(__name__)

# User-facing messages keyed by verdict
_BLOCK_MESSAGES: dict[FilterVerdict, str] = {
    FilterVerdict.JUNK: (
        "Your message appears to contain spam or low-quality content. "
        "Please rephrase and try again."
    ),
    FilterVerdict.PERSONAL: (
        "Your message contains personal information (e.g. email, phone number). "
        "Please remove sensitive details before submitting."
    ),
    FilterVerdict.CONFIDENTIAL: (
        "Your message contains confidential data (e.g. credit card, SSN, API key). "
        "Please remove sensitive credentials before submitting."
    ),
    FilterVerdict.BLOCKED: "Your message has been blocked by the content filter.",
}

# Verdict severity — higher = stop first
_SEVERITY: dict[FilterVerdict, int] = {
    FilterVerdict.JUNK: 1,
    FilterVerdict.PERSONAL: 2,
    FilterVerdict.CONFIDENTIAL: 3,
    FilterVerdict.BLOCKED: 4,
}


class FilterStage(BaseStage):
    """Stage 1: filter junk, personal, and confidential input.

    Checks the input text against all enabled patterns in the
    :class:`FilterPatternStore`.  If any pattern matches, the highest-severity
    verdict is applied and the pipeline status set to ``BLOCKED``.

    Attributes:
        stage_name: Always ``"filter"``.
    """

    stage_name = "filter"

    def __init__(self, store: FilterPatternStore) -> None:
        """Initialise the stage with a pattern store.

        Args:
            store: The long-term memory store of filter patterns.
        """
        self._store = store

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Run the filter check on ``ctx.original_input``.

        Args:
            ctx: Current pipeline context.

        Returns:
            Updated context.  If a match is found, ``filter_result.verdict``
            is set to the blocking verdict and ``status`` is set to
            ``BLOCKED``.  Otherwise, ``verdict`` is ``PASS``.
        """
        text = ctx.original_input
        matches = self._store.match(text)

        if not matches:
            result = FilterResult(
                verdict=FilterVerdict.PASS,
                reason="No filter patterns matched.",
            )
            return ctx.with_update(
                filter_result=result,
                status=PipelineStatus.RUNNING,
            )

        # Pick the highest-severity verdict
        best_pattern, _ = max(
            matches, key=lambda t: _SEVERITY.get(t[0].verdict, 0)
        )
        matched_ids = [p.id for p, _ in matches]

        logger.warning(
            "filter=blocked run_id=%s verdict=%s patterns=%s",
            ctx.run_id,
            best_pattern.verdict,
            matched_ids,
        )

        result = FilterResult(
            verdict=best_pattern.verdict,
            reason=_BLOCK_MESSAGES.get(best_pattern.verdict, "Content blocked."),
            matched_patterns=matched_ids,
        )
        return ctx.with_update(
            filter_result=result,
            status=PipelineStatus.BLOCKED,
        )
