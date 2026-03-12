# Agents Module

## Purpose
Manages AI agent definitions, crew groupings, multi-agent orchestration, and human-in-the-loop supervision.

## Responsibilities
- CRUD for agents and crews
- Assign tools/skills to individual agents
- Coordinate multi-agent workflows via Supervisor
- Support human approval gates (pause/resume/cancel)
- Manage plans and progressive skill disclosure per agent

## Technology Stack
- Python 3.11+, FastAPI
- `backend/agents/base_agent.py` — BaseAgent class
- LangChain / LangGraph (planned for orchestration)

## Key Directories
```
backend/
├── agents/base_agent.py     # BaseAgent runtime class
├── api/agents.py            # Agent CRUD + tool assignment
├── api/crews.py             # Crew CRUD
├── api/supervisor.py        # Workflow + HITL approvals
├── api/workflows.py         # Workflow management
├── api/plans.py             # Plan CRUD
└── core/planning/planner.py # Planning engine
```

## Important Files
| File | Role |
|------|------|
| `agents/base_agent.py` | Base class for all agents |
| `api/agents.py` | POST/GET/PUT/DELETE `/agents` + tool assignment |
| `api/crews.py` | POST/GET/PUT/DELETE `/crews` |
| `api/supervisor.py` | Workflow lifecycle + approval endpoints |
| `api/plans.py` | Plan creation and retrieval |
| `core/planning/planner.py` | Planner logic |

## Data Flow
```
AgentCreate → POST /agents → stores._agents dict → agent_id

Workflow start → supervisor → pause on approval needed
             → POST /supervisor/approvals/{id}/respond
             → resume / cancel
```

## Agent Schema
```python
AgentCreate:
  name: str
  description: str
  role: str
  model: str               # LLM model ID
  system_prompt: str
  temperature: float
  assigned_tools: list[str]
```

## External Dependencies
- `api/stores.py` — `_agents`, `_crews`, `_agent_tools` dicts
- LLM Adapters (`adapters/llm/`) for execution
- Skills module for progressive disclosure

## Development Rules
- Agents are stateless config; runtime state in conversation/memory
- Tool assignment via `PUT /agents/{id}/tools/{tool_id}`
- Supervisor must validate workflow state transitions
