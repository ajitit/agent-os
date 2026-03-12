# Frontend Developer Skill

## Purpose
Use this skill when implementing or modifying UI components, pages, frontend logic, API integrations, or optimizing frontend performance in AgentOS.

## Context Sources
- `docs/modules/ui.md` — frontend module structure, key files, data flow
- `docs/ai-context/frontend-AI_CONTEXT.md` — key files, APIs consumed, critical rules
- `docs/development-rules.md` — TypeScript standards, component conventions
- `frontend/agentos-ui/src/lib/api.ts` — HTTP client (must use for all API calls)
- `frontend/agentos-ui/src/lib/env.ts` — environment variable access

## Workflow
1. **Read context** — Load `modules/ui.md` + `frontend-AI_CONTEXT.md`
2. **Identify files** — Locate the relevant page/component in `src/app/` or `src/components/`
3. **Read target file** — Read existing code before modifying
4. **Check patterns** — Reference `resources/component_patterns.md`
5. **Implement** — Write TypeScript; use `lib/api.ts` for all backend calls
6. **Handle states** — Implement loading, error, empty, and success states
7. **Verify types** — No implicit `any`; types must align with backend `APIResponse<T>`
8. **Test** — Add/update test in `*.test.tsx` using Vitest + @testing-library/react

## Rules
- **Always** use `src/lib/api.ts` — never call `fetch` directly in components
- New pages → `src/app/{feature}/page.tsx`; new components → `src/components/`
- TypeScript strict — no `any`, no `@ts-ignore` without justification
- Tailwind v4 for all styling — no inline styles, no CSS modules
- SSE streaming via fetch with `ReadableStream` (see `chat/page.tsx` as reference)
- Run `npm run lint` before considering work complete

## Output Expectations
- Working TypeScript component or page file(s)
- All API response types matching `APIResponse<T>` from backend
- Loading / error / empty state handling
- Relevant test file updated or created
- No console errors or TypeScript errors

## Resources
- `resources/component_patterns.md` — React component patterns for AgentOS
- `resources/frontend_architecture.md` — page/component organization guide
- `resources/state_management_patterns.md` — local state and data fetching patterns
