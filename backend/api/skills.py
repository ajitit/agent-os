"""
File: skills.py

Purpose:
Implements a Progressive Disclosure API for retrieving AI skills, organizing them
by detail level (metadata, instructions, resources) to optimize context length.

Key Functionalities:
- Level 1: List all available skills and metadata
- Level 2: Retrieve detailed specific skill instructions
- Level 3: Fetch related resource files for a skill

Inputs:
- HTTP GET requests
- Application settings (skills directory)

Outputs:
- JSON responses with skill lists and details
- Raw file content (resources) with appropriate media types

Interacting Files / Modules:
- backend.core.config
- backend.skills.loader
- backend.skills.models
- backend.core.exceptions
"""

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from backend.core.config import Settings, get_settings
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user
from backend.skills.loader import SkillLoader
from backend.skills.models import SkillListResponse

router = APIRouter(prefix="/skills", tags=["Skills"])


def get_skill_loader(settings: Settings = Depends(get_settings)) -> SkillLoader:
    """Dependency: resolve skills directory and return loader."""
    base = Path(settings.skills_dir)
    if not base.is_absolute():
        base = Path(__file__).resolve().parent.parent.parent / base
    return SkillLoader(base)


@router.get("", response_model=APIResponse[SkillListResponse])
async def list_skills(
    user: Annotated[dict, Depends(get_current_user)],
    loader: SkillLoader = Depends(get_skill_loader),
) -> APIResponse[SkillListResponse]:
    """
    Level 1: Get metadata for all skills (~100 tokens each).
    Use in system prompt so agent can decide which skill to use.
    """
    skills = loader.list_metadata()
    return APIResponse(data=SkillListResponse(skills=skills, total=len(skills)))


@router.get("/{skill_id}", response_model=APIResponse[dict])
async def get_skill(
    skill_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    loader: SkillLoader = Depends(get_skill_loader),
):
    """
    Level 2: Get full skill with instructions (SKILL.md).
    Load when agent chooses to use the skill.
    """
    skill = loader.get_skill(skill_id)
    if not skill:
        raise NotFoundError("Skill not found")
    return APIResponse(data=skill.model_dump())


@router.get("/{skill_id}/resources/{resource_path:path}")
async def get_resource(
    skill_id: str,
    resource_path: str,
    user: Annotated[dict, Depends(get_current_user)],
    loader: SkillLoader = Depends(get_skill_loader),
):
    """
    Level 3: Get a resource file.
    Load when instructions reference it.
    """
    result = loader.get_resource(skill_id, resource_path)
    if not result:
        raise NotFoundError("Resource not found")
    content, content_type = result
    return Response(content=content, media_type=content_type)
