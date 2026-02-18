---
title: System Architecture
category: architecture
linked-from: AGENTS.md
status: ACTIVE
last-updated: 2026-02-18
---

# System Architecture

[← Back to AGENTS.md](../../../AGENTS.md)

## Overview

`000-dotfiles` provides an Ubuntu development-environment bootstrap with:
- a Go TUI installer
- staged shell-script lifecycle management
- local-first CI/CD workflows
- AI CLI and MCP-oriented developer setup

## Primary Entry Point

- User-facing: `./start.sh`
- Developer-only: `cd tui && go run ./cmd/installer`

## Core Components

- `tui/`: Go installer application
- `scripts/`: install/check/verify/reinstall/update lifecycle scripts
- `.runners-local/`: local workflow runner and logs
- `configs/`: managed configuration assets (zsh, mcp)
- `.claude/`: agent documentation and instruction system

## Installer Model

The installer uses a data-driven registry (`tui/internal/registry/`) to map tool IDs to scripts across stages:
- detect installed state
- install dependencies
- verify prerequisites
- install/reinstall
- confirm
- update

## Local CI/CD Model

`./.runners-local/workflows/gh-workflow-local.sh` orchestrates local checks, linting, validation, and reporting before remote operations.

## AI Tooling Model

Managed CLIs include:
- Claude Code
- Gemini CLI
- OpenAI Codex CLI
- GitHub Copilot CLI

Spec-Kit integration for Codex is project-scoped through `CODEX_HOME` (recommended via `direnv`).

## Documentation Model

- `AGENTS.md` is the policy gateway.
- Detailed docs are split under `.claude/instructions-for-agents/`.
- Symlink integrity for `CLAUDE.md` and `GEMINI.md` is mandatory.

[← Back to AGENTS.md](../../../AGENTS.md)
