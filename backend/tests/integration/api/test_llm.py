"""
Integration tests for the LLM API router.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_generate_endpoint_no_auth():
    """Test that endpoint requires authentication."""
    response = client.post(
        "/api/v1/llm/generate",
        json={"prompt": "Hello"}
    )
    assert response.status_code == 403 # HTTPBearer without token returns 403 by default in TestClient if not handled

def test_generate_endpoint_with_auth(monkeypatch):
    """Test successful API call with auth and mocked adapter."""
    # Note: In a full integration test, we would mock the adapter at the dependency level
    # For now, we test the envelope structure
    
    from backend.app.adapters.llm.base import LLMResponse
    
    async def mock_generate(*args, **kwargs):
        return LLMResponse(content="Mocked response", model="test-model", usage={})
    
    monkeypatch.setattr("backend.app.adapters.llm.openai.OpenAIAdapter.generate", mock_generate)
    
    headers = {"Authorization": "Bearer fake-token"}
    response = client.post(
        "/api/v1/llm/generate",
        json={"prompt": "Hello"},
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert data["data"]["content"] == "Mocked response"
    assert data["meta"]["version"] == "1.0.0"
