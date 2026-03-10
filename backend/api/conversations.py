"""Conversations API - CRUD, messages, and chat."""

from fastapi import APIRouter
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


@router.get("")
def get_all_conversations():
    """Get all conversations."""
    return conversation_list()


@router.post("")
def create_conversation(payload: ConversationCreate):
    """Create a new conversation."""
    data = payload.model_dump(exclude_none=True) or {}
    return conversation_create(data)


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    """Get a specific conversation."""
    conv = conversation_get(conversation_id)
    if not conv:
        raise NotFoundError("Conversation not found")
    return conv


@router.put("/{conversation_id}")
def update_conversation(conversation_id: str, payload: ConversationUpdate):
    """Update a conversation."""
    data = payload.model_dump(exclude_none=True)
    if not data:
        return get_conversation(conversation_id)
    conv = conversation_update(conversation_id, data)
    if not conv:
        raise NotFoundError("Conversation not found")
    return conv


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if not conversation_delete(conversation_id):
        raise NotFoundError("Conversation not found")


@router.get("/{conversation_id}/messages")
def get_conversation_messages(conversation_id: str):
    """Get messages for a conversation."""
    if not conversation_get(conversation_id):
        raise NotFoundError("Conversation not found")
    return conversation_message_list(conversation_id)


@router.post("/{conversation_id}/messages")
def add_message_to_conversation(conversation_id: str, payload: MessageCreate):
    """Add a message to a conversation."""
    msg = conversation_message_add(conversation_id, payload.model_dump())
    if not msg:
        raise NotFoundError("Conversation not found")
    return msg


@router.post("/{conversation_id}/chat")
def chat(conversation_id: str, payload: ChatMessage):
    """Send a message to the crew and get a response."""
    if not conversation_get(conversation_id):
        raise NotFoundError("Conversation not found")
    conversation_message_add(
        conversation_id, {"role": "user", "content": payload.message}
    )
    response = f"Echo: {payload.message}"
    conversation_message_add(conversation_id, {"role": "assistant", "content": response})
    return {"response": response}


@router.post("/{conversation_id}/chat/stream")
def chat_stream(conversation_id: str, payload: ChatMessage):
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
