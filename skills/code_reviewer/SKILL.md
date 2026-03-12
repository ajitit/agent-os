# Code Reviewer Skill

## Purpose
Use this skill when reviewing pull requests, code changes, or implementations for architecture compliance, coding standards, security, performance risks, and maintainability.

## Context Sources
- `docs/development-rules.md` — all coding standards and architecture rules
- `docs/ARCHITECTURE.md` — layer boundaries and component responsibilities
- `docs/module-map.md` — module dependencies and relationships
- `docs/ai-context/backend-AI_CONTEXT.md` — backend conventions
- `docs/ai-context/frontend-AI_CONTEXT.md` — frontend conventions

## Workflow
1. **Understand scope** — Identify which modules are modified
2. **Load rules** — Read `development-rules.md` + relevant module doc
3. **Architecture check** — Verify layer boundaries are respected
4. **Standards check** — Run through `resources/code_review_checklist.md`
5. **Security scan** — Check against `resources/security_rules.md`
6. **Performance review** — Identify N+1s, blocking calls, missing async
7. **Test coverage** — Confirm tests exist for changed logic
8. **Summarize** — Produce structured review with severity levels

## Rules
- Classify findings: BLOCKER / WARNING / SUGGESTION
- BLOCKER issues must be fixed before merge
- Never approve code that bypasses JWT auth on non-public endpoints
- Never approve direct LLM SDK imports outside `adapters/llm/`
- Flag any `Any` type without justification
- Flag missing `APIResponse[T]` envelope on new routes
- Flag synchronous route handlers (must be `async def`)

## Output Expectations
Structured review report:
```
## Review Summary
- Files reviewed: [list]
- Overall: APPROVED / CHANGES REQUESTED

## Blockers
- [file:line] issue description

## Warnings
- [file:line] issue description

## Suggestions
- [file:line] improvement note
```

## Resources
- `resources/code_review_checklist.md` — complete review checklist
- `resources/architecture_rules.md` — AgentOS-specific architecture rules
- `resources/clean_code_guidelines.md` — naming, size, complexity guidelines
