"""
File: api/plans.py

Supervisor Plan API — manages structured plans that the supervisor creates
before delegating work to agents and crews.

Every user request processed through the supervisor engine first produces a
Plan (goal → ordered task breakdown with agent assignments).  Plans can be
viewed, approved, or rejected by a human before execution begins.

Routes (all under /api/v1/plans):
    POST   /                        Create a plan (or let the engine create one)
    GET    /                        List plans (filter: status, userId)
    GET    /{plan_id}               Plan detail with all tasks
    PUT    /{plan_id}               Update plan fields
    DELETE /{plan_id}               Delete a plan
    POST   /{plan_id}/approve       Human approves → triggers execution event
    POST   /{plan_id}/reject        Human rejects → marks plan as rejected
    GET    /{plan_id}/tasks         List tasks for a plan
    POST   /{plan_id}/tasks         Add a task to a plan
    PUT    /{plan_id}/tasks/{tid}   Update a task (status, result, etc.)
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    audit_log,
    plan_create,
    plan_delete,
    plan_get,
    plan_list,
    plan_task_add,
    plan_task_list,
    plan_task_update,
    plan_update,
)
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plans", tags=["Supervisor Plans"])

# ── Request models ────────────────────────────────────────────────────────────


class PlanCreate(BaseModel):
    """Request body for creating a supervisor plan.

    Attributes:
        goal: High-level goal the plan addresses.
        workflow_id: Optional originating workflow ID.
        steps: Optional pre-defined step list; engine fills this if omitted.
        reasoning: Optional supervisor reasoning text.
        estimated_duration_minutes: Rough time estimate.
    """

    goal: str = Field(..., min_length=1, max_length=2000)
    workflow_id: str | None = None
    steps: list[str] = Field(default_factory=list)
    reasoning: str | None = None
    estimated_duration_minutes: int | None = Field(None, ge=1, le=10080)


class PlanUpdate(BaseModel):
    """Request body for updating a plan.

    Attributes:
        goal: Updated goal text.
        status: New status value.
        reasoning: Updated reasoning.
        estimated_duration_minutes: Updated estimate.
    """

    goal: str | None = Field(None, min_length=1, max_length=2000)
    status: Literal["draft", "planning", "approved", "executing", "complete", "failed"] | None = None
    reasoning: str | None = None
    estimated_duration_minutes: int | None = Field(None, ge=1, le=10080)


class PlanTaskCreate(BaseModel):
    """Request body for adding a task to a plan.

    Attributes:
        title: Short task title.
        description: Detailed task description.
        step_number: Execution order (1-based).
        assigned_to: Agent or crew ID.
        assigned_type: Whether assignee is an agent or crew.
        depends_on: Task IDs that must complete before this task.
    """

    title: str = Field(..., min_length=1, max_length=300)
    description: str = Field(default="", max_length=2000)
    step_number: int = Field(default=1, ge=1)
    assigned_to: str | None = None
    assigned_type: Literal["agent", "crew"] | None = None
    depends_on: list[str] = Field(default_factory=list)


class PlanTaskUpdate(BaseModel):
    """Request body for updating a plan task.

    Attributes:
        status: New task status.
        result: Task output or result text.
        started_at: ISO timestamp when task started.
        ended_at: ISO timestamp when task finished.
    """

    status: Literal["pending", "running", "complete", "failed", "skipped"] | None = None
    result: str | None = None
    started_at: str | None = None
    ended_at: str | None = None
    assigned_to: str | None = None
    assigned_type: Literal["agent", "crew"] | None = None


class RejectRequest(BaseModel):
    """Request body for rejecting a plan.

    Attributes:
        reason: Human-readable rejection reason.
    """

    reason: str = Field(default="", max_length=1000)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _get_or_404(plan_id: str) -> dict[str, Any]:
    """Fetch plan or raise 404.

    Args:
        plan_id: Plan UUID.

    Returns:
        Plan dict.

    Raises:
        HTTPException: 404 if not found.
    """
    plan = plan_get(plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post("", response_model=APIResponse[dict[str, Any]])
async def create_plan(
    payload: PlanCreate,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Create a new supervisor plan.

    The supervisor will decompose the goal into tasks. If a pre-defined
    step list is supplied it is used directly; otherwise the engine fills it
    during execution.

    Args:
        payload: Plan creation request.
        user: Authenticated user from JWT.

    Returns:
        APIResponse wrapping the created plan.
    """
    data: dict[str, Any] = {
        "goal": payload.goal,
        "userId": user["id"],
        "userName": user.get("name") or user.get("email", "unknown"),
        "status": "draft",
        "steps": payload.steps,
        "reasoning": payload.reasoning,
        "estimatedDurationMinutes": payload.estimated_duration_minutes,
    }
    if payload.workflow_id:
        data["workflowId"] = payload.workflow_id

    plan = plan_create(data)

    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", "unknown"),
        "action": "plan.created",
        "resourceType": "plan",
        "resourceId": plan["id"],
        "resourceName": payload.goal[:80],
        "outcome": "success",
    })
    logger.info("plan=created plan_id=%s user=%s", plan["id"], user["id"])
    return APIResponse(data=plan)


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_plans(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    plan_status: str | None = None,
    workflow_id: str | None = None,
    limit: int = 50,
) -> APIResponse[list[dict[str, Any]]]:
    """List supervisor plans with optional filters.

    Args:
        user: Authenticated user.
        plan_status: Filter by status (draft, approved, etc.)
        workflow_id: Filter by workflow.
        limit: Max records (default 50).

    Returns:
        APIResponse wrapping list of plan dicts.
    """
    plans = plan_list(workflow_id=workflow_id, status=plan_status, limit=limit)
    return APIResponse(data=plans)


