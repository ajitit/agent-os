"""
File: api/skill_registry.py

Skill Registry API — full CRUD for skills with group management and agent assignment.
Routes under /api/v1/registry/skills.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field

from backend.api.stores import (
    agent_skill_assign,
    agent_skill_list,
    agent_skill_remove,
    audit_log,
    skill_group_add_member,
    skill_group_create,
    skill_group_delete,
    skill_group_get,
    skill_group_list,
    skill_group_members,
    skill_group_remove_member,
    skill_group_update,
    skill_registry_create,
    skill_registry_delete,
    skill_registry_get,
    skill_registry_list,
    skill_registry_update,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import check_role, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry/skills", tags=["Skill Registry"])


class SkillIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=100)
    author: str = Field(default="", max_length=200)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] = Field(default_factory=list)
    status: str = Field(default="active", pattern="^(active|deprecated|draft)$")


class SkillUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    category: str | None = None
    author: str | None = None
    version: str | None = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    tags: list[str] | None = None
    status: str | None = Field(None, pattern="^(active|deprecated|draft)$")


class GroupIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=500)


class AssignIn(BaseModel):
    skill_id: str


class MemberIn(BaseModel):
    skill_id: str


@router.get("", response_model=APIResponse[list[dict[str, Any]]])
async def list_skills(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    category: str | None = Query(None),
) -> APIResponse[list[dict[str, Any]]]:
    return APIResponse(data=skill_registry_list(category=category))


@router.post("", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_skill(
    payload: SkillIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    skill = skill_registry_create(payload.model_dump())
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.skill.created",
               "resourceType": "skill", "resourceId": skill["id"], "resourceName": payload.name, "outcome": "success"})
    return APIResponse(data=skill)


@router.get("/groups", response_model=APIResponse[list[dict[str, Any]]])
async def list_groups(user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[dict[str, Any]]]:
    groups = skill_group_list()
    for g in groups:
        g["members"] = skill_group_members(g["id"])
    return APIResponse(data=groups)


@router.post("/groups", response_model=APIResponse[dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = skill_group_create(payload.model_dump())
    group["members"] = []
    return APIResponse(data=group)


@router.put("/groups/{group_id}", response_model=APIResponse[dict[str, Any]])
async def update_group(
    group_id: str,
    payload: GroupIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    group = skill_group_update(group_id, payload.model_dump(exclude_none=True))
    if not group:
        raise NotFoundError("Group not found")
    group["members"] = skill_group_members(group_id)
    return APIResponse(data=group)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(group_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not skill_group_delete(group_id):
        raise NotFoundError("Group not found")


@router.post("/groups/{group_id}/members", response_model=APIResponse[dict[str, Any]])
async def add_member(
    group_id: str,
    payload: MemberIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not skill_group_get(group_id):
        raise NotFoundError("Group not found")
    skill_group_add_member(group_id, payload.skill_id)
    return APIResponse(data={"group_id": group_id, "skill_id": payload.skill_id})


@router.delete("/groups/{group_id}/members/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(group_id: str, skill_id: str,
                        user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    skill_group_remove_member(group_id, skill_id)


@router.get("/agents/{agent_id}", response_model=APIResponse[list[str]])
async def get_agent_skills(agent_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[list[str]]:
    return APIResponse(data=agent_skill_list(agent_id))


@router.post("/agents/{agent_id}", response_model=APIResponse[dict[str, Any]])
async def assign_to_agent(
    agent_id: str,
    payload: AssignIn,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    agent_skill_assign(agent_id, payload.skill_id)
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.skill.assigned",
               "resourceType": "agent", "resourceId": agent_id, "outcome": "success"})
    return APIResponse(data={"agent_id": agent_id, "skill_id": payload.skill_id})


@router.delete("/agents/{agent_id}/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_agent(agent_id: str, skill_id: str,
                            user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))]) -> None:
    agent_skill_remove(agent_id, skill_id)


@router.get("/{skill_id}", response_model=APIResponse[dict[str, Any]])
async def get_skill(skill_id: str, user: Annotated[dict[str, Any], Depends(get_current_user)]) -> APIResponse[dict[str, Any]]:
    skill = skill_registry_get(skill_id)
    if not skill:
        raise NotFoundError("Skill not found")
    return APIResponse(data=skill)


@router.put("/{skill_id}", response_model=APIResponse[dict[str, Any]])
async def update_skill(
    skill_id: str,
    payload: SkillUpdate,
    user: Annotated[dict[str, Any], Depends(check_role(["admin", "developer"]))],
) -> APIResponse[dict[str, Any]]:
    if not skill_registry_get(skill_id):
        raise NotFoundError("Skill not found")
    updated = skill_registry_update(skill_id, payload.model_dump(exclude_none=True))
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.skill.updated",
               "resourceType": "skill", "resourceId": skill_id, "outcome": "success"})
    return APIResponse(data=updated)  # type: ignore[arg-type]


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str, user: Annotated[dict[str, Any], Depends(check_role(["admin"]))]) -> None:
    if not skill_registry_delete(skill_id):
        raise NotFoundError("Skill not found")
    audit_log({"actorType": "human", "actorId": user["id"], "action": "registry.skill.deleted",
               "resourceType": "skill", "resourceId": skill_id, "outcome": "success"})
