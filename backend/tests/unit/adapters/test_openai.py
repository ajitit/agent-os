"""
Unit tests for the OpenAIAdapter.
"""

import pytest
import respx
from httpx import Response
<<<<<<< HEAD
from backend.adapters.llm.openai import OpenAIAdapter
from backend.adapters.llm.base import LLMRequest
=======

from backend.adapters.llm.base import LLMRequest
from backend.adapters.llm.openai import OpenAIAdapter

>>>>>>> c952205 (Initial upload of AgentOS code)

@pytest.mark.asyncio
async def test_openai_adapter_generate_success():
    """Test successful generation with mocked OpenAI response."""
    adapter = OpenAIAdapter(api_key="test-key")
    request = LLMRequest(prompt="Hello", system_prompt="Be helpful")
<<<<<<< HEAD
    
=======

>>>>>>> c952205 (Initial upload of AgentOS code)
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
<<<<<<< HEAD
        
        response = await adapter.generate(request)
        
=======

        response = await adapter.generate(request)

>>>>>>> c952205 (Initial upload of AgentOS code)
        assert response.content == "Hi there!"
        assert response.model == "gpt-4o"
        assert response.usage["total_tokens"] == 10

@pytest.mark.asyncio
async def test_openai_adapter_no_api_key():
<<<<<<< HEAD
    """Test error when API key is missing."""
    adapter = OpenAIAdapter(api_key=None)
    # Ensure current settings also don't have it for the test
    adapter.api_key = None 
    request = LLMRequest(prompt="Hello")
    
    with pytest.raises(ValueError, match="OpenAI API Key is not configured"):
        await adapter.generate(request)
=======
    """Test error when API key is missing — raises ValueError at init."""
    with pytest.raises(ValueError, match="OpenAI API Key is not configured"):
        OpenAIAdapter(api_key=None)
>>>>>>> c952205 (Initial upload of AgentOS code)
