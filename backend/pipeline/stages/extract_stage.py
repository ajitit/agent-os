"""
Stage 2 — Extract.

Performs Named Entity Recognition (NER) using a layered approach:

1. Regex-based extraction for structured entity types (email, phone, URL,
   IP address, credit card, SSN).
2. Capitalisation-heuristic extraction for PERSON, ORGANISATION, LOCATION.

No external ML model is required; the stage is fast and deterministic.
For production deployments, swap the implementation behind the
:class:`BaseExtractor` ABC without changing the orchestrator.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from backend.pipeline.base import BaseStage
from backend.pipeline.models import (
    Entity,
    EntityType,
    ExtractResult,
    PipelineContext,
)

# ── Extractor ABC (adapter pattern) ──────────────────────────────────────────


class BaseExtractor(ABC):
    """Abstract extractor — swap implementations without changing stage code.

    Subclasses:
        RegexExtractor: Regex + heuristic implementation (default).
    """

    @abstractmethod
    def extract(self, text: str) -> list[Entity]:
        """Extract entities from *text*.

        Args:
            text: Raw input string.

        Returns:
            List of Entity objects with offsets.
        """


# ── Regex + heuristic extractor ───────────────────────────────────────────────


_STRUCTURED_PATTERNS: list[tuple[EntityType, str]] = [
    (EntityType.EMAIL, r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    (EntityType.PHONE, r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"),
    (EntityType.URL, r"https?://[^\s<>\"']+"),
    (
        EntityType.IP_ADDRESS,
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b",
    ),
    (
        EntityType.CREDIT_CARD,
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
    ),
    (EntityType.SSN, r"\b\d{3}-\d{2}-\d{4}\b"),
    (
        EntityType.DATE,
        r"\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}-\d{2}-\d{2})\b",
    ),
]


class RegexExtractor(BaseExtractor):
    """Regex + capitalisation-heuristic entity extractor.

    Extracts structured entity types (email, phone, URL …) via compiled
    regexes, then uses a simple multi-word capitalisation heuristic to detect
    PERSON, ORGANISATION, and LOCATION mentions.
    """

    def __init__(self) -> None:
        self._compiled = [
            (etype, re.compile(pattern))
            for etype, pattern in _STRUCTURED_PATTERNS
        ]

    def extract(self, text: str) -> list[Entity]:
        """Extract all entities from *text*.

        Args:
            text: Input string.

        Returns:
            Deduplicated list of Entity objects sorted by start offset.
        """
        entities: list[Entity] = []
        covered: set[tuple[int, int]] = set()

        # ── Structured regex pass ──────────────────────────────────────────
        for etype, pattern in self._compiled:
            for m in pattern.finditer(text):
                span = (m.start(), m.end())
                if span not in covered:
                    entities.append(
                        Entity(
                            text=m.group(),
                            entity_type=etype,
                            start=m.start(),
                            end=m.end(),
                            confidence=0.95,
                        )
                    )
                    covered.add(span)

        # ── Capitalised multi-word heuristic ───────────────────────────────
        # Match 1–4 consecutive Title-Case tokens not preceded by sentence start
        cap_pattern = re.compile(
            r"(?<![.!?]\s)(?<!\A)(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})"
        )
        for m in cap_pattern.finditer(text):
            span = (m.start(), m.end())
            if span in covered:
                continue
            raw = m.group().strip()
            if len(raw) < 3:
                continue
            # Rough heuristic for org vs person vs location
            etype = _classify_capitalised(raw)
            entities.append(
                Entity(
                    text=raw,
                    entity_type=etype,
                    start=m.start(),
                    end=m.end(),
                    confidence=0.6,
                )
            )
            covered.add(span)

        return sorted(entities, key=lambda e: e.start)


_ORG_SUFFIXES = re.compile(
    r"\b(Inc|Ltd|LLC|Corp|Co|PLC|GmbH|AG|SA|NV|BV|Group|Foundation|Institute|University|College|Hospital|Bank|Fund)\b",
    re.IGNORECASE,
)
_LOC_WORDS = re.compile(
    r"\b(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Drive|City|Town|County|Province|State|Country|Mountain|River|Lake|Ocean|Bay|Park)\b",
    re.IGNORECASE,
)


def _classify_capitalised(text: str) -> EntityType:
    """Heuristically classify a capitalised phrase.

    Args:
        text: Capitalised phrase to classify.

    Returns:
        Best-guess EntityType.
    """
    if _ORG_SUFFIXES.search(text):
        return EntityType.ORGANISATION
    if _LOC_WORDS.search(text):
        return EntityType.LOCATION
    # Default to PERSON for single or double capitalised names
    word_count = len(text.split())
    if word_count <= 3:
        return EntityType.PERSON
    return EntityType.ORGANISATION


# ── Stage ─────────────────────────────────────────────────────────────────────


class ExtractStage(BaseStage):
    """Stage 2: extract named entities from the (original) input.

    Uses ``ctx.original_input`` so extraction always sees the unmasked text.

    Attributes:
        stage_name: Always ``"extract"``.
    """

    stage_name = "extract"

    def __init__(self, extractor: BaseExtractor | None = None) -> None:
        """Initialise the stage.

        Args:
            extractor: Custom extractor implementation.  Defaults to
                :class:`RegexExtractor`.
        """
        self._extractor: BaseExtractor = extractor or RegexExtractor()

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Extract entities from ``ctx.original_input``.

        Args:
            ctx: Current pipeline context.

        Returns:
            Context with ``extract_result`` populated.
        """
        entities = self._extractor.extract(ctx.original_input)
        return ctx.with_update(
            extract_result=ExtractResult(entities=entities)
        )
