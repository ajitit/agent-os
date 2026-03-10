"""AgentOS FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import agents, chat, conversations, crews, health, mcp_servers, settings, skills, storage, supervisor, tasks
from backend.core.config import get_settings
from backend.core.exceptions import (
    AgentOSException,
    agentos_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from backend.core.logging_config import configure_logging
from backend.core.middleware import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    configure_logging(settings.log_level)
    yield
    # Shutdown: close connections, flush logs, etc.


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Enterprise Multi-Agent AI Operating System - API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Middleware
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(AgentOSException, agentos_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # API v1 routes
    prefix = settings.api_v1_prefix
    app.include_router(health.router, prefix=prefix)
    app.include_router(settings.router, prefix=prefix)
    app.include_router(crews.router, prefix=prefix)
    app.include_router(agents.router, prefix=prefix)
    app.include_router(mcp_servers.router, prefix=prefix)
    app.include_router(conversations.router, prefix=prefix)
    app.include_router(storage.router, prefix=prefix)
    app.include_router(skills.router, prefix=prefix)
    app.include_router(supervisor.router, prefix=prefix)
    app.include_router(tasks.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)

    @app.get("/api/health")
    def api_health_alias():
        return {"status": "ok", "version": "1.0.0", "environment": settings.environment}

    @app.get("/")
    def root():
        return {"status": f"{settings.app_name} running", "docs": "/api/docs"}

    return app


app = create_app()
