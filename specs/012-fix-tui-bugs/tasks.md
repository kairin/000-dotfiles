# Tasks: Fix TUI Bugs

**Input**: Design documents from `/specs/012-fix-tui-bugs/`
**Prerequisites**: plan.md (required), spec.md (required), research.md
**GitHub Issues**: #196, #197, #199, #200, #201

**Tests**: No automated tests required - verification via Go toolchain (`go build`, `go fmt`, `go vet`) and manual testing per quickstart.md.

**Organization**: Tasks are grouped by user story (bug fix) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Target Directory**: `tui/` (Go TUI application)
- **Main Entry**: `tui/cmd/installer/main.go`
- **UI Components**: `tui/internal/ui/*.go`
- **Cache Layer**: `tui/internal/cache/cache.go`

---

## Phase 1: Setup (Pre-Fix Verification)

**Purpose**: Confirm current bug status and establish baseline

- [X] T001 Run `go build ./...` in tui/ to verify code compiles before changes
- [X] T002 Run `go fmt ./...` in tui/ to verify code formatting before changes
- [X] T003 Document current copy/paste behavior (Bug #197 baseline) by running TUI and testing Ctrl+V after exit

**Checkpoint**: Baseline established - ready for bug fixes

---

## Phase 2: Foundational (N/A for this feature)

**Purpose**: No foundational work needed - this is a pure bug fix task targeting existing code

**⚠️ Note**: This phase is intentionally empty as there are no blocking prerequisites.

---

## Phase 3: User Story 1 - Terminal State Restoration (Priority: P1) 🎯 MVP

**Goal**: Fix copy/paste functionality after TUI exit (Bug #197)

**Independent Test**: Run TUI, exit with 'q' or Ctrl+C, verify Ctrl+V paste works in terminal

### Implementation for User Story 1

- [X] T004 [US1] Add signal handling imports (os/signal, syscall) in tui/cmd/installer/main.go
- [X] T005 [US1] Create signal channel and register SIGINT/SIGTERM handlers in tui/cmd/installer/main.go
- [X] T006 [US1] Add deferred cleanup function to restore terminal state in tui/cmd/installer/main.go
- [X] T007 [US1] Verify terminal mode restoration after subprocess (sudo) calls in tui/internal/ui/model.go
- [X] T008 [US1] Manual test: Run TUI, exit with 'q', verify copy/paste works ✓ VERIFIED
- [X] T009 [US1] Manual test: Run TUI, exit with Ctrl+C, verify copy/paste works ✓ VERIFIED

**Checkpoint**: User Story 1 complete - Terminal state properly restored after TUI exit

---

## Phase 4: User Story 2 - Dashboard Auto-Refresh (Priority: P1)

**Goal**: Dashboard automatically shows updated status after "Update All" completes (Bug #199)

**Independent Test**: Run "Update All", observe dashboard shows current status without manual refresh

### Implementation for User Story 2

- [X] T010 [US2] Locate batch completion handler in tui/internal/ui/model.go (lines ~358-370)
- [X] T011 [US2] Add `m.loading = true` when returning to Dashboard after batch update in tui/internal/ui/model.go
- [X] T012 [US2] Ensure cache invalidation for updated tools before refresh call in tui/internal/ui/model.go
- [X] T013 [US2] Verify loading spinner displays while statuses refresh in tui/internal/ui/model.go
- [X] T014 [US2] Manual test: Run "Update All", verify loading indicator appears and status updates automatically
      Verified (2026-02-08):
      - Applied sudoers update so `sudo -n true` succeeds (no interactive prompt).
      - Ran `Update All` (Node.js) end-to-end; dashboard returned without needing manual refresh and update count cleared.
      - Note: Node update required `fnm` bootstrap in update script (fixed in repo) so the batch could complete.

**Checkpoint**: User Story 2 complete - Dashboard auto-refreshes after batch operations

---

## Phase 5: User Story 3 - ESC Navigation After Install (Priority: P2)

**Goal**: ESC returns to ViewToolDetail after install/uninstall, not parent menu (Bug #200)

**Independent Test**: Navigate to tool detail, install/uninstall, press ESC, verify return to tool detail view

### Implementation for User Story 3

- [X] T015 [US3] Locate InstallerExitMsg handler in tui/internal/ui/model.go (lines ~306-338)
- [X] T016 [US3] Add tracking for "came from tool detail" state when launching installer in tui/internal/ui/model.go
- [X] T017 [US3] Modify InstallerExitMsg handler to return to ViewToolDetail (not toolDetailFrom) in tui/internal/ui/model.go
- [X] T018 [US3] Ensure tool status refresh after returning to ViewToolDetail in tui/internal/ui/model.go
- [X] T019 [US3] Manual test: Extras → Tool Detail → Install → ESC → verify return to Tool Detail
      Verified (2026-02-08): Used Extras → ShellCheck → Install, then ESC returned to Tool Detail view.
- [X] T020 [US3] Manual test: From Tool Detail, press ESC again → verify return to Extras
      Verified (2026-02-08): ESC from Tool Detail returned to Extras list as expected.

**Checkpoint**: User Story 3 complete - ESC navigation follows expected flow

---

## Phase 6: User Story 4 - Multi-Line Location Display (Priority: P2)

**Goal**: Tool detail view shows all location lines including Details array (Bug #201)

**Independent Test**: View Claude Config detail, verify both Skills and Agents locations are displayed

### Implementation for User Story 4

- [X] T021 [P] [US4] Verify cache.go correctly parses multi-line locations (no changes expected) in tui/internal/cache/cache.go
- [X] T022 [US4] Locate Location rendering code in tui/internal/ui/tooldetail.go (lines ~249-253)
- [X] T023 [US4] Modify renderRow or add code to also display status.Details array in tui/internal/ui/tooldetail.go
- [X] T024 [US4] Ensure proper indentation/alignment for multi-line location display in tui/internal/ui/tooldetail.go
- [X] T025 [US4] Manual test: View Claude Config detail, verify both "Skills:" and "Agents:" lines visible
      Verified (2026-02-07): Installed Claude Config via scripts and confirmed TUI shows both lines:
      - Skills: /home/kkk/.claude/commands
      - Agents: /home/kkk/.claude/agents

**Checkpoint**: User Story 4 complete - All location data visible in tool detail

---

## Phase 7: User Story 5 - Stray Character Elimination (Priority: P3)

**Goal**: Eliminate stray "8" character from TUI screens (Bug #196)

**Independent Test**: Navigate through all TUI screens, verify no stray characters appear

### Implementation for User Story 5

- [X] T026 [US5] Investigate spinner animation for escape sequence leakage in tui/internal/ui/model.go
- [X] T027 [US5] Check for mouse input being rendered as text in tui/cmd/installer/main.go
- [X] T028 [US5] Test with `tea.WithoutMouseCellMotion()` option to isolate mouse input issues in tui/cmd/installer/main.go
- [X] T029 [US5] Review lipgloss style application for escape sequence corruption in tui/internal/ui/*.go
- [X] T030 [US5] Add screen clear before problematic re-renders if needed in tui/internal/ui/model.go
- [X] T031 [US5] Manual test: Navigate all screens, resize terminal, verify no stray characters
      Verified (2026-02-07): Smoke-tested navigation across Dashboard, Extras, MCP Servers, and SpecKit Updater.
      Note: Did not run install/update flows requiring sudo in this environment.

**Checkpoint**: User Story 5 complete - Clean rendering on all screens

---

## Phase 8: Polish & Verification

**Purpose**: Final verification and issue closure

- [X] T032 Run `go fmt ./...` in tui/ to ensure code formatting
- [X] T033 Run `go vet ./...` in tui/ to check for static analysis issues
- [X] T034 Run `go build ./...` in tui/ to verify compilation
- [X] T035 Execute full quickstart.md verification test suite (all 5 test cases)
      Verified (2026-02-08):
      - #197 terminal state restore: verified earlier (exit via q/Ctrl+C retains copy/paste)
      - #199 Update All auto-refresh: verified (T014)
      - #200 ESC navigation: verified (T019/T020)
      - #201 multi-line Location: verified earlier (Claude Config shows Skills + Agents)
      - #196 stray character: verified earlier during navigation (no stray characters observed)
      Notes (2026-02-07): Partial completion only. Bugs #199/#200 require sudo-driven flows to verify end-to-end.
- [X] T036 Close GitHub Issue #197 (Terminal State)
      Verified (2026-02-07): Issue already CLOSED on GitHub.
- [X] T037 Close GitHub Issue #199 (Dashboard Refresh)
      Verified (2026-02-07): Issue already CLOSED on GitHub.
- [X] T038 Close GitHub Issue #200 (ESC Navigation)
      Verified (2026-02-07): Issue already CLOSED on GitHub.
- [X] T039 Close GitHub Issue #201 (Multi-Line Location)
      Verified (2026-02-07): Issue already CLOSED on GitHub.
- [X] T040 Close GitHub Issue #196 (Stray Character)
      Verified (2026-02-07): Issue already CLOSED on GitHub.

**Checkpoint**: All bugs verified fixed, all issues closed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verification only
- **Foundational (Phase 2)**: N/A - empty phase
- **User Story 1 (Phase 3)**: Can start immediately after Setup
- **User Story 2 (Phase 4)**: Can start immediately after Setup (independent of US1)
- **User Story 3 (Phase 5)**: Can start immediately after Setup (independent of US1, US2)
- **User Story 4 (Phase 6)**: Can start immediately after Setup (independent of other stories)
- **User Story 5 (Phase 7)**: Can start immediately after Setup (independent of other stories)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

| Story | File(s) Modified | Can Parallel With |
|-------|------------------|-------------------|
| US1 | main.go, model.go | US4 (different files) |
| US2 | model.go | US4 (different files) |
| US3 | model.go | US4 (different files) |
| US4 | tooldetail.go, cache.go | US1, US2, US3 (different files) |
| US5 | Unknown (investigation) | Depends on findings |

### Within Each User Story

- Investigation/locate tasks before modification tasks
- Code changes before manual testing
- All manual tests pass before story is considered complete

### Parallel Opportunities

- **US1 + US4**: Can run in parallel (main.go vs tooldetail.go)
- **US2 + US4**: Can run in parallel (model.go refresh vs tooldetail.go display)
- **US3 + US4**: Can run in parallel (model.go navigation vs tooldetail.go display)
- **T021**: Parallel verification task (cache.go is read-only)

**Note**: US1, US2, US3 all modify model.go - recommend sequential execution within this group.

---

## Parallel Example: Stories 1-4

```bash
# Option A: Prioritize by severity (P1 first, then P2)
# Sequential within P1 group (same file)
Execute: US1 (Terminal State) → US2 (Dashboard Refresh) → US3 (ESC Navigation)
# Then:
Execute: US4 (Multi-Line Location) in parallel with any above

# Option B: Maximize parallelism
Developer A: US1, US2, US3 (model.go changes - sequential)
Developer B: US4 (tooldetail.go - parallel with A)
Then: US5 (investigation - after US1-US4 complete to avoid conflicts)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 3: User Story 1 (Terminal State) - **Most disruptive bug**
3. Complete Phase 4: User Story 2 (Dashboard Refresh) - **Causes user confusion**
4. **STOP and VALIDATE**: Test US1 and US2 independently
5. Close Issues #197 and #199

### Incremental Delivery

1. Complete Setup → Baseline established
2. Add User Story 1 → Test → Close #197
3. Add User Story 2 → Test → Close #199
4. Add User Story 3 → Test → Close #200
5. Add User Story 4 → Test → Close #201
6. Add User Story 5 → Test → Close #196
7. Each story fixes a specific bug without affecting others

### Risk-Based Order

| Order | Story | Risk Level | Rationale |
|-------|-------|------------|-----------|
| 1 | US1 | Low | Isolated to main.go entry point |
| 2 | US4 | Low | Isolated to tooldetail.go |
| 3 | US2 | Medium | Modifies model.go state handling |
| 4 | US3 | Medium | Modifies model.go navigation |
| 5 | US5 | High | Unknown root cause, may need investigation |

---

## Notes

- All changes are within existing `tui/` directory
- No new files created - modifying existing Go code only
- Pre-existing module path issues (dotfiles-installer vs dotfiles-installer) may affect `go build` but not code changes
- US5 (Stray Character) may require extended debugging - root cause not yet identified
- Commit after each user story completion for easy rollback
- Manual testing via quickstart.md is the primary verification method
