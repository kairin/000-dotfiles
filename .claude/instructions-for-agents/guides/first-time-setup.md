---
title: First-Time Setup & Installation Guide
category: guides
linked-from: AGENTS.md
status: ACTIVE
last-updated: 2026-02-18
---

# First-Time Setup & Installation Guide

[← Back to AGENTS.md](../../../AGENTS.md)

## Prerequisites

- OS: Ubuntu 25.04+ (24.04 LTS compatible in practice)
- Access: sudo-capable user account
- Network: required for package/tool downloads
- Disk: ~2 GB free recommended

## Installation

### 1. Clone

```bash
cd ~/Apps
git clone https://github.com/kairin/000-dotfiles.git
cd 000-dotfiles
```

### 2. Run installer

```bash
./start.sh
```

`./start.sh` is the user-facing entry point and launches the tool installer workflow.

### 3. Verify core tools

```bash
node --version
claude --version
gemini --version
codex --version
copilot --version
```

## Spec-Kit + Codex (Per-Project Setup)

For any project where you use Spec-Kit with Codex CLI, configure `CODEX_HOME` per repository.

### Recommended: direnv

1. Install and hook `direnv` once:
```bash
sudo apt update && sudo apt install -y direnv
echo 'direnv hook fish | source' >> ~/.config/fish/config.fish
source ~/.config/fish/config.fish
```

2. In each Spec-Kit project root:
```bash
echo 'export CODEX_HOME="$PWD/.codex"' > .envrc
direnv allow
```

After this, entering the directory auto-sets `CODEX_HOME`.

## Local CI/CD (Mandatory Before GitHub)

```bash
./.runners-local/workflows/gh-workflow-local.sh all
```

Optional checks:

```bash
./.runners-local/workflows/gh-workflow-local.sh status
./scripts/check_updates.sh
```

## Optional Configuration

### Git identity

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@users.noreply.github.com"
git config --global init.defaultBranch main
```

### Install Claude agent files to user profile

```bash
./scripts/install-claude-config.sh
```

## Troubleshooting

### Installer fails

```bash
./start.sh --verbose
ls -la .runners-local/logs/
```

### Tool binary not found after install

Open a new shell, then re-check versions. If still missing, rerun installer from `./start.sh` and use the tool detail page to reinstall.

### Spec-Kit commands not available in Codex

In the project root:

```bash
cat .envrc
direnv allow
printf '%s\n' "$CODEX_HOME"
```

Expected: `CODEX_HOME` resolves to `<project>/.codex`.

## Next Steps

1. Read [README.md](../../../README.md)
2. Review [Critical Requirements](../requirements/CRITICAL-requirements.md)
3. Review [Git Strategy](../requirements/git-strategy.md)
4. Review [Local CI/CD Operations](../requirements/local-cicd-operations.md)

[← Back to AGENTS.md](../../../AGENTS.md)
