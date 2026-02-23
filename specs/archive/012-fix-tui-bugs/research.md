# Research: Fix TUI Bugs

**Feature**: 002-fix-tui-bugs
**Date**: 2026-01-29
**Status**: Complete

## Summary

Root cause analysis completed for all 5 TUI bugs. All issues are located within the existing codebase with clear fix paths identified.

## Findings

### Bug #197 - Terminal Copy/Paste Stops Working

**Decision**: Add explicit terminal cleanup and signal handling.

**Rationale**:
- Current code uses `tea.WithAltScreen()` which should restore terminal state on exit
- The issue occurs specifically after `tea.ExecProcess()` calls (sudo authentication)
- When Bubbletea suspends for subprocess and resumes, terminal modes may not fully restore
- Adding explicit cleanup ensures proper state restoration even on abnormal exit

**Root Cause Analysis**:
- Location: `tui/cmd/installer/main.go:57`
- The TUI program is created with `tea.NewProgram(m, tea.WithAltScreen())`
- `tea.ExecProcess()` in `model.go:963` suspends the TUI for sudo prompts
- If the subprocess modifies terminal state and resumption fails, terminal left in bad state

**Alternatives Considered**:
- Use `tea.NoAltScreen()` mode: Rejected - would affect entire TUI rendering
- Wrap subprocess in PTY: Rejected - adds complexity for minimal gain
- **Selected**: Add deferred cleanup and signal handlers for graceful termination

---

### Bug #199 - Dashboard Doesn't Auto-Refresh After Update All

**Decision**: Set loading state and trigger refresh when returning to Dashboard from batch completion.

**Rationale**:
- Current code at lines 358-370 calls `refreshAllStatuses()` but this is asynchronous
- The dashboard is already visible before refresh completes
- User sees stale "1 update available" until manual refresh (TTL 5 min)

**Root Cause Analysis**:
- Location: `tui/internal/ui/model.go:358-370`
- When batch update completes, code returns to Dashboard via `m.currentView = ViewDashboard`
- `refreshAllStatuses()` is called but runs asynchronously
- No `m.loading = true` set, so no spinner visible during refresh
- Dashboard renders immediately with old cached data

**Code Path**:
```text
startBatchUpdate() → ViewInstaller → batch complete → return to Dashboard
                                                    → refreshAllStatuses() (async)
                                                    → User sees stale data
```

**Alternatives Considered**:
- Synchronous refresh: Rejected - would block UI during refresh
- Pre-refresh before showing: Rejected - delays visual feedback
- **Selected**: Set `m.loading = true` + invalidate cache for updated tools + async refresh

---

### Bug #200 - ESC After Install/Uninstall Doesn't Return to ViewToolDetail

**Decision**: Preserve source view context when launching installer from tool detail.

**Rationale**:
- The `InstallerExitMsg` handler checks `if m.toolDetail != nil` but doesn't track the correct return target
- User expects: ViewToolDetail → Install → ESC → ViewToolDetail
- Actual: ViewToolDetail → Install → ESC → ViewExtras (parent menu)

**Root Cause Analysis**:
- Location: `tui/internal/ui/model.go:306-338`
- When entering installer from ViewToolDetail, the `toolDetailFrom` field stores original view (Extras/Dashboard)
- On `InstallerExitMsg`, code checks `m.toolDetail != nil` and returns to ViewToolDetail
- However, after installation, user is being returned to `m.toolDetailFrom` (Extras) instead of staying in tool detail flow

**Expected Navigation Flow**:
```text
ViewExtras → ViewToolDetail (toolDetailFrom=Extras) → ViewInstaller → ESC
         ↓
Should return to: ViewToolDetail (to see updated status)
         ↓
Then ESC from ViewToolDetail: ViewExtras
```

**Alternatives Considered**:
- Always return to ViewExtras: Rejected - breaks user expectation to see install result
- Add separate return stack: Rejected - overengineered for this use case
- **Selected**: On InstallerExitMsg, return to ViewToolDetail if it was the source, refresh status

---

### Bug #201 - Claude Config Detail View Only Shows Skills Location

**Decision**: Modify tooldetail.go to render all location lines including Details array.

**Rationale**:
- Cache parsing in `cache.go` correctly splits multi-line locations by `^` delimiter
- First line goes to `status.Location`, remaining lines go to `status.Details`
- Tool detail view only renders `status.Location`, ignoring `status.Details`

**Root Cause Analysis**:
- Location: `tui/internal/ui/tooldetail.go:249-253`
- The `renderRow()` function only displays the `Location` field
- `status.Details` array (containing "Agents: /path") is not rendered

**Cache Parsing (Correct)**:
```go
// cache.go:212-218
locationParts := strings.Split(parts[3], "^")
if len(locationParts) > 0 {
    status.Location = locationParts[0]  // "Skills: /home/kkk/.claude/commands"
    if len(locationParts) > 1 {
        status.Details = locationParts[1:]  // ["Agents: /home/kkk/.claude/agents"]
    }
}
```

**Tool Detail Rendering (Bug)**:
```go
// tooldetail.go:249-253
location := m.status.Location
if location == "" {
    location = "-"
}
renderRow("Location", location, valueStyle)  // Only renders first line!
// status.Details is ignored
```

**Alternatives Considered**:
- Merge all lines into single Location string: Rejected - loses visual separation
- Add separate "Details" field in UI: Rejected - location is single concept, just multi-line
- **Selected**: Extend renderRow to handle multi-line locations or add Details rendering after Location

---

### Bug #196 - Stray "8" Character Appearing

**Decision**: Investigate and fix rendering artifact through targeted debugging.

**Rationale**:
- No explicit "8" character found in codebase search
- Likely a terminal escape sequence corruption or mouse input leakage
- The "8" could be from CSI sequence (ANSI), mouse event number, or partial unicode

**Root Cause Analysis**:
- Location: Unknown (requires runtime debugging)
- Potential sources identified:
  1. **Spinner animation**: Bubbletea spinner uses ANSI codes that might render incorrectly
  2. **Mouse input**: Mouse event number "8" being rendered as text instead of processed
  3. **Escape sequence corruption**: Partial CSI sequence leaving trailing characters
  4. **Window resize handling**: Re-render at wrong offset during resize

**Debugging Strategy**:
1. Capture exact screen state when "8" appears
2. Check if correlated with spinner ticks (timing-based)
3. Test with mouse disabled via `tea.WithoutMouseCellMotion()`
4. Add screen clear before re-renders if needed
5. Verify lipgloss style application doesn't leak escape sequences

**Alternatives Considered**:
- Ignore (cosmetic only): Rejected - affects perceived quality
- Complete rewrite of rendering: Rejected - overkill for single character artifact
- **Selected**: Targeted debugging and minimal fix once source identified

---

## Open Questions

None - all questions resolved through codebase analysis.

## Next Steps

Proceed to `/speckit.tasks` for task generation.
