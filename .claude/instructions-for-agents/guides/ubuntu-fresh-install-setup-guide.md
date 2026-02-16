# Ubuntu Fresh Install Setup Guide

> **Tested on:** Ubuntu 25.10 (Questing Quetzal) with Fish 4.x

## 1. System Update & Essential Packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install curl wget git fastfetch fish nodejs npm golang-go shellcheck -y
```

> **Note:** Ubuntu 25.10 ships Node.js via apt. If you need a specific version later, consider using `nvm` or `fnm`.

> **Why Go and ShellCheck?** The [000-dotfiles](https://github.com/kairin/000-dotfiles) TUI is built in Go, and the repo's shell scripts benefit from ShellCheck linting. Installing both here ensures the dotfiles manager can build and validate on first run.

## 2. Set Fish as Default Shell

```bash
command -v fish | sudo tee -a /etc/shells
chsh -s "$(command -v fish)"
```

> **⚠️ IMPORTANT:** Log out and back in (or reboot) now. All remaining steps assume you are running inside a Fish shell session.

---

## 3. Install Fisher (Fish Plugin Manager)

```fish
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

## 4. Configure npm Global Packages (without sudo)

This ensures globally installed npm packages (like `codex`) are available without `sudo`:

```fish
mkdir -p ~/.npm-global/bin
npm config set prefix ~/.npm-global
fish_add_path ~/.npm-global/bin
```

Verify the PATH is set:
```fish
echo $fish_user_paths
```

You should see `/home/<user>/.npm-global/bin` in the output. `fish_add_path` is persistent across sessions and idempotent (safe to run multiple times).

> **Why not `set -U fish_user_paths`?** Fish 4.x recommends `fish_add_path` — it avoids duplicate entries and handles edge cases automatically. Note that `fish_add_path` skips non-existent directories, so we create `bin/` upfront (npm only creates it when the first global package is installed).

## 5. Install GitHub CLI (gh)

> **Note:** This uses bash syntax. Run it with `bash -c` from Fish:

```fish
bash -c '(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y'
```

## 6. Authenticate GitHub CLI

```fish
gh auth login
```

During login, select:
- GitHub.com
- HTTPS
- Authenticate Git with credentials: Yes
- Login with a web browser

> **Note:** You may see `update.go: cannot change mount namespace` errors when the browser opens — these are harmless snap sandbox messages and can be ignored.

> **Troubleshooting:** If you see "token in keyring is invalid" on a subsequent session, re-authenticate with: `gh auth login -h github.com`

## 7. Clone and Run Dotfiles Manager

```fish
mkdir -p ~/Apps
cd ~/Apps
gh repo clone kairin/000-dotfiles
cd 000-dotfiles
./start.sh
```

`start.sh` handles the Go build and launches the TUI dashboard. From here, the dotfiles manager takes over and handles the installation and configuration of remaining tools including:
- uv (Python package manager)
- Claude Code
- OpenAI Codex CLI
- Specify CLI
- Context7 MCP
- Git identity configuration
- Nerd Fonts and other extras

> **Tip:** After setup, select **Workstation Audit** from the TUI dashboard to verify your full toolchain, auth, and MCP status in a secret-safe report. Or run it from the command line: `./.runners-local/workflows/health-check.sh --workstation-audit`

---

## Manual Setup Reference

The following steps are handled by the dotfiles manager (Step 7) but are documented here for reference, troubleshooting, or manual installation.

### Install uv (Python Package Manager)

```fish
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then source the PATH for the current session:
```fish
source $HOME/.local/bin/env.fish
```

> **Note:** The uv installer automatically adds itself to `~/.config/fish/conf.d/`, so this persists across future sessions. The `source` command above is only needed for the current session.

### Install Claude Code

```fish
curl -fsSL https://claude.ai/install.sh | bash
```

Verify installation:
```fish
which claude
claude --version
```

> **Note:** Claude Code installs to `~/.local/bin/`, which is already on your PATH if uv was installed first. No additional PATH setup needed.

### Install OpenAI Codex CLI

```fish
npm i -g @openai/codex
```

Verify installation:
```fish
which codex
codex --version
```

> **Troubleshooting:** If `codex` is not found but exists at `~/.npm-global/bin/codex`, the npm global PATH was not configured. Run: `mkdir -p ~/.npm-global/bin && fish_add_path ~/.npm-global/bin`

### Install Specify CLI (Spec-Driven Development)

```fish
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

