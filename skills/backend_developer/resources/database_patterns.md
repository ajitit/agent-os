# Database Patterns

## Current: In-Memory Stores
All data stored in `backend/api/stores.py` dicts. Fast to develop; lost on restart.

```python
# stores.py structure
_agents: dict[str, dict] = {}         # keyed by str UUID
_agent_tools: dict[str, set] = {}     # agent_id → set of tool_ids
```

## Migration Path to PostgreSQL
When migrating a resource from in-memory to PostgreSQL:

1. Define SQLAlchemy model in `backend/models/{resource}.py`
2. Create Alembic migration
3. Replace `_resource[id] = data` with `session.add(ResourceModel(**data))`
4. Replace `list(_resource.values())` with `session.query(ResourceModel).all()`
5. Keep `APIResponse[T]` shape identical — frontend must not need changes

## Redis Usage (Planned)
- Conversation memory: `backend/memory/redis_memory.py`
- Key pattern: `conversation:{id}:messages` → list of message dicts
- TTL: 24h for active conversations

## ChromaDB (Knowledge)
- Collection per knowledge domain
- Embedding model: sentence-transformers
- Similarity search returns top-k chunks with metadata
- Access via `backend/knowledge/vector.py`

## Environment Config
```
DATABASE_URL=postgresql://user:pass@localhost:5432/agentos
REDIS_URL=redis://localhost:6379/0
```
Both injected via `backend/core/config.py` Settings.
