# Change Record Template

> Copy this template and fill in all sections. Reference AI-CHG-2026-014 below as a completed example.

---

## Change Record

| Field | Value |
|-------|-------|
| **Change ID** | AI-CHG-YYYY-NNN |
| **Date** | YYYY-MM-DD |
| **Author** | Full Name / Team |
| **Reviewer** | Full Name / Team |
| **Component** | Service or module name |
| **Type** | Bug Fix \| Feature \| Hotfix \| Config Change \| Infra Change |
| **Priority** | Low \| Medium \| High \| Critical |
| **Risk Level** | Low \| Medium \| High |
| **Version** | vX.Y.Z |
| **Status** | Draft \| In Review \| Approved \| Deployed \| Closed |

---

### Summary

_One sentence describing what changed and why._

---

### Problem Statement

_Describe the symptom or requirement that triggered this change. Include observable behaviour, error messages, or business requirement references._

---

### Root Cause

_For bug fixes: explain the technical root cause. For features: describe the gap or need._

---

### Changes Made

List every file, function, config key, or schema element that was modified:

- `path/to/file.py` — _description of what changed_
- `config/settings.yaml` — _description of what changed_
- `tests/test_module.py` — _new or updated tests_

---

### Impact Assessment

**Affected Components:**
- _List services, APIs, databases, or UIs that are affected_

**Affected Users / Stakeholders:**
- _Who will notice this change? End users, operators, downstream services?_

**Behavioural Changes:**
- _What will behave differently after this change?_

**Data Impact:**
- _Are any database schemas, data formats, or stored values changing?_

---

### Risk Assessment

**Risk Level:** Low | Medium | High

**Justification:**
_Explain why this risk level was chosen. Consider blast radius, reversibility, and test coverage._

**Mitigations:**
- _Risk mitigation actions taken (e.g., feature flags, phased rollout, extra testing)_

---

### Testing

**Automated Tests:**
- Unit: _describe new/updated unit tests_
- Integration: _describe integration test coverage_
- E2E: _describe end-to-end test scenarios (if applicable)_

**Manual Verification:**
1. _Step-by-step manual verification procedure_
2. _Expected outcome at each step_

**Test Results:**
- All automated tests: PASS / FAIL
- Manual verification: PASS / FAIL

---

### Rollback Plan

_Describe specific, actionable steps to revert if deployment fails. Do not just say "revert the commit"._

1. _Step 1_
2. _Step 2_
3. _Verify rollback by..._

---

### Deployment Steps

_Ordered list of deployment actions:_

1. _Step 1 — e.g., merge PR #NNN to main_
2. _Step 2 — e.g., run database migration: `alembic upgrade head`_
3. _Step 3 — e.g., deploy to staging, verify metrics_
4. _Step 4 — e.g., deploy to production_
5. _Step 5 — e.g., monitor error rate for 30 minutes_

---

### Post-Deployment Verification

- [ ] Health check endpoints return 200
- [ ] Key metrics within normal range
- [ ] No spike in error logs
- [ ] Stakeholder sign-off received

---

### Notes / References

- _Links to relevant tickets, PRs, designs, or documentation_

---

---

# Example: AI-CHG-2026-014 (Completed Record)

| Field | Value |
|-------|-------|
| **Change ID** | AI-CHG-2026-014 |
| **Date** | 2026-03-10 |
| **Author** | Vishwakarma Platform Team |
| **Reviewer** | Lead Engineer |
| **Component** | Knowledge Retrieval Agent |
| **Type** | Bug Fix |
| **Priority** | High |
| **Risk Level** | Low |
| **Version** | v1.4.2 |
| **Status** | Deployed |

---

### Summary

Fixed incorrect tool invocation in the Knowledge Retrieval Agent caused by a missing tool description in the system prompt, which caused the LLM to hallucinate tool responses instead of calling the actual retrieval API.

---

### Problem Statement

The Knowledge Retrieval Agent was returning fabricated answers instead of fetching documents from the vector store. Users reported responses that cited documents that did not exist. Error rate on `/api/v1/knowledge/search` rose from 2% to 18% after the v1.4.1 deploy.

---

### Root Cause

The agent's system prompt lacked explicit tool usage constraints. Without a structured tool schema in the prompt, the LLM (claude-sonnet-4-6) inferred tool behaviour from context and hallucinated JSON tool calls with incorrect parameter names. The `retrieve_documents` tool expected a `query` parameter but the LLM was generating `search_query`, causing silent failures that fell back to ungrounded generation.

