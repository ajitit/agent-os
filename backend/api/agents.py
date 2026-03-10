"""
File: agents.py

Purpose:
Defines the REST API endpoints for managing the lifecycle of agents, including
creation, retrieval, updating, deletion, and tool assignment.

Key Functionalities:
- CRUD operations for agents
- Assigning and removing tools from agents
- Pydantic models for request validation (AgentCreate, AgentUpdate)

Inputs:
- HTTP requests with agent configuration data
- Tool IDs for assignment operations

Outputs:
- JSON responses containing agent metadata
- HTTP status codes for operation results

Interacting Files / Modules:
- backend.api.stores
- backend.core.exceptions
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.stores import (
    agent_add_tool,
    agent_create,
    agent_delete,
    agent_get,
    agent_list,
    agent_remove_tool,
    agent_update,
)
from backend.core.exceptions import NotFoundError

router = APIRouter(prefix="/agents", tags=["Agents"])


class AgentCreate(BaseModel):
    """Request to create an agent."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    role: str | None = None
    model: str | None = Field(None, description="LLM model e.g. gpt-4, claude-3-5-sonnet")
    system_prompt: str | None = None
    temperature: float | None = Field(None, ge=0, le=2)
    assigned_tools: list[str] | None = Field(None, alias="tool_ids")


class AgentUpdate(BaseModel):
    """Request to update an agent."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    role: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    temperature: float | None = Field(None, ge=0, le=2)
    status: str | None = Field(None, pattern="^(active|inactive|draft)$")
    assigned_tools: list[str] | None = Field(None, alias="tool_ids")


@router.get("")
def get_all_agents():
    """Get all agents."""
    return agent_list()


@router.post("")
def create_agent(payload: AgentCreate):
    """Create a new agent."""
    data = payload.model_dump(exclude_none=True, by_alias=True)
    tool_ids = data.pop("assigned_tools", data.pop("tool_ids", None)) or []
    agent = agent_create({**data, "status": data.get("status", "active")})
    for tid in tool_ids:
        agent_add_tool(agent["id"], tid)
    return agent_get(agent["id"])


@router.get("/{agent_id}")
def get_agent(agent_id: str):
    """Get a specific agent."""
    agent = agent_get(agent_id)
    if not agent:
        raise NotFoundError("Agent not found")
    return agent


@router.put("/{agent_id}")
def update_agent(agent_id: str, payload: AgentUpdate):
    """Update an agent."""
    data = payload.model_dump(exclude_none=True, by_alias=True)
    tool_ids = data.pop("assigned_tools", data.pop("tool_ids", None))
    if data:
        agent = agent_update(agent_id, data)
        if not agent:
            raise NotFoundError("Agent not found")
    if tool_ids is not None:
        current_agent = agent_get(agent_id)
        current = set(current_agent.get("tool_ids", [])) if current_agent else set()
        desired = set(tool_ids)
        for tid in desired - current:
            agent_add_tool(agent_id, tid)
        for tid in current - desired:
            agent_remove_tool(agent_id, tid)
    return get_agent(agent_id)


@router.delete("/{agent_id}", status_code=204)
def delete_agent(agent_id: str):
    """Delete an agent."""
    if not agent_delete(agent_id):
        raise NotFoundError("Agent not found")


@router.post("/{agent_id}/tools/{tool_id}", status_code=204)
def assign_tool_to_agent(agent_id: str, tool_id: str):
    """Assign a tool to an agent."""
    if not agent_add_tool(agent_id, tool_id):
        raise NotFoundError("Agent not found")


@router.delete("/{agent_id}/tools/{tool_id}", status_code=204)
def remove_tool_from_agent(agent_id: str, tool_id: str):
    """Remove a tool from an agent."""
    agent_remove_tool(agent_id, tool_id)
