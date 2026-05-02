# Getting Started

A complete guide to using this dotfiles repo, from first-time setup to ongoing maintenance
and AI agent doc scaffolding.

## What are dotfiles?

Dotfiles are the hidden configuration files (names starting with `.`) that configure your
shell, editor, git, and other tools. Most developers manually copy these across machines,
losing customizations and consistency. A **dotfiles repo** version-controls these files and
provides an automated way to deploy them on a fresh machine.

This repo does that—and adds two unique features: it manages AI coding tool configs (Claude
Code, Codex, Gemini, Copilot) and scaffolds AI agent guidelines for your projects.

## What does this repo manage?

| Tool | Purpose | Config file |
|---|---|---|
| **fish** | Shell | `~/.config/fish/env.fish`, `direnv.fish` |
| **direnv** | Environment isolation | `~/.config/direnv/direnvrc` |
| **git** | Version control (manual) | `~/.config/git/config` |
| **gh** | GitHub CLI | `~/.config/gh/config.yml` |
| **Claude Code** | AI coding assistant | `~/.claude/settings.json`, `keybindings.json` |
| **Codex** | Codex CLI | `~/.codex/config.toml`, `rules/default.rules` |
| **Gemini** | Gemini CLI | `~/.gemini/settings.json`, `GEMINI.md` |
| **Copilot** | GitHub Copilot CLI | (no config; auth via sign-in) |
| **SpecKit** | SpecKit agent framework | (per-project scaffold) |
| **Fonts** | Terminal UI | JetBrainsMono, FiraCode, Hack, MesloLGS Nerd Fonts + apt fallbacks |
| **AI agent docs** | Your project | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` |

---

## Part 1: First-time setup (fresh machine)

### Prerequisites

- Ubuntu 20.04+ or similar Linux (WSL works; Raspberry Pi supported)
- ~15 min of interactive time
- Internet access to download tools and fonts

### Step 1: Clone the repo

```bash
git clone https://github.com/kairin/000-dotfiles.git ~/000-dotfiles
cd ~/000-dotfiles
```

### Step 2: Run the interactive setup

```bash
./setup
```

You'll see a summary of your machine state and a 5-option menu:

```
1. Install / update developer tools        [recommended]
2. Apply safe non-protected dotfiles
3. Show full technical details
4. Show tool and sign-in guidance
5. Exit without writing
```

Since tools are missing on a fresh machine, **option 1 is highlighted**. Choose it.

```
Choose [1-5]: 1
```

### Step 3: Preview and confirm

You'll see a preview of all tools that will be installed:

```
Already installed (will be updated where possible):
  - Git: git version 2.x → apt --only-upgrade
  - GitHub CLI: gh version 2.x → apt --only-upgrade
  ... etc ...
```

Review the list and confirm:

```
Apply tool install/update actions? [y/N]: y
```

The installer will run for 2–5 minutes. Once done, you'll see a summary with sign-in commands to run:

```
Auth/setup guidance:
  - gh auth status: If it reports no authenticated host, run gh auth login.
  - codex auth: Run when Codex CLI is installed and needs user authentication.
  - claude login: Run when Claude Code CLI is installed and needs user authentication.
  - gemini: Start Gemini CLI and complete its login/setup prompt if needed.
  - copilot /login: Run when GitHub Copilot CLI is installed and needs user authentication.
```

### Step 4: Sign in to each tool

Run the sign-in commands one by one at your leisure:

```bash
gh auth login      # GitHub CLI
claude /login      # Claude Code (or just: claude)
codex auth         # Codex CLI
gemini             # Gemini CLI (prompts for auth)
copilot /login     # GitHub Copilot CLI
```

For `specify` (SpecKit), sign-in happens per-project (see Part 3).

### Step 5: Apply configs and fonts

The menu is now back. Option 2 is now highlighted:

```
1. Install / update developer tools
2. Apply safe non-protected dotfiles        [recommended]
3. Show full technical details
4. Show tool and sign-in guidance
5. Exit without writing
Choose [1-5]: 2
```

Choose option 2:

```
Choose [1-5]: 2
```

You'll see a preview of config files and fonts to install:

```
Update existing files with backups:
  - ~/.claude/settings.json
  - ~/.codex/config.toml
  - (other config templates)

Fonts:
  - JetBrainsMono Nerd Font
  - FiraCode Nerd Font
  - ... etc ...
```

Confirm to apply:

```
Apply these changes? [y/N]: y
```

Configs and fonts are now installed. Done!

### Step 6: Restart your shell

For fish shell changes to take effect:

```bash
exec fish
```

---

## Part 2: Ongoing maintenance

Your machine is now set up. The tools and configs will stay current by following a simple pattern:

### Check for drift

Drift occurs when you've manually edited a config file or when the repo's template has been updated. To audit your machine:

```bash
~/000-dotfiles/setup
```

The menu shows your current state:

```
Machine setup summary
  - All 10 baseline tools are visible on PATH.
  - Configs: 2 drifted, 8 current

