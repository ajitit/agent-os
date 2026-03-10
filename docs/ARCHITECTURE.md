# AgentOS Architecture

## Overview

AgentOS is an enterprise multi-agent AI platform with a clear separation between API, orchestration, and frontend.

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│  React 19 • Tailwind v4 • Vitest • Typed API Client             │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST /api/v1
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                        │
│  Config • Logging • Request ID • CORS • Error Handling          │
│  Health • Agents • Tasks • Chat (streaming)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │PostgreSQL│   │  Redis   │   │  Agent   │
        │ (future) │   │ (future) │   │ Runtime  │
        └──────────┘   └──────────┘   └──────────┘
```

## Backend Structure

```
backend/
├── api/           # Route handlers (agents, tasks, chat, health)
├── app/           # FastAPI app factory (main.py)
├── core/          # Config, logging, exceptions, middleware
└── tests/
```

### Key Patterns

- **Configuration**: Pydantic Settings; env vars with validation
- **Logging**: Structured logs with request correlation IDs
- **Errors**: Consistent APIError model; centralized handlers
- **Security**: CORS, security headers, non-root Docker user

## API Versioning

All routes are prefixed with `/api/v1`. Future versions will use `/api/v2`, etc.

## Deployment

- **Docker**: Multi-stage builds; health checks; dependency health checks
- **CI**: GitHub Actions for lint, test, build on push/PR
