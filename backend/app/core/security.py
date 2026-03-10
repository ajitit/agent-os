"""
File: security.py

Purpose:
Implements security dependencies for FastAPI endpoints, specifically Bearer JWT validation.

Key Functionalities:
- `get_current_user` dependency for enforcing authenticated access.
- JWT decoding and validation.
"""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.config import get_settings

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict[str, Any]:
    """
    Validate the Bearer token and return user information.
    Currently a stub implementation that validates the presence of a token.
    """
    settings = get_settings()
    token = credentials.credentials
    
    # In a real implementation, we would decode the JWT here
    # For now, we enforce that a token is present
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Return a mock user for now
    return {"sub": "system", "role": "admin"}