@router.get("/{plan_id}", response_model=APIResponse[dict[str, Any]])
async def get_plan(
    plan_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Get a plan with its full task list.

    Args:
        plan_id: Plan UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping plan dict including tasks array.

    Raises:
        HTTPException: 404 if plan not found.
    """
    plan = _get_or_404(plan_id)
    tasks = plan_task_list(plan_id)
    return APIResponse(data={**plan, "tasks": tasks})


@router.put("/{plan_id}", response_model=APIResponse[dict[str, Any]])
async def update_plan(
    plan_id: str,
    payload: PlanUpdate,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Update plan fields.

    Args:
        plan_id: Plan UUID.
        payload: Fields to update.
        user: Authenticated user.

    Returns:
        APIResponse wrapping updated plan.

    Raises:
        HTTPException: 404 if plan not found.
    """
    _get_or_404(plan_id)
    update_data = payload.model_dump(exclude_none=True)
    plan = plan_update(plan_id, update_data)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "plan.updated",
        "resourceType": "plan",
        "resourceId": plan_id,
        "details": update_data,
        "outcome": "success",
    })
    return APIResponse(data=plan)  # type: ignore[arg-type]


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> None:
    """Delete a plan and all its tasks.

    Args:
        plan_id: Plan UUID.
        user: Authenticated user.

    Raises:
        HTTPException: 404 if plan not found.
    """
    _get_or_404(plan_id)
    plan_delete(plan_id)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "plan.deleted",
        "resourceType": "plan",
        "resourceId": plan_id,
        "outcome": "success",
    })
    logger.info("plan=deleted plan_id=%s user=%s", plan_id, user["id"])


