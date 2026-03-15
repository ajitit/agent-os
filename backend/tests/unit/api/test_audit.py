"""
Unit and integration tests for the Audit Log API.

Coverage targets:
- GET /audit — list with all filter combinations
- GET /audit/stats — returns correct aggregate structure
- GET /audit/export — returns valid CSV
- GET /audit/{id} — single event detail and 404
- Immutability: audit log only grows, never shrinks
- JWT enforcement
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.stores import audit_log, user_create
from backend.app.main import app
from backend.core.security import create_access_token, hash_password

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def client() -> TestClient:
    """Return a TestClient for the main FastAPI application."""
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    """Return valid Bearer headers for an admin user.

    Returns:
        Auth header dict.
    """
    user = user_create({
        "email": "audit-test@vishwakarma.test",
        "hashed_password": hash_password("testpassword123"),
        "full_name": "Audit Tester",
        "role": "admin",
    })
    token = create_access_token({"sub": user["id"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def seed_events() -> None:
    """Seed a known set of audit events before each test."""
    audit_log({
        "actorType": "human",
        "actorId": "user-001",
        "actorName": "Alice",
        "action": "agent.created",
        "resourceType": "agent",
        "resourceId": "agent-001",
        "resourceName": "Research Agent",
        "outcome": "success",
        "durationMs": 42,
    })
    audit_log({
        "actorType": "agent",
        "actorId": "agent-001",
        "actorName": "Research Agent",
        "action": "agent.executed",
        "resourceType": "run",
        "resourceId": "run-001",
        "outcome": "success",
        "durationMs": 350,
    })
    audit_log({
        "actorType": "system",
        "actorId": "engine",
        "action": "run.completed",
        "resourceType": "run",
        "resourceId": "run-001",
        "outcome": "success",
        "durationMs": 1200,
    })
    audit_log({
        "actorType": "human",
        "actorId": "user-002",
        "actorName": "Bob",
        "action": "plan.rejected",
        "resourceType": "plan",
        "resourceId": "plan-001",
        "outcome": "success",
        "durationMs": 10,
    })


# ── List endpoint ─────────────────────────────────────────────────────────────


class TestAuditList:
    """Tests for GET /audit."""

    def test_list_returns_envelope(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit returns APIResponse envelope."""
        r = client.get("/api/v1/audit", headers=auth_headers)
        assert r.status_code == 200
        body = r.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_list_sorted_newest_first(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit returns events newest-first."""
        r = client.get("/api/v1/audit", headers=auth_headers)
        events = r.json()["data"]
        if len(events) >= 2:
            ts = [e["timestamp"] for e in events]
            assert ts == sorted(ts, reverse=True)

    def test_filter_by_actor_type_human(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit?actor_type=human returns only human events."""
        r = client.get("/api/v1/audit?actor_type=human", headers=auth_headers)
        events = r.json()["data"]
        assert len(events) >= 1
        assert all(e["actorType"] == "human" for e in events)

    def test_filter_by_actor_type_agent(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit?actor_type=agent returns only agent events."""
        r = client.get("/api/v1/audit?actor_type=agent", headers=auth_headers)
        events = r.json()["data"]
        assert all(e["actorType"] == "agent" for e in events)

    def test_filter_by_resource_type(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit?resource_type=plan returns only plan events."""
        r = client.get("/api/v1/audit?resource_type=plan", headers=auth_headers)
        events = r.json()["data"]
        assert len(events) >= 1
        assert all(e.get("resourceType") == "plan" for e in events)

    def test_filter_by_action(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit?action=run.completed returns matching events."""
        r = client.get("/api/v1/audit?action=run.completed", headers=auth_headers)
        events = r.json()["data"]
        assert len(events) >= 1
        assert all(e["action"] == "run.completed" for e in events)

    def test_limit_parameter(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit?limit=2 returns at most 2 events."""
        r = client.get("/api/v1/audit?limit=2", headers=auth_headers)
        assert r.status_code == 200
        events = r.json()["data"]
        assert len(events) <= 2

    def test_offset_parameter(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit?offset=N skips N events."""
        r_all = client.get("/api/v1/audit?limit=100", headers=auth_headers)
        total = len(r_all.json()["data"])
        if total >= 2:
            r_offset = client.get("/api/v1/audit?offset=1&limit=100", headers=auth_headers)
            assert len(r_offset.json()["data"]) == total - 1

    def test_requires_auth(self, client: TestClient) -> None:
        """GET /audit requires Bearer JWT."""
        assert client.get("/api/v1/audit").status_code == 401


# ── Stats endpoint ────────────────────────────────────────────────────────────


class TestAuditStats:
    """Tests for GET /audit/stats."""

    def test_stats_shape(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit/stats returns expected keys."""
        r = client.get("/api/v1/audit/stats", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()["data"]
        assert "total" in data
        assert "by_actor_type" in data
        assert "by_outcome" in data
        assert "daily_counts" in data

    def test_stats_total_gte_seeded(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """Total count must be >= 4 seeded events."""
        r = client.get("/api/v1/audit/stats", headers=auth_headers)
        stats = r.json()["data"]
        assert stats["total"] >= 4

    def test_stats_actor_types_present(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """by_actor_type must include human, agent, system."""
        r = client.get("/api/v1/audit/stats", headers=auth_headers)
        by_type = r.json()["data"]["by_actor_type"]
        assert "human" in by_type
        assert "agent" in by_type
        assert "system" in by_type

    def test_stats_requires_auth(self, client: TestClient) -> None:
        """GET /audit/stats requires Bearer JWT."""
        assert client.get("/api/v1/audit/stats").status_code == 401


# ── Single event ──────────────────────────────────────────────────────────────


class TestAuditSingleEvent:
    """Tests for GET /audit/{audit_id}."""

    def test_get_existing_event(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit/{id} returns the event when it exists."""
        r = client.get("/api/v1/audit?limit=1", headers=auth_headers)
        events = r.json()["data"]
        assert len(events) >= 1
        event_id = events[0]["id"]

        r2 = client.get(f"/api/v1/audit/{event_id}", headers=auth_headers)
        assert r2.status_code == 200
        assert r2.json()["data"]["id"] == event_id

    def test_get_missing_event_404(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit/{id} returns 404 for unknown id."""
        r = client.get("/api/v1/audit/no-such-id", headers=auth_headers)
        assert r.status_code == 404


# ── CSV export ────────────────────────────────────────────────────────────────


class TestAuditExport:
    """Tests for GET /audit/export."""

    def test_export_returns_csv_content_type(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """GET /audit/export returns text/csv."""
        r = client.get("/api/v1/audit/export", headers=auth_headers)
        assert r.status_code == 200
        assert "text/csv" in r.headers.get("content-type", "")

    def test_export_has_header_row(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """CSV export contains expected column headers."""
        r = client.get("/api/v1/audit/export", headers=auth_headers)
        first_line = r.text.splitlines()[0]
        assert "timestamp" in first_line
        assert "actorType" in first_line
        assert "action" in first_line
        assert "outcome" in first_line

    def test_export_data_rows_present(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """CSV export has at least 4 data rows (seeded)."""
        r = client.get("/api/v1/audit/export", headers=auth_headers)
        lines = [ln for ln in r.text.splitlines() if ln.strip()]
        # 1 header + N data rows
        assert len(lines) >= 5  # header + 4 seeded events

    def test_export_filtered(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """CSV export respects actor_type filter."""
        r = client.get("/api/v1/audit/export?actor_type=human", headers=auth_headers)
        lines = r.text.splitlines()
        assert len(lines) >= 2  # header + >=1 human row
        # All data rows should contain 'human' in actorType column
        header = lines[0].split(",")
        at_idx = header.index("actorType") if "actorType" in header else None
        if at_idx is not None:
            for row in lines[1:]:
                cols = row.split(",")
                if len(cols) > at_idx:
                    assert cols[at_idx] == "human"

    def test_export_requires_auth(self, client: TestClient) -> None:
        """GET /audit/export requires Bearer JWT."""
        assert client.get("/api/v1/audit/export").status_code == 401


# ── Immutability ──────────────────────────────────────────────────────────────


class TestAuditImmutability:
    """Verify the audit store is append-only."""

    def test_audit_log_only_grows(self) -> None:
        """Calling audit_log() always increases total event count."""
        from backend.api.stores import audit_list as _list

        before = len(_list())
        audit_log({
            "actorType": "system",
            "actorId": "test",
            "action": "test.event",
            "resourceType": "test",
            "resourceId": "x",
            "outcome": "success",
        })
        after = len(_list())
        assert after == before + 1

    def test_no_delete_endpoint_exists(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        """There is no DELETE endpoint on /audit — audit is immutable."""
        r = client.delete("/api/v1/audit/some-id", headers=auth_headers)
        assert r.status_code == 405  # method not allowed
