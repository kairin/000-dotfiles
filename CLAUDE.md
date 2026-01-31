# 000-Dotfiles - LLM Instructions (2026 Edition)

> **SYMLINK ARCHITECTURE - DO NOT MODIFY**
>
> | File | Role | Action |
> |------|------|--------|
> | `AGENTS.md` | **Master file** (single source of truth) | Edit this file only |
> | `CLAUDE.md` | Symlink -> AGENTS.md | **NEVER convert to regular file** |
> | `GEMINI.md` | Symlink -> AGENTS.md | **NEVER convert to regular file** |
>
> **CONSTITUTIONAL REQUIREMENT**: All edits go to `AGENTS.md`. The symlinks `CLAUDE.md` and `GEMINI.md` must remain as symlinks. DO NOT create separate content, DO NOT break symlinks, DO NOT replace with regular files.

> **CRITICAL**: This file contains NON-NEGOTIABLE requirements that ALL AI assistants (Claude, Gemini, ChatGPT, etc.) working on this repository MUST follow at ALL times.

## Project Overview

**000-Dotfiles** is a comprehensive Ubuntu development environment setup featuring:
- **Developer Tools TUI**: Interactive installer for feh, Node.js, AI tools, glow, gum, and more
- **LLM CLI Integration**: Claude Code, Gemini CLI, GitHub Copilot configurations
- **ZSH Setup**: Oh My Zsh with Powerlevel10k and plugins
- **MCP Servers**: Model Context Protocol integrations
- **Local CI/CD**: Zero-cost GitHub Actions alternative

**Quick Links:** [README](README.md) | [CHANGELOG](CHANGELOG.md)

---

## Complete Documentation Index

> **Token Optimization**: This file is a lightweight gateway. Detailed instructions are in `.claude/instructions-for-agents/`.

### Critical Requirements (NON-NEGOTIABLE)
**Location**: `.claude/instructions-for-agents/requirements/`

- **[All Critical Requirements](/.claude/instructions-for-agents/requirements/CRITICAL-requirements.md)** - Package management, prerequisites, MCP integration
- **[Git Strategy & Branch Management](/.claude/instructions-for-agents/requirements/git-strategy.md)** - Branch preservation, naming, commit workflow
- **[Local CI/CD Operations](/.claude/instructions-for-agents/requirements/local-cicd-operations.md)** - Pipeline stages, workflow tools, logging system

### System Architecture
**Location**: `.claude/instructions-for-agents/architecture/`

- **[System Architecture](/.claude/instructions-for-agents/architecture/system-architecture.md)** - Directory structure, technology stack, core functionality
- **[Directory Structure](/.claude/instructions-for-agents/architecture/DIRECTORY_STRUCTURE.md)** - Complete file tree with descriptions

### Operational Guides
**Location**: `.claude/instructions-for-agents/guides/`

- **[First-Time Setup](/.claude/instructions-for-agents/guides/first-time-setup.md)** - Installation, post-install configuration, troubleshooting

### Constitutional Principles
**Location**: `.claude/instructions-for-agents/principles/`

- **[Script Proliferation Prevention](/.claude/instructions-for-agents/principles/script-proliferation.md)** - Mandatory principle for all script creation

### Tool Implementation Reference
**Location**: `.claude/instructions-for-agents/tools/`

- **[Tool Documentation Index](/.claude/instructions-for-agents/tools/README.md)** - Complete reference for installable tools

---

## Top 5 CRITICAL Requirements (Quick Reference)

### 1. Script Proliferation Prevention (CONSTITUTIONAL PRINCIPLE)
**MANDATORY**: Enhance existing scripts, DO NOT create new wrapper/helper scripts.

**Before creating ANY `.sh` file:**
- [ ] Can this be added to existing script? (If YES -> STOP, add there)
- [ ] Is this a test file? (Only exempt if in `tests/`)
- [ ] Does this violate proliferation principle? (If YES -> STOP)

**Details**: [Script Proliferation Prevention](/.claude/instructions-for-agents/principles/script-proliferation.md)

### 2. Branch Preservation (MANDATORY)
- **NEVER DELETE BRANCHES** without explicit user permission
- Branch naming: `YYYYMMDD-HHMMSS-type-description`
- Always merge to main with `--no-ff`, preserve branch

**Details**: [Git Strategy](/.claude/instructions-for-agents/requirements/git-strategy.md)

### 3. Local CI/CD First (MANDATORY)
**EVERY** configuration change MUST run local CI/CD BEFORE GitHub:

