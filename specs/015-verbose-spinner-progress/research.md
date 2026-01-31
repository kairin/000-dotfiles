# Research: Verbose Spinner Progress Pattern

**Feature**: 015-verbose-spinner-progress
**Date**: 2026-01-31

---

## Decision Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Reference Pattern | Boot Diagnostics (`diagnostics.go`) | Already implemented, proven pattern in codebase |
| Spinner Type | `spinner.Dot` | Consistent with existing components |
| Status Icons | ○ pending, ⠋ loading, ✓ complete, ✗ failed | Match diagnostics.go pattern |
| Description Width | 20 chars name, remaining for description | Fits 80-col terminal |
| Progress Summary | "Progress: X/Y complete" | Simple, clear, matches diagnostics |

---

## Reference Implementation Analysis

### Boot Diagnostics Pattern (`diagnostics.go:380-446`)

The Boot Diagnostics view provides the reference implementation:

```
⠋ Scanning for boot issues...

  ○ Failed Services      Identifies systemd services that failed to start
  ⠋ Orphaned Services    Finds services referencing executables
  ✓ Network Wait Issues  Detects NetworkManager timeout problems
  ○ Unsupported Snaps    Identifies incompatible snaps
  ○ Cosmetic Warnings    Known harmless warnings

Progress: 2/5 complete | Found 1 issue so far

[ESC] Cancel
```

**Key Implementation Details**:

1. **State Tracking**: Uses `DetectorStatus` enum with 5 states
2. **Individual Spinners**: Array of `spinner.Model` (one per detector)
3. **Progress Channel**: Async updates via `progressChan chan DetectorProgress`
4. **Name Alignment**: Fixed-width style for names (`lipgloss.NewStyle().Width(20)`)
5. **Status Icons**: Switch statement mapping status to icon

### Code Pattern (diagnostics.go:399-431)

```go
for i, info := range m.detectorInfos {
    b.WriteString("  ")

    // Status icon/spinner
    switch info.Status {
    case diagnostics.DetectorPending:
        b.WriteString(StatusUnknownStyle.Render("○ "))
    case diagnostics.DetectorRunning:
        b.WriteString(m.detectorSpinners[i].View())
        b.WriteString(" ")
    case diagnostics.DetectorComplete:
        b.WriteString(StatusInstalledStyle.Render(IconCheckmark + " "))
    case diagnostics.DetectorFailed, diagnostics.DetectorTimedOut:
        b.WriteString(StatusMissingStyle.Render(IconCross + " "))
    }

    // Name (fixed width)
    nameStyle := lipgloss.NewStyle().Width(20)
    b.WriteString(nameStyle.Render(info.DisplayName))

    // Description
    b.WriteString(DetailStyle.Render(info.Description))
    b.WriteString("\n")
}
```

---

## Component Analysis

### NerdFonts (`nerdfonts.go`)

**Current Implementation**:
- FontFamily struct with ID, DisplayName, Status, Version
- Single `loading bool` flag for entire view
- Table renders "Loading..." in status column during load

**Current Flow**:
1. Init() → spinner.Tick + refreshNerdFontsStatus()
2. refreshNerdFontsStatus() → checks cache or runs check script
3. nerdfontsStatusLoadedMsg → parseFontStatuses() → loading = false

**Required Changes**:
1. Add font descriptions (const or embedded in FontFamily)
2. Add per-font ItemStatus tracking
3. Add per-font spinner array
4. Implement verbose progress render during loading
5. Show progress summary

**Alternatives Considered**:
- Single spinner with rotating font name: Rejected (less informative)
- Parallel font checks: Already implemented (batch check script)

### MCPServers (`mcpservers.go`)

**Current Implementation**:
- Server list from `registry.GetAllMCPServers()`
- Single `loading bool` flag
- Table renders "Loading" in status column during load

**Current Flow**:
1. Init() → spinner.Tick + refreshMCPStatuses()
2. refreshMCPStatuses() → runs `claude mcp list`
3. mcpAllLoadedMsg → statuses map updated → loading = false

**Required Changes**:
1. Server descriptions already in registry (Server.Description)
2. Add per-server ItemStatus tracking
3. Add per-server spinner array
4. Implement verbose progress render during loading
5. Show progress summary

