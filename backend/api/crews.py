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

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.api.stores import crew_create, crew_delete, crew_get, crew_list, crew_update
from backend.core.exceptions import NotFoundError

router = APIRouter(prefix="/crews", tags=["Crews"])


class CrewCreate(BaseModel):
    """Request to create a crew."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None


class CrewUpdate(BaseModel):
    """Request to update a crew."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None


@router.get("")
def get_all_crews():
    """Get all crews."""
    return crew_list()


@router.post("")
def create_crew(payload: CrewCreate):
    """Create a new crew."""
    return crew_create(payload.model_dump(exclude_none=True))


@router.get("/{crew_id}")
def get_crew(crew_id: str):
    """Get a specific crew."""
    crew = crew_get(crew_id)
    if not crew:
        raise NotFoundError("Crew not found")
    return crew


@router.put("/{crew_id}")
def update_crew(crew_id: str, payload: CrewUpdate):
    """Update a crew."""
    data = payload.model_dump(exclude_none=True)
    if not data:
        return get_crew(crew_id)
    crew = crew_update(crew_id, data)
    if not crew:
        raise NotFoundError("Crew not found")
    return crew


@router.delete("/{crew_id}", status_code=204)
def delete_crew(crew_id: str):
    """Delete a crew."""
    if not crew_delete(crew_id):
        raise NotFoundError("Crew not found")
