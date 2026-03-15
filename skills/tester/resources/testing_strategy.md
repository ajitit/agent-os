# Vishwakarma Testing Strategy

## Test Pyramid
```
         [E2E - minimal]
       [Integration - medium]
    [Unit - comprehensive]
```

## Unit Tests (Priority: HIGH)
- Target: all route handlers, adapters, pipeline stages, skill loader
- Location: `backend/tests/unit/`
- Mock: external HTTP (respx); LLM adapters
- Coverage target: 80%+ for `backend/api/` and `backend/core/`

## Integration Tests (Priority: MEDIUM)
- Target: full request/response cycle; LLM adapter with mocked OpenAI
- Location: `backend/tests/integration/`
- Requirements: may need Docker services running
- Validate: `APIResponse[T]` shape, HTTP status codes, store mutations

## Frontend Tests (Priority: MEDIUM)
- Target: page components, form interactions, API call patterns
- Location: `src/app/**/*.test.tsx`
- Mock: `lib/api.ts` responses
- Validate: loading/error/success states render correctly

## What to Always Test
1. Happy path (expected input → expected output)
2. Not found (404 for GET/PUT/DELETE with unknown ID)
3. Validation error (422 for missing required fields)
4. Auth failure (401 for missing/invalid JWT)

## What NOT to Test
- Third-party library internals (FastAPI routing, Pydantic validation)
- Simple pass-through getters with no logic
- Styles or exact HTML structure (fragile)

## Running Tests
```bash
# Backend
cd backend && pytest --cov=backend --cov-report=term-missing

# Frontend
cd frontend/agentos-ui && npm test
```
