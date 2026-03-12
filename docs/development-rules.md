# AgentOS — Development Rules

## Coding Standards

### Python (Backend)
- **Style:** Ruff (line-length=100); enforced via pre-commit + CI
- **Types:** MyPy strict mode — all functions must have type annotations
- **Imports:** Absolute imports only (`from backend.core.config import settings`)
- **Models:** Use Pydantic v2 for all request/response schemas
- **Async:** All route handlers must be `async def`

### TypeScript (Frontend)
- **Style:** ESLint with Next.js preset
- **Types:** Strict TypeScript — no implicit `any`
- **Components:** Functional components with named exports
- **API calls:** Use `src/lib/api.ts` client; never call `fetch` directly in components

## Architecture Rules

- **API-first:** All features must be accessible via `/api/v1` REST
- **No business logic in route handlers** — handlers call core modules
- **One file per domain** in `backend/api/` — do not add multiple domains per file
- **Adapter pattern for LLMs** — never call OpenAI SDK directly outside `backend/adapters/llm/`
- **Registry entries** must follow the registry module pattern (CRUD + list + get)
- **In-memory stores** via `backend/api/stores.py` — single source of truth until DB migration

## API Conventions

- **Response envelope:** All responses use `APIResponse[T]` from `core/schemas.py`
- **Error format:** All errors use `APIError` with `error`, `detail`, `request_id`, `code`
- **HTTP status codes:** 200 OK, 201 Created, 404 Not Found, 422 Validation, 500 Server Error
- **Route prefix:** `/api/v1/{resource}` (plural nouns)
- **IDs:** Use `str` UUIDs; generate with `str(uuid4())`
- **Pagination:** Not yet implemented; return full lists

## Folder Organization

```
backend/
  api/        # One file per resource domain
  core/       # Shared infra (config, auth, logging, exceptions)
  adapters/   # External service abstractions
  agents/     # Agent runtime
  pipeline/   # Data pipeline stages
  knowledge/  # Knowledge base operations
  skills/     # Skill loading system
  memory/     # Memory backends
  tests/      # Mirror src structure

frontend/src/
  app/        # Next.js App Router pages only
  components/ # Reusable React components
  lib/        # Utilities (api.ts, env.ts)
```

## Dependency Rules

- **Backend:** No circular imports between `api/` modules
- **Frontend:** `app/` pages may import from `components/` and `lib/` only
- **Shared state:** Use `stores.py` for in-memory state; no module-level globals elsewhere
- **External LLM:** Always go through `backend/adapters/llm/base.py` interface

## Error Handling

- Raise `AgentOSException` (from `core/exceptions.py`) for application errors
- Never swallow exceptions silently — log and re-raise or convert
- Validation errors automatically handled by FastAPI + Pydantic
- Frontend: handle HTTP errors in `lib/api.ts`; show user-facing messages

## Security Considerations

- All endpoints require JWT auth except `/health` and `/auth/login`
- Passwords hashed with bcrypt via `passlib`
- CORS origins configurable via `CORS_ORIGINS` env var
- Rate limiting: `RATE_LIMIT_PER_MINUTE=60` default
- Docker: non-root user (uid 1000); no secrets in image layers
- Never commit `.env` files; use `.env.example` as template

## Git Conventions

- Branch naming: `feature/`, `fix/`, `chore/` prefixes
- Commit format: `type(scope): description` (Conventional Commits)
- Pre-commit hooks: Ruff lint + format checks
- CI must pass before merge to `main`
