"""
Module: adapters/llm/openai.py

OpenAI LLM adapter implementing BaseLLMAdapter via the chat completions API.
Supports both single-shot generation and streaming.
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from backend.adapters.llm.base import BaseLLMAdapter, LLMRequest, LLMResponse
from backend.core.config import get_settings


class OpenAIAdapter(BaseLLMAdapter):
    """Concrete LLM adapter for the OpenAI chat completions endpoint.

    Attributes:
        api_key: OpenAI API key used for authentication.
        base_url: Chat completions endpoint URL.
    """

    def __init__(self, api_key: str | None = None) -> None:
        """Initialise the adapter.

        Args:
            api_key: Optional API key override; falls back to settings.

        Raises:
            ValueError: If no API key is available.
        """
        self.settings = get_settings()
        self.api_key = api_key or self.settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API Key is not configured")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def _build_messages(self, request: LLMRequest) -> list[dict[str, str]]:
        """Construct the messages list, prepending a system prompt if set.

        Args:
            request: LLM generation request.

        Returns:
            List of message dicts in OpenAI format.
        """
        messages: list[dict[str, str]] = [{"role": "user", "content": request.prompt}]
        if request.system_prompt:
            messages.insert(0, {"role": "system", "content": request.system_prompt})
        return messages

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Send a single-shot generation request to the OpenAI API.

        Args:
            request: LLM generation parameters.

        Returns:
            LLMResponse with content, model, and usage stats.
        """
        payload: dict[str, Any] = {
            "model": request.model or "gpt-4o",
            "messages": self._build_messages(request),
            "temperature": request.temperature,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                usage=data.get("usage", {}),
            )

    async def stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream generation tokens from the OpenAI API using SSE.

        Args:
            request: LLM generation parameters.

        Yields:
            Partial content strings as they arrive.
        """
        payload: dict[str, Any] = {
            "model": request.model or "gpt-4o",
            "messages": self._build_messages(request),
            "stream": True,
        }
        async with (
            httpx.AsyncClient() as client,
            client.stream(
                "POST",
                self.base_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            ) as response,
        ):
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    try:
                        chunk = json.loads(line[6:])
                        delta = chunk["choices"][0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except json.JSONDecodeError:
                        continue
