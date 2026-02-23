# Historical Roadmap Archive

This document contains completed development waves that have been fully implemented and verified. They are archived here to keep the main `ROADMAP.md` clean and focused on active work.

---

## Wave 0: Immediate Fixes (COMPLETE)

> **Priority**: ✅ COMPLETED - 2026-01-18

| # | Task | Effort | Blocker For | Status |
|---|------|--------|-------------|--------|
| 1 | Create LICENSE file | 5 min | README badges, project credibility | ✅ Done |
| 2 | Fix broken link in local-cicd-operations.md | 5 min | AI assistant navigation | ✅ Done |
| 3 | Unify agent tier definitions (4→5 tier) | 30 min | Documentation consistency | ✅ Done |

**Total**: ~40 minutes | **Status**: ✅ COMPLETE

**Completed:**
- LICENSE: MIT license created with copyright "Mr K" (2026)
- Broken link: Created `local-cicd-guide.md` in guides/
- Tier conflict: Unified to 5-tier (0-4) across all 4 architecture files

**SpecKit Artifacts:** [specs/001-foundation-fixes/](../../specs/001-foundation-fixes/)

---

## Wave 1: Foundation (COMPLETE)

> **Priority**: ✅ COMPLETED - 2026-01-18

| # | Task | Effort | Enables | Status |
|---|------|--------|---------|--------|
| 4 | Create /scripts/README.md | 1 hr | Script navigation for AI/humans | ✅ Done |
| 5 | Consolidate MCP documentation | 2 hr | TUI MCP feature clarity | ✅ Done |
| 6 | Create /scripts/007-update/README.md | 30 min | Update script discovery | ✅ Done |
| 7 | Create /scripts/007-diagnostics/README.md | 30 min | Boot diagnostics docs | ✅ Done |
| 8 | Update ai-cli-tools.md (fix "not created" text) | 15 min | Accurate documentation | ✅ Done |

**Total**: ~4.5 hours | **Status**: ✅ COMPLETE

**Completed:**
- scripts/README.md: Master index for 114 scripts across 11 directories
- MCP docs: Consolidated 5 guides into single mcp-setup.md with redirect stubs
- 007-update/README.md: Documents 12 update scripts with usage and troubleshooting
- 007-diagnostics/README.md: Documents boot diagnostics workflow
- ai-cli-tools.md: Updated from "PLANNED" to "IMPLEMENTED" with correct paths
- AGENTS.md: Updated references to point to new mcp-setup.md

**SpecKit Artifacts:** [specs/002-scripts-documentation/](../../specs/002-scripts-documentation/)

---

## Wave 2: TUI Features (COMPLETE)

> **Priority**: ✅ COMPLETED - 2026-01-18

| # | Task | Effort | Dependencies | Status |
|---|------|--------|--------------|--------|
| 9 | Per-family Nerd Font selection | 2 hr | None | ✅ Done |
| 10 | TUI MCP Server Management | 4 hr | #5 (MCP docs) | ✅ Done |
| 11 | MCP prerequisites detection | 2 hr | #10 | ✅ Done |
| 12 | MCP server registry | 1 hr | #10 | ✅ Done |
| 13 | Secrets template setup wizard | 2 hr | #11, #12 | ✅ Done |

**Total**: ~11 hours | **Status**: ✅ COMPLETE

**Completed:**
- Per-family Nerd Font: Individual font selection with Install/Reinstall/Uninstall actions
- MCP Server Management: New view under Extras → MCP Servers (7 servers with status)
- MCP Prerequisites: Auto-check Node.js, uvx, gh auth before install with fix instructions
- MCP Registry: Data-driven registry in `tui/internal/registry/mcp.go`
- Secrets Wizard: Interactive setup for ~/.mcp-secrets file

**New TUI Files Created:**
- `tui/internal/registry/mcp.go` - MCP server registry (7 servers)
- `tui/internal/ui/mcpservers.go` - MCP Servers management view
- `tui/internal/ui/mcpprereq.go` - Prerequisites failure view
- `tui/internal/ui/secretswizard.go` - Secrets setup wizard

**SpecKit Artifacts:** [specs/003-tui-features/](../../specs/003-tui-features/)

---

## Wave 3: Claude Code Skills (COMPLETE)

> **Priority**: ✅ COMPLETED - 2026-01-18
> **Theme**: Custom slash commands and portable configuration

| # | Task | Effort | Priority | Status |
|---|------|--------|----------|--------|
| 14 | Create `/001-health-check` skill | 1 hr | Medium | ✅ Done |
| 15 | Create `/001-deploy-site` skill | 1 hr | Medium | ✅ Done |
| 16 | Create `/001-git-sync` skill | 1 hr | Low | ✅ Done |
| 17 | Create `/001-full-workflow` skill | 1 hr | Low | ✅ Done |
| 18 | Skills user-level consolidation | 1 hr | **High** | ✅ Done |
| 19 | Agents user-level consolidation | 2 hr | **High** | ✅ Done |
| 20 | Combined install script | 1 hr | **High** | ✅ Done |

**Completed (Skills)**:
- 4 workflow skills created: `/001-health-check`, `/001-deploy-site`, `/001-git-sync`, `/001-full-workflow`
- Skills moved from `.claude/commands/` → `.claude/skill-sources/` (source files)
- Install script copies to `~/.claude/commands/` (user-level)

**Completed (Agents)**:
- 65 agents moved from `.claude/agents/` → `.claude/agent-sources/` (source files)
- Combined install script created: `scripts/install-claude-config.sh`
- Installs to `~/.claude/agents/` at user level

**What this provides**: Portable Claude Code configuration across all computers. Clone repo, run `./scripts/install-claude-config.sh`, identical setup everywhere.

**Total**: ~7 hours | **Status**: ✅ Complete

**SpecKit Artifacts:** [specs/004-claude-skills/](../../specs/004-claude-skills/) (skills) | [specs/005-claude-agents/](../../specs/005-claude-agents/) (agents)

**Reference**: [Skills docs](https://code.claude.com/docs/en/slash-commands)

---

## Wave 6a: TUI Detail Views (COMPLETE)

> **Priority**: ✅ COMPLETED - 2026-01-18
> **Theme**: Navigation restructure for better usability

| # | Task | Effort | Priority | Status |
|---|------|--------|----------|--------|
| 24 | Create ViewToolDetail component | 2 hr | **High** | ✅ Done |
| 25 | Simplify main dashboard (3 tools in table) | 1 hr | **High** | ✅ Done |
| 27 | Convert Extras to navigation menu | 1.5 hr | **High** | ✅ Done |

**Total**: ~5.5 hours | **Status**: ✅ COMPLETE

**What this fixed**:
- Extras header was cut off (not visible)
- Main dashboard too crowded with 5 tools
- Extras showed 7 tools in cramped table

**Solution implemented**:
- Created `tui/internal/ui/tooldetail.go` - reusable ViewToolDetail component (~378 lines)
- Main table: Node.js, AI Tools, Antigravity only (3 tools)
- Extras: navigation menu → individual detail views

**New/Modified TUI Files:**
- `tui/internal/ui/tooldetail.go` - New ViewToolDetail component
- `tui/internal/ui/model.go` - Added ViewToolDetail routing and dashboard simplification
- `tui/internal/ui/extras.go` - Converted from table to menu navigation

**SpecKit Artifacts:** [specs/006-tui-detail-views/](../../specs/006-tui-detail-views/)
