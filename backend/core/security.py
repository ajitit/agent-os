"""
<<<<<<< HEAD
File: security.py

Purpose:
Implements security dependencies for FastAPI endpoints, specifically Bearer JWT validation,
password hashing, and RBAC role checks.

Key Functionalities:
- `get_current_user` dependency for enforcing authenticated access.
- `check_role` dependency for RBAC.
- JWT encoding and decoding.
- Password hashing and verification via passlib.
"""

import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from backend.core.config import get_settings
from backend.api.stores import user_get

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new JWT access token."""
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> dict[str, Any]:
    """
    Validate the Bearer token and return user information.
=======
Module: core/security.py

Implements security dependencies for FastAPI endpoints: Bearer JWT validation,
password hashing via passlib/bcrypt, and RBAC role checks.

All public functions have Google-style docstrings and full type annotations
to satisfy mypy --strict.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from backend.api.stores import user_get
from backend.core.config import get_settings

pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
security: HTTPBearer = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a plain-text password with bcrypt.

    Args:
        password: Plain-text password string.

    Returns:
        Bcrypt hash string.
    """
    result: str = pwd_context.hash(password)
    return result


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored bcrypt hash.

    Args:
        plain_password: User-supplied plain-text password.
        hashed_password: Stored bcrypt hash.

    Returns:
        True if passwords match, False otherwise.
    """
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        data: Claims to encode (must include ``sub``).
        expires_delta: Optional custom TTL; defaults to 15 minutes.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=15))
    to_encode["exp"] = expire
    token: str = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return token


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, Any]:
    """Validate the Bearer token and return the authenticated user.

    Args:
        credentials: HTTP Bearer credentials extracted by FastAPI.

    Returns:
        User dict from the user store.

    Raises:
        HTTPException: 401 if the token is missing, invalid, or expired.
        HTTPException: 404 if the user referenced by the token does not exist.
>>>>>>> c952205 (Initial upload of AgentOS code)
    """
    settings = get_settings()
    token = credentials.credentials
    try:
<<<<<<< HEAD
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
=======
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
>>>>>>> c952205 (Initial upload of AgentOS code)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
<<<<<<< HEAD
    except jwt.PyJWTError:
=======
    except jwt.PyJWTError as exc:
>>>>>>> c952205 (Initial upload of AgentOS code)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
<<<<<<< HEAD
        )
    
    user = user_get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def check_role(allowed_roles: list[str]):
    """Returns a dependency that checks if the user has one of the allowed roles."""
    async def role_checker(user: Annotated[dict, Depends(get_current_user)]):
=======
        ) from exc

    user = user_get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


def check_role(allowed_roles: list[str]) -> Callable[..., Any]:
    """Return a FastAPI dependency that enforces RBAC role membership.

    Args:
        allowed_roles: List of role strings that are permitted to proceed.

    Returns:
        An async dependency function that raises 403 for disallowed roles.
    """

    async def role_checker(
        user: Annotated[dict[str, Any], Depends(get_current_user)],
    ) -> dict[str, Any]:
        """Check that the authenticated user's role is in the allowed set.

        Args:
            user: Authenticated user dict from ``get_current_user``.

        Returns:
            The user dict if the role check passes.

        Raises:
            HTTPException: 403 if the user's role is not in ``allowed_roles``.
        """
>>>>>>> c952205 (Initial upload of AgentOS code)
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return user
<<<<<<< HEAD
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
    return role_checker
