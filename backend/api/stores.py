"""
File: stores.py

Purpose:
Provides in-memory data structures and functions for basic CRUD operations across
all primary resources (crews, agents, MCP servers, conversations, etc.).
Serves as a placeholder for a true database layer.

Key Functionalities:
- Generating unique IDs for new records
- Create, Read, Update, Delete for Crews, Agents, MCP Servers, Conversations
- Tool assignment mapping for agents and MCP servers
- File storage and workflow/approval mapping

Inputs:
- Dictionaries representing updated or new resource data
- String IDs for record lookups

Outputs:
- Dictionary representations of stored records
- Booleans indicating success/failure of deletion

Interacting Files / Modules:
- None
"""

from collections import defaultdict
from typing import Any
from uuid import uuid4

_crews: dict[str, dict[str, Any]] = {}
_agents: dict[str, dict[str, Any]] = {}
_agent_tools: dict[str, set[str]] = defaultdict(set)
_mcp_servers: dict[str, dict[str, Any]] = {}
_mcp_tools: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
_conversations: dict[str, dict[str, Any]] = {}
_conversation_messages: dict[str, list[dict[str, Any]]] = defaultdict(list)
_storage_files: dict[str, bytes] = {}
_sources: dict[str, dict[str, Any]] = {}
_code_examples: dict[str, dict[str, Any]] = {}


def generate_id() -> str:
    return str(uuid4())


# Crews
def crew_list() -> list[dict]:
    return list(_crews.values())


def crew_get(crew_id: str) -> dict | None:
    return _crews.get(crew_id)


def crew_create(data: dict) -> dict:
    crew_id = generate_id()
    _crews[crew_id] = {"id": crew_id, **data}
    return _crews[crew_id]


def crew_update(crew_id: str, data: dict) -> dict | None:
    if crew_id not in _crews:
        return None
    _crews[crew_id].update(data)
    return _crews[crew_id]


def crew_delete(crew_id: str) -> bool:
    if crew_id not in _crews:
        return False
    del _crews[crew_id]
    return True


# Agents
def agent_list() -> list[dict]:
    result = []
    for a in _agents.values():
        r = dict(a)
        r["tool_ids"] = list(_agent_tools.get(a["id"], set()))
        result.append(r)
    return result


def agent_get(agent_id: str) -> dict | None:
    if agent_id not in _agents:
        return None
    a = dict(_agents[agent_id])
    a["tool_ids"] = list(_agent_tools.get(agent_id, set()))
    return a


def agent_create(data: dict) -> dict:
    agent_id = generate_id()
    defaults = {"model": "gpt-4", "status": "active", "temperature": 0.7}
    _agents[agent_id] = {"id": agent_id, **defaults, **data}
    return _agents[agent_id]


def agent_update(agent_id: str, data: dict) -> dict | None:
    if agent_id not in _agents:
        return None
    _agents[agent_id].update(data)
    return _agents[agent_id]


def agent_delete(agent_id: str) -> bool:
    if agent_id not in _agents:
        return False
    del _agents[agent_id]
    del _agent_tools[agent_id]
    return True


def agent_add_tool(agent_id: str, tool_id: str) -> bool:
    if agent_id not in _agents:
        return False
    _agent_tools[agent_id].add(tool_id)
    return True


def agent_remove_tool(agent_id: str, tool_id: str) -> bool:
    if agent_id not in _agent_tools:
        return False
    _agent_tools[agent_id].discard(tool_id)
    return True


# MCP Servers
def mcp_server_list() -> list[dict]:
    return list(_mcp_servers.values())


def mcp_server_get(server_id: str) -> dict | None:
    return _mcp_servers.get(server_id)


def mcp_server_create(data: dict) -> dict:
    server_id = generate_id()
    _mcp_servers[server_id] = {"id": server_id, **data}
    return _mcp_servers[server_id]


def mcp_server_update(server_id: str, data: dict) -> dict | None:
    if server_id not in _mcp_servers:
        return None
    _mcp_servers[server_id].update(data)
    return _mcp_servers[server_id]


def mcp_server_delete(server_id: str) -> bool:
    if server_id not in _mcp_servers:
        return False
    del _mcp_servers[server_id]
    if server_id in _mcp_tools:
        del _mcp_tools[server_id]
    return True


def mcp_server_tool_list(server_id: str) -> list[dict]:
    return list(_mcp_tools.get(server_id, {}).values())


def mcp_server_tool_add(server_id: str, data: dict) -> dict | None:
    if server_id not in _mcp_servers:
        return None
    tool_id = generate_id()
    _mcp_tools[server_id][tool_id] = {"id": tool_id, "enabled": True, **data}
    return _mcp_tools[server_id][tool_id]


def mcp_server_tool_update(server_id: str, tool_id: str, data: dict) -> dict | None:
    if server_id not in _mcp_tools or tool_id not in _mcp_tools[server_id]:
        return None
    _mcp_tools[server_id][tool_id].update(data)
    return _mcp_tools[server_id][tool_id]


def mcp_server_tool_remove(server_id: str, tool_id: str) -> bool:
    if server_id not in _mcp_tools or tool_id not in _mcp_tools[server_id]:
        return False
    del _mcp_tools[server_id][tool_id]
    return True


# Conversations
def conversation_list() -> list[dict]:
    return list(_conversations.values())


