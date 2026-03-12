# Architect Skill

## Purpose
Use this skill when designing or evolving the AgentOS system architecture, defining new module boundaries, selecting technologies, or planning integration strategies.

## Context Sources
- `docs/project-context.md` — project purpose, stack, core capabilities
- `docs/ARCHITECTURE.md` — system layers, component map, data flow
- `docs/development-rules.md` — architecture rules, dependency constraints
- `docs/module-map.md` — module inventory and relationships
- `docs/modules/backend.md` — backend component responsibilities
- `docs/ai-context/backend-AI_CONTEXT.md` — quick backend reference

## Workflow
1. **Load context** — Read `project-context.md` + `ARCHITECTURE.md`
2. **Identify scope** — Determine which modules are affected
3. **Check rules** — Review `development-rules.md` architecture constraints
4. **Design** — Apply patterns from `resources/architecture_patterns.md`
5. **Validate** — Run through `resources/system_design_checklist.md`
6. **Document** — Update affected module docs and `module-map.md`

## Rules
- Never violate layer boundaries (UI → API → Core → Adapters)
- All new resources must follow the registry pattern
- New LLM providers must implement `LLMBase` adapter interface
- No circular imports between `api/` modules
- Prefer in-memory stores for new resources; plan DB migration path

## Output Expectations
- Architecture decision record (ADR) with: context, options, decision, consequences
- Updated or new module doc in `docs/modules/`
- Annotated component diagram if flow changes
- List of affected files requiring changes

## Resources
- `resources/architecture_patterns.md` — patterns used in AgentOS
- `resources/system_design_checklist.md` — validation checklist
- `resources/microservices_patterns.md` — service decomposition patterns
