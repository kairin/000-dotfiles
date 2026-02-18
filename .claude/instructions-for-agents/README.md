# Instructions for Agents - Documentation Index

This directory contains modular policy and implementation docs referenced by `AGENTS.md`.

## Layout

- `requirements/`: mandatory policies and operational constraints
- `architecture/`: repository and installer architecture
- `guides/`: task-oriented setup and operations guides
- `principles/`: constitutional rules
- `tools/`: per-tool implementation notes

## Start Here

1. `requirements/CRITICAL-requirements.md`
2. `requirements/git-strategy.md`
3. `requirements/local-cicd-operations.md`
4. `principles/script-proliferation.md`

## Key Rule Reminders

- User-facing setup command is `./start.sh`.
- Run local workflow before remote operations:
  `./.runners-local/workflows/gh-workflow-local.sh all`
- Preserve branches unless user explicitly requests deletion.
- Keep `CLAUDE.md` and `GEMINI.md` as symlinks to `AGENTS.md`.