@router.post("/{plan_id}/approve", response_model=APIResponse[dict[str, Any]])
async def approve_plan(
    plan_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Human approves a plan, transitioning it to executing state.

    Args:
        plan_id: Plan UUID.
        user: Authenticated reviewer.

    Returns:
        APIResponse wrapping updated plan.

    Raises:
        HTTPException: 404 if not found; 409 if already executed/rejected.
    """
    plan = _get_or_404(plan_id)
    if plan.get("status") in ("complete", "failed"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Plan is already {plan['status']} and cannot be approved",
        )
    updated = plan_update(plan_id, {
        "status": "approved",
        "approvedBy": user["id"],
        "approvedByName": user.get("email", ""),
    })
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "plan.approved",
        "resourceType": "plan",
        "resourceId": plan_id,
        "resourceName": plan.get("goal", "")[:80],
        "outcome": "success",
    })
    logger.info("plan=approved plan_id=%s approver=%s", plan_id, user["id"])
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.post("/{plan_id}/reject", response_model=APIResponse[dict[str, Any]])
async def reject_plan(
    plan_id: str,
    payload: RejectRequest,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Human rejects a plan.

    Args:
        plan_id: Plan UUID.
        payload: Optional rejection reason.
        user: Authenticated reviewer.

    Returns:
        APIResponse wrapping updated plan.

    Raises:
        HTTPException: 404 if not found.
    """
    plan = _get_or_404(plan_id)
    updated = plan_update(plan_id, {
        "status": "rejected",
        "rejectedBy": user["id"],
        "rejectionReason": payload.reason,
    })
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "plan.rejected",
        "resourceType": "plan",
        "resourceId": plan_id,
        "resourceName": plan.get("goal", "")[:80],
        "details": {"reason": payload.reason},
        "outcome": "success",
    })
    logger.info("plan=rejected plan_id=%s rejector=%s", plan_id, user["id"])
    return APIResponse(data=updated)  # type: ignore[arg-type]


# ── Task sub-routes ───────────────────────────────────────────────────────────


@router.get("/{plan_id}/tasks", response_model=APIResponse[list[dict[str, Any]]])
async def get_plan_tasks(
    plan_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[list[dict[str, Any]]]:
    """List all tasks for a plan.

    Args:
        plan_id: Plan UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping list of task dicts.

    Raises:
        HTTPException: 404 if plan not found.
    """
    _get_or_404(plan_id)
    return APIResponse(data=plan_task_list(plan_id))


@router.post("/{plan_id}/tasks", response_model=APIResponse[dict[str, Any]])
async def add_plan_task(
    plan_id: str,
    payload: PlanTaskCreate,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Add a task to an existing plan.

    Args:
        plan_id: Plan UUID.
        payload: Task creation request.
        user: Authenticated user.

    Returns:
        APIResponse wrapping created task.

    Raises:
        HTTPException: 404 if plan not found.
    """
    _get_or_404(plan_id)
    task_data: dict[str, Any] = {
        "title": payload.title,
        "description": payload.description,
        "stepNumber": payload.step_number,
        "dependsOn": payload.depends_on,
    }
    if payload.assigned_to:
        task_data["assignedTo"] = payload.assigned_to
    if payload.assigned_type:
        task_data["assignedType"] = payload.assigned_type

    task = plan_task_add(plan_id, task_data)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")

    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "plan_task.created",
        "resourceType": "plan_task",
        "resourceId": task["id"],
        "details": {"planId": plan_id, "title": payload.title},
        "outcome": "success",
    })
    return APIResponse(data=task)


@router.put("/{plan_id}/tasks/{task_id}", response_model=APIResponse[dict[str, Any]])
async def update_plan_task(
    plan_id: str,
    task_id: str,
    payload: PlanTaskUpdate,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Update a plan task (e.g. mark complete, record result).

    Args:
        plan_id: Plan UUID.
        task_id: Task UUID.
        payload: Fields to update.
        user: Authenticated user.

    Returns:
        APIResponse wrapping updated task.

    Raises:
        HTTPException: 404 if plan or task not found.
    """
    _get_or_404(plan_id)
    update_data = payload.model_dump(exclude_none=True)
    # Convert snake_case → camelCase for store
    remapped: dict[str, Any] = {}
    key_map = {
        "started_at": "startedAt",
        "ended_at": "endedAt",
        "assigned_to": "assignedTo",
        "assigned_type": "assignedType",
    }
    for k, v in update_data.items():
        remapped[key_map.get(k, k)] = v

    task = plan_task_update(plan_id, task_id, remapped)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "plan_task.updated",
        "resourceType": "plan_task",
        "resourceId": task_id,
        "details": remapped,
        "outcome": "success",
    })
    return APIResponse(data=task)
