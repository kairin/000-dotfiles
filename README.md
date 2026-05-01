# dotfiles

Config templates for AI coding tools and shell environment.

## What's here

| Directory | Target path | Contents |
|---|---|---|
| `agents/` | project root | `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` / `copilot-instructions.md` templates |
| `claude/` | `~/.claude/` | `settings.json`, `keybindings.json`, global `CLAUDE.md` |
| `codex/` | `~/.codex/` | `config.toml`, `rules/default.rules` |
| `gemini/` | `~/.gemini/` | `settings.json`, global `GEMINI.md` |
| `gh/` | `~/.config/gh/` | `config.yml`, Codacy branch protection checklist |
| `fish/` | `~/.config/fish/` | `fish_plugins`, `functions/direnv.fish`, `env.fish` |
| `git/` | `~/.config/git/` | `config` |

## Conventions

**`.template` suffix** — copy to the target path and fill in any `{{PLACEHOLDERS}}`.

**Symlinks** — `CLAUDE.md` and `GEMINI.md` always symlink to `AGENTS.md` so there is one source of truth per project:

```bash
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md GEMINI.md
```

**Secrets** — no tokens, passwords, or API keys are ever stored here. Auth files (`hosts.yml`, `auth.json`, `oauth_creds.json`, `token`) are excluded. Use `huggingface-cli login`, `gh auth login`, `codex auth`, and env vars loaded from files outside this repo.

## Bootstrap a new machine

```bash
uv run python -m dotfiles_tools doctor --repo . --home "$HOME"
uv run python -m dotfiles_tools plan --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
```

`dotfiles-manifest.json` is the source of truth for machine targets. `doctor`
audits without writing, `plan` prints exact operations, and `apply` writes only
after `--yes`. Existing differing files are backed up before replacement.

Protected entries are reported but skipped by default:

- `git.config` -> `~/.config/git/config`
- `fish.plugins` -> `~/.config/fish/fish_plugins`
- `repo.gitignore` -> repository `.gitignore`
- `agents.claude-template` and `agents.gemini-template` -> symlink templates

To include a protected machine target, name the exact manifest ID:

```bash
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --include-protected git.config --yes
```

## Bootstrap a new project repo

```bash
cat > project-vars.json <<'JSON'
{
  "PROJECT_NAME": "Example Project",
  "PROJECT_DESCRIPTION": "a concise project description",
  "LANGUAGE": "Python",
  "PACKAGE_MANAGER": "uv",
  "RUNTIME_DESCRIPTION": "local CLI",
  "INSTALL_CMD": "uv run python -m unittest discover -s tests",
  "RUN_CMD": "uv run python -m dotfiles_tools doctor --repo . --home \"$HOME\"",
  "TEST_CMD": "uv run python -m unittest discover -s tests"
}
JSON

uv run python -m dotfiles_tools init-project --repo path/to/dotfiles --project . --vars project-vars.json --yes
uv run python -m dotfiles_tools init-project --repo path/to/dotfiles --project . --vars project-vars.json --copilot --yes
```

`init-project` renders `agents/AGENTS.md.template`, creates `CLAUDE.md` and
`GEMINI.md` symlinks to `AGENTS.md`, and fails if required placeholders remain.

## Validation and coverage

```bash
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
test -f coverage.xml
```

CI runs the same validation suite and generates `coverage.xml`. Codacy upload is
attempted only when the `CODACY_COVERAGE_API_TOKEN` GitHub Actions secret is
configured.

For the reusable setup checklist and current Codacy rollout status, see
`docs/codacy-coverage-rollout.md`.
