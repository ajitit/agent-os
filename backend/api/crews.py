"""
File: crews.py

Purpose:
Provides REST API endpoints for managing multi-agent crews, which coordinate
multiple agents to execute complex tasks.

Key Functionalities:
- CRUD operations for agent crews

Inputs:
- HTTP requests with crew configuration data

Outputs:
- JSON responses containing crew metadata

Interacting Files / Modules:
- backend.api.stores
- backend.core.exceptions
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.api.stores import crew_create, crew_delete, crew_get, crew_list, crew_update
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

router = APIRouter(prefix="/crews", tags=["Crews"])


class CrewCreate(BaseModel):
    """Request to create a crew."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class CrewUpdate(BaseModel):
    """Request to update a crew."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


@router.get("", response_model=APIResponse[list])
async def get_all_crews(user: Annotated[dict, Depends(get_current_user)]):
    """Get all crews."""
    return APIResponse(data=crew_list())


@router.post("", response_model=APIResponse[dict], status_code=201)
async def create_crew(
    payload: CrewCreate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Create a new crew."""
    return APIResponse(data=crew_create(payload.model_dump(exclude_none=True)))


@router.get("/{crew_id}", response_model=APIResponse[dict])
async def get_crew(
    crew_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Get a specific crew."""
    crew = crew_get(crew_id)
    if not crew:
        raise NotFoundError("Crew not found")
    return APIResponse(data=crew)


@router.put("/{crew_id}", response_model=APIResponse[dict])
async def update_crew(
    crew_id: str,
    payload: CrewUpdate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Update a crew."""
    data = payload.model_dump(exclude_none=True)
    if not data:
        crew = crew_get(crew_id)
        if not crew:
            raise NotFoundError("Crew not found")
        return APIResponse(data=crew)
    crew = crew_update(crew_id, data)
    if not crew:
        raise NotFoundError("Crew not found")
    return APIResponse(data=crew)


@router.delete("/{crew_id}", status_code=204)
async def delete_crew(
    crew_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Delete a crew."""
    if not crew_delete(crew_id):
        raise NotFoundError("Crew not found")
