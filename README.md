# 000 Dotfiles

Ubuntu development environment setup with LLM CLI tools integration, developer tool management, and zero-cost local CI/CD infrastructure.

## Purpose

This repository provides a comprehensive development environment for Ubuntu 25.04+ including:
- **LLM CLI Tools Configuration**: Sudoers configuration for Claude Code, Gemini CLI, OpenAI Codex CLI, and GitHub Copilot CLI
- **Developer Tools TUI Installer**: Interactive installer for fastfetch, glow, gum, Node.js, AI tools, and more
- **ZSH Configuration**: Oh My Zsh with Powerlevel10k theme and plugins
- **MCP Server Configs**: Model Context Protocol integrations
- **Local CI/CD**: Zero-cost GitHub Actions alternative for local validation

## Quick Start

### One-Line Installation

```bash
wget -qO- https://raw.githubusercontent.com/kairin/000-dotfiles/main/install.sh | bash
```

This installs the sudoers configuration for LLM CLI tools.

### Full Setup (Recommended)

```bash
git clone https://github.com/kairin/000-dotfiles.git ~/Apps/000-dotfiles
cd ~/Apps/000-dotfiles
./start.sh
```

The `start.sh` script provides an interactive setup for all components.

### TUI Installer

For interactive tool management:

```bash
./start.sh
```

The script handles Go installation, building, and launching automatically.

## Components

### Developer Tools (via TUI)

| Tool | Description | Installation Method |
|------|-------------|---------------------|
| **Feh** | Lightweight image viewer | Source build |
| **Node.js** | JavaScript runtime with fnm | Script |
| **Claude Code** | Anthropic Claude CLI | Mixed (curl + npm) |
| **Gemini CLI** | Google Gemini CLI | NPM |
| **OpenAI Codex CLI** | OpenAI Codex command line interface | NPM |
| **GitHub Copilot CLI** | GitHub Copilot command line interface | NPM |
| **Antigravity** | Google Antigravity agentic development platform | Script |
| **Fastfetch** | System info fetcher | APT |
| **Glow** | Terminal markdown renderer | Charm repo |
| **Go** | Go programming language | Tarball |
| **Gum** | TUI component library | Charm repo |
| **Python/uv** | Python with uv package manager | Script |
| **VHS** | Terminal recording/GIF | Charm repo |
| **ZSH** | ZSH + Oh My Zsh + Powerlevel10k | APT |
| **Nerd Fonts** | Developer fonts (8 families) | GitHub release |

### Sudoers Configuration

Passwordless sudo for whitelisted commands used by LLM CLI tools:

| Category | Commands |
|----------|----------|
| **Package Management** | `apt`, `apt-get`, `dpkg`, `snap` |
| **Container Management** | `docker`, `docker-compose` |
| **System Services** | `systemctl` |
| **User Management** | `usermod`, `groupadd` |
| **File Operations** | `install`, `mkdir`, `chmod`, `chown`, `tee` |
| **Network Tools** | `curl`, `wget` |

### LLM Configuration

- `.claude/` - Claude Code settings and instructions
- `.gemini/` - Gemini CLI configuration
- `configs/mcp/` - MCP server configurations

### Local CI/CD

```bash
# Run full validation workflow locally
./.runners-local/workflows/gh-workflow-local.sh all

# Check GitHub Actions billing
./.runners-local/workflows/gh-workflow-local.sh billing
```

## Directory Structure

```
000-dotfiles/
├── .claude/                    # Claude Code configuration
│   ├── instructions-for-agents/
│   └── settings.json
├── .gemini/                    # Gemini CLI configuration
├── .runners-local/             # Local CI/CD infrastructure
├── configs/
│   ├── mcp/                    # MCP server configs
│   └── zsh/                    # ZSH configuration
├── scripts/
│   ├── 000-check/              # Tool check scripts
│   ├── 001-uninstall/          # Tool uninstall scripts
│   ├── 002-install-first-time/ # First-time install scripts
│   ├── 003-verify/             # Verification scripts
│   ├── 004-reinstall/          # Reinstall scripts
│   ├── 005-confirm/            # Confirmation scripts
│   ├── 006-logs/               # Logging scripts
│   ├── 007-diagnostics/        # Diagnostic scripts
│   ├── 007-update/             # Update scripts
│   └── deploy-sudoers.sh       # Sudoers deployment
├── sudoers/
│   └── llm-cli-tools           # Sudoers configuration
├── tui/                        # Go-based TUI installer
├── AGENTS.md                   # LLM instructions (single source of truth)
├── CLAUDE.md -> AGENTS.md      # Symlink for Claude Code
├── GEMINI.md -> AGENTS.md      # Symlink for Gemini CLI
├── install.sh                  # Quick sudoers installer
├── start.sh                    # Full environment setup
└── README.md                   # This file
```

## Requirements

- **OS**: Ubuntu 25.04+ (compatible with 22.04+)
- **Go**: 1.23+ (for TUI installer, optional)
- **Python**: System Python 3
- **Package Manager**: `uv` (auto-installed)

## Security

- `.gitignore` prevents committing secrets
- Sudoers syntax validated before applying
- Automatic rollback on validation failure
- Whitelisted commands only - no blanket sudo access

## Update Management

```bash
# Smart update checker
./scripts/check_updates.sh

# Run update orchestration
./scripts/daily-updates.sh

# View latest update summary
source ./scripts/006-logs/logger.sh && show_latest_update_summary
```

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Contributing

1. Test locally first
2. Update CHANGELOG.md
3. Follow branch naming: `YYYYMMDD-HHMMSS-type-description`
4. Use conventional commits

## License

Personal configuration files - use at your own discretion.
