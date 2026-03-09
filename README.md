# AgentOS v1.0

Enterprise-style multi-agent AI platform scaffold.

## Stack
- FastAPI backend
- LangGraph orchestration
- Redis memory
- PostgreSQL + pgvector
- Next.js frontend
- Docker deployment

## Run

Backend:
uvicorn backend.app.main:app --reload

Frontend:
cd frontend/agentos-ui
npm install
npm run dev
