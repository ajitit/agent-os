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

from fastapi import APIRouter
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


@router.get("")
def get_all_mcp_servers():
    """Get all MCP servers."""
    return mcp_server_list()


@router.post("")
def create_mcp_server(payload: MCPServerCreate):
    """Create a new MCP server."""
    data = payload.model_dump(exclude_none=True)
    if "schema_" in data:
        data["schema"] = data.pop("schema_")
    return mcp_server_create(data)


@router.get("/{server_id}")
def get_mcp_server(server_id: str):
    """Get a specific MCP server."""
    server = mcp_server_get(server_id)
    if not server:
        raise NotFoundError("MCP server not found")
    return server


@router.put("/{server_id}")
def update_mcp_server(server_id: str, payload: MCPServerUpdate):
    """Update an MCP server."""
    data = payload.model_dump(exclude_none=True)
    if not data:
        return get_mcp_server(server_id)
    server = mcp_server_update(server_id, data)
    if not server:
        raise NotFoundError("MCP server not found")
    return server


@router.delete("/{server_id}", status_code=204)
def delete_mcp_server(server_id: str):
    """Delete an MCP server."""
    if not mcp_server_delete(server_id):
        raise NotFoundError("MCP server not found")


@router.get("/{server_id}/tools")
def get_mcp_server_tools(server_id: str):
    """Get tools for an MCP server."""
    if not mcp_server_get(server_id):
        raise NotFoundError("MCP server not found")
    return mcp_server_tool_list(server_id)


@router.post("/{server_id}/tools")
def add_tool_to_mcp_server(server_id: str, payload: MCPToolCreate):
    """Add a tool to an MCP server."""
    tool = mcp_server_tool_add(server_id, payload.model_dump(exclude_none=True))
    if not tool:
        raise NotFoundError("MCP server not found")
    return tool


@router.put("/{server_id}/tools/{tool_id}")
def update_tool(server_id: str, tool_id: str, payload: MCPToolUpdate):
    """Enable/disable a tool."""
    if not mcp_server_get(server_id):
        raise NotFoundError("MCP server not found")
    data = payload.model_dump(exclude_none=True)
    tool = mcp_server_tool_update(server_id, tool_id, data)
    if not tool:
        raise NotFoundError("Tool not found")
    return tool


@router.delete("/{server_id}/tools/{tool_id}", status_code=204)
def remove_tool_from_mcp_server(server_id: str, tool_id: str):
    """Remove a tool from an MCP server."""
    if not mcp_server_get(server_id):
        raise NotFoundError("MCP server not found")
    mcp_server_tool_remove(server_id, tool_id)


@router.post("/{server_id}/test")
def test_mcp_connection(server_id: str):
    """Test connection to MCP server. Returns health status."""
    server = mcp_server_get(server_id)
    if not server:
        raise NotFoundError("MCP server not found")
    # Simulate health check; in production, call MCP server's initialize/list_tools
    return {
        "status": "ok",
        "message": "Connection check simulated. Implement real MCP health check in production.",
    }
