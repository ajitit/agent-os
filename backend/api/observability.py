"""
File: observability.py

Purpose:
REST API for the Observability Dashboard — traces, spans, logs, metrics.

Routes:
  GET  /observability/metrics          — KPI snapshot
  GET  /observability/runs             — paginated run list (with filters)
  GET  /observability/runs/{run_id}    — run detail + spans
  GET  /observability/logs             — structured logs
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.api.stores import (
    metrics_snapshot,
    obs_log_list,
    run_get,
    run_list,
    span_list_by_run,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get("/metrics", response_model=APIResponse[dict])
async def get_metrics(user: Annotated[dict, Depends(get_current_user)]):
    """Return real-time KPI snapshot."""
    return APIResponse(data=metrics_snapshot())


@router.get("/runs", response_model=APIResponse[list])
async def list_runs(
    user: Annotated[dict, Depends(get_current_user)],
    workflow_id: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List workflow runs with optional filters."""
    runs = run_list(workflow_id=workflow_id, status=status, limit=limit)
    return APIResponse(data=runs)


@router.get("/runs/{run_id}", response_model=APIResponse[dict])
async def get_run(run_id: str, user: Annotated[dict, Depends(get_current_user)]):
    """Get a single run with its spans (trace detail)."""
    run = run_get(run_id)
    if not run:
        raise NotFoundError("Run not found")
    spans = span_list_by_run(run_id)
    return APIResponse(data={**run, "spans": spans})


@router.get("/logs", response_model=APIResponse[list])
async def get_logs(
    user: Annotated[dict, Depends(get_current_user)],
    run_id: str | None = Query(None),
    level: str | None = Query(None),
    limit: int = Query(200, ge=1, le=1000),
):
    """Fetch structured observability logs."""
    logs = obs_log_list(run_id=run_id, level=level, limit=limit)
    return APIResponse(data=logs)
