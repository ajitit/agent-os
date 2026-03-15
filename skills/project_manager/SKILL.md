# Project Manager Skill

## Purpose
Use this skill when creating user stories, defining epics, breaking features into tasks, planning sprints, prioritizing the backlog, or creating release roadmaps for Vishwakarma.

## Context Sources
- `docs/project-context.md` — product purpose, capabilities, roadmap
- `docs/module-map.md` — module inventory for scoping
- `docs/ARCHITECTURE.md` — technical constraints affecting planning
- `docs/development-rules.md` — conventions affecting estimate accuracy

## Workflow
1. **Understand goal** — Clarify the feature or improvement being planned
2. **Map to modules** — Identify affected modules using `module-map.md`
3. **Write epics** — Define high-level epics using `resources/user_story_template.md`
4. **Break into stories** — Create user stories with acceptance criteria
5. **Task breakdown** — Decompose stories using `resources/task_breakdown_patterns.md`
6. **Estimate complexity** — Tag as XS/S/M/L/XL (not time estimates)
7. **Prioritize** — Apply MoSCoW (Must/Should/Could/Won't) to backlog
8. **Plan sprint** — Reference `resources/sprint_planning_guide.md` for cadence

## Rules
- User stories follow: "As a [role], I want [action] so that [benefit]"
- Every story must have: acceptance criteria, affected modules, skill tags
- Tag each task with the relevant skill: architect / frontend_developer / backend_developer / tester
- No story is "done" without: code + tests + docs updated
- Reference `development-rules.md` for Definition of Done
- Roadmap items must align with `project-context.md` core capabilities

## Output Expectations
- Epic definition with child stories
- User story cards with acceptance criteria
- Task list with module assignment and skill tag
- Sprint plan (if requested) with capacity notes
- Prioritized backlog with MoSCoW labels

### Story Format
```
## Story: [Title]
**As a** [role]
**I want** [feature]
**So that** [benefit]

### Acceptance Criteria
- [ ] criterion 1
- [ ] criterion 2

### Tasks
- [ ] [backend_developer] implement endpoint
- [ ] [frontend_developer] build UI component
- [ ] [tester] write test cases
```

## Resources
- `resources/user_story_template.md` — story format and examples
- `resources/sprint_planning_guide.md` — sprint cadence and capacity planning
- `resources/task_breakdown_patterns.md` — decomposition patterns by feature type
