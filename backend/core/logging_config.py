"""
File: logging_config.py

Purpose:
Configures structured application logging to ensure traceability, injecting
request correlation IDs into log records.

Key Functionalities:
- Define a structured log formatter
- Attach request IDs from context variables to log output
- Configure global root logger and Uvicorn loggers

Inputs:
- Log level configuration string (e.g., 'INFO', 'DEBUG')
- Application log events

Outputs:
- Formatted log messages emitted to stdout

Interacting Files / Modules:
- None
"""

import logging
import sys
from contextvars import ContextVar
from typing import Any

import uvicorn

# Correlation ID for request tracing
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Structured log formatter for traceability."""

    def format(self, record: logging.LogRecord) -> str:
        extras: dict[str, Any] = {
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.exc_info:
            extras["exception"] = self.formatException(record.exc_info)
        rid = request_id_ctx.get()
        if rid:
            extras["request_id"] = rid
        return " | ".join(f"{k}={v}" for k, v in extras.items())


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    handler.setLevel(log_level)

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(log_level)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    uvicorn.config.LOGGING_CONFIG["formatters"]["default"]["fmt"] = (
        "%(levelprefix)s %(message)s"
    )
