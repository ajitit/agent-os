# Service Layer Patterns

## Current Pattern (Thin Services)
Business logic lives in route handlers. Acceptable for current complexity.

```python
@router.post("/agents/{agent_id}/run")
async def run_agent(agent_id: str):
    agent = _agents.get(agent_id)
    if not agent:
        raise AgentOSException(404, "Agent not found")
    # Business logic inline for simple cases
    result = await llm_adapter.complete(agent["system_prompt"], messages)
    return APIResponse(data={"result": result})
```

## When to Extract a Service
Extract to a service class when:
- Logic is shared across multiple route handlers
- Logic has multiple steps (> 5 lines of business logic)
- Logic requires coordination between multiple stores

```python
# backend/services/agent_runner.py
class AgentRunner:
    def __init__(self, llm: LLMBase):
        self.llm = llm

    async def run(self, agent: dict, messages: list) -> str:
        ...
```

## LLM Integration Pattern
```python
from backend.adapters.llm.openai import OpenAIAdapter
from backend.core.config import settings

adapter = OpenAIAdapter(api_key=settings.openai_api_key)
response = await adapter.complete(
    system_prompt=agent["system_prompt"],
    messages=conversation_messages,
    model=agent["model"],
    temperature=agent["temperature"]
)
```

## Store Access Pattern
```python
from backend.api.stores import _agents, _agent_tools
# Always use store functions — never import store dicts in other modules
```
