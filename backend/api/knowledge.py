"""
Module: api/knowledge.py

FastAPI router for the Knowledge Management module.  Exposes endpoints
for source management and semantic vector search.

All external services (VectorSearchEngine, SourceManager) are lazily
instantiated on first request via Depends() — never at import time — so
the module can be imported in test environments without triggering
heavyweight ML model loading.

Routes (all under /api/v1/knowledge):
    POST   /sources              Ingest a new knowledge source
    GET    /sources              List sources (optional type filter)
    DELETE /sources/{source_id}  Remove a source
    POST   /sources/{source_id}/refresh  Re-process a source
    POST   /search               Semantic search over stored chunks
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, status
from pydantic import BaseModel, Field

from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user
from backend.knowledge.manager import SourceManager
from backend.knowledge.vector import VectorSearchEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])

# ── Lazy singletons ───────────────────────────────────────────────────────────
# Instantiated on first request, NOT at module import time.

_vector_engine: VectorSearchEngine | None = None
_manager: SourceManager | None = None


def get_vector_engine() -> VectorSearchEngine:
    """Return (or lazily create) the singleton VectorSearchEngine.

    Returns:
        Shared VectorSearchEngine instance.
    """
    global _vector_engine
    if _vector_engine is None:
        _vector_engine = VectorSearchEngine()
    return _vector_engine


def get_manager(
    engine: Annotated[VectorSearchEngine, Depends(get_vector_engine)],
) -> SourceManager:
    """Return (or lazily create) the singleton SourceManager.

    Args:
        engine: Vector engine dependency (injected by FastAPI).

    Returns:
        Shared SourceManager instance.
    """
    global _manager
    if _manager is None:
        _manager = SourceManager(engine)
    return _manager


# ── Request/Response models ───────────────────────────────────────────────────


class SourceCreateItem(BaseModel):
    """Request body for creating a knowledge source.

    Attributes:
        name: Human-readable source name.
        type: Source type identifier (e.g. 'web', 'pdf', 'text').
        url: Optional URL for the source content.
        tags: Optional classification tags.
    """

    name: str = Field(..., min_length=1, max_length=300)
    type: str = Field(..., min_length=1, max_length=50)
    url: str | None = None
    tags: list[str] = Field(default_factory=list)


class SearchQuery(BaseModel):
    """Request body for semantic knowledge search.

    Attributes:
        query: Natural-language search query.
        top_k: Maximum number of results to return.
        filters: Optional metadata filters.
    """

    query: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=50)
    filters: dict[str, Any] | None = None


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post("/sources", status_code=status.HTTP_201_CREATED)
async def create_source(
    item: SourceCreateItem,
    background_tasks: BackgroundTasks,
    mgr: Annotated[SourceManager, Depends(get_manager)],
    user: Annotated[dict, Depends(get_current_user)],
) -> APIResponse[dict]:
    """Ingest a new knowledge source.

    Args:
        item: Source creation request.
        background_tasks: FastAPI background task runner.
        mgr: SourceManager dependency.
        user: Authenticated user (injected by FastAPI).

    Returns:
        Created source record.
    """
    source: dict[str, Any] = await mgr.add_source(
        name=item.name,
        source_type=item.type,
        url=item.url,
        tags=item.tags,
    )
    if item.url:
        background_tasks.add_task(mgr.process_source, source["id"])
    logger.info("knowledge=source_created id=%s type=%s", source["id"], item.type)
    return APIResponse(data=source)


@router.get("/sources")
async def list_sources(
    mgr: Annotated[SourceManager, Depends(get_manager)],
    user: Annotated[dict, Depends(get_current_user)],
    type: str | None = None,
) -> APIResponse[list]:
    """List knowledge sources with optional type filter.

    Args:
        mgr: SourceManager dependency.
        user: Authenticated user (injected by FastAPI).
        type: Optional source type to filter on.

    Returns:
        List of source records.
    """
    filters: dict[str, Any] = {}
    if type:
        filters["type"] = type
    return APIResponse(data=mgr.list_sources(filters))  # type: ignore[return-value]


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: str,
    mgr: Annotated[SourceManager, Depends(get_manager)],
    user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Remove a knowledge source and its stored chunks.

    Args:
        source_id: Source UUID.
        mgr: SourceManager dependency.
        user: Authenticated user (injected by FastAPI).

    Raises:
        NotFoundError: If source not found.
    """
    if not mgr.delete_source(source_id):
        raise NotFoundError("Source not found")
    logger.info("knowledge=source_deleted id=%s", source_id)


@router.post("/sources/{source_id}/refresh")
async def refresh_source(
    source_id: str,
    background_tasks: BackgroundTasks,
    mgr: Annotated[SourceManager, Depends(get_manager)],
    user: Annotated[dict, Depends(get_current_user)],
) -> APIResponse[dict]:
    """Queue a source for re-processing in the background.

    Args:
        source_id: Source UUID.
        background_tasks: FastAPI background task runner.
        mgr: SourceManager dependency.
        user: Authenticated user (injected by FastAPI).

    Returns:
        Status message.
    """
    background_tasks.add_task(mgr.process_source, source_id)
    return APIResponse(data={"status": "refreshing"})


@router.post("/search")
async def search_knowledge(
    query: SearchQuery,
    engine: Annotated[VectorSearchEngine, Depends(get_vector_engine)],
    user: Annotated[dict, Depends(get_current_user)],
) -> APIResponse[dict]:
    """Perform semantic search over ingested knowledge chunks.

    Args:
        query: Search request with query text and optional filters.
        engine: VectorSearchEngine dependency.
        user: Authenticated user (injected by FastAPI).

    Returns:
        Dict with ``results`` list of matching chunks.
    """
    results = engine.search(
        query=query.query,
        n_results=query.top_k,
        where=query.filters,
    )
    return APIResponse(data={"results": results})
