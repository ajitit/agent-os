# AgentOS — Module Map

## Quick Reference

| Module | Purpose | Primary Directory | Related Modules |
|--------|---------|-------------------|-----------------|
| UI | Next.js frontend | `frontend/agentos-ui/src/` | Backend API |
| Backend | FastAPI REST API | `backend/` | All modules |
| Agents | Agent runtime & config | `backend/agents/`, `backend/api/agents.py` | LLM, Skills |
| LLM | LLM provider adapters | `backend/adapters/llm/` | Agents, Chat |
| Pipeline | 9-stage data pipeline | `backend/pipeline/` | Knowledge |
| Knowledge | Vector knowledge base | `backend/knowledge/` | Pipeline, LLM |
| Skills | Progressive disclosure | `backend/skills/`, `skills/` | Agents |
| Supervisor | HITL workflow control | `backend/api/supervisor.py` | Agents, Crews |
| Registry | Resource registries | `backend/api/*_registry.py` | All |
| Testing | Test suites | `backend/tests/`, `frontend/.../test*` | All |
| Infra | Docker, CI/CD, config | `/docker-compose.yml`, `/.github/` | All |

---

## Module Details

### UI Module
- **Directory:** `frontend/agentos-ui/src/`
- **Key Files:**
  - `app/layout.tsx` — root layout + Nav
  - `app/page.tsx` — home page
  - `lib/api.ts` — HTTP client
  - `lib/env.ts` — env config
  - `components/Nav.tsx` — navigation
  - `components/ModelSelector.tsx` — LLM model picker
- **Pages (28):** chat, agents, crews, registry/*, settings/*, plans, workflows, marketplace, observability, audit, analytics, evaluations, profile
- **Dependencies:** Next.js 16, React 19, Tailwind v4, recharts, react-markdown

### Backend Module
- **Directory:** `backend/`
- **Key Files:**
  - `app/main.py` — FastAPI factory + 27 routers
  - `core/config.py` — Pydantic Settings
  - `core/schemas.py` — APIResponse[T] envelope
  - `core/exceptions.py` — AgentOSException + handlers
  - `core/security.py` — JWT auth
  - `api/stores.py` — in-memory CRUD store
- **Dependencies:** FastAPI, Pydantic v2, PyJWT, passlib

### Agents Module
- **Directory:** `backend/agents/`, `backend/api/agents.py`
- **Key Files:**
  - `agents/base_agent.py` — BaseAgent class
  - `api/agents.py` — CRUD + tool assignment endpoints
  - `api/crews.py` — crew management
- **Data:** AgentCreate {name, role, model, system_prompt, temperature, tools}
- **Dependencies:** LLM Adapters, Skills, Stores

### LLM Module
- **Directory:** `backend/adapters/llm/`
- **Key Files:**
  - `adapters/llm/base.py` — abstract LLMBase interface
  - `adapters/llm/openai.py` — OpenAI implementation
  - `api/llm.py` — model listing endpoint
  - `api/model_registry.py` — model registry CRUD
- **Config:** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` env vars

### Pipeline Module
- **Directory:** `backend/pipeline/`
- **Key Files:**
  - `pipeline/base.py` — BaseStage abstract class
  - `pipeline/orchestrator.py` — PipelineOrchestrator
  - `pipeline/models.py` — PipelineContext, PipelineResult
  - `pipeline/stages/` — 6 stage implementations
  - `api/pipeline.py` — pipeline endpoints
- **Stages:** extract → filter → map → mask → review → routing

### Knowledge Module
- **Directory:** `backend/knowledge/`
- **Key Files:**
  - `knowledge/manager.py` — KnowledgeManager
  - `knowledge/crawler.py` — web crawler
  - `knowledge/parser.py` — document parser
  - `knowledge/vector.py` — ChromaDB vector ops
  - `knowledge/extractor.py` — information extraction
- **Dependencies:** ChromaDB, sentence-transformers, beautifulsoup4, pypdf

### Skills Module
- **Directory:** `backend/skills/`, `skills/`
- **Key Files:**
  - `skills/loader.py` — SkillLoader (3-level loading)
  - `skills/models.py` — SkillMetadata, Skill, SkillResource
  - `api/skills.py` — progressive disclosure endpoints
  - `skills/web_research/` — example skill
- **Pattern:** metadata.json → SKILL.md → resources/

### Supervisor Module
- **Directory:** `backend/api/supervisor.py`, `backend/core/planning/`
- **Key Files:**
  - `api/supervisor.py` — workflow + approval endpoints
  - `core/planning/planner.py` — planning engine
  - `api/workflows.py` — workflow management
  - `api/plans.py` — plan CRUD
- **HITL Flow:** start → pause → human approval → resume/cancel

### Registry Modules
- **Directory:** `backend/api/*_registry.py`
- **Files:** `skill_registry.py`, `model_registry.py`, `tool_registry.py`, `knowledge_graphs.py`, `remote_apis.py`, `data_sources.py`, `mcp_servers.py`
- **Pattern:** All follow CRUD: create, list, get, update, delete

### Testing Module
- **Backend:** `backend/tests/` — pytest + pytest-asyncio
- **Frontend:** `frontend/agentos-ui/` — vitest + @testing-library/react
- **Key Files:** `conftest.py`, `test_api.py`, `integration/api/test_llm.py`

### Infra Module
- **Files:** `docker-compose.yml`, `backend/Dockerfile`, `.github/workflows/ci.yml`, `.env.example`, `.pre-commit-config.yaml`
- **Services:** PostgreSQL 15, Redis 7, FastAPI backend
