"""
Pipeline models — shared Pydantic types for the 9-stage input processing pipeline.

All stage inputs/outputs are represented as immutable value objects so that
the orchestrator can pass context forward without mutation side-effects.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# ── Enums ────────────────────────────────────────────────────────────────────


class FilterVerdict(enum.StrEnum):
    """Decision produced by the Filter stage."""

    PASS = "pass"
    JUNK = "junk"
    PERSONAL = "personal"
    CONFIDENTIAL = "confidential"
    BLOCKED = "blocked"


class EntityType(enum.StrEnum):
    """Canonical entity types recognised by the Extract stage."""

    PERSON = "PERSON"
    ORGANISATION = "ORGANISATION"
    LOCATION = "LOCATION"
    DATE = "DATE"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    URL = "URL"
    IP_ADDRESS = "IP_ADDRESS"
    CREDIT_CARD = "CREDIT_CARD"
    SSN = "SSN"
    MEDICAL = "MEDICAL"
    FINANCIAL = "FINANCIAL"
    OTHER = "OTHER"


class PipelineStatus(enum.StrEnum):
    """Overall pipeline run status."""

    PENDING = "pending"
    RUNNING = "running"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


# ── Stage-level value objects ─────────────────────────────────────────────────


class FilterResult(BaseModel):
    """Output of the Filter stage.

    Attributes:
        verdict: Classification decision.
        reason: Human-readable explanation.
        matched_patterns: Pattern IDs that triggered the decision.
    """

    verdict: FilterVerdict
    reason: str
    matched_patterns: list[str] = Field(default_factory=list)


class Entity(BaseModel):
    """A single extracted entity.

    Attributes:
        text: Raw surface form as it appears in the input.
        entity_type: Canonical type from EntityType enum.
        start: Byte offset in the original text.
        end: Byte offset (exclusive) in the original text.
        confidence: Extraction confidence 0–1.
        ontology_ids: IDs of matching ontology concepts.
    """

    text: str
    entity_type: EntityType
    start: int
    end: int
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    ontology_ids: list[str] = Field(default_factory=list)


class ExtractResult(BaseModel):
    """Output of the Extract stage.

    Attributes:
        entities: List of extracted Entity objects.
        entity_count: Convenience count.
    """

    entities: list[Entity] = Field(default_factory=list)

    @property
    def entity_count(self) -> int:
        """Total number of extracted entities."""
        return len(self.entities)


class OntologyMatch(BaseModel):
    """A single entity-to-ontology mapping.

    Attributes:
        entity_text: Surface form of the entity.
        entity_type: Type of the entity.
        ontology_id: Matched concept ID in the ontology store.
        ontology_label: Human-readable label.
        confidence: Match confidence 0–1.
    """

    entity_text: str
    entity_type: EntityType
    ontology_id: str
    ontology_label: str
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)


class MapResult(BaseModel):
    """Output of the Map stage.

    Attributes:
        mappings: List of entity → ontology concept mappings.
        unmapped_count: Number of entities with no ontology match.
    """

    mappings: list[OntologyMatch] = Field(default_factory=list)
    unmapped_count: int = 0


class MaskResult(BaseModel):
    """Output of the Mask stage.

    Attributes:
        masked_text: Input text with sensitive tokens replaced.
        mask_map: token_placeholder → original_value (for unmasking).
        mask_count: Number of replacements made.
    """

    masked_text: str
    mask_map: dict[str, str] = Field(default_factory=dict)
    mask_count: int = 0


class RouteDecision(BaseModel):
    """A single routing target produced by the Route stage.

    Attributes:
        agent_id: ID of the target agent or crew.
        agent_name: Display name.
        reason: Why this agent was selected.
        priority: Numeric priority (lower = higher priority).
    """

    agent_id: str
    agent_name: str
    reason: str
    priority: int = 0


class RouteResult(BaseModel):
    """Output of the Route stage.

    Attributes:
        targets: Ordered list of routing decisions.
        primary: The top-priority target.
    """

    targets: list[RouteDecision] = Field(default_factory=list)

    @property
    def primary(self) -> RouteDecision | None:
        """Highest-priority routing target."""
        return self.targets[0] if self.targets else None


class ClassifyResult(BaseModel):
    """Output of the Classify stage.

    Attributes:
        category: Top-level category label.
        subcategory: Optional fine-grained label.
        intent: Detected user intent.
        sentiment: Positive / neutral / negative.
        confidence: Classification confidence 0–1.
        tags: Additional free-form classification tags.
    """

    category: str
    subcategory: str | None = None
    intent: str
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    tags: list[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    """Result from a single agent invocation during aggregation.

    Attributes:
        agent_id: Originating agent ID.
        agent_name: Display name.
        content: Raw output text.
        metadata: Arbitrary agent-specific metadata.
    """

    agent_id: str
    agent_name: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AggregateResult(BaseModel):
    """Output of the Aggregate stage.

    Attributes:
        summary: Synthesised summary of all agent outputs.
        agent_outputs: Individual per-agent results.
        consensus: Whether all agents agreed.
    """

    summary: str
    agent_outputs: list[AgentOutput] = Field(default_factory=list)
    consensus: bool = True


# ── Human review ──────────────────────────────────────────────────────────────


class ReviewFeedback(BaseModel):
    """Human reviewer feedback submitted to the review loop.

    Attributes:
        approved: Whether the result is accepted.
        comment: Optional freeform feedback.
        modifications: Key-value corrections the reviewer applied.
        reviewer_id: ID of the reviewing user.
    """

    approved: bool
    comment: str | None = None
    modifications: dict[str, Any] = Field(default_factory=dict)
    reviewer_id: str = "anonymous"


# ── Top-level pipeline context ────────────────────────────────────────────────


class PipelineContext(BaseModel):
    """Immutable snapshot passed between pipeline stages.

    Every field is populated by the corresponding stage; downstream stages
    read from earlier fields but never mutate them — they return a new context.

    Attributes:
        run_id: Unique identifier for this pipeline run.
        user_id: Originating user.
        original_input: Raw unmodified user text.
        created_at: UTC timestamp of context creation.
        filter_result: Populated after Filter stage.
        extract_result: Populated after Extract stage.
        map_result: Populated after Map stage.
        mask_result: Populated after Mask stage.
        route_result: Populated after Route stage.
        classify_result: Populated after Classify stage.
        aggregate_result: Populated after Aggregate stage.
        final_result: Populated after Result stage.
        review_feedback: Populated after human review.
        status: Current pipeline status.
        stage_errors: Any non-fatal per-stage errors.
    """

    run_id: str
    user_id: str = "anonymous"
    original_input: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    filter_result: FilterResult | None = None
    extract_result: ExtractResult | None = None
    map_result: MapResult | None = None
    mask_result: MaskResult | None = None
    route_result: RouteResult | None = None
    classify_result: ClassifyResult | None = None
    aggregate_result: AggregateResult | None = None
    final_result: str | None = None
    review_feedback: ReviewFeedback | None = None
    status: PipelineStatus = PipelineStatus.PENDING
    stage_errors: dict[str, str] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    def with_update(self, **kwargs: Any) -> PipelineContext:
        """Return a copy of this context with updated fields.

        Args:
            **kwargs: Fields to update.

        Returns:
            New PipelineContext instance with the requested changes applied.
        """
        return self.model_copy(update=kwargs)
