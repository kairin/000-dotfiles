# Feature Specification: Fix TUI Bugs

**Feature Branch**: `002-fix-tui-bugs`
**Created**: 2026-01-29
**Status**: Completed
**Completed**: 2026-02-08
**Input**: User description: "Fix 5 TUI bugs: multi-line location display (#201), ESC navigation after install (#200), dashboard auto-refresh after Update All (#199), terminal copy/paste restoration (#197), and stray '8' character rendering (#196)"

**Verification Notes**:
- Manual verification completed and recorded in `tasks.md` (all tasks checked).
- Upstream GitHub issues (#196, #197, #199, #200, #201) are CLOSED (2026-01-31) and were re-verified during 2026-02-08 follow-up.

## Background

The TUI installer application has 5 reported bugs affecting user experience and functionality. These bugs were identified during verification testing of the TUI Dashboard Consistency feature and impact navigation, display, and terminal state management.

### Bug Summary

| Issue | Title | Impact | Category |
|-------|-------|--------|----------|
| #201 | Claude Config detail view only shows Skills location, not Agents | Medium | Display |
| #200 | ESC after install/uninstall doesn't return to ViewToolDetail | Medium | Navigation |
| #199 | Dashboard doesn't auto-refresh after "Update All" completes | High | Refresh |
| #197 | Copy/paste stops working in terminal after running TUI | High | Terminal State |
| #196 | Stray "8" character appearing in TUI screens | Low | Rendering |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Terminal State Restoration (Priority: P1)

As a user running the TUI installer, I want copy/paste functionality to work normally in my terminal after exiting the TUI, so that I can continue my work without restarting the terminal.

**Why this priority**: This is the most disruptive bug - users must close and reopen their terminal after every TUI session, breaking their workflow and potentially losing unsaved terminal history.

**Independent Test**: Run the TUI, perform any operation, exit, and verify that Ctrl+V paste works correctly in the terminal.

**Acceptance Scenarios**:

1. **Given** a fresh terminal session with working copy/paste, **When** the user runs the TUI and exits normally with 'q', **Then** copy/paste continues to work in the terminal
2. **Given** the TUI is running and displaying any view, **When** the user presses Ctrl+C to force quit, **Then** copy/paste still works in the terminal
3. **Given** the TUI is running an installation, **When** the installation completes and user exits, **Then** copy/paste works normally
4. **Given** the TUI uses sudo authentication via subprocess, **When** the sudo prompt is displayed and user completes authentication, **Then** terminal state is properly restored

---

### User Story 2 - Dashboard Auto-Refresh After Batch Update (Priority: P1)

As a user who just completed an "Update All" operation, I want the dashboard to automatically show the updated tool statuses, so that I can verify the updates were successful without manually refreshing.

**Why this priority**: Users currently see stale data ("1 update available") after updates complete, causing confusion about whether updates succeeded.

**Independent Test**: Run "Update All" from dashboard, wait for completion, and verify dashboard shows current status without pressing 'r' to refresh.

**Acceptance Scenarios**:

1. **Given** the dashboard shows "1 update available" for a tool, **When** user selects "Update All" and the update completes successfully, **Then** the dashboard automatically shows updated tool status with no pending updates
2. **Given** a batch update is in progress, **When** all updates complete, **Then** a loading indicator appears briefly while statuses refresh
3. **Given** the dashboard is returned to after batch update, **When** the refresh completes, **Then** the "Update All" menu option shows "(0)" or is hidden

---

### User Story 3 - ESC Navigation After Install/Uninstall (Priority: P2)

As a user who just installed or uninstalled a tool from its detail view, I want pressing ESC to return me to that tool's detail view showing updated status, so I can verify the action completed successfully.

**Why this priority**: Currently, ESC returns users to the wrong view (Extras menu instead of Tool Detail), breaking the expected navigation flow and requiring extra navigation steps.

**Independent Test**: Navigate to a tool's detail view, perform install/uninstall, and verify ESC returns to the same tool's detail view.

**Acceptance Scenarios**:

1. **Given** user is viewing a tool's detail from Extras menu, **When** user selects "Install" and the installation completes, **Then** pressing ESC returns to that tool's detail view
2. **Given** user is viewing a tool's detail from Dashboard, **When** user selects "Uninstall" and it completes, **Then** pressing ESC returns to that tool's detail view with updated status
3. **Given** user presses ESC on the tool detail view after returning from install, **When** ESC is pressed again, **Then** user returns to the original menu (Extras or Dashboard)

---

### User Story 4 - Multi-Line Location Display (Priority: P2)

As a user viewing Claude Config's detail view, I want to see both the Skills location and Agents location, so I can verify both paths are correctly configured.

**Why this priority**: Users only see partial information about Claude Config's file locations, which affects their ability to troubleshoot configuration issues.

**Independent Test**: Navigate to Claude Config detail view and verify both "Skills: /path" and "Agents: /path" locations are displayed.

**Acceptance Scenarios**:

1. **Given** Claude Config is installed with both Skills and Agents directories, **When** user views Claude Config detail, **Then** both location paths are displayed on separate lines
2. **Given** a tool status includes multi-line location data (using ^ delimiter), **When** the tool detail view renders, **Then** all location lines are visible
3. **Given** the location data has only one path, **When** the tool detail view renders, **Then** the single path displays normally without extra blank lines

---

### User Story 5 - Stray Character Elimination (Priority: P3)

As a user navigating the TUI, I want all screens to render cleanly without stray characters, so that the interface appears professional and trustworthy.

**Why this priority**: While cosmetically annoying, this doesn't prevent functionality. It affects user perception but not task completion.

**Independent Test**: Navigate through all TUI screens and verify no stray "8" or other unexpected characters appear.

**Acceptance Scenarios**:

1. **Given** user is on the Dashboard with tools showing various statuses, **When** user views the screen, **Then** no stray characters appear outside expected content
2. **Given** user navigates to BatchPreview screen, **When** the tool list renders, **Then** no unexpected characters appear before or within list items
3. **Given** the terminal window is resized during TUI operation, **When** the TUI re-renders, **Then** no rendering artifacts remain on screen

---

### Edge Cases

- What happens when the TUI crashes unexpectedly?
  - Terminal state should be recoverable via `reset` command or new terminal
- What happens if user presses Ctrl+C during installation?
  - Terminal cleanup should still execute via signal handler
- What happens when batch update has nothing to update?
  - Dashboard should show current status without refresh delay
- What happens if the ^ delimiter appears in a path name?
  - Should be handled as literal character, not split
- What happens if tool detail has more than 2 location lines?
  - All lines should display, with reasonable vertical limits

## Requirements *(mandatory)*

### Functional Requirements

**Bug #197 - Terminal State**
- **FR-001**: System MUST restore terminal to cooked mode (line editing, copy/paste) upon normal exit
- **FR-002**: System MUST restore terminal state when handling SIGINT (Ctrl+C) and SIGTERM signals
- **FR-003**: System MUST restore terminal state after subprocess execution (sudo prompts)
- **FR-004**: System MUST use deferred cleanup functions to ensure terminal restoration even on panic

**Bug #199 - Dashboard Refresh**
- **FR-005**: System MUST trigger status refresh when returning to Dashboard from batch update completion
- **FR-006**: System MUST display loading indicator while statuses refresh after batch operations
- **FR-007**: System MUST invalidate cached statuses for tools that were just updated

**Bug #200 - ESC Navigation**
- **FR-008**: System MUST preserve the source view (tool detail) when launching installer from tool detail
- **FR-009**: System MUST return to tool detail view (not parent menu) when ESC is pressed after installation
- **FR-010**: System MUST refresh tool status in detail view after install/uninstall completes

**Bug #201 - Multi-Line Location**
- **FR-011**: System MUST display all location lines from tool status (not just the first)
- **FR-012**: System MUST render multi-line locations with proper line breaks in tool detail view
- **FR-013**: System MUST maintain visual alignment for multi-line location display

**Bug #196 - Stray Characters**
- **FR-014**: System MUST not render unexpected characters outside of defined UI components
- **FR-015**: System MUST properly clear screen areas before re-rendering content
- **FR-016**: System MUST handle terminal escape sequences without character leakage

### Key Entities

- **View State**: Represents the current and previous screen/view in the navigation stack
- **Tool Status**: Contains installation state, location(s), version information for a tool
- **Terminal Mode**: Represents terminal input mode settings (raw vs cooked, echo on/off)
- **Batch Operation State**: Tracks queue of tools, current index, and completion status

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Copy/paste works correctly after TUI exit in 100% of normal exit scenarios
- **SC-002**: Dashboard shows updated status within 2 seconds of batch update completion
- **SC-003**: ESC navigation returns to correct view in 100% of install/uninstall scenarios
- **SC-004**: All multi-line location data is visible in tool detail view
- **SC-005**: Zero stray characters appear during normal TUI operation
- **SC-006**: All 5 GitHub issues (#196, #197, #199, #200, #201) can be closed as resolved

## Assumptions

- The TUI uses Bubbletea framework with AltScreen mode
- Terminal cleanup is primarily handled by Bubbletea's built-in exit logic
- The location ^ delimiter is an internal convention, not user-facing
- Signal handling can be added without breaking existing message flow
- The stray "8" character is a rendering artifact, not intentional content

## Out of Scope

- Adding new TUI features beyond bug fixes
- Refactoring TUI architecture
- Performance optimization
- Adding automated tests (verification via manual testing)
- Fixing pre-existing module path issues
