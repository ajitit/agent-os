# AgentOS v1.0

## Enterprise Multi-Agent AI Operating System

AgentOS is a **full-stack AI agent platform** designed to run autonomous multi-agent workflows using modern AI infrastructure. It provides orchestration, crews, agents, MCP tools, conversations, storage, and a web console to build and operate intelligent agents.

---

## Key Capabilities

- **Supervisor + Human-in-the-Loop** – Coordinate multi-agent workflows; pause for human approval
- **Progressive Disclosure Skills** – Load instructions/resources on-demand, framework agnostic
- **Crews & Agents** – Create and manage agent crews with tool assignments
- **MCP Servers & Tools** – Model Context Protocol server and tool management
- **Conversations** – Multi-turn chat with streaming support
- **Storage** – File upload, download, presigned URLs
- **Tasks** – Goal-based task creation and queuing
- **Health & Observability** – Request tracing, structured logging

---

## Technology Stack

| Layer        | Technologies                          |
| ------------ | ------------------------------------- |
| Backend      | Python 3.11+, FastAPI, Pydantic       |
| Frontend     | Next.js 16, React 19, Tailwind v4     |
| Data         | PostgreSQL, Redis (Docker)            |
| Infrastructure | Docker, Docker Compose              |

---

## Repository Structure

```
agent-os/
├── backend/
│   ├── api/              # Route handlers
│   ├── app/
│   ├── core/
│   ├── skills/           # Progressive disclosure loader (Level 1–3)
│   └── tests/
├── skills/               # Skill definitions (metadata.json, SKILL.md, resources/)
│   └── web_research/     # Example skill
├── frontend/agentos-ui/
├── docs/skills/          # Skill system docs
├── docker-compose.yml
└── .env.example
```

---

## API Endpoints

All API routes are prefixed with `/api/v1`. Interactive docs: **http://localhost:8000/api/docs**

### Crews & Agents

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | /api/v1/crews | Get all crews |
| POST | /api/v1/crews | Create a crew |
| GET | /api/v1/crews/{crew_id} | Get a crew |
| PUT | /api/v1/crews/{crew_id} | Update a crew |
| DELETE | /api/v1/crews/{crew_id} | Delete a crew |
| GET | /api/v1/agents | Get all agents |
| POST | /api/v1/agents | Create an agent |
| GET | /api/v1/agents/{agent_id} | Get an agent |
| PUT | /api/v1/agents/{agent_id} | Update an agent |
| DELETE | /api/v1/agents/{agent_id} | Delete an agent |
| POST | /api/v1/agents/{agent_id}/tools/{tool_id} | Assign tool to agent |
| DELETE | /api/v1/agents/{agent_id}/tools/{tool_id} | Remove tool from agent |

### MCP Servers & Tools

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | /api/v1/mcp-servers | Get all MCP servers |
| POST | /api/v1/mcp-servers | Create MCP server |
| GET | /api/v1/mcp-servers/{server_id} | Get MCP server |
| PUT | /api/v1/mcp-servers/{server_id} | Update MCP server |
| DELETE | /api/v1/mcp-servers/{server_id} | Delete MCP server |
| GET | /api/v1/mcp-servers/{server_id}/tools | Get tools |
| POST | /api/v1/mcp-servers/{server_id}/tools | Add tool |
| DELETE | /api/v1/mcp-servers/{server_id}/tools/{tool_id} | Remove tool |

### Conversations & Chat

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | /api/v1/conversations | Get all conversations |
| POST | /api/v1/conversations | Create conversation |
| GET | /api/v1/conversations/{id} | Get conversation |
| PUT | /api/v1/conversations/{id} | Update conversation |
| DELETE | /api/v1/conversations/{id} | Delete conversation |
| GET | /api/v1/conversations/{id}/messages | Get messages |
| POST | /api/v1/conversations/{id}/messages | Add message |
| POST | /api/v1/conversations/{id}/chat | Send message, get response |
| POST | /api/v1/conversations/{id}/chat/stream | Send message, stream response |

### Storage

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | /api/v1/storage/upload | Upload file |
| GET | /api/v1/storage/files/{key} | Download file |
| GET | /api/v1/storage/urls/{key} | Get presigned URL |
| DELETE | /api/v1/storage/files/{key} | Delete file |
| GET | /api/v1/storage/files | List files |

### Supervisor & Human-in-the-Loop

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | /api/v1/supervisor/workflows | List workflows |
| POST | /api/v1/supervisor/workflows | Start workflow |
| GET | /api/v1/supervisor/workflows/{id} | Get workflow + approvals |
| POST | /api/v1/supervisor/workflows/{id}/pause | Pause for human approval |
| GET | /api/v1/supervisor/approvals | List pending approvals |
| GET | /api/v1/supervisor/approvals/{id} | Get approval details |
| POST | /api/v1/supervisor/approvals/{id}/respond | Submit human decision |

### Skills (Progressive Disclosure)

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | /api/v1/skills | List metadata (Level 1) |
| GET | /api/v1/skills/{skill_id} | Get full skill + instructions (Level 2) |
| GET | /api/v1/skills/{skill_id}/resources/{path} | Get resource file (Level 3) |

See [docs/skills/QUICKSTART.md](docs/skills/QUICKSTART.md) for the Progressive Disclosure pattern.

### Tasks & Health

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | /api/v1/tasks | Create task |
| GET | /api/v1/health | Health check |
| GET | /api/v1/health/ready | Readiness check |
| GET | /api/health | Health alias (no version prefix) |

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for PostgreSQL, Redis)

### 1. Backend Setup

From project root:

```bash
python -m venv backend/venv

# Windows
backend\venv\Scripts\activate

# Linux/macOS
source backend/venv/bin/activate

pip install -r backend/requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend/agentos-ui
npm install
```

### 3. Environment

```bash
cp .env.example .env
# Edit .env as needed
```

---

## Running the Project

### Option A: Docker (full stack)

```bash
docker compose up
```

- Backend: http://localhost:8000  
- API docs: http://localhost:8000/api/docs

### Option B: Local development

**Terminal 1 – Backend**

```bash
uvicorn backend.app.main:app --reload
```

**Terminal 2 – Frontend**

```bash
cd frontend/agentos-ui
npm run dev
```

**Terminal 3 – Infrastructure (optional)**

```bash
docker compose up postgres redis
```

---

## Testing

### Backend
# Ensure venv is activated and deps installed

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt

pytest tests/ -v
```

### Frontend

```bash
cd frontend/agentos-ui
npm install
npm run lint
npm run test
npm run build
npm run dev
```

---

## Roadmap

- Visual agent workflow builder
- LangGraph/LangChain integration
- PostgreSQL persistence
- Redis-backed memory
- RAG knowledge retrieval

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and code standards.

---

## License

MIT License

---

## Author

Ajit Kumar
