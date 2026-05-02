# dotfiles — AI Agent Guidelines

Single source of truth for LLM agents. `CLAUDE.md` and `GEMINI.md` symlink to this file.

For human-facing setup instructions (quick start, scenarios, command reference), see `README.md`. This file focuses on conventions agents must respect.

## What this repo is

A collection of config templates for AI coding tools (Claude Code, Codex, Gemini CLI, gh CLI) and shell environment (fish, git), plus a small Python CLI (`dotfiles_tools`) and a bash entrypoint (`./setup`) that audit and apply those templates. Every file with a `.template` suffix is meant to be copied to its target path and customized — it is never executed or sourced directly from here.

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
agents/             Project-level agent doc templates (AGENTS.md, CLAUDE.md, GEMINI.md, copilot-instructions.md)
claude/             ~/.claude/ templates (settings.json, keybindings.json, CLAUDE.md)
codex/              ~/.codex/ templates (config.toml, rules/default.rules)
gemini/             ~/.gemini/ templates (settings.json, GEMINI.md)
gh/                 ~/.config/gh/ templates (config.yml)
fish/               ~/.config/fish/ templates and live files (fish_plugins, direnv.fish, env.fish)
git/                ~/.config/git/ live files (config)
dotfiles_tools/     Python validation/setup CLI (stdlib only)
tests/              unittest suite (uv-managed)
specs/              Spec Kit feature specs (current: 001-dotfiles-bootstrap-validation)
docs/               Operational docs (e.g. Codacy coverage rollout)
setup               Bash entrypoint that wraps dotfiles_tools with sensible defaults
dotfiles-manifest.json  Source of truth for what installs where
```

## Template Convention

- Files ending in `.template` are copy-and-customize — never source or execute from this path.
- Placeholders follow the pattern `{ {UPPER_SNAKE_CASE} }` (double-braces with no spaces) and must all be replaced before use.
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
- Adding a curl-based installer to `TOOL_BASELINE`: declare `"interpreter": "..."` in `install_args` if the script is anything other than bash. `_execute_curl` runs the script under that interpreter (Ubuntu's default `/bin/sh` is dash and rejects bash extensions).
- Adding a new bootstrap tool to `TOOL_BASELINE`: declare a `post_install` tuple (may be empty) listing follow-up actions. `kind="auto"` runs when the user passes `--yes`; `kind="guidance"` only prints the command. Templates may use `{which:<name>}` and `{user}` placeholders; unresolved placeholders downgrade to guidance automatically.

## Development Workflow

```bash
git status                    # check what changed
git diff                      # review before staging
git add <specific files>      # never git add -A
git commit -m "..."
```

Runtime validation tooling uses Python standard library modules and uv-managed
developer commands:

```bash
uv run python -m dotfiles_tools doctor --repo . --home "$HOME"
uv run python -m dotfiles_tools plan --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools init-project --repo . --project /path/to/project --vars project-vars.json --yes
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
```

Do not add lock files unless runtime dependencies are introduced and the Spec
Kit plan explains why they are needed. Coverage is only meaningful for real
validation/setup code and must generate `coverage.xml` before Codacy upload.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, see the spec documents in
`specs/`. Recent implementations (setup menu recommendation, optional integrations)
are complete. Check `specs/` for any new active specifications or design documents.
<!-- SPECKIT END -->
