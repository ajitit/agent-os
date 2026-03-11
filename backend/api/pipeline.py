"""
File: api/pipeline.py

REST API for the 9-stage input processing pipeline.

Routes
------
POST   /pipeline/process              — run full pipeline (stages 1-8, opt. stage 9)
GET    /pipeline/runs                 — list pipeline run records
GET    /pipeline/runs/{run_id}        — get single run detail

POST   /pipeline/review/{run_id}/respond — submit human review decision
GET    /pipeline/review/pending          — list runs awaiting review

GET    /pipeline/memory/filter            — list filter patterns
POST   /pipeline/memory/filter            — create filter pattern
PUT    /pipeline/memory/filter/{id}       — update filter pattern
DELETE /pipeline/memory/filter/{id}       — delete filter pattern

GET    /pipeline/memory/mask              — list mask patterns
POST   /pipeline/memory/mask              — create mask pattern
PUT    /pipeline/memory/mask/{id}         — update mask pattern
DELETE /pipeline/memory/mask/{id}         — delete mask pattern

GET    /pipeline/ontology                 — list ontology concepts
POST   /pipeline/ontology                 — create concept
GET    /pipeline/ontology/{id}            — get concept
PUT    /pipeline/ontology/{id}            — update concept
DELETE /pipeline/ontology/{id}            — delete concept
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user
from backend.pipeline.dependencies import (
    get_filter_store,
    get_mask_store,
    get_ontology_store,
    get_orchestrator,
)
from backend.pipeline.memory.pattern_store import (
    FilterPattern,
    FilterPatternStore,
    MaskPattern,
    MaskPatternStore,
)
from backend.pipeline.models import (
    EntityType,
    FilterVerdict,
    PipelineContext,
    ReviewFeedback,
)
from backend.pipeline.ontology.ontology_store import OntologyConcept, OntologyStore
from backend.pipeline.orchestrator import PipelineOrchestrator

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


# ── Request / Response models ─────────────────────────────────────────────────


class ProcessRequest(BaseModel):
    """Request body for POST /pipeline/process.

    Attributes:
        text: Raw user input to process through the pipeline.
        require_review: If True, pipeline pauses at stage 9 for human approval.
    """

    text: str = Field(..., min_length=1, max_length=10_000)
    require_review: bool = False


class ProcessResponse(BaseModel):
    """Summary response after pipeline processing.

    Attributes:
        run_id: Unique identifier for this run.
        status: Final pipeline status.
        filter_verdict: Result of the filter stage.
        filter_reason: Human-readable filter explanation.
        entity_count: Number of extracted entities.
        mask_count: Number of tokens masked.
        category: Detected content category.
        intent: Detected user intent.
        route_primary: Primary routing target agent name.
        final_result: Composed output (None if blocked).
        stage_errors: Any non-fatal stage errors.
        blocked_message: Human-facing block message (if blocked).
    """

    run_id: str
    status: str
    filter_verdict: str | None
    filter_reason: str | None
    entity_count: int
    mask_count: int
    category: str | None
    intent: str | None
    route_primary: str | None
    final_result: str | None
    stage_errors: dict[str, str]
    blocked_message: str | None = None


class ReviewDecisionRequest(BaseModel):
    """Body for POST /pipeline/review/{run_id}/respond.

    Attributes:
        approved: Whether the result is accepted.
        comment: Optional reviewer comment.
        modifications: Key-value corrections.
    """

    approved: bool
    comment: str | None = None
    modifications: dict[str, Any] = Field(default_factory=dict)


class FilterPatternCreate(BaseModel):
    """Body for creating a filter pattern.

    Attributes:
        name: Human-readable label.
        verdict: Verdict on match.
        pattern: Python regex string.
        description: Optional explanation.
        enabled: Whether active.
    """

    name: str = Field(..., min_length=1, max_length=200)
    verdict: FilterVerdict
    pattern: str = Field(..., min_length=1)
    description: str = ""
    enabled: bool = True


class FilterPatternUpdate(BaseModel):
    """Body for updating a filter pattern."""

    name: str | None = None
    verdict: FilterVerdict | None = None
    pattern: str | None = None
    description: str | None = None
    enabled: bool | None = None


class MaskPatternCreate(BaseModel):
    """Body for creating a mask pattern."""

    name: str = Field(..., min_length=1, max_length=200)
    pattern: str = Field(..., min_length=1)
    placeholder: str = Field(..., min_length=1, max_length=50)
    description: str = ""
    enabled: bool = True


class MaskPatternUpdate(BaseModel):
    """Body for updating a mask pattern."""

    name: str | None = None
    pattern: str | None = None
    placeholder: str | None = None
    description: str | None = None
    enabled: bool | None = None


class OntologyConceptCreate(BaseModel):
    """Body for creating an ontology concept."""

    id: str = Field(..., min_length=1, max_length=50)
    label: str = Field(..., min_length=1, max_length=200)
    domain: str = Field(..., min_length=1, max_length=100)
    entity_types: list[EntityType]
    aliases: list[str] = Field(default_factory=list)
    description: str = ""
    parent_id: str | None = None


class OntologyConceptUpdate(BaseModel):
    """Body for updating an ontology concept."""

    label: str | None = None
    domain: str | None = None
    entity_types: list[EntityType] | None = None
    aliases: list[str] | None = None
    description: str | None = None
    enabled: bool | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────


def _ctx_to_response(ctx: PipelineContext) -> ProcessResponse:
    """Convert a PipelineContext to a ProcessResponse.

    Args:
        ctx: Completed pipeline context.

    Returns:
        ProcessResponse summary.
    """
    blocked_msg: str | None = None
    if ctx.filter_result and ctx.filter_result.verdict.value != "pass":
        blocked_msg = ctx.filter_result.reason

    return ProcessResponse(
        run_id=ctx.run_id,
        status=ctx.status.value,
        filter_verdict=ctx.filter_result.verdict.value if ctx.filter_result else None,
        filter_reason=ctx.filter_result.reason if ctx.filter_result else None,
        entity_count=ctx.extract_result.entity_count if ctx.extract_result else 0,
        mask_count=ctx.mask_result.mask_count if ctx.mask_result else 0,
        category=ctx.classify_result.category if ctx.classify_result else None,
        intent=ctx.classify_result.intent if ctx.classify_result else None,
        route_primary=(
            ctx.route_result.primary.agent_name
            if ctx.route_result and ctx.route_result.primary
            else None
        ),
        final_result=ctx.final_result,
        stage_errors=ctx.stage_errors,
        blocked_message=blocked_msg,
    )


# ── Pipeline processing ───────────────────────────────────────────────────────


@router.post("/process", response_model=APIResponse[ProcessResponse])
async def process_input(
    payload: ProcessRequest,
    user: Annotated[dict, Depends(get_current_user)],
    orchestrator: Annotated[PipelineOrchestrator, Depends(get_orchestrator)],
) -> APIResponse[ProcessResponse]:
    """Run user input through the full 9-stage pipeline.

    Stages:

    1. Filter — block junk / personal / confidential content.
    2. Extract — named entity recognition.
    3. Map — entity to ontology concept mapping.
    4. Mask — redact sensitive tokens.
    5. Route — select target agents.
    6. Classify — intent, category, sentiment.
    7. Aggregate — synthesise agent outputs.
    8. Result — compose final response.
    9. Review — optional human-in-the-loop approval.

    Args:
        payload: Request body.
        user: Authenticated user (from JWT).
        orchestrator: Injected PipelineOrchestrator singleton.

    Returns:
        APIResponse wrapping a ProcessResponse summary.
    """
    ctx = await orchestrator.run(
        text=payload.text,
        user_id=user["id"],
        require_review=payload.require_review,
    )
    return APIResponse(data=_ctx_to_response(ctx))


@router.get("/runs", response_model=APIResponse[list[dict]])
async def list_runs(
    user: Annotated[dict, Depends(get_current_user)],
    orchestrator: Annotated[PipelineOrchestrator, Depends(get_orchestrator)],
    limit: int = 50,
) -> APIResponse[list[dict]]:
    """List recent pipeline runs.

    Args:
        user: Authenticated user.
        orchestrator: Injected orchestrator.
        limit: Maximum number of records to return.

    Returns:
        APIResponse wrapping a list of run record dicts.
    """
    return APIResponse(data=orchestrator.run_store.list(limit=limit))


@router.get("/runs/{run_id}", response_model=APIResponse[dict])
async def get_run(
    run_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    orchestrator: Annotated[PipelineOrchestrator, Depends(get_orchestrator)],
) -> APIResponse[dict]:
    """Get a single pipeline run record.

    Args:
        run_id: Pipeline run identifier.
        user: Authenticated user.
        orchestrator: Injected orchestrator.

    Returns:
        APIResponse wrapping the run record dict.

    Raises:
        HTTPException: 404 if run_id not found.
    """
    record = orchestrator.run_store.get(run_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return APIResponse(data=record)


# ── Human review ──────────────────────────────────────────────────────────────


@router.get("/review/pending", response_model=APIResponse[list[dict]])
async def list_pending_reviews(
    user: Annotated[dict, Depends(get_current_user)],
    orchestrator: Annotated[PipelineOrchestrator, Depends(get_orchestrator)],
) -> APIResponse[list[dict]]:
    """List all pipeline runs currently awaiting human review.

    Args:
        user: Authenticated user.
        orchestrator: Injected orchestrator.

    Returns:
        APIResponse wrapping list of pending review summaries.
    """
    return APIResponse(data=orchestrator.pending_reviews())


@router.post("/review/{run_id}/respond", response_model=APIResponse[dict])
async def respond_to_review(
    run_id: str,
    payload: ReviewDecisionRequest,
    user: Annotated[dict, Depends(get_current_user)],
    orchestrator: Annotated[PipelineOrchestrator, Depends(get_orchestrator)],
) -> APIResponse[dict]:
    """Submit a human review decision for a paused pipeline run.

    Args:
        run_id: Run to respond to.
        payload: Review decision.
        user: Authenticated user (becomes ``reviewer_id``).
        orchestrator: Injected orchestrator.

    Returns:
        APIResponse confirming the decision.

    Raises:
        HTTPException: 404 if run_id not found or already resolved.
    """
    feedback = ReviewFeedback(
        approved=payload.approved,
        comment=payload.comment,
        modifications=payload.modifications,
        reviewer_id=user["id"],
    )
    success = orchestrator.resume_review(run_id, feedback)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found or already resolved",
        )
    return APIResponse(data={"run_id": run_id, "approved": payload.approved})


# ── Long-term memory: filter patterns ────────────────────────────────────────


@router.get("/memory/filter", response_model=APIResponse[list[dict]])
async def list_filter_patterns(
    user: Annotated[dict, Depends(get_current_user)],
    store: Annotated[FilterPatternStore, Depends(get_filter_store)],
) -> APIResponse[list[dict]]:
    """List all filter patterns from long-term memory.

    Args:
        user: Authenticated user.
        store: Injected FilterPatternStore.

    Returns:
        APIResponse wrapping list of filter pattern dicts.
    """
    return APIResponse(data=[p.model_dump() for p in store.list_all()])


@router.post("/memory/filter", response_model=APIResponse[dict])
async def create_filter_pattern(
    payload: FilterPatternCreate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[FilterPatternStore, Depends(get_filter_store)],
) -> APIResponse[dict]:
    """Create a new filter pattern in long-term memory.

    Args:
        payload: Pattern definition.
        user: Admin or developer user.
        store: Injected FilterPatternStore.

    Returns:
        APIResponse wrapping the created pattern.
    """
    pattern = FilterPattern(**payload.model_dump())
    created = store.create(pattern)
    return APIResponse(data=created.model_dump())


@router.put("/memory/filter/{pattern_id}", response_model=APIResponse[dict])
async def update_filter_pattern(
    pattern_id: str,
    payload: FilterPatternUpdate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[FilterPatternStore, Depends(get_filter_store)],
) -> APIResponse[dict]:
    """Update an existing filter pattern.

    Args:
        pattern_id: Pattern UUID.
        payload: Fields to update.
        user: Admin or developer user.
        store: Injected FilterPatternStore.

    Returns:
        APIResponse wrapping the updated pattern.

    Raises:
        HTTPException: 404 if pattern_id not found.
    """
    updated = store.update(pattern_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Filter pattern not found")
    return APIResponse(data=updated.model_dump())


@router.delete("/memory/filter/{pattern_id}", response_model=APIResponse[dict])
async def delete_filter_pattern(
    pattern_id: str,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[FilterPatternStore, Depends(get_filter_store)],
) -> APIResponse[dict]:
    """Delete a filter pattern.

    Args:
        pattern_id: Pattern UUID.
        user: Admin or developer user.
        store: Injected FilterPatternStore.

    Returns:
        APIResponse confirming deletion.

    Raises:
        HTTPException: 404 if pattern_id not found.
    """
    if not store.delete(pattern_id):
        raise HTTPException(status_code=404, detail="Filter pattern not found")
    return APIResponse(data={"deleted": True})


# ── Long-term memory: mask patterns ──────────────────────────────────────────


@router.get("/memory/mask", response_model=APIResponse[list[dict]])
async def list_mask_patterns(
    user: Annotated[dict, Depends(get_current_user)],
    store: Annotated[MaskPatternStore, Depends(get_mask_store)],
) -> APIResponse[list[dict]]:
    """List all mask patterns from long-term memory.

    Args:
        user: Authenticated user.
        store: Injected MaskPatternStore.

    Returns:
        APIResponse wrapping list of mask pattern dicts.
    """
    return APIResponse(data=[p.model_dump() for p in store.list_all()])


@router.post("/memory/mask", response_model=APIResponse[dict])
async def create_mask_pattern(
    payload: MaskPatternCreate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[MaskPatternStore, Depends(get_mask_store)],
) -> APIResponse[dict]:
    """Create a new mask pattern.

    Args:
        payload: Pattern definition.
        user: Admin or developer user.
        store: Injected MaskPatternStore.

    Returns:
        APIResponse wrapping the created pattern.
    """
    pattern = MaskPattern(**payload.model_dump())
    created = store.create(pattern)
    return APIResponse(data=created.model_dump())


@router.put("/memory/mask/{pattern_id}", response_model=APIResponse[dict])
async def update_mask_pattern(
    pattern_id: str,
    payload: MaskPatternUpdate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[MaskPatternStore, Depends(get_mask_store)],
) -> APIResponse[dict]:
    """Update an existing mask pattern.

    Args:
        pattern_id: Pattern UUID.
        payload: Fields to update.
        user: Admin or developer user.
        store: Injected MaskPatternStore.

    Returns:
        APIResponse wrapping the updated pattern.

    Raises:
        HTTPException: 404 if pattern_id not found.
    """
    updated = store.update(pattern_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Mask pattern not found")
    return APIResponse(data=updated.model_dump())


@router.delete("/memory/mask/{pattern_id}", response_model=APIResponse[dict])
async def delete_mask_pattern(
    pattern_id: str,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[MaskPatternStore, Depends(get_mask_store)],
) -> APIResponse[dict]:
    """Delete a mask pattern.

    Args:
        pattern_id: Pattern UUID.
        user: Admin or developer user.
        store: Injected MaskPatternStore.

    Returns:
        APIResponse confirming deletion.

    Raises:
        HTTPException: 404 if pattern_id not found.
    """
    if not store.delete(pattern_id):
        raise HTTPException(status_code=404, detail="Mask pattern not found")
    return APIResponse(data={"deleted": True})


# ── Ontology ──────────────────────────────────────────────────────────────────


@router.get("/ontology", response_model=APIResponse[list[dict]])
async def list_ontology(
    user: Annotated[dict, Depends(get_current_user)],
    store: Annotated[OntologyStore, Depends(get_ontology_store)],
    domain: str | None = None,
) -> APIResponse[list[dict]]:
    """List all ontology concepts, optionally filtered by domain.

    Args:
        user: Authenticated user.
        store: Injected OntologyStore.
        domain: Optional domain filter.

    Returns:
        APIResponse wrapping list of concept dicts.
    """
    return APIResponse(data=[c.model_dump() for c in store.list_all(domain=domain)])


@router.post("/ontology", response_model=APIResponse[dict])
async def create_concept(
    payload: OntologyConceptCreate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[OntologyStore, Depends(get_ontology_store)],
) -> APIResponse[dict]:
    """Create a new ontology concept.

    Args:
        payload: Concept definition.
        user: Admin or developer user.
        store: Injected OntologyStore.

    Returns:
        APIResponse wrapping the created concept.
    """
    concept = OntologyConcept(**payload.model_dump())
    try:
        created = store.create(concept)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return APIResponse(data=created.model_dump())


@router.get("/ontology/{concept_id}", response_model=APIResponse[dict])
async def get_concept(
    concept_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    store: Annotated[OntologyStore, Depends(get_ontology_store)],
) -> APIResponse[dict]:
    """Get a single ontology concept.

    Args:
        concept_id: Concept identifier.
        user: Authenticated user.
        store: Injected OntologyStore.

    Returns:
        APIResponse wrapping the concept dict.

    Raises:
        HTTPException: 404 if concept_id not found.
    """
    concept = store.get(concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Ontology concept not found")
    return APIResponse(data=concept.model_dump())


@router.put("/ontology/{concept_id}", response_model=APIResponse[dict])
async def update_concept(
    concept_id: str,
    payload: OntologyConceptUpdate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[OntologyStore, Depends(get_ontology_store)],
) -> APIResponse[dict]:
    """Update an ontology concept.

    Args:
        concept_id: Concept identifier.
        payload: Fields to update.
        user: Admin or developer user.
        store: Injected OntologyStore.

    Returns:
        APIResponse wrapping the updated concept.

    Raises:
        HTTPException: 404 if concept_id not found.
    """
    updated = store.update(concept_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Ontology concept not found")
    return APIResponse(data=updated.model_dump())


@router.delete("/ontology/{concept_id}", response_model=APIResponse[dict])
async def delete_concept(
    concept_id: str,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
    store: Annotated[OntologyStore, Depends(get_ontology_store)],
) -> APIResponse[dict]:
    """Delete an ontology concept.

    Args:
        concept_id: Concept identifier.
        user: Admin or developer user.
        store: Injected OntologyStore.

    Returns:
        APIResponse confirming deletion.

    Raises:
        HTTPException: 404 if concept_id not found.
    """
    if not store.delete(concept_id):
        raise HTTPException(status_code=404, detail="Ontology concept not found")
    return APIResponse(data={"deleted": True})
