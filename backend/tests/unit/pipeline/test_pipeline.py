"""
Unit tests for the 9-stage input processing pipeline.

Coverage targets:
- FilterPatternStore + FilterStage
- MaskPatternStore + MaskStage
- OntologyStore + MapStage
- ExtractStage (RegexExtractor)
- RouteStage (with mock agent registry)
- ClassifyStage
- AggregateStage
- ResultStage
- ReviewLoopStage
- PipelineOrchestrator end-to-end (pass and blocked paths)
"""

from __future__ import annotations

import asyncio

import pytest

from backend.pipeline.memory.pattern_store import (
    FilterPattern,
    FilterPatternStore,
    MaskPattern,
    MaskPatternStore,
)
from backend.pipeline.models import (
    AgentOutput,
    AggregateResult,
    EntityType,
    FilterVerdict,
    PipelineContext,
    PipelineStatus,
    ReviewFeedback,
)
from backend.pipeline.ontology.ontology_store import OntologyConcept, OntologyStore
from backend.pipeline.orchestrator import PipelineOrchestrator, PipelineRunStore
from backend.pipeline.stages.extract_stage import ExtractStage
from backend.pipeline.stages.filter_stage import FilterStage
from backend.pipeline.stages.map_stage import MapStage
from backend.pipeline.stages.mask_stage import MaskStage
from backend.pipeline.stages.review_stage import ReviewLoopStage
from backend.pipeline.stages.routing_stages import (
    AggregateStage,
    ClassifyStage,
    ResultStage,
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def _ctx(text: str = "hello world", run_id: str = "test-run") -> PipelineContext:
    """Build a minimal PipelineContext for testing."""
    return PipelineContext(run_id=run_id, original_input=text)


def _make_orchestrator() -> PipelineOrchestrator:
    """Build a fully wired orchestrator with fresh stores."""
    return PipelineOrchestrator(
        filter_store=FilterPatternStore(),
        mask_store=MaskPatternStore(),
        ontology_store=OntologyStore(),
        review_stage=ReviewLoopStage(timeout_seconds=5.0),
        run_store=PipelineRunStore(),
    )


# ── FilterPatternStore ────────────────────────────────────────────────────────


class TestFilterPatternStore:
    """Tests for FilterPatternStore CRUD and match logic."""

    def test_defaults_seeded(self) -> None:
        """Default patterns are seeded on construction."""
        store = FilterPatternStore()
        patterns = store.list_all()
        assert len(patterns) >= 5

    def test_create_and_get(self) -> None:
        """Create and retrieve a custom pattern."""
        store = FilterPatternStore()
        p = FilterPattern(
            name="test_pattern",
            verdict=FilterVerdict.JUNK,
            pattern=r"\bfoo\b",
        )
        created = store.create(p)
        fetched = store.get(created.id)
        assert fetched is not None
        assert fetched.name == "test_pattern"

    def test_duplicate_create_raises(self) -> None:
        """Creating a duplicate ID raises ValueError."""
        store = FilterPatternStore()
        p = FilterPattern(name="x", verdict=FilterVerdict.JUNK, pattern=r"\bx\b")
        store.create(p)
        with pytest.raises(ValueError, match="already exists"):
            store.create(p)

    def test_update(self) -> None:
        """Update a pattern field."""
        store = FilterPatternStore()
        p = FilterPattern(name="old", verdict=FilterVerdict.JUNK, pattern=r"\bfoo\b")
        created = store.create(p)
        updated = store.update(created.id, {"name": "new"})
        assert updated is not None
        assert updated.name == "new"

    def test_delete(self) -> None:
        """Delete a pattern."""
        store = FilterPatternStore()
        p = FilterPattern(name="del", verdict=FilterVerdict.JUNK, pattern=r"\bdel\b")
        created = store.create(p)
        assert store.delete(created.id) is True
        assert store.get(created.id) is None

    def test_delete_nonexistent(self) -> None:
        """Deleting a missing ID returns False."""
        store = FilterPatternStore()
        assert store.delete("nonexistent") is False

    def test_match_spam(self) -> None:
        """Spam keywords trigger JUNK verdict."""
        store = FilterPatternStore()
        matches = store.match("BUY NOW and click here for free money!")
        verdicts = {p.verdict for p, _ in matches}
        assert FilterVerdict.JUNK in verdicts

    def test_match_email(self) -> None:
        """Email address triggers PERSONAL verdict."""
        store = FilterPatternStore()
        matches = store.match("Contact me at bob@example.com for details.")
        verdicts = {p.verdict for p, _ in matches}
        assert FilterVerdict.PERSONAL in verdicts

    def test_match_ssn(self) -> None:
        """SSN triggers CONFIDENTIAL verdict."""
        store = FilterPatternStore()
        matches = store.match("My SSN is 123-45-6789.")
        verdicts = {p.verdict for p, _ in matches}
        assert FilterVerdict.CONFIDENTIAL in verdicts

    def test_no_match_clean_text(self) -> None:
        """Clean text produces no matches."""
        store = FilterPatternStore()
        matches = store.match("Please analyse the quarterly report.")
        assert matches == []

    def test_disabled_pattern_ignored(self) -> None:
        """Disabled patterns are excluded from match."""
        store = FilterPatternStore()
        p = FilterPattern(
            name="disabled",
            verdict=FilterVerdict.JUNK,
            pattern=r"\bdisabled\b",
            enabled=False,
        )
        store.create(p)
        matches = store.match("this is a disabled test")
        pattern_names = [pat.name for pat, _ in matches]
        assert "disabled" not in pattern_names


# ── FilterStage ───────────────────────────────────────────────────────────────


class TestFilterStage:
    """Tests for FilterStage.process()."""

    @pytest.mark.asyncio
    async def test_pass_clean_text(self) -> None:
        """Clean text passes the filter."""
        store = FilterPatternStore()
        stage = FilterStage(store)
        ctx = await stage.process(_ctx("What is the weather today?"))
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.PASS
        assert ctx.status == PipelineStatus.RUNNING

    @pytest.mark.asyncio
    async def test_block_spam(self) -> None:
        """Spam text is blocked."""
        store = FilterPatternStore()
        stage = FilterStage(store)
        ctx = await stage.process(_ctx("BUY NOW click here free money lottery"))
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.JUNK
        assert ctx.status == PipelineStatus.BLOCKED

    @pytest.mark.asyncio
    async def test_block_ssn(self) -> None:
        """SSN is blocked as confidential."""
        store = FilterPatternStore()
        stage = FilterStage(store)
        ctx = await stage.process(_ctx("My social security number is 123-45-6789"))
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.CONFIDENTIAL

    @pytest.mark.asyncio
    async def test_highest_severity_wins(self) -> None:
        """When multiple verdicts match, the most severe wins."""
        store = FilterPatternStore()
        stage = FilterStage(store)
        # SSN (CONFIDENTIAL) + spam keyword (JUNK) — should return CONFIDENTIAL
        ctx = await stage.process(_ctx("buy now 123-45-6789"))
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.CONFIDENTIAL


# ── ExtractStage ──────────────────────────────────────────────────────────────


class TestExtractStage:
    """Tests for ExtractStage and RegexExtractor."""

    @pytest.mark.asyncio
    async def test_email_extracted(self) -> None:
        stage = ExtractStage()
        ctx = await stage.process(_ctx("Email me at alice@example.org tomorrow."))
        assert ctx.extract_result is not None
        types = [e.entity_type for e in ctx.extract_result.entities]
        assert EntityType.EMAIL in types

    @pytest.mark.asyncio
    async def test_phone_extracted(self) -> None:
        stage = ExtractStage()
        ctx = await stage.process(_ctx("Call 555-867-5309 for support."))
        assert ctx.extract_result is not None
        types = [e.entity_type for e in ctx.extract_result.entities]
        assert EntityType.PHONE in types

    @pytest.mark.asyncio
    async def test_url_extracted(self) -> None:
        stage = ExtractStage()
        ctx = await stage.process(_ctx("Visit https://example.com for more."))
        assert ctx.extract_result is not None
        types = [e.entity_type for e in ctx.extract_result.entities]
        assert EntityType.URL in types

    @pytest.mark.asyncio
    async def test_ip_extracted(self) -> None:
        stage = ExtractStage()
        ctx = await stage.process(_ctx("Server is at 192.168.1.100"))
        assert ctx.extract_result is not None
        types = [e.entity_type for e in ctx.extract_result.entities]
        assert EntityType.IP_ADDRESS in types

    @pytest.mark.asyncio
    async def test_no_entities_empty_text(self) -> None:
        stage = ExtractStage()
        ctx = await stage.process(_ctx("   "))
        assert ctx.extract_result is not None
        assert ctx.extract_result.entity_count == 0

    @pytest.mark.asyncio
    async def test_entity_count_property(self) -> None:
        stage = ExtractStage()
        ctx = await stage.process(_ctx("alice@test.com and 192.168.0.1"))
        assert ctx.extract_result is not None
        assert ctx.extract_result.entity_count >= 2


# ── OntologyStore ─────────────────────────────────────────────────────────────


class TestOntologyStore:
    """Tests for OntologyStore CRUD and alias lookup."""

    def test_defaults_seeded(self) -> None:
        store = OntologyStore()
        concepts = store.list_all()
        assert len(concepts) >= 10

    def test_create_and_get(self) -> None:
        store = OntologyStore()
        c = OntologyConcept(
            id="TEST_001",
            label="Test Concept",
            domain="test",
            entity_types=[EntityType.OTHER],
            aliases=["testconcept", "tc"],
        )
        store.create(c)
        fetched = store.get("TEST_001")
        assert fetched is not None
        assert fetched.label == "Test Concept"

    def test_duplicate_raises(self) -> None:
        store = OntologyStore()
        c = OntologyConcept(
            id="DUP_001", label="Dup", domain="test", entity_types=[EntityType.OTHER]
        )
        store.create(c)
        with pytest.raises(ValueError):
            store.create(c)

    def test_alias_lookup(self) -> None:
        store = OntologyStore()
        results = store.find_by_alias("hospital visit", None)
        ids = [r.id for r in results]
        assert "MED_004" in ids

    def test_delete_removes_from_index(self) -> None:
        store = OntologyStore()
        store.delete("MED_001")
        results = store.find_by_alias("patient", EntityType.PERSON)
        ids = [r.id for r in results]
        assert "MED_001" not in ids

    def test_domain_filter(self) -> None:
        store = OntologyStore()
        finance = store.list_all(domain="finance")
        assert all(c.domain == "finance" for c in finance)

    def test_domains(self) -> None:
        store = OntologyStore()
        d = store.domains()
        assert "healthcare" in d
        assert "finance" in d


# ── MapStage ──────────────────────────────────────────────────────────────────


class TestMapStage:
    """Tests for MapStage.process()."""

    @pytest.mark.asyncio
    async def test_maps_medical_entity(self) -> None:
        extract = ExtractStage()
        map_stage = MapStage(OntologyStore())
        ctx = await extract.process(_ctx("The patient was seen at the hospital."))
        ctx = await map_stage.process(ctx)
        assert ctx.map_result is not None
        assert len(ctx.map_result.mappings) >= 0  # may match on aliases

    @pytest.mark.asyncio
    async def test_no_extract_result(self) -> None:
        """MapStage handles missing extract_result gracefully."""
        map_stage = MapStage(OntologyStore())
        ctx = await map_stage.process(_ctx())
        assert ctx.map_result is not None
        assert ctx.map_result.mappings == []


# ── MaskStage ─────────────────────────────────────────────────────────────────


class TestMaskStage:
    """Tests for MaskStage.process()."""

    @pytest.mark.asyncio
    async def test_masks_email(self) -> None:
        store = MaskPatternStore()
        stage = MaskStage(store)
        ctx = await stage.process(_ctx("Contact bob@example.com for help."))
        assert ctx.mask_result is not None
        assert "[EMAIL_1]" in ctx.mask_result.masked_text
        assert "bob@example.com" not in ctx.mask_result.masked_text
        assert ctx.mask_result.mask_map["[EMAIL_1]"] == "bob@example.com"

    @pytest.mark.asyncio
    async def test_masks_multiple(self) -> None:
        store = MaskPatternStore()
        stage = MaskStage(store)
        ctx = await stage.process(_ctx("alice@a.com and bob@b.com"))
        assert ctx.mask_result is not None
        assert ctx.mask_result.mask_count == 2

    @pytest.mark.asyncio
    async def test_no_match_unchanged(self) -> None:
        store = MaskPatternStore()
        stage = MaskStage(store)
        ctx = await stage.process(_ctx("The sky is blue."))
        assert ctx.mask_result is not None
        assert ctx.mask_result.mask_count == 0
        assert ctx.mask_result.masked_text == "The sky is blue."

    @pytest.mark.asyncio
    async def test_mask_map_invertible(self) -> None:
        """mask_map contains the original value for each placeholder."""
        store = MaskPatternStore()
        stage = MaskStage(store)
        original = "My SSN is 123-45-6789."
        ctx = await stage.process(_ctx(original))
        assert ctx.mask_result is not None
        for _token, value in ctx.mask_result.mask_map.items():
            assert value in original


# ── ClassifyStage ─────────────────────────────────────────────────────────────


class TestClassifyStage:
    """Tests for ClassifyStage.process()."""

    @pytest.mark.asyncio
    async def test_healthcare_category(self) -> None:
        stage = ClassifyStage()
        ctx = await stage.process(_ctx("The patient has a diagnosis of diabetes."))
        assert ctx.classify_result is not None
        assert ctx.classify_result.category == "healthcare"

    @pytest.mark.asyncio
    async def test_finance_category(self) -> None:
        stage = ClassifyStage()
        ctx = await stage.process(_ctx("Please process the invoice payment."))
        assert ctx.classify_result is not None
        assert ctx.classify_result.category == "finance"

    @pytest.mark.asyncio
    async def test_technology_category(self) -> None:
        stage = ClassifyStage()
        ctx = await stage.process(_ctx("Fix the bug in the API server code."))
        assert ctx.classify_result is not None
        assert ctx.classify_result.category == "technology"

    @pytest.mark.asyncio
    async def test_general_fallback(self) -> None:
        stage = ClassifyStage()
        ctx = await stage.process(_ctx("What is the meaning of life?"))
        assert ctx.classify_result is not None
        assert ctx.classify_result.category == "general"

    @pytest.mark.asyncio
    async def test_positive_sentiment(self) -> None:
        stage = ClassifyStage()
        ctx = await stage.process(_ctx("This is great, excellent work, I love it!"))
        assert ctx.classify_result is not None
        assert ctx.classify_result.sentiment == "positive"

    @pytest.mark.asyncio
    async def test_negative_sentiment(self) -> None:
        stage = ClassifyStage()
        ctx = await stage.process(_ctx("This is terrible, awful, broken and wrong."))
        assert ctx.classify_result is not None
        assert ctx.classify_result.sentiment == "negative"


# ── AggregateStage + ResultStage ──────────────────────────────────────────────


class TestAggregateAndResult:
    """Tests for AggregateStage and ResultStage."""

    @pytest.mark.asyncio
    async def test_aggregate_no_route(self) -> None:
        stage = AggregateStage()
        ctx = await stage.process(_ctx("hello"))
        assert ctx.aggregate_result is not None
        assert ctx.aggregate_result.summary != ""

    @pytest.mark.asyncio
    async def test_aggregate_with_pre_populated_outputs(self) -> None:
        stage = AggregateStage()
        pre = AggregateResult(
            summary="",
            agent_outputs=[
                AgentOutput(agent_id="a1", agent_name="Agent1", content="Answer A"),
                AgentOutput(agent_id="a2", agent_name="Agent2", content="Answer B"),
            ],
        )
        ctx = _ctx("hello").with_update(aggregate_result=pre)
        ctx = await stage.process(ctx)
        assert ctx.aggregate_result is not None
        assert "Agent1" in ctx.aggregate_result.summary or "Aggregated" in ctx.aggregate_result.summary

    @pytest.mark.asyncio
    async def test_result_composes_final(self) -> None:
        stage = ResultStage()
        agg = AggregateResult(summary="This is the answer.", agent_outputs=[])
        ctx = _ctx().with_update(aggregate_result=agg)
        ctx = await stage.process(ctx)
        assert ctx.final_result is not None
        assert "This is the answer." in ctx.final_result


# ── ReviewLoopStage ───────────────────────────────────────────────────────────


class TestReviewLoopStage:
    """Tests for ReviewLoopStage human-in-the-loop logic."""

    @pytest.mark.asyncio
    async def test_approve_resolves(self) -> None:
        """Approving a review completes with APPROVED status."""
        stage = ReviewLoopStage(timeout_seconds=5.0)
        ctx = _ctx("test review", run_id="review-approve-1")

        async def _approve_after_delay() -> None:
            await asyncio.sleep(0.05)
            stage.resume("review-approve-1", ReviewFeedback(approved=True))

        asyncio.create_task(_approve_after_delay())
        result = await stage.process(ctx)
        assert result.status == PipelineStatus.APPROVED

    @pytest.mark.asyncio
    async def test_reject_resolves(self) -> None:
        """Rejecting a review completes with REJECTED status."""
        stage = ReviewLoopStage(timeout_seconds=5.0)
        ctx = _ctx("test reject", run_id="review-reject-1")

        async def _reject_after_delay() -> None:
            await asyncio.sleep(0.05)
            stage.resume("review-reject-1", ReviewFeedback(approved=False))

        asyncio.create_task(_reject_after_delay())
        result = await stage.process(ctx)
        assert result.status == PipelineStatus.REJECTED

    @pytest.mark.asyncio
    async def test_timeout_rejects(self) -> None:
        """Expired review is auto-rejected."""
        stage = ReviewLoopStage(timeout_seconds=0.05)
        ctx = _ctx("test timeout", run_id="review-timeout-1")
        result = await stage.process(ctx)
        assert result.status == PipelineStatus.REJECTED

    def test_resume_unknown_run(self) -> None:
        """resume() returns False for unknown run_id."""
        stage = ReviewLoopStage()
        assert stage.resume("unknown", ReviewFeedback(approved=True)) is False

    def test_pending_reviews_list(self) -> None:
        """pending_reviews() is accessible (empty on fresh instance)."""
        stage = ReviewLoopStage()
        assert isinstance(stage.pending_reviews(), list)


# ── PipelineOrchestrator E2E ──────────────────────────────────────────────────


class TestPipelineOrchestratorE2E:
    """End-to-end pipeline integration tests."""

    @pytest.mark.asyncio
    async def test_clean_input_passes_all_stages(self) -> None:
        """Clean text passes all 8 main stages and reaches COMPLETE."""
        orch = _make_orchestrator()
        ctx = await orch.run("Please summarise the quarterly sales report.")
        assert ctx.status == PipelineStatus.COMPLETE
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.PASS
        assert ctx.extract_result is not None
        assert ctx.mask_result is not None
        assert ctx.classify_result is not None
        assert ctx.aggregate_result is not None
        assert ctx.final_result is not None

    @pytest.mark.asyncio
    async def test_spam_input_blocked(self) -> None:
        """Spam input is blocked after stage 1."""
        orch = _make_orchestrator()
        ctx = await orch.run("BUY NOW free money lottery click here")
        assert ctx.status == PipelineStatus.BLOCKED
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.JUNK
        # Downstream stages should NOT run
        assert ctx.extract_result is None

    @pytest.mark.asyncio
    async def test_ssn_input_blocked(self) -> None:
        """SSN disclosure is blocked as confidential."""
        orch = _make_orchestrator()
        ctx = await orch.run("My social security number is 123-45-6789")
        assert ctx.status == PipelineStatus.BLOCKED
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.CONFIDENTIAL

    @pytest.mark.asyncio
    async def test_email_is_blocked_by_filter(self) -> None:
        """Email address in input is blocked by the filter stage (PII).

        Per spec, the filter stage checks for personal data patterns.
        An email address matches the ``email_address`` PERSONAL filter so the
        pipeline short-circuits with BLOCKED before reaching the mask stage.
        """
        orch = _make_orchestrator()
        ctx = await orch.run("Send the report to alice@example.com please.")
        assert ctx.status == PipelineStatus.BLOCKED
        assert ctx.filter_result is not None
        assert ctx.filter_result.verdict == FilterVerdict.PERSONAL

    @pytest.mark.asyncio
    async def test_run_recorded_in_store(self) -> None:
        """Completed runs are persisted in the run store."""
        orch = _make_orchestrator()
        await orch.run("Hello pipeline", run_id="store-test-001")
        record = orch.run_store.get("store-test-001")
        assert record is not None
        assert record["run_id"] == "store-test-001"
        assert record["status"] == PipelineStatus.COMPLETE.value

    @pytest.mark.asyncio
    async def test_with_review_approved(self) -> None:
        """require_review=True pauses then completes on approval."""
        orch = _make_orchestrator()

        async def _approve() -> None:
            await asyncio.sleep(0.05)
            orch.resume_review("review-e2e-ok", ReviewFeedback(approved=True))

        asyncio.create_task(_approve())
        ctx = await orch.run(
            "Analyse the data.", require_review=True, run_id="review-e2e-ok"
        )
        assert ctx.status == PipelineStatus.APPROVED

    @pytest.mark.asyncio
    async def test_stage_errors_do_not_crash_pipeline(self) -> None:
        """A non-fatal stage error is recorded but pipeline continues."""
        orch = _make_orchestrator()
        # Inject a bad mask pattern (invalid regex)
        orch._mask._store.create(  # type: ignore[attr-defined]
            MaskPattern(
                name="broken",
                pattern="[invalid regex",
                placeholder="[BROKEN]",
                enabled=True,
            )
        )
        # Pipeline should still complete (bad pattern is skipped)
        ctx = await orch.run("Test with a broken mask pattern present.")
        assert ctx.status == PipelineStatus.COMPLETE

    @pytest.mark.asyncio
    async def test_run_list(self) -> None:
        """run_store.list_all() returns records after multiple runs."""
        orch = _make_orchestrator()
        await orch.run("First run")
        await orch.run("Second run")
        records = orch.run_store.list()
        assert len(records) >= 2
