# Feature Specification: Boot Diagnostics Verbose Progress Display

**Feature Branch**: `014-boot-diagnostics-progress`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Improve Boot Diagnostics scanning UI to show verbose per-detector progress with spinners for each diagnostic check"

## Problem Statement

Currently, when selecting Boot Diagnostics, users only see:

```
Boot Diagnostics

Initializing...

[ESC] Back
```

This provides no visibility into:
- Which diagnostic checks are running
- Progress of individual detectors
- Real-time status updates
- How many checks remain

Users have no feedback that the system is actively scanning, leading to uncertainty about whether the tool is working.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Individual Detector Progress (Priority: P1)

As a user running Boot Diagnostics, I want to see each diagnostic check listed with its own progress indicator so I know exactly what the system is scanning.

**Why this priority**: This is the core value proposition - transforming a blank "Initializing..." screen into an informative progress display that shows all 5 detector checks with real-time status.

**Independent Test**: Can be fully tested by launching the TUI, selecting Boot Diagnostics, and observing that all 5 detector names appear with spinners that update in real-time.

**Acceptance Scenarios**:

1. **Given** user selects Boot Diagnostics, **When** scanning begins, **Then** all 5 detector checks are listed with their names and descriptions
2. **Given** scanning is in progress, **When** a detector is actively running, **Then** a spinner animation appears next to that detector's name
3. **Given** scanning is in progress, **When** a detector completes, **Then** its spinner is replaced with a checkmark (success) or X (failed)

---

### User Story 2 - View Detector Descriptions (Priority: P2)

As a user, I want to see a brief description of what each detector checks so I understand what the system is looking for.

**Why this priority**: Enhances user understanding by providing context for each check, making the diagnostic process educational rather than opaque.

**Independent Test**: Can be verified by reading the descriptions next to each detector and confirming they explain the purpose (e.g., "Identifies systemd services that failed to start").

**Acceptance Scenarios**:

1. **Given** the diagnostic list is displayed, **When** user reads the list, **Then** each detector shows its name and a one-line description of what it checks
2. **Given** the detector "Failed Services" is shown, **When** user reads its description, **Then** it says "Identifies systemd services that failed to start"

---

### User Story 3 - View Real-Time Issue Count (Priority: P3)

As a user, I want to see a running count of issues found as detectors complete so I have immediate feedback on system health.

**Why this priority**: Provides instant value by showing results as they arrive rather than waiting for all detectors to finish.

**Independent Test**: Can be tested by observing the issue counter increment as each detector completes and finds issues.

**Acceptance Scenarios**:

1. **Given** scanning is in progress, **When** a detector completes and finds issues, **Then** a summary line shows the updated total (e.g., "Found 3 issues so far")
2. **Given** all detectors complete with no issues, **When** scanning finishes, **Then** a success message displays "No boot issues found"

---

### Edge Cases

- What happens when a detector script times out (30-second limit)?
  - Show timeout indicator and continue with remaining detectors
- What happens when a detector script fails to execute?
  - Show error status for that detector, continue scanning, log the error
- What happens when user presses ESC during scanning?
  - Cancel remaining detectors gracefully and return to previous view
- What happens when terminal is resized during scanning?
  - Re-render the progress list to fit new dimensions

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display all 5 detector names when scanning begins
- **FR-002**: System MUST show an animated spinner next to each actively running detector
- **FR-003**: System MUST replace the spinner with a status icon when a detector completes (checkmark for success, X for error)
- **FR-004**: System MUST display a one-line description for each detector explaining what it checks
- **FR-005**: System MUST show a running count of issues found as detectors complete
- **FR-006**: System MUST handle detector timeouts (30 seconds) gracefully with a timeout indicator
- **FR-007**: System MUST allow users to cancel scanning with ESC key
- **FR-008**: System MUST continue scanning remaining detectors if one fails

### Detector Display Information

| Detector | Display Name | Description |
|----------|--------------|-------------|
| detect_failed_services.sh | Failed Services | Identifies systemd services that failed to start |
| detect_orphaned_services.sh | Orphaned Services | Finds services referencing executables that no longer exist |
| detect_network_wait_issues.sh | Network Wait Issues | Detects NetworkManager-wait-online timeout problems |
| detect_unsupported_snaps.sh | Unsupported Snaps | Identifies snaps incompatible with your Ubuntu version |
| detect_cosmetic_warnings.sh | Cosmetic Warnings | Known harmless warnings (ALSA, GNOME keyring, etc.) |

### Visual Layout

```
                Boot Diagnostics

Scanning for boot issues...

  [spinner] Failed Services      Identifies systemd services that failed to start
  [check]   Orphaned Services    Finds services referencing missing executables
  [spinner] Network Wait Issues  Detects NetworkManager timeout problems
  [pending] Unsupported Snaps    Identifies incompatible snaps
  [pending] Cosmetic Warnings    Known harmless warnings

Progress: 2/5 complete | Found 1 issue so far

[ESC] Cancel
```

**Status Icons**:
- `[spinner]` - Animated spinner (actively running)
- `[check]` - Green checkmark (completed successfully)
- `[X]` - Red X (failed or timed out)
- `[pending]` - Gray dot or dash (not yet started)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can identify which diagnostic check is currently running within 1 second of viewing the screen
- **SC-002**: All 5 detector names and descriptions are visible without scrolling on standard terminal sizes (80x24)
- **SC-003**: Progress updates appear within 100ms of detector completion
- **SC-004**: Users report improved confidence that the tool is working (qualitative feedback)
- **SC-005**: Scanning cancellation via ESC responds within 500ms

## Assumptions

- The existing 5 detector scripts will continue to be used without modification
- The Bubbletea spinner component is available and suitable for this use case
- Terminal supports Unicode characters for status icons (checkmark, X)
- The 30-second per-detector timeout is appropriate

## Out of Scope

- Modifying the detector scripts themselves
- Adding new diagnostic checks
- Changing the issue display after scanning completes
- Adding verbose output/logs from detector scripts (keep UI clean)
