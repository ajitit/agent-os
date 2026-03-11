"""
Unit tests for the OpenAIAdapter.
"""

import pytest
import respx
from httpx import Response
from backend.adapters.llm.openai import OpenAIAdapter
from backend.adapters.llm.base import LLMRequest

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
async def test_openai_adapter_no_api_key():
    """Test error when API key is missing."""
    adapter = OpenAIAdapter(api_key=None)
    # Ensure current settings also don't have it for the test
    adapter.api_key = None 
    request = LLMRequest(prompt="Hello")
    
    with pytest.raises(ValueError, match="OpenAI API Key is not configured"):
        await adapter.generate(request)
