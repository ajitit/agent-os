"""Custom middleware for request processing."""

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.logging_config import request_id_ctx


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add X-Request-ID header and store in context for tracing."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx.reset(token)
