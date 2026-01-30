# Ubuntu Fresh Install Setup Guide

## 1. System Update & Essential Packages

```bash
sudo apt update
sudo apt install curl wget git fastfetch fish -y
```

## 2. Set Fish as Default Shell

```bash
command -v fish | sudo tee -a /etc/shells
chsh -s "$(command -v fish)"
```
Log out and back in for the change to take effect.

## 3. Install Fisher (Fish Plugin Manager)

```fish
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher
```

## 4. Install GitHub CLI (gh)

> **Note:** This command uses bash syntax. Run it with `bash -c` from fish:

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

## 5. Install uv (Python Package Manager)

```fish
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then add to PATH:
```fish
source $HOME/.local/bin/env.fish
```

## 6. Install Claude Code

```fish
curl -fsSL https://claude.ai/install.sh | bash
```

## 7. Install Specify CLI (Spec-Driven Development)

```fish
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

## 8. Install Context7 MCP (Documentation Context for Claude)

1. Get your API key from: https://context7.com/dashboard
2. Install the MCP server (replace `YOUR_API_KEY` with your actual key):

```fish
claude mcp add --header "CONTEXT7_API_KEY: YOUR_API_KEY" --transport http context7 https://mcp.context7.com/mcp
```

## 9. Verify Installation

```fish
fastfetch
fish --version
fisher --version
git --version
gh --version
uv --version
claude --version
specify --help
```

## 10. Authenticate GitHub CLI

```fish
gh auth login
```

During login, select:
- GitHub.com
- HTTPS
- Authenticate Git with credentials: Yes
- Login with a web browser

## 11. Configure Git with Claude Code

Once `gh auth login` is complete, launch Claude Code:

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

## 12. Initialize Spec Kit in a Project

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
1. `/speckit.constitution` - Establish project principles
2. `/speckit.specify` - Create baseline specification
3. `/speckit.plan` - Create implementation plan
4. `/speckit.tasks` - Generate actionable tasks
5. `/speckit.implement` - Execute implementation

**Optional Enhancement Commands:**
- `/speckit.clarify` - Ask questions to de-risk ambiguous areas (before `/speckit.plan`)
- `/speckit.analyze` - Cross-artifact consistency report (after `/speckit.tasks`)
- `/speckit.checklist` - Generate quality checklists (after `/speckit.plan`)

> **Note:** Consider adding `.claude/` to `.gitignore` to prevent accidental credential leakage.

---

## TUI Integration Requirements

This section describes the Fish shell setup integrated into the 000-dotfiles TUI installer.

### Priority
- **Category**: Main Tool (Dashboard)
- **Position**: 5th (after antigravity)
- **Recommendation**: Fish is the recommended modern shell; ZSH remains available in Extras

### Components

| Component | Install Method | Description |
|-----------|---------------|-------------|
| Fish shell | apt | Smart shell with built-in features |
| Fisher | curl script | Plugin manager for Fish |
| fzf.fish | Fisher plugin | Fuzzy finder integration (Ctrl+R, Ctrl+T) |
| z | Fisher plugin | Directory jumping |
| autopair.fish | Fisher plugin | Auto-close brackets and quotes |
| Tide | Fisher plugin | Modern prompt theme (like Powerlevel10k) |
| bass | Fisher plugin | Run bash scripts in Fish |
| done | Fisher plugin | Command completion notifications |

### TUI Actions
1. **Install**: Fish + Fisher + 6 plugins + Tide configuration
2. **Configure**: PATH setup, tool completions, aliases
3. **Update**: apt update + fisher update
4. **Uninstall**: Remove plugins, apt package, preserve configs

### Manual Fish Setup (Without TUI)

If setting up manually without the TUI:

```bash
# Install Fish
sudo apt install fish

# Install Fisher
fish -c 'curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher'

# Install plugins
fish -c 'fisher install PatrickF1/fzf.fish jethrokuan/z jorgebucaran/autopair.fish IlanCosman/tide edc/bass franciscolourenco/done'

# Configure Tide theme
fish -c 'tide configure'

# Set Fish as default shell (optional)
chsh -s $(which fish)
```

### Check Script Output Format
```
INSTALLED|<version>|<method>|<location>^fisher:<yes/no>^plugins:<n>^tide:<yes/no>|<latest>
```

### Notes
- **POSIX Incompatibility**: Fish is not POSIX-compliant. Scripts requiring bash should use `#!/bin/bash` shebang or be run via `bass source ./script.sh`
- **fzf Dependency**: The fzf.fish plugin requires fzf, which is installed automatically
- **Default Shell**: The TUI does NOT automatically set Fish as default shell for safety. Users must run `chsh -s $(which fish)` manually
