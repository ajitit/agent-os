# Contributing to AgentOS

Thank you for contributing to AgentOS. This document outlines our development workflow and standards.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

## Development Setup

1. **Clone and install backend**
   ```bash
   python -m venv backend/venv
   source backend/venv/bin/activate  # or `backend\venv\Scripts\activate` on Windows
   pip install -r backend/requirements.txt
   ```

2. **Install frontend**
   ```bash
   cd frontend/agentos-ui && npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

## Code Standards

### Backend (Python)

- **Formatter/Linter**: Ruff (`ruff check backend/` and `ruff format backend/`)
- **Type hints**: Required for public APIs
- **Tests**: Pytest; run with `cd backend && pytest`

### Frontend (TypeScript/React)

- **Linter**: ESLint (`npm run lint`)
- **Tests**: Vitest (`npm run test`)

## Pre-commit

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

## Pull Request Process

1. Create a feature branch from `develop`
2. Make changes; ensure tests pass
3. Run `pre-commit run --all-files`
4. Submit PR with a clear description
5. Address review feedback

## Commit Messages

- Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, etc.
- Example: `feat(api): add rate limiting to task endpoints`

## Push the Chnages
```bash
#1️⃣ Check current status
git status
#2️⃣ Add changes to staging
git add .
#3️⃣ Commit the changes
git commit -m "Your commit message"
#4️⃣ Push to remote repository
git push origin main or branch_name



```