1. Install / update developer tools
2. Apply safe non-protected dotfiles        [recommended]
3. Show full technical details
4. Show tool and sign-in guidance
5. Exit without writing
```

Option 2 is highlighted because configs have drifted. Choose it to review and apply the changes.

### Update tools

To upgrade installed tools:

```bash
~/000-dotfiles/setup
Choose [1-5]: 1
```

This runs:
- `apt --only-upgrade` for OS packages (git, gh, fish, direnv)
- `npm update -g` for globally-installed npm tools (codex, gemini, copilot)
- Self-update for curl installers (claude)
- `uv tool upgrade` for uv-managed tools (specify)

### Show details (option 3)

If you want to inspect cache paths, font versions, or the full operation plan without applying:

```bash
Choose [1-5]: 3
```

Shows raw cache state, package versions, and all pending operations.

---

## Part 3: Scaffold AI agent docs in your project

Once you have this repo cloned, you can scaffold AI agent guidelines in any of your projects. This creates a consistent interface for Claude Code, Codex, and Gemini CLIs to work with your codebase.

### In your project directory:

```bash
cd ~/Apps/my-project
~/000-dotfiles/setup

# Or with explicit variables:
~/000-dotfiles/setup init --yes \
  --project ~/Apps/my-project \
  --vars <(cat <<'EOF'
{
  "PROJECT_NAME": "My Project",
  "PROJECT_DESCRIPTION": "A concise description",
  "LANGUAGE": "Python",
  "PACKAGE_MANAGER": "uv",
  "RUNTIME_DESCRIPTION": "CLI tool",
  "INSTALL_CMD": "uv sync",
  "RUN_CMD": "uv run main.py",
  "TEST_CMD": "uv run pytest"
}
EOF
)
```

This creates:

- `AGENTS.md` — shared guidelines for all AI agents
- `CLAUDE.md` → symlink to `AGENTS.md`
- `GEMINI.md` → symlink to `AGENTS.md`
- `copilot-instructions.md` (optional) — Copilot-specific instructions

### Optional project integrations

Project-scoped integrations that are useful only for some repositories live
behind a secondary menu so they do not compete with the core setup actions.

```bash
~/000-dotfiles/setup ~/Apps/my-project
```

Choose `Optional integrations and APIs`, then `Manage Codacy API access`.

Codacy setup supports two modes:

- `repository token` exposes `CODACY_PROJECT_TOKEN` for one project.
- `account token` exposes `CODACY_API_TOKEN` for broader Codacy API access.

Both modes also expose `CODACY_ORGANIZATION_PROVIDER`, `CODACY_USERNAME`, and
`CODACY_PROJECT_NAME`. Token values are stored outside the project under
`~/.codacy/`; project files only contain a bridge that reads those files.

Before writing anything, setup shows a token-free preview of the project files
and token-storage path that would change. Writes require final confirmation.
If existing `.envrc` or `.envrc.local` files are changed, setup creates a
backup first. After setup, run the shell activation step shown in the output,
for example:

```bash
direnv allow ~/Apps/my-project
```

### For SpecKit users:

Once `specify` is installed, initialize SpecKit in your project:

```bash
cd ~/Apps/my-project
specify init --here
```

This creates per-project scaffolding (`.specify/`, `.agents/skills/`, etc.) that lets you define feature specs and code-generation integrations specific to your project.

---

## Troubleshooting

### `uv: command not found`

The setup script installs uv if missing. If you see this:

1. Check if the install completed: `which uv`
2. If not found, manually install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Reload your shell: `exec fish` (or `bash`, `zsh`)
4. Re-run `./setup`

### `Tool install failed: X not found`

Most tools install via `apt`, `npm`, or `uv`. If one fails:

1. Check the error message (scroll back in your terminal)
2. Run the tool doctor to see state: `./setup doctor`
3. Try the install command manually, e.g. `apt install git` or `npm install -g @github/copilot`
4. Re-run `./setup`

### `Config drift: file X differs`

If the setup script reports config drift:

1. Review the difference: `./setup` then choose option 3 (full details)
2. If you want to keep your changes, skip this file: just don't confirm the apply
3. If you want the repo's version: choose option 2 and confirm
4. Backups are created before overwrite (default: `~/.dotfiles-backups/`)

### Font icons look broken in my terminal

Nerd Fonts provide glyphs for code icons. If they're not displaying:

1. Confirm fonts installed: `fc-list | grep JetBrainsMono` (should find them)
2. In your terminal preferences, set the font to **JetBrainsMono Nerd Font Mono** (or another `* Nerd Font Mono`)
3. If terminal doesn't show that option, try `FiraCode Nerd Font Mono` or `Hack Nerd Font Mono`

### I accidentally overwrote a file I wanted to keep

Your old file is in `~/.dotfiles-backups/`. Restore it:

```bash
# List backups
ls ~/.dotfiles-backups/

# Restore one
cp ~/.dotfiles-backups/settings.json ~/.claude/settings.json
```

---

## Next steps

- Customize the AI agent docs for your projects: edit `AGENTS.md` to reflect your team's coding standards
- Set up SpecKit for feature-driven development: `specify init --here` in any project
- Contribute improvements: the repo is open source and welcomes issues and PRs
