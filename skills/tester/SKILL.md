# Tester Skill

## Purpose
Use this skill when creating test cases, validating coverage, writing functional or regression tests, or debugging failing tests in AgentOS.

## Context Sources
- `docs/modules/testing.md` — test structure, frameworks, run commands, mocking strategy
- `docs/ai-context/backend-AI_CONTEXT.md` — backend data flow and API contracts
- `docs/ai-context/frontend-AI_CONTEXT.md` — frontend component structure
- `backend/tests/conftest.py` — shared pytest fixtures
- `frontend/agentos-ui/vitest.config.ts` — Vitest configuration

## Workflow
1. **Identify target** — Determine what is being tested (unit / integration / e2e)
2. **Load context** — Read module doc for the component under test
3. **Review existing tests** — Check `tests/unit/` or `tests/integration/` for patterns
4. **Use templates** — Reference `resources/test_case_templates.md`
5. **Write test** — Follow `resources/testing_strategy.md` for structure
6. **Mock correctly** — Use `respx` for HTTP, fixtures for store state
7. **Assert contracts** — Validate `APIResponse[T]` shape and HTTP status codes
8. **Run and verify** — Confirm test passes; check coverage impact

## Rules
- Backend: all async tests use `@pytest.mark.asyncio`
- Mock HTTP with `respx` — never monkeypatch `requests`/`httpx` directly
- Do not mock in-memory stores — use real store state via fixtures
- Frontend: use `@testing-library/react` — no direct DOM manipulation
- Integration tests require Docker services (postgres + redis)
- Test file names: `test_{module}.py` for backend, `{component}.test.tsx` for frontend
- One assertion concept per test function

## Output Expectations
- Test file(s) placed in correct directory mirroring source structure
- All tests pass with `pytest` / `npm test`
- Coverage report shows improved or maintained coverage
- Edge cases and error paths covered (not just happy path)

## Resources
- `resources/test_case_templates.md` — templates for unit, integration, API tests
- `resources/testing_strategy.md` — AgentOS testing strategy and priorities
