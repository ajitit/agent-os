"""
File: auth.py

Purpose:
Defines the REST API endpoints for user authentication.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPPasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from backend.api.stores import user_create, user_get_by_email
from backend.core.security import hash_password, verify_password, create_access_token, get_current_user
from backend.core.schemas import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None
    role: str = Field(default="operator", pattern="^(admin|developer|operator|viewer)$")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

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
async def login(form_data: Annotated[HTTPPasswordRequestForm, Depends()]):
    user = user_get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.get("hashed_password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user["id"]})
    return APIResponse(data=Token(access_token=access_token))

@router.get("/me", response_model=APIResponse[dict])
async def get_me(user: Annotated[dict, Depends(get_current_user)]):
    display_user = dict(user)
    display_user.pop("hashed_password", None)
    return APIResponse(data=display_user)
