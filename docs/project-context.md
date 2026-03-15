# Vishwakarma — Project Context

## Project Name
Vishwakarma v1.0 — Enterprise Multi-Agent AI Operating System

## Purpose
Platform for building, orchestrating, and supervising AI agents at enterprise scale. Provides a structured runtime for multi-agent workflows with human oversight.

## Problem Solved
- Eliminates manual coordination of multiple AI agents
- Provides human-in-the-loop approval gates for critical decisions
- Manages skills/tools/knowledge as versioned, composable registry entries
- Unifies LLM providers behind a single adapter interface

## Core Capabilities
- **Crews & Agents** — Organize agents into crews; assign tools/skills per agent
- **Progressive Disclosure Skills** — 3-level lazy-loading skill system (metadata → instructions → resources)
- **Supervisor + HITL** — Pause workflows for human approvals before proceeding
- **9-Stage Pipeline** — Extract → Filter → Map → Mask → Review → Route data
- **Multi-LLM** — Adapter pattern over OpenAI (Anthropic planned)
- **Knowledge Base** — ChromaDB vector store with web crawler + document parser
- **Registry System** — Manage models, tools, skills, MCP servers, data sources, remote APIs, knowledge graphs

## Technology Stack
| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, FastAPI 0.115+, Pydantic v2 |
| Frontend | Next.js 16, React 19, Tailwind v4 |
| Data | PostgreSQL 15, Redis 7 (planned), in-memory stores (current) |
| Vector DB | ChromaDB + sentence-transformers |
| Auth | JWT (PyJWT + passlib[bcrypt]) |
| Infra | Docker, Docker Compose, GitHub Actions |

## Repository Structure
```
/
├── backend/          # FastAPI Python backend
├── frontend/agentos-ui/  # Next.js frontend
├── skills/           # Skill definitions (Progressive Disclosure)
├── docs/             # Architecture & guides
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Key Design Principles
- **API-first** — All features exposed via `/api/v1` REST endpoints
- **Registry pattern** — Resources (tools, models, skills) stored in registries
- **Adapter pattern** — LLM providers abstracted behind `LLMBase`
- **Progressive loading** — Skills load only what the agent needs
- **Context isolation** — Each module independently testable