```bash
./.runners-local/workflows/gh-workflow-local.sh all
```

**Details**: [Local CI/CD Operations](/.claude/instructions-for-agents/requirements/local-cicd-operations.md)

### 4. Zero GitHub Actions Cost (MANDATORY)
- All testing runs locally FIRST
- GitHub Actions only for final deployment
- Monitor usage: `gh api user/settings/billing/actions`

**Details**: [Local CI/CD Operations](/.claude/instructions-for-agents/requirements/local-cicd-operations.md#cost-verification-mandatory)

### 5. Context7 MCP Setup (RECOMMENDED)
Query Context7 before major configuration changes.

**Details**: [Context7 MCP Setup](/.claude/instructions-for-agents/guides/context7-mcp.md)

---

## LLM Quick Start Protocol

> **For AI Assistants**: Use this section to quickly classify your task and determine the correct workflow.

### Step 1: Classify Your Task

| Task Type | Complexity | Action | Orchestrator? |
|-----------|------------|--------|---------------|
| Bug fix (single file) | ATOMIC | Direct fix -> validate -> commit | No |
| Feature (multi-file) | MODERATE | TodoWrite -> incremental execution | Maybe |
| Deployment | COMPLEX | Use `000-deploy` agent or orchestrate | Yes |
| Investigation | VARIABLE | Explore first -> propose -> await approval | No |
| Cleanup | MODERATE | Scan -> present findings -> await approval | Yes (approval) |

### Step 2: Pre-Execution Checklist

Before ANY operation, verify:
- [ ] No new scripts created (except in `tests/`)
- [ ] Enhancing existing code (not wrapping with helpers)
- [ ] Local CI/CD will run before GitHub push
- [ ] User approval obtained for destructive operations
- [ ] Branch naming follows `YYYYMMDD-HHMMSS-type-description`

### Step 3: Execution Mode Decision

```
STATE-MUTATING? (git commit, file delete, push)
  |-- YES -> SEQUENTIAL execution only
  |-- NO  -> Check dependencies...

HAS DEPENDENCY on another task?
  |-- YES -> SEQUENTIAL after dependency completes
  |-- NO  -> PARALLEL eligible
```

**Parallel-Safe**: Analysis, validation, health checks, documentation scans
**Sequential-Only**: Git operations, file deletions, deployments

### Error Handling Protocol

| Error Type | Response | Max Retries |
|------------|----------|-------------|
| Transient (network, timeout) | Retry immediately | 3 |
| Input error (invalid format) | Fix input, retry | 2 |
| Dependency failure | Fix upstream first | 1 cascade |
| Constitutional violation | **ESCALATE to user** | 0 (no retry) |

**Constitutional violations NEVER retry** - always escalate immediately.

---

## Development Commands (Quick Reference)

### Environment Setup
```bash
./start.sh                                  # One-command fresh install
./.runners-local/workflows/gh-workflow-local.sh init  # Initialize CI/CD
```

### Local CI/CD Operations
```bash
./.runners-local/workflows/gh-workflow-local.sh all      # Complete workflow
./.runners-local/workflows/gh-workflow-local.sh validate # Config validation
./.runners-local/workflows/gh-workflow-local.sh billing  # Check Actions usage
```

### Update Management
```bash
./scripts/check_updates.sh              # Smart updates
```

### TUI Installer
```bash
cd tui && go run ./cmd/installer        # Launch TUI installer
./tui/dotfiles-installer                # Run compiled binary (if built)
```
**Features**: Interactive tool installation, Nerd Fonts management, update/uninstall support

### Testing & Validation
```bash
./.runners-local/workflows/performance-monitor.sh --baseline  # Performance test
```

**Complete Guide**: [First-Time Setup](/.claude/instructions-for-agents/guides/first-time-setup.md)

---

## ABSOLUTE PROHIBITIONS (DO NOT)

- Delete branches without explicit user permission
- Use GitHub Actions that consume minutes (run locally first)
- Skip local CI/CD validation before GitHub deployment
- Create wrapper/helper scripts (violates script proliferation principle)
- Commit sensitive data (API keys, passwords)

**Complete List**: [Critical Requirements](/.claude/instructions-for-agents/requirements/CRITICAL-requirements.md)

---

## MANDATORY ACTIONS (Before Every Configuration Change)

1. **Local CI/CD**: Run `./.runners-local/workflows/gh-workflow-local.sh all`
2. **Branch**: Create timestamped branch (`YYYYMMDD-HHMMSS-type-description`)
3. **Documentation**: Update relevant docs if adding features
4. **Commit**: Use proper format with co-authorship

**Complete Checklist**: [Git Strategy - Pre-Commit](/.claude/instructions-for-agents/requirements/git-strategy.md#pre-commit-checklist)

---

## Success Criteria

### Performance Metrics
- **CI/CD**: <2 minutes complete workflow
- **Setup**: <10 minutes fresh Ubuntu install

### Quality Gates
- Local CI/CD workflows pass
- Configuration validates without errors
- GitHub Actions usage within free tier
- All logging captures complete information

---

## Additional Documentation

### Key Documents
- [README.md](README.md) - User documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CLAUDE.md](CLAUDE.md) - Claude Code integration (symlink to this file)
- [GEMINI.md](GEMINI.md) - Gemini CLI integration (symlink to this file)

### Setup Guides
- [MCP Setup Guide](/.claude/instructions-for-agents/guides/mcp-setup.md) - Complete setup for MCP servers
- [Context7 MCP](/.claude/instructions-for-agents/guides/context7-mcp.md) - Documentation server
- [GitHub MCP](/.claude/instructions-for-agents/guides/github-mcp.md) - Repository operations
- [Logging Guide](/.claude/instructions-for-agents/guides/LOGGING_GUIDE.md) - Dual-mode logging system

### Agent & Command Reference

| Tier | Model | Count | Purpose |
|------|-------|-------|---------|
| 0 | Sonnet | 5 | Complete workflows (000-*) |
| 1 | Opus | 1 | Multi-agent orchestration |
| 2-3 | Sonnet | 9 | Core/utility operations |
| 4 | Haiku | 50 | Atomic execution |

- **[Agent Delegation Guide](/.claude/instructions-for-agents/architecture/agent-delegation.md)** - When to use which tier
- **[Agent Registry](/.claude/instructions-for-agents/architecture/agent-registry.md)** - Complete agent reference
- **Workflow Agents**: `000-health`, `000-cleanup`, `000-commit`, `000-deploy`, `000-docs`

---

## Finding Specific Information

### "How do I...?"
-> See [First-Time Setup Guide](/.claude/instructions-for-agents/guides/first-time-setup.md)

### "What are the critical requirements for...?"
-> See [Critical Requirements](/.claude/instructions-for-agents/requirements/CRITICAL-requirements.md)

### "How does the branch workflow work?"
-> See [Git Strategy](/.claude/instructions-for-agents/requirements/git-strategy.md)

### "How do I run local CI/CD?"
-> See [Local CI/CD Operations](/.claude/instructions-for-agents/requirements/local-cicd-operations.md)

### "What is the system architecture?"
-> See [System Architecture](/.claude/instructions-for-agents/architecture/system-architecture.md)

---

## Metadata

**Version**: 4.0-2026-Dotfiles-Migration
**Last Updated**: 2026-01-27
**Status**: ACTIVE - MANDATORY COMPLIANCE
**Target**: Ubuntu 25.04+ with zero-cost local CI/CD
**Token Count**: ~1,200 tokens

### Recent Changes (v4.0)
- **Migration**: Consolidated from ghostty-config-files repository
- **TUI Installer**: Renamed to dotfiles-installer, removed Ghostty tool
- **Focus**: General developer environment setup, not terminal-specific
- **Simplified**: Removed terminal-specific validation steps

---

**CRITICAL**: These requirements are NON-NEGOTIABLE. All AI assistants must follow these guidelines exactly. Failure to comply may result in configuration corruption, performance degradation, user data loss, or unexpected GitHub Actions charges.

**Full Details**: All detailed instructions, examples, diagrams, and comprehensive documentation are preserved in `.claude/instructions-for-agents/` directory structure.

## Active Technologies
- Go 1.23+ (existing TUI codebase) + Bubbletea, Lipgloss (existing) (003-fix-fish-tui-display)
- N/A (UI-only change) (003-fix-fish-tui-display)
- N/A (UI-only change + GitHub issue management) (003-fix-fish-tui-display)
- Go 1.23+ + Bubbletea, Bubbles (spinner), Lipgloss (styling) (015-verbose-spinner-progress)
- Go 1.23+ + Bubbletea (TUI framework), Bubbles (spinner), Lipgloss (styling) (015-verbose-spinner-progress)
- N/A (UI-only changes) (015-verbose-spinner-progress)

## Recent Changes
- 003-fix-fish-tui-display: Added Go 1.23+ (existing TUI codebase) + Bubbletea, Lipgloss (existing)
