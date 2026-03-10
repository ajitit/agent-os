"""
File: chat.py

Purpose:
Provides API endpoints for chat interactions, including streaming responses
from agents.

Key Functionalities:
- Stream chat interactions to the client

Inputs:
- HTTP GET requests for the stream endpoint

Outputs:
- Server-Sent Events (SSE) or streaming text responses

Interacting Files / Modules:
- None
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


async def _stream():
    """Stream placeholder response."""
    yield "Agent thinking...\n"
    yield "Done."


@router.get("/stream")
async def chat_stream():
    """Stream chat responses from agents."""
    return StreamingResponse(_stream(), media_type="text/plain; charset=utf-8")
