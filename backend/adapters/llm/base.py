"""
File: base.py
"""
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)

class BaseLLMAdapter(ABC):
    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        pass

    @abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        yield ""
