"""
File: openai.py

Purpose:
Concrete implementation of the BaseLLMAdapter for OpenAI models.

Key Functionalities:
- Integration with OpenAI Chat Completions API via httpx.
- Support for streaming and non-streaming responses.
"""

from typing import AsyncGenerator
import httpx
from backend.app.adapters.llm.base import BaseLLMAdapter, LLMRequest, LLMResponse
from backend.core.config import get_settings

class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI LLMs."""

    def __init__(self, api_key: str | None = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.openai_api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a completion using OpenAI."""
        if not self.api_key:
            raise ValueError("OpenAI API Key is not configured")

        payload = {
            "model": request.model or "gpt-4o",
            "messages": [
                {"role": "system", "content": request.system_prompt} if request.system_prompt else None,
                {"role": "user", "content": request.prompt}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        # Filter out None messages
        payload["messages"] = [m for m in payload["messages"] if m is not None]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                usage=data.get("usage", {})
            )

    async def stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream a completion from OpenAI."""
        if not self.api_key:
            raise ValueError("OpenAI API Key is not configured")

        payload = {
            "model": request.model or "gpt-4o",
            "messages": [
                {"role": "system", "content": request.system_prompt} if request.system_prompt else None,
                {"role": "user", "content": request.prompt}
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True,
        }
        payload["messages"] = [m for m in payload["messages"] if m is not None]

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                self.base_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30.0
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        # Simple parsing for example purposes
                        # In a production env, use a library like openai-python or more robust JSON parsing
                        import json
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
