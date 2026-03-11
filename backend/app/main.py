"""
Module: app/main.py

Application factory for the AgentOS FastAPI application.

Configures middleware, exception handlers, and registers all API routers
under the ``/api/v1`` prefix.  Uses the lifespan context manager for
structured startup/shutdown logging.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import (
    agents,
    audit,
    auth,
    chat,
    conversations,
    crews,
    health,
    knowledge,
    llm,
    marketplace,
    mcp_servers,
    observability,
    pipeline,
    plans,
    preferences,
    skills,
    storage,
    supervisor,
    tasks,
    workflows,
)
from backend.api import (
    settings as settings_api,
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

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — configure logging on startup.

    Args:
        app: FastAPI application instance.

    Yields:
        Control back to the ASGI server.
    """
    cfg = get_settings()
    configure_logging(cfg.log_level)
    logger.info("app=startup name=%s env=%s", cfg.app_name, cfg.environment)
    yield
    logger.info("app=shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Fully configured FastAPI instance.
    """
    cfg = get_settings()
    app = FastAPI(
        title=cfg.app_name,
        description="Enterprise Multi-Agent AI Operating System — API",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ────────────────────────────────────────────────────
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(AgentOSException, agentos_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]

    # ── Routers ───────────────────────────────────────────────────────────────
    prefix = cfg.api_v1_prefix

    # Infrastructure & auth
    app.include_router(health.router, prefix=prefix)
    app.include_router(auth.router, prefix=prefix)
    app.include_router(preferences.router, prefix=prefix)
    app.include_router(settings_api.router, prefix=prefix)

    # Core resources
    app.include_router(crews.router, prefix=prefix)
    app.include_router(agents.router, prefix=prefix)
    app.include_router(mcp_servers.router, prefix=prefix)
    app.include_router(conversations.router, prefix=prefix)
    app.include_router(storage.router, prefix=prefix)
    app.include_router(knowledge.router, prefix=prefix)
    app.include_router(skills.router, prefix=prefix)
    app.include_router(tasks.router, prefix=prefix)
    app.include_router(llm.router, prefix=prefix)

    # Execution & orchestration
    app.include_router(supervisor.router, prefix=prefix)
    app.include_router(plans.router, prefix=prefix)
    app.include_router(chat.router, prefix=prefix)
    app.include_router(workflows.router, prefix=prefix)

    # Pipeline
    app.include_router(pipeline.router, prefix=prefix)

    # Observability & audit
    app.include_router(observability.router, prefix=prefix)
    app.include_router(audit.router, prefix=prefix)

    # Marketplace
    app.include_router(marketplace.router, prefix=prefix)

    # ── Built-in utility routes ───────────────────────────────────────────────
    @app.get("/api/health")
    def api_health_alias() -> dict[str, str]:
        """Health check alias at /api/health."""
        return {"status": "ok", "version": "1.0.0", "environment": cfg.environment}

    @app.get("/")
    def root() -> dict[str, str]:
        """Root — returns app name and docs URL."""
        return {"status": f"{cfg.app_name} running", "docs": "/api/docs"}

    return app


app = create_app()
