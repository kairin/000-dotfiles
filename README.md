# dotfiles

Config templates and tools to bootstrap a developer machine and scaffold AI agent docs in any
project. Status: **0.1.x beta** — feature-complete, single-maintainer, suitable for personal
and team use.

## What is this?

You've just bought a new laptop (or your hard drive died, or you're setting up CI). On a
fresh machine, you normally spend hours manually installing tools, copying config files, and
signing in to each one. This repo automates that: **one command installs your full tool stack
and applies your configs.** Repeated runs apply any config drift—changes you've made that
differ from the repo's templates.

This particular repo manages configs for AI coding tools (Claude Code, Codex, Gemini,
Copilot), shell customization (fish, direnv), version control (git, gh), and terminal fonts
(Nerd Fonts). It also scaffolds AI agent guidelines for your projects so Claude Code and
other tools know your codebase conventions.

## What gets installed

| Category | Tools | Notes |
|---|---|---|
| **Shell & environment** | fish, direnv | Shell and per-project env vars |
| **Version control** | git, GitHub CLI | Git + GitHub; auth is manual |
| **Python toolchain** | uv | Fast Python installer & package manager |
| **AI coding assistants** | Claude Code, Codex, Gemini, Copilot, SpecKit | Latest versions; sign-in on first run |
| **Fonts** | JetBrainsMono, FiraCode, Hack, MesloLGS Nerd Fonts | Auto-downloaded and installed |
| **Project scaffolding** | AI agent docs | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` per project |

## Quick start

### Clone and run setup on a fresh machine

```bash
git clone https://github.com/kairin/000-dotfiles.git ~/000-dotfiles
~/000-dotfiles/setup
# → Menu appears. Choose 1 (open the phased tool submenu), then 2 (open safe changes). Done in ~5 min.
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

---

## How it works — setup flow

When you run `./setup`, the script audits your machine and shows a **6-option menu**. The
option numbers **never change**, but the `[recommended]` tag highlights which action fits
your current state. Option 2 opens a safe-changes submenu so you can see which files and
fonts are affected before you apply anything.

### Fresh machine (tools missing)

```
$ ~/000-dotfiles/setup
                         ↓
        ╔═══════════════════════════════════════╗
        ║ Machine setup summary                 ║
        ║ Home: /home/user                      ║
        ║ Tools: 7/10 missing                   ║
        ║ Configs: N/A (tools not installed)    ║
        ╚═══════════════════════════════════════╝
                         ↓
   1. Install / update developer tools   [recommended] ← CHOOSE THIS
   2. Apply safe non-protected dotfiles.
   3. Show full technical details
   4. Show tool and sign-in guidance
   5. Configure / verify API tokens
   6. Exit without writing
                         ↓
        Choose [1-6]: 1
                         ↓
   [Developer tool phases submenu opens]
   1. Preview dev-base packages
   2. Apply dev-base packages
   3. Preview individual tool installers
   4. Apply individual tool installers
   5. Split post-install verification and guidance
   6. Back to main menu
                         ↓
   Choose [1-6]: 2
                         ↓
   [Preview shows the dev-base apt bundle]
                         ↓
   Apply dev-base packages actions? [y/N]: y
                         ↓
   [Dev-base packages updated]
   [Return to the submenu or run option 5 for verification/sign-in guidance]
                         ↓
   Menu reappears. Now tool count reflects the phase you just applied.
                         ↓
   1. Install / update developer tools
   2. Apply safe non-protected dotfiles.  [recommended] ← NOW CHOOSE THIS
   3. Show full technical details
   4. Show tool and sign-in guidance
   5. Configure / verify API tokens
   6. Exit without writing
                         ↓
        Choose [1-6]: 2
                         ↓
   [Safe changes submenu shows dotfiles vs fonts]
                         ↓
        Choose [1-4]: 3
                         ↓
   [Configs + fonts installed; backups created]
                         ↓
   1. Install / update developer tools
   2. Apply safe non-protected dotfiles.
   3. Show full technical details
   4. Show tool and sign-in guidance
   5. Configure / verify API tokens. Opens a submenu that splits
      verification-only, auto post-install actions, and manual guidance.
   6. Exit without writing
                         ↓
        Choose [1-6]: 5
                         ↓
   [Post-install submenu shows verify / auto / guidance]
                         ↓
        DONE. Run these sign-in commands:
        $ gh auth login
        $ claude /login
        $ codex auth
        $ gemini
        $ copilot /login
```

