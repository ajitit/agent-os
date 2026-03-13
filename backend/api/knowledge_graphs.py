"""
File: api/knowledge_graphs.py

Knowledge Graph Registry API — CRUD for remote knowledge graphs with groups and agent assignment.
Routes under /api/v1/registry/knowledge-graphs.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    agent_kg_assign,
    agent_kg_list,
    agent_kg_remove,
    audit_log,
    kg_create,
    kg_delete,
    kg_get,
    kg_group_add_member,
    kg_group_create,
    kg_group_delete,
    kg_group_get,
    kg_group_list,
    kg_group_members,
    kg_group_remove_member,
    kg_group_update,
    kg_list,
    kg_update,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry/knowledge-graphs", tags=["Knowledge Graph Registry"])


class KGIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    category: str = Field(default="general", max_length=100)
    endpoint_url: str = Field(..., min_length=1, max_length=500)
    auth_type: str = Field(default="none", pattern="^(none|api_key|oauth2|basic)$")
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|inactive|draft)$")


class KGUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    category: str | None = None
    endpoint_url: str | None = None
    auth_type: str | None = Field(None, pattern="^(none|api_key|oauth2|basic)$")
    tags: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|inactive|draft)$")


class GroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class AssignIn(BaseModel):
    kg_id: str


class MemberIn(BaseModel):
    kg_id: str


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_kgs(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    category: str | None = Query(None),
) -> APIResponse[list[dict[str, Any]]]:
    return APIResponse(data=kg_list(category=category))


@router.post("", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_kg(
    payload: KGIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    data = payload.model_dump()
    data["endpointUrl"] = data.pop("endpoint_url")
    data["authType"] = data.pop("auth_type")
    kg = kg_create(data)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.kg.created",
               "resourceType": "knowledge_graph", "resourceId": kg["id"], "resourceName": payload.name, "outcome": "success"})
    return APIResponse(data=kg)


@router.get("/groups", response_model=APIResponse[list[dict[str, Any]]])
async def list_groups(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[dict[str, Any]]]:
    groups = kg_group_list()
    for g in groups:
        g["members"] = kg_group_members(g["id"])
    return APIResponse(data=groups)


@router.post("/groups", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = kg_group_create(payload.model_dump())
    group["members"] = []
    return APIResponse(data=group)


@router.put("/groups/{group_id}", response_model=APIResponse[dict[str, Any]])
async def update_group(
    group_id: str, payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = kg_group_update(group_id, payload.model_dump(exclude_none=True))
    if not group:
        raise NotFoundError("Group not found")
    group["members"] = kg_group_members(group_id)
    return APIResponse(data=group)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not kg_group_delete(group_id):
        raise NotFoundError("Group not found")


@router.post("/groups/{group_id}/members", response_model=APIResponse[dict[str, Any]])
async def add_member(
    group_id: str, payload: MemberIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not kg_group_get(group_id):
        raise NotFoundError("Group not found")
    kg_group_add_member(group_id, payload.kg_id)
    return APIResponse(data={"group_id": group_id, "kg_id": payload.kg_id})


@router.delete("/groups/{group_id}/members/{kg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_id: str, kg_id: str,
                        user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    kg_group_remove_member(group_id, kg_id)


@router.get("/agents/{agent_id}", response_model=APIResponse[list[str]])
async def get_agent_kgs(agent_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=agent_kg_list(agent_id))


@router.post("/agents/{agent_id}", response_model=APIResponse[dict[str, Any]])
async def assign_to_agent(
    agent_id: str, payload: AssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    agent_kg_assign(agent_id, payload.kg_id)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.kg.assigned",
               "resourceType": "agent", "resourceId": agent_id, "outcome": "success"})
    return APIResponse(data={"agent_id": agent_id, "kg_id": payload.kg_id})


@router.delete("/agents/{agent_id}/{kg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_agent(agent_id: str, kg_id: str,
                            user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    agent_kg_remove(agent_id, kg_id)


@router.get("/{kg_id}", response_model=APIResponse[dict[str, Any]])
async def get_kg(kg_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[dict[str, Any]]:
    kg = kg_get(kg_id)
    if not kg:
        raise NotFoundError("Knowledge graph not found")
    return APIResponse(data=kg)


@router.put("/{kg_id}", response_model=APIResponse[dict[str, Any]])
async def update_kg(
    kg_id: str, payload: KGUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not kg_get(kg_id):
        raise NotFoundError("Knowledge graph not found")
    data = payload.model_dump(exclude_none=True)
    if "endpoint_url" in data:
        data["endpointUrl"] = data.pop("endpoint_url")
    if "auth_type" in data:
        data["authType"] = data.pop("auth_type")
    updated = kg_update(kg_id, data)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.kg.updated",
               "resourceType": "knowledge_graph", "resourceId": kg_id, "outcome": "success"})
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/{kg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kg(kg_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not kg_delete(kg_id):
        raise NotFoundError("Knowledge graph not found")
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.kg.deleted",
               "resourceType": "knowledge_graph", "resourceId": kg_id, "outcome": "success"})
