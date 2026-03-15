# Service Decomposition Patterns

## Current State (Monolith)
Vishwakarma backend is a single FastAPI service. All modules in one process.

## Decomposition Candidates (Future)
| Service | Trigger | Boundary |
|---------|---------|---------|
| Pipeline Service | Independent scaling | `backend/pipeline/` |
| Knowledge Service | High storage/compute | `backend/knowledge/` |
| Agent Runtime | Isolated execution | `backend/agents/` |
| Notification Service | Async event delivery | Supervisor approvals |

## When to Decompose
- Module has independent scaling needs
- Module has different deployment lifecycle
- Module team ownership is distinct
- Communication between modules is already async

## Communication Patterns
- Synchronous: REST (current) → keep for request/response
- Asynchronous: Redis pub/sub or message queue → use for pipeline, notifications
- Streaming: SSE (current for chat) → WebSocket for real-time agent status

## Data Ownership Rule
Each service owns its data. Cross-service reads use APIs, not shared DBs.
