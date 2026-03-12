# Backend Developer Skill

## Purpose
Use this skill when implementing or modifying API endpoints, business logic, LLM integrations, pipeline stages, knowledge management, or skills in the AgentOS Python backend.

## Context Sources
- `docs/modules/backend.md` — module structure, key files, data flow
- `docs/ai-context/backend-AI_CONTEXT.md` — quick reference: key files, APIs, rules
- `docs/development-rules.md` — Python standards, API conventions, error handling
- `docs/modules/agents.md` — agent/crew/supervisor patterns
- `docs/modules/llm.md` — LLM adapter usage rules
- `backend/core/schemas.py` — `APIResponse[T]` envelope
- `backend/core/exceptions.py` — `AgentOSException`
- `backend/api/stores.py` — in-memory data store

## Workflow
1. **Load context** — Read `backend-AI_CONTEXT.md` + relevant module doc
2. **Read target files** — Read existing route/module before modifying
3. **Identify store** — Check `stores.py` for existing data structures
4. **Check patterns** — Reference `resources/api_design_patterns.md`
5. **Implement** — Write `async def` handler; use `APIResponse[T]` for responses
6. **Error handling** — Raise `AgentOSException` for business errors; never swallow
7. **Add types** — Full type annotations; no `Any` without justification
8. **Write test** — Add unit test under `tests/unit/api/` using pytest-asyncio

## Rules
- All route handlers must be `async def`
- Return `APIResponse[T]` — never return raw dicts
- Raise `AgentOSException` for domain errors; let Pydantic handle validation errors
- LLM calls only through `backend/adapters/llm/` — never import OpenAI SDK directly
- Use `settings` singleton from `core/config.py` for all config/env vars
- New resource domains: follow CRUD pattern (create, list, get, update, delete)
- New registry entries: add to appropriate `*_registry.py` module

## Output Expectations
- Route handler(s) with full type annotations
- Pydantic models for request/response schemas
- `stores.py` update if new data structure needed
- Unit test in `tests/unit/api/`
- No MyPy errors; Ruff lint passes

## Resources
- `resources/api_design_patterns.md` — AgentOS REST API patterns
- `resources/service_layer_patterns.md` — business logic organization
- `resources/database_patterns.md` — store/DB migration patterns
