# Feature Specification: Verbose Spinner Progress for All TUI Components

**Feature Branch**: `015-verbose-spinner-progress`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Enhance all spinner segments for all dashboards and all installers to follow the Boot Diagnostics verbose progress pattern with individual item spinners, descriptions, and real-time status updates"

---

## Problem Statement

Currently, the TUI uses minimal "Loading...", "Installing...", or "Initializing..." displays across multiple components. Users see no feedback about what's happening during multi-item operations, leading to uncertainty about whether the tool is working.

**Components with minimal progress feedback:**

| Component | Current Display | Items |
|-----------|-----------------|-------|
| NerdFonts | "Loading" per cell | 8 fonts |
| MCPServers | "Loading" per cell | 7 servers |
| Extras | Menu with no status indicators | 9 tools + 4 menu items |
| Installer | "Installing..." + linear stages | Variable stages |
| ToolDetail | "Loading..." | 1 tool |
| SpecKitDetail | "Scanning for differences..." | 1 project |

**Reference pattern (Boot Diagnostics - already implemented):**

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

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Per-Item Progress During Multi-Item Loading (Priority: P1)

As a user loading multiple items (fonts, servers, tools), I want to see individual progress for each item so I understand what's being checked and what's complete.

**Why this priority**: Core value proposition - transforms opaque "Loading..." into transparent per-item feedback showing exactly what's happening.

**Independent Test**: Can be fully tested by navigating to NerdFonts, MCPServers, or Extras view and observing that each item shows its own status indicator (pending/loading/complete/failed) with a description.

**Acceptance Scenarios**:

1. **Given** user navigates to NerdFonts view, **When** status refresh begins, **Then** all 8 fonts are listed with individual status indicators (○ pending, ⠋ loading, ✓ installed, ✗ not installed)
2. **Given** user navigates to MCPServers view, **When** status refresh begins, **Then** all 7 servers are listed with individual status indicators showing connection state
3. **Given** user navigates to Extras view, **When** status refresh begins, **Then** all 9 tools are listed in the menu with individual status indicators (○ pending, ⠋ loading, ✓ installed, ✗ not installed) showing installation state
4. **Given** a status check completes for one item, **When** rendering updates, **Then** that item's spinner is replaced with a final status icon immediately

---

### User Story 2 - View Per-Stage Progress During Installation (Priority: P2)

As a user installing a tool, I want to see individual stage progress with descriptions so I understand what's happening at each step and where in the process I am.

**Why this priority**: Improves the most user-facing operation (installation) by showing meaningful progress instead of opaque "Installing..." with a single spinner.

**Independent Test**: Can be tested by initiating any tool installation and observing that each stage (Check, InstallDeps, VerifyDeps, Install, Confirm) shows its own status indicator with a description of what that stage does.

**Acceptance Scenarios**:

1. **Given** user starts tool installation, **When** pipeline begins, **Then** all stages are listed with pending status and one-line descriptions
2. **Given** installation is in progress, **When** a stage is actively running, **Then** that stage shows an animated spinner
3. **Given** a stage completes successfully, **When** next stage starts, **Then** completed stage shows checkmark and next stage shows spinner
4. **Given** a stage fails, **When** failure is detected, **Then** failed stage shows X icon and user sees failure context

---

### User Story 3 - View Real-Time Item Count During Batch Operations (Priority: P3)

As a user waiting for batch operations, I want to see a running count of completed items and found issues so I have immediate feedback on progress.

**Why this priority**: Provides reassurance that work is progressing and gives early indication of results.

**Independent Test**: Can be tested by triggering any multi-item operation and observing a progress summary line that updates as items complete.

**Acceptance Scenarios**:

1. **Given** multi-item loading is in progress, **When** items complete, **Then** a summary line shows "Progress: X/Y complete"
2. **Given** items have mixed status results, **When** status check completes, **Then** summary includes found issues/problems count

---

### User Story 4 - Per-Tool Status in Extras Menu (Priority: P1)

As a user viewing the Extras menu, I want to see status indicators for each tool inline with the menu items so I can quickly identify which tools are installed, loading, or need attention.

**Why this priority**: The Extras menu is a frequent navigation point. Adding per-tool status indicators provides value without requiring the user to navigate to each tool's detail view.

**Independent Test**: Navigate to Extras menu and observe that each tool menu item has a leading status indicator (○ pending, ⠋ loading, ✓ installed, ✗ not installed) while status checks run in background.

**Acceptance Scenarios**:

1. **Given** user navigates to Extras menu, **When** menu renders, **Then** each tool shows a status indicator in front of the tool name
2. **Given** Extras is loading tool statuses, **When** a tool check is in progress, **Then** that tool's menu item shows an animated spinner (⠋)
3. **Given** a tool status check completes, **When** menu re-renders, **Then** spinner is replaced with final status icon (✓ installed, ✗ not installed)
4. **Given** menu header, **When** loading is in progress, **Then** header shows progress summary "⠋ Loading... (X/9 complete)"
5. **Given** all status checks complete, **When** menu is idle, **Then** header shows "Extras Tools • 9 Additional Tools" without spinner

