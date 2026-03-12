# AI + Manual Development Git Workflow

This document describes the Git workflow for managing development between an AI agent and a manual developer. The workflow ensures quality control, easy merging, and traceable history.

## Branching Strategy

- **main**: Stable, production-ready code.
- **agent-feature/<feature>**: Branch where AI agent develops new features.
- **manual-feature/<feature>**: Branch where manual review, testing, and fixes happen.

## Workflow Steps

### 1. Agent Development

1. Create a feature branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b agent-feature/<feature-name>

AI agent writes code and commits:

git add .
git commit -m "AI: Implemented <feature-name>"
git push -u origin agent-feature/<feature-name>
2. Manual Review & Testing

Create a manual branch from agent’s branch:

git checkout agent-feature/<feature-name>
git checkout -b manual-feature/<feature-name>

Review, test, and update code:

git add .
git commit -m "Manual: Reviewed and tested <feature-name>"
git push -u origin manual-feature/<feature-name>

Optional: Rebase manual branch if main has changed:

git fetch origin
git rebase origin/main
3. Merge to Main

Switch to main and pull latest:

git checkout main
git pull origin main

Merge manual branch:

git merge manual-feature/<feature-name> --no-ff

Push main:

git push origin main
4. Next AI Feature

Agent creates the next feature branch from updated main:

git checkout main
git pull origin main
git checkout -b agent-feature/<next-feature>

AI continues development from latest stable code.

5. Cleaning Up Old Branches

After merging to main, delete old branches:

# Delete local branches
git branch -d agent-feature/<feature-name>
git branch -d manual-feature/<feature-name>

# Delete remote branches
git push origin --delete agent-feature/<feature-name>
git push origin --delete manual-feature/<feature-name>
Notes & Best Practices

Use descriptive feature names, e.g., agent-feature/login-auth.

Keep branches short-lived; merge often to avoid conflicts.

Always test manual-feature branches before merging to main.

Consider using Pull Requests (PRs) for formal review even if it’s only you.

Example Diagram
main
  │
  │  ← stable production-ready code
  │
  ├─────────────────────────────┐
  │                             │
agent-feature/<feature1>       agent-feature/<feature2>
  │                             │
  │  ← AI agent develops        │  ← AI agent starts next feature
  │
manual-feature/<feature1>
  │
  │  ← You review, test, fix
  │
  └───────────────> main
                   │
                   │  ← stable, tested code updated
                   │
agent-feature/<feature-next>
  │
  │  ← Agent picks up latest main and continues

This workflow ensures AI code is reviewed, tested, and merged safely while maintaining a clear development history.


---

### 2️⃣ Save the Git Commands Cheat Sheet File

1. Create another file:


Git_CheatSheet.md


2. Copy and paste the content below:

```markdown
# Git Commands Cheat Sheet for AI + Manual Workflow

This cheat sheet contains the exact Git commands to manage your AI and manual development workflow efficiently.

---

## 1. Agent Feature Branch Creation

```bash
git checkout main
git pull origin main
git checkout -b agent-feature/<feature-name>
2. AI Commits Code
git add .
git commit -m "AI: Implemented <feature-name>"
git push -u origin agent-feature/<feature-name>
3. Manual Review Branch
git checkout agent-feature/<feature-name>
git checkout -b manual-feature/<feature-name>
4. Manual Review & Testing
git add .
git commit -m "Manual: Reviewed and tested <feature-name>"
git push -u origin manual-feature/<feature-name>
Optional: Rebase if main has changed
git fetch origin
git rebase origin/main
5. Merge Manual Branch into Main
git checkout main
git pull origin main
git merge manual-feature/<feature-name> --no-ff
git push origin main
6. Next AI Feature Branch
git checkout main
git pull origin main
git checkout -b agent-feature/<next-feature>
7. Cleaning Up Old Branches
git branch -d agent-feature/<feature-name>
git branch -d manual-feature/<feature-name>
git push origin --delete agent-feature/<feature-name>
git push origin --delete manual-feature/<feature-name>