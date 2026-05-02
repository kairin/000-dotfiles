# Repo Layout

This repo stores templates, validation code, docs, and the interactive setup wrapper.

## Top-Level Layout

| Directory or file | Purpose |
|---|---|
| `agents/` | Project-level agent doc templates |
| `claude/` | `~/.claude/` templates |
| `codex/` | `~/.codex/` templates |
| `gemini/` | `~/.gemini/` templates |
| `gh/` | `~/.config/gh/` templates |
| `fish/` | `~/.config/fish/` live files and templates |
| `git/` | `~/.config/git/` live files |
| `dotfiles_tools/` | Python validation and setup CLI |
| `setup` | Bash entrypoint that wraps `dotfiles_tools` |
| `tests/` | Unit tests for the CLI, docs, and workflow contract |
| `docs/` | User docs, architecture notes, and rollout guidance |
| `specs/` | Spec Kit feature specs and task artifacts |
| `dotfiles-manifest.json` | Source of truth for install targets |

## Template Convention

Files ending in `.template` are copy-and-customize sources. They are not executed or sourced directly from the repo.
Placeholders use `{{UPPER_SNAKE_CASE}}` and should be fully replaced before use.

## Symlink Convention

The root `CLAUDE.md` and `GEMINI.md` files are symlinks to `AGENTS.md`.
At the project level, the agent templates in `agents/` use the same single-source pattern.
