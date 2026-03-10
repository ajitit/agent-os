"""
File: openai.py
"""
import httpx
import json
from typing import AsyncGenerator
from backend.adapters.llm.base import BaseLLMAdapter, LLMRequest, LLMResponse
from backend.core.config import get_settings

class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str | None = None):
        self.settings = get_settings()
        self.api_key = api_key or self.settings.openai_api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        payload = {
            "model": request.model or "gpt-4o",
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
        }
        if request.system_prompt:
            payload["messages"].insert(0, {"role": "system", "content": request.system_prompt})

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
        payload = {
            "model": request.model or "gpt-4o",
            "messages": [{"role": "user", "content": request.prompt}],
            "stream": True,
        }
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", self.base_url, json=payload, headers={"Authorization": f"Bearer {self.api_key}"}) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            if delta: yield delta
                        except: continue
