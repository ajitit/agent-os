"""
File: tasks.py

Purpose:
Defines API endpoints for task creation and management for agent execution.

Key Functionalities:
- Submitting new tasks with specific goals
- (Future) querying task status

Inputs:
- HTTP requests with task goals and constraints

Outputs:
- JSON responses indicating queued task status

Interacting Files / Modules:
- None
"""
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class TaskRequest(BaseModel):
    """Request model for creating a task."""

    goal: str = Field(..., min_length=1, max_length=1000, description="Task goal")


class TaskResponse(BaseModel):
    """Response model for task creation."""

    goal: str
    status: str


@router.post("", response_model=TaskResponse)
def create_task(req: TaskRequest) -> TaskResponse:
    """Create a new agent task."""
    return TaskResponse(goal=req.goal, status="queued")