### Configured machine (tools present, configs drifted)

```
$ ~/000-dotfiles/setup
                         ↓
        ╔═══════════════════════════════════════╗
        ║ Machine setup summary                 ║
        ║ Home: /home/user                      ║
        ║ Tools: 10/10 found                    ║
        ║ Configs: 2 drifted, 8 current         ║
        ╚═══════════════════════════════════════╝
                         ↓
   1. Install / update developer tools
   2. Apply safe non-protected dotfiles.  [recommended] ← CHOOSE THIS
   3. Show full technical details
   4. Show tool and sign-in guidance
   5. Configure / verify API tokens
   6. Exit without writing
                         ↓
        Choose [1-6]: 2
                         ↓
   [Safe changes submenu shows dotfiles vs fonts]
                         ↓
        Choose [1-4]: 3
                         ↓
   [2 files written with backups]
   [Fonts already installed, no changes]
                         ↓
        DONE.
```

Nothing is written without your explicit confirmation (`[y/N]`). Files are backed up before overwrite (default: `~/.dotfiles-backups/`). The script is idempotent—safe to run repeatedly. User-customizable files (such as `~/.claude/settings.json`, `~/.config/gh/config.yml`, `~/.config/fish/env.fish`, and 7 others) skip drift detection and are never silently overwritten by option 2.

---

## What you can do with this

| Scenario | Command |
|---|---|
| Fresh-machine setup (tools + configs + fonts) | `./setup` |
| Check current state (read-only) | `./setup doctor` |
| Scaffold `AGENTS.md` + `CLAUDE.md`/`GEMINI.md` in a project | `./setup init --yes` |
| Verify agent docs in CI / pre-commit (no uv required) | `./setup verify` |
| Audit machine and show API credential status (GitHub, HuggingFace) | `./setup` → choose option 3 |
| Manage optional integrations (GitHub, HuggingFace, Codacy) | `./setup` → choose option 4 |
| Upgrade installed tools | `./setup` → choose option 1 |
| Apply config drift | `./setup` → choose option 2 |

Supported platforms: Ubuntu-style Linux, WSL (with Windows host font install), Raspberry Pi, Pixel Terminal, Pixel AVF.

---

## Going deeper

