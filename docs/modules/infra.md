# Infrastructure Module

## Purpose
Deployment environment, containerization, CI/CD pipeline, environment configuration, and secrets management for Vishwakarma.

## Deployment Environment

### Local Development
```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000

# Frontend
cd frontend/agentos-ui
npm install && npm run dev   # http://localhost:3000
```

### Docker (Full Stack)
```bash
docker-compose up            # Starts postgres + redis + backend
```

## Containerization

### Backend Dockerfile (`backend/Dockerfile`)
- **Base:** `python:3.11-slim` (multi-stage build)
- **Security:** Non-root user `uid=1000`
- **Healthcheck:** `GET /api/v1/health` every 30s
- **Startup:** `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`

### docker-compose.yml Services
| Service | Image | Port | Notes |
|---------|-------|------|-------|
| `postgres` | postgres:15-alpine | 5432 | Persistent volume |
| `redis` | redis:7-alpine | 6379 | Ephemeral |
| `backend` | local build | 8000 | Depends on postgres+redis health |

## CI/CD Pipeline (`.github/workflows/ci.yml`)

**Triggers:** Push to `main`/`develop`, Pull Requests

### Backend Job
1. Python 3.11 setup + pip cache
2. `pip install -r requirements.txt`
3. `ruff check .` — linting
4. `pytest` — full test suite

### Frontend Job
1. Node 20 setup + npm cache
2. `npm ci` — install dependencies
3. `npm run lint` — ESLint
4. `npm test` — Vitest
5. `npm run build` — Next.js production build

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `APP_NAME` | No | App display name (default: Vishwakarma) |
| `ENVIRONMENT` | No | `development`/`production` |
| `API_V1_PREFIX` | No | Route prefix (default: `/api/v1`) |
| `DATABASE_URL` | Docker | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Docker | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Yes | Secret for JWT signing |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (planned) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `RATE_LIMIT_PER_MINUTE` | No | Default: 60 |
| `SKILLS_DIR` | No | Path to skills directory (default: `skills`) |
| `NEXT_PUBLIC_API_URL` | Yes (FE) | Backend URL for frontend |

## Secrets Management
- Copy `.env.example` → `.env` (never commit `.env`)
- Secrets never baked into Docker layers
- CI secrets stored in GitHub Actions Secrets

## Pre-commit Hooks (`.pre-commit-config.yaml`)
- Ruff lint + format on Python files
- Runs automatically on `git commit`

## Configuration Strategy
- Backend: Pydantic `Settings` class in `core/config.py` — reads env vars with validation
- Frontend: `src/lib/env.ts` — wraps `process.env.NEXT_PUBLIC_*`
- All required env vars fail fast at startup if missing
