"""
File: api/marketplace.py

Marketplace API — registry for Skills, Models, and Tools available to agents.

Each registry is a separate namespace.  Read operations are open to all
authenticated users; create/update/delete require admin or developer role.
Install endpoints are available to all authenticated users and record an
audit event.

Routes (all under /api/v1/marketplace):

Skills:
    GET    /skills                   List (category filter)
    POST   /skills                   Publish (admin/developer)
    GET    /skills/{id}              Detail
    PUT    /skills/{id}              Update (admin/developer)
    DELETE /skills/{id}              Delete (admin)
    POST   /skills/{id}/install      Increment install count

Models:
    GET    /models                   List (provider/type filter)
    POST   /models                   Register (admin)
    GET    /models/{id}              Detail
    PUT    /models/{id}              Update (admin)
    DELETE /models/{id}              Delete (admin)
    POST   /models/{id}/install      Increment install count

Tools:
    GET    /tools                    List (category filter)
    POST   /tools                    Publish (admin/developer)
    GET    /tools/{id}               Detail
    PUT    /tools/{id}               Update (admin/developer)
    DELETE /tools/{id}               Delete (admin)
    POST   /tools/{id}/install       Increment install count
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    audit_log,
    model_registry_create,
    model_registry_delete,
    model_registry_get,
    model_registry_install,
    model_registry_list,
    model_registry_update,
    skill_registry_create,
    skill_registry_delete,
    skill_registry_get,
    skill_registry_install,
    skill_registry_list,
    skill_registry_update,
    tool_registry_create,
    tool_registry_delete,
    tool_registry_get,
    tool_registry_install,
    tool_registry_list,
    tool_registry_update,
)
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# ── Request models ────────────────────────────────────────────────────────────


class SkillCreate(BaseModel):
    """Request body for publishing a skill.

    Attributes:
        name: Unique skill name.
        description: Short description shown in the marketplace.
        category: Skill category (e.g. research, coding, communication).
        author: Author name or organisation.
        version: Semantic version string.
        tags: Free-form tags for discovery.
        readme: Full markdown documentation.
        config_schema: JSON Schema dict for required configuration.
    """

    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=100)
    author: str = Field(default="", max_length=200)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] = Field(default_factory=list)
    readme: str = Field(default="")
    config_schema: dict[str, Any] = Field(default_factory=dict)


class SkillUpdate(BaseModel):
    """Request body for updating a skill."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1, max_length=1000)
    category: str | None = None
    author: str | None = None
    version: str | None = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] | None = None
    readme: str | None = None
    config_schema: dict[str, Any] | None = None
    status: str | None = Field(None, pattern="^(active|deprecated|draft)$")


class ModelCreate(BaseModel):
    """Request body for registering a model.

    Attributes:
        id: Canonical model ID (e.g. gpt-4o).
        name: Human-readable display name.
        provider: Provider name (OpenAI, Anthropic, Meta…).
        type: Model type (chat, embedding, image, audio).
        context_window: Maximum token context window.
        description: Short description.
        tags: Free-form tags.
        capabilities: List of capability strings.
        config_schema: JSON Schema for model configuration.
    """

    id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    provider: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(chat|embedding|image|audio|vision)$")
    context_window: int = Field(default=4096, ge=1)
    description: str = Field(default="", max_length=1000)
    tags: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    config_schema: dict[str, Any] = Field(default_factory=dict)


class ModelUpdate(BaseModel):
    """Request body for updating a model."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    tags: list[str] | None = None
    capabilities: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|deprecated|draft)$")
    config_schema: dict[str, Any] | None = None


class ToolCreate(BaseModel):
    """Request body for registering a tool.

    Attributes:
        name: Unique tool name.
        category: Tool category (search, code, files, communication…).
        description: Short description.
        author: Author name.
        version: Semantic version string.
        tags: Free-form tags.
        input_schema: JSON Schema for tool inputs.
        output_schema: JSON Schema for tool outputs.
        config_schema: JSON Schema for required configuration.
    """

    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    author: str = Field(default="", max_length=200)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    config_schema: dict[str, Any] = Field(default_factory=dict)


class ToolUpdate(BaseModel):
    """Request body for updating a tool."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = None
    version: str | None = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] | None = None
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    config_schema: dict[str, Any] | None = None
    status: str | None = Field(None, pattern="^(active|deprecated|draft)$")


# ── Skills ────────────────────────────────────────────────────────────────────


@router.get("/skills", response_model=APIResponse[list[dict[str, Any]]])
async def list_skills(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    category: str | None = Query(None),
) -> APIResponse[list[dict[str, Any]]]:
    """List skills in the marketplace.

    Args:
        user: Authenticated user.
        category: Optional category filter.

    Returns:
        APIResponse wrapping list of skill dicts.
    """
    return APIResponse(data=skill_registry_list(category=category))


