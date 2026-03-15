# Backend AI Context — Vishwakarma API

## Module Purpose
Vishwakarma FastAPI Python backend. 26 route modules under `/api/v1`. All data flows through `api/stores.py` in-memory dicts (transitioning to PostgreSQL).

## Key Files
- `app/main.py` — FastAPI factory; registers all 26 routers
- `core/config.py` — `settings` singleton (Pydantic Settings)
- `core/schemas.py` — `APIResponse[T]` response envelope
- `core/exceptions.py` — `AgentOSException` + 3 global handlers
- `core/security.py` — JWT create/verify
- `api/stores.py` — all in-memory CRUD state
- `adapters/llm/base.py` — abstract LLM interface
- `adapters/llm/openai.py` — OpenAI implementation
- `skills/loader.py` — 3-level progressive skill loading
- `pipeline/orchestrator.py` — 9-stage pipeline runner

## Data Flow
```
Request → RequestIDMiddleware → JWT auth
        → Route handler → stores.py
        → APIResponse[T] → JSON
Error   → AgentOSException → APIError JSON
```

## Important APIs
- `POST /api/v1/auth/login` — get JWT
- `POST /api/v1/agents` — create agent
- `GET  /api/v1/skills/{id}` — get skill instructions
- `POST /api/v1/conversations/{id}/chat/stream` — SSE streaming
- `POST /api/v1/supervisor/workflows` — start workflow
- `POST /api/v1/supervisor/approvals/{id}/respond` — HITL decision

## Critical Rules
- All handlers are `async def`
- Return `APIResponse[T]`; raise `AgentOSException` for errors
- LLM calls only through `adapters/llm/` — never direct SDK imports
- Config only via `settings` from `core/config.py`

## Dependencies
- FastAPI 0.115+, Pydantic v2, PyJWT, passlib
- langchain-openai, chromadb, sentence-transformers
- PostgreSQL (planned), Redis, ChromaDB
