# Research: Fix Fish Shell TUI Display + Issue Cleanup

**Date**: 2026-01-31
**Feature**: 003-fix-fish-tui-display

## Summary

Expanded scope to include verification and closure of stale GitHub issues from previous TUI bug fix feature.

## Findings

### Root Cause Analysis

**Decision**: Bug is in `getTableTools()` function which hardcodes tool IDs
**Rationale**: Fish was added to registry but not to the UI filter function
**Alternatives considered**: None - this is the only correct fix

### Code Location

**Decision**: Modify `tui/internal/ui/model.go` lines 1546-1550
**Rationale**: This is where `getTableTools()` filters which tools appear in the table
**Alternatives considered**:
- Could modify registry to add a "showInTable" flag, but this adds unnecessary complexity for a simple fix

### Implementation Approach

**Decision**: Add `|| tool.ID == "fish"` to the existing filter condition
**Rationale**: Follows existing pattern, minimal change, no new abstractions
**Alternatives considered**:
- Refactor to use registry metadata for filtering - rejected as over-engineering for this fix
- Loop through all CategoryMain tools without hardcoding - would require understanding why some tools (Feh) are menu-only

## Unknowns Resolved

None - all technical context was clear from the spec and code investigation.

## Issue Cleanup Research

### Commit Analysis

Commit `95400cf` (merged via `20260129-072011-fix-tui-batch-update-issues`) addressed:

1. **Redundant sudo authentication** - Added `SkipSudoCache` flag
2. **Check script interruption** - Added `needsRefreshOnDashboardReturn` flag
3. **Confirmation screens** - Added `ConfirmInstall`, `ConfirmUpdate`, `ConfirmReinstall`

### Issue Mapping

| Issue | Bug Description | Likely Fixed By |
|-------|-----------------|-----------------|
| #196 | Stray "8" character | Terminal state handling |
| #197 | Copy/paste broken | Terminal restoration on exit |
| #199 | No auto-refresh | `needsRefreshOnDashboardReturn` flag |
| #200 | ESC navigation | Status refresh deferral |
| #201 | Claude Config | Needs verification |

### Orphaned Task Issues

Issues #218-257 were created by `/speckit.taskstoissues` for the 002-fix-tui-bugs feature. Since the main bugs are now fixed, these task issues should be closed.

**Decision**: Close all 45 issues after manual verification
**Rationale**: Commit history shows fixes were implemented; need verification before closing
**Alternative considered**: Leave open until formal QA - rejected as issues are orphaned and blocking tracker cleanup
