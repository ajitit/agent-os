"""
File: settings.py

Purpose:
Provides API endpoints to retrieve and update global system settings, such as
the primary orchestration LLM.

Key Functionalities:
- Get available models and current settings
- Update the primary model for the system

Inputs:
- HTTP requests to update settings Configuration

Outputs:
- JSON responses with global system settings

Interacting Files / Modules:
- None
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.stores import settings_get, settings_update
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings"])


class ModelSettingsUpdate(BaseModel):
    """Update primary orchestration LLM."""

    primary_model: str = Field(..., min_length=1, description="Model ID e.g. gpt-4, claude-3-5-sonnet")


@router.get("/models", response_model=APIResponse[dict])
async def get_model_settings(
    user: Annotated[dict, Depends(get_current_user)],
):
    """Get available models and current primary model."""
    return APIResponse(data=settings_get())


@router.put("/models", response_model=APIResponse[dict])
async def update_primary_model(
    payload: ModelSettingsUpdate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Set primary orchestration LLM for the system."""
    settings_update({"primary_model": payload.primary_model})
    return APIResponse(data=settings_get())
