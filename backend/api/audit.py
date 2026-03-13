"""
File: api/audit.py

Audit Log API — immutable, append-only audit trail for every action performed
by humans, agents, crews, and the system.

Every significant operation in the platform calls ``audit_log()`` from
``backend.api.stores``.  This module exposes read-only query, stats, and
CSV-export endpoints so operators can investigate incidents and prove
compliance.

Routes (all under /api/v1/audit):
    GET  /              Filtered, paginated event list
    GET  /stats         Aggregate statistics (counts by type, top actions, daily)
    GET  /export        CSV download of filtered results
    GET  /{audit_id}    Single event detail
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from backend.api.stores import audit_get, audit_list, audit_stats
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit Log"])

# CSV column order
_CSV_FIELDS: list[str] = [
    "id",
    "timestamp",
    "actorType",
    "actorId",
    "actorName",
    "action",
    "resourceType",
    "resourceId",
    "resourceName",
    "outcome",
    "durationMs",
    "ip",
]


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_audit_events(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    actor_type: str | None = Query(None, description="human | agent | crew | system"),
    actor_id: str | None = Query(None),
    resource_type: str | None = Query(None),
    resource_id: str | None = Query(None),
    action: str | None = Query(None, description="e.g. plan.approved"),
    from_date: str | None = Query(None, description="ISO datetime lower bound"),
    to_date: str | None = Query(None, description="ISO datetime upper bound"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> APIResponse[list[dict[str, Any]]]:
    """Query the audit log with flexible filters.

    Returns entries newest-first.  Use ``offset`` + ``limit`` for pagination.

    Args:
        user: Authenticated user.
        actor_type: Filter by who performed the action.
        actor_id: Filter by specific actor UUID.
        resource_type: Filter by resource type (plan, agent, workflow…).
        resource_id: Filter by specific resource UUID.
        action: Exact action string match.
        from_date: ISO timestamp lower bound.
        to_date: ISO timestamp upper bound.
        limit: Maximum records to return (1–1000).
        offset: Records to skip for pagination.

    Returns:
        APIResponse wrapping list of audit event dicts.
    """
    events = audit_list(
        actor_type=actor_type,
        actor_id=actor_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return APIResponse(data=events)


@router.get("/stats", response_model=APIResponse[dict[str, Any]])
async def get_audit_stats(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Return aggregate audit statistics.

    Includes total event count, breakdown by actor type and outcome, and
    a 30-day rolling daily-count series.

    Args:
        user: Authenticated user.

    Returns:
        APIResponse wrapping stats dict.
    """
    stats = audit_stats()
    return APIResponse(data=stats)


@router.get("/export")
async def export_audit_csv(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    actor_type: str | None = Query(None),
    actor_id: str | None = Query(None),
    resource_type: str | None = Query(None),
    action: str | None = Query(None),
    from_date: str | None = Query(None),
    to_date: str | None = Query(None),
    limit: int = Query(10000, ge=1, le=50000),
) -> StreamingResponse:
    """Export filtered audit events as a CSV download.

    The CSV contains a fixed set of columns defined by ``_CSV_FIELDS``.
    Any missing field in an event is written as an empty string.

    Args:
        user: Authenticated user.
        actor_type: Optional actor type filter.
        actor_id: Optional actor ID filter.
        resource_type: Optional resource type filter.
        action: Optional action filter.
        from_date: Optional start date filter.
        to_date: Optional end date filter.
        limit: Maximum rows to export.

    Returns:
        StreamingResponse with ``text/csv`` content-type.
    """
    events = audit_list(
        actor_type=actor_type,
        actor_id=actor_id,
        resource_type=resource_type,
        action=action,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=_CSV_FIELDS,
        extrasaction="ignore",
    )
    writer.writeheader()
    for event in events:
        row = {field: event.get(field, "") for field in _CSV_FIELDS}
        writer.writerow(row)

    csv_content = output.getvalue()

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit_export.csv"},
    )


@router.get("/{audit_id}", response_model=APIResponse[dict[str, Any]])
async def get_audit_event(
    audit_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Get a single audit event by ID.

    Args:
        audit_id: Audit record UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping the audit event dict.

    Raises:
        HTTPException: 404 if event not found.
    """
    event = audit_get(audit_id)
    if not event:
        raise NotFoundError("Audit event not found")
    return APIResponse(data=event)
