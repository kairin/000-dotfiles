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
| **direnv** | Fish shell direnv hook | `~/.config/fish/functions/direnv.fish` |
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

You'll see a summary of your machine state and a 7-option menu:

```
1. Install / update developer tools        [recommended]
2. Apply safe non-protected dotfiles.
3. Show full technical details
4. Show tool and sign-in guidance
5. Configure / verify API tokens
6. Install / update Git hooks for this repo
7. Exit without writing
```

Since tools are missing on a fresh machine, **option 1 is highlighted**. Choose it.

```
Choose [1-7]: 1
```

### Step 3: Pick a tool phase

Option 1 opens a submenu so you can isolate the slow step before you write
anything:

```
Developer tool phases:
1. Preview dev-base packages.
2. Apply dev-base packages.
3. Preview individual tool installers.
4. Apply individual tool installers.
5. Split post-install verification and guidance.
6. Back to main menu.
```

Choose the phase you want to inspect or apply. For example, start with the
dev-base package preview:

```
Choose [1-6]: 1
```

You'll see the dev-base package preview:

```
Preparing dev-base package preview...
```

Then confirm the apply step if you want to write the dev-base changes:

```
Choose [1-6]: 2
Apply dev-base packages actions? [y/N]: y
```

If you want the tool installers instead, choose option 3 or 4. After the
selected phase finishes, you can run option 5 for a second submenu that splits
post-install verification, auto actions, and manual guidance. Once the relevant
phase completes, you'll see a summary with sign-in commands to run:

```
Auth/setup guidance:
  - gh auth status: If it reports no authenticated host, run gh auth login.
  - codex auth: Run when Codex CLI is installed and needs user authentication.
  - claude /login: Run when Claude Code CLI is installed and needs user authentication.
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
2. Apply safe non-protected dotfiles.       [recommended]
3. Show full technical details
4. Show tool and sign-in guidance
5. Configure / verify API tokens
6. Install / update Git hooks for this repo
7. Exit without writing
Choose [1-7]: 2
```

Choose option 2 to open the safe-changes submenu:

```
Safe setup changes:
1. Dotfiles and config files.
2. Fonts and terminal setup.
3. Apply all safe changes now.
4. Back to main menu.
```

Choose `1` to review dotfiles or `2` to review fonts, then `3` to apply:

```
Choose [1-4]: 3
```

Configs and fonts are now installed.

### Step 5b: MCP server registration

After applying dotfiles, setup automatically registers GitHub MCP and Codacy MCP
with Claude Code at user scope:

```
  github MCP server registered
  codacy MCP server registered
```

Both are registered via `claude mcp add --scope user` and skipped if already
present. Prerequisites:

- **GitHub MCP**: `gh auth login` must have been run first (so `GITHUB_TOKEN` is
  non-empty in `~/.envrc.local`).
- **Codacy MCP**: the machine-level Codacy account token must be set up. Run
  `./setup`, choose `Configure API tokens` → `Codacy`, and enter your account
  token.

To verify registration after setup:

```bash
claude mcp list
```

Both `github` and `codacy` should appear. Alternatively, `./setup verify` includes
an MCP server status section in its audit report:

```
MCP server configuration:
  Server               Status
  ---                  ---
  github               ✓ Configured
  codacy               ✓ Configured
```

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
2. Apply safe non-protected dotfiles.       [recommended]
3. Show full technical details
4. Show tool and sign-in guidance
5. Configure / verify API tokens
6. Install / update Git hooks for this repo
7. Exit without writing
```

Option 2 is highlighted because configs have drifted. Choose it to review the dotfiles/fonts
split and then apply the changes.

### Update tools

To upgrade installed tools:

```bash
~/000-dotfiles/setup
Choose [1-7]: 1
```

This runs:
- `apt --only-upgrade` for OS packages (git, gh, fish, direnv)
- `npm update -g --prefix ~/.local` for user-local npm tools (codex, gemini, copilot)
- Self-update for curl installers (claude)
- `uv tool upgrade` for uv-managed tools (specify)

### Show details (option 3)

If you want to inspect cache paths, font versions, or the full operation plan without applying:

```bash
Choose [1-7]: 3
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

Choose `Optional integrations and APIs`. The menu dynamically shows only the integrations you need:

1. **Manage GitHub (gh) API access** — available only if `gh` is not yet authenticated. Offers to install `gh` via `apt` if not found.
2. **Configure HuggingFace API token** — available only if no HF token is found in `$HF_TOKEN` or `~/.cache/huggingface/token`. Offers to install `huggingface-hub` via `uv tool install` if not found.
3. **Manage Codacy API access** — always available.

#### Codacy setup

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

### Check API credential status

To verify which integrations are configured, run:

```bash
./setup verify --project ~/Apps/my-project
```

The output includes an API credential status table and an MCP server status section:

```
API credential status:
  Service              Status
  ---                  ---
  GitHub (gh)          ✓ Authenticated
  HuggingFace          ✓ Token found
  Codacy               ✗ Not configured

MCP server configuration:
  Server               Status
  ---                  ---
  github               ✓ Configured
  codacy               ✓ Configured
```

This is a quick health check to see which integrations and MCP servers are ready to use.

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
3. Try the install command manually, e.g. `apt install git` or `npm install -g --prefix ~/.local @github/copilot`
4. Re-run `./setup`

### `Config drift: file X differs`

If the setup script reports config drift:

1. Review the difference: `./setup` then choose option 3 (full details)
2. If you want to keep your changes, skip this file: just don't confirm the apply
3. If you want the repo's version: choose option 2 and confirm
4. Backups are created before overwrite (default: `~/.dotfiles-backups/`)

**Note:** Some files are intentionally excluded from drift resolution and your customizations are always preserved. These files are marked `user_customizable` and include: `claude/settings.json`, `claude/keybindings.json`, `claude/CLAUDE.md`, `codex/config.toml`, `codex/default.rules`, `gemini/settings.json`, `gemini/GEMINI.md`, `gh/config.yml`, `fish/env.fish`, and `fish/functions/direnv.fish`. Option 2 will never overwrite these files even if they differ from the template.

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
