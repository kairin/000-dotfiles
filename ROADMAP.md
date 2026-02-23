# Development Roadmap

> **Version**: 3.4-Wave-Structure | **Last Updated**: 2026-02-08 | **Status**: Active

This document tracks planned features, outstanding tasks, and maintenance items for the 000-dotfiles project.

---

## Current Status Snapshot (2026-02-08)

### Active SpecKit Specs (Blocking / In Flight)

| Spec | What It Is | Tracking | Status |
|------|------------|----------|--------|
| **015-verbose-spinner-progress** | Per-item progress spinners for NerdFonts/MCPServers/Extras/Installer views | Tasks: [specs/015-verbose-spinner-progress/tasks.md](specs/015-verbose-spinner-progress/tasks.md) • Issues: 54 open (all labeled `015-verbose-spinner-progress`) | 🔴 Next up (blocks UI polish + reduces “black box” loading) |
| **008-mcp-server-dashboard** | New TUI dashboard for MCP servers + Skills/Agents | Tasks: [specs/008-mcp-server-dashboard/tasks.md](specs/008-mcp-server-dashboard/tasks.md) | 📋 Large feature (start after 015 stabilizes UX patterns) |

### Recently Completed Specs (Verified)

| Spec | What It Was | Tracking | Status |
|------|-------------|----------|--------|
| **012-fix-tui-bugs** | Verified and closed issues #196, #197, #199, #200, #201 (terminal restore, refresh, ESC nav, location lines, stray char) | Tasks: [specs/012-fix-tui-bugs/tasks.md](specs/012-fix-tui-bugs/tasks.md) | ✅ Completed + verified |
| **013-fix-fish-tui-display** | Fish appears in main table + detail view; verified prior bug closures | Tasks: [specs/013-fix-fish-tui-display/tasks.md](specs/013-fix-fish-tui-display/tasks.md) | ✅ Completed + verified |

### Recommended Execution Order (Spec Track)

1. **015** (verbose progress spinners): smallest surface area that improves all installs and future debugging
2. **008** (dashboards): biggest feature, benefits from the progress patterns and stable navigation

---

## Vision: Consistent Developer Environment Everywhere

**Goal**: Every Ubuntu Linux system you set up - whether a fresh install or an update to an existing machine - will have all your familiar tools configured identically, so you can work the same way on any computer.

### Why This Matters

| Scenario | Without This Project | With This Project |
|----------|---------------------|-------------------|
| New machine setup | Hours of manual configuration | `git clone && ./start.sh` |
| Updating existing system | Remember what's installed where | `./start.sh` detects and updates |
| AI assistant behavior | Different on each machine | Same 65 agents, same rules, same behavior |
| Tool versions | Drift over time | Centralized version management |

### Core Philosophy: Developer Environment as Code

This project treats your **personal developer environment** the same way infrastructure-as-code treats servers:

1. **Reproducible** - Clone the repo, run one command, get the same environment
2. **Version-controlled** - All configuration is tracked in Git
3. **Declarative** - AGENTS.md defines how AI assistants behave
4. **Idempotent** - Run `./start.sh` multiple times safely; it detects what's already installed
5. **Self-documenting** - 34 guide files explain every component

### What Gets Synchronized

| Category | Components | Status |
|----------|-----------|--------|
| **Shell** | ZSH, Oh My ZSH, PowerLevel10k | ✅ Complete |
| **AI Tools** | Claude Code agents/permissions, Gemini CLI | ✅ Complete |
| **Development** | Go, Node.js (fnm), Python (uv) | ✅ Complete |
| **TUI Tools** | gum, glow, vhs, fastfetch, feh | ✅ Complete |
| **MCP Servers** | Context7, GitHub, MarkItDown, Playwright | ✅ Template ready |

### Design Principles

1. **One Command**: Fresh install should work with `./start.sh`
2. **Detect, Don't Duplicate**: Check if tools exist before installing
3. **Local First**: CI/CD runs locally, not burning GitHub Actions minutes
4. **Script Proliferation Prevention**: Enhance existing scripts, don't create new ones
5. **Single Source of Truth**: AGENTS.md is the master; CLAUDE.md/GEMINI.md are symlinks

### Claude Code: Same Behavior Everywhere

The AI assistant configuration is **fully portable**:

| Component | What It Provides | Location |
|-----------|-----------------|----------|
| **65 Custom Agents** | Specialized subagents for every task type | `.claude/agents/` |
| **195+ Permission Rules** | Pre-approved tools, no repeated prompts | `.claude/settings.local.json` |
| **7 MCP Servers** | Context7, GitHub, MarkItDown, Playwright, HF, shadcn (x2) | `~/.claude.json` (user scope) |
| **34 Guide Files** | Consistent instructions for AI behavior | `.claude/instructions-for-agents/` |
| **Symlink Architecture** | CLAUDE.md → AGENTS.md (single source of truth) | Project root |

