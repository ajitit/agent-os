"""
File: exceptions.py

Purpose:
Defines custom application exceptions and FastAPI exception handlers to provide
consistent, structured error responses across the API.

Key Functionalities:
- Define `AgentOSException`, `NotFoundError`, `ValidationError`
- Define standardized `APIError` response model
- Provide exception handlers for FastAPI integration

Inputs:
- Caught exceptions during API request processing
- FastAPI Request objects

Outputs:
- Standardized JSON error responses (APIError format)
- Correct HTTP status codes

Interacting Files / Modules:
- backend.core.logging_config
"""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class APIError(BaseModel):
    """Standard API error response model."""

    error: str
    detail: str | None = None
    request_id: str | None = None
    code: str | None = None


class AgentOSException(Exception):
    """Base exception for AgentOS application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code or "INTERNAL_ERROR"
        super().__init__(message)


class NotFoundError(AgentOSException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND, "NOT_FOUND")


class ValidationError(AgentOSException):
    """Validation error."""

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR")


async def agentos_exception_handler(request: Request, exc: AgentOSException) -> JSONResponse:
    """Handle AgentOS exceptions."""
    from backend.core.logging_config import request_id_ctx

    return JSONResponse(
        status_code=exc.status_code,
        content=APIError(
            error=exc.code,
            detail=exc.message,
            request_id=request_id_ctx.get(),
        ).model_dump(),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    from backend.core.logging_config import request_id_ctx

    errors = exc.errors()
    detail = "; ".join(
        f"{e['loc'][-1]}: {e['msg']}" for e in errors if e.get("loc")
    ) or "Validation failed"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIError(
            error="VALIDATION_ERROR",
            detail=detail,
            request_id=request_id_ctx.get(),
        ).model_dump(),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    from backend.core.logging_config import request_id_ctx

    import logging

    logging.getLogger("backend").exception("Unhandled exception")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIError(
            error="INTERNAL_ERROR",
            detail="An unexpected error occurred",
            request_id=request_id_ctx.get(),
        ).model_dump(),
    )
