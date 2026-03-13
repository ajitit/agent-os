"""
File: conversations.py

Purpose:
Defines REST API endpoints for managing conversations and integrating chat functionality,
allowing users to interact with agents and crews.

Key Functionalities:
- CRUD operations for conversations
- Managing messages within a conversation
- Synchronous and streaming chat endpoints

Inputs:
- HTTP requests with conversation metadata
- Chat messages (user input)

Outputs:
- JSON responses with conversation and message data
- Streaming responses for chat interactions

Interacting Files / Modules:
- backend.api.stores
- backend.core.exceptions
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.api.stores import (
    conversation_create,
    conversation_delete,
    conversation_get,
    conversation_list,
    conversation_message_add,
    conversation_message_list,
    conversation_update,
)
from backend.core.exceptions import NotFoundError
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    """Request to create a conversation."""

    title: str | None = None


class ConversationUpdate(BaseModel):
    """Request to update a conversation."""

    title: str | None = Field(None, min_length=1, max_length=500)


class MessageCreate(BaseModel):
    """Request to add a message."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)


class ChatMessage(BaseModel):
    """Request to send a chat message."""

    message: str = Field(..., min_length=1)


async def _stream_response(text: str):
    """Stream response in chunks."""
    for chunk in [text[i : i + 10] for i in range(0, len(text), 10)]:
        yield chunk


@router.get("", response_model=APIResponse[list])
async def get_all_conversations(user: Annotated[dict, Depends(get_current_user)]):
    """Get all conversations."""
    return APIResponse(data=conversation_list())


@router.post("", response_model=APIResponse[dict], status_code=201)
async def create_conversation(
    payload: ConversationCreate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Create a new conversation."""
    data = payload.model_dump(exclude_none=True) or {}
    return APIResponse(data=conversation_create(data))


@router.get("/{conversation_id}", response_model=APIResponse[dict])
async def get_conversation(
    conversation_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Get a specific conversation."""
    conv = conversation_get(conversation_id)
    if not conv:
        raise NotFoundError("Conversation not found")
    return APIResponse(data=conv)


@router.put("/{conversation_id}", response_model=APIResponse[dict])
async def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Update a conversation."""
    data = payload.model_dump(exclude_none=True)
    if not data:
        conv = conversation_get(conversation_id)
        if not conv:
            raise NotFoundError("Conversation not found")
        return APIResponse(data=conv)
    conv = conversation_update(conversation_id, data)
    if not conv:
        raise NotFoundError("Conversation not found")
    return APIResponse(data=conv)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Delete a conversation."""
    if not conversation_delete(conversation_id):
        raise NotFoundError("Conversation not found")


@router.get("/{conversation_id}/messages", response_model=APIResponse[list])
async def get_conversation_messages(
    conversation_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Get messages for a conversation."""
    if not conversation_get(conversation_id):
        raise NotFoundError("Conversation not found")
    return APIResponse(data=conversation_message_list(conversation_id))


@router.post("/{conversation_id}/messages", response_model=APIResponse[dict], status_code=201)
async def add_message_to_conversation(
    conversation_id: str,
    payload: MessageCreate,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Add a message to a conversation."""
    msg = conversation_message_add(conversation_id, payload.model_dump())
    if not msg:
        raise NotFoundError("Conversation not found")
    return APIResponse(data=msg)


@router.post("/{conversation_id}/chat", response_model=APIResponse[dict], status_code=201)
async def chat(
    conversation_id: str,
    payload: ChatMessage,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Send a message to the crew and get a response."""
    if not conversation_get(conversation_id):
        raise NotFoundError("Conversation not found")
    conversation_message_add(
        conversation_id, {"role": "user", "content": payload.message}
    )
    response = f"Echo: {payload.message}"
    conversation_message_add(conversation_id, {"role": "assistant", "content": response})
    return APIResponse(data={"response": response})


@router.post("/{conversation_id}/chat/stream", status_code=201)
async def chat_stream(
    conversation_id: str,
    payload: ChatMessage,
    user: Annotated[dict, Depends(get_current_user)],
):
    """Send a message and get a streaming response."""
    if not conversation_get(conversation_id):
        raise NotFoundError("Conversation not found")
    conversation_message_add(
        conversation_id, {"role": "user", "content": payload.message}
    )
    response = f"Echo (streaming): {payload.message}"
    conversation_message_add(conversation_id, {"role": "assistant", "content": response})
    return StreamingResponse(
        _stream_response(response), media_type="text/plain; charset=utf-8"
    )
