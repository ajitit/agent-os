# Security Testing Expert Skill

## Purpose
Use this skill when performing security assessments, vulnerability testing, authentication audits, or OWASP validation on AgentOS API endpoints, authentication flows, and data handling.

## Context Sources
- `docs/ARCHITECTURE.md` — auth layer, external dependencies, deployment model
- `docs/development-rules.md` — security considerations section
- `docs/modules/backend.md` — JWT auth, CORS, rate limiting configuration
- `docs/modules/infra.md` — secrets management, Docker security, env vars
- `backend/core/security.py` — JWT implementation
- `backend/core/middleware.py` — request middleware

## Workflow
1. **Define attack surface** — Map all public and authenticated endpoints
2. **Authentication audit** — Review JWT implementation in `core/security.py`
3. **OWASP check** — Run through `resources/owasp_top10_checklist.md`
4. **Input validation** — Check Pydantic models for injection vectors
5. **Auth bypass test** — Attempt to access protected endpoints without/with invalid JWT
6. **Secrets audit** — Verify no secrets in code, logs, or Docker layers
7. **CORS review** — Validate `CORS_ORIGINS` configuration
8. **Report** — Produce findings with CVSS severity and remediation

## Rules
- Use `resources/security_testing_methods.md` for test procedures
- All findings must include: endpoint/file, vulnerability type, CVSS severity, reproduction steps, fix recommendation
- Never test against production without explicit authorization
- Rate limit bypass tests must use isolated environment
- JWT tests: expired token, wrong secret, missing token, malformed token
- SQL injection tests: not applicable (no SQL yet), but flag when DB added

## Output Expectations
Security assessment report:
```
## Security Assessment Summary
- Scope: [endpoints / modules tested]
- Critical: X findings
- High: X findings

## Findings
### [CRITICAL/HIGH/MEDIUM/LOW] Finding Title
- Location: [file:line or endpoint]
- Description: ...
- Reproduction: ...
- Fix: ...
```

## Resources
- `resources/owasp_top10_checklist.md` — OWASP Top 10 validation checklist
- `resources/security_testing_methods.md` — test procedures for AgentOS
