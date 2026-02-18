---
title: Local CI/CD Operations & Requirements
category: requirements
linked-from: AGENTS.md, CRITICAL-requirements.md
status: ACTIVE
last-updated: 2026-02-18
---

# Local CI/CD Requirements

[← Back to AGENTS.md](../../../AGENTS.md)

## Mandatory Before GitHub

Run this for every configuration or script change:

```bash
./.runners-local/workflows/gh-workflow-local.sh all
```

Then verify status/logs if needed:

```bash
./.runners-local/workflows/gh-workflow-local.sh status
ls -la .runners-local/logs/
```

## Common Commands

- `./.runners-local/workflows/gh-workflow-local.sh validate`
- `./.runners-local/workflows/gh-workflow-local.sh all`
- `./.runners-local/workflows/gh-workflow-local.sh status`
- `./.runners-local/workflows/gh-workflow-local.sh billing`

## Cost Control

Keep validation local to reduce GitHub Actions usage:

```bash
gh api user/settings/billing/actions
```

## Failure Handling

1. Inspect latest workflow logs in `.runners-local/logs/`.
2. Fix reported scripts/docs/config.
3. Re-run `validate`.
4. Re-run `all` before pushing.

## Quality Gates

- Local workflow succeeds end-to-end.
- Script lint/security checks pass.
- Tool status checks remain functional.
- Documentation matches current behavior.

[← Back to AGENTS.md](../../../AGENTS.md)
