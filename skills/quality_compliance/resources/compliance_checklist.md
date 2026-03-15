# Vishwakarma Compliance Checklist

## Code Standards — Python
- [ ] All functions have type annotations (MyPy strict)
- [ ] Ruff lint passes with line-length=100
- [ ] No bare `except:` clauses
- [ ] No `print()` in production code — use `logging`
- [ ] No hardcoded secrets or API keys
- [ ] All route handlers are `async def`
- [ ] Config accessed only via `settings` singleton

## Code Standards — TypeScript
- [ ] No implicit `any` types
- [ ] All API calls via `lib/api.ts`
- [ ] ESLint passes with no warnings
- [ ] No direct `process.env` access outside `lib/env.ts`

## API Consistency
- [ ] All routes prefixed `/api/v1/`
- [ ] All success responses use `APIResponse[T]` envelope
- [ ] All error responses use `APIError` format
- [ ] Route names are plural nouns (`/agents`, not `/agent`)
- [ ] HTTP methods match semantics (GET=read, POST=create, PUT=update, DELETE=remove)

## Documentation Completeness
- [ ] Every module in `backend/api/` has a doc in `docs/modules/`
- [ ] `docs/module-map.md` reflects current module inventory
- [ ] New env vars added to `.env.example` with description
- [ ] New skills have `metadata.json` + `SKILL.md`
- [ ] `CHANGELOG` or commit messages explain breaking changes

## Test Coverage
- [ ] New route handlers have unit tests
- [ ] New business logic has unit tests
- [ ] CI runs full test suite on push

## Security Baseline
- [ ] No endpoint skips JWT auth (except `/health`, `/auth`)
- [ ] No sensitive data logged (no tokens, passwords, API keys in logs)
- [ ] Docker image runs as non-root (uid 1000)
- [ ] Rate limiting configured (`RATE_LIMIT_PER_MINUTE`)
