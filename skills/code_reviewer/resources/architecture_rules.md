# Vishwakarma Architecture Rules for Code Review

## Layer Boundary Rules
```
ALLOWED:
  frontend/src/app/ → frontend/src/lib/api.ts → /api/v1/*
  backend/api/      → backend/core/
  backend/api/      → backend/adapters/
  backend/api/      → backend/api/stores.py
  backend/pipeline/ → backend/knowledge/

FORBIDDEN:
  backend/core/     → backend/api/      (core must not import api)
  backend/api/X     → backend/api/Y     (no cross-api imports)
  frontend/         → backend/ directly  (only via HTTP)
```

## Store Rules
- All state lives in `api/stores.py`
- No module-level mutable state outside stores.py
- Store dicts keyed by `str(uuid4())`
- Deletion: remove key from dict (no soft-delete for in-memory)

## Response Contract Rules
- `GET /resources` → `APIResponse[list[dict]]`
- `POST /resources` → `APIResponse[dict]` with 201 status
- `GET /resources/{id}` → `APIResponse[dict]` or 404
- `PUT /resources/{id}` → `APIResponse[dict]` or 404
- `DELETE /resources/{id}` → `APIResponse[dict]` with message

## Router Registration Rule
Every new `api/{resource}.py` module must be:
1. Imported in `backend/app/main.py`
2. Registered with `app.include_router()`
3. Added to `docs/module-map.md`
