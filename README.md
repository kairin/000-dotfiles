# dotfiles

Config templates and tools to bootstrap a developer machine and scaffold AI
agent docs in any project. Status: **0.1.x beta** — feature-complete,
single-maintainer, suitable for personal and team use.

## What is this?

You've just bought a new laptop, or your hard drive died, or you're setting up
CI. On a fresh machine you normally spend hours manually installing tools,
copying config files, and signing in. This repo automates that: **one command
installs your full tool stack and applies your configs**, and repeat runs
catch and apply any drift.

This repo manages configs for AI coding tools (Claude Code, Codex, Gemini CLI,
Copilot CLI), shell environment (fish, direnv), version control (git, gh),
and terminal fonts (Nerd Fonts). It also scaffolds AI agent guidelines
(`AGENTS.md` and symlinked `CLAUDE.md`/`GEMINI.md`) for projects.

For deep system-design and convention claims, see
[ARCHITECTURE.md](ARCHITECTURE.md).

## What gets installed

| Category | Tools | Notes |
|---|---|---|
| **Shell & environment** | fish, direnv | Shell and per-project env vars |
| **Version control** | git, GitHub CLI | Git + GitHub; auth is manual |
| **Python toolchain** | uv | Fast Python installer & package manager |
| **AI coding assistants** | Claude Code, Codex, Gemini CLI, Copilot CLI, SpecKit | Latest versions; sign-in on first run |
| **Fonts** | JetBrainsMono, FiraCode, Hack, MesloLGS Nerd Fonts | Auto-downloaded and installed |
| **Project scaffolding** | AI agent docs | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` per project |
| **Container runtime** | Docker Engine | Required for `gstack-browser` container (Ubuntu 24.04 + Playwright) |
| **HuggingFace Hub** | `hf` (optional) | `uv tool install huggingface-hub`; sign in with `hf auth login` |
| **Local code analysis** | Codacy CLI (optional) | curl installer; for local Codacy runs |

Full tool catalog with install methods and post-install actions:
[ARCHITECTURE.md#tool-catalog](ARCHITECTURE.md#tool-catalog).

## Quick start

### Clone and run setup on a fresh machine

```bash
git clone https://github.com/kairin/000-dotfiles.git ~/000-dotfiles
~/000-dotfiles/setup
# → Menu appears. Choose 1 (developer tool submenu), then 2 (safe changes). Done in ~5 min.
```

### Scaffold AI agent docs in a project

```bash
cd ~/Apps/my-project
~/000-dotfiles/setup init --yes
# → Creates AGENTS.md, CLAUDE.md, GEMINI.md. Your AI tools now know your codebase.
```

### Update a machine you already set up

```bash
~/000-dotfiles/setup
# → Menu shows state. Choose 2 to apply any drift. Tools update automatically.
```

## How it works

`./setup` audits the machine and shows a 7-option menu. Option numbers are
stable; the `[recommended]` tag highlights the next action for the machine's
current state.

```
./setup
  ├─ menu
  │   ├─ 1  Install / update developer tools
  │   ├─ 2  Apply safe non-protected dotfiles
  │   ├─ 3  Show full technical details
  │   ├─ 4  Show tool and sign-in guidance
  │   ├─ 5  Configure / verify API tokens   (GitHub, HuggingFace, Codacy)
  │   ├─ 6  Install / update Git hooks
  │   └─ 7  Exit
  └─ writes only after explicit [y/N]; backups go to ~/.dotfiles-backups/