**Result**: Clone this repo on any Ubuntu system, and Claude Code will behave identically - same agents available, same permissions configured, same documentation context.

### Update Workflow: Existing Systems

The project supports both **fresh installs** and **updates to existing systems**:

| Scenario | Command | What Happens |
|----------|---------|--------------|
| **Fresh install** | `git clone && ./start.sh` | Installs everything from scratch |
| **Daily auto-update** | `./scripts/daily-updates.sh` (cron) | Runs at 9 AM, updates all tools |
| **Check before update** | `./start.sh` → "Check Updates" | Shows what would change |

**Idempotent by design**: Running `./start.sh` multiple times is safe - it checks what's already installed and skips those tools.

### Machine Management (Future)

Track your fleet of Ubuntu systems:

```
├── inventory.json         # List of machines with this config
├── machine-001.json       # Per-machine version snapshots
├── machine-002.json
└── sync-report.md         # Last sync status
```

---

## Historical Archive

For previously completed waves (Wave 0 through Wave 3, Wave 6a), please see the [Historical Roadmap Archive](specs/archive/roadmap-history.md).

---

## Wave 4: Claude Code Hooks (READY)

> **Priority**: Automation hooks (HIGH VALUE subset) - reduces permission prompts
> **Theme**: Pre/post execution automation

| # | Task | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 18 | Add PermissionRequest hook | 2 hr | **High** | Auto-approve safe ops, reduce prompts |
| 19 | Add PreToolUse validation hook | 1 hr | Medium | Validate before tool execution |
| 20 | Add PostToolUse audit hook | 1 hr | Medium | Log/validate after execution |

**Deferred to backlog**: Stop hook (Low), Setup hook (Low)

**What hooks provide**: Automated pre/post execution scripts. Configured in settings.json.

**Total**: ~4 hours | **Status**: ⏳ Ready to start

