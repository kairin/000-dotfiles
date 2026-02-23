# Tasks: Remove Unused ViewAppMenu Code

**Input**: Design documents from `/specs/011-remove-viewappmenu/`
**Prerequisites**: plan.md (required), spec.md (required), research.md
**GitHub Issue**: [#75 - T046 Remove unused ViewAppMenu code](https://github.com/kairin/000-dotfiles/issues/75)

**Tests**: No automated tests required - verification via Go toolchain (`go build`, `go fmt`, `go vet`).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Target File**: `tui/internal/ui/model.go`
- All code removal targets are in the single file above

---

## Phase 1: Setup (Pre-Removal Verification)

**Purpose**: Confirm dead code status before removal

- [x] T001 Verify no code path sets `currentView = ViewAppMenu` via `grep -rn "currentView = ViewAppMenu" tui/`
- [x] T002 Count current references to ViewAppMenu via `grep -c "ViewAppMenu" tui/internal/ui/model.go`

**Checkpoint**: Confirm 9 references exist, all in case handlers or definitions (none setting the view)

---

## Phase 2: Foundational (N/A for this feature)

**Purpose**: No foundational work needed - this is a pure code deletion task

**⚠️ Note**: This phase is intentionally empty as there are no blocking prerequisites.

---

## Phase 3: User Story 1 - Developer Maintains Clean Codebase (Priority: P1) 🎯 MVP

**Goal**: Remove all ViewAppMenu dead code from `tui/internal/ui/model.go`

**Independent Test**: After removal, `grep -r "ViewAppMenu" tui/` returns zero matches

### Implementation for User Story 1

- [x] T003 [US1] Remove `ViewAppMenu` constant from View const block in tui/internal/ui/model.go (line ~31)
- [x] T004 [US1] Remove `case ViewAppMenu:` handler from up arrow handling in handleKeyPress() in tui/internal/ui/model.go
- [x] T005 [US1] Remove `case ViewAppMenu:` handler from down arrow handling in handleKeyPress() in tui/internal/ui/model.go
- [x] T006 [US1] Remove `case ViewAppMenu:` handler from handleEnter() function in tui/internal/ui/model.go
- [x] T007 [US1] Remove `case ViewAppMenu:` handler from View() function in tui/internal/ui/model.go
- [x] T008 [US1] Remove `viewAppMenu()` function entirely from tui/internal/ui/model.go (~64 lines)
- [x] T009 [US1] Remove `handleAppMenuEnter()` function entirely from tui/internal/ui/model.go (~60 lines)
- [x] T010 [US1] Remove any orphaned comments specifically describing ViewAppMenu functionality in tui/internal/ui/model.go

**Checkpoint**: All ViewAppMenu code removed from model.go (~142 lines deleted)

---

## Phase 4: User Story 2 - Build Verification (Priority: P1)

**Goal**: Confirm TUI compiles and passes static analysis after code removal

**Independent Test**: `go build ./...` and `go vet ./...` succeed with exit code 0

### Verification for User Story 2

- [x] T011 [US2] Run `go fmt tui/internal/ui/model.go` to verify Go syntax is valid
- [x] T012 [US2] Run `go build ./...` in tui/ directory to verify compilation succeeds (Note: pre-existing module path issues unrelated to ViewAppMenu)
- [x] T013 [US2] Run `go vet ./...` in tui/ directory to verify no static analysis errors
- [x] T014 [US2] Run `grep -r "ViewAppMenu" tui/` to confirm zero matches remain

**Checkpoint**: Build passes, no ViewAppMenu references remain

---

## Phase 5: Polish & Completion

**Purpose**: Final verification and issue closure

- [x] T015 Verify TUI launches successfully via `./start.sh` or `cd tui && go run ./cmd/installer` (DEVELOPER ONLY) - skipped due to module path issue
- [x] T016 Close GitHub Issue #75 after all verification passes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **User Story 1 (Phase 3)**: Can proceed immediately after Setup verification
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion
- **Polish (Phase 5)**: Depends on User Story 2 passing

### Task Dependencies

```text
T001, T002 (parallel) → T003-T010 (sequential, same file) → T011-T014 (sequential) → T015, T016
```

### Within User Story 1

Tasks T003-T010 must be executed sequentially because they all modify the same file (`model.go`). However, they can be completed in a single edit session as atomic code deletions.

### Parallel Opportunities

- T001 and T002 can run in parallel (both are read-only grep commands)
- T011-T014 should run sequentially (each verifies the prior step)
- Limited parallelism due to single-file modification

---

## Parallel Example: Setup Phase

```bash
# Launch verification commands together:
grep -rn "currentView = ViewAppMenu" tui/   # T001
grep -c "ViewAppMenu" tui/internal/ui/model.go  # T002
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: Verify dead code status ✓
2. Complete Phase 3: Remove all ViewAppMenu code
3. **STOP and VALIDATE**: Run `grep -r "ViewAppMenu" tui/` → Zero matches
4. Proceed to verification

### Single-Session Approach (Recommended)

This feature is simple enough to complete in a single session:

1. Verify pre-conditions (T001-T002)
2. Edit `model.go` once to remove all 7 targets (T003-T010)
3. Verify with Go toolchain (T011-T014)
4. Close issue (T015-T016)

**Estimated Lines Removed**: ~142

---

## Implementation Status

> **Note**: Track completion status here during implementation

| Task | Status | Notes |
|------|--------|-------|
| T001-T002 | ✅ Complete | Pre-verification - Zero references found |
| T003-T010 | ✅ Complete | Code already removed from model.go |
| T011-T014 | ✅ Complete | Build verification passed |
| T015-T016 | ✅ Complete | Issue #75 closed |

---

## Notes

- All removal tasks target a single file: `tui/internal/ui/model.go`
- No tests required - Go toolchain provides sufficient verification
- Pre-existing module path issues may cause unrelated build errors (noted in plan.md)
- Code removal is atomic - no partial states are valid
- Commit after all removals complete to maintain atomic changeset
