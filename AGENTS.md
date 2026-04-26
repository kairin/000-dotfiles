# dotfiles — AI Agent Guidelines

Single source of truth for LLM agents. `CLAUDE.md` and `GEMINI.md` symlink to this file.

## What this repo is

A collection of config templates for AI coding tools (Claude Code, Codex, Gemini CLI, gh CLI) and shell environment (fish, git). Every file with a `.template` suffix is meant to be copied to its target path and customized — it is never executed or sourced directly from here.

## Protected Files — NEVER Modify Without Explicit Per-File Directive

| File | Why protected |
|---|---|
| `git/config` | Contains committer identity; silent changes affect all git operations. |
| `fish/fish_plugins` | Plugin list is manually curated; additions require a `fisher update` run. |
| `.gitignore` | Changing exclusion rules can accidentally expose secrets to git history. |
| `agents/CLAUDE.md.template`, `agents/GEMINI.md.template` | These are symlinks — rewriting them as regular files breaks the single-source pattern. |

**Rules:**
- Read any file freely for context. Do not write without explicit instruction.
- If a task seems to require touching a protected file, stop and ask.
- `git show origin/main:<file>` is the authoritative original.

## Repo Structure

```
agents/     Project-level agent instruction templates (AGENTS.md, CLAUDE.md, GEMINI.md, copilot-instructions.md)
claude/     ~/.claude/ templates (settings.json, keybindings.json, CLAUDE.md)
codex/      ~/.codex/ templates (config.toml, rules/default.rules)
gemini/     ~/.gemini/ templates (settings.json, GEMINI.md)
gh/         ~/.config/gh/ templates (config.yml)
fish/       ~/.config/fish/ templates and live files (fish_plugins, direnv.fish, env.fish)
git/        ~/.config/git/ live files (config)
```

## Template Convention

- Files ending in `.template` are copy-and-customize — never source or execute from this path.
- Placeholders use `{{UPPER_SNAKE_CASE}}` and must all be replaced before use.
- No secrets, tokens, or API keys are stored anywhere in this repo. Auth files are excluded by `.gitignore` and the global git ignore.

## Symlink Convention

`CLAUDE.md` and `GEMINI.md` at the repo root are symlinks to `AGENTS.md`. At the project level, `agents/CLAUDE.md.template` and `agents/GEMINI.md.template` are symlinks to `agents/AGENTS.md.template`. This keeps one source of truth per scope.

To verify the symlinks are intact:
```bash
ls -la CLAUDE.md GEMINI.md
# expected: both point to AGENTS.md
```

## Making Changes

- Adding a new tool config: create a `<tool>/` directory with `<file>.template` files; update `README.md` table and the bootstrap commands.
- Updating an existing template: edit the `.template` file directly; note in the commit message if any placeholder names changed.
- Never commit files containing real credentials. Run `git diff --staged` before every commit and check for tokens, keys, or personal paths.

## Development Workflow

```bash
git status                    # check what changed
git diff                      # review before staging
git add <specific files>      # never git add -A
git commit -m "..."
```

No build step, no tests, no lock files. Changes are valid the moment the template content is correct and placeholders are documented.
