"""
<<<<<<< HEAD
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
=======
File: api/agents.py

Agent management — full CRUD for AI agent configurations with audit instrumentation.

Every mutating operation emits an audit event via ``audit_log`` so operators
can track the full lifecycle of every agent.  All endpoints are JWT-protected.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends
>>>>>>> c952205 (Initial upload of AgentOS code)
from pydantic import BaseModel, Field

from backend.api.stores import (
    agent_add_tool,
    agent_create,
    agent_delete,
    agent_get,
    agent_list,
    agent_remove_tool,
    agent_update,
<<<<<<< HEAD
)
from backend.core.exceptions import NotFoundError
=======
    audit_log,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

logger = logging.getLogger(__name__)
>>>>>>> c952205 (Initial upload of AgentOS code)

router = APIRouter(prefix="/agents", tags=["Agents"])


class AgentCreate(BaseModel):
<<<<<<< HEAD
    """Request to create an agent."""
=======
    """Request to create an agent.

    Attributes:
        name: Human-readable agent name.
        description: Optional description.
        role: Agent role (e.g. researcher, coder).
        model: LLM model identifier.
        system_prompt: Agent system prompt.
        temperature: Sampling temperature 0–2.
        assigned_tools: Tool IDs to assign on creation.
    """
>>>>>>> c952205 (Initial upload of AgentOS code)

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    role: str | None = None
<<<<<<< HEAD
    model: str | None = Field(None, description="LLM model e.g. gpt-4, claude-3-5-sonnet")
=======
    model: str | None = Field(None, description="LLM model e.g. gpt-4o, claude-sonnet-4-6")
>>>>>>> c952205 (Initial upload of AgentOS code)
    system_prompt: str | None = None
    temperature: float | None = Field(None, ge=0, le=2)
    assigned_tools: list[str] | None = Field(None, alias="tool_ids")


class AgentUpdate(BaseModel):
<<<<<<< HEAD
    """Request to update an agent."""
=======
    """Request to update an agent.

    Attributes:
        name: Updated name.
        description: Updated description.
        role: Updated role.
        model: Updated model identifier.
        system_prompt: Updated system prompt.
        temperature: Updated temperature.
        status: Lifecycle status.
        assigned_tools: Updated tool ID list.
    """
>>>>>>> c952205 (Initial upload of AgentOS code)

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    role: str | None = None
    model: str | None = None
    system_prompt: str | None = None
    temperature: float | None = Field(None, ge=0, le=2)
    status: str | None = Field(None, pattern="^(active|inactive|draft)$")
    assigned_tools: list[str] | None = Field(None, alias="tool_ids")


<<<<<<< HEAD
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
=======
@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def get_all_agents(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[list[dict[str, Any]]]:
    """List all agents.

    Args:
        user: Authenticated user.

    Returns:
        APIResponse wrapping list of agent dicts.
    """
    return APIResponse(data=agent_list())


@router.post("", response_model=APIResponse[dict[str, Any]])
async def create_agent(
    payload: AgentCreate,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Create a new agent.

    Args:
        payload: Agent creation request.
        user: Authenticated user.

    Returns:
        APIResponse wrapping created agent.
    """
    data = payload.model_dump(exclude_none=True, by_alias=True)
    tool_ids: list[str] = data.pop("assigned_tools", data.pop("tool_ids", None)) or []
    agent = agent_create({**data, "status": data.get("status", "active")})
    for tid in tool_ids:
        agent_add_tool(agent["id"], tid)

    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "agent.created",
        "resourceType": "agent",
        "resourceId": agent["id"],
        "resourceName": payload.name,
        "outcome": "success",
    })
    logger.info("agent=created id=%s name=%s user=%s", agent["id"], payload.name, user["id"])
    result = agent_get(agent["id"])
    return APIResponse(data=result or agent)


@router.get("/{agent_id}", response_model=APIResponse[dict[str, Any]])
async def get_agent(
    agent_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Get a specific agent by ID.

    Args:
        agent_id: Agent UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping agent dict.

    Raises:
        NotFoundError: If agent does not exist.
    """
    agent = agent_get(agent_id)
    if not agent:
        raise NotFoundError("Agent not found")
    return APIResponse(data=agent)


@router.put("/{agent_id}", response_model=APIResponse[dict[str, Any]])
async def update_agent(
    agent_id: str,
    payload: AgentUpdate,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Update an agent.

    Args:
        agent_id: Agent UUID.
        payload: Update fields.
        user: Authenticated user.

    Returns:
        APIResponse wrapping updated agent.

    Raises:
        NotFoundError: If agent does not exist.
    """
    data = payload.model_dump(exclude_none=True, by_alias=True)
    tool_ids: list[str] | None = data.pop("assigned_tools", data.pop("tool_ids", None))
    if data:
        updated = agent_update(agent_id, data)
        if not updated:
            raise NotFoundError("Agent not found")
    if tool_ids is not None:
        current_agent = agent_get(agent_id)
        current: set[str] = set(current_agent.get("tool_ids", [])) if current_agent else set()
        desired: set[str] = set(tool_ids)
>>>>>>> c952205 (Initial upload of AgentOS code)
        for tid in desired - current:
            agent_add_tool(agent_id, tid)
        for tid in current - desired:
            agent_remove_tool(agent_id, tid)
<<<<<<< HEAD
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
=======

    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "agent.updated",
        "resourceType": "agent",
        "resourceId": agent_id,
        "details": {k: v for k, v in data.items() if k != "system_prompt"},
        "outcome": "success",
    })
    result = agent_get(agent_id)
    if not result:
        raise NotFoundError("Agent not found")
    return APIResponse(data=result)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> None:
    """Delete an agent.

    Args:
        agent_id: Agent UUID.
        user: Authenticated user.

    Raises:
        NotFoundError: If agent does not exist.
    """
    agent = agent_get(agent_id)
    if not agent_delete(agent_id):
        raise NotFoundError("Agent not found")
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "agent.deleted",
        "resourceType": "agent",
        "resourceId": agent_id,
        "resourceName": agent.get("name", "") if agent else "",
        "outcome": "success",
    })
    logger.info("agent=deleted id=%s user=%s", agent_id, user["id"])


@router.post("/{agent_id}/tools/{tool_id}", status_code=204)
async def assign_tool_to_agent(
    agent_id: str,
    tool_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> None:
    """Assign a tool to an agent.

    Args:
        agent_id: Agent UUID.
        tool_id: Tool UUID.
        user: Authenticated user.

    Raises:
        NotFoundError: If agent does not exist.
    """
    if not agent_add_tool(agent_id, tool_id):
        raise NotFoundError("Agent not found")
    audit_log({
        "actorType": "human", "actorId": user["id"],
        "action": "agent.tool_assigned", "resourceType": "agent", "resourceId": agent_id,
        "details": {"toolId": tool_id}, "outcome": "success",
    })


@router.delete("/{agent_id}/tools/{tool_id}", status_code=204)
async def remove_tool_from_agent(
    agent_id: str,
    tool_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> None:
    """Remove a tool from an agent.

    Args:
        agent_id: Agent UUID.
        tool_id: Tool UUID.
        user: Authenticated user.
    """
    agent_remove_tool(agent_id, tool_id)
    audit_log({
        "actorType": "human", "actorId": user["id"],
        "action": "agent.tool_removed", "resourceType": "agent", "resourceId": agent_id,
        "details": {"toolId": tool_id}, "outcome": "success",
    })
>>>>>>> c952205 (Initial upload of AgentOS code)
