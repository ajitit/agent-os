# Code Review Checklist

## Architecture (BLOCKER if violated)
- [ ] Layer boundaries respected (UI → API → Core → Adapters)
- [ ] No circular imports between `api/` modules
- [ ] LLM calls only in `adapters/llm/` — not in `api/` directly
- [ ] New route handlers added to `app/main.py`
- [ ] New resources follow registry/CRUD pattern

## Python / FastAPI (BLOCKER if violated)
- [ ] All route handlers are `async def`
- [ ] All responses use `APIResponse[T]` envelope
- [ ] Errors use `AgentOSException` — no bare `raise Exception`
- [ ] All functions have type annotations
- [ ] Config accessed via `settings` from `core/config.py` only
- [ ] No hardcoded API keys or secrets

## TypeScript / React (BLOCKER if violated)
- [ ] No `any` type without `// justification` comment
- [ ] All API calls via `lib/api.ts` — no direct `fetch`
- [ ] New pages in `src/app/`; new components in `src/components/`
- [ ] Loading + error + empty states handled

## Testing (WARNING if missing)
- [ ] Unit test added/updated for changed logic
- [ ] Test file mirrors source structure
- [ ] `@pytest.mark.asyncio` on async tests
- [ ] Happy path + at least one error path tested

## Security (BLOCKER if missing)
- [ ] Protected endpoints require JWT — no auth bypass
- [ ] No secrets in code or logs
- [ ] User input validated by Pydantic before use

## Quality (SUGGESTION)
- [ ] Function names are descriptive verbs
- [ ] No function longer than 50 lines without justification
- [ ] No commented-out code committed
- [ ] No TODO without linked issue
