# Dotfiles Quality Gate Plugin — Codex CLI Edition

Complete quality pipeline automation for the dotfiles project on Codex CLI. This plugin bundles three core skills for managing dotfiles and enforcing code quality standards before pushing to remote.

## What's Included

### Core Skills (Shared with Claude Code)

All three skills are identical across both Claude Code and Codex CLI:

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

### Codex CLI Features

**MCP Servers** — Fully defined with environment variables:
- **GitHub** — Issue management, PR operations, code search
- **Codacy** — Quality metrics, coverage analysis, issue tracking

**Hooks** (Codex CLI Advantages):
- **SessionStart** — Guides recommended plugin installation
- **PermissionRequest** — Gates `git push` without running quality pipeline
- **PreToolUse** — Blocks dangerous operations (e.g., direct .env edits)
- **PostToolUse** — Provides guidance after tool completion

## Installation

### From Local Dotfiles Repo

```bash
codex plugin install ~/Apps/000-dotfiles-main
```

### From GitHub

```bash
codex plugin install kairin/000-dotfiles-quality-gate
```

### From Codex Marketplace (Future)

```bash
codex plugin install dotfiles-quality-gate
```

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

#### 3. Verify MCP Servers (Optional)
```bash
codex config show mcp
# Expected output: github and codacy both listed as active
```

## Usage

### Run Quality Pipeline

```
/quality-pipeline
```

All 7 stages run automatically. Exit code 0 = all checks pass.

### Apply Dotfiles

```
/dotfiles-apply
```

Prompts for phase selection:
- **doctor** — Diagnose current state
- **plan** — Preview changes
- **apply** — Make changes with backup

### Setup Claude Code (Optional)

```
/setup-claude-code
```

Registers GitHub and Codacy MCP servers globally for Claude Code sessions.

## Codex CLI Advantages Over Claude Code

### 1. Richer Hook System
This plugin leverages Codex's advanced hooks:

```json
{
  "PermissionRequest": "Gates git push without running /quality-pipeline",
  "PreToolUse": "Blocks .env file edits (prevent secrets)",
  "PostToolUse": "Provides guidance after tool completion"
}
```

Claude Code only supports `SessionStart` hooks; Codex CLI supports 6 event types.

### 2. Scope-Based Configuration
Define hooks at **user** or **project** scope:
```json
{
  "scopes": ["user", "project"]
}
```

User-scoped hooks apply to all projects; project-scoped hooks affect only current directory.

### 3. Built-in Settings
```json
{
  "settings": {
    "quality-pipeline": {
      "enabled": true,
      "stages": ["tests", "complexity", "review", "style", "architecture", "optimization", "gate"]
    }
  }
}
```

Enable/disable individual pipeline stages via `codex config`.

### 4. Native GitHub Marketplace
Codex CLI has formal plugin marketplace:
```
https://github.com/openai/codex-plugins/
```

Claude Code requires manual plugin installation.

## Configuration

### User-Level Configuration

Edit `~/.codex/config.toml`:

```toml
[plugins]
"dotfiles-quality-gate" = "~1.0.0"

[plugins.settings]
"dotfiles-quality-gate.quality-pipeline.enabled" = true
"dotfiles-quality-gate.quality-pipeline.stages" = ["tests", "complexity", "review"]
```

### Project-Level Configuration

Edit `.codex/config.toml` in your repo:

```toml
[plugins]
"dotfiles-quality-gate" = { path = "./", version = "1.0.0" }

[hooks]
enabled = true
"SessionStart" = true
"PermissionRequest" = true
```

## File Organization

```
dotfiles/
  .agents/skills/                            # Shared with Claude Code
    quality-pipeline/SKILL.md
    setup-claude-code/SKILL.md
    dotfiles-apply/SKILL.md
  
  .codex/
    plugins/
      dotfiles-quality-gate/
        plugin.json                          # Codex manifest
        hooks/hooks.json                     # Codex hooks
        README.md                            # This file
  
  .claude/
    plugins/
      dotfiles-quality-gate/
        plugin.json                          # Claude Code manifest
        hooks/hooks.json                     # Claude Code hooks
```

## Hooks Explained

### SessionStart Hook
Runs when Codex CLI session begins. Prints guidance on:
- How to use the three skills
- Which recommended plugins to install
- How to check MCP server status

### PermissionRequest Hook
Blocks unsafe operations:
- Prevents `git push` without running `/quality-pipeline` first
- Provides helpful error message guiding user to correct workflow

### PreToolUse Hook
Prevents dangerous writes:
- Blocks editing `.env` files directly
- Suggests using `.envrc.local` instead (personal, not committed)

### PostToolUse Hook
Provides context-aware guidance:
- After running tests, suggests running `/quality-pipeline`
- Helps users build better habits

## Troubleshooting

### MCP Servers Not Available
```bash
# Verify setup
codex config show mcp

# If missing, re-run prerequisites:
gh auth login
mkdir -p ~/.codacy && echo "token" > ~/.codacy/account-token
```

### Hooks Not Triggering
Hooks require explicit scopes in `.codex/config.toml`:

```toml
[plugins.dotfiles-quality-gate]
hooks.scopes = ["user", "project"]
```

Or use CLI:
```bash
codex config set plugins.dotfiles-quality-gate.hooks.scopes user project
```

### PermissionRequest Hook Blocking Legitimate Pushes
If you need to bypass the quality gate (not recommended):

```bash
codex plugin disable dotfiles-quality-gate
git push origin main
codex plugin enable dotfiles-quality-gate
```

Or modify hook enablement in `.codex/config.toml`:

```toml
[[hooks]]
matcher = "Bash.*git\\spush"
enabled = false
```

## Comparison: Claude Code vs Codex CLI

| Feature | Claude Code | Codex CLI |
|---------|---|---|
| Skills bundling | ✓ | ✓ |
| Shared skill content | ✓ | ✓ |
| SessionStart hook | ✓ | ✓ |
| PermissionRequest hook | ✗ | ✓ |
| PreToolUse hook | ✓ | ✓ |
| PostToolUse hook | ✗ | ✓ |
| Scope-based config | ✗ | ✓ |
| Feature flags | ✗ | ✓ |
| Plugin marketplace | ✗ | ✓ (GitHub) |
| MCP definitions | Reference | Full | 

## Integration with Superpowers

Both Claude Code and Codex CLI benefit from superpowers plugin:

```bash
# Claude Code
claude plugin install superpowers

# Codex CLI
codex plugin install superpowers
```

When installed, your quality pipeline stages leverage:
- **TDD** — Test-first workflow for quality gates
- **Debugging** — When stages fail, systematic debugging guide
- **Code review** — Stage 3 uses code review patterns
- **Planning** — Before large dotfiles changes, use /writing-plans skill

## Contributing

Skills are shared in `.agents/skills/`. To contribute:

1. Edit skill in `.agents/skills/<skill-name>/SKILL.md`
2. Test in both Claude Code and Codex CLI
3. Update version in both `.claude/plugins/` and `.codex/plugins/` manifests
4. Submit PR

## License

MIT — See repository for details.

## Support

- **Issues**: GitHub Issues (https://github.com/kairin/000-dotfiles/issues)
- **Docs**: README.md (this file) and skill content
- **Feedback**: Use `codex feedback` command

---

**Next Steps:**
1. Install recommended plugins: `codex plugin install superpowers`
2. Verify setup: `codex config show`
3. Try a skill: `/quality-pipeline`
