"""
Unit tests for the supervisor planning layer.

Coverage targets:
- PlanStep dataclass construction and immutability
- PlanDecomposition structure
- RuleBasedPlanner.decompose() — domain detection, step count, step ordering
- RuleBasedPlanner._pick_agent() — picks matching agent, falls back to first
- LLMPlanner falls back to RuleBasedPlanner on error
- PlannerService.from_settings() returns correct adapter type
- PlannerService.plan() returns PlanDecomposition with >= 1 step
"""

from __future__ import annotations

import pytest

from backend.core.planning.planner import (
    LLMPlanner,
    PlanDecomposition,
    PlannerService,
    PlanStep,
    RuleBasedPlanner,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

AGENTS_FIXTURE: list[dict] = [
    {"id": "a1", "name": "Research Agent", "role": "research", "status": "active"},
    {"id": "a2", "name": "Coding Agent", "role": "coding", "status": "active"},
    {"id": "a3", "name": "Summary Agent", "role": "summary", "status": "active"},
]


# ── PlanStep ──────────────────────────────────────────────────────────────────


class TestPlanStep:
    """Tests for PlanStep value object."""

    def test_creation_defaults(self) -> None:
        """PlanStep has sensible defaults for optional fields."""
        step = PlanStep(step_number=1, title="Research", description="Find info")
        assert step.assigned_type == "agent"
        assert step.assigned_id is None
        assert step.depends_on == []

    def test_creation_full(self) -> None:
        """PlanStep stores all provided fields."""
        step = PlanStep(
            step_number=2,
            title="Analyse",
            description="Analyse data",
            assigned_type="crew",
            assigned_id="crew-001",
            depends_on=[1],
        )
        assert step.step_number == 2
        assert step.assigned_type == "crew"
        assert step.assigned_id == "crew-001"
        assert step.depends_on == [1]

    def test_immutable(self) -> None:
        """PlanStep is frozen (immutable after creation)."""
        import dataclasses
        step = PlanStep(step_number=1, title="x", description="y")
        with pytest.raises(dataclasses.FrozenInstanceError):
            step.title = "z"  # type: ignore[misc]


# ── PlanDecomposition ─────────────────────────────────────────────────────────


class TestPlanDecomposition:
    """Tests for PlanDecomposition data class."""

    def test_stores_steps(self) -> None:
        """PlanDecomposition stores steps list."""
        steps = [PlanStep(step_number=1, title="Step 1", description="")]
        decomp = PlanDecomposition(goal="Do X", reasoning="Because Y", steps=steps)
        assert len(decomp.steps) == 1
        assert decomp.goal == "Do X"

    def test_default_duration(self) -> None:
        """Default estimated duration is 5 minutes."""
        decomp = PlanDecomposition(goal="g", reasoning="r", steps=[])
        assert decomp.estimated_duration_minutes == 5


# ── RuleBasedPlanner ──────────────────────────────────────────────────────────


class TestRuleBasedPlanner:
    """Tests for RuleBasedPlanner."""

    @pytest.mark.asyncio
    async def test_produces_steps(self) -> None:
        """decompose() always produces at least 2 steps."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Research the quarterly report", AGENTS_FIXTURE)
        assert isinstance(result, PlanDecomposition)
        assert len(result.steps) >= 2

    @pytest.mark.asyncio
    async def test_steps_have_sequential_numbers(self) -> None:
        """Steps are numbered starting from 1 without gaps."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Write and review a blog post", AGENTS_FIXTURE)
        numbers = [s.step_number for s in result.steps]
        assert numbers == list(range(1, len(numbers) + 1))

    @pytest.mark.asyncio
    async def test_all_steps_have_titles(self) -> None:
        """Every step has a non-empty title."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Analyse sales data and generate report", AGENTS_FIXTURE)
        for step in result.steps:
            assert step.title.strip() != ""

    @pytest.mark.asyncio
    async def test_all_steps_have_descriptions(self) -> None:
        """Every step has a non-empty description."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Deploy the new API", AGENTS_FIXTURE)
        for step in result.steps:
            assert step.description.strip() != ""

    @pytest.mark.asyncio
    async def test_reasoning_not_empty(self) -> None:
        """Reasoning string is non-empty."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Summarise the document", AGENTS_FIXTURE)
        assert result.reasoning.strip() != ""

    @pytest.mark.asyncio
    async def test_duration_positive(self) -> None:
        """Estimated duration is a positive integer."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Do something", AGENTS_FIXTURE)
        assert result.estimated_duration_minutes > 0

    @pytest.mark.asyncio
    async def test_no_agents_still_produces_steps(self) -> None:
        """decompose() works even when no agents are available."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Research topic", [])
        assert len(result.steps) >= 2
        for step in result.steps:
            assert step.assigned_id is None

    @pytest.mark.asyncio
    async def test_research_keyword_detected(self) -> None:
        """Goal containing 'research' triggers a research domain step."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Research the latest AI papers", AGENTS_FIXTURE)
        titles_lower = [s.title.lower() for s in result.steps]
        assert any("research" in t or "gather" in t for t in titles_lower)

    @pytest.mark.asyncio
    async def test_write_keyword_triggers_generation(self) -> None:
        """Goal containing 'write' triggers a generation domain step."""
        planner = RuleBasedPlanner()
        result = await planner.decompose("Write a technical specification", AGENTS_FIXTURE)
        titles_lower = [s.title.lower() for s in result.steps]
        assert any("generat" in t or "write" in t or "output" in t for t in titles_lower)

    def test_pick_agent_matching_role(self) -> None:
        """_pick_agent returns agent whose role matches the domain."""
        agent_id = RuleBasedPlanner._pick_agent(AGENTS_FIXTURE, "research")
        assert agent_id == "a1"

    def test_pick_agent_fallback_to_first(self) -> None:
        """_pick_agent falls back to first agent when no role matches."""
        agent_id = RuleBasedPlanner._pick_agent(AGENTS_FIXTURE, "unknown_domain")
        assert agent_id == "a1"

    def test_pick_agent_empty_list(self) -> None:
        """_pick_agent returns None when agent list is empty."""
        agent_id = RuleBasedPlanner._pick_agent([], "research")
        assert agent_id is None


