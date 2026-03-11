"""
Pipeline long-term memory — in-memory stores for filter patterns and mask patterns.

These stores act as the "long-term memory" for the pipeline:

* :class:`FilterPatternStore` — regex patterns that classify input as junk,
  personal, or confidential.
* :class:`MaskPatternStore` — regex patterns that define what to redact and
  what placeholder token to use.

Both stores are pre-seeded with sensible defaults and allow runtime CRUD so
administrators can tune detection without code changes.
"""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.pipeline.models import FilterVerdict

# ── Filter pattern ────────────────────────────────────────────────────────────


class FilterPattern(BaseModel):
    """A single filter rule.

    Attributes:
        id: Unique pattern identifier.
        name: Human-readable label.
        verdict: Verdict to return when this pattern matches.
        pattern: Python ``re``-compatible regex string.
        description: Optional explanation of the pattern's intent.
        enabled: Whether the pattern is active.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    verdict: FilterVerdict
    pattern: str
    description: str = ""
    enabled: bool = True


# ── Mask pattern ──────────────────────────────────────────────────────────────


class MaskPattern(BaseModel):
    """A single masking rule.

    Attributes:
        id: Unique pattern identifier.
        name: Human-readable label.
        pattern: Python ``re``-compatible regex string.
        placeholder: Replacement token inserted in the masked text,
            e.g. ``"[EMAIL]"``.
        description: Optional explanation.
        enabled: Whether the pattern is active.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    pattern: str
    placeholder: str
    description: str = ""
    enabled: bool = True


# ── In-memory stores ──────────────────────────────────────────────────────────


class FilterPatternStore:
    """In-memory store for :class:`FilterPattern` records.

    Pre-seeded with default patterns covering common junk, personal, and
    confidential content.  All CRUD methods are synchronous because the
    underlying structure is a plain dict.
    """

    # Default seed patterns (verdict → patterns)
    _DEFAULTS: list[dict[str, Any]] = [
        # ── Junk ──────────────────────────────────────────────────────────
        {
            "name": "spam_keywords",
            "verdict": FilterVerdict.JUNK,
            "pattern": r"(?i)\b(buy now|click here|free money|you have won|lottery|casino|viagra|enlargement)\b",
            "description": "Common spam keywords",
        },
        {
            "name": "excessive_caps",
            "verdict": FilterVerdict.JUNK,
            "pattern": r"[A-Z]{10,}",
            "description": "Excessive capital letters (shouting / noise)",
        },
        {
            "name": "repeated_chars",
            "verdict": FilterVerdict.JUNK,
            "pattern": r"(.)\1{9,}",
            "description": "Same character repeated 10+ times",
        },
        # ── Personal ──────────────────────────────────────────────────────
        {
            "name": "email_address",
            "verdict": FilterVerdict.PERSONAL,
            "pattern": r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
            "description": "Email address (PII)",
        },
        {
            "name": "phone_number",
            "verdict": FilterVerdict.PERSONAL,
            "pattern": r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "description": "US-format phone number (PII)",
        },
        {
            "name": "date_of_birth",
            "verdict": FilterVerdict.PERSONAL,
            "pattern": r"(?i)\b(date of birth|dob|born on)[\s:]+\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
            "description": "Date-of-birth disclosure",
        },
        # ── Confidential ──────────────────────────────────────────────────
        {
            "name": "ssn",
            "verdict": FilterVerdict.CONFIDENTIAL,
            "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
            "description": "US Social Security Number",
        },
        {
            "name": "credit_card",
            "verdict": FilterVerdict.CONFIDENTIAL,
            "pattern": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
            "description": "Credit card number (Visa / MC / Amex / Discover)",
        },
        {
            "name": "api_key_leak",
            "verdict": FilterVerdict.CONFIDENTIAL,
            "pattern": r"(?i)(api[_\-]?key|secret[_\-]?key|access[_\-]?token)\s*[=:]\s*[A-Za-z0-9_\-]{16,}",
            "description": "Potential API key or secret in plain text",
        },
        {
            "name": "password_disclosure",
            "verdict": FilterVerdict.CONFIDENTIAL,
            "pattern": r"(?i)\bpassword\s*[=:]\s*\S+",
            "description": "Password value in plain text",
        },
    ]

    def __init__(self) -> None:
        self._store: dict[str, FilterPattern] = {}
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        """Populate the store with built-in default patterns."""
        for raw in self._DEFAULTS:
            p = FilterPattern(**raw)
            self._store[p.id] = p

    # ── CRUD ──────────────────────────────────────────────────────────────

    def list_all(self) -> list[FilterPattern]:
        """Return all patterns.

        Returns:
            Sorted list of FilterPattern instances.
        """
        return sorted(self._store.values(), key=lambda p: p.name)

    def get(self, pattern_id: str) -> FilterPattern | None:
        """Retrieve a single pattern by ID.

        Args:
            pattern_id: Pattern UUID.

        Returns:
            The pattern, or None if not found.
        """
        return self._store.get(pattern_id)

    def create(self, pattern: FilterPattern) -> FilterPattern:
        """Persist a new pattern.

        Args:
            pattern: Pattern to store.

        Returns:
            The stored pattern.

        Raises:
            ValueError: If a pattern with the same ID already exists.
        """
        if pattern.id in self._store:
            raise ValueError(f"FilterPattern '{pattern.id}' already exists.")
        self._store[pattern.id] = pattern
        return pattern

    def update(self, pattern_id: str, data: dict[str, Any]) -> FilterPattern | None:
        """Update an existing pattern.

        Args:
            pattern_id: ID of the pattern to update.
            data: Fields to update.

        Returns:
            Updated pattern, or None if not found.
        """
        existing = self._store.get(pattern_id)
        if not existing:
            return None
        updated = existing.model_copy(update=data)
        self._store[pattern_id] = updated
        return updated

    def delete(self, pattern_id: str) -> bool:
        """Delete a pattern.

        Args:
            pattern_id: Pattern UUID.

        Returns:
            True if deleted, False if not found.
        """
        if pattern_id not in self._store:
            return False
        del self._store[pattern_id]
        return True

    # ── Query ─────────────────────────────────────────────────────────────

    def enabled_patterns(self) -> list[FilterPattern]:
        """Return only enabled patterns.

        Returns:
            List of active FilterPattern instances.
        """
        return [p for p in self._store.values() if p.enabled]

    def match(self, text: str) -> list[tuple[FilterPattern, list[str]]]:
        """Find all enabled patterns that match in *text*.

        Args:
            text: Input string to scan.

        Returns:
            List of (pattern, matched_strings) tuples for each matching pattern.
        """
        results: list[tuple[FilterPattern, list[str]]] = []
        for pattern in self.enabled_patterns():
            try:
                matches = re.findall(pattern.pattern, text)
                if matches:
                    results.append((pattern, matches))
            except re.error:
                continue
        return results


