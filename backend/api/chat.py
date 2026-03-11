"""
File: chat.py

Purpose:
<<<<<<< HEAD
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
=======
Chat UI backend — real-time streaming chat endpoint that routes user messages
through the SupervisorAgent/WorkflowExecutionEngine via SSE.

Key Functionalities:
- POST /chat/send — submit a task, returns run_id
- GET  /chat/stream/{run_id} — SSE stream of execution events
- GET  /chat/conversations/{conv_id}/messages — conversation history
- POST /chat/conversations — create conversation
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.api.stores import (
    conversation_create,
    conversation_get,
    conversation_list,
    conversation_message_add,
    conversation_message_list,
    generate_id,
)
from backend.core.engine import get_engine
from backend.core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

# In-memory event queues: run_id -> list of events
_run_queues: dict[str, asyncio.Queue] = {}


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: str | None = None
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    agent_id: str | None = None


class ConversationCreate(BaseModel):
    title: str | None = None


@router.post("/conversations")
async def create_conversation(
    payload: ConversationCreate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Create a new chat conversation."""
    conv = conversation_create({"title": payload.title or "New Chat", "userId": user["id"]})
    return {"data": conv}


@router.get("/conversations")
async def list_conversations(user: Annotated[dict, Depends(get_current_user)]):
    """List conversations for the current user."""
    convs = conversation_list()
    user_convs = [c for c in convs if c.get("userId") == user["id"]]
    return {"data": user_convs}


@router.get("/conversations/{conv_id}/messages")
async def get_messages(conv_id: str, user: Annotated[dict, Depends(get_current_user)]):
    """Get message history for a conversation."""
    conv = conversation_get(conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    msgs = conversation_message_list(conv_id)
    return {"data": msgs}


@router.post("/send")
async def send_message(
    payload: SendMessageRequest,
    user: Annotated[dict, Depends(get_current_user)],
):
    """
    Submit a user message. Starts async workflow execution and returns a run_id
    the client can use to subscribe to the SSE stream.
    """
    run_id = generate_id()
    conv_id = payload.conversation_id

    # Persist user message
    if conv_id:
        conversation_message_add(conv_id, {
            "role": "user",
            "content": payload.message,
            "runId": run_id,
        })

    # Create SSE queue
    q: asyncio.Queue = asyncio.Queue()
    _run_queues[run_id] = q

    # Launch workflow in background
    asyncio.create_task(
        _run_workflow(run_id, payload.message, user["id"], conv_id, q)
    )

    return {"data": {"runId": run_id, "status": "started"}}


@router.get("/stream/{run_id}")
async def stream_run(run_id: str):
    """
    SSE endpoint — streams execution events for a given run_id.
    Client subscribes after POST /chat/send.
    """
    if run_id not in _run_queues:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator() -> AsyncGenerator[str, None]:
        q = _run_queues[run_id]
        while True:
            try:
                event = await asyncio.wait_for(q.get(), timeout=120)
                if event is None:  # sentinel — done
                    yield "event: done\ndata: {}\n\n"
                    break
                yield f"data: {json.dumps(event)}\n\n"
            except TimeoutError:
                yield "event: ping\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _run_workflow(
    run_id: str,
    message: str,
    user_id: str,
    conv_id: str | None,
    q: asyncio.Queue,
) -> None:
    """Background task: run the workflow engine and feed events into the SSE queue."""
    engine = get_engine()
    try:
        async for event in engine.run(
            workflow_id="supervisor",
            initial_input=message,
            config={"threadId": run_id, "userId": user_id},
        ):
            await q.put(event)
            # Persist assistant messages to conversation
            if conv_id and event.get("type") == "message" and event.get("nodeName") == "agent":
                conversation_message_add(conv_id, {
                    "role": "assistant",
                    "content": event.get("message", ""),
                    "runId": run_id,
                })
    finally:
        await q.put(None)  # sentinel
        # Clean up after 5 min
        await asyncio.sleep(300)
        _run_queues.pop(run_id, None)
>>>>>>> c952205 (Initial upload of AgentOS code)
