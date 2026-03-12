# Frontend Architecture Guide

## Directory Rules
```
src/
  app/                    # Next.js App Router
    {feature}/
      page.tsx            # Page component (route)
      page.test.tsx       # Co-located test
      [id]/
        page.tsx          # Dynamic route
  components/             # Shared reusable components
    {ComponentName}.tsx   # PascalCase filenames
  lib/
    api.ts                # HTTP client — only file that calls fetch
    env.ts                # env var accessors
```

## Naming Conventions
- Pages: `page.tsx` (Next.js convention)
- Components: `PascalCase.tsx`
- Utilities: `camelCase.ts`
- Types/interfaces: `PascalCase` (inline or in component file)

## Data Fetching Strategy
- Simple page data: `useEffect` + `useState` (current pattern)
- Streaming: native `fetch` with `ReadableStream`
- Mutations: inline async handlers with loading/error state

## Environment Variables
```ts
// src/lib/env.ts — always use this, not process.env directly
export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
```

## Error Boundary
- `src/app/error.tsx` — catches unhandled render errors
- `src/app/loading.tsx` — Suspense fallback for page loading
