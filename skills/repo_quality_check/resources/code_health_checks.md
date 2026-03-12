# Code Health Checks — AgentOS

## Anti-Pattern Scan Commands

### 1. Hardcoded Secrets (BLOCKER)
```bash
# Check for hardcoded API keys, secrets, passwords in source
grep -rn --include="*.py" --include="*.ts" --include="*.tsx" \
  -E "(api_key|secret_key|password|token)\s*=\s*['\"][^'\"]{8,}" \
  backend/ frontend/src/ \
  --exclude-dir=".venv" --exclude-dir="node_modules"
# Expected: 0 matches
```

### 2. Bare except Clauses (BLOCKER)
```bash
grep -rn --include="*.py" "except:" backend/
# Expected: 0 matches
# Fix: replace with `except Exception as e:` or specific exception type
```

### 3. Direct fetch() in Pages (BLOCKER)
```bash
grep -rn --include="*.tsx" --include="*.ts" \
  "fetch(" frontend/src/app/ frontend/src/components/
# Expected: 0 matches (all fetch calls must go through lib/api.ts)
```

### 4. Missing APIResponse[T] on Route Handlers (BLOCKER)
```bash
# Find route handlers that return raw dicts
grep -rn --include="*.py" \
  -E "^(async )?def (get_|post_|create_|update_|delete_|list_)" \
  backend/api/ | grep -v "APIResponse"
# Review each result — should all use APIResponse(data=...)
```

### 5. Synchronous Route Handlers (BLOCKER)
```bash
# Find non-async route handlers (must all be async def)
grep -rn --include="*.py" \
  -E "^def (get_|post_|create_|update_|delete_|list_|run_|start_)" \
  backend/api/
# Expected: 0 matches — all handlers must be `async def`
```

### 6. Unregistered Routers (BLOCKER)
```bash
# List all router modules
ls backend/api/*.py | grep -v "__init__\|stores" | \
  xargs -I{} basename {} .py

# Compare against registered routers in main.py
grep "include_router" backend/app/main.py | \
  grep -oP "(?<=from backend\.api\.)[\w]+"
# Every module in api/ must appear in main.py
```

### 7. TODO Without Issue Link (WARNING)
```bash
grep -rn --include="*.py" --include="*.ts" --include="*.tsx" \
  -E "# ?(TODO|FIXME|HACK)" \
  backend/ frontend/src/ | grep -v "#[0-9]\+"
# Flag any TODO not followed by an issue number like (issue-123)
```

### 8. print() in Production Code (WARNING)
```bash
grep -rn --include="*.py" "^\s*print(" backend/ \
  --exclude-dir="tests"
# Expected: 0 — use logging instead
```

### 9. Direct process.env Access Outside env.ts (WARNING)
```bash
grep -rn --include="*.ts" --include="*.tsx" \
  "process\.env\." \
  frontend/src/app/ frontend/src/components/
# Expected: 0 — all env vars via src/lib/env.ts
```

### 10. Missing Type Annotations (WARNING)
```bash
# Run MyPy with strict flag for targeted modules
cd backend && mypy backend/api/ backend/core/ \
  --ignore-missing-imports --strict
```

## Quick Health Score
Run all checks and count results:
```bash
BLOCKERS=0
WARNINGS=0

# Add +1 per violation type found
# Final score: BLOCKERS=0 → healthy; any BLOCKER → fix before merge
```
