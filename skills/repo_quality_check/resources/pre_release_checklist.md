# Pre-Release / Pre-Merge Checklist — Vishwakarma

Use this checklist before merging to `main` or cutting a release tag.
Every BLOCKER item must be ✅ before proceeding.

---

## 1. Documentation _(run: Phase 1 of Repo Quality Check)_

| Item | Severity | Status |
|------|----------|--------|
| `docs/project-context.md` reflects current capabilities | BLOCKER | ☐ |
| `docs/ARCHITECTURE.md` reflects current system layers | BLOCKER | ☐ |
| `docs/module-map.md` lists all current modules | BLOCKER | ☐ |
| Every module in `backend/api/` has a `docs/modules/*.md` | WARNING | ☐ |
| Every skill in `skills/` has `metadata.json` + `SKILL.md` | WARNING | ☐ |
| `.env.example` documents all required env vars | BLOCKER | ☐ |
| No docs reference files that no longer exist | WARNING | ☐ |
| `CHANGELOG` or release notes updated (if release) | BLOCKER | ☐ |

---

## 2. Code Quality _(run: Phase 2 of Repo Quality Check)_

| Item | Severity | Status |
|------|----------|--------|
| `ruff check .` passes with 0 errors | BLOCKER | ☐ |
| `mypy backend/` passes with 0 errors (api/, core/, adapters/) | BLOCKER | ☐ |
| `npm run lint` passes with 0 errors | BLOCKER | ☐ |
| No hardcoded secrets, API keys, or passwords | BLOCKER | ☐ |
| No bare `except:` clauses | BLOCKER | ☐ |
| No direct `fetch()` calls outside `lib/api.ts` | BLOCKER | ☐ |
| All route handlers are `async def` | BLOCKER | ☐ |
| All route handlers return `APIResponse[T]` | BLOCKER | ☐ |
| All new routers registered in `app/main.py` | BLOCKER | ☐ |
| No `print()` statements outside tests | WARNING | ☐ |
| No unresolved `TODO` without issue link | WARNING | ☐ |

---

## 3. Tests _(run: Phase 3 of Repo Quality Check)_

| Item | Severity | Status |
|------|----------|--------|
| `pytest` — 0 failures, 0 errors | BLOCKER | ☐ |
| `npm test -- --run` — 0 failures | BLOCKER | ☐ |
| `backend/api/` coverage ≥ 70% | WARNING | ☐ |
| `backend/core/` coverage ≥ 80% | WARNING | ☐ |
| New route handlers have unit tests | WARNING | ☐ |
| New business logic has unit tests | BLOCKER | ☐ |
| Integration tests pass (if Docker available) | WARNING | ☐ |

---

## 4. Security _(reference: security_testing_expert skill)_

| Item | Severity | Status |
|------|----------|--------|
| No secrets committed to git (`git log` check) | BLOCKER | ☐ |
| All non-public endpoints require JWT | BLOCKER | ☐ |
| CORS restricted to known origins (not `*`) | BLOCKER | ☐ |
| Docker image runs as non-root (uid 1000) | BLOCKER | ☐ |
| `pip audit` — no critical CVEs | WARNING | ☐ |
| `npm audit` — no critical CVEs | WARNING | ☐ |

---

## 5. Functional Validation _(reference: end_user skill)_

| Item | Severity | Status |
|------|----------|--------|
| Core flows work end-to-end (create agent → chat) | BLOCKER | ☐ |
| New feature works as described in acceptance criteria | BLOCKER | ☐ |
| No UI regressions on existing pages | WARNING | ☐ |
| Error states show user-friendly messages | WARNING | ☐ |

---

## 6. Infrastructure _(reference: infra module)_

| Item | Severity | Status |
|------|----------|--------|
| `docker-compose up` builds without errors | BLOCKER | ☐ |
| Health check `GET /api/v1/health` returns 200 | BLOCKER | ☐ |
| All required env vars documented in `.env.example` | BLOCKER | ☐ |
| CI pipeline passes on target branch | BLOCKER | ☐ |

---

## Release Gate Decision

```
Count BLOCKERs remaining: ___

If BLOCKERs = 0  →  ✅ APPROVED TO MERGE / RELEASE
If BLOCKERs > 0  →  ❌ BLOCKED — resolve all blockers first

Warning count: ___  (document in release notes if > 5)
```

### Sign-off
```
Checked by:   [name / agent]
Date:         [YYYY-MM-DD]
Branch:       [branch]
Commit:       [SHA]
Decision:     APPROVED / BLOCKED
```
