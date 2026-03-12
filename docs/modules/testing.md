# Testing Module

## Purpose
Test suites for backend (Python/Pytest) and frontend (TypeScript/Vitest) components.

## Testing Framework

### Backend
- **Framework:** pytest 8+ with pytest-asyncio
- **Coverage:** pytest-cov
- **HTTP mocking:** respx (for external API calls)
- **Config:** `pyproject.toml` → `[tool.pytest.ini_options]`

### Frontend
- **Framework:** Vitest 4.0.18
- **DOM:** @testing-library/react, @testing-library/jest-dom
- **Config:** `vitest.config.ts`, `vitest.setup.ts`

## Test Structure

### Backend
```
backend/tests/
├── conftest.py                    # Shared fixtures
├── test_api.py                    # General API tests
├── test_knowledge.py              # Knowledge module tests
├── test_skills.py                 # Skills module tests
├── integration/
│   └── api/test_llm.py           # LLM integration tests
└── unit/
    ├── adapters/test_openai.py    # OpenAI adapter unit tests
    ├── api/
    │   ├── test_audit.py
    │   ├── test_marketplace.py
    │   └── test_plans.py
    ├── pipeline/test_pipeline.py  # Pipeline stage tests
    └── planning/test_planner.py   # Planner unit tests
```

### Frontend
```
frontend/agentos-ui/src/
└── app/page.test.tsx              # Home page test
```

## How to Run Tests

### Backend
```bash
cd backend
pytest                          # All tests
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest --cov=backend            # With coverage report
```

### Frontend
```bash
cd frontend/agentos-ui
npm test                        # Run all tests
npm run test:watch              # Watch mode
```

## Mocking Strategy
- **HTTP calls:** `respx` for mocking httpx requests to external APIs
- **In-memory stores:** Tests use isolated store state via fixtures
- **LLM calls:** Mocked at adapter level in unit tests
- **No database mocks:** Integration tests use real services (via Docker)

## CI Integration
- GitHub Actions: `.github/workflows/ci.yml`
- Backend: `pytest` on every push/PR
- Frontend: `npm run lint && npm test && npm run build`

## Example Test Locations
- Agent API test: `tests/unit/api/test_plans.py`
- Pipeline test: `tests/unit/pipeline/test_pipeline.py`
- LLM adapter test: `tests/unit/adapters/test_openai.py`
- Integration: `tests/integration/api/test_llm.py`