> **Note:** `uv tool` installs to `~/.local/bin/`, shared with uv and Claude Code.

### Install Context7 MCP (Documentation Context for AI Tools)

1. Get your API key from: https://context7.com/dashboard

2. Add to Claude Code (replace `YOUR_API_KEY` with your actual key):

```fish
claude mcp add --scope user --header "CONTEXT7_API_KEY: YOUR_API_KEY" --transport http context7 https://mcp.context7.com/mcp
```

> **Why `--scope user`?** Without it, the MCP server is only available in the current project directory. With `--scope user`, it's available globally across all projects.

3. Add to Codex CLI:

```fish
codex mcp add context7 --url https://mcp.context7.com/mcp
```

> **Important (Codex scope):** Keep Codex configuration in the default global location (`~/.codex`). Do not set `CODEX_HOME` to this repository path; this repo is reference/documentation for expected MCP setup, not the canonical Codex config home.

Then set the API key as an environment variable for Codex:

```fish
mkdir -p ~/.config/fish/conf.d
echo 'set -gx CONTEXT7_API_KEY "YOUR_API_KEY"' > ~/.config/fish/conf.d/context7.fish
source ~/.config/fish/conf.d/context7.fish
```

### Configure Git with Claude Code

With `gh auth login` already complete, launch Claude Code:

```fish
claude
```

**Prompt 1:** Set up Git credential helper
```
use gh cli to obtain the relevant credentials to use git
```

**Prompt 2:** Verify setup and configure git identity
```
can you help to verify if gh and git are properly setup?
```
When asked about configuring user.name and email, select "Yes" and tell Claude:
```
use gh cli to get the correct details but do not use my private email, use the GitHub noreply email address instead
```

> **Note:** GitHub provides a noreply email format (`ID+username@users.noreply.github.com`) to keep your personal email private while performing Git operations.

### Initialize Spec Kit in a Project

Navigate to your project directory and initialize:

```fish
cd ~/your-project
specify init --here --ai claude
```

Then launch Claude Code and use the slash commands:

```fish
claude
```

**Spec Kit Workflow Commands:**
1. `/speckit.constitution` — Establish project principles
2. `/speckit.specify` — Create baseline specification
3. `/speckit.plan` — Create implementation plan
4. `/speckit.tasks` — Generate actionable tasks
5. `/speckit.implement` — Execute implementation

**Optional Enhancement Commands:**
- `/speckit.clarify` — Ask questions to de-risk ambiguous areas (before `/speckit.plan`)
- `/speckit.analyze` — Cross-artifact consistency report (after `/speckit.tasks`)
- `/speckit.checklist` — Generate quality checklists (after `/speckit.plan`)

> **Note:** Consider adding `.claude/` to `.gitignore` to prevent accidental credential leakage.

### Verify All Installations

```fish
fastfetch
fish --version
fisher --version
node --version
npm --version
go version
shellcheck --version
git --version
gh --version
gh auth status
uv --version
claude --version
codex --version
specify --help
```

> **Note:** Specify CLI does not support `--version`. Use `specify --help` to confirm it's installed.

---

## Quick Reference: PATH Fixes for Fish

If any tool is not found after installation, these are the common fixes:

| Tool | Fix |
|------|-----|
| npm global packages (`codex`) | `mkdir -p ~/.npm-global/bin && fish_add_path ~/.npm-global/bin` |
| uv, Claude Code, Specify CLI | `fish_add_path ~/.local/bin` (all share this path; set by uv installer) |

## Troubleshooting

**gh auth: "token in keyring is invalid"**
Tokens stored in the system keyring can expire or become corrupted between sessions. Fix with: `gh auth login -h github.com`

**Context7 MCP shows "Failed to connect" in `claude mcp list`**
The CLI health check runs outside an interactive session and may time out. If Context7 shows connected inside Claude Code (`/mcp`), it's working fine. If it's genuinely missing, check that you used `--scope user` when adding it.

**Snap mount namespace errors during `gh auth login`**
Messages like `update.go: cannot change mount namespace` are harmless snap sandbox warnings from the browser opening. Authentication still completes normally.

**`specify --version` returns exit code 2**
This is expected — Specify CLI doesn't support `--version`. Use `specify --help` to verify installation.

**Fish 4.x: `fish_add_path` skips non-existent directories**
Unlike Fish 3.x, `fish_add_path` in Fish 4.x validates that directories exist before adding them. Always `mkdir -p` the target directory first.
