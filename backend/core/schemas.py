"""
File: schemas.py

Purpose:
Defines generic Pydantic models for standardizing API responses across the AgentOS project.

Key Functionalities:
- Generic `APIResponse` model for standard envelope structure.
- Metadata models for request identification and versioning.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseMeta(BaseModel):
    """Metadata for API responses."""
    request_id: str | None = Field(None, description="Unique identifier for the request")
    version: str = Field("1.0.0", description="API version")

class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)  # type: ignore[arg-type]
