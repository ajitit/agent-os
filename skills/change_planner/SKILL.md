# Change Planner

## Purpose

Use this skill when you need to author, review, validate, or process a structured Change Record for any software modification — bug fixes, features, hotfixes, configuration changes, or infrastructure updates. This skill guides you through producing a complete, audit-ready change document that captures intent, risk, impact, and deployment steps.

## Instructions

### Step 1 — Gather Context

Before drafting a change record, collect the following from the user or codebase:

1. **Type of change**: Bug Fix | Feature | Hotfix | Config Change | Infra Change
2. **Affected component(s)**: service name, module, API endpoint, or configuration file
3. **Problem statement**: what symptom or requirement triggered this change
4. **Root cause** (for bug fixes): what was the underlying technical cause
5. **Scope of changes**: which files, functions, configs were modified

### Step 2 — Determine Change ID

Use the naming convention: `CODE-CHG-YYYY-NNN`
- `YYYY` = current year (e.g., 2026)
- `NNN` = sequential 3-digit number (e.g., 019)

If no ID is provided, assign the next available number or leave as `CODE-CHG-YYYY-XXX` for the user to fill in.

### Step 3 — Draft the Change Record

Populate all sections of the change record template. Use `resources/change_template.md` as the authoritative template structure.

Key sections to fill:

| Section | Guidance |
|---------|----------|
| **Summary** | One sentence: what changed and why |
| **Root Cause** | Technical explanation of the defect or need (bug fixes only) |
| **Changes Made** | Bullet list of specific file/function/config changes |
| **Impact Assessment** | Which components, users, or systems are affected |
| **Risk Level** | Low / Medium / High — justify the rating |
| **Testing** | Unit tests, integration tests, manual verification steps |
| **Rollback Plan** | How to revert if deployment fails |
| **Deployment Steps** | Ordered list of deployment actions |

### Step 4 — Validate the Record

Before finalising, verify:

- [ ] Change ID follows the `CODE-CHG-YYYY-NNN` format
- [ ] Root cause is specific (not vague like "bug in code")
- [ ] All affected files are listed under "Changes Made"
- [ ] Risk level is justified with reasoning
- [ ] Rollback plan is actionable (not just "revert the commit")
- [ ] Deployment steps are ordered and complete
- [ ] Testing section lists both automated and manual verification

### Step 5 — Output

Return the completed change record as a Markdown document. If the user provides an existing change record for review, identify gaps, inconsistencies, or missing sections and suggest corrections.

## Resources

- `resources/change_template.md` — Canonical change record template with all required sections and example content based on AI-CHG-2026-014.
