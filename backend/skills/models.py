"""
File: models.py

Purpose:
Defines Pydantic models for the Progressive Disclosure skill system, ensuring
type safety and validation when loading or serving skills.

Key Functionalities:
- Define `SkillMetadata` for Level 1 concise representations
- Define `Skill` for complete Level 2 + 3 representations
- Define `SkillResource` to represent specific file resources
- Enforce validation, preventing path traversal attacks on resources

Inputs:
- Dictionaries or JSON objects containing parsed skill data

Outputs:
- Robust Pydantic model instances

Interacting Files / Modules:
- None
"""

<<<<<<< HEAD
from pathlib import Path
from typing import Any
=======
>>>>>>> c952205 (Initial upload of AgentOS code)

from pydantic import BaseModel, Field, field_validator


class SkillMetadata(BaseModel):
    """
    Level 1: ~100 tokens per skill.
    Loaded into system prompt so agent can decide which skill is relevant.
    """

    id: str = Field(..., description="Unique skill identifier (directory name)")
    name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Brief description for agent selection",
    )
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] = Field(default_factory=list, description="Optional tags for discovery")

    model_config = {"extra": "allow"}


class SkillResource(BaseModel):
    """Level 3: Resource file reference - loaded on-demand when instructions reference it."""

    path: str = Field(..., description="Relative path within skill's resources/")
    content_type: str = Field(default="text/plain", description="MIME type")
    size_bytes: int = Field(..., ge=0)

    @field_validator("path")
    @classmethod
    def path_no_traversal(cls, v: str) -> str:
        if ".." in v or v.startswith("/"):
            raise ValueError("Invalid resource path")
        return v


class Skill(BaseModel):
    """
    Level 2 + 3: Full skill with instructions and resource list.
    Instructions (SKILL.md) loaded on-demand when agent chooses the skill.
    Resources loaded on-demand when instructions reference them.
    """

    metadata: SkillMetadata
    instructions: str = Field(..., description="Full SKILL.md content")
    resource_paths: list[str] = Field(
        default_factory=list,
        description="Paths to resources/ files (Level 3 - load on demand)",
    )


class SkillListResponse(BaseModel):
    """Response for listing skills - metadata only (Level 1)."""

    skills: list[SkillMetadata]
    total: int
