"""
File: base.py

Purpose:
Defines the abstract interface for LLM adapters, ensuring modularity and 
interchangeability of different LLM providers.

Key Functionalities:
- `BaseLLMAdapter` abstract base class.
- Pydantic models for LLM requests (LLMRequest) and responses (LLMResponse).
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator
from pydantic import BaseModel, Field

class LLMRequest(BaseModel):
    """Request model for LLM generation."""
    prompt: str = Field(..., description="The input prompt for the LLM")
    system_prompt: str | None = Field(None, description="Optional system instruction")
    model: str | None = Field(None, description="Specific model to use")
    temperature: float = Field(0.7, ge=0, le=2, description="Sampling temperature")
    max_tokens: int | None = Field(None, description="Maximum tokens to generate")

class LLMResponse(BaseModel):
    """Response model for LLM generation."""
    content: str = Field(..., description="The generated text content")
    model: str = Field(..., description="The model used for generation")
    usage: dict[str, int] = Field(default_factory=dict, description="Token usage statistics")

class BaseLLMAdapter(ABC):
    """Abstract Base Class for all LLM Adapters."""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a single completion from the LLM."""
        pass

    @abstractmethod
    async def stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream the LLM response content."""
        yield ""  # Abstract methods can yield or pass
