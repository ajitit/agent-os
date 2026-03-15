"""
File: test_api.py

Purpose:
Comprehensive integration tests for the FastAPI application routes, encompassing
all primary modules like agents, crews, storage, supervisor, and chat.

Key Functionalities:
- Spin up a `TestClient` instance against the main `app`
- Test full CRUD lifecycles for Agent, Crew, Storage, Task, and MCP Server endpoints
- Verify health check, missing route (404), and error handling formats
- Validate the complex supervisor workflows including pause and respond mechanics

Inputs:
- Mocked or temporary database connections (in-memory app state)

Outputs:
- Extensive test assertions against HTTP status codes and JSON payloads

Interacting Files / Modules:
- backend.app.main
"""

from fastapi.testclient import TestClient

from backend.api.stores import user_create
from backend.app.main import app
from backend.core.security import create_access_token, hash_password

client = TestClient(app)
API_PREFIX = "/api/v1"

# ── Module-level auth — created once for the whole test file ─────────────────

def _make_auth_headers() -> dict[str, str]:
    """Create a test admin user and return Bearer auth headers.

    Returns:
        Dict with Authorization header.
    """
    user = user_create({
        "email": "integration-test@vishwakarma.test",
        "hashed_password": hash_password("testpassword123"),
        "full_name": "Integration Tester",
        "role": "admin",
    })
    token = create_access_token({"sub": user["id"]})
    return {"Authorization": f"Bearer {token}"}


_AUTH = _make_auth_headers()


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Vishwakarma" in data["status"]
    assert "docs" in data


