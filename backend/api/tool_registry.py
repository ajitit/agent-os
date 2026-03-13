"""
File: api/tool_registry.py

Tool Registry API — CRUD for tools with groups, agent assignment, MCP/API/DataSource sub-resources.
Routes under /api/v1/registry/tools.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    agent_tool_registry_assign,
    agent_tool_registry_list,
    agent_tool_registry_remove,
    audit_log,
    tool_data_source_assign,
    tool_data_source_list,
    tool_data_source_remove,
    tool_group_add_member,
    tool_group_create,
    tool_group_delete,
    tool_group_get,
    tool_group_list,
    tool_group_members,
    tool_group_remove_member,
    tool_group_update,
    tool_mcp_assign,
    tool_mcp_list,
    tool_mcp_remove,
    tool_registry_create,
    tool_registry_delete,
    tool_registry_get,
    tool_registry_list,
    tool_registry_update,
    tool_remote_api_assign,
    tool_remote_api_list,
    tool_remote_api_remove,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry/tools", tags=["Tool Registry"])


class ToolIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    author: str = Field(default="", max_length=200)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|deprecated|draft)$")


class ToolUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    category: str | None = None
    description: str | None = None
    version: str | None = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|deprecated|draft)$")


class GroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class AssignIn(BaseModel):
    tool_id: str


class MemberIn(BaseModel):
    tool_id: str


class ServerAssignIn(BaseModel):
    server_id: str


class ApiAssignIn(BaseModel):
    api_id: str


class DsAssignIn(BaseModel):
    ds_id: str


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_tools(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    category: str | None = Query(None),
) -> APIResponse[list[dict[str, Any]]]:
    return APIResponse(data=tool_registry_list(category=category))


@router.post("", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_tool(
    payload: ToolIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    tool = tool_registry_create(payload.model_dump())
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.tool.created",
               "resourceType": "tool", "resourceId": tool["id"], "resourceName": payload.name, "outcome": "success"})
    return APIResponse(data=tool)


@router.get("/groups", response_model=APIResponse[list[dict[str, Any]]])
async def list_groups(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[dict[str, Any]]]:
    groups = tool_group_list()
    for g in groups:
        g["members"] = tool_group_members(g["id"])
    return APIResponse(data=groups)


@router.post("/groups", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = tool_group_create(payload.model_dump())
    group["members"] = []
    return APIResponse(data=group)


@router.put("/groups/{group_id}", response_model=APIResponse[dict[str, Any]])
async def update_group(
    group_id: str, payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = tool_group_update(group_id, payload.model_dump(exclude_none=True))
    if not group:
        raise NotFoundError("Group not found")
    group["members"] = tool_group_members(group_id)
    return APIResponse(data=group)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not tool_group_delete(group_id):
        raise NotFoundError("Group not found")


@router.post("/groups/{group_id}/members", response_model=APIResponse[dict[str, Any]])
async def add_member(
    group_id: str, payload: MemberIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not tool_group_get(group_id):
        raise NotFoundError("Group not found")
    tool_group_add_member(group_id, payload.tool_id)
    return APIResponse(data={"group_id": group_id, "tool_id": payload.tool_id})


@router.delete("/groups/{group_id}/members/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_id: str, tool_id: str,
                        user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    tool_group_remove_member(group_id, tool_id)


@router.get("/agents/{agent_id}", response_model=APIResponse[list[str]])
async def get_agent_tools(agent_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=agent_tool_registry_list(agent_id))


@router.post("/agents/{agent_id}", response_model=APIResponse[dict[str, Any]])
async def assign_to_agent(
    agent_id: str, payload: AssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    agent_tool_registry_assign(agent_id, payload.tool_id)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.tool.assigned",
               "resourceType": "agent", "resourceId": agent_id, "outcome": "success"})
    return APIResponse(data={"agent_id": agent_id, "tool_id": payload.tool_id})


@router.delete("/agents/{agent_id}/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_agent(agent_id: str, tool_id: str,
                            user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    agent_tool_registry_remove(agent_id, tool_id)


@router.get("/{tool_id}/mcp-servers", response_model=APIResponse[list[str]])
async def get_tool_mcp_servers(tool_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=tool_mcp_list(tool_id))


@router.post("/{tool_id}/mcp-servers", response_model=APIResponse[dict[str, Any]])
async def assign_mcp_server(
    tool_id: str, payload: ServerAssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not tool_registry_get(tool_id):
        raise NotFoundError("Tool not found")
    tool_mcp_assign(tool_id, payload.server_id)
    return APIResponse(data={"tool_id": tool_id, "server_id": payload.server_id})


@router.delete("/{tool_id}/mcp-servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_mcp_server(tool_id: str, server_id: str,
                            user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    tool_mcp_remove(tool_id, server_id)


@router.get("/{tool_id}/remote-apis", response_model=APIResponse[list[str]])
async def get_tool_remote_apis(tool_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=tool_remote_api_list(tool_id))


@router.post("/{tool_id}/remote-apis", response_model=APIResponse[dict[str, Any]])
async def assign_remote_api(
    tool_id: str, payload: ApiAssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not tool_registry_get(tool_id):
        raise NotFoundError("Tool not found")
    tool_remote_api_assign(tool_id, payload.api_id)
    return APIResponse(data={"tool_id": tool_id, "api_id": payload.api_id})


@router.delete("/{tool_id}/remote-apis/{api_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_remote_api(tool_id: str, api_id: str,
                            user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    tool_remote_api_remove(tool_id, api_id)


@router.get("/{tool_id}/data-sources", response_model=APIResponse[list[str]])
async def get_tool_data_sources(tool_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=tool_data_source_list(tool_id))


@router.post("/{tool_id}/data-sources", response_model=APIResponse[dict[str, Any]])
async def assign_data_source(
    tool_id: str, payload: DsAssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not tool_registry_get(tool_id):
        raise NotFoundError("Tool not found")
    tool_data_source_assign(tool_id, payload.ds_id)
    return APIResponse(data={"tool_id": tool_id, "ds_id": payload.ds_id})


@router.delete("/{tool_id}/data-sources/{ds_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_data_source(tool_id: str, ds_id: str,
                             user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    tool_data_source_remove(tool_id, ds_id)


@router.get("/{tool_id}", response_model=APIResponse[dict[str, Any]])
async def get_tool(tool_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[dict[str, Any]]:
    tool = tool_registry_get(tool_id)
    if not tool:
        raise NotFoundError("Tool not found")
    return APIResponse(data=tool)


@router.put("/{tool_id}", response_model=APIResponse[dict[str, Any]])
async def update_tool(
    tool_id: str, payload: ToolUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not tool_registry_get(tool_id):
        raise NotFoundError("Tool not found")
    updated = tool_registry_update(tool_id, payload.model_dump(exclude_none=True))
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.tool.updated",
               "resourceType": "tool", "resourceId": tool_id, "outcome": "success"})
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not tool_registry_delete(tool_id):
        raise NotFoundError("Tool not found")
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.tool.deleted",
               "resourceType": "tool", "resourceId": tool_id, "outcome": "success"})
