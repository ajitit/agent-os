"""
File: main.py

Purpose:
Serves as the main entry point for the AgentOS FastAPI application, initializing
the app, configuring middleware, and routing all API endpoints.

Key Functionalities:
- Initialize FastAPI application instance
- Configure CORS and request ID middleware
- Register exception handlers
- Include all API routers
- Define health and root endpoints

Inputs:
- HTTP requests
- Environment variables via configuration settings

Outputs:
- Configured FastAPI application instance
- HTTP responses for all registered routes

Interacting Files / Modules:
- backend.api.*
- backend.core.config
- backend.core.exceptions
- backend.core.logging_config
- backend.core.middleware
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import (
    agents,
    auth,
    chat,
    conversations,
    crews,
    health,
    mcp_servers,
    settings as settings_api,
    skills,
    storage,
    supervisor,
    tasks,
    knowledge,
    llm,
    preferences,
)
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
    cfg = get_settings()
    configure_logging(cfg.log_level)
    yield
    # Shutdown: close connections, flush logs, etc.


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    cfg = get_settings()
    app = FastAPI(
        title=cfg.app_name,
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
        allow_origins=cfg.cors_origins,
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
    prefix = cfg.api_v1_prefix
    app.include_router(health.router, prefix=prefix)
    app.include_router(auth.router, prefix=prefix)
    app.include_router(preferences.router, prefix=prefix)
    app.include_router(settings_api.router, prefix=prefix)
    app.include_router(crews.router, prefix=prefix)
    app.include_router(agents.router, prefix=prefix)
    app.include_router(mcp_servers.router, prefix=prefix)
    app.include_router(conversations.router, prefix=prefix)
    app.include_router(storage.router, prefix=prefix)
    app.include_router(knowledge.router, prefix=prefix)
    app.include_router(skills.router, prefix=prefix)
    app.include_router(supervisor.router, prefix=prefix)
    app.include_router(tasks.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(llm.router, prefix=prefix)

    @app.get("/api/health")
    def api_health_alias():
        return {"status": "ok", "version": "1.0.0", "environment": cfg.environment}

    @app.get("/")
    def root():
        return {"status": f"{cfg.app_name} running", "docs": "/api/docs"}

    return app


app = create_app()
