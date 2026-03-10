# Supervisor + Human-in-the-Loop

## Overview

The Supervisor pattern coordinates multi-agent workflows and supports **Human-in-the-Loop (HITL)** at decision points. The supervisor delegates tasks to agents and can pause execution for human review, approval, or modification.

## Flow

1. **Start workflow** – `POST /api/v1/supervisor/workflows` with a goal
2. **Supervisor delegates** – Assigns work to agents based on goal
3. **Pause for approval** – At checkpoints, `POST /api/v1/supervisor/workflows/{id}/pause` creates an approval request
4. **Human responds** – `POST /api/v1/supervisor/approvals/{id}/respond` with `approve`, `reject`, or `modify`
5. **Resume or branch** – Workflow continues on approve; stops or adapts on reject/modify

## API

| Endpoint | Purpose |
| -------- | ------- |
| `GET /api/v1/supervisor/workflows` | List all workflows |
| `POST /api/v1/supervisor/workflows` | Start a new workflow |
| `GET /api/v1/supervisor/workflows/{id}` | Get workflow status + approval history |
| `POST /api/v1/supervisor/workflows/{id}/pause` | Create approval checkpoint (HITL) |
| `GET /api/v1/supervisor/approvals` | List pending approvals (HITL queue) |
| `GET /api/v1/supervisor/approvals/{id}` | Get approval details |
| `POST /api/v1/supervisor/approvals/{id}/respond` | Submit human decision |

## Human Decisions

| Decision | Effect |
| -------- | ------ |
| `approve` | Workflow resumes |
| `reject` | Workflow stops or retries |
| `modify` | Requires `feedback` or `modification`; workflow adapts and continues |

## Example

```bash
# Start workflow
curl -X POST http://localhost:8000/api/v1/supervisor/workflows \
  -H "Content-Type: application/json" \
  -d '{"goal": "Research EV battery market"}'

# Supervisor pauses; get pending approvals
curl http://localhost:8000/api/v1/supervisor/approvals

# Human approves
curl -X POST http://localhost:8000/api/v1/supervisor/approvals/{approval_id}/respond \
  -H "Content-Type: application/json" \
  -d '{"decision": "approve"}'
```
