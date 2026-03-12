# End User Skill

## Purpose
Use this skill to simulate real user interactions with AgentOS, validate usability, provide non-technical workflow feedback, and identify friction points that technical reviewers may miss.

## Context Sources
- `docs/project-context.md` — product purpose and core user capabilities
- `docs/modules/ui.md` — available pages and features
- `frontend/agentos-ui/src/app/` — actual page implementations

## Workflow
1. **Define persona** — Establish the user role (e.g., ops engineer, data scientist, business analyst)
2. **Select journey** — Choose a workflow to simulate (e.g., create agent → chat → review results)
3. **Walk through steps** — Simulate each UI interaction step by step
4. **Apply checklist** — Run through `resources/usability_testing_checklist.md`
5. **Identify friction** — Note confusing labels, missing feedback, unclear flows
6. **Collect feedback** — Use `resources/user_feedback_template.md` to structure findings
7. **Rate usability** — Score on clarity, efficiency, error recovery, satisfaction
8. **Report** — Produce structured usability report with prioritized issues

## Rules
- Adopt a non-technical perspective — avoid assuming technical knowledge
- Focus on: discoverability, clarity of labels, feedback on actions, error messages
- Flag any workflow requiring more than 5 steps for a common task
- Note missing loading states, unhelpful error messages, or confusing navigation
- Validate that new features are accessible without reading documentation

## Output Expectations
Usability report:
```
## Usability Test Summary
- Persona: [role description]
- Workflow tested: [name]
- Overall score: X/10

## Friction Points
- [Page/Step] issue — impact: HIGH/MED/LOW — suggestion: ...

## Positive Observations
- [what works well]

## Recommendations
- [priority] improvement
```

## Resources
- `resources/user_feedback_template.md` — structured feedback collection form
- `resources/usability_testing_checklist.md` — heuristic evaluation checklist
