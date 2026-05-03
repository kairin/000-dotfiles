# Dotfiles Quality Gate Plugin

Complete quality pipeline automation for the dotfiles project. This plugin bundles three core skills for managing dotfiles and enforcing code quality standards before pushing to remote.

## What's Included

### Core Skills

1. **quality-pipeline** — 7-stage pre-push validation
   - Local tests + complexity checks (automated)
   - Code review, style, architecture, optimization analysis (agent-driven)
   - Codacy quality gate (remote validation)
   - Prevents broken pushes before they reach GitHub

2. **setup-claude-code** — One-time global Claude Code setup
   - Registers GitHub MCP server (requires `gh auth login`)
   - Registers Codacy MCP server (requires `~/.codacy/account-token`)
   - Enables MCP tools across all Claude Code sessions
   - Includes verification step to confirm setup worked

3. **dotfiles-apply** — Safe machine sync workflow
   - Doctor phase: Audit current state without changes
   - Plan phase: Preview what will change before applying
   - Apply phase: Make changes with automatic backups
   - Preserves user customizations and protected files

### MCP Servers

Plugin declares these MCP servers as required:
- **GitHub** — Issue management, PR operations, code search
- **Codacy** — Quality metrics, coverage analysis, issue tracking

## Installation

### Option 1: From Dotfiles Repo (Recommended)

```bash
cd ~/Apps/000-dotfiles-main
claude plugin install .
# Or install from GitHub:
claude plugin install https://github.com/kairin/000-dotfiles
```

After install, restart Claude Code:
```bash
exit  # or Ctrl+D
claude
```

### Option 2: Manual Installation

Copy this directory to `~/.claude/plugins/dotfiles-quality-gate`:

```bash
cp -r ~/.claude/plugins/dotfiles-quality-gate /path/to/.claude/plugins/
```

## Recommended Plugins

When you first install this plugin, a SessionStart hook will suggest installing these complementary plugins:

### Superpowers Ecosystem (Core Development)
```bash
claude plugin install superpowers
```
Includes: TDD, debugging, code review, planning, subagent dispatch, git worktrees

**Why:** Many of the agent-driven stages in quality-pipeline leverage superpowers skills for code analysis and review.

### Plugin Development Ecosystem (If Extending)
```bash
claude plugin install plugin-dev
```
Includes: Agent development, command development, hook development, MCP integration

**Why:** If you plan to extend the dotfiles automation or create custom plugins.

### MCP Server Development (For Custom Integrations)
```bash
claude plugin install mcp-server-dev
```
Includes: Build MCP apps, build MCP servers, build MCPB packages

**Why:** Develop custom MCP servers for your toolchain.

### Desktop Commander (File Operations)
```bash
claude plugin install desktop-commander
```
Includes: Local file and directory operations, search, process management

**Why:** Complements dotfiles-apply for interactive file operations.

## Setup

### Prerequisites

Before using the skills, complete one-time setup:

#### 1. GitHub Authentication
```bash
gh auth login
# Follow prompts to authenticate with GitHub
# Verify: gh auth status
```

#### 2. Codacy Account Token
```bash
mkdir -p ~/.codacy
# Get your account token from https://app.codacy.com/account/settings/tokens
echo "your-token-here" > ~/.codacy/account-token
chmod 600 ~/.codacy/account-token
```

#### 3. Run Setup Skill (Optional, Automates MCP Registration)
```
/setup-claude-code
```
This registers GitHub and Codacy MCP servers globally so all Claude Code sessions can access them.

### Quick Start

1. **Install the plugin**
2. **Run setup** (register MCPs, authenticate)
3. **Use the skills:**
   - `/quality-pipeline` — Before pushing code
   - `/setup-claude-code` — First-time global setup
   - `/dotfiles-apply` — Sync machine state with dotfiles

## Usage Examples

### Validate Before Pushing

```bash
/quality-pipeline
# Runs all 7 stages, reports any issues
# Prevents push if quality gates fail
```

### First-Time Claude Code Setup

```
/setup-claude-code
# Registers GitHub and Codacy MCP servers
# All subsequent sessions have full tool access
```

### Sync Dotfiles to Machine

```bash
/dotfiles-apply
# Prompts: doctor → plan → apply
# Doctor: Check what needs syncing
# Plan: Preview changes without applying
# Apply: Sync changes with automatic backup
```

