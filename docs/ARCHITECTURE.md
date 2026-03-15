# Vishwakarma — Architecture

## System Layers

```
┌─────────────────────────────────────────┐
│          Next.js Frontend (UI)           │
│  Pages: chat, agents, crews, registry,  │
│         workflows, plans, marketplace   │
└───────────────┬─────────────────────────┘
                │ HTTP REST / SSE streaming
┌───────────────▼─────────────────────────┐
│        FastAPI Backend /api/v1           │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐  │
│  │  Router  │ │  Core   │ │ Pipeline │  │
│  │  Layer   │ │(auth,   │ │ (9-stage)│  │
│  │ 26 mods  │ │ cfg,exc)│ │          │  │
│  └──────────┘ └─────────┘ └──────────┘  │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐  │
│  │  Agents  │ │Knowledge│ │   LLM    │  │
│  │ +Skills  │ │ Manager │ │ Adapters │  │
│  └──────────┘ └─────────┘ └──────────┘  │
└──────────┬─────────────┬────────────────┘
           │             │
    ┌──────▼──────┐ ┌────▼─────┐
    │ PostgreSQL  │ │  Redis   │
    │  (planned)  │ │ (memory) │
    └─────────────┘ └──────────┘
         ┌──────────────┐
         │  ChromaDB    │
         │ (vector DB)  │
         └──────────────┘
```

## Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `backend/api/` | 26 REST route modules; each owns its domain |
| `backend/core/` | Config, auth/JWT, logging, middleware, exceptions, schemas |
| `backend/adapters/llm/` | Abstract LLM provider calls (OpenAI impl) |
| `backend/agents/` | Base agent runtime class |
| `backend/pipeline/` | 9-stage data pipeline with BaseStage + registry |
| `backend/knowledge/` | Crawl → parse → embed → store in ChromaDB |
| `backend/skills/` | Progressive Disclosure skill loading (3 levels) |
| `backend/memory/` | Redis-backed conversation memory |
| `backend/kernel/` | Kernel runtime abstraction |
| `frontend/src/app/` | Next.js App Router pages (28 routes) |
| `frontend/src/lib/api.ts` | Typed HTTP client wrapping fetch |

## Service Interactions

```
Agent → Skill Loader → Level1 metadata (always loaded)
                     → Level2 SKILL.md (on skill selection)
                     → Level3 resources/ (on demand)

Chat Request → ConversationAPI → LLM Adapter → OpenAI
                              → Memory (Redis)

Supervisor → Workflow Engine → Approval Gate → Human Decision
                             → Resume/Cancel

Pipeline → StageRegistry → Stage N → PipelineContext → Stage N+1
```

## Data Flow

1. Request enters FastAPI; `RequestIDMiddleware` assigns `X-Request-ID`
2. JWT validated via `core/security.py`
3. Route handler reads/writes in-memory store (transitioning to PostgreSQL)
4. Response wrapped in `APIResponse[T]` with `ResponseMeta`
5. Errors caught by global handlers → `APIError` JSON response

## External Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| OpenAI API | LLM inference | Yes |
| Anthropic API | LLM inference (planned) | No |
| PostgreSQL 15 | Persistent storage | Docker |
| Redis 7 | Session memory / caching | Docker |
| ChromaDB | Vector embeddings | Yes (local) |

## Deployment Model

- **Local dev:** `uvicorn backend.app.main:app --reload` + `npm run dev`
- **Docker:** `docker-compose up` — postgres + redis + backend
- **Production:** Non-root Docker image (uid 1000); health check on `/api/v1/health`
- **CI/CD:** GitHub Actions — lint → test → build on push to `main`/`develop`

## API Versioning

- All routes prefixed `/api/v1`
- Version controlled via `API_V1_PREFIX` env var
- Future versions use `/api/v2` pattern

## Key Patterns

- **Configuration:** Pydantic Settings; env vars with validation (`core/config.py`)
- **Logging:** Structured logs with request correlation IDs (`core/logging_config.py`)
- **Errors:** Consistent `APIError` model; centralized handlers (`core/exceptions.py`)
- **Security:** CORS, security headers, non-root Docker user, rate limiting
- **Registry Pattern:** Resources stored in typed in-memory registries (transitioning to DB)
