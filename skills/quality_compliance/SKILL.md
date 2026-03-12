# Quality & Compliance Skill

## Purpose
Use this skill when auditing AgentOS code and documentation for coding standards compliance, documentation completeness, API consistency, and governance requirements.

## Context Sources
- `docs/development-rules.md` — all standards and conventions
- `docs/module-map.md` — expected module structure
- `docs/modules/` — module documentation completeness baseline
- `docs/project-context.md` — project goals and design principles

## Workflow
1. **Define audit scope** — Identify what is being audited (code, docs, API, all)
2. **Run standards check** — Verify against `resources/compliance_checklist.md`
3. **Documentation audit** — Check all modules have up-to-date docs in `docs/modules/`
4. **API consistency** — Verify all routes use `APIResponse[T]` and follow naming conventions
5. **Dependency audit** — Check for unauthorized imports crossing layer boundaries
6. **Documentation gaps** — Identify missing docstrings, missing type hints, missing tests
7. **Report** — Produce prioritized findings with remediation actions

## Rules
- All Python functions in `backend/` must have type annotations
- All route handlers must return `APIResponse[T]`
- Every module must have a corresponding doc in `docs/modules/`
- `development-rules.md` is the source of truth for all standards
- Report findings with: location, rule violated, severity, suggested fix

## Output Expectations
Compliance report:
```
## Compliance Summary
- Scope: [files/modules audited]
- Pass rate: X/Y checks passed

## Critical Findings
- [file] rule violated — fix: ...

## Documentation Gaps
- Missing: [module].md for [module]

## Recommendations
- [priority] action item
```

## Resources
- `resources/compliance_checklist.md` — full compliance audit checklist
- `resources/documentation_requirements.md` — documentation standards per file type
