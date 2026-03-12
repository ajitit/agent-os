"""
Unit tests for the OpenAIAdapter.
"""

import pytest
import respx
from httpx import Response

from backend.adapters.llm.base import LLMRequest
from backend.adapters.llm.openai import OpenAIAdapter


@pytest.mark.asyncio
async def test_openai_adapter_generate_success():
    """Test successful generation with mocked OpenAI response."""
    adapter = OpenAIAdapter(api_key="test-key")
    request = LLMRequest(prompt="Hello", system_prompt="Be helpful")

    with respx.mock:
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=Response(
                200,
                json={
                    "choices": [{"message": {"content": "Hi there!"}}],
                    "model": "gpt-4o",
                    "usage": {"total_tokens": 10}
                }
            )
        )

        response = await adapter.generate(request)

        assert response.content == "Hi there!"
        assert response.model == "gpt-4o"
        assert response.usage["total_tokens"] == 10

@pytest.mark.asyncio
async def test_openai_adapter_no_api_key(monkeypatch):
    """Test error when API key is missing — raises ValueError at init."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from backend.core.config import get_settings
    settings = get_settings()
    monkeypatch.setattr(settings, "openai_api_key", None)
    with pytest.raises(ValueError, match="OpenAI API Key is not configured"):
        OpenAIAdapter(api_key=None)