Secondary factor: model temperature was set to 0.7, which increased creative (non-deterministic) tool usage patterns.

---

### Changes Made

- `backend/agents/knowledge_retrieval/prompt.py` — Added explicit tool schema block to system prompt with parameter names, types, and usage constraints
- `backend/agents/knowledge_retrieval/agent.py` — Added tool schema validation layer; unknown tool calls now raise `ToolInvocationError`
- `backend/agents/knowledge_retrieval/config.py` — Reduced `temperature` from `0.7` to `0.2` for tool-calling mode
- `backend/tests/unit/agents/test_knowledge_retrieval.py` — Added 8 unit tests covering valid tool calls, invalid parameter names, and fallback behaviour
- `backend/tests/integration/test_knowledge_search.py` — Added integration test asserting retrieved documents are grounded in vector store results

---

### Impact Assessment

**Affected Components:**
- Knowledge Retrieval Agent (primary)
- `/api/v1/knowledge/search` endpoint (surface area)
- Vector store (Qdrant) — read path only, no schema changes

**Affected Users / Stakeholders:**
- All users querying the knowledge base
- Downstream agents that call the Knowledge Retrieval Agent as a tool

**Behavioural Changes:**
- Responses will now always cite real documents from the vector store
- Tool calls with unrecognised parameter names will return a structured error instead of silently falling back to generation

**Data Impact:**
- No schema or data changes. Read-only fix.

---

### Risk Assessment

**Risk Level:** Low

**Justification:**
Change is limited to the agent prompt and temperature config. No database migrations, no API contract changes, no new dependencies. Existing test suite covers the retrieval path. The fix makes behaviour more deterministic, reducing hallucination risk.

**Mitigations:**
- Deployed to staging first with 24-hour soak period
- Monitored retrieval accuracy metrics before production rollout
- Feature flag available to revert temperature to 0.7 without redeployment

---

### Testing

**Automated Tests:**
- Unit: 8 new tests in `test_knowledge_retrieval.py` — all passing
- Integration: 2 new tests in `test_knowledge_search.py` — all passing
- Regression: full suite of 187 tests — 185 passing, 2 skipped (auth integration — require live API key)

**Manual Verification:**
1. Send query `"What is the deployment architecture?"` to `/api/v1/knowledge/search`
2. Verify response cites documents matching vector store content
3. Inspect agent trace in Observability dashboard — confirm `retrieve_documents` tool was called with `query` parameter
4. Send query with rare term not in vector store — verify response states "no relevant documents found" rather than hallucinating

**Test Results:**
- All automated tests: PASS
- Manual verification: PASS

---

### Rollback Plan

1. Revert `backend/agents/knowledge_retrieval/config.py`: set `temperature` back to `0.7`
2. Revert `backend/agents/knowledge_retrieval/prompt.py`: remove the tool schema block (restore prior commit)
3. Revert `backend/agents/knowledge_retrieval/agent.py`: remove `ToolInvocationError` validation
4. Deploy the reverted version via standard CI/CD pipeline
5. Verify rollback by checking `/api/v1/health` returns 200 and querying `/api/v1/knowledge/search` returns responses (even if ungrounded)

---

### Deployment Steps

1. Merge PR #47 (`fix/knowledge-retrieval-tool-invocation`) to `main`
2. CI pipeline runs full test suite — verify all pass
3. Deploy to staging: `kubectl apply -f k8s/staging/`
4. Run smoke tests against staging endpoint
5. Monitor staging for 24 hours — check error rate stays below 3%
6. Deploy to production: `kubectl apply -f k8s/production/`
7. Monitor production error rate and token usage for 30 minutes
8. Confirm with stakeholders that knowledge search responses are grounded

---

### Post-Deployment Verification

- [x] Health check endpoints return 200
- [x] Knowledge search error rate dropped from 18% to 1.2%
- [x] No spike in error logs
- [x] Retrieval accuracy improved by ~30% (measured via golden-set eval)
- [x] Stakeholder sign-off received

---

### Notes / References

- Related ticket: AGOS-412 — "Knowledge agent returns hallucinated citations"
- PR: #47 — `fix/knowledge-retrieval-tool-invocation`
- Observability trace showing the bug: Run ID `8f3a2b1c`
- Temperature recommendation: [Anthropic tool use docs](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
