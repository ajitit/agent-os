# AgentOS Change Execution Instructions

This document defines the standard workflow for planning, executing, and reviewing any change to the AgentOS codebase. Follow these steps in order for every task — bug fix, feature, config change, or refactor.

---

## Step 1 — Pick the `change_planner` Skill

Before writing a single line of code, activate the **Change Planner** skill to frame the work as a structured change record.

**How to activate:**

```
GET /api/v1/skills/change_planner
```

This loads the full `SKILL.md` instructions. Follow the 5-step process defined there:

1. Gather context (component, type, problem statement, root cause)
2. Assign a Change ID: `AI-CHG-YYYY-NNN`
3. Draft the change record using `skills/change_planner/resources/change_template.md`
4. Validate all required sections are complete
5. Hold the draft — do not execute until Steps 2–4 below are done

> The change record is your contract for the work. Every subsequent decision should be traceable back to it.

---

## Step 2 — Pick Appropriate Skills from `agent-os/skills/`

Select one or more domain skills that match the type of work in your change record. Load each skill via:

```
GET /api/v1/skills/{skill_id}
```

| Skill | Use When |
|-------|----------|
| `architect` | Designing system structure, service boundaries, or data flow |
| `backend_developer` | Writing or modifying FastAPI routes, models, services, or DB logic |
| `frontend_developer` | Writing or modifying Next.js pages, components, or API calls |
| `tester` | Writing unit, integration, or E2E tests |
| `code_reviewer` | Reviewing a diff for correctness, style, and security |
| `security_testing_expert` | Assessing attack surface, auth flows, or injection risks |
| `performance_testing_expert` | Load testing, profiling, or latency optimisation |
| `quality_compliance` | Ensuring code meets project standards and lint rules |
| `repo_quality_check` | Full repository hygiene scan (imports, dead code, lint, tests) |
| `ui_ux_designer` | Designing user flows, layouts, or accessibility |
| `project_manager` | Scoping, prioritising, or coordinating multi-step work |
| `web_research` | Researching external libraries, APIs, or best practices |
| `end_user` | Validating from a product/UX perspective |

**Rule:** pick the minimum set of skills needed. Do not load skills that are not relevant to the change.

---

## Step 3 — Pick Appropriate Docs from `agent-os/docs/`

Load reference documentation relevant to your change. Key documents:

| Document | When to Use |
|----------|-------------|
| `docs/ARCHITECTURE.md` | Understanding system design, service layout, or component ownership |
| `docs/module-map.md` | Finding which module owns a feature or API endpoint |
| `docs/development-rules.md` | Checking coding conventions, naming rules, and PR standards |
| `docs/project-context.md` | Understanding product goals, constraints, and non-negotiables |
| `docs/process/git_workflow.md` | Following branch, commit, and PR naming conventions |
| `docs/process/git_workflow_cheat_sheet/` | Quick-reference git commands for the workflow |
| `docs/modules/` | Deep-dive docs for individual backend or frontend modules |
| `docs/skills/QUICKSTART.md` | Creating or modifying skills (Progressive Disclosure pattern) |
| `docs/supervisor/` | Understanding supervisor agent routing and task delegation |
| `docs/ai-context/` | AI system prompts and agent context files |

**Rule:** read docs before reading code. Docs give you the intent; code gives you the implementation.

---

## Step 4 — Create a Plan

With the change record, skills, and docs loaded, draft an execution plan:

```
plan/
└── AI-CHG-YYYY-NNN.md    ← one plan file per change
```

The plan file must include:

### 4.1 — Objective
One sentence: what this change accomplishes.

### 4.2 — Scope
- Files to be created, modified, or deleted
- APIs or schemas that will change
- Tests that must be added or updated

### 4.3 — Approach
Step-by-step implementation strategy. For each step:
- What to do
- Which skill is responsible
- Expected output or artefact

### 4.4 — Risk Check
- What could go wrong
- How to detect it
- How to roll back

### 4.5 — Definition of Done
Checklist the work must satisfy before moving to review:
- [ ] All tests pass (`pytest` + `npm run lint`)
- [ ] No new lint errors or warnings
- [ ] Change record is complete
- [ ] Docs updated if behaviour changed
- [ ] Plan file reflects what was actually done

---

## Step 5 — Execute the Plan

Follow the plan step by step. For each step:

1. Mark the step as **In Progress** in the plan file
2. Write or modify code using the relevant skill's instructions
3. Run tests and lint after each logical unit of work — do not batch failures
4. Mark the step as **Done** only when tests pass
5. Update the change record with actual files changed

**Execution rules:**
- Do not skip steps
- Do not modify files outside the declared scope without updating the plan first
- If a step is blocked, note the blocker in the plan and stop — do not work around it silently
- Follow `docs/development-rules.md` and `docs/process/git_workflow.md` at all times

---

## Step 6 — Create a Change Summary and Request Review

When execution is complete, produce a **Change Summary** at the top of the plan file:

```markdown
## Change Summary

| Field         | Value |
|---------------|-------|
| Change ID     | AI-CHG-YYYY-NNN |
| Files Changed | N files |
| Tests         | X passing, Y skipped |
| Lint          | Clean |
| Risk          | Low / Medium / High |

### What Changed
- Brief bullet list of what was done

### What Was Not Changed
- Anything explicitly left out of scope

### Open Questions
- Any decisions deferred to the reviewer
```

Then ask explicitly:

> **"Please review the Change Summary above. Should I also apply `repo_quality_check` before committing?"**

The `repo_quality_check` skill (`GET /api/v1/skills/repo_quality_check`) runs a full repository hygiene scan — dead imports, unused variables, lint violations, test coverage gaps. It adds time but catches issues that per-change checks miss. Apply it when:
- The change touches more than 5 files
- New dependencies were added
- A refactor moved or renamed code
- CI was recently failing

---

## Step 7 — Apply Changes After Approval

Once the reviewer approves the Change Summary (and `repo_quality_check` if requested):

1. **Commit** following the project convention in `docs/process/git_workflow.md`:
   ```
   <type>(<scope>): <short description>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   ```
   Valid types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`

2. **Push** to the feature branch:
   ```bash
   git push origin <branch>
   ```

3. **Update the change record** status to `Deployed` or `In Review` as appropriate

4. **Update the plan file** — mark all steps Done, record the final commit hash

5. **Open a PR** if required by `docs/process/git_workflow.md`, linking the Change ID in the PR description

> Do not push directly to `main` or `dev` without reviewer sign-off.

---

## Quick Reference

```
Step 1  →  GET /api/v1/skills/change_planner          Draft change record
Step 2  →  GET /api/v1/skills/{skill_id}               Load domain skills
Step 3  →  Read docs/ARCHITECTURE.md + relevant docs   Understand context
Step 4  →  Create plan/AI-CHG-YYYY-NNN.md              Write execution plan
Step 5  →  Execute plan, run tests after each step     Implement the change
Step 6  →  Write Change Summary, ask for review        Get approval
Step 7  →  Commit → Push → PR → Update change record   Ship it
```

---

## File Structure Reference

```
agent-os/
├── plan/
│   ├── INSTRUCTIONS.md          ← this file
│   └── AI-CHG-YYYY-NNN.md      ← one plan per change
├── skills/
│   ├── change_planner/          ← always use first
│   ├── backend_developer/
│   ├── frontend_developer/
│   └── ...
└── docs/
    ├── ARCHITECTURE.md
    ├── development-rules.md
    ├── module-map.md
    ├── project-context.md
    └── process/
        └── git_workflow.md
```
