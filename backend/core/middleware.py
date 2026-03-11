"""
File: middleware.py

Purpose:
Defines custom FastAPI middleware to process incoming HTTP requests before they
reach route handlers, specifically for request tracing.

Key Functionalities:
- Extract or generate an `X-Request-ID` for each incoming request
- Store the request ID in a context variable for use in logging/error handling
- Attach the request ID to the outgoing HTTP response

Inputs:
- Incoming FastAPI HTTP requests

Outputs:
- Outgoing FastAPI HTTP responses with appended correlation headers

Interacting Files / Modules:
- backend.core.logging_config
"""

import uuid
<<<<<<< HEAD

from fastapi import Request
=======
from typing import Any

from fastapi import Request, Response
>>>>>>> c952205 (Initial upload of AgentOS code)
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.logging_config import request_id_ctx


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add X-Request-ID header and store in context for tracing."""

<<<<<<< HEAD
    async def dispatch(self, request: Request, call_next):
=======
    async def dispatch(self, request: Request, call_next: Any) -> Any:
>>>>>>> c952205 (Initial upload of AgentOS code)
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)