def test_health():
    response = client.get(f"{API_PREFIX}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_api_health_alias():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_readiness():
    response = client.get(f"{API_PREFIX}/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True


# Crews
def test_crews_crud():
    # Create
    r = client.post(f"{API_PREFIX}/crews", json={"name": "Research Crew"}, headers=_AUTH)
    assert r.status_code in (200, 201)
    body = r.json()
    crew = body.get("data", body)
    assert crew["name"] == "Research Crew"
    crew_id = crew["id"]

    # List
    r = client.get(f"{API_PREFIX}/crews", headers=_AUTH)
    assert r.status_code == 200
    body = r.json()
    crews_list = body.get("data", body) if isinstance(body, dict) else body
    assert len(crews_list) >= 1

    # Get
    r = client.get(f"{API_PREFIX}/crews/{crew_id}", headers=_AUTH)
    assert r.status_code == 200

    # Update
    r = client.put(f"{API_PREFIX}/crews/{crew_id}", json={"name": "Updated Crew"}, headers=_AUTH)
    assert r.status_code == 200
    body = r.json()
    updated = body.get("data", body)
    assert updated["name"] == "Updated Crew"

    # Delete
    r = client.delete(f"{API_PREFIX}/crews/{crew_id}", headers=_AUTH)
    assert r.status_code == 204


# Agents
def test_agents_crud():
    # Create
    r = client.post(f"{API_PREFIX}/agents", json={"name": "Research Agent"}, headers=_AUTH)
    assert r.status_code == 200
    agent = r.json().get("data") or r.json()
    assert agent["name"] == "Research Agent"
    agent_id = agent["id"]

    # List
    r = client.get(f"{API_PREFIX}/agents", headers=_AUTH)
    assert r.status_code == 200
    body = r.json()
    agents_list = body.get("data", body) if isinstance(body, dict) else body
    assert isinstance(agents_list, list)

    # Get
    r = client.get(f"{API_PREFIX}/agents/{agent_id}", headers=_AUTH)
    assert r.status_code == 200
    agent_detail = r.json().get("data") or r.json()
    assert agent_detail["tool_ids"] == []

    # Assign tool
    r = client.post(f"{API_PREFIX}/agents/{agent_id}/tools/tool-1", headers=_AUTH)
    assert r.status_code == 204

    # Remove tool
    r = client.delete(f"{API_PREFIX}/agents/{agent_id}/tools/tool-1", headers=_AUTH)
    assert r.status_code == 204

    # Update
    r = client.put(f"{API_PREFIX}/agents/{agent_id}", json={"name": "Coding Agent"}, headers=_AUTH)
    assert r.status_code == 200

    # Delete
    r = client.delete(f"{API_PREFIX}/agents/{agent_id}", headers=_AUTH)
    assert r.status_code == 204


# MCP Servers
def test_mcp_servers_crud():
    r = client.post(
        f"{API_PREFIX}/mcp-servers", json={"name": "Test MCP", "url": "http://mcp.local"},
        headers=_AUTH,
    )
    assert r.status_code in (200, 201)
    body = r.json()
    server = body.get("data", body)
    server_id = server["id"]

    r = client.get(f"{API_PREFIX}/mcp-servers/{server_id}/tools", headers=_AUTH)
    assert r.status_code == 200
    body = r.json()
    tools = body.get("data", body)
    assert tools == []

    r = client.post(
        f"{API_PREFIX}/mcp-servers/{server_id}/tools",
        json={"name": "search", "description": "Search tool"},
        headers=_AUTH,
    )
    assert r.status_code in (200, 201)
    body = r.json()
    tool = body.get("data", body)
    tool_id = tool["id"]

    r = client.delete(f"{API_PREFIX}/mcp-servers/{server_id}/tools/{tool_id}", headers=_AUTH)
    assert r.status_code == 204

    r = client.delete(f"{API_PREFIX}/mcp-servers/{server_id}", headers=_AUTH)
    assert r.status_code == 204


# Conversations
def test_conversations_crud_and_chat():
    r = client.post(f"{API_PREFIX}/conversations", json={}, headers=_AUTH)
    assert r.status_code in (200, 201)
    body = r.json()
    conv = body.get("data", body)
    conv_id = conv["id"]

    r = client.post(
        f"{API_PREFIX}/conversations/{conv_id}/messages",
        json={"role": "user", "content": "Hello"},
        headers=_AUTH,
    )
    assert r.status_code in (200, 201)

    r = client.get(f"{API_PREFIX}/conversations/{conv_id}/messages", headers=_AUTH)
    assert r.status_code == 200
    assert len(r.json()) >= 1

    r = client.post(
        f"{API_PREFIX}/conversations/{conv_id}/chat", json={"message": "Hi"}, headers=_AUTH
    )
    assert r.status_code in (200, 201)
    chat_body = r.json()
    chat_data = chat_body.get("data", chat_body)
    assert "response" in chat_data

    r = client.post(
        f"{API_PREFIX}/conversations/{conv_id}/chat/stream", json={"message": "Stream me"},
        headers=_AUTH,
    )
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")

    r = client.delete(f"{API_PREFIX}/conversations/{conv_id}", headers=_AUTH)
    assert r.status_code == 204


# Storage
def test_storage():
    r = client.post(
        f"{API_PREFIX}/storage/upload",
        files={"file": ("test.txt", b"hello world")},
        headers=_AUTH,
    )
    assert r.status_code == 200
    body = r.json()
    data = body.get("data", body)
    assert "key" in data

    r = client.get(f"{API_PREFIX}/storage/files", headers=_AUTH)
    assert r.status_code == 200
    list_body = r.json()
    files_list = list_body.get("data", list_body)
    keys = [f["key"] for f in files_list]
    assert data["key"] in keys

    r = client.get(f"{API_PREFIX}/storage/files/{data['key']}", headers=_AUTH)
    assert r.status_code == 200
    assert r.content == b"hello world"

    r = client.get(f"{API_PREFIX}/storage/urls/{data['key']}", headers=_AUTH)
    assert r.status_code == 200

    r = client.delete(f"{API_PREFIX}/storage/files/{data['key']}", headers=_AUTH)
    assert r.status_code == 204


def test_create_task():
    r = client.post(f"{API_PREFIX}/tasks", json={"goal": "Test goal"}, headers=_AUTH)
    assert r.status_code in (200, 201)
    body = r.json()
    data = body.get("data", body)
    assert data["goal"] == "Test goal"
    assert data["status"] == "queued"


def test_chat_stream():
    """Chat stream SSE endpoint returns 404 for unknown run ID."""
    r = client.get(f"{API_PREFIX}/chat/stream/nonexistent-run-id", headers=_AUTH)
    assert r.status_code == 404


def test_request_id_header():
    r = client.get("/", headers={"X-Request-ID": "test-id-123"})
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID") == "test-id-123"


def test_not_found():
    r = client.get(f"{API_PREFIX}/agents/nonexistent-id", headers=_AUTH)
    assert r.status_code == 404
    assert r.json()["error"] == "NOT_FOUND"


# Skills (Progressive Disclosure)
def test_skills_list():
    r = client.get(f"{API_PREFIX}/skills", headers=_AUTH)
    assert r.status_code == 200
    body = r.json()
    data = body.get("data", body)
    assert "skills" in data
    assert "total" in data
    assert isinstance(data["skills"], list)


def test_skills_get():
    r = client.get(f"{API_PREFIX}/skills/web_research", headers=_AUTH)
    assert r.status_code == 200
    body = r.json()
    data = body.get("data", body)
    assert data["metadata"]["id"] == "web_research"
    assert data["metadata"]["name"] == "Web Research"
    assert "instructions" in data
    assert "resource_paths" in data


def test_skills_resource():
    r = client.get(f"{API_PREFIX}/skills/web_research/resources/tools.py", headers=_AUTH)
    assert r.status_code == 200
    assert b"def web_search" in r.content or b"web_search" in r.content


def test_skills_not_found():
    r = client.get(f"{API_PREFIX}/skills/nonexistent_skill", headers=_AUTH)
    assert r.status_code == 404


# Supervisor + Human-in-the-Loop
def test_supervisor_workflows():
    r = client.post(
        f"{API_PREFIX}/supervisor/workflows",
        json={"goal": "Research EV batteries", "crew_id": None},
        headers=_AUTH,
    )
    assert r.status_code in (200, 201)
    body = r.json()
    wf = body.get("data", body)
    assert wf["goal"] == "Research EV batteries"
    assert wf["status"] == "running"
    workflow_id = wf["id"]

    r = client.get(f"{API_PREFIX}/supervisor/workflows/{workflow_id}", headers=_AUTH)
    assert r.status_code == 200
    detail_body = r.json()
    detail = detail_body.get("data", detail_body)
    assert "approvals" in detail

    r = client.post(
        f"{API_PREFIX}/supervisor/workflows/{workflow_id}/pause",
        json={
            "agent_id": "agent-1",
            "action_description": "Execute web search",
            "options": ["approve", "reject"],
        },
        headers=_AUTH,
    )
    assert r.status_code in (200, 201)
    pause_body = r.json()
    approval = pause_body.get("data", pause_body)
    approval_id = approval["id"]

    r = client.get(f"{API_PREFIX}/supervisor/approvals", headers=_AUTH)
    assert r.status_code == 200
    pending_body = r.json()
    pending = pending_body.get("data", pending_body)
    assert len(pending) >= 1

    r = client.post(
        f"{API_PREFIX}/supervisor/approvals/{approval_id}/respond",
        json={"decision": "approve"},
        headers=_AUTH,
    )
    assert r.status_code == 200
    resp_body = r.json()
    resp = resp_body.get("data", resp_body)
    assert resp["decision"] == "approve"


def test_supervisor_approval_modify_requires_feedback():
    r = client.post(f"{API_PREFIX}/supervisor/workflows", json={"goal": "Test"}, headers=_AUTH)
    body = r.json()
    wf_id = body.get("data", body)["id"]
    r = client.post(
        f"{API_PREFIX}/supervisor/workflows/{wf_id}/pause",
        json={"agent_id": "a1", "action_description": "Do X"},
        headers=_AUTH,
    )
    pause_body = r.json()
    apr_id = pause_body.get("data", pause_body)["id"]
    r = client.post(
        f"{API_PREFIX}/supervisor/approvals/{apr_id}/respond",
        json={"decision": "modify"},
        headers=_AUTH,
    )
    assert r.status_code == 422
