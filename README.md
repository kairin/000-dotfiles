# dotfiles

Config templates plus a small Python+bash tool to bootstrap a developer
machine and scaffold AI-agent docs in any project. Status: **0.1.x beta** —
feature-complete, single-maintainer, suitable for personal and team use.

## Quick start

```bash
# 1. Clone (or symlink ./setup onto PATH).
git clone https://github.com/kairin/000-dotfiles.git ~/000-dotfiles

# 2. Bootstrap this computer (installs uv if missing, then shows a menu).
~/000-dotfiles/setup

# 3. Scaffold AI-agent docs in any project folder.
~/000-dotfiles/setup ~/Apps/my-project
```

`./setup` with no args audits the current machine and offers four choices:
apply safe dotfiles + fonts, show full diagnostics, show sign-in guidance, or
exit. Nothing is written without explicit confirmation.

## What you can do with this

| Scenario | Command |
|---|---|
| Fresh-machine setup (configs + Nerd Fonts) | `./setup` |
| Drift audit on an existing machine (read-only) | `./setup doctor` |
| Scaffold `AGENTS.md` + `CLAUDE.md`/`GEMINI.md` symlinks in a project | `./setup init --yes` |
| Verify project agent docs in CI / pre-commit | `./setup verify` |
| Add `.github/copilot-instructions.md` to a project | `./setup init --copilot --yes` |
| Reuse the Codacy coverage workflow in another repo | see `docs/codacy-coverage-rollout.md` |

Supported platforms: Ubuntu-style Linux, WSL (with Windows host font install),
Raspberry Pi, Pixel Terminal (ttyd), Pixel AVF (weston-terminal fallback).

## Repo layout

| Directory | Target on disk | Contents |
|---|---|---|
| `agents/` | a project root | `AGENTS.md` + `CLAUDE.md`/`GEMINI.md`/`copilot-instructions.md` templates |
| `claude/` | `~/.claude/` | `settings.json`, `keybindings.json`, global `CLAUDE.md` |
| `codex/` | `~/.codex/` | `config.toml`, `rules/default.rules` |
| `gemini/` | `~/.gemini/` | `settings.json`, global `GEMINI.md` |
| `gh/` | `~/.config/gh/` | `config.yml`, Codacy branch-protection checklist |
| `fish/` | `~/.config/fish/` | `fish_plugins`, `functions/direnv.fish`, `env.fish` |
| `git/` | `~/.config/git/` | `config` |
| `dotfiles_tools/` | — | Python validation/setup CLI (`python -m dotfiles_tools …`) |
| `setup` | `~/.local/bin/dotfiles-setup` (optional) | Self-locating bash entrypoint |
| `dotfiles-manifest.json` | — | Source of truth for what installs where |

Files ending in `.template` are copy-and-customize sources. Placeholders use
`{{UPPER_SNAKE_CASE}}` and must all be replaced before use.

## Setup script reference

| Command | What it does |
|---|---|
| `./setup` | Audit machine, present a menu, optionally apply non-protected dotfiles + font recipes |
| `./setup /path/to/project` | Inspect project folder, offer agent-doc actions |
| `./setup init [--project PATH] [--vars FILE] [--copilot] --yes` | Render `AGENTS.md` + `CLAUDE.md`/`GEMINI.md` symlinks; auto-discovers `project-vars.json` or `.dotfiles/project-vars.json` and infers defaults from `package.json`/`pyproject.toml`/`Cargo.toml`/`go.mod`/Makefile when missing |
| `./setup verify [--project PATH] [--copilot]` | Read-only check: requires no `uv`, suitable for CI |
| `./setup doctor [--home PATH] [--profile NAME]` | Read-only machine audit (wraps `dotfiles_tools doctor`) |

Install on `PATH`:

```bash
ln -s /path/to/000-dotfiles/setup ~/.local/bin/dotfiles-setup
dotfiles-setup verify --project ~/code/my-app
```

## Direct CLI (advanced)

`./setup` is a wrapper. The underlying commands are stable and useful for
automation:

```bash
uv run python -m dotfiles_tools doctor          --repo . --home "$HOME"
uv run python -m dotfiles_tools plan            --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply           --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools bootstrap-plan  --repo . --home "$HOME" --json
uv run python -m dotfiles_tools bootstrap-apply --repo . --home "$HOME" --yes
uv run python -m dotfiles_tools init-project    --repo . --project /path/to/project --vars project-vars.json --yes
```

