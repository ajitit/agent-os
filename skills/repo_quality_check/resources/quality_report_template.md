# Repository Quality Report

## Header
```
Date:        [YYYY-MM-DD]
Branch:      [branch name]
Commit:      [short SHA]
Run by:      [skill / CI / manual]
Overall:     ✅ PASS  |  ❌ FAIL
```

---

## Phase 1 — Documentation Audit

| Check | Status | Notes |
|-------|--------|-------|
| `docs/project-context.md` exists | ✅ / ❌ | |
| `docs/ARCHITECTURE.md` exists | ✅ / ❌ | |
| `docs/development-rules.md` exists | ✅ / ❌ | |
| `docs/module-map.md` exists | ✅ / ❌ | |
| Module docs complete (1 per module) | ✅ / ⚠️ / ❌ | List missing: |
| All skills have metadata.json + SKILL.md | ✅ / ⚠️ / ❌ | List missing: |
| `.env.example` covers all config vars | ✅ / ⚠️ / ❌ | List missing vars: |
| No stale file references in docs | ✅ / ⚠️ | List stale refs: |

**Phase 1 Result:** ✅ PASS / ⚠️ WARNINGS / ❌ FAIL

### Documentation Blockers
- [ ] _(list each blocker with file path and fix action)_

### Documentation Warnings
- [ ] _(list each warning — not blocking but should be addressed)_

---

## Phase 2 — Code & Issues Health

| Check | Status | Notes |
|-------|--------|-------|
| `ruff check .` (backend) | ✅ / ❌ | Error count: |
| `mypy backend/` | ✅ / ❌ | Error count: |
| `npm run lint` (frontend) | ✅ / ❌ | Error count: |
| No hardcoded secrets in source | ✅ / ❌ | |
| No bare `except:` clauses | ✅ / ❌ | Count: |
| No direct `fetch` in page components | ✅ / ❌ | Files: |
| All route handlers return `APIResponse[T]` | ✅ / ⚠️ | Files missing: |
| All routers registered in `app/main.py` | ✅ / ❌ | Missing: |
| No unresolved TODO without issue link | ✅ / ⚠️ | Count: |

**Phase 2 Result:** ✅ PASS / ⚠️ WARNINGS / ❌ FAIL

### Code Health Blockers
- [ ] _(file:line — issue — fix)_

### Code Health Warnings
- [ ] _(file:line — issue — suggested fix)_

---

## Phase 3 — Test Suite

### Backend (pytest)
```
Command:   pytest --tb=short -q
Result:    [PASSED / FAILED]

Total:     X tests
Passed:    X
Failed:    X  ← BLOCKER if > 0
Skipped:   X
Errors:    X  ← BLOCKER if > 0
```

### Backend Coverage
```
Command:   pytest --cov=backend --cov-report=term-missing -q
```

| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| `backend/api/` | X% | 70% | ✅ / ⚠️ |
| `backend/core/` | X% | 80% | ✅ / ⚠️ |
| `backend/adapters/` | X% | 70% | ✅ / ⚠️ |
| `backend/pipeline/` | X% | 60% | ✅ / ⚠️ |

### Frontend (Vitest)
```
Command:   npm test -- --run
Result:    [PASSED / FAILED]

Total:     X tests
Passed:    X
Failed:    X  ← BLOCKER if > 0
```

### Missing Test Files
| Source File | Test File | Status |
|-------------|-----------|--------|
| `backend/api/agents.py` | `tests/unit/api/test_agents.py` | ✅ / ⚠️ Missing |

**Phase 3 Result:** ✅ PASS / ⚠️ WARNINGS / ❌ FAIL

### Test Blockers
- [ ] _(test name — failure reason — fix)_

---

## Summary

### All Blockers (must fix before PASS)
| # | Phase | Location | Issue | Fix |
|---|-------|----------|-------|-----|
| 1 | | | | |

### All Warnings (should fix soon)
| # | Phase | Location | Issue | Priority |
|---|-------|----------|-------|---------|
| 1 | | | | HIGH / MED / LOW |

---

## Final Verdict
```
┌─────────────────────────────────────┐
│  Overall Status:  ✅ PASS / ❌ FAIL  │
│  Blockers:        X                  │
│  Warnings:        X                  │
│  Ready to merge:  YES / NO           │
└─────────────────────────────────────┘
```
