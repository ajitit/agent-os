# Frontend AI Context — Vishwakarma UI

## Module Purpose
Next.js 16 + React 19 frontend for Vishwakarma. All pages call `/api/v1` via `src/lib/api.ts`.

## Key Files
- `src/app/layout.tsx` — root layout + Nav
- `src/app/chat/page.tsx` — streaming chat UI
- `src/app/registry/*/page.tsx` — 7 registry management pages
- `src/lib/api.ts` — **all** HTTP calls go through here
- `src/lib/env.ts` — `NEXT_PUBLIC_API_URL` accessor
- `src/components/Nav.tsx` — sidebar nav
- `src/components/ModelSelector.tsx` — LLM picker

## Data Flow
```
Page → lib/api.ts → fetch(NEXT_PUBLIC_API_URL + /api/v1/...)
     ← APIResponse<T> JSON ← Backend
```

## Important APIs Consumed
- `GET/POST /api/v1/agents` — agent management
- `GET/POST /api/v1/conversations/{id}/chat/stream` — SSE chat
- `GET /api/v1/skills` — skill listing
- `GET /api/v1/llm/models` — model selector data
- Registry endpoints: `/tools`, `/skills`, `/models`, `/mcp-servers`, `/data-sources`, `/knowledge-graphs`, `/remote-apis`

## Critical Rules
- Never call `fetch` directly — always use `lib/api.ts`
- TypeScript strict mode — no `any`
- Pages in `app/`; reusable components in `components/`

## Dependencies
- Next.js 16, React 19, Tailwind v4
- recharts (charts), react-markdown (markdown)
- Vitest + @testing-library/react (tests)
