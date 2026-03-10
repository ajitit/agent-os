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

from backend.app.main import app

client = TestClient(app)
API_PREFIX = "/api/v1"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "AgentOS" in data["status"]
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
    r = client.post(f"{API_PREFIX}/crews", json={"name": "Research Crew"})
    assert r.status_code == 200
    crew = r.json()
    assert crew["name"] == "Research Crew"
    crew_id = crew["id"]

    # List
    r = client.get(f"{API_PREFIX}/crews")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # Get
    r = client.get(f"{API_PREFIX}/crews/{crew_id}")
    assert r.status_code == 200

    # Update
    r = client.put(f"{API_PREFIX}/crews/{crew_id}", json={"name": "Updated Crew"})
    assert r.status_code == 200
    assert r.json()["name"] == "Updated Crew"

    # Delete
    r = client.delete(f"{API_PREFIX}/crews/{crew_id}")
    assert r.status_code == 204


# Agents
def test_agents_crud():
    # Create
    r = client.post(f"{API_PREFIX}/agents", json={"name": "Research Agent"})
    assert r.status_code == 200
    agent = r.json()
    assert agent["name"] == "Research Agent"
    agent_id = agent["id"]

    # List
    r = client.get(f"{API_PREFIX}/agents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    # Get
    r = client.get(f"{API_PREFIX}/agents/{agent_id}")
    assert r.status_code == 200
    assert r.json()["tool_ids"] == []

    # Assign tool
    r = client.post(f"{API_PREFIX}/agents/{agent_id}/tools/{'tool-1'}")
    assert r.status_code == 204

    # Remove tool
    r = client.delete(f"{API_PREFIX}/agents/{agent_id}/tools/tool-1")
    assert r.status_code == 204

    # Update
    r = client.put(f"{API_PREFIX}/agents/{agent_id}", json={"name": "Coding Agent"})
    assert r.status_code == 200

    # Delete
    r = client.delete(f"{API_PREFIX}/agents/{agent_id}")
    assert r.status_code == 204


# MCP Servers
def test_mcp_servers_crud():
    r = client.post(
        f"{API_PREFIX}/mcp-servers", json={"name": "Test MCP", "url": "http://mcp.local"}
    )
    assert r.status_code == 200
    server = r.json()
    server_id = server["id"]

    r = client.get(f"{API_PREFIX}/mcp-servers/{server_id}/tools")
    assert r.status_code == 200
    assert r.json() == []

    r = client.post(
        f"{API_PREFIX}/mcp-servers/{server_id}/tools",
        json={"name": "search", "description": "Search tool"},
    )
    assert r.status_code == 200
    tool = r.json()
    tool_id = tool["id"]

    r = client.delete(f"{API_PREFIX}/mcp-servers/{server_id}/tools/{tool_id}")
    assert r.status_code == 204

    r = client.delete(f"{API_PREFIX}/mcp-servers/{server_id}")
    assert r.status_code == 204


# Conversations
def test_conversations_crud_and_chat():
    r = client.post(f"{API_PREFIX}/conversations", json={})
    assert r.status_code == 200
    conv = r.json()
    conv_id = conv["id"]

    r = client.post(
        f"{API_PREFIX}/conversations/{conv_id}/messages",
        json={"role": "user", "content": "Hello"},
    )
    assert r.status_code == 200

    r = client.get(f"{API_PREFIX}/conversations/{conv_id}/messages")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    r = client.post(
        f"{API_PREFIX}/conversations/{conv_id}/chat", json={"message": "Hi"}
    )
    assert r.status_code == 200
    assert "response" in r.json()

    r = client.post(
        f"{API_PREFIX}/conversations/{conv_id}/chat/stream", json={"message": "Stream me"}
    )
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")

    r = client.delete(f"{API_PREFIX}/conversations/{conv_id}")
    assert r.status_code == 204


# Storage
def test_storage():
    r = client.post(
        f"{API_PREFIX}/storage/upload",
        files={"file": ("test.txt", b"hello world")},
    )
    assert r.status_code == 200
    data = r.json()
    assert "key" in data

    r = client.get(f"{API_PREFIX}/storage/files")
    assert r.status_code == 200
    keys = [f["key"] for f in r.json()]
    assert data["key"] in keys

    r = client.get(f"{API_PREFIX}/storage/files/{data['key']}")
    assert r.status_code == 200
    assert r.content == b"hello world"

    r = client.get(f"{API_PREFIX}/storage/urls/{data['key']}")
    assert r.status_code == 200

    r = client.delete(f"{API_PREFIX}/storage/files/{data['key']}")
    assert r.status_code == 204


def test_create_task():
    r = client.post(f"{API_PREFIX}/tasks", json={"goal": "Test goal"})
    assert r.status_code == 200
    data = r.json()
    assert data["goal"] == "Test goal"
    assert data["status"] == "queued"


def test_chat_stream():
    r = client.get(f"{API_PREFIX}/chat/stream")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")
    assert "Agent thinking" in r.text or "Done" in r.text


def test_request_id_header():
    r = client.get("/", headers={"X-Request-ID": "test-id-123"})
    assert r.status_code == 200
    assert r.headers.get("X-Request-ID") == "test-id-123"


def test_not_found():
    r = client.get(f"{API_PREFIX}/agents/nonexistent-id")
    assert r.status_code == 404
    assert r.json()["error"] == "NOT_FOUND"


# Skills (Progressive Disclosure)
def test_skills_list():
    r = client.get(f"{API_PREFIX}/skills")
    assert r.status_code == 200
    data = r.json()
    assert "skills" in data
    assert "total" in data
    assert isinstance(data["skills"], list)


def test_skills_get():
    r = client.get(f"{API_PREFIX}/skills/web_research")
    assert r.status_code == 200
    data = r.json()
    assert data["metadata"]["id"] == "web_research"
    assert data["metadata"]["name"] == "Web Research"
    assert "instructions" in data
    assert "resource_paths" in data


def test_skills_resource():
    r = client.get(f"{API_PREFIX}/skills/web_research/resources/tools.py")
    assert r.status_code == 200
    assert b"def web_search" in r.content or b"web_search" in r.content


def test_skills_not_found():
    r = client.get(f"{API_PREFIX}/skills/nonexistent_skill")
    assert r.status_code == 404


# Supervisor + Human-in-the-Loop
def test_supervisor_workflows():
    r = client.post(
        f"{API_PREFIX}/supervisor/workflows",
        json={"goal": "Research EV batteries", "crew_id": None},
    )
    assert r.status_code == 200
    wf = r.json()
    assert wf["goal"] == "Research EV batteries"
    assert wf["status"] == "running"
    workflow_id = wf["id"]

    r = client.get(f"{API_PREFIX}/supervisor/workflows/{workflow_id}")
    assert r.status_code == 200
    assert "approvals" in r.json()

    r = client.post(
        f"{API_PREFIX}/supervisor/workflows/{workflow_id}/pause",
        json={
            "agent_id": "agent-1",
            "action_description": "Execute web search",
            "options": ["approve", "reject"],
        },
    )
    assert r.status_code == 200
    approval = r.json()
    approval_id = approval["id"]

    r = client.get(f"{API_PREFIX}/supervisor/approvals")
    assert r.status_code == 200
    pending = r.json()
    assert len(pending) >= 1

    r = client.post(
        f"{API_PREFIX}/supervisor/approvals/{approval_id}/respond",
        json={"decision": "approve"},
    )
    assert r.status_code == 200
    assert r.json()["decision"] == "approve"


def test_supervisor_approval_modify_requires_feedback():
    r = client.post(f"{API_PREFIX}/supervisor/workflows", json={"goal": "Test"})
    wf_id = r.json()["id"]
    r = client.post(
        f"{API_PREFIX}/supervisor/workflows/{wf_id}/pause",
        json={"agent_id": "a1", "action_description": "Do X"},
    )
    apr_id = r.json()["id"]
    r = client.post(
        f"{API_PREFIX}/supervisor/approvals/{apr_id}/respond",
        json={"decision": "modify"},
    )
    assert r.status_code == 422