```

Detailed walkthroughs, every menu screen, and the four sub-flows
(bootstrap, drift detection, safe changes, validation) live at
[ARCHITECTURE.md#system-design](ARCHITECTURE.md#system-design) and the
tutorial at [docs/getting-started.md](docs/getting-started.md).

## Safety <!-- mirrors: ARCHITECTURE.md#protected-files-canonical-list -->

Four files in this repo are **protected** — never modified without an
explicit per-file directive:

- `git/config` (committer identity)
- `fish/fish_plugins` (manually curated)
- `.gitignore` (silent edits can leak secrets)
- `agents/CLAUDE.md.template` and `agents/GEMINI.md.template` (symlinks)

**No secrets, tokens, or API keys live in this repo.** Auth files
(`hosts.yml`, `auth.json`, `oauth_creds.json`, `token`) are gitignored.
Sign in via `gh auth login`, `codex auth`, `claude login`, etc.

**Always merge via `./setup ship`** — it polls all four required Codacy
checks and squash-merges only when they all report green. See
[ARCHITECTURE.md#protected-files](ARCHITECTURE.md#protected-files-canonical-list),
[ARCHITECTURE.md#auth-guidance](ARCHITECTURE.md#auth-guidance), and
[ARCHITECTURE.md#ship](ARCHITECTURE.md#-setup-ship-) for details.

## What you can do with this

| Scenario | Command |
|---|---|
| Fresh-machine setup (tools + configs + fonts) | `./setup` |
| Check current state (read-only) | `./setup doctor` |
| Scaffold `AGENTS.md` + `CLAUDE.md`/`GEMINI.md` in a project | `./setup init --yes` |
| Verify agent docs in CI / pre-commit (no uv required) | `./setup verify` |
| Audit machine + API credential status | `./setup` → option 3 |
| Manage optional integrations (GitHub, HF, Codacy) | `./setup` → option 5 |
| Upgrade installed tools | `./setup` → option 1 |
| Apply config drift | `./setup` → option 2 |

Supported platforms: Ubuntu-style Linux, WSL (with Windows host font install),
Raspberry Pi, Pixel Terminal, Pixel AVF.

## Going deeper

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Canonical hub: system design, tool catalog, MCP, conventions
- **[Getting Started](docs/getting-started.md)** — Step-by-step first-time setup, ongoing maintenance, troubleshooting
- **[Codacy workflow templates](docs/codacy-workflow-templates.md)** — Coverage upload snippets for Python, Node, mixed repos
- **[GitHub Actions usage baseline](docs/operations/github-actions-usage-baseline.md)** — Live Actions usage history
- **[AGENTS.md](AGENTS.md)** — AI agent guidelines (CLAUDE.md and GEMINI.md symlink to this)
- **[Changelog](CHANGELOG.md)** — Version history

## Repo layout

| Directory | Target on disk | Contents |
|---|---|---|
| `agents/` | a project root | `AGENTS.md` + `CLAUDE.md`/`GEMINI.md`/`copilot-instructions.md` templates |
| `claude/` | `~/.claude/` | `settings.json`, `keybindings.json`, global `CLAUDE.md`, `hooks/load-project-env.sh` |
| `codex/` | `~/.codex/` | `config.toml`, global `AGENTS.md`, `rules/default.rules` |
| `gemini/` | `~/.gemini/` | `settings.json`, global `GEMINI.md` |
| `copilot/` | `~/.copilot/` | global `copilot-instructions.md` |
| `gh/` | `~/.config/gh/` | `config.yml` |
| `fish/` | `~/.config/fish/` | `fish_plugins`, `conf.d/direnv.fish`, `conf.d/env.fish`, `functions/direnv.fish` |
| `git/` | `~/.config/git/` | `config` |
| `dotfiles_tools/` | — | Python validation/setup CLI (`python -m dotfiles_tools …`) |
| `scripts/` | — | Helper shell scripts (`install-hooks.sh`, `quality-pipeline.sh`, `hooks/`) |
| `docker/` | — | Dockerfiles and compose configs (`gstack-browser/`) |
| `setup` | `~/.local/bin/dotfiles-setup` (optional) | Bash entrypoint |
| `dotfiles-manifest.json` | — | Source of truth for what installs where |
| `specs/`, `docs/` | — | Specs, operational docs, design history |

Files ending in `.template` are copy-and-customize sources. Placeholders
follow `{{UPPER_SNAKE_CASE}}` and must all be replaced before use.

## Setup script reference

| Command | What it does |
|---|---|
| `./setup` | Audit machine, present menu, optionally apply safe-changes submenu |
| `./setup /path/to/project` | Inspect project, offer agent-doc actions |
| `./setup init [--project PATH] [--vars FILE] [--copilot] --yes` | Render `AGENTS.md` + symlinks |
| `./setup verify [--project PATH] [--copilot]` | Read-only check; no `uv` required (CI-safe) |
| `./setup doctor [--home PATH] [--profile NAME]` | Read-only machine audit |
| `./setup quality` | Run local quality pipeline (`scripts/quality-pipeline.sh`) |
| `./setup hooks` | Install/update Git hooks (writes `.git/hooks/pre-push`) |
| `./setup docker-build` | Build the `gstack-browser:latest` Ubuntu 24.04 image |
| `./setup gstack-setup [path]` | Run gstack's setup inside the container |
| `./setup gstack-codex [path]` | Open Codex inside the container |
| `./setup gstack-shell` | Shell into the running container |
| `./setup gstack-exec [--workdir PATH] -- <command>` | Run `<command>` inside the container |
| `./setup codacy-plan --repo OWNER/REPO` | Print the rollout plan for a Codacy-managed repo |
| `./setup repair-codacy-env [<project>] [--owner OWNER] [--repo REPO]` | Repair direnv-managed Codacy variables in a project |
| `./setup ship [<pr-number>]` | Finalize a PR (refresh, poll required checks, squash-merge) |

### Direct CLI (advanced)

`./setup` wraps stable Python commands. For automation:

```bash
uv run python -m dotfiles_tools doctor       --repo . --home "$HOME"
uv run python -m dotfiles_tools plan         --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply        --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools init-project --repo . --project /path/to/project --vars project-vars.json --yes
```

`doctor` audits without writing; `plan` prints exact operations; `apply`
writes only after `--yes` (with backups). Every command supports `--json`.

## Hook trigger map

The Git repo hook (`.git/hooks/pre-push`) blocks pushes to `main` regardless
of which CLI initiated the push. Install once per repo via `./setup hooks`.

- **Claude Code:** `/hooks` slash command; SessionStart loads project env.
- **Gemini CLI:** `gemini hooks --help`; do NOT run `gemini hooks migrate`.
- **Codex CLI:** loads `AGENTS.md` context only.
- **Copilot CLI:** `/instructions`, `/env`; `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`.

Full per-CLI matrix: [ARCHITECTURE.md#hook-trigger-map](ARCHITECTURE.md#hook-trigger-map).

## Validation and coverage

```bash
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
```

CI runs the same suite on pushes and PRs. Coverage upload to Codacy is
attempted on push events only when `CODACY_ACCOUNT_TOKEN` is configured.
See `docs/codacy-coverage-rollout.md` for replicating this in other repos.

For local Codacy SARIF pipeline and the 7 quality-pipeline stages, see
[ARCHITECTURE.md#codacy-cli-configuration](ARCHITECTURE.md#codacy-cli-configuration)
and [ARCHITECTURE.md#quality-pipeline](ARCHITECTURE.md#local-quality-pipeline).
