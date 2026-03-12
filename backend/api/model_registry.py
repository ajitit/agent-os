"""
File: api/model_registry.py

Model Registry API — full CRUD for LLM models with group management and agent assignment.
Routes under /api/v1/registry/models.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    agent_model_assign,
    agent_model_list,
    agent_model_remove,
    audit_log,
    model_group_add_member,
    model_group_create,
    model_group_delete,
    model_group_get,
    model_group_list,
    model_group_members,
    model_group_remove_member,
    model_group_update,
    model_registry_create,
    model_registry_delete,
    model_registry_get,
    model_registry_list,
    model_registry_update,
)
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry/models", tags=["Model Registry"])


class ModelIn(BaseModel):
    id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    provider: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., pattern="^(chat|embedding|image|audio|vision)$")
    context_window: int = Field(default=4096, ge=1)
    description: str = Field(default="", max_length=1000)
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|deprecated|draft)$")


class ModelUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    tags: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|deprecated|draft)$")


class GroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class AssignIn(BaseModel):
    model_id: str


class MemberIn(BaseModel):
    model_id: str


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_models(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    provider: str | None = Query(None),
    model_type: str | None = Query(None, alias="type"),
) -> APIResponse[list[dict[str, Any]]]:
    return APIResponse(data=model_registry_list(provider=provider, model_type=model_type))


@router.post("", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_model(
    payload: ModelIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    data = payload.model_dump()
    data["contextWindow"] = data.pop("context_window")
    model = model_registry_create(data)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.model.created",
               "resourceType": "model", "resourceId": model["id"], "resourceName": payload.name, "outcome": "success"})
    return APIResponse(data=model)


@router.get("/groups", response_model=APIResponse[list[dict[str, Any]]])
async def list_groups(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[dict[str, Any]]]:
    groups = model_group_list()
    for g in groups:
        g["members"] = model_group_members(g["id"])
    return APIResponse(data=groups)


@router.post("/groups", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    group = model_group_create(payload.model_dump())
    group["members"] = []
    return APIResponse(data=group)


@router.put("/groups/{group_id}", response_model=APIResponse[dict[str, Any]])
async def update_group(
    group_id: str, payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    group = model_group_update(group_id, payload.model_dump(exclude_none=True))
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    group["members"] = model_group_members(group_id)
    return APIResponse(data=group)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not model_group_delete(group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")


@router.post("/groups/{group_id}/members", response_model=APIResponse[dict[str, Any]])
async def add_member(
    group_id: str, payload: MemberIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    if not model_group_get(group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    model_group_add_member(group_id, payload.model_id)
    return APIResponse(data={"group_id": group_id, "model_id": payload.model_id})


@router.delete("/groups/{group_id}/members/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_id: str, model_id: str,
                        user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    model_group_remove_member(group_id, model_id)


@router.get("/agents/{agent_id}", response_model=APIResponse[list[str]])
async def get_agent_models(agent_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=agent_model_list(agent_id))


@router.post("/agents/{agent_id}", response_model=APIResponse[dict[str, Any]])
async def assign_to_agent(
    agent_id: str, payload: AssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    agent_model_assign(agent_id, payload.model_id)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.model.assigned",
               "resourceType": "agent", "resourceId": agent_id, "outcome": "success"})
    return APIResponse(data={"agent_id": agent_id, "model_id": payload.model_id})


@router.delete("/agents/{agent_id}/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_agent(agent_id: str, model_id: str,
                            user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    agent_model_remove(agent_id, model_id)


@router.get("/{model_id}", response_model=APIResponse[dict[str, Any]])
async def get_model(model_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[dict[str, Any]]:
    model = model_registry_get(model_id)
    if not model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return APIResponse(data=model)


@router.put("/{model_id}", response_model=APIResponse[dict[str, Any]])
async def update_model(
    model_id: str, payload: ModelUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin"]))],
) -> APIResponse[dict[str, Any]]:
    if not model_registry_get(model_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    updated = model_registry_update(model_id, payload.model_dump(exclude_none=True))
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.model.updated",
               "resourceType": "model", "resourceId": model_id, "outcome": "success"})
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not model_registry_delete(model_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.model.deleted",
               "resourceType": "model", "resourceId": model_id, "outcome": "success"})
