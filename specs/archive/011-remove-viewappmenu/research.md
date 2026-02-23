# Research: Remove Unused ViewAppMenu Code

**Feature**: 001-remove-viewappmenu
**Date**: 2026-01-28
**Status**: Complete

## Summary

No research required. This is a straightforward dead code removal task with no unknowns or technical decisions.

## Findings

### Dead Code Verification

**Decision**: ViewAppMenu is confirmed dead code suitable for removal.

**Rationale**:
- Searched entire codebase for `currentView = ViewAppMenu` → Zero matches
- All 9 references are in switch case handlers or function definitions
- No code path sets the view to ViewAppMenu after TUI Dashboard Consistency migration
- T020, T030, T038, T045 (ViewToolDetail migration tasks) are complete

**Alternatives Considered**:
- Deprecation with warning: Rejected - code is already unreachable, no runtime impact
- Gradual removal: Rejected - single atomic deletion is simpler and cleaner

### Go iota Reassignment

**Decision**: Allow Go to reassign iota values automatically.

**Rationale**:
- View constants are internal to the TUI package
- No external serialization or storage of View values
- Removing ViewAppMenu will shift subsequent iota values (ViewMethodSelect, ViewInstaller, etc.)
- This is safe because View values are only used in runtime switch statements

**Alternatives Considered**:
- Preserve iota values with explicit assignment: Rejected - unnecessary complexity for internal enum
- Add placeholder constant: Rejected - defeats purpose of dead code removal

### Build Verification Strategy

**Decision**: Use `go build`, `go fmt`, `go vet` for verification.

**Rationale**:
- Standard Go toolchain for syntax and semantic verification
- No runtime tests needed since removed code was unreachable
- Manual TUI testing optional but not required

**Alternatives Considered**:
- Full integration test suite: Rejected - overkill for dead code removal
- Skip verification: Rejected - must confirm no compile errors

## Open Questions

None - all questions resolved.

## Next Steps

Proceed to `/speckit.tasks` for task generation.
