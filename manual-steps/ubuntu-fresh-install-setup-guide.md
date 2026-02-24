# Fresh Install Setup Guide

> **Tested on:** Ubuntu 24.04 LTS (Noble), Ubuntu 25.10 (Questing Quetzal), and Raspberry Pi OS/Armbian (Debian Trixie) with Fish 4.x on diverse architectures (x86_64, aarch64, arm64).

> **Note on TUI Stability:** If you experience bugs, rendering issues, or freezes with the `start.sh` TUI dashboard, this manual setup guide serves as the official, reliable fallback. The CLI commands below achieve the exact same configuration as the interactive installer.

## 1. System Update & Essential Packages

> **SBCs (Raspberry Pi / Orange Pi) only:** Run `sudo raspi-config` (or `sudo armbian-config` for Orange Pi) first to configure locale, timezone, SSH, and Wi-Fi before proceeding.

```bash
sudo apt update && sudo apt upgrade -y
```

**Ubuntu 24.04 only** — add PPAs to ensure you get the absolute latest versions of `fastfetch` and `fish` (3.7.0 → 4.5+), bypassing the outdated default apt repositories:

```bash
sudo add-apt-repository ppa:zhangsongcui3371/fastfetch -y
sudo add-apt-repository ppa:fish-shell/release-4 -y
```

> **Skip PPAs on:** Ubuntu 25.10+, Raspberry Pi OS/Armbian (Debian Trixie) — fastfetch is already in the default repos. Debian-based systems don't have `add-apt-repository`.

> **Why the Fish PPA on 24.04?** Ubuntu 24.04 ships Fish 3.7.0, which is missing features like `fish_add_path` validation, improved key bindings, and Rust-based performance. The official PPA provides Fish 4.5+ with full compatibility for modern plugins like Tide v6.

Install core packages:

**Ubuntu (all versions):**
```bash
sudo apt install curl wget git fastfetch fish shellcheck direnv fzf -y
```

**SBCs: Raspberry Pi OS / Orange Pi (Debian Trixie/Armbian)** — install Fish 4.5.0 from upstream instead of apt's outdated 4.0.2:
```bash
sudo apt install curl wget git fastfetch shellcheck direnv fzf -y

cd /tmp
curl -fLO https://github.com/fish-shell/fish-shell/releases/download/4.5.0/fish-4.5.0-linux-aarch64.tar.xz
tar -xf fish-4.5.0-linux-aarch64.tar.xz
sudo cp fish /usr/local/bin/fish
sudo chmod +x /usr/local/bin/fish
rm -f fish fish-4.5.0-linux-aarch64.tar.xz
```

> **Why not `apt install fish` on Pi?** Debian Trixie ships Fish 4.0.2 which lacks features needed by Tide v6 and other modern plugins. The upstream static binary for aarch64 provides Fish 4.5.0. Check https://github.com/fish-shell/fish-shell/releases for newer versions.

Install Google Chrome (**x86_64 / amd64 only** — skip on ARM SBCs like Raspberry Pi and Orange Pi):

```bash
wget -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install /tmp/google-chrome.deb -y
rm /tmp/google-chrome.deb
```

> **Note:** The Chrome .deb automatically adds Google's apt repository, so Chrome receives updates through `sudo apt upgrade` alongside your other packages. On ARM SBCs like Raspberry Pi or Orange Pi, Chromium is typically pre-installed via your distribution.

