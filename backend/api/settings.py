"""Global settings API - model selection, etc."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/settings", tags=["Settings"])

# In-memory global settings (use DB in production)
_global_settings: dict = {
    "primary_model": "gpt-4",
    "available_models": [
        {"id": "gpt-4", "name": "GPT-4", "provider": "OpenAI"},
        {"id": "gpt-4o", "name": "GPT-4o", "provider": "OpenAI"},
        {"id": "claude-3-5-sonnet", "name": "Claude 3.5 Sonnet", "provider": "Anthropic"},
        {"id": "claude-3-opus", "name": "Claude 3 Opus", "provider": "Anthropic"},
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "provider": "Google"},
    ],
}


class ModelSettingsUpdate(BaseModel):
    """Update primary orchestration LLM."""

    primary_model: str = Field(..., min_length=1, description="Model ID e.g. gpt-4, claude-3-5-sonnet")


@router.get("/models")
def get_model_settings():
    """Get available models and current primary model."""
    return _global_settings


@router.put("/models")
def update_primary_model(payload: ModelSettingsUpdate):
    """Set primary orchestration LLM for the system."""
    _global_settings["primary_model"] = payload.primary_model
    return _global_settings
