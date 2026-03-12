# Documentation Requirements

## Required Documentation per File Type

### `backend/api/{resource}.py`
- Corresponding `docs/modules/{resource}.md` must exist
- Entry in `docs/module-map.md`

### `backend/adapters/{service}/`
- Mention in `docs/modules/llm.md` (or equivalent)
- Interface contract documented in `base.py` docstring

### `skills/{name}/`
- `metadata.json` with name, description, version, tags
- `SKILL.md` with Purpose, Context Sources, Workflow, Rules, Output Expectations
- At least one resource file in `resources/`

### `.env.example`
- Every env var that the system reads must appear here
- Include default value and brief comment

### New Frontend Page
- Page purpose described in `docs/modules/ui.md` under Key Directories or Important Files

## Module Doc Template
Every `docs/modules/{module}.md` must include:
1. Module Name
2. Purpose (1–2 sentences)
3. Responsibilities (bullet list)
4. Technology Stack (table)
5. Key Directories (tree)
6. Important Files (table: file | role)
7. Data Flow (diagram or steps)
8. Development Rules (bullet list)

## Freshness Rule
Module docs must be updated whenever:
- New files are added to the module
- API contracts change
- Dependencies change
- Architecture decisions affect the module
