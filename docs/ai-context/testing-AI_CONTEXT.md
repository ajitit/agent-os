# Testing AI Context — Vishwakarma

## Module Purpose
Backend uses Pytest; frontend uses Vitest. Tests mirror source structure.

## Key Files

### Backend
- `tests/conftest.py` — shared fixtures
- `tests/test_api.py` — general API smoke tests
- `tests/unit/adapters/test_openai.py` — LLM adapter unit tests
- `tests/unit/api/test_plans.py` — plans API tests
- `tests/unit/pipeline/test_pipeline.py` — pipeline stage tests
- `tests/integration/api/test_llm.py` — LLM integration tests

### Frontend
- `src/app/page.test.tsx` — home page component test
- `vitest.config.ts` — test runner config
- `vitest.setup.ts` — jest-dom setup

## Data Flow (Test Execution)
```
pytest → conftest fixtures → test functions → assert APIResponse
vitest → vitest.setup.ts → component render → assert DOM
```

## Run Commands
```bash
# Backend
pytest                       # all
pytest tests/unit/           # unit only
pytest --cov=backend         # with coverage

# Frontend
npm test                     # all
npm run test:watch            # watch mode
```

## Critical Rules
- Mock external HTTP via `respx` (not monkeypatch)
- No mocking in-memory stores — use real store state in fixtures
- Integration tests require running Docker services
- CI runs full suite on every push

## Dependencies
- pytest, pytest-asyncio, pytest-cov, respx (backend)
- vitest, @testing-library/react, @testing-library/jest-dom (frontend)