**Note**: Since `claude mcp list` is a single command, per-server progress is simulated - all servers transition from Loading to Complete together.

### Extras (`extras.go`)

**Current Implementation**:
- Menu-only view (no table currently shown)
- Tools navigate to ToolDetail for individual loading
- refreshExtrasStatuses() runs parallel checks in background
- Already has `loading bool`, `state *sharedState`, per-tool spinners

**Current Flow**:
1. Init() → spinner.Tick + refreshExtrasStatuses()
2. refreshExtrasStatuses() → batch commands for each tool
3. extrasStatusLoadedMsg → updates sharedState.statuses
4. extrasAllLoadedMsg → loading = false

**Updated Analysis (User Story 4)**:
- Extras menu runs background status checks but doesn't show per-tool progress
- Users can't see which tools are installed without navigating to each
- **Decision**: Add per-tool status indicators inline with menu items

**Required Changes**:
1. Add ToolMenuStatus enum (Pending, Loading, Complete, Failed)
2. Add per-tool status tracking array
3. Add per-tool spinner array for loading state
4. Modify renderExtrasMenu() to prefix each tool with status icon
5. Add visual separator between tools and action items
6. Modify header to show progress during loading

**Visual Pattern**:
```
Extras Tools • ⠋ Loading... (3/9 complete)

Choose:
> ✓ Glow                  (installed)
  ✓ Gum                   (installed)
  ⠋ Fastfetch             (loading)
  ○ VHS                   (pending)
  ─────────────
    Install All
    Install Claude Config
    ...
```

**Alternatives Considered**:
- Full table with verbose loading: Rejected (menu-only design is intentional)
- No changes: Rejected (per-tool status adds significant value)
- **Result**: Inline status indicators in existing menu format

### Installer (`installer.go`)

**Current Implementation**:
- stageStatus struct with complete, success, duration
- renderStageInfo() shows "Stage X/Y: StageName (elapsed: Xs)"
- renderProgressBar() shows animated bar + stage list with icons

**Current Flow**:
1. startPipeline() → sets stages array
2. StageProgressMsg → updateStageProgress()
3. renderProgressBar() shows compact stage list

**Required Changes**:
1. Add stage descriptions constant array
2. Modify renderProgressBar() to show verbose stage list
3. Each stage: icon + name + description
4. Keep output log visible (TailSpinner)

---

## Font Descriptions

| Font | Short Description |
|------|-------------------|
| JetBrainsMono | IDE-optimized with ligatures |
| FiraCode | Programming ligatures pioneer |
| Hack | Clear, readable, no ligatures |
| Meslo | macOS derivative, powerline ready |
| CascadiaCode | Microsoft's coding font |
| SourceCodePro | Adobe's monospace, legible |
| IBMPlexMono | Modern IBM, distinctive |
| Iosevka | Narrow, space-efficient |

## Stage Descriptions

| Stage | Description |
|-------|-------------|
| Check | Verifying prerequisites |
| InstallDeps | Installing dependencies |
| VerifyDeps | Confirming dependencies |
| Install | Installing tool |
| Confirm | Verifying installation |
| Uninstall | Removing tool |
| Configure | Applying settings |
| Update | Updating to latest |

---

## Implementation Approach

### Minimal Change Strategy

1. **Reuse existing styles** from diagnostics.go pattern
2. **Reuse existing icons** from styles.go constants
3. **No new packages** - only use existing bubbles/lipgloss
4. **No new messages** - extend existing message handling
5. **Preserve existing behavior** - enhance, don't replace

### Per-Component Effort

| Component | Lines Added | Complexity |
|-----------|-------------|------------|
| nerdfonts.go | ~80-100 | Medium |
| mcpservers.go | ~80-100 | Medium |
| extras.go | ~60-80 | Medium (menu inline status) |
| installer.go | ~50-70 | Low-Medium |
| styles.go | ~0-10 | Low |
| **Total** | ~270-360 | Medium |

---

## Alternatives Rejected

1. **Shared progress component**: Too much abstraction for 3-4 uses
2. **New progress package**: Overkill, diagnostics pattern sufficient
3. **Animated progress bars per item**: Too busy, spinner is cleaner
4. **Color-coded descriptions**: Adds visual noise, keep simple
