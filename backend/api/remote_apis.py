"""
File: api/remote_apis.py

Remote API Registry — CRUD for external REST/GraphQL APIs with groups and tool assignment.
Routes under /api/v1/registry/remote-apis.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    api_group_add_member,
    api_group_create,
    api_group_delete,
    api_group_get,
    api_group_list,
    api_group_members,
    api_group_remove_member,
    api_group_update,
    audit_log,
    remote_api_create,
    remote_api_delete,
    remote_api_get,
    remote_api_list,
    remote_api_update,
    tool_remote_api_assign,
    tool_remote_api_list,
    tool_remote_api_remove,
)
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry/remote-apis", tags=["Remote API Registry"])


class RemoteAPIIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    category: str = Field(default="general", max_length=100)
    base_url: str = Field(..., min_length=1, max_length=500)
    api_type: str = Field(default="rest", pattern="^(rest|graphql|grpc|soap)$")
    auth_type: str = Field(default="none", pattern="^(none|api_key|oauth2|basic|bearer)$")
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|inactive|deprecated)$")


class RemoteAPIUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    category: str | None = None
    base_url: str | None = None
    api_type: str | None = Field(None, pattern="^(rest|graphql|grpc|soap)$")
    auth_type: str | None = Field(None, pattern="^(none|api_key|oauth2|basic|bearer)$")
    tags: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|inactive|deprecated)$")


class GroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class AssignIn(BaseModel):
    api_id: str


class MemberIn(BaseModel):
    api_id: str


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_remote_apis(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    category: str | None = Query(None),
) -> APIResponse[list[dict[str, Any]]]:
    return APIResponse(data=remote_api_list(category=category))


@router.post("", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_remote_api(
    payload: RemoteAPIIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    data = payload.model_dump()
    data["baseUrl"] = data.pop("base_url")
    data["apiType"] = data.pop("api_type")
    data["authType"] = data.pop("auth_type")
    api_obj = remote_api_create(data)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.remote_api.created",
               "resourceType": "remote_api", "resourceId": api_obj["id"], "resourceName": payload.name, "outcome": "success"})
    return APIResponse(data=api_obj)


@router.get("/groups", response_model=APIResponse[list[dict[str, Any]]])
async def list_groups(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[dict[str, Any]]]:
    groups = api_group_list()
    for g in groups:
        g["members"] = api_group_members(g["id"])
    return APIResponse(data=groups)


@router.post("/groups", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = api_group_create(payload.model_dump())
    group["members"] = []
    return APIResponse(data=group)


@router.put("/groups/{group_id}", response_model=APIResponse[dict[str, Any]])
async def update_group(
    group_id: str, payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = api_group_update(group_id, payload.model_dump(exclude_none=True))
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    group["members"] = api_group_members(group_id)
    return APIResponse(data=group)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not api_group_delete(group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")


@router.post("/groups/{group_id}/members", response_model=APIResponse[dict[str, Any]])
async def add_member(
    group_id: str, payload: MemberIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not api_group_get(group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    api_group_add_member(group_id, payload.api_id)
    return APIResponse(data={"group_id": group_id, "api_id": payload.api_id})


@router.delete("/groups/{group_id}/members/{api_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_id: str, api_id: str,
                        user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    api_group_remove_member(group_id, api_id)


@router.get("/tools/{tool_id}", response_model=APIResponse[list[str]])
async def get_tool_apis(tool_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=tool_remote_api_list(tool_id))


@router.post("/tools/{tool_id}", response_model=APIResponse[dict[str, Any]])
async def assign_to_tool(
    tool_id: str, payload: AssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    tool_remote_api_assign(tool_id, payload.api_id)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.remote_api.assigned",
               "resourceType": "tool", "resourceId": tool_id, "outcome": "success"})
    return APIResponse(data={"tool_id": tool_id, "api_id": payload.api_id})


@router.delete("/tools/{tool_id}/{api_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_tool(tool_id: str, api_id: str,
                           user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    tool_remote_api_remove(tool_id, api_id)


@router.get("/{api_id}", response_model=APIResponse[dict[str, Any]])
async def get_remote_api(api_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[dict[str, Any]]:
    api_obj = remote_api_get(api_id)
    if not api_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remote API not found")
    return APIResponse(data=api_obj)


@router.put("/{api_id}", response_model=APIResponse[dict[str, Any]])
async def update_remote_api(
    api_id: str, payload: RemoteAPIUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not remote_api_get(api_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remote API not found")
    data = payload.model_dump(exclude_none=True)
    if "base_url" in data:
        data["baseUrl"] = data.pop("base_url")
    if "api_type" in data:
        data["apiType"] = data.pop("api_type")
    if "auth_type" in data:
        data["authType"] = data.pop("auth_type")
    updated = remote_api_update(api_id, data)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.remote_api.updated",
               "resourceType": "remote_api", "resourceId": api_id, "outcome": "success"})
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/{api_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_remote_api(api_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not remote_api_delete(api_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remote API not found")
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.remote_api.deleted",
               "resourceType": "remote_api", "resourceId": api_id, "outcome": "success"})
