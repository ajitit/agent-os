# AgentOS Architecture Patterns

## 1. Registry Pattern
Used for all manageable resources (tools, models, skills, MCP servers, etc.)
```
GET    /api/v1/{resources}          → list all
POST   /api/v1/{resources}          → create; returns {id, ...}
GET    /api/v1/{resources}/{id}     → get one
PUT    /api/v1/{resources}/{id}     → update
DELETE /api/v1/{resources}/{id}     → soft delete (set status=inactive)
```
- Store: dict keyed by str UUID in `api/stores.py`
- Module: `api/{resource}_registry.py`

## 2. Adapter Pattern (LLM)
- Interface: `backend/adapters/llm/base.py` → `LLMBase`
- Implementations: `adapters/llm/openai.py`, (planned: anthropic.py)
- Rule: All new providers implement `LLMBase`; no direct SDK imports in API layer

## 3. Progressive Disclosure Pattern (Skills)
- Level 1: `metadata.json` — always loaded (~100 tokens)
- Level 2: `SKILL.md` — loaded when agent selects skill
- Level 3: `resources/` — loaded on demand by skill instructions
- Loader: `backend/skills/loader.py`

## 4. Pipeline Stage Pattern
- Base: `pipeline/base.py` → `BaseStage`
- Registration: `StageRegistry` maps stage name → class
- Context: `PipelineContext` flows through all stages
- Error isolation: stage errors logged; pipeline continues to next stage

## 5. Response Envelope Pattern
```python
APIResponse[T]:
  data: T
  meta: ResponseMeta(request_id, version)
```
- Always wrap responses in `APIResponse[T]`
- Error: `APIError(error, detail, request_id, code)`

## 6. Human-in-the-Loop Pattern
```
workflow.start() → execute → check if approval needed
  → pause(approval_id) → notify human
  → human.respond(decision) → resume or cancel
```
- Module: `api/supervisor.py`
