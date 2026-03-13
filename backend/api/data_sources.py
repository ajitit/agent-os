"""
File: api/data_sources.py

Data Source Registry — CRUD for DB/fileshare data sources with groups and tool assignment.
Routes under /api/v1/registry/data-sources.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    audit_log,
    data_source_create,
    data_source_delete,
    data_source_get,
    data_source_list,
    data_source_update,
    ds_group_add_member,
    ds_group_create,
    ds_group_delete,
    ds_group_get,
    ds_group_list,
    ds_group_members,
    ds_group_remove_member,
    ds_group_update,
    tool_data_source_assign,
    tool_data_source_list,
    tool_data_source_remove,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry/data-sources", tags=["Data Source Registry"])

_DS_TYPES = "^(postgresql|mysql|sqlite|mongodb|redis|s3|gcs|azure_blob|sftp|nfs|sharepoint|local)$"


class DataSourceIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    type: str = Field(..., pattern=_DS_TYPES)
    host: str = Field(default="", max_length=500)
    port: int | None = Field(None, ge=1, le=65535)
    database: str = Field(default="", max_length=200)
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|inactive|maintenance)$")


class DataSourceUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    description: str | None = None
    type: str | None = Field(None, pattern=_DS_TYPES)
    host: str | None = None
    port: int | None = Field(None, ge=1, le=65535)
    database: str | None = None
    tags: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|inactive|maintenance)$")


class GroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class AssignIn(BaseModel):
    ds_id: str


class MemberIn(BaseModel):
    ds_id: str


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_data_sources(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    source_type: str | None = Query(None, alias="type"),
) -> APIResponse[list[dict[str, Any]]]:
    return APIResponse(data=data_source_list(source_type=source_type))


@router.post("", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_data_source(
    payload: DataSourceIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    ds = data_source_create(payload.model_dump())
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.data_source.created",
               "resourceType": "data_source", "resourceId": ds["id"], "resourceName": payload.name, "outcome": "success"})
    return APIResponse(data=ds)


@router.get("/groups", response_model=APIResponse[list[dict[str, Any]]])
async def list_groups(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[dict[str, Any]]]:
    groups = ds_group_list()
    for g in groups:
        g["members"] = ds_group_members(g["id"])
    return APIResponse(data=groups)


@router.post("/groups", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = ds_group_create(payload.model_dump())
    group["members"] = []
    return APIResponse(data=group)


@router.put("/groups/{group_id}", response_model=APIResponse[dict[str, Any]])
async def update_group(
    group_id: str, payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = ds_group_update(group_id, payload.model_dump(exclude_none=True))
    if not group:
        raise NotFoundError("Group not found")
    group["members"] = ds_group_members(group_id)
    return APIResponse(data=group)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not ds_group_delete(group_id):
        raise NotFoundError("Group not found")


@router.post("/groups/{group_id}/members", response_model=APIResponse[dict[str, Any]])
async def add_member(
    group_id: str, payload: MemberIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not ds_group_get(group_id):
        raise NotFoundError("Group not found")
    ds_group_add_member(group_id, payload.ds_id)
    return APIResponse(data={"group_id": group_id, "ds_id": payload.ds_id})


@router.delete("/groups/{group_id}/members/{ds_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_id: str, ds_id: str,
                        user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    ds_group_remove_member(group_id, ds_id)


@router.get("/tools/{tool_id}", response_model=APIResponse[list[str]])
async def get_tool_data_sources(tool_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=tool_data_source_list(tool_id))


@router.post("/tools/{tool_id}", response_model=APIResponse[dict[str, Any]])
async def assign_to_tool(
    tool_id: str, payload: AssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    tool_data_source_assign(tool_id, payload.ds_id)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.data_source.assigned",
               "resourceType": "tool", "resourceId": tool_id, "outcome": "success"})
    return APIResponse(data={"tool_id": tool_id, "ds_id": payload.ds_id})


@router.delete("/tools/{tool_id}/{ds_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_tool(tool_id: str, ds_id: str,
                           user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    tool_data_source_remove(tool_id, ds_id)


@router.get("/{ds_id}", response_model=APIResponse[dict[str, Any]])
async def get_data_source(ds_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[dict[str, Any]]:
    ds = data_source_get(ds_id)
    if not ds:
        raise NotFoundError("Data source not found")
    return APIResponse(data=ds)


@router.put("/{ds_id}", response_model=APIResponse[dict[str, Any]])
async def update_data_source(
    ds_id: str, payload: DataSourceUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not data_source_get(ds_id):
        raise NotFoundError("Data source not found")
    updated = data_source_update(ds_id, payload.model_dump(exclude_none=True))
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.data_source.updated",
               "resourceType": "data_source", "resourceId": ds_id, "outcome": "success"})
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/{ds_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_data_source(ds_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not data_source_delete(ds_id):
        raise NotFoundError("Data source not found")
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.data_source.deleted",
               "resourceType": "data_source", "resourceId": ds_id, "outcome": "success"})
