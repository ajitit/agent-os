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

<<<<<<< HEAD
from collections import defaultdict
=======
from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
>>>>>>> c952205 (Initial upload of AgentOS code)
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
_users: dict[str, dict[str, Any]] = {}
_preferences: dict[str, dict[str, Any]] = {}
_api_keys: dict[str, dict[str, Any]] = {}


def generate_id() -> str:
    return str(uuid4())


# Crews
<<<<<<< HEAD
def crew_list() -> list[dict]:
    return list(_crews.values())


def crew_get(crew_id: str) -> dict | None:
    return _crews.get(crew_id)


def crew_create(data: dict) -> dict:
=======
def crew_list() -> list[dict[str, Any]]:
    return list(_crews.values())


def crew_get(crew_id: str) -> dict[str, Any] | None:
    return _crews.get(crew_id)


def crew_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    crew_id = generate_id()
    _crews[crew_id] = {"id": crew_id, **data}
    return _crews[crew_id]


<<<<<<< HEAD
def crew_update(crew_id: str, data: dict) -> dict | None:
=======
def crew_update(crew_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
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
<<<<<<< HEAD
def agent_list() -> list[dict]:
=======
def agent_list() -> list[dict[str, Any]]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    result = []
    for a in _agents.values():
        r = dict(a)
        r["tool_ids"] = list(_agent_tools.get(a["id"], set()))
        result.append(r)
    return result


<<<<<<< HEAD
def agent_get(agent_id: str) -> dict | None:
=======
def agent_get(agent_id: str) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
    if agent_id not in _agents:
        return None
    a = dict(_agents[agent_id])
    a["tool_ids"] = list(_agent_tools.get(agent_id, set()))
    return a


<<<<<<< HEAD
def agent_create(data: dict) -> dict:
=======
def agent_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    agent_id = generate_id()
    defaults = {"model": "gpt-4", "status": "active", "temperature": 0.7}
    _agents[agent_id] = {"id": agent_id, **defaults, **data}
    return _agents[agent_id]


<<<<<<< HEAD
def agent_update(agent_id: str, data: dict) -> dict | None:
=======
def agent_update(agent_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
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
<<<<<<< HEAD
def mcp_server_list() -> list[dict]:
    return list(_mcp_servers.values())


def mcp_server_get(server_id: str) -> dict | None:
    return _mcp_servers.get(server_id)


def mcp_server_create(data: dict) -> dict:
=======
def mcp_server_list() -> list[dict[str, Any]]:
    return list(_mcp_servers.values())


def mcp_server_get(server_id: str) -> dict[str, Any] | None:
    return _mcp_servers.get(server_id)


def mcp_server_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    server_id = generate_id()
    _mcp_servers[server_id] = {"id": server_id, **data}
    return _mcp_servers[server_id]


<<<<<<< HEAD
def mcp_server_update(server_id: str, data: dict) -> dict | None:
=======
def mcp_server_update(server_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
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


<<<<<<< HEAD
def mcp_server_tool_list(server_id: str) -> list[dict]:
    return list(_mcp_tools.get(server_id, {}).values())


def mcp_server_tool_add(server_id: str, data: dict) -> dict | None:
=======
def mcp_server_tool_list(server_id: str) -> list[dict[str, Any]]:
    return list(_mcp_tools.get(server_id, {}).values())


def mcp_server_tool_add(server_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
    if server_id not in _mcp_servers:
        return None
    tool_id = generate_id()
    _mcp_tools[server_id][tool_id] = {"id": tool_id, "enabled": True, **data}
    return _mcp_tools[server_id][tool_id]


<<<<<<< HEAD
def mcp_server_tool_update(server_id: str, tool_id: str, data: dict) -> dict | None:
=======
def mcp_server_tool_update(server_id: str, tool_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
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
<<<<<<< HEAD
def conversation_list() -> list[dict]:
    return list(_conversations.values())


def conversation_get(conv_id: str) -> dict | None:
    return _conversations.get(conv_id)


def conversation_create(data: dict) -> dict:
=======
def conversation_list() -> list[dict[str, Any]]:
    return list(_conversations.values())


def conversation_get(conv_id: str) -> dict[str, Any] | None:
    return _conversations.get(conv_id)


def conversation_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    conv_id = generate_id()
    _conversations[conv_id] = {"id": conv_id, **data}
    return _conversations[conv_id]


<<<<<<< HEAD
def conversation_update(conv_id: str, data: dict) -> dict | None:
=======
def conversation_update(conv_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
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


<<<<<<< HEAD
def conversation_message_list(conv_id: str) -> list[dict]:
    return _conversation_messages.get(conv_id, [])[:]


def conversation_message_add(conv_id: str, data: dict) -> dict | None:
=======
def conversation_message_list(conv_id: str) -> list[dict[str, Any]]:
    return _conversation_messages.get(conv_id, [])[:]


def conversation_message_add(conv_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
    if conv_id not in _conversations:
        return None
    msg_id = generate_id()
    msg = {"id": msg_id, **data}
    _conversation_messages[conv_id].append(msg)
    return msg


# Storage
<<<<<<< HEAD
def storage_list() -> list[dict]:
=======
def storage_list() -> list[dict[str, Any]]:
>>>>>>> c952205 (Initial upload of AgentOS code)
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
<<<<<<< HEAD
def source_list() -> list[dict]:
    return list(_sources.values())


def source_get(source_id: str) -> dict | None:
    return _sources.get(source_id)


def source_create(data: dict) -> dict:
=======
def source_list() -> list[dict[str, Any]]:
    return list(_sources.values())


def source_get(source_id: str) -> dict[str, Any] | None:
    return _sources.get(source_id)


def source_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    source_id = data.get("id") or generate_id()
    _sources[source_id] = {"id": source_id, **data}
    return _sources[source_id]


<<<<<<< HEAD
def source_update(source_id: str, data: dict) -> dict | None:
=======
def source_update(source_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
    if source_id not in _sources:
        return None
    _sources[source_id].update(data)
    return _sources[source_id]


def source_delete(source_id: str) -> bool:
    if source_id not in _sources:
        return False
    del _sources[source_id]
<<<<<<< HEAD
    
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
    # Cascade delete code examples
    code_ids = [c["id"] for c in _code_examples.values() if c.get("sourceId") == source_id]
    for cid in code_ids:
        del _code_examples[cid]
    return True


# Code Examples
<<<<<<< HEAD
def code_example_list() -> list[dict]:
    return list(_code_examples.values())


def code_example_get(code_id: str) -> dict | None:
    return _code_examples.get(code_id)


def code_example_create(data: dict) -> dict:
=======
def code_example_list() -> list[dict[str, Any]]:
    return list(_code_examples.values())


def code_example_get(code_id: str) -> dict[str, Any] | None:
    return _code_examples.get(code_id)


def code_example_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
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


<<<<<<< HEAD
def workflow_list() -> list[dict]:
    return list(_workflows.values())


def workflow_get(workflow_id: str) -> dict | None:
    return _workflows.get(workflow_id)


def workflow_create(data: dict) -> dict:
=======
def workflow_list() -> list[dict[str, Any]]:
    return list(_workflows.values())


def workflow_get(workflow_id: str) -> dict[str, Any] | None:
    return _workflows.get(workflow_id)


def workflow_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    wf_id = generate_id()
    _workflows[wf_id] = {
        "id": wf_id,
        "status": "running",
        "current_agent": None,
        "history": [],
        **data,
    }
    return _workflows[wf_id]


<<<<<<< HEAD
def workflow_update(workflow_id: str, data: dict) -> dict | None:
=======
def workflow_update(workflow_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
    if workflow_id not in _workflows:
        return None
    _workflows[workflow_id].update(data)
    return _workflows[workflow_id]


<<<<<<< HEAD
def workflow_add_history(workflow_id: str, entry: dict) -> bool:
=======
def workflow_add_history(workflow_id: str, entry: dict[str, Any]) -> bool:
>>>>>>> c952205 (Initial upload of AgentOS code)
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


<<<<<<< HEAD
def approval_create(data: dict) -> dict:
=======
def approval_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    apr_id = generate_id()
    _approval_requests[apr_id] = {"id": apr_id, "status": "pending", **data}
    wf_id = data.get("workflow_id")
    if wf_id:
        _workflow_approvals[wf_id].append(apr_id)
    return _approval_requests[apr_id]


<<<<<<< HEAD
def approval_get(approval_id: str) -> dict | None:
    return _approval_requests.get(approval_id)


def approval_list_pending(workflow_id: str | None = None) -> list[dict]:
=======
def approval_get(approval_id: str) -> dict[str, Any] | None:
    return _approval_requests.get(approval_id)


def approval_list_pending(workflow_id: str | None = None) -> list[dict[str, Any]]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    result = [a for a in _approval_requests.values() if a.get("status") == "pending"]
    if workflow_id:
        result = [a for a in result if a.get("workflow_id") == workflow_id]
    return result


<<<<<<< HEAD
def approval_update(approval_id: str, data: dict) -> dict | None:
=======
def approval_update(approval_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
    if approval_id not in _approval_requests:
        return None
    _approval_requests[approval_id].update(data)
    return _approval_requests[approval_id]


<<<<<<< HEAD
def approval_list_by_workflow(workflow_id: str) -> list[dict]:
=======
def approval_list_by_workflow(workflow_id: str) -> list[dict[str, Any]]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    return [
        _approval_requests[aid]
        for aid in _workflow_approvals.get(workflow_id, [])
        if aid in _approval_requests
    ]


# Users
<<<<<<< HEAD
def user_get_by_email(email: str) -> dict | None:
=======
def user_get_by_email(email: str) -> dict[str, Any] | None:
>>>>>>> c952205 (Initial upload of AgentOS code)
    for u in _users.values():
        if u.get("email") == email:
            return u
    return None


<<<<<<< HEAD
def user_get(user_id: str) -> dict | None:
    return _users.get(user_id)


def user_create(data: dict) -> dict:
=======
def user_get(user_id: str) -> dict[str, Any] | None:
    return _users.get(user_id)


def user_create(data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    user_id = generate_id()
    user = {"id": user_id, **data}
    _users[user_id] = user
    # Initialize default preferences
    preference_update(
        user_id,
        {
            "theme": "system",
            "accentColor": "#007bff",
            "fontSize": "md",
            "defaultPriority": "normal",
            "streamingEnabled": True,
            "showAgentThinking": True,
            "defaultSupervisorBehavior": "auto_route",
            "emailOnFailure": True,
            "emailDigestFrequency": "daily",
        },
    )
    return user


# Preferences
<<<<<<< HEAD
def preference_get(user_id: str) -> dict | None:
    return _preferences.get(user_id)


def preference_update(user_id: str, data: dict) -> dict:
=======
def preference_get(user_id: str) -> dict[str, Any] | None:
    return _preferences.get(user_id)


def preference_update(user_id: str, data: dict[str, Any]) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    if user_id not in _preferences:
        _preferences[user_id] = {"userId": user_id}
    _preferences[user_id].update(data)
    return _preferences[user_id]


# API Keys
<<<<<<< HEAD
def api_key_create(user_id: str, name: str) -> dict:
=======
def api_key_create(user_id: str, name: str) -> dict[str, Any]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    key_id = generate_id()
    # In a real app, internal_key would be hashed
    key = {
        "id": key_id,
        "userId": user_id,
        "name": name,
        "key": f"sk_{generate_id().replace('-', '')}",
        "createdAt": "2024-03-10T00:00:00Z",  # Mock timestamp
    }
    _api_keys[key_id] = key
    return key


<<<<<<< HEAD
def api_key_list(user_id: str) -> list[dict]:
=======
def api_key_list(user_id: str) -> list[dict[str, Any]]:
>>>>>>> c952205 (Initial upload of AgentOS code)
    return [k for k in _api_keys.values() if k.get("userId") == user_id]


def api_key_delete(key_id: str) -> bool:
    if key_id in _api_keys:
        del _api_keys[key_id]
        return True
    return False
<<<<<<< HEAD
=======


# ─── Observability / Tracing ─────────────────────────────────────────────────
_spans: dict[str, dict[str, Any]] = {}
_runs: dict[str, dict[str, Any]] = {}
_obs_logs: list[dict[str, Any]] = []
_metrics_buckets: list[dict[str, Any]] = []


def run_create(data: dict[str, Any]) -> dict[str, Any]:
    run_id = data.get("runId") or generate_id()
    _runs[run_id] = {"runId": run_id, **data}
    return _runs[run_id]


def run_get(run_id: str) -> dict[str, Any] | None:
    return _runs.get(run_id)


def run_update(run_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    if run_id not in _runs:
        return None
    _runs[run_id].update(data)
    return _runs[run_id]


def run_list(
    workflow_id: str | None = None,
    user_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    result = list(_runs.values())
    if workflow_id:
        result = [r for r in result if r.get("workflowId") == workflow_id]
    if user_id:
        result = [r for r in result if r.get("userId") == user_id]
    if status:
        result = [r for r in result if r.get("status") == status]
    return result[-limit:]


def span_create(data: dict[str, Any]) -> dict[str, Any]:
    span_id = data.get("spanId") or generate_id()
    _spans[span_id] = {"spanId": span_id, **data}
    return _spans[span_id]


def span_update(span_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    if span_id not in _spans:
        return None
    _spans[span_id].update(data)
    return _spans[span_id]


def span_list_by_run(run_id: str) -> list[dict[str, Any]]:
    return [s for s in _spans.values() if s.get("runId") == run_id]


def obs_log_append(entry: dict[str, Any]) -> None:
    _obs_logs.append(entry)
    if len(_obs_logs) > 10_000:
        del _obs_logs[0]


def obs_log_list(run_id: str | None = None, level: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    result = list(_obs_logs)
    if run_id:
        result = [entry for entry in result if entry.get("runId") == run_id]
    if level:
        result = [entry for entry in result if entry.get("level") == level]
    return result[-limit:]


def metrics_snapshot() -> dict[str, Any]:
    runs = list(_runs.values())
    total = len(runs)
    success = sum(1 for r in runs if r.get("status") == "complete")
    failed = sum(1 for r in runs if r.get("status") == "failed")
    active = sum(1 for r in runs if r.get("status") == "running")
    durations = [r.get("durationMs", 0) for r in runs if r.get("durationMs")]
    avg_duration = int(sum(durations) / len(durations)) if durations else 0
    total_tokens = sum(r.get("totalTokens", 0) for r in runs)
    return {
        "totalRuns24h": total,
        "successRate": round(success / total * 100, 1) if total else 0,
        "failureRate": round(failed / total * 100, 1) if total else 0,
        "activeRuns": active,
        "avgDurationMs": avg_duration,
        "totalTokens": total_tokens,
    }


# ─── Visual Workflow Definitions ─────────────────────────────────────────────
_workflow_defs: dict[str, dict[str, Any]] = {}


def workflow_def_list(user_id: str | None = None) -> list[dict[str, Any]]:
    result = list(_workflow_defs.values())
    if user_id:
        result = [w for w in result if w.get("userId") == user_id]
    return result


def workflow_def_get(wf_id: str) -> dict[str, Any] | None:
    return _workflow_defs.get(wf_id)


def workflow_def_create(data: dict[str, Any]) -> dict[str, Any]:
    wf_id = generate_id()
    _workflow_defs[wf_id] = {"id": wf_id, "version": 1, **data}
    return _workflow_defs[wf_id]


def workflow_def_update(wf_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    if wf_id not in _workflow_defs:
        return None
    _workflow_defs[wf_id].update(data)
    _workflow_defs[wf_id]["version"] = _workflow_defs[wf_id].get("version", 1) + 1
    return _workflow_defs[wf_id]


def workflow_def_delete(wf_id: str) -> bool:
    if wf_id not in _workflow_defs:
        return False
    del _workflow_defs[wf_id]
    return True


# ─── Supervisor Plans ─────────────────────────────────────────────────────────

# ─── Supervisor Plans ─────────────────────────────────────────────────────────

_plans: dict[str, dict[str, Any]] = {}
_plan_tasks: dict[str, list[dict[str, Any]]] = defaultdict(list)


def plan_create(data: dict[str, Any]) -> dict[str, Any]:
    """Create a new supervisor plan record.

    Args:
        data: Plan fields including goal, userId, workflowId, etc.

    Returns:
        Created plan dict with generated id and createdAt.
    """
    plan_id = generate_id()
    now = datetime.now(UTC).isoformat()
    record: dict[str, Any] = {
        "id": plan_id,
        "createdAt": now,
        "updatedAt": now,
        "status": "draft",
        **data,
    }
    _plans[plan_id] = record
    return record


def plan_get(plan_id: str) -> dict[str, Any] | None:
    """Retrieve a plan by ID.

    Args:
        plan_id: Plan UUID.

    Returns:
        Plan dict or None.
    """
    return _plans.get(plan_id)


def plan_list(
    workflow_id: str | None = None,
    user_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List plans with optional filters.

    Args:
        workflow_id: Filter by originating workflow.
        user_id: Filter by owning user.
        status: Filter by plan status.
        limit: Maximum records to return.

    Returns:
        Plans sorted newest-first.
    """
    result = list(_plans.values())
    if workflow_id:
        result = [p for p in result if p.get("workflowId") == workflow_id]
    if user_id:
        result = [p for p in result if p.get("userId") == user_id]
    if status:
        result = [p for p in result if p.get("status") == status]
    result.sort(key=lambda p: p.get("createdAt", ""), reverse=True)
    return result[:limit]


def plan_update(plan_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update an existing plan.

    Args:
        plan_id: Plan UUID.
        data: Fields to update.

    Returns:
        Updated plan or None if not found.
    """
    if plan_id not in _plans:
        return None
    _plans[plan_id].update({**data, "updatedAt": datetime.now(UTC).isoformat()})
    return _plans[plan_id]


def plan_delete(plan_id: str) -> bool:
    """Delete a plan and all its tasks.

    Args:
        plan_id: Plan UUID.

    Returns:
        True if deleted, False if not found.
    """
    if plan_id not in _plans:
        return False
    del _plans[plan_id]
    _plan_tasks.pop(plan_id, None)
    return True


def plan_task_add(plan_id: str, task: dict[str, Any]) -> dict[str, Any] | None:
    """Append a task to a plan.

    Args:
        plan_id: Parent plan UUID.
        task: Task fields.

    Returns:
        Created task dict or None if plan not found.
    """
    if plan_id not in _plans:
        return None
    task_id = generate_id()
    now = datetime.now(UTC).isoformat()
    entry: dict[str, Any] = {
        "id": task_id,
        "planId": plan_id,
        "status": "pending",
        "createdAt": now,
        "updatedAt": now,
        **task,
    }
    _plan_tasks[plan_id].append(entry)
    return entry


def plan_task_list(plan_id: str) -> list[dict[str, Any]]:
    """List all tasks for a plan ordered by stepNumber.

    Args:
        plan_id: Plan UUID.

    Returns:
        List of task dicts sorted by stepNumber.
    """
    tasks = list(_plan_tasks.get(plan_id, []))
    tasks.sort(key=lambda t: t.get("stepNumber", 0))
    return tasks


def plan_task_update(plan_id: str, task_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a specific task within a plan.

    Args:
        plan_id: Parent plan UUID.
        task_id: Task UUID.
        data: Fields to update.

    Returns:
        Updated task dict or None if not found.
    """
    for task in _plan_tasks.get(plan_id, []):
        if task["id"] == task_id:
            task.update({**data, "updatedAt": datetime.now(UTC).isoformat()})
            return task
    return None


# ─── Audit Log ────────────────────────────────────────────────────────────────

_audit_logs: list[dict[str, Any]] = []
_AUDIT_MAX: int = 50_000


def audit_log(entry: dict[str, Any]) -> dict[str, Any]:
    """Append an immutable audit log entry.

    Never modifies or deletes existing entries.

    Args:
        entry: Audit event fields (actorType, actorId, action, resourceType, etc.)

    Returns:
        Stored audit record with id and timestamp.
    """
    record: dict[str, Any] = {
        "id": generate_id(),
        "timestamp": datetime.now(UTC).isoformat(),
        **entry,
    }
    _audit_logs.append(record)
    if len(_audit_logs) > _AUDIT_MAX:
        del _audit_logs[0]
    return record


def audit_list(
    actor_type: str | None = None,
    actor_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    action: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Query the audit log with filters.

    Args:
        actor_type: Filter by actor type (human, agent, crew, system).
        actor_id: Filter by specific actor ID.
        resource_type: Filter by resource type (plan, agent, workflow, etc.)
        resource_id: Filter by specific resource ID.
        action: Filter by action string (e.g. "plan.approved").
        from_date: ISO timestamp lower bound.
        to_date: ISO timestamp upper bound.
        limit: Maximum records.
        offset: Skip first N records.

    Returns:
        Matching audit entries newest-first.
    """
    result = list(_audit_logs)
    if actor_type:
        result = [e for e in result if e.get("actorType") == actor_type]
    if actor_id:
        result = [e for e in result if e.get("actorId") == actor_id]
    if resource_type:
        result = [e for e in result if e.get("resourceType") == resource_type]
    if resource_id:
        result = [e for e in result if e.get("resourceId") == resource_id]
    if action:
        result = [e for e in result if e.get("action") == action]
    if from_date:
        result = [e for e in result if e.get("timestamp", "") >= from_date]
    if to_date:
        result = [e for e in result if e.get("timestamp", "") <= to_date]
    result.reverse()
    return result[offset : offset + limit]


def audit_get(audit_id: str) -> dict[str, Any] | None:
    """Get a single audit entry by ID.

    Args:
        audit_id: Audit record UUID.

    Returns:
        Audit record or None.
    """
    for entry in _audit_logs:
        if entry.get("id") == audit_id:
            return entry
    return None


def audit_stats() -> dict[str, Any]:
    """Compute aggregate audit statistics.

    Returns:
        Dict with counts by actor type, top actions, and daily event counts.
    """
    from collections import Counter

    actor_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    outcome_counts: Counter[str] = Counter()
    daily_counts: Counter[str] = Counter()

    for e in _audit_logs:
        actor_counts[e.get("actorType", "unknown")] += 1
        action_counts[e.get("action", "unknown")] += 1
        outcome_counts[e.get("outcome", "success")] += 1
        ts = e.get("timestamp", "")
        if ts:
            daily_counts[ts[:10]] += 1

    return {
        "total": len(_audit_logs),
        "by_actor_type": dict(actor_counts),
        "top_actions": actor_counts.most_common(10),
        "by_outcome": dict(outcome_counts),
        "daily_counts": dict(sorted(daily_counts.items())[-30:]),
    }


# ─── Marketplace: Skill Registry ─────────────────────────────────────────────

_skill_registry: dict[str, dict[str, Any]] = {}


def skill_registry_list(category: str | None = None) -> list[dict[str, Any]]:
    """List registered skills with optional category filter.

    Args:
        category: Optional category filter string.

    Returns:
        Skills sorted by name.
    """
    result = list(_skill_registry.values())
    if category:
        result = [s for s in result if s.get("category") == category]
    result.sort(key=lambda s: s.get("name", ""))
    return result


def skill_registry_get(skill_id: str) -> dict[str, Any] | None:
    """Get a skill registry entry by ID.

    Args:
        skill_id: Skill UUID.

    Returns:
        Skill dict or None.
    """
    return _skill_registry.get(skill_id)


def skill_registry_create(data: dict[str, Any]) -> dict[str, Any]:
    """Register a new skill in the marketplace.

    Args:
        data: Skill fields (name, description, category, author, etc.)

    Returns:
        Created skill registry entry.
    """
    skill_id = generate_id()
    now = datetime.now(UTC).isoformat()
    record: dict[str, Any] = {
        "id": skill_id,
        "createdAt": now,
        "updatedAt": now,
        "version": "1.0.0",
        "status": "active",
        "installs": 0,
        **data,
    }
    _skill_registry[skill_id] = record
    return record


def skill_registry_update(skill_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a skill registry entry.

    Args:
        skill_id: Skill UUID.
        data: Fields to update.

    Returns:
        Updated skill or None.
    """
    if skill_id not in _skill_registry:
        return None
    _skill_registry[skill_id].update({**data, "updatedAt": datetime.now(UTC).isoformat()})
    return _skill_registry[skill_id]


def skill_registry_delete(skill_id: str) -> bool:
    """Remove a skill from the registry.

    Args:
        skill_id: Skill UUID.

    Returns:
        True if deleted, False if not found.
    """
    if skill_id not in _skill_registry:
        return False
    del _skill_registry[skill_id]
    return True


def skill_registry_install(skill_id: str) -> dict[str, Any] | None:
    """Increment the install counter for a skill.

    Args:
        skill_id: Skill UUID.

    Returns:
        Updated skill or None.
    """
    if skill_id not in _skill_registry:
        return None
    _skill_registry[skill_id]["installs"] = _skill_registry[skill_id].get("installs", 0) + 1
    return _skill_registry[skill_id]


# ─── Marketplace: Model Registry ─────────────────────────────────────────────

_model_registry: dict[str, dict[str, Any]] = {}

_SEEDED_MODELS: list[dict[str, Any]] = [
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "provider": "OpenAI",
        "type": "chat",
        "contextWindow": 128_000,
        "status": "active",
        "tags": ["flagship", "multimodal"],
        "description": "OpenAI's most capable multimodal model.",
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "OpenAI",
        "type": "chat",
        "contextWindow": 128_000,
        "status": "active",
        "tags": ["fast", "cheap"],
        "description": "Affordable, fast model for lighter tasks.",
    },
    {
        "id": "claude-opus-4-6",
        "name": "Claude Opus 4.6",
        "provider": "Anthropic",
        "type": "chat",
        "contextWindow": 200_000,
        "status": "active",
        "tags": ["flagship", "reasoning"],
        "description": "Anthropic's most intelligent model.",
    },
    {
        "id": "claude-sonnet-4-6",
        "name": "Claude Sonnet 4.6",
        "provider": "Anthropic",
        "type": "chat",
        "contextWindow": 200_000,
        "status": "active",
        "tags": ["balanced"],
        "description": "Balanced performance and speed.",
    },
    {
        "id": "claude-haiku-4-5-20251001",
        "name": "Claude Haiku 4.5",
        "provider": "Anthropic",
        "type": "chat",
        "contextWindow": 200_000,
        "status": "active",
        "tags": ["fast", "cheap"],
        "description": "Fast and cost-effective.",
    },
    {
        "id": "llama-3.1-70b",
        "name": "Llama 3.1 70B",
        "provider": "Meta",
        "type": "chat",
        "contextWindow": 128_000,
        "status": "active",
        "tags": ["open-source"],
        "description": "Meta's open-source flagship model.",
    },
    {
        "id": "text-embedding-3-large",
        "name": "Text Embedding 3 Large",
        "provider": "OpenAI",
        "type": "embedding",
        "contextWindow": 8_192,
        "status": "active",
        "tags": ["embedding"],
        "description": "High-performance text embedding model.",
    },
]

for _m in _SEEDED_MODELS:
    _now_iso = datetime.now(UTC).isoformat()
    _model_registry[_m["id"]] = {
        "createdAt": _now_iso,
        "updatedAt": _now_iso,
        "installs": 0,
        **_m,
    }


def model_registry_list(
    provider: str | None = None,
    model_type: str | None = None,
) -> list[dict[str, Any]]:
    """List registered models with optional filters.

    Args:
        provider: Filter by provider name.
        model_type: Filter by model type (chat, embedding, etc.)

    Returns:
        Models sorted by provider then name.
    """
    result = list(_model_registry.values())
    if provider:
        result = [m for m in result if m.get("provider") == provider]
    if model_type:
        result = [m for m in result if m.get("type") == model_type]
    result.sort(key=lambda m: (m.get("provider", ""), m.get("name", "")))
    return result


def model_registry_get(model_id: str) -> dict[str, Any] | None:
    """Get a model registry entry by ID.

    Args:
        model_id: Model identifier string.

    Returns:
        Model dict or None.
    """
    return _model_registry.get(model_id)


def model_registry_create(data: dict[str, Any]) -> dict[str, Any]:
    """Register a new model in the marketplace.

    Args:
        data: Model fields. Must include 'id' or one will be generated.

    Returns:
        Created model registry entry.
    """
    model_id: str = str(data.get("id") or generate_id())
    now = datetime.now(UTC).isoformat()
    record: dict[str, Any] = {
        "id": model_id,
        "createdAt": now,
        "updatedAt": now,
        "status": "active",
        "installs": 0,
        **data,
    }
    _model_registry[model_id] = record
    return record


def model_registry_update(model_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a model registry entry.

    Args:
        model_id: Model identifier.
        data: Fields to update.

    Returns:
        Updated model or None.
    """
    if model_id not in _model_registry:
        return None
    _model_registry[model_id].update({**data, "updatedAt": datetime.now(UTC).isoformat()})
    return _model_registry[model_id]


def model_registry_delete(model_id: str) -> bool:
    """Remove a model from the registry.

    Args:
        model_id: Model identifier.

    Returns:
        True if deleted, False if not found.
    """
    if model_id not in _model_registry:
        return False
    del _model_registry[model_id]
    return True


def model_registry_install(model_id: str) -> dict[str, Any] | None:
    """Increment the install counter for a model.

    Args:
        model_id: Model identifier.

    Returns:
        Updated model or None.
    """
    if model_id not in _model_registry:
        return None
    _model_registry[model_id]["installs"] = _model_registry[model_id].get("installs", 0) + 1
    return _model_registry[model_id]


# ─── Marketplace: Tool Registry ──────────────────────────────────────────────

_tool_registry: dict[str, dict[str, Any]] = {}

_SEEDED_TOOLS: list[dict[str, Any]] = [
    {
        "name": "web_search",
        "category": "search",
        "description": "Search the web for current information",
        "author": "AgentOS",
        "tags": ["search", "web"],
    },
    {
        "name": "code_interpreter",
        "category": "code",
        "description": "Execute Python code safely in a sandbox",
        "author": "AgentOS",
        "tags": ["code", "python"],
    },
    {
        "name": "file_reader",
        "category": "files",
        "description": "Read and parse local or remote files (PDF, CSV, DOCX)",
        "author": "AgentOS",
        "tags": ["files", "parsing"],
    },
    {
        "name": "email_sender",
        "category": "communication",
        "description": "Send emails via SMTP or SendGrid",
        "author": "AgentOS",
        "tags": ["email", "notify"],
    },
    {
        "name": "sql_query",
        "category": "database",
        "description": "Run read-only SQL against configured data sources",
        "author": "AgentOS",
        "tags": ["database", "sql"],
    },
    {
        "name": "vector_search",
        "category": "search",
        "description": "Semantic similarity search over knowledge bases",
        "author": "AgentOS",
        "tags": ["search", "embeddings"],
    },
    {
        "name": "image_generator",
        "category": "media",
        "description": "Generate images via DALL-E or Stable Diffusion",
        "author": "AgentOS",
        "tags": ["image", "generative"],
    },
    {
        "name": "calendar_api",
        "category": "productivity",
        "description": "Read/write Google or Outlook calendar events",
        "author": "AgentOS",
        "tags": ["calendar", "scheduling"],
    },
]

for _t in _SEEDED_TOOLS:
    _tid = generate_id()
    _now_iso2 = datetime.now(UTC).isoformat()
    _tool_registry[_tid] = {
        "id": _tid,
        "createdAt": _now_iso2,
        "updatedAt": _now_iso2,
        "status": "active",
        "installs": 0,
        "version": "1.0.0",
        **_t,
    }


def tool_registry_list(category: str | None = None) -> list[dict[str, Any]]:
    """List registered tools with optional category filter.

    Args:
        category: Optional category filter string.

    Returns:
        Tools sorted by name.
    """
    result = list(_tool_registry.values())
    if category:
        result = [t for t in result if t.get("category") == category]
    result.sort(key=lambda t: t.get("name", ""))
    return result


def tool_registry_get(tool_id: str) -> dict[str, Any] | None:
    """Get a tool registry entry by ID.

    Args:
        tool_id: Tool UUID.

    Returns:
        Tool dict or None.
    """
    return _tool_registry.get(tool_id)


def tool_registry_create(data: dict[str, Any]) -> dict[str, Any]:
    """Register a new tool in the marketplace.

    Args:
        data: Tool fields (name, category, description, author, etc.)

    Returns:
        Created tool registry entry.
    """
    tool_id = generate_id()
    now = datetime.now(UTC).isoformat()
    record: dict[str, Any] = {
        "id": tool_id,
        "createdAt": now,
        "updatedAt": now,
        "status": "active",
        "installs": 0,
        "version": "1.0.0",
        **data,
    }
    _tool_registry[tool_id] = record
    return record


def tool_registry_update(tool_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Update a tool registry entry.

    Args:
        tool_id: Tool UUID.
        data: Fields to update.

    Returns:
        Updated tool or None.
    """
    if tool_id not in _tool_registry:
        return None
    _tool_registry[tool_id].update({**data, "updatedAt": datetime.now(UTC).isoformat()})
    return _tool_registry[tool_id]


def tool_registry_delete(tool_id: str) -> bool:
    """Remove a tool from the registry.

    Args:
        tool_id: Tool UUID.

    Returns:
        True if deleted, False if not found.
    """
    if tool_id not in _tool_registry:
        return False
    del _tool_registry[tool_id]
    return True


def tool_registry_install(tool_id: str) -> dict[str, Any] | None:
    """Increment the install counter for a tool.

    Args:
        tool_id: Tool UUID.

    Returns:
        Updated tool or None.
    """
    if tool_id not in _tool_registry:
        return None
    _tool_registry[tool_id]["installs"] = _tool_registry[tool_id].get("installs", 0) + 1
    return _tool_registry[tool_id]
>>>>>>> c952205 (Initial upload of AgentOS code)
