---
name: setup-claude-code
description: Use when setting up Claude Code for the first time and need to register global MCP servers (GitHub, Codacy) and enable plugins so all sessions have full tool access
tags: [setup, mcp-servers, plugins, automation, one-time]
---

# Setup Claude Code

## Overview

One-time global setup that registers MCP servers and enables plugins in Claude Code. After running, all Claude Code sessions everywhere automatically have access to GitHub and Codacy tools, quality-gate plugin features, and related automations.

This skill removes the friction of manual configuration—run once, forget about it, everything works.

## When to Use

Use this skill when:
- First time setting up Claude Code on a machine
- Switching to a new machine or fresh OS install
- Resetting Claude Code configuration
- Troubleshooting "MCP servers not available" errors
- Team member needs to onboard with full tooling

**Before running:**
- `gh` must be authenticated: `gh auth login`
- Codacy account token must exist: `~/.codacy/account-token`

## What Gets Configured

| Component | Scope | Status After Setup |
|-----------|-------|-------------------|
| GitHub MCP | User (global) | Registered + available in all sessions |
| Codacy MCP | User (global) | Registered + available in all sessions |
| quality-gate plugin | User (global) | Enabled + hooks active |
| GITHUB_TOKEN env var | Session | Auto-exported from `gh auth token` |
| CODACY_ACCOUNT_TOKEN env var | Session | Auto-exported from `~/.codacy/account-token` |
| SessionStart hooks | Project | Quality pipeline prompt on session open |

## How to Run

### From Claude Code
```
/setup-claude-code
```

### From Terminal
```bash
# Option 1: Interactive setup (recommended)
cd ~/Apps/000-dotfiles-main
./setup
# Select: "Option 4: Manage optional integrations"

# Option 2: Manual commands
claude mcp add -e 'GITHUB_TOKEN=$(gh auth token)' --scope user github -- npx -y @modelcontextprotocol/server-github
claude mcp add -e 'CODACY_ACCOUNT_TOKEN=$(cat ~/.codacy/account-token)' --scope user codacy -- npx -y @codacy/codacy-mcp@latest
```

## Verify Setup Worked

Check that MCP servers are registered:

```bash
claude mcp list --scope user
# Expected output:
#   github         ✓
#   codacy         ✓

# Or inspect the config directly:
cat ~/.claude.json | jq '.mcpServers'
```

Check that plugins are enabled:

```bash
cat ~/.claude.json | jq '.enabledPlugins'
# Expected:
#   { "quality-gate": true }
```

## What Happens After Setup

### In Every Claude Code Session
- MCP servers auto-load (no manual setup needed)
- Plugins auto-load from global registry
- SessionStart hook prompts: "Run quality pipeline?"
- All tools immediately available

### In This Project (dotfiles)
- Opening in Claude Code triggers quality pipeline prompt
- Can invoke `/quality-pipeline` slash command
- Can run `./scripts/quality-pipeline.sh` from terminal
- GitHub and Codacy operations integrate seamlessly

### In Other Projects
- MCP servers available (GitHub, Codacy)
- Plugins available (quality-gate)
- Can use any Claude Code automation that depends on these

## Common Mistakes

**Running setup but skipping "Register MCP servers" step**
- Result: MCP tools say "not available"
- Fix: Complete the full setup; all steps are required

**Assuming setup only affects current project**
- Result: Confused when MCP servers don't work in other projects
- Fix: Setup is global and persistent; affects all sessions forever

**Running setup without authenticating gh**
- Result: GITHUB_TOKEN env var is empty; GitHub MCP fails silently
- Fix: Run `gh auth login` first; verify with `gh auth status`

**Running setup multiple times**
- Result: Harmless—script detects existing servers and skips re-registration
- Fix: No action needed; safe to re-run

**Editing ~/.claude.json manually after setup**
- Result: Custom config may be overwritten on restart
- Fix: Use `claude mcp add/remove` commands instead of hand-editing

## After Setup: What's Next?

1. **Restart Claude Code** (if already running)
   ```bash
   # If using CLI
   exit  # or Ctrl+D
   claude  # Restart
   ```

2. **Open dotfiles project**
   ```bash
   cd ~/Apps/000-dotfiles-main
   claude
   ```
   You should see: "Run quality pipeline? [y/N]"

3. **Run the quality pipeline** (optional, but recommended)
   Select yes to validate the full setup works

4. **Verify MCP servers are working**
   ```
   In Claude Code, try: /github or /codacy
   (These are slash commands provided by MCP servers)
   ```

## Troubleshooting

**"GITHUB_TOKEN is empty"**
- Cause: `gh` not authenticated
- Fix: `gh auth login` (follow prompts to sign in)

**"CODACY_ACCOUNT_TOKEN is empty"**
- Cause: `~/.codacy/account-token` file not found
- Fix: Create it: `mkdir -p ~/.codacy && echo "your-token" > ~/.codacy/account-token`

**"MCP server command not found"**
- Cause: `npx` or Node.js not installed
- Fix: `npm install -g npx` or use `uv` to install Node: `uv tool install node`

**"claude mcp add fails"**
- Cause: Claude CLI not installed or old version
- Fix: Update Claude: `curl https://claude.ai/install.sh | bash`

## Real-World Impact

Before setup:
- Install Claude Code
- Manually register each MCP server
- Copy config files
- Restart Claude Code
- Still missing some features
- Result: 15-20 min, frustrating

After setup:
- Run `/setup-claude-code`
- Everything ready immediately
- Same configuration everywhere
- Result: 2-3 min, seamless
