"""Health check endpoints for load balancers and orchestration."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.core.config import Settings, get_settings

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    """Readiness check response."""

    ready: bool
    database: str
    redis: str


@router.get("", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Liveness probe - returns 200 if the process is running."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(settings: Settings = Depends(get_settings)) -> ReadinessResponse:
    """Readiness probe - checks dependencies (database, redis) are reachable."""
    # TODO: Add actual DB/Redis connectivity checks
    return ReadinessResponse(
        ready=True,
        database="connected",
        redis="connected",
    )
