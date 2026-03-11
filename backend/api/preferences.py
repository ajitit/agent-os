"""
File: preferences.py

Purpose:
Defines the REST API endpoints for user preferences.
"""

from typing import Annotated
<<<<<<< HEAD
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.stores import preference_get, preference_update
<<<<<<< HEAD
from backend.core.security import get_current_user
from backend.core.schemas import APIResponse
=======
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user
>>>>>>> c952205 (Initial upload of AgentOS code)

router = APIRouter(prefix="/preferences", tags=["Preferences"])

class UserPreferencesUpdate(BaseModel):
    theme: str | None = Field(None, pattern="^(light|dark|system)$")
    accentColor: str | None = None
    fontSize: str | None = Field(None, pattern="^(sm|md|lg)$")
    defaultPriority: str | None = Field(None, pattern="^(low|normal|high|urgent)$")
    streamingEnabled: bool | None = None
    showAgentThinking: bool | None = None
    defaultSupervisorBehavior: str | None = Field(None, pattern="^(auto_route|confirm_routing|manual_select)$")
    emailOnFailure: bool | None = None
    emailDigestFrequency: str | None = Field(None, pattern="^(never|daily|weekly)$")

@router.get("", response_model=APIResponse[dict])
async def get_preferences(user: Annotated[dict, Depends(get_current_user)]):
    prefs = preference_get(user["id"]) or {}
    return APIResponse(data=prefs)

@router.put("", response_model=APIResponse[dict])
async def update_preferences(payload: UserPreferencesUpdate, user: Annotated[dict, Depends(get_current_user)]):
    data = payload.model_dump(exclude_none=True)
    prefs = preference_update(user["id"], data)
    return APIResponse(data=prefs)