@router.post("/skills", response_model=APIResponse[dict[str, Any]])
async def create_skill(
    payload: SkillCreate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    """Publish a new skill to the marketplace.

    Args:
        payload: Skill definition.
        user: Admin or developer user.

    Returns:
        APIResponse wrapping created skill.
    """
    data = payload.model_dump()
    data["configSchema"] = data.pop("config_schema")
    skill = skill_registry_create(data)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "marketplace.skill.created",
        "resourceType": "skill",
        "resourceId": skill["id"],
        "resourceName": payload.name,
        "outcome": "success",
    })
    logger.info("marketplace=skill_created id=%s name=%s", skill["id"], payload.name)
    return APIResponse(data=skill)


@router.get("/skills/{skill_id}", response_model=APIResponse[dict[str, Any]])
async def get_skill(
    skill_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Get a single skill by ID.

    Args:
        skill_id: Skill UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping skill dict.

    Raises:
        HTTPException: 404 if not found.
    """
    skill = skill_registry_get(skill_id)
    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return APIResponse(data=skill)


@router.put("/skills/{skill_id}", response_model=APIResponse[dict[str, Any]])
async def update_skill(
    skill_id: str,
    payload: SkillUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    """Update a skill registry entry.

    Args:
        skill_id: Skill UUID.
        payload: Fields to update.
        user: Admin or developer user.

    Returns:
        APIResponse wrapping updated skill.

    Raises:
        HTTPException: 404 if not found.
    """
    if not skill_registry_get(skill_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    data = payload.model_dump(exclude_none=True)
    if "config_schema" in data:
        data["configSchema"] = data.pop("config_schema")
    updated = skill_registry_update(skill_id, data)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.skill.updated",
        "resourceType": "skill",
        "resourceId": skill_id,
        "outcome": "success",
    })
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: str,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> None:
    """Delete a skill from the marketplace.

    Args:
        skill_id: Skill UUID.
        user: Admin user.

    Raises:
        HTTPException: 404 if not found.
    """
    if not skill_registry_delete(skill_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.skill.deleted",
        "resourceType": "skill",
        "resourceId": skill_id,
        "outcome": "success",
    })


@router.post("/skills/{skill_id}/install", response_model=APIResponse[dict[str, Any]])
async def install_skill(
    skill_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Increment the install counter for a skill.

    Args:
        skill_id: Skill UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping updated skill.

    Raises:
        HTTPException: 404 if not found.
    """
    updated = skill_registry_install(skill_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.skill.installed",
        "resourceType": "skill",
        "resourceId": skill_id,
        "outcome": "success",
    })
    return APIResponse(data=updated)


# ── Models ────────────────────────────────────────────────────────────────────


@router.get("/models", response_model=APIResponse[list[dict[str, Any]]])
async def list_models(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    provider: str | None = Query(None),
    model_type: str | None = Query(None, alias="type"),
) -> APIResponse[list[dict[str, Any]]]:
    """List models in the registry.

    Args:
        user: Authenticated user.
        provider: Optional provider filter.
        model_type: Optional type filter (chat, embedding, etc.)

    Returns:
        APIResponse wrapping list of model dicts.
    """
    return APIResponse(data=model_registry_list(provider=provider, model_type=model_type))


@router.post("/models", response_model=APIResponse[dict[str, Any]])
async def create_model(
    payload: ModelCreate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    """Register a new model in the marketplace.

    Args:
        payload: Model definition.
        user: Admin user.

    Returns:
        APIResponse wrapping created model.
    """
    data = payload.model_dump()
    data["contextWindow"] = data.pop("context_window")
    data["configSchema"] = data.pop("config_schema")
    model = model_registry_create(data)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.model.created",
        "resourceType": "model",
        "resourceId": model["id"],
        "resourceName": payload.name,
        "outcome": "success",
    })
    logger.info("marketplace=model_created id=%s", payload.id)
    return APIResponse(data=model)