- **[Getting Started](docs/getting-started.md)** — Step-by-step first-time setup, ongoing maintenance, AI agent doc scaffolding, troubleshooting
- **[GitHub Actions usage baseline](docs/operations/github-actions-usage-baseline.md)** — Live repo-level Actions history for comparing GitHub-hosted and local-runner usage
- **[Setup script reference](#setup-script-reference)** (below) — All commands and options
- **[Direct CLI reference](#direct-cli-advanced)** (below) — Stable commands for automation
- **[Protected files](#protected-files)** — Which files are never auto-overwritten
- **[Project bootstrap example](#project-bootstrap-example)** (below) — Detailed walkthrough
- **[Validation and coverage](#validation-and-coverage)** (below) — Running tests
- **[Changelog](CHANGELOG.md)** — Version history and what was built

## Is this a good dotfiles repo? ✓

A good dotfiles repo should:

| Requirement | Status |
|---|---|
| Version-controlled config templates | ✓ All `.template` files tracked |
| One-command bootstrap on a fresh machine | ✓ `./setup` handles it |
| Idempotent — safe to run repeatedly | ✓ No errors from running twice |
| Backup before overwrite | ✓ Default: `~/.dotfiles-backups/` |
| Never writes without confirmation | ✓ Requires explicit `[y/N]` |
| Protected files never auto-overwritten | ✓ git config, fish plugins, etc. |
| No secrets or tokens committed | ✓ Auth files `.gitignore`d |
| Multi-platform support | ✓ Linux, WSL, Pi, Pixel Terminal |
| Validation & test coverage | ✓ 120 unit tests; CI/CD integration |
| AI tool config management | ✓ Claude, Codex, Gemini, Copilot |
| Per-project AI agent scaffolding | ✓ `AGENTS.md` + symlinks |

---

## Repo layout

| Directory | Target on disk | Contents |
|---|---|---|
| `agents/` | a project root | `AGENTS.md` + `CLAUDE.md`/`GEMINI.md`/`copilot-instructions.md` templates |
| `claude/` | `~/.claude/` | `settings.json`, `keybindings.json`, global `CLAUDE.md`, `hooks/load-project-env.sh` |
| `codex/` | `~/.codex/` | `config.toml`, `rules/default.rules` |
| `gemini/` | `~/.gemini/` | `settings.json`, global `GEMINI.md` |
| `gh/` | `~/.config/gh/` | `config.yml` |
| `fish/` | `~/.config/fish/` | `fish_plugins`, `conf.d/direnv.fish` (auto-installs direnv hook), `functions/direnv.fish`, `env.fish` |
| `git/` | `~/.config/git/` | `config` |
| `dotfiles_tools/` | — | Python validation/setup CLI (`python -m dotfiles_tools …`) |
| `setup` | `~/.local/bin/dotfiles-setup` (optional) | Self-locating bash entrypoint |
| `dotfiles-manifest.json` | — | Source of truth for what installs where |
| `specs/` | — | Design specification, task tracking, contracts |
| `docs/` | — | Getting started guide, operations docs, issue tracking |

Files ending in `.template` are copy-and-customize sources. Placeholders follow the pattern of double-braces with upper-snake-case content (e.g. `{{PROJECT_NAME}}`) and must all be replaced before use.

---

## Setup script reference

| Command | What it does |
|---|---|
| `./setup` | Audit machine, present a menu, optionally apply a safe-changes submenu for non-protected dotfiles + fonts |
| `./setup /path/to/project` | Inspect project folder, offer agent-doc actions |
| `./setup init [--project PATH] [--vars FILE] [--copilot] --yes` | Render `AGENTS.md` + `CLAUDE.md`/`GEMINI.md` symlinks; auto-discovers `project-vars.json` or `.dotfiles/project-vars.json` and infers defaults from `package.json`/`pyproject.toml`/`Cargo.toml`/`go.mod`/Makefile when missing |
| `./setup verify [--project PATH] [--copilot]` | Read-only check: requires no `uv`, suitable for CI |
| `./setup doctor [--home PATH] [--profile NAME]` | Read-only machine audit (wraps `dotfiles_tools doctor`) |
| `./setup quality` | Run the local quality pipeline (`scripts/quality-pipeline.sh`): tests, coverage, Codacy upload |
| `./setup ship [<pr-number>]` | Finalize a PR: refresh branch, re-upload Codacy SARIF, poll required checks, squash-merge |

Menu options during `./setup`:
- **Option 1:** Install or update developer tools. Opens a submenu that
  splits dev-base packages, tool installers, and post-install verification so
  you can isolate slow phases.
- **Option 2:** Apply safe non-protected dotfiles. Opens a submenu that separates
  dotfiles/config files from fonts before applying the combined safe changes.
- **Option 3:** Show full technical details (machine state, versions, all pending operations)
- **Option 4:** Manage optional integrations (GitHub auth, HuggingFace token configuration, Codacy setup). GitHub CLI installs via `apt`; HuggingFace CLI (`hf`) installs via `uv tool install huggingface-hub`; use `hf auth login` to authenticate. Machine bootstrap calls `ensure_mcp_servers()`, which auto-registers the **GitHub MCP** server (uses `GITHUB_TOKEN`) and **Codacy MCP** server (uses `CODACY_ACCOUNT_TOKEN`) with the Claude CLI.

Install on `PATH`:

```bash
ln -s /path/to/000-dotfiles/setup ~/.local/bin/dotfiles-setup
dotfiles-setup verify --project ~/code/my-app
```

### Finalizing a PR

Once a PR is open, `./setup ship` drives it to merged:

```bash
# After your PR is open:
./setup ship              # ships the PR for the current branch
./setup ship 183          # ships PR #183 explicitly
```

`setup ship` requires `CODACY_PROJECT_TOKEN` to be exported and `gh` to be
authenticated. It runs `gh pr update-branch` automatically when the branch is
BEHIND `main`, re-uploads the Codacy SARIF for the new HEAD and base SHA so the
diff comparison is fresh, then polls the four required checks
(`Codacy Static Code Analysis`, `Codacy Coverage Variation`,
`Codacy Diff Coverage`, `codacy-safety-net`) before squash-merging. It allows
GitHub's `UNSTABLE` merge state after those required checks are green because
non-required advisory jobs can be skipped or cancelled.
The default check polling window is 15 minutes; override with
`SHIP_CHECK_TIMEOUT=<seconds>` or `SHIP_CHECK_INTERVAL=<seconds>` only when
debugging.

---

## Direct CLI (advanced)

`./setup` is a wrapper. The underlying commands are stable and useful for automation:

```bash
uv run python -m dotfiles_tools doctor          --repo . --home "$HOME"
uv run python -m dotfiles_tools plan            --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply           --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools bootstrap-plan  --repo . --home "$HOME" --json
uv run python -m dotfiles_tools bootstrap-apply --repo . --home "$HOME" --yes
uv run python -m dotfiles_tools init-project    --repo . --project /path/to/project --vars project-vars.json --yes
```

`doctor` audits without writing. `plan` prints exact operations. `apply` writes only after `--yes`. Existing differing files are backed up before replacement. `bootstrap-plan`/`bootstrap-apply` add font recipes to the same manifest operations. Every command supports `--json` for stable machine output.

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

The font stage is catalog-driven. On Linux it manages Nerd Fonts archives (`JetBrainsMono`, `FiraCode`, `Hack`, `Meslo`) cached in `~/.cache/000-dotfiles/fonts/` and installs to `~/.local/share/fonts/`. It also installs apt fallbacks (`fonts-noto-color-emoji`, `fonts-symbola`, `fonts-freefont-ttf`, `fonts-dejavu-core`). Terminal checks always use `* Nerd Font Mono` faces, never Propo. WSL additionally installs JetBrainsMono on the Windows host and updates Windows Terminal defaults when discoverable.

---

## Project bootstrap example

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

When `project-vars.json` is missing and `--yes` is supplied, defaults are inferred from `package.json`/`pyproject.toml`/`Cargo.toml`/`go.mod`/Makefile and persisted to `<project>/.dotfiles/project-vars.json`.

---

## Validation and coverage

```bash
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
```

CI runs the same validation suite on pushes and pull requests and generates `coverage.xml`. Codacy upload is attempted on push events only when the `CODACY_PROJECT_TOKEN` GitHub secret is configured. See `docs/codacy-coverage-rollout.md` for replicating this pattern in other repos.

---

## Conventions and safety

- **No secrets.** No tokens, passwords, or API keys live in this repo. Auth files (`hosts.yml`, `auth.json`, `oauth_creds.json`, `token`) are `.gitignore`d. Sign in via `gh auth login`, `codex auth`, `claude /login`, etc. The local `.envrc.local` (also `.gitignore`d) exports `GITHUB_TOKEN` dynamically via `$(gh auth token 2>/dev/null)` so the GitHub MCP server can authenticate without storing a static token.
- **Symlinks for AI-agent docs.** Root `CLAUDE.md`/`GEMINI.md` symlink to `AGENTS.md`; `agents/CLAUDE.md.template` and `agents/GEMINI.md.template` symlink to `agents/AGENTS.md.template`. One source of truth per scope.
- **Backups before replace.** Drifted targets are copied to the backup dir (default `~/.dotfiles-backups`) before being overwritten.
- **Stop on first failure.** `apply` halts on the first failed write and reports `partial` status with completed operations and backups intact.

---

## Design and contributing

The implementation plan, contracts, and task list live in `specs/001-dotfiles-bootstrap-validation/`. AI-agent guidelines are in `AGENTS.md` (which `CLAUDE.md` and `GEMINI.md` symlink to). When changing templates, edit the `.template` file directly and run `git diff --staged` before every commit to catch tokens or personal paths. See `AGENTS.md` for detailed agent guidelines.
