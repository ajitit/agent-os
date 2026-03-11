"""
Stage 4 — Mask.

Replaces sensitive tokens in the original input using the patterns stored in
:class:`~backend.pipeline.memory.pattern_store.MaskPatternStore`.

Each enabled mask pattern is applied in order; matched substrings are replaced
with a numbered placeholder (e.g. ``[EMAIL_1]``) so that the downstream text
is anonymised.  A ``mask_map`` is kept so that privileged consumers can
unmask if needed.
"""

from __future__ import annotations

import re

from backend.pipeline.base import BaseStage
from backend.pipeline.memory.pattern_store import MaskPatternStore
from backend.pipeline.models import MaskResult, PipelineContext


class MaskStage(BaseStage):
    """Stage 4: redact sensitive tokens in ``ctx.original_input``.

    Attributes:
        stage_name: Always ``"mask"``.
    """

    stage_name = "mask"

    def __init__(self, store: MaskPatternStore) -> None:
        """Initialise the stage with a mask pattern store.

        Args:
            store: The long-term memory store of mask patterns.
        """
        self._store = store

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Apply masking to ``ctx.original_input``.

        Replacement tokens use the format ``<PLACEHOLDER>_<n>`` where *n* is a
        monotonically increasing counter per placeholder type, ensuring that
        two different email addresses are not collapsed into the same token.

        Args:
            ctx: Current pipeline context.

        Returns:
            Context with ``mask_result`` populated.
        """
        text = ctx.original_input
        mask_map: dict[str, str] = {}
        counters: dict[str, int] = {}
        total_replacements = 0

        for pattern in self._store.enabled_patterns():
            try:
                compiled = re.compile(pattern.pattern)
            except re.error:
                continue

            def _replace(m: re.Match[str], placeholder: str = pattern.placeholder) -> str:
                nonlocal total_replacements
                original = m.group()
                # Assign unique token per occurrence type
                base = placeholder.strip("[]")
                counters[base] = counters.get(base, 0) + 1
                token = f"[{base}_{counters[base]}]"
                mask_map[token] = original
                total_replacements += 1
                return token

            text = compiled.sub(_replace, text)

        return ctx.with_update(
            mask_result=MaskResult(
                masked_text=text,
                mask_map=mask_map,
                mask_count=total_replacements,
            )
        )
