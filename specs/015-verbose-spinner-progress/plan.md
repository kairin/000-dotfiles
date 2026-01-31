# Implementation Plan: Verbose Spinner Progress for All TUI Components

**Branch**: `015-verbose-spinner-progress` | **Date**: 2026-01-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-verbose-spinner-progress/spec.md`

## Summary

Enhance all TUI spinner segments to follow the Boot Diagnostics verbose progress pattern with individual item spinners, descriptions, and real-time status updates. This transforms opaque "Loading..." indicators across NerdFonts, MCPServers, Extras, and Installer components into transparent per-item progress displays.

## Technical Context

**Language/Version**: Go 1.23+
**Primary Dependencies**: Bubbletea (TUI framework), Bubbles (spinner), Lipgloss (styling)
**Storage**: N/A (UI-only changes)
**Testing**: Manual visual testing via `cd tui && go build ./cmd/installer && ./dotfiles-installer`
**Target Platform**: Linux terminal (Ubuntu 25.04+)
**Project Type**: Single project (existing TUI codebase)
**Performance Goals**: Status updates within 100ms of item completion (perceived as instant)
**Constraints**: 80x24 terminal minimum, ESC cancellation within 500ms
**Scale/Scope**: 4 UI components, ~270-360 lines of changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Script Consolidation | ✅ PASS | No new scripts - modifying existing Go files only |
| II. Branch Preservation | ✅ PASS | Branch `015-verbose-spinner-progress` created, will preserve |
| III. Local-First CI/CD | ✅ PASS | Will run `go build` locally before any commits |
| IV. Modularity Limits | ✅ PASS | No file exceeds 300 lines with changes (~60-100 lines per file) |
| V. Symlink Single Source | ✅ PASS | Not touching AGENTS.md/CLAUDE.md/GEMINI.md |

**Gate Status**: ✅ PASSED - No constitutional violations

## Project Structure

### Documentation (this feature)

```text
specs/015-verbose-spinner-progress/
├── plan.md              # This file
├── research.md          # Reference implementation analysis (complete)
├── quickstart.md        # Quick validation workflow
└── tasks.md             # Implementation tasks (exists)
```

### Source Code (files to modify)

```text
tui/internal/ui/
├── nerdfonts.go         # Add per-font spinners and progress rendering
├── mcpservers.go        # Add per-server spinners and progress rendering
├── extras.go            # Add per-tool menu status indicators
├── installer.go         # Enhance stage progress with descriptions
├── styles.go            # May need additional styles for consistency
└── diagnostics.go       # Reference implementation (read-only)
```

**Structure Decision**: Existing TUI structure maintained. All changes within `tui/internal/ui/` package. No new files created.

## Design Decisions

### 1. Status Enum Pattern

Each component gets a local status enum matching the diagnostics pattern:

```go
type ItemStatus int

const (
    StatusPending ItemStatus = iota
    StatusLoading
    StatusComplete
    StatusFailed
)
```

**Rationale**: Matches existing `DetectorStatus` pattern in diagnostics.go. Simple, clear, type-safe.

### 2. Per-Item Spinner Array

Each component maintains a spinner array parallel to its items:

```go
type NerdFontsModel struct {
    fontStatuses  []ItemStatus
    fontSpinners  []spinner.Model
    completedCount int
    // ... existing fields
}
```

**Rationale**: Allows independent animation per item. Matches diagnostics.go pattern exactly.

### 3. Fixed-Width Name Column

All components use 20-character fixed-width for item names:

```go
nameStyle := lipgloss.NewStyle().Width(20)
```

**Rationale**: Ensures alignment across all items. Matches diagnostics.go. Fits in 80-column terminal with room for status icon (2) + name (20) + description (~55).

### 4. Progress Summary Format

All components use the same summary format:

```
Progress: X/Y complete
```

With optional issues count for applicable views:

```
Progress: X/Y complete | Found Z issues so far
```

**Rationale**: Consistent with Boot Diagnostics. Clear, informative, not cluttered.

### 5. Extras Menu Inline Status

Extras uses inline status indicators in menu items rather than a separate table:

```
> ✓ Glow
  ⠋ Fastfetch
  ○ VHS
  ─────────────
    Install All
```

**Rationale**: Preserves menu-only design while adding per-tool visibility.

## Complexity Tracking

> No constitutional violations requiring justification.

| Aspect | Complexity | Justification |
|--------|------------|---------------|
| Per-item spinners | Medium | Proven pattern from diagnostics.go |
| Extras menu status | Medium | Reuses existing status check infrastructure |
| Installer stages | Low | Adds descriptions to existing stage rendering |

## Implementation Phases

### Phase 1: Setup (T001-T002)
- Verify build environment
- Study diagnostics.go reference implementation (lines 380-446)

### Phase 2: NerdFonts Component (T003-T010)
- Add font descriptions constant
- Add ItemStatus enum
- Add per-font status/spinner tracking
- Implement renderVerboseProgress()
- Update View() to show verbose progress during loading

### Phase 3: MCPServers Component (T011-T017)
- Similar pattern to NerdFonts
- Server descriptions already in registry

### Phase 4: Extras Component (T018-T025)
- Add ToolMenuStatus enum
- Add per-tool spinner/status fields
- Modify renderExtrasMenu() for inline status
- Add separator between tools and actions
- Update header for loading progress

### Phase 5: Installer Component (T026-T032)
- Add stage descriptions constant
- Add per-stage spinners
- Modify renderProgressBar() for verbose display
- Preserve output log visibility

### Phase 6: Polish (T039-T048)
- Consistency verification
- ESC cancellation testing
- Terminal resize testing
- Full visual validation

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Spinner performance with many items | Bubbletea handles spinner updates efficiently; diagnostics.go works fine with 5 items |
| Terminal width issues | Fixed-width columns designed for 80-col minimum |
| Status check timing | Already async in all components; verbose display is rendering-only change |

## Validation Checklist

- [ ] `cd tui && go build ./cmd/installer` succeeds
- [ ] NerdFonts shows per-font progress with spinners
- [ ] MCPServers shows per-server progress with spinners
- [ ] Extras menu shows per-tool status indicators
- [ ] Installer shows per-stage progress with descriptions
- [ ] ESC cancellation works in all views
- [ ] 80x24 terminal displays correctly (no horizontal scrolling)
- [ ] Spinner animation is smooth (no flickering)

## Next Step

Run `/speckit.tasks` to generate the detailed task list.
