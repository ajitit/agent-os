"""
File: supervisor.py

Purpose:
Implements a Supervisor API enabling Human-in-the-Loop workflows, allowing execution
to pause for human approval before proceeding.

Key Functionalities:
- Creating and managing workflows
- Creating approval checkpoints during execution
- Submitting responses (approve/reject/modify) to checkpoints

Inputs:
- HTTP requests with workflow goals
- Approval decisions and unstructured/structured feedback

Outputs:
- JSON responses showing workflow and approval states

Interacting Files / Modules:
- backend.api.stores
- backend.core.exceptions
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.stores import (
    approval_create,
    approval_get,
    approval_list_by_workflow,
    approval_list_pending,
    approval_update,
    workflow_create,
    workflow_get,
    workflow_list,
    workflow_update,
)
from backend.core.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/supervisor", tags=["Supervisor & Human-in-the-Loop"])


class WorkflowCreate(BaseModel):
    """Start a supervised multi-agent workflow."""

    goal: str = Field(..., min_length=1, max_length=2000)
    crew_id: str | None = None
    conversation_id: str | None = None


class ApprovalRequestCreate(BaseModel):
    """Create a human-in-the-loop approval checkpoint (simulates supervisor pause)."""

    agent_id: str
    action_description: str = Field(..., min_length=1)
    options: list[str] = Field(default=["approve", "reject"], description="e.g. approve, reject, modify")
    context: dict | None = None


class HumanDecision(BaseModel):
    """Human response at an approval checkpoint."""

    decision: str = Field(..., pattern="^(approve|reject|modify)$")
    feedback: str | None = Field(None, max_length=2000, description="Required when decision is modify")
    modification: dict | None = Field(None, description="Structured modification when decision is modify")


@router.get("/workflows")
def list_workflows():
    """List all supervised workflows."""
    return workflow_list()


@router.post("/workflows")
def create_workflow(payload: WorkflowCreate):
    """Start a new supervised workflow. Supervisor will delegate to agents and may pause for human approval."""
    return workflow_create(payload.model_dump())


@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str):
    """Get workflow status and history."""
    wf = workflow_get(workflow_id)
    if not wf:
        raise NotFoundError("Workflow not found")
    approvals = approval_list_by_workflow(workflow_id)
    return {**wf, "approvals": approvals}


@router.post("/workflows/{workflow_id}/pause")
def pause_for_approval(workflow_id: str, payload: ApprovalRequestCreate):
    """
    Human-in-the-Loop: Create an approval checkpoint.
    Supervisor pauses execution until human responds.
    """
    if not workflow_get(workflow_id):
        raise NotFoundError("Workflow not found")
    data = payload.model_dump()
    data["workflow_id"] = workflow_id
    approval = approval_create(data)
    workflow_update(workflow_id, {"status": "waiting_approval", "pending_approval_id": approval["id"]})
    return approval


@router.get("/approvals")
def list_pending_approvals(workflow_id: str | None = None):
    """List approval requests awaiting human decision (Human-in-the-Loop queue)."""
    return approval_list_pending(workflow_id)


@router.get("/approvals/{approval_id}")
def get_approval(approval_id: str):
    """Get an approval request details."""
    apr = approval_get(approval_id)
    if not apr:
        raise NotFoundError("Approval not found")
    return apr


@router.post("/approvals/{approval_id}/respond")
def respond_to_approval(approval_id: str, payload: HumanDecision):
    """
    Human-in-the-Loop: Submit human decision.
    Workflow resumes after approve; stops or branches on reject/modify.
    """
    apr = approval_get(approval_id)
    if not apr:
        raise NotFoundError("Approval not found")
    if apr.get("status") != "pending":
        raise NotFoundError("Approval already responded")
    if payload.decision == "modify" and not payload.feedback and not payload.modification:
        raise ValidationError("Modification requires feedback or modification payload")
    approval_update(
        approval_id,
        {
            "status": "responded",
            "human_decision": payload.decision,
            "human_feedback": payload.feedback,
            "human_modification": payload.modification,
        },
    )
    wf_id = apr.get("workflow_id")
    if wf_id:
        workflow_update(wf_id, {"status": "running", "pending_approval_id": None})
    return {"status": "ok", "decision": payload.decision}
