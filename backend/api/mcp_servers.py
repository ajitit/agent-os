"""
File: mcp_servers.py

Purpose:
Manages Model Context Protocol (MCP) servers and their associated tools via REST API,
enabling external tool integration for agents.

Key Functionalities:
- CRUD operations for MCP servers
- Managing tools provided by MCP servers
- Testing MCP server connections

Inputs:
- HTTP requests with MCP server configuration
- Tool definitions and states

Outputs:
- JSON responses with server and tool metadata

Interacting Files / Modules:
- backend.api.stores
- backend.core.exceptions
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.stores import (
    mcp_server_create,
    mcp_server_delete,
    mcp_server_get,
    mcp_server_list,
    mcp_server_tool_add,
    mcp_server_tool_list,
    mcp_server_tool_remove,
    mcp_server_tool_update,
    mcp_server_update,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

router = APIRouter(prefix="/mcp-servers", tags=["MCP Servers"])


class MCPServerCreate(BaseModel):
    """Request to create an MCP server."""

    name: str = Field(..., min_length=1, max_length=200)
    url: str | None = Field(None, description="MCP server URL (e.g. http://localhost:3000)")
    command: str | None = Field(None, description="Command-line path for stdio transport")
    config: dict | None = None


class MCPServerUpdate(BaseModel):
    """Request to update an MCP server."""

    name: str | None = Field(None, min_length=1, max_length=200)
    url: str | None = None
    config: dict | None = None


class MCPToolCreate(BaseModel):
    """Request to add a tool to an MCP server."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    tool_schema: dict | None = Field(None, description="JSON schema for the tool")


class MCPToolUpdate(BaseModel):
    """Request to update a tool (e.g. enable/disable)."""

    enabled: bool | None = None


@router.get("", response_model=APIResponse[list])
async def get_all_mcp_servers(user: Annotated[dict, Depends(get_current_user)]):
    """Get all MCP servers."""
    return APIResponse(data=mcp_server_list())


@router.post("", response_model=APIResponse[dict], status_code=201)
async def create_mcp_server(
    payload: MCPServerCreate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Create a new MCP server."""
    data = payload.model_dump(exclude_none=True)
    if "schema_" in data:
        data["schema"] = data.pop("schema_")
    return APIResponse(data=mcp_server_create(data))


@router.get("/{server_id}", response_model=APIResponse[dict])
async def get_mcp_server(
    server_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Get a specific MCP server."""
    server = mcp_server_get(server_id)
    if not server:
        raise NotFoundError("MCP server not found")
    return APIResponse(data=server)


@router.put("/{server_id}", response_model=APIResponse[dict])
async def update_mcp_server(
    server_id: str,
    payload: MCPServerUpdate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Update an MCP server."""
    data = payload.model_dump(exclude_none=True)
    if not data:
        server = mcp_server_get(server_id)
        if not server:
            raise NotFoundError("MCP server not found")
        return APIResponse(data=server)
    server = mcp_server_update(server_id, data)
    if not server:
        raise NotFoundError("MCP server not found")
    return APIResponse(data=server)


@router.delete("/{server_id}", status_code=204)
async def delete_mcp_server(
    server_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Delete an MCP server."""
    if not mcp_server_delete(server_id):
        raise NotFoundError("MCP server not found")


@router.get("/{server_id}/tools", response_model=APIResponse[list])
async def get_mcp_server_tools(
    server_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Get tools for an MCP server."""
    if not mcp_server_get(server_id):
        raise NotFoundError("MCP server not found")
    return APIResponse(data=mcp_server_tool_list(server_id))


@router.post("/{server_id}/tools", response_model=APIResponse[dict], status_code=201)
async def add_tool_to_mcp_server(
    server_id: str,
    payload: MCPToolCreate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Add a tool to an MCP server."""
    tool = mcp_server_tool_add(server_id, payload.model_dump(exclude_none=True))
    if not tool:
        raise NotFoundError("MCP server not found")
    return APIResponse(data=tool)


@router.put("/{server_id}/tools/{tool_id}", response_model=APIResponse[dict])
async def update_tool(
    server_id: str,
    tool_id: str,
    payload: MCPToolUpdate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Enable/disable a tool."""
    if not mcp_server_get(server_id):
        raise NotFoundError("MCP server not found")
    data = payload.model_dump(exclude_none=True)
    tool = mcp_server_tool_update(server_id, tool_id, data)
    if not tool:
        raise NotFoundError("Tool not found")
    return APIResponse(data=tool)


@router.delete("/{server_id}/tools/{tool_id}", status_code=204)
async def remove_tool_from_mcp_server(
    server_id: str,
    tool_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Remove a tool from an MCP server."""
    if not mcp_server_get(server_id):
        raise NotFoundError("MCP server not found")
    mcp_server_tool_remove(server_id, tool_id)


@router.post("/{server_id}/test", response_model=APIResponse[dict], status_code=201)
async def test_mcp_connection(
    server_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Test connection to MCP server. Returns health status."""
    server = mcp_server_get(server_id)
    if not server:
        raise NotFoundError("MCP server not found")
    # Simulate health check; in production, call MCP server's initialize/list_tools
    return APIResponse(data={
        "status": "ok",
        "message": "Connection check simulated. Implement real MCP health check in production.",
    })