## File Organization

```
.claude/
  plugins/
    dotfiles-quality-gate/
      plugin.json           # Plugin metadata
      hooks/
        hooks.json          # SessionStart hook (guides plugin install)
      README.md             # This file

.claude/
  skills/
    quality-pipeline/       # 7-stage validation
    setup-claude-code/      # MCP registration
    dotfiles-apply/         # doctor/plan/apply workflow
```

## How It Works

### quality-pipeline Skill

1. **Stages 1-2** (Automated via git hook)
   - Unit tests (pytest)
   - McCabe complexity check (radon)

2. **Stages 3-5** (Agent-driven analysis)
   - Code review (agent examines changes)
   - Style analysis (agent checks conventions)
   - Architecture review (agent checks design)

3. **Stages 6-7** (Automated + remote gate)
   - Optimization check (agent suggests improvements)
   - Codacy quality gate (remote CI checks for violations)

### setup-claude-code Skill

Registers two MCP servers globally:

```bash
# GitHub MCP
claude mcp add -e 'GITHUB_TOKEN=$(gh auth token)' --scope user github \
  -- npx -y @modelcontextprotocol/server-github

# Codacy MCP
claude mcp add -e 'CODACY_ACCOUNT_TOKEN=$(cat ~/.codacy/account-token)' --scope user codacy \
  -- npx -y @codacy/codacy-mcp@latest
```

After setup:
- All Claude Code sessions can use `/github` and `/codacy` commands
- All MCP tools are available without manual setup
- Environment variables are auto-loaded from tokens

### dotfiles-apply Skill

Three-phase workflow:

```bash
# Phase 1: Doctor (diagnose without changing)
uv run python -m dotfiles_tools doctor --repo . --home $HOME
# ↓ Reports missing files, drifted config, protected files

# Phase 2: Plan (show changes without applying)
uv run python -m dotfiles_tools plan --repo . --home $HOME --profile machine
# ↓ Lists all files that will change, where backups go, what's skipped

# Phase 3: Apply (make changes with backup)
uv run python -m dotfiles_tools apply --repo . --home $HOME --profile machine --yes
# ↓ Backs up changed files, applies updates, reports success/failure
```

## Known Limitations

### quality-pipeline
- Code review stages (3-5) are powered by Claude, which gives human-quality but not deterministic results
- Merge strategy for conflicting review findings is not automated (requires human judgment)

### setup-claude-code
- Requires `gh` and `npm`/`npx` installed
- Token debugging (checking if vars are set correctly) is manual

### dotfiles-apply
- Recovery from failed apply requires manual intervention (restores from backup in ~/.dotfiles-backups/)
- Protected file handling requires understanding the dotfiles manifest

## Troubleshooting

### MCP Servers Not Available
```bash
# Verify setup:
claude mcp list --scope user
# Expected: github, codacy both listed

# If missing, run:
/setup-claude-code
```

### Quality Pipeline Fails
```bash
# Check what stage failed:
/quality-pipeline
# Review output, fix issues, re-run
```

### Dotfiles Apply Fails
```bash
# Always run doctor first:
/dotfiles-apply
# Select "doctor" to diagnose issues

# Then plan to preview:
/dotfiles-apply
# Select "plan" to see changes

# Then apply with confidence:
/dotfiles-apply
# Select "apply"

# Restore from backup if needed:
ls ~/.dotfiles-backups/
```

## Integration with Superpowers

This plugin works seamlessly with superpowers skills:

- **TDD** — quality-pipeline enforces test-first workflow
- **Code Review** — quality-pipeline stage 3 uses code review patterns
- **Debugging** — When quality gates fail, use systematic-debugging
- **Planning** — Use writing-plans before large dotfiles changes

Install superpowers for full integration:
```bash
claude plugin install superpowers
```

## Contributing

To extend or modify these skills, see:
- `.claude/skills/quality-pipeline/SKILL.md` — Skill reference
- `.claude/skills/setup-claude-code/SKILL.md` — Skill reference
- `.claude/skills/dotfiles-apply/SKILL.md` — Skill reference

Each skill follows RED-GREEN-REFACTOR TDD methodology with documented edge cases.

## License

MIT — See repository for details.
