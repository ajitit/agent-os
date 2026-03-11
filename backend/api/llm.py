"""
File: llm.py
"""
from typing import Annotated
<<<<<<< HEAD
from fastapi import APIRouter, Depends
=======

from fastapi import APIRouter, Depends

>>>>>>> c952205 (Initial upload of AgentOS code)
from backend.adapters.llm.base import BaseLLMAdapter, LLMRequest, LLMResponse
from backend.adapters.llm.openai import OpenAIAdapter
from backend.core.schemas import APIResponse
from backend.core.security import get_current_user

router = APIRouter(prefix="/llm", tags=["LLM"])

def get_llm_adapter() -> BaseLLMAdapter:
    return OpenAIAdapter()

@router.post("/generate", response_model=APIResponse[LLMResponse])
async def generate_completion(
    request: LLMRequest,
    adapter: Annotated[BaseLLMAdapter, Depends(get_llm_adapter)],
    user: Annotated[dict, Depends(get_current_user)]
):
    response = await adapter.generate(request)
    return APIResponse(data=response)
