"""
File: workflows.py

Purpose:
REST API for the Visual Workflow Builder — CRUD for workflow graph definitions,
plus compile, deploy, and test-run endpoints.

Routes:
  GET    /workflows               — list saved workflows
  POST   /workflows               — create workflow
  GET    /workflows/{id}          — get workflow
  PUT    /workflows/{id}          — update workflow graph
  DELETE /workflows/{id}          — delete workflow
  POST   /workflows/{id}/deploy   — compile + deploy
  POST   /workflows/{id}/run      — test-run with input
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.api.stores import (
    workflow_def_create,
    workflow_def_delete,
    workflow_def_get,
    workflow_def_list,
    workflow_def_update,
)
from backend.core.engine import get_engine
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

router = APIRouter(prefix="/workflows", tags=["Visual Workflow Builder"])


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    graph: dict = Field(default_factory=lambda: {"nodes": [], "edges": []})


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    graph: dict | None = None


class WorkflowRunRequest(BaseModel):
    input: str = Field(..., min_length=1)


@router.get("", response_model=APIResponse[list])
async def list_workflows(user: Annotated[dict, Depends(get_current_user)]):
    wfs = workflow_def_list()
    return APIResponse(data=wfs)


@router.post("", response_model=APIResponse[dict])
async def create_workflow(
    payload: WorkflowCreate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
):
    wf = workflow_def_create({
        "name": payload.name,
        "description": payload.description,
        "graph": payload.graph,
        "userId": user["id"],
        "status": "draft",
    })
    return APIResponse(data=wf)


@router.get("/{wf_id}", response_model=APIResponse[dict])
async def get_workflow(wf_id: str, user: Annotated[dict, Depends(get_current_user)]):
    wf = workflow_def_get(wf_id)
    if not wf:
        raise NotFoundError("Workflow not found")
    return APIResponse(data=wf)


@router.put("/{wf_id}", response_model=APIResponse[dict])
async def update_workflow(
    wf_id: str,
    payload: WorkflowUpdate,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
):
    wf = workflow_def_get(wf_id)
    if not wf:
        raise NotFoundError("Workflow not found")
    data = payload.model_dump(exclude_none=True)
    updated = workflow_def_update(wf_id, data)
    return APIResponse(data=updated)


@router.delete("/{wf_id}", response_model=APIResponse[dict])
async def delete_workflow(
    wf_id: str,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
):
    if not workflow_def_get(wf_id):
        raise NotFoundError("Workflow not found")
    workflow_def_delete(wf_id)
    return APIResponse(data={"deleted": True})


@router.post("/{wf_id}/deploy", response_model=APIResponse[dict])
async def deploy_workflow(
    wf_id: str,
    user: Annotated[dict, Depends(check_role(["admin", "developer"]))],
):
    """Mark a workflow as deployed (compiled on first run)."""
    wf = workflow_def_get(wf_id)
    if not wf:
        raise NotFoundError("Workflow not found")
    # Validate: must have at least one node
    nodes = wf.get("graph", {}).get("nodes", [])
    if not nodes:
        raise HTTPException(status_code=400, detail="Workflow graph has no nodes")
    updated = workflow_def_update(wf_id, {"status": "deployed"})
    return APIResponse(data=updated)


@router.post("/{wf_id}/run")
async def run_workflow(
    wf_id: str,
    payload: WorkflowRunRequest,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Test-run a workflow and stream execution events via SSE."""
    wf = workflow_def_get(wf_id)
    if not wf:
        raise NotFoundError("Workflow not found")

    engine = get_engine()

    async def event_gen():
        async for event in engine.run_visual_workflow(
            graph_definition=wf,
            initial_input=payload.input,
            config={"userId": user["id"]},
        ):
            yield f"data: {json.dumps(event)}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
