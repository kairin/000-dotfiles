# Implementation Plan: Fix Fish Shell TUI Display + Issue Cleanup

**Branch**: `003-fix-fish-tui-display` | **Date**: 2026-01-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/013-fix-fish-tui-display/spec.md`

## Summary

1. Fix bug where Fish shell doesn't appear in TUI (2-line code change)
2. Verify previous TUI bug fixes are working (5 bugs from commit 95400cf)
3. Close 45 stale GitHub issues (#196, #197, #199, #200, #201, #218-257)

## Technical Context

**Language/Version**: Go 1.23+ (existing TUI codebase)
**Primary Dependencies**: Bubbletea, Lipgloss (existing)
**Storage**: N/A (UI-only change + GitHub issue management)
**Testing**: `go run ./cmd/installer` manual verification
**Target Platform**: Linux (Ubuntu 25.04+)
**Project Type**: Single project (Go TUI application)
**Scale/Scope**: 1 file code change, 45 issues to close

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Script Consolidation | PASS | No new scripts - modifying existing Go code |
| II. Branch Preservation | PASS | Using feature branch `003-fix-fish-tui-display` |
| III. Local-First CI/CD | PASS | Will test locally with `go run ./cmd/installer` |
| IV. Modularity Limits | PASS | No new files, minor edit to existing code |
| V. Symlink Single Source | N/A | Not touching AGENTS.md/CLAUDE.md/GEMINI.md |

**Gate Result**: PASS

## Project Structure

### Documentation (this feature)

```text
specs/013-fix-fish-tui-display/
├── spec.md              # Feature specification (updated)
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # Spec validation checklist
└── tasks.md             # Phase 2 output (needs regeneration)
```

### Source Code

```text
tui/internal/ui/model.go     # FIX: getTableTools() line ~1550
```

## Implementation Details

### Part 1: Fish Shell Fix

**File**: `tui/internal/ui/model.go`

**Change 1** (line ~1546):
```go
tableTools := make([]*registry.Tool, 0, 4)  // was 3
```

**Change 2** (line ~1550):
```go
if tool.ID == "nodejs" || tool.ID == "ai_tools" || tool.ID == "antigravity" || tool.ID == "fish" {
```

### Part 2: Bug Verification Checklist

| Bug | Test | Expected Result |
|-----|------|-----------------|
| #196 | Navigate all TUI screens | No stray "8" character |
| #197 | Exit TUI with q or Ctrl+C | Copy/paste works in terminal |
| #199 | Run Update All | Dashboard auto-refreshes |
| #200 | Press ESC after install | Returns to ViewToolDetail |
| #201 | View Claude Config detail | Shows both Agents and Skills locations |

### Part 3: Issues to Close

**Original Bugs (5 issues):**
- #196, #197, #199, #200, #201

**Task Issues (40 issues):**
- #218-257 (from 002-fix-tui-bugs feature)

**Total**: 45 issues to close

## Verification Steps

1. Run TUI: `cd tui && go run ./cmd/installer`
2. Verify Fish appears in main tools table
3. Test each bug from the checklist above
4. If all verified, close issues via GitHub CLI

## Risk Assessment

- **Risk Level**: Low
- **Rollback**: Single file revert if issues
- **Regression Scope**: Only affects tool table display

---

## Planning Complete

**Generated Artifacts**:
- `plan.md` - This implementation plan (updated)
- `spec.md` - Updated with issue cleanup requirements

**Next Step**: Run `/speckit.tasks` to regenerate implementation tasks with issue cleanup
