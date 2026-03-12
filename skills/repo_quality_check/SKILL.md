# Repo Quality Check Skill

## Purpose
Use this skill to perform a full repository quality gate before a release, sprint close, or merge to `main`.
It validates three pillars in sequence: **Documentation**, **Issues & Code Health**, and **Test Suite**.
Produces a pass/fail report with a clear list of blockers.

## Context Sources
- `docs/project-context.md` — expected capabilities and module inventory
- `docs/module-map.md` — expected docs per module
- `docs/development-rules.md` — standards that must be met
- `docs/modules/testing.md` — test commands and coverage targets
- `docs/ai-context/backend-AI_CONTEXT.md` — backend file conventions
- `docs/ai-context/frontend-AI_CONTEXT.md` — frontend file conventions
- `skills/quality_compliance/resources/compliance_checklist.md` — code standards reference
- `skills/quality_compliance/resources/documentation_requirements.md` — docs completeness reference
- `skills/tester/resources/testing_strategy.md` — coverage targets

## Workflow

### Phase 1 — Documentation Audit
1. Load `docs/module-map.md`; list all modules
2. For each module, verify a corresponding `docs/modules/{module}.md` exists and is non-empty
3. Verify `docs/project-context.md`, `docs/ARCHITECTURE.md`, `docs/development-rules.md` are present
4. Verify all skills in `skills/` have `metadata.json` + `SKILL.md`
5. Verify `.env.example` lists every env var read by `backend/core/config.py`
6. Check `docs/modules/` freshness: key files referenced must exist in the repo
7. Record: docs present / docs missing / docs stale

### Phase 2 — Code & Issues Health Check
1. Run Ruff lint: `cd backend && ruff check .`
   - FAIL if any errors remain
2. Run MyPy: `cd backend && mypy backend/`
   - FAIL if type errors in `backend/api/`, `backend/core/`, `backend/adapters/`
3. Run ESLint: `cd frontend/agentos-ui && npm run lint`
   - FAIL if any errors remain
4. Scan for known anti-patterns via `resources/code_health_checks.md`
   - Hardcoded secrets, bare `except`, direct `fetch` in pages, missing `APIResponse[T]`
5. Check `TODO` / `FIXME` comments — flag any without a linked issue
6. Verify all routers in `backend/api/` are registered in `backend/app/main.py`
7. Record: lint status / type status / anti-patterns found / unresolved TODOs

### Phase 3 — Test Suite Validation
1. Run backend tests: `cd backend && pytest --tb=short -q`
   - FAIL if any test fails
   - Record: total / passed / failed / skipped
2. Run frontend tests: `cd frontend/agentos-ui && npm test -- --run`
   - FAIL if any test fails
3. Check coverage: `cd backend && pytest --cov=backend --cov-report=term-missing -q`
   - WARN if coverage for `backend/api/` < 70%
   - WARN if coverage for `backend/core/` < 80%
4. Verify test files exist for all route modules in `backend/api/`
5. Record: pass/fail, coverage %, missing test files

### Phase 4 — Final Report
Compile results from all three phases into the report format defined in
`resources/quality_report_template.md`. Assign overall status:
- **PASS** — all BLOCKERs resolved; WARNINGs documented
- **FAIL** — one or more BLOCKERs remain

## Rules
- A single BLOCKER in any phase = overall FAIL
- Lint errors are always BLOCKERs
- Failing tests are always BLOCKERs
- Missing module docs are WARNINGs (BLOCKER if this is a release gate)
- Coverage below target is a WARNING
- Stale docs are WARNINGs (flag but do not block)
- Never mark PASS if tests were not actually run
- Run phases in order — do not skip Phase 1 to save time

## Output Expectations
Structured quality report using `resources/quality_report_template.md`:
- Overall status: PASS / FAIL
- Phase-by-phase results with BLOCKER / WARNING / OK per check
- Actionable remediation list for every BLOCKER
- Coverage table for backend modules
- Checklist of missing or stale docs

## Resources
- `resources/quality_report_template.md` — report format and scoring
- `resources/code_health_checks.md` — anti-pattern scan patterns
- `resources/pre_release_checklist.md` — full release gate checklist