`doctor` audits without writing. `plan` prints exact operations. `apply`
writes only after `--yes`. Existing differing files are backed up before
replacement. `bootstrap-plan`/`bootstrap-apply` add font recipes to the same
manifest operations. Every command supports `--json` for stable machine output.

### Protected files

Five manifest entries are protected by default (reported but never written):

- `git.config` → `~/.config/git/config` (committer identity)
- `fish.plugins` → `~/.config/fish/fish_plugins` (manually curated; needs `fisher update`)
- `repo.gitignore` → repo `.gitignore`
- `agents.claude-template`, `agents.gemini-template` → symlinks to `agents/AGENTS.md.template`

To include one explicitly, name its exact manifest ID:

```bash
uv run python -m dotfiles_tools apply --repo . --home "$HOME" \
  --profile machine --backup-dir "$HOME/.dotfiles-backups" \
  --include-protected git.config --yes
```

### Fonts

The font stage is catalog-driven. On Linux it manages Nerd Fonts archives
(`JetBrainsMono`, `FiraCode`, `Hack`, `Meslo`) cached in
`~/.cache/000-dotfiles/fonts/` and installs to `~/.local/share/fonts/`. It
also installs apt fallbacks (`fonts-noto-color-emoji`, `fonts-symbola`,
`fonts-freefont-ttf`, `fonts-dejavu-core`). Terminal checks always use
`* Nerd Font Mono` faces, never Propo. WSL additionally installs JetBrainsMono
on the Windows host and updates Windows Terminal defaults when discoverable.

### Project bootstrap example

```bash
cd ~/Apps/my-project
cat > project-vars.json <<'JSON'
{
  "PROJECT_NAME": "Example",
  "PROJECT_DESCRIPTION": "a concise description",
  "LANGUAGE": "Python",
  "PACKAGE_MANAGER": "uv",
  "RUNTIME_DESCRIPTION": "local CLI",
  "INSTALL_CMD": "uv sync",
  "RUN_CMD": "uv run python main.py",
  "TEST_CMD": "uv run pytest"
}
JSON

~/000-dotfiles/setup init --yes              # bootstrap + auto-verify
~/000-dotfiles/setup init --copilot --yes    # also write copilot file
~/000-dotfiles/setup verify                  # re-check
```

When `project-vars.json` is missing and `--yes` is supplied, defaults are
inferred from `package.json`/`pyproject.toml`/`Cargo.toml`/`go.mod`/Makefile
and persisted to `<project>/.dotfiles/project-vars.json`.

## Validation and coverage

```bash
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
```

CI runs the same validation suite on pushes and pull requests and generates
`coverage.xml`. Codacy upload is attempted on push events only when the
`CODACY_PROJECT_TOKEN` GitHub secret is configured. See
`docs/codacy-coverage-rollout.md` for replicating this pattern in other repos.

## Conventions and safety

- **No secrets.** No tokens, passwords, or API keys live in this repo. Auth
  files (`hosts.yml`, `auth.json`, `oauth_creds.json`, `token`) are
  `.gitignore`d. Sign in via `huggingface-cli login`, `gh auth login`,
  `codex auth`, etc.
- **Symlinks for AI-agent docs.** Root `CLAUDE.md`/`GEMINI.md` symlink to
  `AGENTS.md`; `agents/CLAUDE.md.template` and `agents/GEMINI.md.template`
  symlink to `agents/AGENTS.md.template`. One source of truth per scope.
- **Backups before replace.** Drifted targets are copied to the backup dir
  (default `~/.dotfiles-backups`) before being overwritten.
- **Stop on first failure.** `apply` halts on the first failed write and
  reports `partial` status with completed operations and backups intact.

## Spec and contributing

The implementation plan, contracts, and task list live under
`specs/001-dotfiles-bootstrap-validation/`. AI-agent guidelines are in
`AGENTS.md` (which `CLAUDE.md` and `GEMINI.md` symlink to). When changing
templates, edit the `.template` file directly and run `git diff --staged`
before every commit to catch tokens or personal paths.
