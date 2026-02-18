---
title: Critical Requirements (NON-NEGOTIABLE)
category: requirements
linked-from: AGENTS.md
status: ACTIVE
last-updated: 2026-02-18
---

# CRITICAL Requirements (NON-NEGOTIABLE)

[← Back to AGENTS.md](../../../AGENTS.md)

## 1) Script Proliferation Prevention (Constitutional)

- Enhance existing scripts; do not create wrapper/helper scripts.
- New shell scripts are only acceptable for tests under `tests/`.
- Before adding any script, check if logic can be integrated into an existing stage script.

Reference: [Script Proliferation](../principles/script-proliferation.md)

## 2) Single Entry Point for Users (Constitutional)

- User-facing instructions must use `./start.sh`.
- Developer-only execution paths are allowed but must be clearly labeled.

Reference: [Single Entry Point](../principles/single-entry-point.md)

## 3) Branch Preservation (Mandatory)

- Never delete branches without explicit user approval.
- Branch naming format: `YYYYMMDD-HHMMSS-type-description`.
- Merge to `main` with `--no-ff` when performing local merge workflows.

Reference: [Git Strategy](./git-strategy.md)

## 4) Local CI/CD First (Mandatory)

Run local validation before any GitHub push:

```bash
./.runners-local/workflows/gh-workflow-local.sh all
```

Reference: [Local CI/CD Operations](./local-cicd-operations.md)

## 5) Zero GitHub Actions Cost Policy

- Prefer local workflows for validation and build checks.
- Use GitHub-hosted workflows only when necessary for final remote deployment.
- Monitor billing with:

```bash
gh api user/settings/billing/actions
```

## 6) AI Tooling and Spec-Kit Expectations

Managed AI CLI tools:
- Claude Code
- Gemini CLI
- OpenAI Codex CLI
- GitHub Copilot CLI

Spec-Kit with Codex is project-scoped and should use per-repo `CODEX_HOME`:

```bash
echo 'export CODEX_HOME="$PWD/.codex"' > .envrc
direnv allow
```

## 7) Security Baseline

- Never commit secrets, tokens, or private credentials.
- Keep `.codex/` and other agent artifact paths out of git if they may contain sensitive material.
- Validate sudoers edits before applying; avoid broad `NOPASSWD: ALL` policies.

## 8) MCP Usage

- Context7 and GitHub MCP are recommended for documentation freshness and repository operations.
- Verify MCP configuration before relying on it in critical workflows.

References:
- [Context7 MCP](../guides/context7-mcp.md)
- [GitHub MCP](../guides/github-mcp.md)

[← Back to AGENTS.md](../../../AGENTS.md)
