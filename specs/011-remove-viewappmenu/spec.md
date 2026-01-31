# Feature Specification: Remove Unused ViewAppMenu Code

**Feature Branch**: `001-remove-viewappmenu`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "Remove unused ViewAppMenu code from TUI (GitHub Issue #75)"
**GitHub Issue**: [#75 - T046 Remove unused ViewAppMenu code](https://github.com/kairin/000-dotfiles/issues/75)

## Background

The TUI codebase has been refactored to use `ViewToolDetail` instead of `ViewAppMenu` for displaying tool action menus. This migration was part of the TUI Dashboard Consistency initiative (spec 008). The ViewAppMenu code is now dead code that is never executed:

- **Definition**: `ViewAppMenu` constant exists at line 31 of `model.go`
- **Usage**: 9 references exist but none set `currentView = ViewAppMenu`
- **Functions**: `viewAppMenu()` and `handleAppMenuEnter()` exist but are unreachable
- **Dependencies**: T020, T030, T038, T045 (all verified complete)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Maintains Clean Codebase (Priority: P1)

As a developer maintaining the TUI codebase, I want unused code removed so that the codebase is easier to understand, navigate, and maintain.

**Why this priority**: Dead code creates confusion for developers, increases cognitive load when reading the codebase, and may cause false positives in code analysis tools.

**Independent Test**: After removal, the TUI compiles successfully and all existing functionality works exactly as before since the removed code was never executed.

**Acceptance Scenarios**:

1. **Given** the TUI codebase with ViewAppMenu dead code, **When** the dead code is removed, **Then** the project compiles without errors
2. **Given** the TUI codebase with ViewAppMenu dead code, **When** the dead code is removed, **Then** no references to ViewAppMenu remain in the codebase
3. **Given** the cleaned TUI codebase, **When** a user navigates through all TUI screens, **Then** all existing functionality works identically to before

---

### User Story 2 - Build Verification (Priority: P1)

As a CI/CD pipeline, I want the codebase to compile cleanly after dead code removal so that deployments are not affected.

**Why this priority**: Build failure would block all development and deployment activities.

**Independent Test**: Run `go build` in the tui directory and verify successful compilation.

**Acceptance Scenarios**:

1. **Given** ViewAppMenu code has been removed, **When** `go build ./...` is run in the tui directory, **Then** the build succeeds with exit code 0
2. **Given** ViewAppMenu code has been removed, **When** `go vet ./...` is run, **Then** no errors are reported

---

### Edge Cases

- What happens if there are hidden references in comments or strings?
  - Comments mentioning ViewAppMenu should be removed if they describe removed functionality
  - String literals are not expected to reference ViewAppMenu (it's a Go constant)

- What happens if ViewAppMenu is imported by external packages?
  - The tui package is internal and not exported; no external dependencies exist

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST remove the `ViewAppMenu` constant from the View type definition in `model.go`
- **FR-002**: System MUST remove the `case ViewAppMenu:` handler from `handleKeyPress()` for up arrow navigation
- **FR-003**: System MUST remove the `case ViewAppMenu:` handler from `handleKeyPress()` for down arrow navigation
- **FR-004**: System MUST remove the `case ViewAppMenu:` handler from `handleEnter()` function
- **FR-005**: System MUST remove the `case ViewAppMenu:` handler from `View()` function
- **FR-006**: System MUST remove the `viewAppMenu()` function entirely
- **FR-007**: System MUST remove the `handleAppMenuEnter()` function entirely
- **FR-008**: System MUST remove any comments that specifically describe ViewAppMenu functionality
- **FR-009**: System MUST NOT introduce any new compiler errors or warnings
- **FR-010**: System MUST NOT change any existing user-facing behavior

### Files Affected

- **`tui/internal/ui/model.go`**: Primary file containing all ViewAppMenu code (9 references)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero references to "ViewAppMenu" exist in the codebase after cleanup (verified via grep)
- **SC-002**: TUI compiles successfully with `go build ./...` (exit code 0)
- **SC-002a**: TUI passes formatting check with `go fmt` (no changes needed)
- **SC-003**: TUI passes static analysis with `go vet ./...` (no errors)
- **SC-004**: All existing TUI navigation paths function correctly (manual verification)
- **SC-005**: GitHub Issue #75 can be closed upon completion

## Assumptions

- The migration from ViewAppMenu to ViewToolDetail is complete (T020, T030, T038, T045 verified)
- No runtime code paths set `currentView = ViewAppMenu` (verified via codebase search)
- The ViewAppMenu code is purely dead code with no side effects from removal
- The `View` enum iota values do not need to be preserved (Go will reassign)

## Out of Scope

- Refactoring other unused code (separate issues)
- Adding new functionality
- Modifying ViewToolDetail behavior
- Documentation updates beyond code comments
