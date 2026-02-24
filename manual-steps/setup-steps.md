# Setup Steps — Command Reference

> **Source**: [version-verification-feb2026.xlsx](version-verification-feb2026.xlsx), Sheet 2 — "Setup Steps"
> **Narrative guide**: [ubuntu-fresh-install-setup-guide.md](ubuntu-fresh-install-setup-guide.md) for explanatory context

This document lists every command in the manual setup process, organized by section. Steps 1-10 are the core setup sequence. Steps M1-M10 are manual-only steps (not handled by the TUI). Step V is the full verification script.

---

## Step 1: System Update & Essential Packages

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 1a | Update system | All | |
| 1b | Add PPAs (24.04 only) | Ubuntu 24.04 only | Skip on 25.10+, Pi OS, Armbian |
| 1c | Install core packages (Ubuntu) | Ubuntu (all) | |
| 1c | Install core packages (SBC) | Pi OS / Armbian | Fish installed separately below |
| 1d | Install Fish 4.5.0 from upstream (SBC) | Pi OS / Armbian | Debian Trixie ships 4.0.2; need 4.5+ |
| 1e | Install Google Chrome | x86_64 only | Skip on ARM SBCs |

**1a** — Update system:
```bash
sudo apt update && sudo apt upgrade -y
```

**1b** — Add PPAs (Ubuntu 24.04 only):
```bash
sudo add-apt-repository ppa:zhangsongcui3371/fastfetch -y
sudo add-apt-repository ppa:fish-shell/release-4 -y
```

**1c** — Install core packages (Ubuntu):
```bash
sudo apt install curl wget git fastfetch fish shellcheck direnv fzf -y
```

**1c** — Install core packages (SBC):
```bash
sudo apt install curl wget git fastfetch shellcheck direnv fzf -y
```

**1d** — Install Fish 4.5.0 from upstream (SBC):
```bash
cd /tmp
curl -fLO https://github.com/fish-shell/fish-shell/releases/download/4.5.0/fish-4.5.0-linux-aarch64.tar.xz
tar -xf fish-4.5.0-linux-aarch64.tar.xz
sudo cp fish /usr/local/bin/fish
sudo chmod +x /usr/local/bin/fish
```

**1e** — Install Google Chrome (x86_64 only):
```bash
wget -O /tmp/google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install /tmp/google-chrome.deb -y
```

---

## Step 2: Set Fish as Default Shell

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 2a | Add Fish to shells & set default (Ubuntu) | Ubuntu | Fish at /usr/bin/fish |
| 2a | Add Fish to shells & set default (SBC) | Pi OS / Armbian | Fish at /usr/local/bin/fish |
| 2b | Log out and back in | All | All remaining steps require Fish shell |

**2a** — Ubuntu:
```bash
command -v fish | sudo tee -a /etc/shells
chsh -s "$(command -v fish)"
```

**2a** — SBC:
```bash
echo /usr/local/bin/fish | sudo tee -a /etc/shells
chsh -s /usr/local/bin/fish
```

---

## Step 3: Install Nerd Fonts

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 3a | Via dotfiles script (if available) | All | Installs full recommended set |
| 3b | Manual install (4 recommended fonts) | All | JetBrainsMono, FiraCode, Hack, Meslo |
| 3c | Set Nerd Font in terminal emulator | All | Required for Tide icons |

**3a** — Via dotfiles script:
```fish
~/Apps/000-dotfiles/scripts/004-reinstall/install_nerdfonts.sh
```

**3b** — Manual install:
```fish
mkdir -p ~/.local/share/fonts
cd /tmp
for FONT in JetBrainsMono FiraCode Hack Meslo
  curl -fLo /tmp/$FONT.tar.xz https://github.com/ryanoasis/nerd-fonts/releases/download/v3.4.0/$FONT.tar.xz
  tar -xJf /tmp/$FONT.tar.xz -C ~/.local/share/fonts
  rm /tmp/$FONT.tar.xz
end
fc-cache -fv ~/.local/share/fonts
```

---

## Step 4: Install Fisher, Plugins & Shell Config

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 4a | Install Fisher | All | Fish plugin manager |
| 4b | Install plugins | All | Tide, fzf.fish, z, done, autopair |
| 4c | Configure Tide prompt | All | Nerd Font must be set first (Step 3) |
| 4d | Enable direnv hook | All | Auto-loads .envrc per project |

