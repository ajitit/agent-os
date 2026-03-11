"""
Stage 3 — Map.

Maps extracted entities to concepts in the
:class:`~backend.pipeline.ontology.ontology_store.OntologyStore`.

For each entity produced by the Extract stage the mapper:

1. Performs a direct alias lookup in the ontology.
2. If no alias hit, falls back to entity-type-based concept lookup.
3. Attaches matching ontology IDs back onto the entity (mutated copy).
"""

from __future__ import annotations

from backend.pipeline.base import BaseStage
from backend.pipeline.models import (
    Entity,
    MapResult,
    OntologyMatch,
    PipelineContext,
)
from backend.pipeline.ontology.ontology_store import OntologyStore


class MapStage(BaseStage):
    """Stage 3: map extracted entities to ontology concepts.

    Attributes:
        stage_name: Always ``"map"``.
    """

    stage_name = "map"

    def __init__(self, store: OntologyStore) -> None:
        """Initialise the stage with an ontology store.

        Args:
            store: The ontology concept store.
        """
        self._store = store

    async def process(self, ctx: PipelineContext) -> PipelineContext:
        """Map entities in ``ctx.extract_result`` to ontology concepts.

        Args:
            ctx: Current pipeline context.

        Returns:
            Context with ``map_result`` populated.  Entities in
            ``extract_result`` are replaced with copies that carry their
            ``ontology_ids``.
        """
        if not ctx.extract_result:
            return ctx.with_update(map_result=MapResult())

        mappings: list[OntologyMatch] = []
        unmapped = 0
        enriched_entities: list[Entity] = []

        for entity in ctx.extract_result.entities:
            # Try alias-based lookup first
            concepts = self._store.find_by_alias(entity.text, entity.entity_type)

            # Fallback: lookup by entity type alone
            if not concepts:
                concepts = self._store.find_by_alias("", entity.entity_type)

            if concepts:
                ontology_ids = [c.id for c in concepts]
                # Add a mapping record for each matched concept
                for concept in concepts:
                    mappings.append(
                        OntologyMatch(
                            entity_text=entity.text,
                            entity_type=entity.entity_type,
                            ontology_id=concept.id,
                            ontology_label=concept.label,
                            confidence=entity.confidence * 0.9,
                        )
                    )
                enriched_entities.append(
                    entity.model_copy(update={"ontology_ids": ontology_ids})
                )
            else:
                unmapped += 1
                enriched_entities.append(entity)

        # Rebuild extract_result with enriched entities
        enriched_extract = ctx.extract_result.model_copy(
            update={"entities": enriched_entities}
        )

        return ctx.with_update(
            extract_result=enriched_extract,
            map_result=MapResult(mappings=mappings, unmapped_count=unmapped),
        )
