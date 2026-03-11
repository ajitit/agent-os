"""
Unit and integration tests for the Supervisor Plans API.

Coverage targets:
- Plan CRUD (create, list, get, update, delete)
- Plan task management (add, list, update)
- Approve / reject lifecycle transitions
- Audit log instrumentation on every mutating operation
- JWT authentication enforcement
- 404 handling for missing resources
- Response envelope conforms to APIResponse[T] schema
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from backend.api.stores import audit_list, user_create
from backend.app.main import app
from backend.core.security import create_access_token, hash_password

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def client() -> TestClient:
    """Return a TestClient for the main FastAPI application."""
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    """Create a test user and return valid Bearer auth headers.

    Returns:
        Dict with Authorization header.
    """
    user = user_create({
        "email": "plans-test@agentos.test",
        "hashed_password": hash_password("testpassword123"),
        "full_name": "Plan Tester",
        "role": "admin",
    })
    token = create_access_token({"sub": user["id"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    """Admin user headers for role-gated endpoints.

    Returns:
        Dict with Authorization header for admin user.
    """
    user = user_create({
        "email": "plans-admin@agentos.test",
        "hashed_password": hash_password("adminpass123"),
        "full_name": "Admin User",
        "role": "admin",
    })
    token = create_access_token({"sub": user["id"]})
    return {"Authorization": f"Bearer {token}"}


# ── Helper ────────────────────────────────────────────────────────────────────


def _create_plan(client: TestClient, headers: dict[str, str], goal: str = "Test goal") -> dict[str, Any]:
    """Create a plan and return the response data dict.

    Args:
        client: FastAPI TestClient.
        headers: Auth headers.
        goal: Plan goal text.

    Returns:
        Created plan dict from response data.
    """
    r = client.post("/api/v1/plans", json={"goal": goal}, headers=headers)
    assert r.status_code == 200, r.text
    envelope = r.json()
    assert "data" in envelope
    return envelope["data"]


# ── Plan CRUD ─────────────────────────────────────────────────────────────────


class TestPlanCrud:
    """Tests for basic plan create / read / update / delete."""

    def test_create_plan_returns_envelope(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """POST /plans returns APIResponse envelope with plan data."""
        r = client.post("/api/v1/plans", json={"goal": "Analyse the sales report"}, headers=auth_headers)
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert "meta" in body
        plan = body["data"]
        assert plan["goal"] == "Analyse the sales report"
        assert plan["status"] == "draft"
        assert "id" in plan

    def test_create_plan_with_steps(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """POST /plans with pre-defined steps stores them."""
        r = client.post(
            "/api/v1/plans",
            json={"goal": "Deploy app", "steps": ["Build", "Test", "Deploy"]},
            headers=auth_headers,
        )
        assert r.status_code == 200
        plan = r.json()["data"]
        assert plan["steps"] == ["Build", "Test", "Deploy"]

    def test_create_plan_empty_goal_rejected(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """POST /plans with empty goal returns 422."""
        r = client.post("/api/v1/plans", json={"goal": ""}, headers=auth_headers)
        assert r.status_code == 422

    def test_list_plans_returns_list(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /plans returns a list of plan dicts."""
        _create_plan(client, auth_headers, "Plan A")
        _create_plan(client, auth_headers, "Plan B")
        r = client.get("/api/v1/plans", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_list_plans_filter_by_status(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /plans?plan_status=draft returns only draft plans."""
        _create_plan(client, auth_headers, "Draft plan 1")
        r = client.get("/api/v1/plans?plan_status=draft", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert all(p["status"] == "draft" for p in data)

    def test_get_plan_includes_tasks(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /plans/{id} returns plan with tasks array."""
        plan = _create_plan(client, auth_headers)
        r = client.get(f"/api/v1/plans/{plan['id']}", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["id"] == plan["id"]
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_get_plan_404_unknown(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /plans/{id} with unknown id returns 404."""
        r = client.get("/api/v1/plans/no-such-plan", headers=auth_headers)
        assert r.status_code == 404

    def test_update_plan_goal(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """PUT /plans/{id} updates the goal field."""
        plan = _create_plan(client, auth_headers, "Old goal")
        r = client.put(f"/api/v1/plans/{plan['id']}", json={"goal": "New goal"}, headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["data"]["goal"] == "New goal"

    def test_update_plan_404(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """PUT /plans/{id} with unknown id returns 404."""
        r = client.put("/api/v1/plans/missing", json={"goal": "x"}, headers=auth_headers)
        assert r.status_code == 404

    def test_delete_plan(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """DELETE /plans/{id} removes the plan."""
        plan = _create_plan(client, auth_headers, "To delete")
        r = client.delete(f"/api/v1/plans/{plan['id']}", headers=auth_headers)
        assert r.status_code == 204
        # Confirm gone
        r2 = client.get(f"/api/v1/plans/{plan['id']}", headers=auth_headers)
        assert r2.status_code == 404

    def test_delete_plan_404(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """DELETE /plans/{id} with unknown id returns 404."""
        r = client.delete("/api/v1/plans/nope", headers=auth_headers)
        assert r.status_code == 404

    def test_requires_auth(self, client: TestClient) -> None:
        """All plan endpoints require Bearer JWT."""
        assert client.get("/api/v1/plans").status_code == 401
        assert client.post("/api/v1/plans", json={"goal": "x"}).status_code == 401


# ── Plan lifecycle ────────────────────────────────────────────────────────────


class TestPlanLifecycle:
    """Tests for approve / reject plan lifecycle transitions."""

    def test_approve_plan(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """POST /plans/{id}/approve transitions status to approved."""
        plan = _create_plan(client, auth_headers, "Approve me")
        r = client.post(f"/api/v1/plans/{plan['id']}/approve", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["data"]["status"] == "approved"

    def test_reject_plan(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """POST /plans/{id}/reject transitions status to rejected."""
        plan = _create_plan(client, auth_headers, "Reject me")
        r = client.post(
            f"/api/v1/plans/{plan['id']}/reject",
            json={"reason": "Not aligned with Q3 priorities."},
            headers=auth_headers,
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["status"] == "rejected"
        assert data["rejectionReason"] == "Not aligned with Q3 priorities."

    def test_approve_missing_plan_404(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """POST /plans/missing/approve returns 404."""
        r = client.post("/api/v1/plans/missing/approve", headers=auth_headers)
        assert r.status_code == 404

    def test_approve_complete_plan_conflicts(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Approving a complete plan returns 409 Conflict."""
        plan = _create_plan(client, auth_headers, "Already done")
        client.put(
            f"/api/v1/plans/{plan['id']}",
            json={"status": "complete"},
            headers=auth_headers,
        )
        r = client.post(f"/api/v1/plans/{plan['id']}/approve", headers=auth_headers)
        assert r.status_code == 409


# ── Plan tasks ────────────────────────────────────────────────────────────────


class TestPlanTasks:
    """Tests for plan task sub-resource."""

    def test_add_and_list_tasks(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """POST /plans/{id}/tasks adds a task; GET lists it."""
        plan = _create_plan(client, auth_headers, "Tasked plan")
        task_payload = {
            "title": "Research phase",
            "description": "Gather all relevant data",
            "step_number": 1,
        }
        r = client.post(f"/api/v1/plans/{plan['id']}/tasks", json=task_payload, headers=auth_headers)
        assert r.status_code == 200
        task = r.json()["data"]
        assert task["title"] == "Research phase"
        assert task["stepNumber"] == 1
        assert task["status"] == "pending"

        r2 = client.get(f"/api/v1/plans/{plan['id']}/tasks", headers=auth_headers)
        assert r2.status_code == 200
        tasks = r2.json()["data"]
        assert any(t["title"] == "Research phase" for t in tasks)

    def test_update_task_status(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """PUT /plans/{id}/tasks/{tid} updates task status."""
        plan = _create_plan(client, auth_headers, "Update task plan")
        r = client.post(
            f"/api/v1/plans/{plan['id']}/tasks",
            json={"title": "Step 1", "step_number": 1},
            headers=auth_headers,
        )
        task = r.json()["data"]
        tid = task["id"]
        r2 = client.put(
            f"/api/v1/plans/{plan['id']}/tasks/{tid}",
            json={"status": "complete", "result": "Finished successfully."},
            headers=auth_headers,
        )
        assert r2.status_code == 200
        updated = r2.json()["data"]
        assert updated["status"] == "complete"
        assert updated["result"] == "Finished successfully."

    def test_add_task_missing_plan_404(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Adding task to missing plan returns 404."""
        r = client.post(
            "/api/v1/plans/missing/tasks",
            json={"title": "x", "step_number": 1},
            headers=auth_headers,
        )
        assert r.status_code == 404

    def test_update_task_missing_task_404(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Updating non-existent task returns 404."""
        plan = _create_plan(client, auth_headers)
        r = client.put(
            f"/api/v1/plans/{plan['id']}/tasks/no-such-task",
            json={"status": "complete"},
            headers=auth_headers,
        )
        assert r.status_code == 404

    def test_task_step_number_ordering(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Tasks are returned ordered by stepNumber."""
        plan = _create_plan(client, auth_headers, "Ordered plan")
        for step_num in [3, 1, 2]:
            client.post(
                f"/api/v1/plans/{plan['id']}/tasks",
                json={"title": f"Step {step_num}", "step_number": step_num},
                headers=auth_headers,
            )
        r = client.get(f"/api/v1/plans/{plan['id']}/tasks", headers=auth_headers)
        tasks = r.json()["data"]
        nums = [t["stepNumber"] for t in tasks]
        assert nums == sorted(nums)


# ── Audit instrumentation ─────────────────────────────────────────────────────


class TestPlanAuditInstrumentation:
    """Verify that mutating plan operations emit audit events."""

    def test_create_emits_audit(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Creating a plan records a plan.created audit event."""
        before_count = len(audit_list(action="plan.created"))
        _create_plan(client, auth_headers, "Audit create test")
        after_count = len(audit_list(action="plan.created"))
        assert after_count > before_count

    def test_approve_emits_audit(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Approving a plan records a plan.approved audit event."""
        plan = _create_plan(client, auth_headers, "Audit approve test")
        before_count = len(audit_list(action="plan.approved"))
        client.post(f"/api/v1/plans/{plan['id']}/approve", headers=auth_headers)
        after_count = len(audit_list(action="plan.approved"))
        assert after_count > before_count

    def test_delete_emits_audit(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Deleting a plan records a plan.deleted audit event."""
        plan = _create_plan(client, auth_headers, "Audit delete test")
        before_count = len(audit_list(action="plan.deleted"))
        client.delete(f"/api/v1/plans/{plan['id']}", headers=auth_headers)
        after_count = len(audit_list(action="plan.deleted"))
        assert after_count > before_count