**4a** — Install Fisher:
```fish
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

**4b** — Install plugins:
```fish
fisher install IlanCosman/tide@v6 PatrickF1/fzf.fish jethrokuan/z franciscolourenco/done jorgebucaran/autopair.fish
```

**4c** — Configure Tide:
```fish
tide configure
```

**4d** — Enable direnv hook:
```fish
echo 'direnv hook fish | source' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

---

## Step 5: Install fnm and Node.js

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 5a | Install fnm | All | Close & reopen terminal after |
| 5b | Install Node.js 25 | All | Installs latest Node 25.x |

**5a** — Install fnm:
```fish
curl -o- https://fnm.vercel.app/install | bash
```

**5b** — Install Node.js:
```fish
fnm install 25
node -v
npm -v
```

---

## Step 6: Configure npm Global Packages

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 6a | Set up npm global dir | All | Avoids needing sudo for npm -g |
| 6b | Verify PATH | All | Should show ~/.npm-global/bin |

**6a** — Set up npm global dir:
```fish
mkdir -p ~/.npm-global/bin
npm config set prefix ~/.npm-global
fish_add_path ~/.npm-global/bin
```

**6b** — Verify PATH:
```fish
echo $fish_user_paths
```

---

## Step 7: Install Go

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 7a | Download & install Go | x86_64 or arm64 | See platform-specific commands below |
| 7b | Verify Go | All | Should show go1.26.0 |

**7a** — x86_64:
```fish
curl -LO https://go.dev/dl/go1.26.0.linux-amd64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.26.0.linux-amd64.tar.gz
rm go1.26.0.linux-amd64.tar.gz
fish_add_path /usr/local/go/bin
```

**7a** — arm64:
```fish
curl -LO https://go.dev/dl/go1.26.0.linux-arm64.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.26.0.linux-arm64.tar.gz
rm go1.26.0.linux-arm64.tar.gz
fish_add_path /usr/local/go/bin
```

**7b** — Verify:
```fish
go version
```

---

## Step 8: Install GitHub CLI (gh)

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 8a | Add GitHub apt repo & install | All | See guide for full command |

**8a** — Install gh:
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

---

## Step 9: Authenticate GitHub CLI

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 9a | Login to GitHub | All | Select: GitHub.com, HTTPS, Yes, Browser |

**9a** — Login:
```fish
gh auth login
```

---

## Step 10: Clone & Run Dotfiles Manager

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| 10a | Clone and launch | All | TUI handles remaining tools |

**10a** — Clone and launch:
```fish
mkdir -p ~/Apps
cd ~/Apps
gh repo clone kairin/000-dotfiles
cd 000-dotfiles
./start.sh
```

---

## M1: Install uv

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M1a | Install uv | All | Python package manager; auto-adds to PATH |
| M1b | Source PATH | All | Current session only |

```fish
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env.fish
```

---

## M2: Install Claude Code

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M2a | Install Claude Code | All | Installs to ~/.local/bin/ |
| M2b | Verify | All | |

```fish
curl -fsSL https://claude.ai/install.sh | bash
which claude && claude --version
```

---

## M3: Install Codex CLI

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M3a | Install Codex CLI | All | Requires npm global config (Step 6) |
| M3b | Verify | All | |

```fish
npm i -g @openai/codex
which codex && codex --version
```

---

## M4: Install Gemini CLI

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M4a | Install Gemini CLI | All | Requires Node.js 20+ |
| M4b | Verify | All | |

```fish
npm i -g @google/gemini-cli
which gemini && gemini --version
```

---

## M5: Install Specify CLI

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M5a | Install Specify CLI | All | Spec-driven development |

```fish
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

---

## M6: Install Backlog.md

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M6a | Install Backlog.md | All | Markdown task manager & Kanban; v1.38.0 |
| M6b | Verify | All | |
| M6c | Init in project | All | Choose MCP connector for AI integration |
| M6d | Add MCP to Claude Code | All | Auto-detects project backlog |
| M6e | Add MCP to Codex CLI | All | |
| M6f | Add MCP to Gemini CLI | All | |

```fish
# Install
npm i -g backlog.md
backlog --help