def conversation_get(conv_id: str) -> dict | None:
    return _conversations.get(conv_id)


def conversation_create(data: dict) -> dict:
    conv_id = generate_id()
    _conversations[conv_id] = {"id": conv_id, **data}
    return _conversations[conv_id]


def conversation_update(conv_id: str, data: dict) -> dict | None:
    if conv_id not in _conversations:
        return None
    _conversations[conv_id].update(data)
    return _conversations[conv_id]


def conversation_delete(conv_id: str) -> bool:
    if conv_id not in _conversations:
        return False
    del _conversations[conv_id]
    if conv_id in _conversation_messages:
        del _conversation_messages[conv_id]
    return True


def conversation_message_list(conv_id: str) -> list[dict]:
    return _conversation_messages.get(conv_id, [])[:]


def conversation_message_add(conv_id: str, data: dict) -> dict | None:
    if conv_id not in _conversations:
        return None
    msg_id = generate_id()
    msg = {"id": msg_id, **data}
    _conversation_messages[conv_id].append(msg)
    return msg


# Storage
def storage_list() -> list[dict]:
    return [{"key": k} for k in _storage_files]


def storage_get(key: str) -> bytes | None:
    return _storage_files.get(key)


def storage_put(key: str, content: bytes) -> None:
    _storage_files[key] = content


def storage_delete(key: str) -> bool:
    if key not in _storage_files:
        return False
    del _storage_files[key]
    return True


# Knowledge Sources
def source_list() -> list[dict]:
    return list(_sources.values())


def source_get(source_id: str) -> dict | None:
    return _sources.get(source_id)


def source_create(data: dict) -> dict:
    source_id = data.get("id") or generate_id()
    _sources[source_id] = {"id": source_id, **data}
    return _sources[source_id]


def source_update(source_id: str, data: dict) -> dict | None:
    if source_id not in _sources:
        return None
    _sources[source_id].update(data)
    return _sources[source_id]


def source_delete(source_id: str) -> bool:
    if source_id not in _sources:
        return False
    del _sources[source_id]
    
    # Cascade delete code examples
    code_ids = [c["id"] for c in _code_examples.values() if c.get("sourceId") == source_id]
    for cid in code_ids:
        del _code_examples[cid]
    return True


# Code Examples
def code_example_list() -> list[dict]:
    return list(_code_examples.values())


def code_example_get(code_id: str) -> dict | None:
    return _code_examples.get(code_id)


def code_example_create(data: dict) -> dict:
    code_id = data.get("id") or generate_id()
    _code_examples[code_id] = {"id": code_id, **data}
    return _code_examples[code_id]


def code_example_delete(code_id: str) -> bool:
    if code_id not in _code_examples:
        return False
    del _code_examples[code_id]
    return True

# Supervisor + Human-in-the-Loop
_workflows: dict[str, dict[str, Any]] = {}
_approval_requests: dict[str, dict[str, Any]] = {}
_workflow_approvals: dict[str, list[str]] = defaultdict(list)


def workflow_list() -> list[dict]:
    return list(_workflows.values())


def workflow_get(workflow_id: str) -> dict | None:
    return _workflows.get(workflow_id)


def workflow_create(data: dict) -> dict:
    wf_id = generate_id()
    _workflows[wf_id] = {
        "id": wf_id,
        "status": "running",
        "current_agent": None,
        "history": [],
        **data,
    }
    return _workflows[wf_id]


def workflow_update(workflow_id: str, data: dict) -> dict | None:
    if workflow_id not in _workflows:
        return None
    _workflows[workflow_id].update(data)
    return _workflows[workflow_id]


def workflow_add_history(workflow_id: str, entry: dict) -> bool:
    if workflow_id not in _workflows:
        return False
    _workflows[workflow_id].setdefault("history", []).append(entry)
    return True


def workflow_delete(workflow_id: str) -> bool:
    if workflow_id not in _workflows:
        return False
    del _workflows[workflow_id]
    if workflow_id in _workflow_approvals:
        for apr_id in _workflow_approvals[workflow_id]:
            if apr_id in _approval_requests:
                del _approval_requests[apr_id]
        del _workflow_approvals[workflow_id]
    return True


def approval_create(data: dict) -> dict:
    apr_id = generate_id()
    _approval_requests[apr_id] = {"id": apr_id, "status": "pending", **data}
    wf_id = data.get("workflow_id")
    if wf_id:
        _workflow_approvals[wf_id].append(apr_id)
    return _approval_requests[apr_id]


def approval_get(approval_id: str) -> dict | None:
    return _approval_requests.get(approval_id)


def approval_list_pending(workflow_id: str | None = None) -> list[dict]:
    result = [a for a in _approval_requests.values() if a.get("status") == "pending"]
    if workflow_id:
        result = [a for a in result if a.get("workflow_id") == workflow_id]
    return result


def approval_update(approval_id: str, data: dict) -> dict | None:
    if approval_id not in _approval_requests:
        return None
    _approval_requests[approval_id].update(data)
    return _approval_requests[approval_id]


def approval_list_by_workflow(workflow_id: str) -> list[dict]:
    return [
        _approval_requests[aid]
        for aid in _workflow_approvals.get(workflow_id, [])
        if aid in _approval_requests
    ]
