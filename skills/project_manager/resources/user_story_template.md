# User Story Template

## Epic Template
```markdown
## Epic: [Epic Name]
**Goal:** [One sentence describing the business goal]
**Modules affected:** [List from module-map.md]
**Priority:** Must / Should / Could / Won't

### Stories
- [ ] Story 1
- [ ] Story 2
```

## User Story Template
```markdown
## Story: [Story Title]
**As a** [agent operator / developer / admin / end user]
**I want** [specific action or capability]
**So that** [business benefit or goal]

**Complexity:** XS / S / M / L / XL
**Modules:** [backend, frontend, agents, etc.]
**Skills needed:** [backend_developer, frontend_developer, tester, etc.]

### Acceptance Criteria
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]
- [ ] Error case: [what happens on failure]

### Definition of Done
- [ ] Code implemented and passes Ruff/ESLint
- [ ] Unit tests written and passing
- [ ] Integration test written (if API changes)
- [ ] Module doc updated (if structure changes)
- [ ] Code reviewed and approved
```

## Example Story
```markdown
## Story: Create Agent via UI
**As an** agent operator
**I want** to create a new agent with name, model, and system prompt via the admin UI
**So that** I can deploy new agents without using the API directly

**Complexity:** M
**Modules:** frontend, backend
**Skills needed:** frontend_developer, backend_developer, tester

### Acceptance Criteria
- [ ] Form on /admin/agents page with name, description, role, model, system_prompt, temperature fields
- [ ] Model dropdown populated from GET /api/v1/llm/models
- [ ] Submit calls POST /api/v1/agents; shows success toast
- [ ] Validation errors shown inline (required fields)
- [ ] New agent appears in agent list after creation
```
