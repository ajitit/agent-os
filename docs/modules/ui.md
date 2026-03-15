# UI Module

## Purpose
Next.js 16 + React 19 frontend for Vishwakarma. Provides all user-facing interfaces for managing agents, crews, workflows, knowledge, and settings.

## Responsibilities
- Render all 28 application pages via App Router
- Call backend `/api/v1` endpoints via typed HTTP client
- Display real-time chat with SSE streaming
- Manage registry views (tools, skills, models, MCP servers, knowledge graphs, data sources, remote APIs)

## Technology Stack
- **Framework:** Next.js 16.1.6 (App Router)
- **UI:** React 19.2.3, Tailwind v4
- **Charts:** recharts 2.15.4
- **Markdown:** react-markdown 9.0.0
- **Testing:** Vitest 4.0.18, @testing-library/react
- **Language:** TypeScript (strict)

## Key Directories
```
frontend/agentos-ui/src/
├── app/          # Pages (App Router)
│   ├── chat/
│   ├── registry/ # 7 registry sub-pages
│   ├── settings/
│   ├── plans/
│   └── ...
├── components/   # Shared UI components
└── lib/          # Utilities
```

## Important Files
| File | Role |
|------|------|
| `src/app/layout.tsx` | Root HTML layout, fonts, Nav |
| `src/app/page.tsx` | Home/dashboard |
| `src/app/chat/page.tsx` | Chat interface with streaming |
| `src/lib/api.ts` | HTTP client (all backend calls) |
| `src/lib/env.ts` | `NEXT_PUBLIC_API_URL` accessor |
| `src/components/Nav.tsx` | Persistent sidebar navigation |
| `src/components/ModelSelector.tsx` | LLM model dropdown |
| `next.config.ts` | Next.js configuration |
| `vitest.config.ts` | Test runner configuration |

## Data Flow
```
User action → Page component → lib/api.ts → fetch() → /api/v1
                                                          ↓
Page state update ← JSON response ← APIResponse<T> envelope
```

## External Dependencies
- `NEXT_PUBLIC_API_URL` — backend base URL (default: `http://localhost:8000`)

## Development Rules
- Never call `fetch` directly; always use `src/lib/api.ts`
- Pages go in `app/`; reusable components go in `components/`
- Use TypeScript strict mode — no implicit `any`
- Run `npm run lint` and `npm test` before committing
- SSE streaming handled in `chat/page.tsx` via `EventSource` or streaming fetch