# Init in project
cd ~/your-project
backlog init "My Project"

# Add MCP servers
claude mcp add backlog --scope user -- backlog mcp start
codex mcp add backlog backlog mcp start
gemini mcp add backlog -s user backlog mcp start
```

---

## M7: Install Context7 MCP

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M7a | Add to Claude Code | All | Get key from context7.com/dashboard |
| M7b | Add to Codex CLI | All | Uses npx-based MCP runner |

```fish
# Claude Code (replace YOUR_KEY)
claude mcp add --scope user --header "CONTEXT7_API_KEY: YOUR_KEY" --transport http context7 https://mcp.context7.com/mcp

# Codex CLI
codex mcp add context7 -- npx -y @upstash/context7-mcp
```

---

## M8: Configure Git with Claude Code

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M8a | Launch Claude Code | All | Then prompt to set up git credentials |
| M8b | Prompt: Set up Git credentials | All | Paste into Claude Code |
| M8c | Prompt: Verify & configure identity | All | Use noreply email |

```fish
claude
```

Prompts to paste in Claude Code:
1. `use gh cli to obtain the relevant credentials to use git`
2. `can you help to verify if gh and git are properly setup?`
3. When asked about identity: `use gh cli to get the correct details but do not use my private email, use the GitHub noreply email address instead`

---

## M9: Init Spec Kit

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M9a | Init for Claude Code | All | Consider adding .claude/ to .gitignore |
| M9b | Init for Codex | All | Consider adding .codex/ to .gitignore |

**Claude Code:**
```fish
cd ~/your-project
specify init --here --ai claude
claude
```

**Codex:**
```fish
cd ~/your-project
specify init --here --ai codex
echo 'export CODEX_HOME="$PWD/.codex"' > .envrc
direnv allow
codex
```

---

## M10: Init Backlog.md in Project

| Sub-step | Action | Platform | Notes |
|----------|--------|----------|-------|
| M10a | Init (interactive wizard) | All | Choose MCP connector for AI integration |
| M10b | Init (Claude Code workflow) | All | Select MCP connector when prompted |
| M10c | Init (Codex workflow) | All | Select MCP connector when prompted |
| M10d | Verify MCP connection | All | Should show backlog server connected |
| M10e | Backlog.md workflow: create tasks | All | board = terminal Kanban; browser = web UI |

```fish
# Init
cd ~/your-project
backlog init "My Project"

# Verify MCP (inside Claude Code or Codex)
/mcp

# Create tasks
backlog task create "My first task"
backlog board
backlog browser
```

---

## V: Verify All Installations

Run this complete verification script in Fish to confirm every tool is installed and working:

```fish
echo ""
echo "━━━ Core System: fastfetch, fish, git ━━━"
fastfetch
fish --version
git --version

echo ""
echo "━━━ Shell Plugins: fisher, tide ━━━"
fisher --version
tide --version

echo ""
echo "━━━ Node.js Ecosystem: fnm, node, npm ━━━"
fnm --version
node --version
npm --version

echo ""
echo "━━━ Go ━━━"
go version

echo ""
echo "━━━ System Utilities: shellcheck, direnv, fzf ━━━"
shellcheck --version
direnv --version
fzf --version

echo ""
echo "━━━ GitHub: gh, auth status ━━━"
gh --version
gh auth status

echo ""
echo "━━━ Python / uv ━━━"
uv --version

echo ""
echo "━━━ AI Coding CLIs: claude, codex, gemini ━━━"
claude --version
codex --version
gemini --version

echo ""
echo "━━━ Task & Spec Tools: backlog, specify ━━━"
backlog --version
specify --help

echo ""
echo "━━━ MCP Servers: claude, codex ━━━"
claude mcp list
codex mcp list

echo ""
echo "━━━ Nerd Fonts: JetBrainsMono, FiraCode, Hack, Meslo ━━━"
fc-list : family | grep -i 'JetBrainsMono\|FiraCode\|Hack\|Meslo'
```

> **Note**: `specify` uses `--help` (no `--version` support). MCP lists verify Context7 + Backlog servers. `fc-list` verifies Nerd Fonts installed.
