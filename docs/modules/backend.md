# Backend Module

## Purpose
FastAPI Python backend exposing all AgentOS capabilities via 26 REST route modules under `/api/v1`.

## Responsibilities
- Route all API requests with authentication, validation, and error handling
- Manage in-memory data stores (crews, agents, conversations, files, preferences)
- Coordinate LLM calls, pipeline execution, knowledge operations, and skill loading
- Issue JWT tokens; enforce rate limits; log with request correlation IDs

## Technology Stack
- **Framework:** FastAPI 0.115+, Uvicorn
- **Validation:** Pydantic v2
- **Auth:** PyJWT, passlib[bcrypt]
- **HTTP:** httpx, respx (testing)
- **Language:** Python 3.11+

## Key Directories
```
backend/
├── app/main.py        # FastAPI factory + router registration
├── api/               # 26 route modules (one per domain)
├── core/              # Shared infra
│   ├── config.py      # Pydantic Settings
│   ├── schemas.py     # APIResponse[T], ResponseMeta
│   ├── exceptions.py  # AgentOSException, handlers
│   ├── security.py    # JWT create/verify
│   ├── middleware.py  # RequestIDMiddleware
│   └── logging_config.py
└── tests/
```

## Important Files
| File | Role |
|------|------|
| `app/main.py` | App factory, CORS, middleware, exception handlers |
| `core/config.py` | All env var settings via `settings` singleton |
| `core/schemas.py` | `APIResponse[T]` response envelope |
| `core/exceptions.py` | `AgentOSException`, 3 global handlers |
| `api/stores.py` | All in-memory CRUD dictionaries |
| `api/agents.py` | Agent CRUD + tool assignment |
| `api/conversations.py` | Chat sessions + streaming |
| `api/supervisor.py` | Workflows + human approvals |
| `api/skills.py` | Progressive disclosure endpoints |

## Data Flow
```
Request → RequestIDMiddleware → Auth middleware
        → Route handler → stores.py / module
        → APIResponse[T] → JSON response

Error → AgentOSException handler → APIError JSON
      → RequestValidationError handler → 422
```

## External Dependencies
- `DATABASE_URL` — PostgreSQL (Docker; in-memory fallback)
- `REDIS_URL` — Redis (Docker)
- `OPENAI_API_KEY` — required for LLM calls
- `JWT_SECRET_KEY` — required for auth

## Development Rules
- All route handlers are `async def`
- Return `APIResponse[T]` for all success responses
- Raise `AgentOSException` for business logic errors
- Use `settings` (singleton) for all config access
- One route module per resource domain in `api/`