> **Why ShellCheck?** The [000-dotfiles](https://github.com/kairin/000-dotfiles) repo's shell scripts benefit from ShellCheck linting. Installing it here ensures the dotfiles manager can validate on first run.

> **Why direnv?** Automatically sets per-project environment variables (e.g. `CODEX_HOME` for Spec-Kit) when you `cd` into a project directory.

## 2. Set Fish as Default Shell

**Ubuntu** (Fish installed via apt/PPA to `/usr/bin/fish`):
```bash
command -v fish | sudo tee -a /etc/shells
chsh -s "$(command -v fish)"
```

**SBCs: Raspberry Pi / Orange Pi** (Fish installed to `/usr/local/bin/fish`):
```bash
echo /usr/local/bin/fish | sudo tee -a /etc/shells
chsh -s /usr/local/bin/fish
```

> **⚠️ IMPORTANT:** Log out and back in (or reboot) now. All remaining steps assume you are running inside a Fish shell session.

---

## 3. Install Fisher, Plugins, and Shell Configuration

```fish
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

Install recommended plugins:

```fish
fisher install IlanCosman/tide@v6 PatrickF1/fzf.fish jethrokuan/z franciscolourenco/done jorgebucaran/autopair.fish
```

| Plugin | What it does |
|--------|-------------|
| [Tide](https://github.com/IlanCosman/tide) | Modern prompt with git status, async rendering, and multi-line support |
| [fzf.fish](https://github.com/PatrickF1/fzf.fish) | Fuzzy search for files, history, processes, and variables (requires `fzf` from apt) |
| [z](https://github.com/jethrokuan/z) | Smart directory jumping — `z project` jumps to your most-used matching directory |
| [done](https://github.com/franciscolourenco/done) | Desktop notification when long-running commands finish |
| [autopair.fish](https://github.com/jorgebucaran/autopair.fish) | Auto-close brackets, quotes, and parentheses |

Configure the Tide prompt:

```fish
tide configure
```

> **Tip:** Fisher commands for later: `fisher list` to see installed plugins, `fisher update` to update all, `fisher remove <plugin>` to uninstall.

Enable direnv hook for Fish (auto-loads per-project `.envrc` files):

```fish
echo 'direnv hook fish | source' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

## 4. Install fnm and Node.js

Install [fnm](https://github.com/Schniz/fnm) (Fast Node Manager) and Node.js:

```fish
curl -o- https://fnm.vercel.app/install | bash
```

Close and reopen your terminal (or log out and back in) for fnm to be available, then:

```fish
fnm install 25
node -v
npm -v
```

> **Why fnm over apt/NodeSource?** Ubuntu 24.04 ships Node.js v18 which is too old for modern CLI tools (Gemini CLI, Codex). fnm lets you install and switch between any Node.js version per-user without sudo, and works natively with Fish.

> **⚠️ Do not install Node.js via apt.** If you previously installed `nodejs` or `npm` via apt, remove them first to avoid conflicts: `sudo apt remove nodejs npm -y && sudo apt autoremove -y`

## 5. Configure npm Global Packages (without sudo)

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

## 6. Install Go (from go.dev)

The [000-dotfiles](https://github.com/kairin/000-dotfiles) TUI is built in Go. Install the latest version directly from go.dev rather than apt (which lags behind):

**x86_64:**
```fish
curl -LO https://go.dev/dl/go1.26.0.linux-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.26.0.linux-amd64.tar.gz
rm go1.26.0.linux-amd64.tar.gz
fish_add_path /usr/local/go/bin
```

**SBCs: Raspberry Pi / Orange Pi (arm64 / aarch64):**
```fish
curl -LO https://go.dev/dl/go1.26.0.linux-arm64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.26.0.linux-arm64.tar.gz
rm go1.26.0.linux-arm64.tar.gz
fish_add_path /usr/local/go/bin
```

Verify:
```fish
go version
```

> **Why not `apt install golang-go`?** Ubuntu 24.04 ships Go 1.22, Debian Trixie ships 1.24.4 — both lag significantly behind the current release. The official tarball gives you the latest version and works identically across all platforms. Check https://go.dev/dl/ for newer versions.

## 7. Install GitHub CLI (gh)

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

## 8. Authenticate GitHub CLI

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

## 9. Clone and Run Dotfiles Manager

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
- Google Gemini CLI
- Specify CLI
- Context7 MCP
- Git identity configuration
- Nerd Fonts and other extras

> **Tip:** After setup, select **Workstation Audit** from the TUI dashboard to verify your full toolchain, auth, and MCP status in a secret-safe report. Or run it from the command line: `./.runners-local/workflows/health-check.sh --workstation-audit`

---

## Manual Setup Reference

The following steps are handled by the dotfiles manager (Step 8) but are documented here for reference, troubleshooting, or manual installation.

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

### Install Google Gemini CLI

```fish
npm i -g @google/gemini-cli
```

Verify installation:
```fish
which gemini
gemini --version
```

> **Note:** Gemini CLI requires Node.js 20+. If you see `SyntaxError: Invalid regular expression flags`, your Node.js is too old (v18). See Step 4 for installing Node.js via fnm.

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
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

> **Note:** Codex uses the npx-based MCP runner rather than the HTTP transport used by Claude Code. The API key can be passed inline via the `--api-key` flag if needed.

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

**For Claude Code:**

```fish
cd ~/your-project
specify init --here --ai claude
claude
```

> **Note:** Consider adding `.claude/` to `.gitignore` to prevent accidental credential leakage.

**For Codex CLI:**

```fish
cd ~/your-project
specify init --here --ai codex
echo 'export CODEX_HOME="$PWD/.codex"' > .envrc
direnv allow
codex
```

The `.envrc` sets `CODEX_HOME` so Codex can find Spec-Kit's `/speckit.*` slash commands. `direnv allow` trusts it (one-time per project). After that, `CODEX_HOME` loads automatically whenever you `cd` into the project.

> **Note:** The dotfiles manager's `configure_fish.sh` adds the direnv Fish hook, and `update_ai_tools.sh` keeps Spec Kit and `.envrc` current automatically. These manual steps are only needed outside the dotfiles workflow.

> **Note:** Consider adding `.codex/` to `.gitignore` to prevent accidental credential leakage.

**Spec Kit Workflow Commands (both Claude and Codex):**
1. `/speckit.constitution` — Establish project principles
2. `/speckit.specify` — Create baseline specification
3. `/speckit.plan` — Create implementation plan
4. `/speckit.tasks` — Generate actionable tasks
5. `/speckit.implement` — Execute implementation

**Optional Enhancement Commands:**
- `/speckit.clarify` — Ask questions to de-risk ambiguous areas (before `/speckit.plan`)
- `/speckit.analyze` — Cross-artifact consistency report (after `/speckit.tasks`)
- `/speckit.checklist` — Generate quality checklists (after `/speckit.plan`)

### Install Nerd Fonts

The easiest way to install Nerd Fonts is via the TUI dashboard (`./start.sh` -> **Extras** -> **Nerd Fonts**). Alternatively, you can run the standalone installer script provided by the dotfiles manager to install the complete recommended set (JetBrainsMono, FiraCode, Hack, Meslo, etc.):

```fish
~/Apps/000-dotfiles/scripts/004-reinstall/install_nerdfonts.sh
```

**Manual installation (e.g., JetBrains Mono):**

```fish
mkdir -p ~/.local/share/fonts
curl -fLo /tmp/JetBrainsMono.tar.xz https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/JetBrainsMono.tar.xz
tar -xJf /tmp/JetBrainsMono.tar.xz -C ~/.local/share/fonts
rm /tmp/JetBrainsMono.tar.xz
fc-cache -fv ~/.local/share/fonts
```

> **Note:** Fish shell and plugins like Tide require a Nerd Font to render icons correctly in the prompt. Ensure your terminal emulator is configured to use the installed Nerd Font.

### Verify All Installations

```fish
fastfetch
fish --version
fisher --version
tide --version
node --version
npm --version
go version
shellcheck --version
direnv --version
fzf --version
git --version
gh --version
gh auth status
uv --version
claude --version
codex --version
gemini --version
specify --help
```

> **Note:** Specify CLI does not support `--version`. Use `specify --help` to confirm it's installed.

**Verified on Raspberry Pi 4 & Orange Pi 5 (Debian Trixie/Armbian, arm64) — 24 Feb 2026:**

| Tool | Version |
|------|---------|
| Fish | 4.5.0 |
| Fisher | 4.4.8 |
| Tide | 6.2.0 |
| Node.js | 25.6.1 |
| npm | 11.9.0 |
| Go | 1.26.0 linux/arm64 |
| ShellCheck | 0.10.0 |
| direnv | 2.32.1 |
| fzf | 0.60 |
| Git | 2.47.3 |
| gh | 2.87.2 |
| uv | 0.10.4 |
| Claude Code | 2.1.50 |
| Codex CLI | 0.104.0 |
| Gemini CLI | 0.29.5 |
| Specify | ✓ (via `--help`) |

---

## Quick Reference: PATH Fixes for Fish

If any tool is not found after installation, these are the common fixes:

| Tool | Fix |
|------|-----|
| Go (`go`) | `fish_add_path /usr/local/go/bin` |
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

**Node.js v18: `SyntaxError: Invalid regular expression flags`**
Ubuntu 24.04 ships Node.js v18 which doesn't support the `/v` regex flag used by modern CLI tools (Gemini CLI, newer Codex versions). Remove apt-installed Node.js and use fnm instead (see Step 4): `sudo apt remove nodejs npm -y && sudo apt autoremove -y && curl -o- https://fnm.vercel.app/install | bash` then restart your terminal and run `fnm install 25`
