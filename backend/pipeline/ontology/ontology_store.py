"""
Pipeline ontology store — in-memory concept registry for the Map stage.

The ontology is a flat registry of :class:`OntologyConcept` records keyed by
ID.  Each concept belongs to a domain and carries a set of surface-form
aliases that the Map stage uses to find matches against extracted entities.
The store is pre-seeded with a healthcare, finance, and technology sub-ontology.
"""

from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.pipeline.models import EntityType


class OntologyConcept(BaseModel):
    """A single concept node in the ontology.

    Attributes:
        id: Unique concept identifier (e.g. ``"MED_001"``).
        label: Canonical human-readable label.
        domain: Top-level domain (e.g. ``"healthcare"``, ``"finance"``).
        entity_types: Which EntityType values this concept can match.
        aliases: Surface-form strings (case-insensitive) that map to this concept.
        description: Optional extended description.
        parent_id: ID of the parent concept for hierarchical ontologies.
        enabled: Whether this concept participates in mapping.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    domain: str
    entity_types: list[EntityType]
    aliases: list[str] = Field(default_factory=list)
    description: str = ""
    parent_id: str | None = None
    enabled: bool = True


class OntologyStore:
    """In-memory store for :class:`OntologyConcept` records.

    Pre-seeded with three sub-ontologies (healthcare, finance, technology).
    Supports full CRUD and a fast alias-based lookup used by the Map stage.
    """

    _DEFAULTS: list[dict[str, Any]] = [
        # ── Healthcare ────────────────────────────────────────────────────
        {
            "id": "MED_001",
            "label": "Patient",
            "domain": "healthcare",
            "entity_types": [EntityType.PERSON],
            "aliases": ["patient", "pt", "client"],
            "description": "An individual receiving medical care",
        },
        {
            "id": "MED_002",
            "label": "Diagnosis",
            "domain": "healthcare",
            "entity_types": [EntityType.MEDICAL],
            "aliases": ["diagnosis", "dx", "condition", "disorder", "disease", "syndrome"],
            "description": "A medical diagnosis or condition",
        },
        {
            "id": "MED_003",
            "label": "Medication",
            "domain": "healthcare",
            "entity_types": [EntityType.MEDICAL],
            "aliases": ["medication", "medicine", "drug", "prescription", "rx", "dosage"],
            "description": "A pharmaceutical substance or treatment",
        },
        {
            "id": "MED_004",
            "label": "Hospital",
            "domain": "healthcare",
            "entity_types": [EntityType.ORGANISATION, EntityType.LOCATION],
            "aliases": ["hospital", "clinic", "medical center", "health system", "er", "icu"],
            "description": "A healthcare facility",
        },
        # ── Finance ───────────────────────────────────────────────────────
        {
            "id": "FIN_001",
            "label": "Bank Account",
            "domain": "finance",
            "entity_types": [EntityType.FINANCIAL],
            "aliases": ["account number", "bank account", "iban", "routing number"],
            "description": "A financial account identifier",
        },
        {
            "id": "FIN_002",
            "label": "Transaction",
            "domain": "finance",
            "entity_types": [EntityType.FINANCIAL],
            "aliases": ["transaction", "payment", "transfer", "wire", "debit", "credit"],
            "description": "A financial transaction event",
        },
        {
            "id": "FIN_003",
            "label": "Company",
            "domain": "finance",
            "entity_types": [EntityType.ORGANISATION],
            "aliases": ["company", "corporation", "firm", "enterprise", "inc", "ltd", "llc", "plc"],
            "description": "A legal business entity",
        },
        {
            "id": "FIN_004",
            "label": "Invoice",
            "domain": "finance",
            "entity_types": [EntityType.FINANCIAL],
            "aliases": ["invoice", "bill", "receipt", "purchase order", "po"],
            "description": "A billing document",
        },
        # ── Technology ────────────────────────────────────────────────────
        {
            "id": "TECH_001",
            "label": "API Endpoint",
            "domain": "technology",
            "entity_types": [EntityType.URL],
            "aliases": ["api", "endpoint", "rest api", "graphql", "webhook", "url"],
            "description": "A software API endpoint",
        },
        {
            "id": "TECH_002",
            "label": "Server",
            "domain": "technology",
            "entity_types": [EntityType.IP_ADDRESS, EntityType.URL],
            "aliases": ["server", "host", "hostname", "vm", "instance", "node", "ip"],
            "description": "A computing server or host",
        },
        {
            "id": "TECH_003",
            "label": "Software Repository",
            "domain": "technology",
            "entity_types": [EntityType.URL, EntityType.OTHER],
            "aliases": ["repository", "repo", "github", "gitlab", "codebase", "git"],
            "description": "A source code repository",
        },
        # ── General ───────────────────────────────────────────────────────
        {
            "id": "GEN_001",
            "label": "Person Name",
            "domain": "general",
            "entity_types": [EntityType.PERSON],
            "aliases": [],
            "description": "A named individual",
        },
        {
            "id": "GEN_002",
            "label": "Geographic Location",
            "domain": "general",
            "entity_types": [EntityType.LOCATION],
            "aliases": ["city", "country", "state", "region", "address", "street", "zip", "postcode"],
            "description": "A geographic place or address",
        },
        {
            "id": "GEN_003",
            "label": "Date / Time",
            "domain": "general",
            "entity_types": [EntityType.DATE],
            "aliases": ["date", "time", "datetime", "timestamp", "schedule", "deadline"],
            "description": "A temporal reference",
        },
    ]

    def __init__(self) -> None:
        self._store: dict[str, OntologyConcept] = {}
        # alias → list[concept_id] for fast lookup
        self._alias_index: dict[str, list[str]] = {}
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        """Populate the store with built-in domain concepts."""
        for raw in self._DEFAULTS:
            concept = OntologyConcept(**raw)
            self._store[concept.id] = concept
            self._index_concept(concept)

    def _index_concept(self, concept: OntologyConcept) -> None:
        """Update the alias index for a concept.

        Args:
            concept: Concept to index.
        """
        for alias in concept.aliases:
            key = alias.lower().strip()
            if key not in self._alias_index:
                self._alias_index[key] = []
            if concept.id not in self._alias_index[key]:
                self._alias_index[key].append(concept.id)

    def _deindex_concept(self, concept: OntologyConcept) -> None:
        """Remove a concept from the alias index.

        Args:
            concept: Concept to deindex.
        """
        for alias in concept.aliases:
            key = alias.lower().strip()
            ids = self._alias_index.get(key, [])
            if concept.id in ids:
                ids.remove(concept.id)

    # ── CRUD ──────────────────────────────────────────────────────────────

    def list_all(self, domain: str | None = None) -> list[OntologyConcept]:
        """Return all concepts, optionally filtered by domain.

        Args:
            domain: If provided, only return concepts in this domain.

        Returns:
            Sorted list of OntologyConcept instances.
        """
        concepts = self._store.values()
        if domain:
            concepts = [c for c in concepts if c.domain == domain]  # type: ignore[assignment]
        return sorted(concepts, key=lambda c: c.id)

    def get(self, concept_id: str) -> OntologyConcept | None:
        """Retrieve a concept by ID.

        Args:
            concept_id: Concept ID string.

        Returns:
            OntologyConcept or None.
        """
        return self._store.get(concept_id)

    def create(self, concept: OntologyConcept) -> OntologyConcept:
        """Persist a new concept.

        Args:
            concept: Concept to store.

        Returns:
            Stored concept.

        Raises:
            ValueError: If concept ID already exists.
        """
        if concept.id in self._store:
            raise ValueError(f"OntologyConcept '{concept.id}' already exists.")
        self._store[concept.id] = concept
        self._index_concept(concept)
        return concept

    def update(self, concept_id: str, data: dict[str, Any]) -> OntologyConcept | None:
        """Update an existing concept.

        Args:
            concept_id: ID to update.
            data: Fields to update.

        Returns:
            Updated concept, or None if not found.
        """
        existing = self._store.get(concept_id)
        if not existing:
            return None
        self._deindex_concept(existing)
        updated = existing.model_copy(update=data)
        self._store[concept_id] = updated
        self._index_concept(updated)
        return updated

    def delete(self, concept_id: str) -> bool:
        """Delete a concept.

        Args:
            concept_id: Concept ID.

        Returns:
            True if deleted, False if not found.
        """
        existing = self._store.get(concept_id)
        if not existing:
            return False
        self._deindex_concept(existing)
        del self._store[concept_id]
        return True

    # ── Lookup ────────────────────────────────────────────────────────────

    def find_by_alias(
        self, text: str, entity_type: EntityType | None = None
    ) -> list[OntologyConcept]:
        """Find concepts whose aliases appear in *text*.

        Args:
            text: Input text to scan (case-insensitive).
            entity_type: Optional filter — only return concepts that list
                this type in ``entity_types``.

        Returns:
            De-duplicated list of matching OntologyConcept instances.
        """
        text_lower = text.lower()
        seen: set[str] = set()
        results: list[OntologyConcept] = []

        for alias, concept_ids in self._alias_index.items():
            if re.search(r"\b" + re.escape(alias) + r"\b", text_lower):
                for cid in concept_ids:
                    if cid in seen:
                        continue
                    concept = self._store.get(cid)
                    if concept and concept.enabled and (entity_type is None or entity_type in concept.entity_types):
                        results.append(concept)
                        seen.add(cid)

        return results

    def domains(self) -> list[str]:
        """Return all distinct domain names.

        Returns:
            Sorted list of domain strings.
        """
        return sorted({c.domain for c in self._store.values()})
