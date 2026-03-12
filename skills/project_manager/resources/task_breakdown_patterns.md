# Task Breakdown Patterns

## New API Endpoint Feature
```
Story: Add [resource] management
Tasks:
  [ ] [architect]          Define data model + API contract
  [ ] [backend_developer]  Add Pydantic models (Create, Update, Response)
  [ ] [backend_developer]  Implement CRUD handlers in api/{resource}.py
  [ ] [backend_developer]  Register router in app/main.py
  [ ] [backend_developer]  Add store dict in stores.py
  [ ] [frontend_developer] Build list page (src/app/registry/{resource}/page.tsx)
  [ ] [frontend_developer] Build create/edit form
  [ ] [tester]             Write unit tests for all 5 CRUD handlers
  [ ] [tester]             Write frontend component test
  [ ] [code_reviewer]      Review PR
  [ ] [quality_compliance] Update docs/modules/ and module-map.md
```

## Bug Fix
```
Story: Fix [bug description]
Tasks:
  [ ] [tester]             Write failing test reproducing bug
  [ ] [backend/frontend]   Implement fix
  [ ] [tester]             Verify test now passes
  [ ] [code_reviewer]      Review fix
```

## New Skill
```
Story: Add [skill name] skill
Tasks:
  [ ] [architect]          Define skill purpose and levels
  [ ] [backend_developer]  Create metadata.json
  [ ] [backend_developer]  Write SKILL.md (workflow, rules, output)
  [ ] [backend_developer]  Create resources/ files (templates, checklists)
  [ ] [tester]             Load skill via API and validate all 3 levels
```

## Performance Improvement
```
Story: Optimize [endpoint/feature]
Tasks:
  [ ] [performance_expert] Baseline benchmark current performance
  [ ] [backend_developer]  Implement optimization
  [ ] [performance_expert] Re-benchmark to validate improvement
  [ ] [tester]             Regression tests to confirm no breakage
  [ ] [code_reviewer]      Review change
```
