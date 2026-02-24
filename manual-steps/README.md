# Manual Steps — Developer Environment Setup

> **Purpose**: Manual CLI setup guides, verification artifacts, and comparison with the TUI installer for Ubuntu development environments.

This folder contains the complete manual setup path for configuring a developer workstation. It complements the TUI installer (`./start.sh`) by providing a transparent, paste-and-run alternative that achieves the same end state.

## File Index

| File | Description |
|------|-------------|
| [ubuntu-fresh-install-setup-guide.md](ubuntu-fresh-install-setup-guide.md) | Canonical 485-line narrative guide — step-by-step walkthrough for fresh Ubuntu installs (also covers Raspberry Pi / Orange Pi) |
| [version-verification.md](version-verification.md) | 24-tool version matrix — which versions the guide targets, what's current, and install methods |
| [setup-steps.md](setup-steps.md) | 55-step command reference — every command organized by section with platform notes |
| [verification-output.md](verification-output.md) | Formatted terminal output from running the full verification script (25 Feb 2026) |
| [version-verification-feb2026.xlsx](version-verification-feb2026.xlsx) | Original Excel workbook (preserved) — source for version-verification.md and setup-steps.md |
| [verification-output-feb2026.txt](verification-output-feb2026.txt) | Original terminal capture (preserved) — source for verification-output.md |

## Manual CLI vs TUI Installer

Both approaches produce the same fully-configured environment. They differ in speed, coverage, and use case.

### Why Manual Is Faster for Fresh Installs

1. **Batch apt install** — Manual runs `sudo apt install curl wget git fastfetch fish shellcheck direnv fzf -y` (8 packages, 1 command). TUI runs each tool through a separate 5-stage pipeline (check, deps, verify, install, confirm), each stage a separate shell script invocation.

2. **No Go bootstrap** — TUI requires: install Go (4-stage pipeline) then compile TUI binary then launch. Manual starts immediately with `apt`.

3. **~85 script invocations vs ~30 commands** — 17 TUI tools x 5 stages = 85 shell scripts. Manual uses ~30 direct commands total.

4. **Coverage gaps** — TUI doesn't handle: `chsh` (Fish as default), Fisher + plugins (Tide, fzf.fish, z, done, autopair.fish), npm global dir config, `gh auth login`, MCP server setup, git credential config, Spec Kit init, Backlog.md init. These must be done manually after TUI anyway.

5. **No UI navigation overhead** — Manual is linear paste-and-run. TUI requires screen navigation, tool selection, confirmation dialogs.

### When to Use the TUI Instead

The TUI (`./start.sh`) is better for **ongoing maintenance**:

- **Interactive selection** — pick individual tools to install/update/uninstall
- **Resumable installs** — interrupted installs can continue where they left off
- **Update management** — detects installed versions and shows what's outdated
- **Extras catalog** — Nerd Fonts, themes, and optional tools
- **Diagnostics** — workstation audit, health checks

### Recommendation

| Scenario | Use |
|----------|-----|
| Fresh Ubuntu install | Manual CLI guide |
| Setting up a new SBC (Raspberry Pi, Orange Pi) | Manual CLI guide |
| Updating tools on an existing machine | TUI (`./start.sh`) |
| Installing/removing individual tools | TUI (`./start.sh`) |
| Debugging a broken install | Manual CLI guide (transparent commands) |

## Cross-References

- **TUI entry point**: `./start.sh` (repo root)
- **Agent instructions for setup**: [.claude/instructions-for-agents/guides/ubuntu-fresh-install-setup-guide.md](../.claude/instructions-for-agents/guides/ubuntu-fresh-install-setup-guide.md) (shorter agent-facing version, separate file)
- **Roadmap**: [ROADMAP.md](../ROADMAP.md)

---

**Last updated**: 25 Feb 2026
