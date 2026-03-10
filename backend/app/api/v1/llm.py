"""
File: llm.py

Purpose:
Exposes LLM functionalities via REST API endpoints, following project engineering standards.

Key Functionalities:
- Endpoint for standard LLM generation.
- Uses standard response envelope and JWT security.
- Dependency-based adapter selection.
"""

from typing import Annotated
from fastapi import APIRouter, Depends
from backend.app.adapters.llm.base import BaseLLMAdapter, LLMRequest, LLMResponse
from backend.app.adapters.llm.openai import OpenAIAdapter
from backend.app.core.schemas import APIResponse
from backend.app.core.security import get_current_user

router = APIRouter(prefix="/llm", tags=["LLM"])

def get_llm_adapter() -> BaseLLMAdapter:
    """Dependency provider for LLM adapter."""
    return OpenAIAdapter()

@router.post("/generate", response_model=APIResponse[LLMResponse])
async def generate_completion(
    request: LLMRequest,
    adapter: Annotated[BaseLLMAdapter, Depends(get_llm_adapter)],
    user: Annotated[dict, Depends(get_current_user)]
) -> APIResponse[LLMResponse]:
    """
    Generate a completion from an LLM.
    
    Requires a valid Bearer JWT.
    """
    # Note: user information can be used here for tracing/logging
    response = await adapter.generate(request)
    return APIResponse(data=response)
