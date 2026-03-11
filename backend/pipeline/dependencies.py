"""
Pipeline dependencies — FastAPI ``Depends()`` factories.

All pipeline singletons are created once at import time and exposed via
getter functions so route handlers never instantiate services directly.

Usage in route handlers::

    from backend.pipeline.dependencies import get_orchestrator

    @router.post("/process")
    async def process(
        orchestrator: Annotated[PipelineOrchestrator, Depends(get_orchestrator)],
    ) -> ...:
        ...
"""

from __future__ import annotations

from functools import lru_cache

from backend.pipeline.memory.pattern_store import FilterPatternStore, MaskPatternStore
from backend.pipeline.ontology.ontology_store import OntologyStore
from backend.pipeline.orchestrator import PipelineOrchestrator, PipelineRunStore
from backend.pipeline.stages.review_stage import ReviewLoopStage


@lru_cache(maxsize=1)
def get_filter_store() -> FilterPatternStore:
    """Return the singleton FilterPatternStore.

    Returns:
        Application-wide FilterPatternStore instance.
    """
    return FilterPatternStore()


@lru_cache(maxsize=1)
def get_mask_store() -> MaskPatternStore:
    """Return the singleton MaskPatternStore.

    Returns:
        Application-wide MaskPatternStore instance.
    """
    return MaskPatternStore()


@lru_cache(maxsize=1)
def get_ontology_store() -> OntologyStore:
    """Return the singleton OntologyStore.

    Returns:
        Application-wide OntologyStore instance.
    """
    return OntologyStore()


@lru_cache(maxsize=1)
def get_review_stage() -> ReviewLoopStage:
    """Return the singleton ReviewLoopStage.

    Returns:
        Application-wide ReviewLoopStage instance.
    """
    return ReviewLoopStage(timeout_seconds=3600.0)


@lru_cache(maxsize=1)
def get_run_store() -> PipelineRunStore:
    """Return the singleton PipelineRunStore.

    Returns:
        Application-wide PipelineRunStore instance.
    """
    return PipelineRunStore()


@lru_cache(maxsize=1)
def get_orchestrator() -> PipelineOrchestrator:
    """Return the singleton PipelineOrchestrator.

    Wires together all stores and stages.

    Returns:
        Application-wide PipelineOrchestrator instance.
    """
    return PipelineOrchestrator(
        filter_store=get_filter_store(),
        mask_store=get_mask_store(),
        ontology_store=get_ontology_store(),
        review_stage=get_review_stage(),
        run_store=get_run_store(),
    )
