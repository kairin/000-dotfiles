---
name: bcm-direnv-codacy
description: Load BCM's direnv environment and handle Codacy CLI and MCP authentication safely.
---

# BCM Direnv + Codacy

Use this skill when a task depends on the local shell environment, Codacy tokens, or Codacy tooling.

## Environment Load Path

1. Check `ls -l .envrc`.
2. If permissions are not `-r--r--r--`, stop and ask the user to run `chmod 444 .envrc`.
3. Run `direnv allow` in the repo root.
4. Treat `.envrc.local` as the source of local secrets and machine-specific tokens.

`.envrc` only loads `.envrc.local` with `source_env_if_exists`, so any Codacy variable must be exported there or by another direnv-loaded file.

**IMPORTANT:** `.envrc.local` **must be in `.gitignore`** — it contains machine-specific secrets and tokens that should never be committed to version control.

## Codacy Tooling

- `codacy-cli analyze` can use `CODACY_API_TOKEN` when fetching Codacy configuration from the API.
- `codacy-cli upload` uses `CODACY_PROJECT_TOKEN` for SARIF uploads.
- `mcp__codacy__*` requires `CODACY_ACCOUNT_TOKEN`.

## Startup Checks

```bash
uv sync
uv run python --version
codacy-cli --help
```

If a Codacy command fails because a token is missing, name the missing variable explicitly and point back to `direnv` rather than guessing.
