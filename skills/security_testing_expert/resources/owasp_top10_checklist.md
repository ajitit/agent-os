# OWASP Top 10 Checklist — AgentOS

## A01 Broken Access Control
- [ ] All non-public endpoints require valid JWT
- [ ] User can only access their own resources (check ownership validation)
- [ ] `DELETE /api/v1/{resource}/{id}` requires auth
- [ ] Test: call protected endpoint with no token → expect 401
- [ ] Test: call with expired token → expect 401
- [ ] Test: call with wrong secret JWT → expect 401

## A02 Cryptographic Failures
- [ ] JWT signed with `JWT_SECRET_KEY` (env var, never hardcoded)
- [ ] Passwords hashed with bcrypt (passlib) — not MD5/SHA1
- [ ] No sensitive data (tokens, passwords) in response bodies or logs
- [ ] No secrets in Docker image layers or git history

## A03 Injection
- [ ] All user input validated by Pydantic before use
- [ ] No string concatenation for queries (mitigated by no raw SQL currently)
- [ ] Test: send `<script>alert(1)</script>` in string fields → verify stored as-is, not executed
- [ ] Test: send `{"$where": "1==1"}` style payloads → verify Pydantic rejects

## A05 Security Misconfiguration
- [ ] CORS origins restricted to known frontends (not `*`)
- [ ] Debug mode disabled in production (`ENVIRONMENT=production`)
- [ ] Error responses do not expose stack traces to clients
- [ ] Docker non-root user (uid 1000)

## A06 Vulnerable Components
- [ ] `requirements.txt` dependencies have no known CVEs (run `pip audit`)
- [ ] `package.json` dependencies have no known CVEs (run `npm audit`)

## A07 Authentication Failures
- [ ] Rate limiting on `/auth/login` to prevent brute force
- [ ] JWT algorithm explicitly set (`JWT_ALGORITHM=HS256`)
- [ ] Token expiry configured and enforced
- [ ] Test: replay expired token → expect 401

## A09 Security Logging & Monitoring
- [ ] Failed auth attempts are logged with IP and timestamp
- [ ] `X-Request-ID` correlation on all requests for tracing
- [ ] Audit log populated for sensitive operations (`/audit` endpoint)
