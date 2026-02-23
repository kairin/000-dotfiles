---
title: Git Strategy & Branch Management
category: requirements
linked-from: AGENTS.md, CRITICAL-requirements.md
status: ACTIVE
last-updated: 2026-02-18
---

# Branch Management & Git Strategy

[← Back to AGENTS.md](../../../AGENTS.md)

## Mandatory Rules

- Never delete branches unless the user explicitly asks.
- Branch names must follow `YYYYMMDD-HHMMSS-type-description`.
- Use conventional commit types (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).

## Standard Workflow

```bash
# 1) Create branch
DATETIME=$(date +"%Y%m%d-%H%M%S")
BRANCH_NAME="${DATETIME}-docs-update-reference"
git checkout -b "$BRANCH_NAME"

# 2) Make changes
# ... edit files ...

# 3) Validate locally first
./.runners-local/workflows/gh-workflow-local.sh all

# 4) Commit
git add -A
git commit -m "docs: refresh installer and tooling references"

# 5) Push
git push -u origin "$BRANCH_NAME"
```

## Merge Policy

If merging locally:

```bash
git checkout main
git pull --ff-only origin main
git merge "$BRANCH_NAME" --no-ff
git push origin main
```

If merging via PR, keep branch history unless the user requests cleanup.

## Pre-Commit Checklist

- [ ] Local CI/CD passed (`gh-workflow-local.sh all`)
- [ ] No secrets included
- [ ] Docs updated for behavior changes
- [ ] Branch name follows required schema

## Approval Gates

Explicit user confirmation is required before:
- Merging to `main`
- Deleting files or branches
- Force-pushing
- Changing branch protection settings

[← Back to AGENTS.md](../../../AGENTS.md)
