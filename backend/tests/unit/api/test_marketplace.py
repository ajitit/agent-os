"""
Unit and integration tests for the Marketplace API.

Coverage targets:
- Skills: list, create (admin), get, update, delete, install
- Models: list, create (admin), get, update, delete, install
- Tools: list, create (developer), get, update, delete, install
- RBAC: non-admin users cannot create/delete
- Seeded data: pre-populated models and tools exist at startup
- Install counter increments correctly
- JWT enforcement
- Response envelope conforms to APIResponse[T]
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.api.stores import user_create
from backend.app.main import app
from backend.core.security import create_access_token, hash_password

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def client() -> TestClient:
    """Return a TestClient for the main FastAPI application."""
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    """Return valid Bearer headers for an admin user.

    Returns:
        Auth header dict.
    """
    user = user_create({
        "email": f"mkt-admin-{id(object())}@vishwakarma.test",
        "hashed_password": hash_password("adminpass123"),
        "full_name": "Marketplace Admin",
        "role": "admin",
    })
    return {"Authorization": f"Bearer {create_access_token({'sub': user['id']})}"}


@pytest.fixture()
def dev_headers() -> dict[str, str]:
    """Return valid Bearer headers for a developer user.

    Returns:
        Auth header dict.
    """
    user = user_create({
        "email": f"mkt-dev-{id(object())}@vishwakarma.test",
        "hashed_password": hash_password("devpass123"),
        "full_name": "Marketplace Dev",
        "role": "developer",
    })
    return {"Authorization": f"Bearer {create_access_token({'sub': user['id']})}"}


@pytest.fixture()
def operator_headers() -> dict[str, str]:
    """Return Bearer headers for an operator user (no create/delete rights).

    Returns:
        Auth header dict.
    """
    user = user_create({
        "email": f"mkt-op-{id(object())}@vishwakarma.test",
        "hashed_password": hash_password("oppass123"),
        "full_name": "Marketplace Operator",
        "role": "operator",
    })
    return {"Authorization": f"Bearer {create_access_token({'sub': user['id']})}"}


def _new_skill(suffix: str = "") -> dict[str, Any]:
    """Return a valid SkillCreate payload.

    Args:
        suffix: Unique suffix to avoid name collisions.

    Returns:
        Dict suitable for POST /marketplace/skills.
    """
    return {
        "name": f"test-skill-{suffix}",
        "description": "A test skill for unit testing",
        "category": "research",
        "author": "TestSuite",
        "version": "1.0.0",
        "tags": ["test", "unit"],
    }


def _new_tool(suffix: str = "") -> dict[str, Any]:
    """Return a valid ToolCreate payload.

    Args:
        suffix: Unique suffix to avoid name collisions.

    Returns:
        Dict suitable for POST /marketplace/tools.
    """
    return {
        "name": f"test-tool-{suffix}",
        "category": "code",
        "description": "A test tool for unit testing",
        "author": "TestSuite",
        "version": "1.0.0",
        "tags": ["test"],
    }


# ── Models ────────────────────────────────────────────────────────────────────


class TestMarketplaceModels:
    """Tests for GET/POST/PUT/DELETE /marketplace/models."""

    def test_list_models_seeded(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/models returns pre-seeded models."""
        r = client.get("/api/v1/marketplace/models", headers=operator_headers)
        assert r.status_code == 200
        models = r.json()["data"]
        assert isinstance(models, list)
        assert len(models) >= 5

    def test_list_models_includes_anthropic(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """Pre-seeded models include Anthropic Claude."""
        r = client.get("/api/v1/marketplace/models", headers=operator_headers)
        providers = [m["provider"] for m in r.json()["data"]]
        assert "Anthropic" in providers

    def test_list_models_filter_by_provider(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/models?provider=OpenAI returns only OpenAI models."""
        r = client.get("/api/v1/marketplace/models?provider=OpenAI", headers=operator_headers)
        assert r.status_code == 200
        models = r.json()["data"]
        assert len(models) >= 1
        assert all(m["provider"] == "OpenAI" for m in models)

    def test_list_models_filter_by_type(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/models?type=embedding returns only embedding models."""
        r = client.get("/api/v1/marketplace/models?type=embedding", headers=operator_headers)
        models = r.json()["data"]
        assert all(m["type"] == "embedding" for m in models)

    def test_get_model_by_id(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/models/{id} returns model detail."""
        r = client.get("/api/v1/marketplace/models/gpt-4o", headers=operator_headers)
        assert r.status_code == 200
        model = r.json()["data"]
        assert model["id"] == "gpt-4o"
        assert model["provider"] == "OpenAI"

    def test_get_model_404(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/models/{id} returns 404 for unknown model."""
        r = client.get("/api/v1/marketplace/models/nonexistent", headers=operator_headers)
        assert r.status_code == 404

    def test_create_model_admin(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        """Admin can POST /marketplace/models."""
        payload = {
            "id": "test-model-001",
            "name": "Test Model",
            "provider": "TestProvider",
            "type": "chat",
            "context_window": 8192,
            "description": "A test model",
        }
        r = client.post("/api/v1/marketplace/models", json=payload, headers=admin_headers)
        assert r.status_code == 200
        model = r.json()["data"]
        assert model["name"] == "Test Model"
        assert model["provider"] == "TestProvider"

    def test_create_model_forbidden_for_operator(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """Operator cannot POST /marketplace/models."""
        payload = {
            "id": "op-model",
            "name": "Op Model",
            "provider": "X",
            "type": "chat",
            "context_window": 4096,
        }
        r = client.post("/api/v1/marketplace/models", json=payload, headers=operator_headers)
        assert r.status_code == 403

    def test_install_model_increments_count(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """POST /marketplace/models/{id}/install increments installs."""
        r_before = client.get("/api/v1/marketplace/models/gpt-4o-mini", headers=operator_headers)
        before = r_before.json()["data"]["installs"]
        r = client.post("/api/v1/marketplace/models/gpt-4o-mini/install", headers=operator_headers)
        assert r.status_code == 200
        after = r.json()["data"]["installs"]
        assert after == before + 1

    def test_install_missing_model_404(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """POST /marketplace/models/missing/install returns 404."""
        r = client.post("/api/v1/marketplace/models/missing/install", headers=operator_headers)
        assert r.status_code == 404

    def test_models_require_auth(self, client: TestClient) -> None:
        """GET /marketplace/models requires Bearer JWT."""
        assert client.get("/api/v1/marketplace/models").status_code == 401


# ── Skills ────────────────────────────────────────────────────────────────────


class TestMarketplaceSkills:
    """Tests for GET/POST/PUT/DELETE /marketplace/skills."""

    def test_list_skills_empty_by_default(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/skills returns a list (may be empty at start)."""
        r = client.get("/api/v1/marketplace/skills", headers=operator_headers)
        assert r.status_code == 200
        assert isinstance(r.json()["data"], list)

    def test_create_and_get_skill(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        """Admin can create a skill and then retrieve it."""
        payload = _new_skill("create-01")
        r = client.post("/api/v1/marketplace/skills", json=payload, headers=admin_headers)
        assert r.status_code == 200
        skill = r.json()["data"]
        assert skill["name"] == payload["name"]
        assert skill["category"] == "research"
        skill_id = skill["id"]

        r2 = client.get(f"/api/v1/marketplace/skills/{skill_id}", headers=admin_headers)
        assert r2.status_code == 200
        assert r2.json()["data"]["id"] == skill_id

    def test_developer_can_create_skill(self, client: TestClient, dev_headers: dict[str, str]) -> None:
        """Developer role can create skills."""
        r = client.post("/api/v1/marketplace/skills", json=_new_skill("dev-01"), headers=dev_headers)
        assert r.status_code == 200

    def test_operator_cannot_create_skill(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """Operator role cannot create skills."""
        r = client.post("/api/v1/marketplace/skills", json=_new_skill("op-01"), headers=operator_headers)
        assert r.status_code == 403

    def test_get_skill_404(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/skills/{id} returns 404 for unknown id."""
        r = client.get("/api/v1/marketplace/skills/does-not-exist", headers=operator_headers)
        assert r.status_code == 404

    def test_update_skill(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        """Admin can update a skill's description."""
        r = client.post("/api/v1/marketplace/skills", json=_new_skill("upd-01"), headers=admin_headers)
        sid = r.json()["data"]["id"]
        r2 = client.put(
            f"/api/v1/marketplace/skills/{sid}",
            json={"description": "Updated description"},
            headers=admin_headers,
        )
        assert r2.status_code == 200
        assert r2.json()["data"]["description"] == "Updated description"

    def test_delete_skill(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        """Admin can delete a skill."""
        r = client.post("/api/v1/marketplace/skills", json=_new_skill("del-01"), headers=admin_headers)
        sid = r.json()["data"]["id"]
        r2 = client.delete(f"/api/v1/marketplace/skills/{sid}", headers=admin_headers)
        assert r2.status_code == 204
        r3 = client.get(f"/api/v1/marketplace/skills/{sid}", headers=admin_headers)
        assert r3.status_code == 404

    def test_install_increments(self, client: TestClient, admin_headers: dict[str, str], operator_headers: dict[str, str]) -> None:
        """POST /marketplace/skills/{id}/install increments count."""
        r = client.post("/api/v1/marketplace/skills", json=_new_skill("inst-01"), headers=admin_headers)
        sid = r.json()["data"]["id"]
        before = r.json()["data"]["installs"]

        r2 = client.post(f"/api/v1/marketplace/skills/{sid}/install", headers=operator_headers)
        assert r2.status_code == 200
        assert r2.json()["data"]["installs"] == before + 1

    def test_filter_by_category(self, client: TestClient, admin_headers: dict[str, str]) -> None:
        """GET /marketplace/skills?category=research returns matching skills."""
        client.post("/api/v1/marketplace/skills", json=_new_skill("cat-01"), headers=admin_headers)
        r = client.get("/api/v1/marketplace/skills?category=research", headers=admin_headers)
        assert r.status_code == 200
        skills = r.json()["data"]
        assert all(s["category"] == "research" for s in skills)


# ── Tools ─────────────────────────────────────────────────────────────────────


class TestMarketplaceTools:
    """Tests for GET/POST/PUT/DELETE /marketplace/tools."""

    def test_list_tools_seeded(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET /marketplace/tools returns pre-seeded tools."""
        r = client.get("/api/v1/marketplace/tools", headers=operator_headers)
        assert r.status_code == 200
        tools = r.json()["data"]
        assert isinstance(tools, list)
        assert len(tools) >= 5

    def test_list_tools_includes_web_search(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """Pre-seeded tools include web_search."""
        r = client.get("/api/v1/marketplace/tools", headers=operator_headers)
        names = [t["name"] for t in r.json()["data"]]
        assert "web_search" in names

    def test_create_tool_developer(self, client: TestClient, dev_headers: dict[str, str]) -> None:
        """Developer can create a tool."""
        r = client.post("/api/v1/marketplace/tools", json=_new_tool("dev-001"), headers=dev_headers)
        assert r.status_code == 200
        assert r.json()["data"]["name"] == "test-tool-dev-001"

    def test_operator_cannot_create_tool(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """Operator cannot create tools."""
        r = client.post("/api/v1/marketplace/tools", json=_new_tool("op-001"), headers=operator_headers)
        assert r.status_code == 403

    def test_get_tool_404(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """GET unknown tool returns 404."""
        r = client.get("/api/v1/marketplace/tools/no-such-tool", headers=operator_headers)
        assert r.status_code == 404

    def test_install_tool_increments(self, client: TestClient, operator_headers: dict[str, str]) -> None:
        """POST /marketplace/tools/{id}/install increments installs."""
        r_list = client.get("/api/v1/marketplace/tools", headers=operator_headers)
        first_tool = r_list.json()["data"][0]
        tid = first_tool["id"]
        before = first_tool["installs"]
        r = client.post(f"/api/v1/marketplace/tools/{tid}/install", headers=operator_headers)
        assert r.status_code == 200
        assert r.json()["data"]["installs"] == before + 1

    def test_tools_require_auth(self, client: TestClient) -> None:
        """All tool endpoints require Bearer JWT."""
        assert client.get("/api/v1/marketplace/tools").status_code == 401
