"""
File: auth.py

Purpose:
Defines the REST API endpoints for user authentication.
"""

from typing import Annotated
<<<<<<< HEAD
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from backend.api.stores import user_create, user_get_by_email
<<<<<<< HEAD
from backend.core.security import hash_password, verify_password, create_access_token, get_current_user
from backend.core.schemas import APIResponse
=======
from backend.core.schemas import APIResponse
from backend.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
>>>>>>> c952205 (Initial upload of AgentOS code)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None
    role: str = Field(default="operator", pattern="^(admin|developer|operator|viewer)$")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "operator"

class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str
    createdAt: str

@router.post("/register", response_model=APIResponse[dict])
async def register(payload: UserRegister):
    if user_get_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user_data = payload.model_dump()
    user_data["hashed_password"] = hash_password(user_data.pop("password"))
    user = user_create(user_data)
    display_user = dict(user)
    display_user.pop("hashed_password", None)
    return APIResponse(data=display_user)

@router.post("/login", response_model=APIResponse[Token])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = user_get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.get("hashed_password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user["id"]})
    return APIResponse(data=Token(access_token=access_token, role=user.get("role", "operator")))

@router.get("/keys", response_model=APIResponse[list[APIKeyResponse]])
async def list_keys(user: Annotated[dict, Depends(get_current_user)]):
    from backend.api.stores import api_key_list
    keys = api_key_list(user["id"])
    return APIResponse(data=keys)

@router.post("/keys", response_model=APIResponse[APIKeyResponse])
async def create_key(payload: APIKeyCreate, user: Annotated[dict, Depends(get_current_user)]):
    from backend.api.stores import api_key_create
    key = api_key_create(user["id"], payload.name)
    return APIResponse(data=key)

@router.delete("/keys/{key_id}", response_model=APIResponse[dict])
async def delete_key(key_id: str, user: Annotated[dict, Depends(get_current_user)]):
    from backend.api.stores import api_key_delete, api_key_list
    # Verify ownership before delete
    user_keys = api_key_list(user["id"])
    if not any(k["id"] == key_id for k in user_keys):
        raise HTTPException(status_code=404, detail="API Key not found or access denied")
<<<<<<< HEAD
    
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
    success = api_key_delete(key_id)
    return APIResponse(data={"success": success})

@router.get("/me", response_model=APIResponse[dict])
async def get_me(user: Annotated[dict, Depends(get_current_user)]):
    display_user = dict(user)
    display_user.pop("hashed_password", None)
    return APIResponse(data=display_user)