**Reference**: [Hooks docs](https://code.claude.com/docs/en/hooks)

---

## Wave 5: Claude Code Memory (READY)

> **Priority**: Persistent rules for consistent behavior - cleaner than AGENTS.md
> **Theme**: Memory rules and standards

| # | Task | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 21 | Create `.claude/rules/git-conventions.md` | 45 min | Medium | Branch naming, commit format rules |
| 22 | Create `.claude/rules/code-standards.md` | 45 min | Low | Project coding standards |
| 23 | Migrate Tailwind rules to `.claude/rules/` | 30 min | Low | Move from `rules-tailwindcss/` |

**What rules provide**: Persistent instructions loaded every session. Cleaner than AGENTS.md.

**Total**: ~2 hours | **Status**: ⏳ Ready to start

**Reference**: [Memory docs](https://code.claude.com/docs/en/memory)

---

## Wave 6b: TUI Polish (READY)

> **Priority**: Complete TUI functionality after detail views
> **Theme**: TUI enhancements and quality

| # | Task | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 28 | Glamour markdown viewer (`details.go`) | 2 hr | Medium | Render docs in-terminal |
| 29 | TUI unit tests | 2 hr | Medium | Quality assurance |
| 30 | "Install All" batch installation | 1 hr | Low | Convenience feature |
| 31 | Proper semver comparison | 1 hr | Low | TUI version handling |

**Total**: ~6 hours | **Status**: ⏳ Ready to start

---

## Wave 7: Documentation Cleanup (READY)

> **Priority**: Finalize documentation consistency
> **Theme**: Documentation standardization

| # | Task | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 32 | Standardize script headers | 2 hr | Medium | 61% coverage → 100% |
| 33 | Add bidirectional cross-references | 1 hr | Medium | Links go A→B but not B→A |
| 34 | Create stage-specific READMEs | 1 hr | Medium | 000-005 directories need docs |
| 35 | Rename LOGGING_GUIDE.md | 15 min | Low | Caps inconsistent |

**Total**: ~4 hours | **Status**: ⏳ Ready to start

---

## Wave 8: CI/CD & Monitoring (READY)

> **Priority**: Automated quality gates
> **Theme**: Continuous quality monitoring

| # | Task | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 36 | Automated link validation | 1.5 hr | Medium | CI/CD enhancement |
| 37 | AGENTS.md size tracking | 30 min | Low | Monitor vs 40KB limit |

**Total**: ~2 hours | **Status**: ⏳ Ready to start

---

## Wave 9: Multi-Machine Foundation (READY)

> **Priority**: Core sync infrastructure
> **Theme**: Cross-system synchronization basics

| # | Task | Effort | Priority | Notes |
|---|------|--------|----------|-------|
| 39 | Per-machine version snapshots | 2 hr | Medium | Record tool versions on each system |
| 40 | Sync status reporting | 2 hr | Medium | Show drift between machines |
| 41 | MCP server configuration sync | 2 hr | **High** | Same MCP servers on all machines |

**Total**: ~8 hours | **Status**: ⏳ Ready to start

---

## Wave 10: Multi-Machine Advanced (BACKLOG)

> **Priority**: Extended sync capabilities - future consideration
> **Theme**: Advanced cross-system features

| Task | Priority | Notes |
|------|----------|-------|
| Remote sync via SSH | Low | Push updates to other machines |
| Version pinning per-machine | Medium | Lock specific versions if needed |
| Rollback capability | Low | Revert to previous tool versions |
| Agent version tracking | Medium | Track agent definitions across systems |
| Permission rule sync | Medium | Ensure identical approval rules |
| MCP secrets portable sync | Medium | Gist export/import via TUI |

**Status**: 📋 Backlog

---

## Wave 11: Advanced Features (BACKLOG)

> **Priority**: Nice-to-have enhancements
> **Theme**: Future polish and advanced capabilities

| Task | Priority | Notes |
|------|----------|-------|
| Add Stop hook for CI/CD | Low | Auto-run validation on completion |
| Add Setup hook | Low | New contributor onboarding |
| Context7 health check integration | Medium | `health-check.sh --context7-validate all` |
| Parallel validation execution | Low | Performance enhancement |
| HTML report generation | Low | Charts and graphs for reports |

**Future consideration**: Could this become a Claude Code plugin for sharing with others?

**Reference**: [Plugins docs](https://code.claude.com/docs/en/plugins)

**Status**: 📋 Backlog

---

## Maintenance Tasks

*No pending maintenance tasks.*

---

## Completed

| Task | Completed | Notes |
|------|-----------|-------|
| TUI Installer v1.0 | 2026-01-17 | Core installation working |
| Nerd Fonts Management | 2026-01-17 | Bulk install/uninstall working |
| Dynamic Theme Switching | 2026-01-17 | Catppuccin Mocha/Latte auto-switch |
| Claude Workflow Generator | 2026-01-17 | TUI command generator |
| Context7 header auth fix | 2026-01-18 | Setup script updated with --header flag |
| MCP scope verification | 2026-01-18 | User scope confirmed correct via Context7 |
| ROADMAP wave restructure | 2026-01-18 | Replaced v3.x with Wave 0-4 structure |
| Wave 0 Foundation Fixes | 2026-01-18 | LICENSE, broken link fix, tier unification - [specs/001-foundation-fixes/](specs/001-foundation-fixes/) |
| Wave 1 Scripts Documentation | 2026-01-18 | 5 READMEs, MCP consolidation, ai-cli-tools fix - [specs/002-scripts-documentation/](specs/002-scripts-documentation/) |
| Wave 2 TUI Features | 2026-01-18 | Per-font selection, MCP management, prerequisites, secrets wizard - [specs/003-tui-features/](specs/003-tui-features/) |
| Wave 3 Skills + Agents | 2026-01-18 | 4 skills + 65 agents consolidated to user-level - [specs/004-claude-skills/](specs/004-claude-skills/) + [specs/005-claude-agents/](specs/005-claude-agents/) |
| Wave 6a TUI Detail Views | 2026-01-18 | ViewToolDetail component, dashboard simplification, extras menu - [specs/006-tui-detail-views/](specs/006-tui-detail-views/) |

---

## SpecKit Verification Summary

All completed waves have been verified against their SpecKit specifications:

| Wave | SpecKit Spec | Checklist | Tasks | Status |
|------|--------------|-----------|-------|--------|
| Wave 0 | [001-foundation-fixes](specs/001-foundation-fixes/) | 16/16 ✓ | 17/17 ✓ | ✅ Verified |
| Wave 1 | [002-scripts-documentation](specs/002-scripts-documentation/) | 16/16 ✓ | 54/54 ✓ | ✅ Verified |
| Wave 2 | [003-tui-features](specs/003-tui-features/) | 16/16 ✓ | 78/78 ✓ | ✅ Verified |
| Wave 3 | [004-claude-skills](specs/004-claude-skills/) + [005-claude-agents](specs/005-claude-agents/) | 16/16 ✓ | 7/7 ✓ | ✅ Verified |
| Wave 4 | *Claude Hooks* | - | 3 defined | ⏳ Ready |
| Wave 5 | *Claude Memory* | - | 3 defined | ⏳ Ready |
| Wave 6a | [006-tui-detail-views](specs/006-tui-detail-views/) | 16/16 ✓ | 44/44 ✓ | ✅ Verified |
| Wave 6b | *TUI Polish* | - | 4 defined | ⏳ Ready |
| Wave 7 | *Documentation* | - | 4 defined | ⏳ Ready |
| Wave 8 | *CI/CD & Monitoring* | - | 2 defined | ⏳ Ready |
| Wave 9 | *Multi-Machine* | - | 4 defined | ⏳ Ready |
| Wave 10-11 | *Backlog* | - | ~11 defined | 📋 Future |

**Total verified tasks:** 193 across 5 completed waves
**Pending tasks:** 35 across 7 ready waves + 11 in backlog

**Last verified:** 2026-02-08

---

## How to Use This Roadmap

### Wave Execution Order

```
COMPLETED:
  Wave 0 (Immediate Fixes)      ✅ Done
  Wave 1 (Foundation Docs)      ✅ Done
  Wave 2 (TUI Features)         ✅ Done
  Wave 3 (Claude Skills+Agents) ✅ Done
  Wave 6a (TUI Detail Views)    ✅ Done

NEXT UP:
  Wave 4 (Claude Hooks)         ⏳ 3 tasks, ~4 hr  ← START HERE
      ↓
  Wave 5 (Claude Memory)        ⏳ 3 tasks, ~2 hr
      ↓
  Wave 5 (Claude Memory)        ⏳ 3 tasks, ~2 hr

THEN ENHANCEMENTS:
  Wave 6b (TUI Polish)          ⏳ 4 tasks, ~6 hr
      ↓
  Wave 7 (Documentation)        ⏳ 4 tasks, ~4 hr
      ↓
  Wave 8 (CI/CD & Monitoring)   ⏳ 2 tasks, ~2 hr
      ↓
  Wave 9 (Multi-Machine)        ⏳ 4 tasks, ~8 hr

BACKLOG:
  Wave 10-11 (Advanced)         📋 ~11 tasks
```

### Status Indicators
- 🔴 **Not Started**: Blocking work, needs immediate attention
- ⏳ **Pending**: Waiting on previous wave completion
- 🟡 **In Progress**: Actively being worked on
- ✅ **Completed**: Done and merged to main
- 📋 **Backlog**: Future consideration, no timeline

### SpecKit Workflow for New Waves

When starting a new wave, use SpecKit to manage the development lifecycle:

```
1. /speckit.specify   →  Create spec.md from ROADMAP tasks
2. /speckit.checklist →  Generate requirements checklist
3. /speckit.plan      →  Create implementation plan
4. /speckit.tasks     →  Generate detailed tasks.md
5. /speckit.implement →  Execute tasks with tracking
6. /speckit.analyze   →  Verify completion
```

**Spec directory structure:**
```
specs/
├── 001-foundation-fixes/      # Wave 0 ✅
├── 002-scripts-documentation/ # Wave 1 ✅
├── 003-tui-features/          # Wave 2 ✅
├── 004-claude-skills/         # Wave 3 (when started)
├── 005-claude-hooks/          # Wave 4 (when started)
├── 006-claude-memory/         # Wave 5 (when started)
├── 007-tui-polish/            # Wave 6 (when started)
├── 008-documentation/         # Wave 7 (when started)
├── 009-cicd-monitoring/       # Wave 8 (when started)
└── 010-multi-machine/         # Wave 9 (when started)
```

### Adding New Items
1. Determine which wave the task belongs to
2. Add with effort estimate and dependencies
3. Include location (file:line if applicable)
4. Move to Completed section when merged

### For AI Assistants
When working on tasks from this roadmap:
1. **Check Wave 0 first** - Complete blocking items before other work
2. Follow [Git Strategy](/.claude/instructions-for-agents/requirements/git-strategy.md)
3. Run [Local CI/CD](/.claude/instructions-for-agents/requirements/local-cicd-operations.md) before pushing
4. Observe [Script Proliferation](/.claude/instructions-for-agents/principles/script-proliferation.md) principle

---

## References

- [README.md](README.md) - Project overview
- [CLAUDE.md](CLAUDE.md) - AI assistant instructions
- [System Architecture](/.claude/instructions-for-agents/architecture/system-architecture.md)
- [First-Time Setup](/.claude/instructions-for-agents/guides/first-time-setup.md)