# ── LLMPlanner ────────────────────────────────────────────────────────────────


class TestLLMPlanner:
    """Tests for LLMPlanner — uses fallback path (no real API key in tests)."""

    @pytest.mark.asyncio
    async def test_falls_back_on_invalid_key(self) -> None:
        """LLMPlanner falls back to RuleBasedPlanner when API key is invalid."""
        planner = LLMPlanner(api_key="sk-invalid-key-for-testing")
        result = await planner.decompose("Analyse the data", AGENTS_FIXTURE)
        assert isinstance(result, PlanDecomposition)
        assert len(result.steps) >= 2

    @pytest.mark.asyncio
    async def test_fallback_produces_valid_steps(self) -> None:
        """Fallback result has valid step structure."""
        planner = LLMPlanner(api_key="invalid")
        result = await planner.decompose("Deploy to production", AGENTS_FIXTURE)
        for step in result.steps:
            assert step.step_number >= 1
            assert step.title != ""


# ── PlannerService ────────────────────────────────────────────────────────────


class TestPlannerService:
    """Tests for PlannerService factory and public interface."""

    def test_from_settings_no_key_uses_rule_based(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PlannerService.from_settings() uses RuleBasedPlanner when no API key."""
        from unittest.mock import MagicMock
        mock_settings = MagicMock()
        mock_settings.openai_api_key = None
        monkeypatch.setattr(
            "backend.core.planning.planner.get_settings", lambda: mock_settings
        )
        service = PlannerService.from_settings()
        assert isinstance(service._adapter, RuleBasedPlanner)

    def test_from_settings_with_key_uses_llm(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """PlannerService.from_settings() uses LLMPlanner when API key present."""
        from unittest.mock import MagicMock
        mock_settings = MagicMock()
        mock_settings.openai_api_key = "sk-fake-key-for-test"
        monkeypatch.setattr(
            "backend.core.planning.planner.get_settings", lambda: mock_settings
        )
        service = PlannerService.from_settings()
        assert isinstance(service._adapter, LLMPlanner)

    @pytest.mark.asyncio
    async def test_plan_returns_decomposition(self) -> None:
        """PlannerService.plan() returns a PlanDecomposition."""
        service = PlannerService(adapter=RuleBasedPlanner())
        result = await service.plan("Summarise the quarterly report", AGENTS_FIXTURE)
        assert isinstance(result, PlanDecomposition)
        assert len(result.steps) >= 2

    @pytest.mark.asyncio
    async def test_plan_with_empty_goal(self) -> None:
        """PlannerService.plan() handles an empty goal string."""
        service = PlannerService(adapter=RuleBasedPlanner())
        result = await service.plan("", AGENTS_FIXTURE)
        assert len(result.steps) >= 2

    @pytest.mark.asyncio
    async def test_plan_goal_preserved(self) -> None:
        """PlanDecomposition preserves the original goal."""
        service = PlannerService(adapter=RuleBasedPlanner())
        goal = "Write a detailed technical spec"
        result = await service.plan(goal, AGENTS_FIXTURE)
        assert result.goal == goal