class MaskPatternStore:
    """In-memory store for :class:`MaskPattern` records.

    Pre-seeded with patterns that cover common PII and credential types.
    """

    _DEFAULTS: list[dict[str, Any]] = [
        {
            "name": "email",
            "pattern": r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
            "placeholder": "[EMAIL]",
            "description": "Email addresses",
        },
        {
            "name": "phone_us",
            "pattern": r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "placeholder": "[PHONE]",
            "description": "US phone numbers",
        },
        {
            "name": "ssn",
            "pattern": r"\b\d{3}-\d{2}-\d{4}\b",
            "placeholder": "[SSN]",
            "description": "Social Security Numbers",
        },
        {
            "name": "credit_card",
            "pattern": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
            "placeholder": "[CREDIT_CARD]",
            "description": "Credit card numbers",
        },
        {
            "name": "ipv4",
            "pattern": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "placeholder": "[IP_ADDRESS]",
            "description": "IPv4 addresses",
        },
        {
            "name": "api_key",
            "pattern": r"(?i)(api[_\-]?key|secret[_\-]?key|access[_\-]?token)\s*[=:]\s*([A-Za-z0-9_\-]{16,})",
            "placeholder": "[API_KEY]",
            "description": "API keys and secrets",
        },
        {
            "name": "password",
            "pattern": r"(?i)\bpassword\s*[=:]\s*\S+",
            "placeholder": "[PASSWORD]",
            "description": "Plain-text passwords",
        },
    ]

    def __init__(self) -> None:
        self._store: dict[str, MaskPattern] = {}
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        """Populate the store with built-in default patterns."""
        for raw in self._DEFAULTS:
            p = MaskPattern(**raw)
            self._store[p.id] = p

    # ── CRUD ──────────────────────────────────────────────────────────────

    def list_all(self) -> list[MaskPattern]:
        """Return all patterns.

        Returns:
            Sorted list of MaskPattern instances.
        """
        return sorted(self._store.values(), key=lambda p: p.name)

    def get(self, pattern_id: str) -> MaskPattern | None:
        """Retrieve a single pattern by ID.

        Args:
            pattern_id: Pattern UUID.

        Returns:
            The pattern, or None if not found.
        """
        return self._store.get(pattern_id)

    def create(self, pattern: MaskPattern) -> MaskPattern:
        """Persist a new pattern.

        Args:
            pattern: Pattern to store.

        Returns:
            The stored pattern.
        """
        self._store[pattern.id] = pattern
        return pattern

    def update(self, pattern_id: str, data: dict[str, Any]) -> MaskPattern | None:
        """Update an existing pattern.

        Args:
            pattern_id: Pattern UUID.
            data: Fields to update.

        Returns:
            Updated pattern, or None if not found.
        """
        existing = self._store.get(pattern_id)
        if not existing:
            return None
        updated = existing.model_copy(update=data)
        self._store[pattern_id] = updated
        return updated

    def delete(self, pattern_id: str) -> bool:
        """Delete a pattern.

        Args:
            pattern_id: Pattern UUID.

        Returns:
            True if deleted, False if not found.
        """
        if pattern_id not in self._store:
            return False
        del self._store[pattern_id]
        return True

    def enabled_patterns(self) -> list[MaskPattern]:
        """Return only enabled patterns.

        Returns:
            List of active MaskPattern instances.
        """
        return [p for p in self._store.values() if p.enabled]