@router.get("/models/{model_id}", response_model=APIResponse[dict[str, Any]])
async def get_model(
    model_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Get a single model by ID.

    Args:
        model_id: Model identifier string.
        user: Authenticated user.

    Returns:
        APIResponse wrapping model dict.

    Raises:
        HTTPException: 404 if not found.
    """
    model = model_registry_get(model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return APIResponse(data=model)


@router.put("/models/{model_id}", response_model=APIResponse[dict[str, Any]])
async def update_model(
    model_id: str,
    payload: ModelUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    """Update a model registry entry.

    Args:
        model_id: Model identifier.
        payload: Fields to update.
        user: Admin user.

    Returns:
        APIResponse wrapping updated model.

    Raises:
        HTTPException: 404 if not found.
    """
    if not model_registry_get(model_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    data = payload.model_dump(exclude_none=True)
    if "config_schema" in data:
        data["configSchema"] = data.pop("config_schema")
    updated = model_registry_update(model_id, data)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.model.updated",
        "resourceType": "model",
        "resourceId": model_id,
        "outcome": "success",
    })
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: str,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> None:
    """Delete a model from the registry.

    Args:
        model_id: Model identifier.
        user: Admin user.

    Raises:
        HTTPException: 404 if not found.
    """
    if not model_registry_delete(model_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.model.deleted",
        "resourceType": "model",
        "resourceId": model_id,
        "outcome": "success",
    })


@router.post("/models/{model_id}/install", response_model=APIResponse[dict[str, Any]])
async def install_model(
    model_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Increment the install counter for a model.

    Args:
        model_id: Model identifier.
        user: Authenticated user.

    Returns:
        APIResponse wrapping updated model.

    Raises:
        HTTPException: 404 if not found.
    """
    updated = model_registry_install(model_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.model.installed",
        "resourceType": "model",
        "resourceId": model_id,
        "outcome": "success",
    })
    return APIResponse(data=updated)


# ── Tools ─────────────────────────────────────────────────────────────────────


@router.get("/tools", response_model=APIResponse[list[dict[str, Any]]])
async def list_tools(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    category: str | None = Query(None),
) -> APIResponse[list[dict[str, Any]]]:
    """List tools in the marketplace.

    Args:
        user: Authenticated user.
        category: Optional category filter.

    Returns:
        APIResponse wrapping list of tool dicts.
    """
    return APIResponse(data=tool_registry_list(category=category))


@router.post("/tools", response_model=APIResponse[dict[str, Any]])
async def create_tool(
    payload: ToolCreate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    """Publish a new tool to the marketplace.

    Args:
        payload: Tool definition.
        user: Admin or developer user.

    Returns:
        APIResponse wrapping created tool.
    """
    data = payload.model_dump()
    data["inputSchema"] = data.pop("input_schema")
    data["outputSchema"] = data.pop("output_schema")
    data["configSchema"] = data.pop("config_schema")
    tool = tool_registry_create(data)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "actorName": user.get("email", ""),
        "action": "marketplace.tool.created",
        "resourceType": "tool",
        "resourceId": tool["id"],
        "resourceName": payload.name,
        "outcome": "success",
    })
    logger.info("marketplace=tool_created id=%s name=%s", tool["id"], payload.name)
    return APIResponse(data=tool)


@router.get("/tools/{tool_id}", response_model=APIResponse[dict[str, Any]])
async def get_tool(
    tool_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Get a single tool by ID.

    Args:
        tool_id: Tool UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping tool dict.

    Raises:
        HTTPException: 404 if not found.
    """
    tool = tool_registry_get(tool_id)
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return APIResponse(data=tool)


@router.put("/tools/{tool_id}", response_model=APIResponse[dict[str, Any]])
async def update_tool(
    tool_id: str,
    payload: ToolUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    """Update a tool registry entry.

    Args:
        tool_id: Tool UUID.
        payload: Fields to update.
        user: Admin or developer user.

    Returns:
        APIResponse wrapping updated tool.

    Raises:
        HTTPException: 404 if not found.
    """
    if not tool_registry_get(tool_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    data = payload.model_dump(exclude_none=True)
    for old, new in [("input_schema", "inputSchema"), ("output_schema", "outputSchema"), ("config_schema", "configSchema")]:
        if old in data:
            data[new] = data.pop(old)
    updated = tool_registry_update(tool_id, data)
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.tool.updated",
        "resourceType": "tool",
        "resourceId": tool_id,
        "outcome": "success",
    })
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: str,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> None:
    """Delete a tool from the marketplace.

    Args:
        tool_id: Tool UUID.
        user: Admin user.

    Raises:
        HTTPException: 404 if not found.
    """
    if not tool_registry_delete(tool_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.tool.deleted",
        "resourceType": "tool",
        "resourceId": tool_id,
        "outcome": "success",
    })


@router.post("/tools/{tool_id}/install", response_model=APIResponse[dict[str, Any]])
async def install_tool(
    tool_id: str,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> APIResponse[dict[str, Any]]:
    """Increment the install counter for a tool.

    Args:
        tool_id: Tool UUID.
        user: Authenticated user.

    Returns:
        APIResponse wrapping updated tool.

    Raises:
        HTTPException: 404 if not found.
    """
    updated = tool_registry_install(tool_id)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    audit_log({
        "actorType": "human",
        "actorId": user["id"],
        "action": "marketplace.tool.installed",
        "resourceType": "tool",
        "resourceId": tool_id,
        "outcome": "success",
    })
    return APIResponse(data=updated)