**Visual Example:**
```
Extras Tools • ⠋ Loading... (3/9 complete)

Choose:
> ✓ Glow                  (installed)
  ✓ Gum                   (installed)
  ⠋ Fastfetch             (loading)
  ○ VHS                   (pending)
  ○ Atuin                 (pending)
  ○ Carapace              (pending)
  ○ TV                    (pending)
  ○ Fish                  (pending)
  ○ Claude Code           (pending)
  ─────────────
    Install All
    Install Claude Config
    MCP Servers
    SpecKit Updater
    Back
```

---

### Edge Cases

- What happens when a single item check times out?
  - Show timeout indicator (⏱ or ✗) for that item, continue with remaining items
- What happens when all items fail to load?
  - Show all items with failure indicators, display overall error message
- What happens if user presses ESC during loading?
  - Cancel remaining checks gracefully, preserve completed results
- What happens with terminal resize during progress display?
  - Re-render the progress list to fit new dimensions
- What happens with very long item names or descriptions?
  - Truncate with ellipsis, maintain column alignment

---

## Requirements *(mandatory)*

### Functional Requirements

**Per-Item Progress Display:**
- **FR-001**: System MUST display all items in a list when multi-item loading begins
- **FR-002**: System MUST show an animated spinner (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏) next to each actively loading item
- **FR-003**: System MUST replace spinner with status icon (✓ success, ✗ failed, ⏱ timeout, ○ pending) on completion
- **FR-004**: System MUST display a one-line description for each item explaining its purpose
- **FR-005**: System MUST use fixed-width columns for item names to maintain alignment

**Progress Summary:**
- **FR-006**: System MUST show a running progress summary (e.g., "Progress: 4/8 complete")
- **FR-007**: System MUST update progress count within 100ms of item completion

**Installer Stage Progress:**
- **FR-008**: Installer MUST list all pipeline stages with descriptions when installation begins
- **FR-009**: Installer MUST show stage transition with spinner animation
- **FR-010**: Installer MUST continue to show output log alongside stage progress

**Error Handling:**
- **FR-011**: System MUST handle individual item timeouts gracefully (show timeout icon, continue)
- **FR-012**: System MUST allow ESC cancellation at any point during loading
- **FR-013**: System MUST continue loading remaining items if one fails

**Extras Menu Per-Tool Status:**
- **FR-014**: Extras menu MUST display a status indicator (○/⠋/✓/✗) in front of each tool menu item
- **FR-015**: Extras menu header MUST show progress summary during loading (e.g., "⠋ Loading... (X/9 complete)")
- **FR-016**: Extras menu MUST update individual tool indicators immediately when status check completes
- **FR-017**: Extras menu MUST show a visual separator between tool items and action items (Install All, Back, etc.)

**Consistency:**
- **FR-018**: All multi-item views MUST use the same visual pattern as Boot Diagnostics
- **FR-019**: Spinner animation style MUST be consistent across all views (spinner.Dot)

---

### Components to Enhance

| Component | File | Items | Description Column Content |
|-----------|------|-------|---------------------------|
| NerdFonts | nerdfonts.go | 8 fonts | Font family name + what it's optimized for |
| MCPServers | mcpservers.go | 7 servers | Server purpose description |
| Extras | extras.go | 9 tools + 4 menu items | Per-tool status in menu with compact format |
| Installer | installer.go | 5 stages | What each stage accomplishes |
| ToolDetail | tooldetail.go | 1 item | Single item - keep simple |
| SpecKitDetail | speckitdetail.go | 1 item | Single item - keep simple |

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify which specific item is currently loading within 1 second of viewing any multi-item loading screen
- **SC-002**: All item names and descriptions are visible without horizontal scrolling on standard terminal sizes (80x24)
- **SC-003**: Status updates appear within 100ms of item completion (perceived as instant)
- **SC-004**: ESC cancellation responds within 500ms
- **SC-005**: The progress pattern is visually consistent across all enhanced components (same icons, spacing, animation style)
- **SC-006**: No information is lost compared to current implementation (output logs still visible for installer)

---

## Assumptions

- The Boot Diagnostics pattern (already implemented) serves as the reference implementation
- All status checks can provide individual per-item progress (not just batch completion)
- Terminal supports Unicode characters for status icons (✓, ✗, ○)
- Spinner animation rate (spinner.Dot) is appropriate for all components
- Existing component layouts can accommodate the verbose progress display

---

## Out of Scope

- Modifying the underlying status check logic (only the UI display changes)
- Adding new status checks or items to any component
- Changing the order or structure of existing data
- Adding progress persistence (caching intermediate states)

---

## Files to Modify

| File | Change |
|------|--------|
| `tui/internal/ui/nerdfonts.go` | Add per-font spinners and progress rendering |
| `tui/internal/ui/mcpservers.go` | Add per-server spinners and progress rendering |
| `tui/internal/ui/extras.go` | Add per-tool spinners and progress rendering |
| `tui/internal/ui/installer.go` | Enhance stage progress with descriptions |
| `tui/internal/ui/styles.go` | May need additional styles for consistency |

---

## Specification Quality Checklist

**Purpose**: Validate specification completeness and quality before proceeding to planning

### Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

### Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

---

## Next Step

Run `/speckit.plan` to generate the implementation plan.
