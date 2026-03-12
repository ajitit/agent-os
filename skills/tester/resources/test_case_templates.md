# Test Case Templates

## Backend Unit Test (pytest-asyncio)
```python
# tests/unit/api/test_{resource}.py
import pytest
from httpx import AsyncClient
from backend.app.main import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.mark.asyncio
async def test_create_{resource}_success(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/{resources}",
            json={"name": "Test", "description": "Test desc"},
            headers={"Authorization": "Bearer test-token"}
        )
    assert response.status_code == 201
    data = response.json()
    assert data["data"]["name"] == "Test"
    assert "id" in data["data"]

@pytest.mark.asyncio
async def test_get_{resource}_not_found(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/{resources}/nonexistent-id")
    assert response.status_code == 404
    assert "error" in response.json()
```

## Backend Integration Test (with external HTTP mock)
```python
# tests/integration/api/test_{service}.py
import pytest
import respx
import httpx

@pytest.mark.asyncio
async def test_llm_call_success():
    with respx.mock:
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json={"choices": [{"message": {"content": "Hello"}}]})
        )
        # call your function that uses the LLM
        result = await my_function()
    assert result == "Hello"
```

## Frontend Component Test (Vitest)
```tsx
// src/app/{feature}/page.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import FeaturePage from './page'
import * as api from '@/lib/api'

vi.mock('@/lib/api')

test('renders items after load', async () => {
  vi.mocked(api.get).mockResolvedValue({ data: [{ id: '1', name: 'Test' }] })
  render(<FeaturePage />)
  await waitFor(() => expect(screen.getByText('Test')).toBeInTheDocument())
})

test('shows error on API failure', async () => {
  vi.mocked(api.get).mockRejectedValue(new Error('Network error'))
  render(<FeaturePage />)
  await waitFor(() => expect(screen.getByText(/error/i)).toBeInTheDocument())
})
```
