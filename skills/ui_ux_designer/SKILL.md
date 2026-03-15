# UI/UX Designer Skill

## Purpose
Use this skill when designing new user-facing features, improving existing workflows, defining interaction patterns, or ensuring accessibility compliance in the Vishwakarma frontend.

## Context Sources
- `docs/project-context.md` — product purpose and user goals
- `docs/modules/ui.md` — current frontend structure and pages
- `docs/ai-context/frontend-AI_CONTEXT.md` — key frontend files and API calls
- `frontend/agentos-ui/src/app/` — existing page implementations

## Workflow
1. **Understand goal** — Identify the user need or problem being solved
2. **Map user journey** — Define steps from entry to completion
3. **Audit existing UI** — Review relevant pages in `frontend/agentos-ui/src/app/`
4. **Apply patterns** — Reference `resources/design_patterns.md`
5. **Check accessibility** — Validate against `resources/accessibility_guidelines.md`
6. **Produce deliverable** — Wireframe description, component list, interaction spec
7. **Handoff** — Provide structured spec for `frontend_developer` skill

## Rules
- All interactive elements must meet WCAG 2.1 AA contrast and focus standards
- Navigation follows existing `Nav.tsx` pattern — do not redesign global nav without architect approval
- New pages go in `src/app/{feature}/page.tsx` (App Router convention)
- Reusable components go in `src/components/` with descriptive names
- Dark mode must be considered for all new UI elements (Tailwind v4 dark: prefix)

## Output Expectations
- User journey map (step-by-step user actions)
- Page/component inventory (what to create or modify)
- Interaction specification (hover, click, loading, error states)
- Accessibility notes (ARIA roles, keyboard navigation)
- Handoff spec for developer implementation

## Resources
- `resources/ui_design_principles.md` — Vishwakarma UI conventions
- `resources/accessibility_guidelines.md` — WCAG 2.1 AA requirements
- `resources/design_patterns.md` — reusable interaction patterns
