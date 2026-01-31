# Feature Specification: Fix Fish Shell TUI Display + Issue Cleanup

**Feature Branch**: `003-fix-fish-tui-display`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Fish shell not appearing in TUI despite being added to registry - getTableTools() hardcodes only nodejs, ai_tools, antigravity" + verify and close stale GitHub issues

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Fish Shell in Main Tools Table (Priority: P1)

A user opens the TUI installer to manage their development tools. They expect to see Fish shell listed in the main tools table alongside Node.js, Local AI Tools, and Google Antigravity so they can view its installation status, version, and manage it.

**Why this priority**: This is the core bug - Fish was added to the registry but doesn't appear in the UI, making it invisible and unmanageable through the TUI.

**Independent Test**: Can be fully tested by launching the TUI (`cd tui && go run ./cmd/installer`) and visually confirming Fish appears in the main tools table.

**Acceptance Scenarios**:

1. **Given** Fish shell is defined in the registry with `Category: CategoryMain`, **When** the user launches the TUI, **Then** Fish shell appears in the main tools status table with correct display name "Fish + Fisher"
2. **Given** Fish shell is installed on the system, **When** the user views the TUI, **Then** Fish shows "INSTALLED" status with version information
3. **Given** Fish shell is not installed, **When** the user views the TUI, **Then** Fish shows "Not Installed" status

---

### User Story 2 - Access Fish Shell Detail View (Priority: P2)

A user wants to install, update, or get more information about Fish shell. They need a way to access the Fish detail view from the main menu to perform these actions.

**Why this priority**: Once Fish is visible in the table, users need a way to interact with it for installation/management.

**Independent Test**: Can be tested by navigating to Fish in the menu and pressing enter to access the detail view.

**Acceptance Scenarios**:

1. **Given** Fish is listed in the TUI, **When** the user selects Fish, **Then** the Fish detail view opens showing installation options
2. **Given** the user is on the main screen, **When** they view the status table, **Then** Fish appears as a row in the table (not as a separate menu item)

---

### Edge Cases

- What happens when Fish check script fails? System should show "Unknown" status with graceful error handling (existing pattern from other tools)
- How does the UI handle Fish having a Configure script in addition to Install? The existing tool detail view already supports Configure scripts

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display Fish shell in the main tools status table (via `getTableTools()`) alongside Node.js, AI Tools, and Antigravity
- **FR-002**: System MUST show Fish shell's installation status (INSTALLED/Not Installed/Unknown)
- **FR-003**: System MUST display Fish shell's version when installed
- **FR-004**: System MUST provide access to Fish detail view for install/update/uninstall actions
- **FR-005**: System MUST run Fish status checks in parallel with other tools during refresh

### Key Entities

- **Tool Registry**: Contains Fish definition with ID "fish", DisplayName "Fish + Fisher", Category "CategoryMain"
- **UI Filter Functions**: `getTableTools()` and `getMenuTools()` control which tools appear where in the UI

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Fish shell appears in the main tools table when TUI is launched
- **SC-002**: Fish status is correctly detected and displayed (matching output of check_fish.sh)
- **SC-003**: Users can access Fish detail view and perform install/update/uninstall operations
- **SC-004**: All existing tools continue to display correctly (no regression)

## Clarifications

### Session 2026-01-31

- Q: Should Fish appear in the status table (like Node.js) or as a menu item only (like Feh)? → A: Fish appears in status table alongside Node.js, AI Tools, and Antigravity

---

### User Story 3 - Verify and Close Stale GitHub Issues (Priority: P3)

A maintainer wants to clean up the GitHub issue tracker by verifying that previously fixed bugs are actually resolved and closing the corresponding issues.

**Why this priority**: After implementing the Fish fix, verify that previous TUI bug fixes (from commit 95400cf) are working and close the stale issues.

**Independent Test**: Run TUI and verify each bug is fixed, then close the corresponding GitHub issues.

**Acceptance Scenarios**:

1. **Given** bug #196 (stray "8" character) was reportedly fixed, **When** the TUI is run and screens navigated, **Then** no stray characters appear AND issue #196 is closed
2. **Given** bug #197 (copy/paste stops working) was reportedly fixed, **When** the TUI is exited, **Then** copy/paste works in terminal AND issue #197 is closed
3. **Given** bug #199 (dashboard no auto-refresh) was reportedly fixed, **When** Update All completes, **Then** dashboard refreshes AND issue #199 is closed
4. **Given** bug #200 (ESC navigation broken) was reportedly fixed, **When** ESC is pressed after install, **Then** user returns to correct view AND issue #200 is closed
5. **Given** bug #201 (Claude Config location) was reportedly fixed, **When** Claude Config detail is viewed, **Then** both locations are shown AND issue #201 is closed
6. **Given** task issues #218-257 are orphaned, **When** original bugs are verified fixed, **Then** all 40 task issues are closed

---

## Requirements *(mandatory - updated)*

### Functional Requirements

- **FR-001**: System MUST display Fish shell in the main tools status table (via `getTableTools()`) alongside Node.js, AI Tools, and Antigravity
- **FR-002**: System MUST show Fish shell's installation status (INSTALLED/Not Installed/Unknown)
- **FR-003**: System MUST display Fish shell's version when installed
- **FR-004**: System MUST provide access to Fish detail view for install/update/uninstall actions
- **FR-005**: System MUST run Fish status checks in parallel with other tools during refresh
- **FR-006**: Maintainer MUST verify bugs #196, #197, #199, #200, #201 are fixed before closing
- **FR-007**: Maintainer MUST close orphaned task issues #218-257 after verification

### GitHub Issues to Close (After Verification)

| Issue | Description | Verification |
|-------|-------------|--------------|
| #196 | Stray "8" character | Navigate TUI screens, no stray chars |
| #197 | Copy/paste broken after exit | Exit TUI, test copy/paste |
| #199 | Dashboard no auto-refresh | Run Update All, check refresh |
| #200 | ESC navigation broken | Press ESC after install |
| #201 | Claude Config shows one location | View Claude Config detail |
| #218-257 | Task issues from 002-fix-tui-bugs | Close after above verified |

## Assumptions

- Fish shell scripts (check, install, uninstall, etc.) already exist and function correctly (they were added in commit e63c629)
- The existing tool detail view component can handle Fish without modification
- Fish appears in the status table (confirmed via clarification) since it has full version detection and update capability like other main tools
- Commit 95400cf fixed bugs #197, #199, #200 (terminal state, dashboard refresh, ESC navigation)
- Bugs #196 and #201 need manual verification before closing
