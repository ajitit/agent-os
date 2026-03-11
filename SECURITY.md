# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities by email. Do not open public issues for security-sensitive findings.

- **Do not** commit secrets (API keys, passwords) to the repository
- Use `.env` for local configuration; `.env` is in `.gitignore`
- Rotate any accidentally exposed credentials immediately

## Best Practices

- All API routes use consistent error responses (no stack traces in production)
- CORS is configurable via `CORS_ORIGINS`
- Backend runs as non-root user in Docker
- Security headers enabled on frontend (X-Frame-Options, X-Content-Type-Options, etc.)
