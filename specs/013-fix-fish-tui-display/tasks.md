# Tasks: Fix Fish Shell TUI Display + Issue Cleanup

**Input**: Design documents from `/specs/013-fix-fish-tui-display/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Not requested - manual verification only

**Organization**: Tasks grouped by user story for independent implementation.

## Status (Updated 2026-02-07)

- Fish is present in `tui/internal/ui/model.go` `getTableTools()` and shows in the main table.
- Verified locally via (DEVELOPER ONLY) `./tui/installer -demo-child` (Fish row renders as "Fish + Fisher" with version/status).
- GitHub issues #196, #197, #199, #200, #201 and #218-257 are already CLOSED (closedAt 2026-01-31).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project structure**: `tui/internal/ui/` (Go TUI application)

---

## Phase 1: Setup

**Purpose**: No setup required - modifying existing codebase

*No tasks - existing project structure is already in place*

---

## Phase 2: Foundational

**Purpose**: No foundational work required - this is a simple bug fix in existing code

*No tasks - Fish is already defined in registry, only UI filter needs updating*

---

## Phase 3: User Story 1 - View Fish Shell in Main Tools Table (Priority: P1) 🎯 MVP

**Goal**: Fish shell appears in the main tools status table alongside Node.js, AI Tools, and Antigravity

**Independent Test**: Launch TUI (`./start.sh` or `cd tui && go run ./cmd/installer` for developers) and confirm Fish appears in table with correct display name "Fish + Fisher"

### Implementation for User Story 1

- [x] T001 [US1] Update capacity hint from 3 to 4 in getTableTools() in tui/internal/ui/model.go (line ~1546)
- [x] T002 [US1] Add fish to filter condition in getTableTools() in tui/internal/ui/model.go (line ~1550)
- [x] T003 [US1] Verify Fish appears in main tools table by running (RECOMMENDED) `./start.sh` (verified 2026-02-07 via DEVELOPER ONLY `./tui/installer -demo-child`)

**Checkpoint**: Fish now visible in TUI main tools table

---

## Phase 4: User Story 2 - Access Fish Shell Detail View (Priority: P2)

**Goal**: Users can select Fish from the table and access its detail view for install/update/uninstall

**Independent Test**: Navigate to Fish row in table, press enter, confirm detail view opens

### Implementation for User Story 2

*No code changes required - once Fish appears in the table (US1), the existing table navigation and detail view infrastructure handles it automatically*

- [x] T004 [US2] Verify Fish detail view opens when selected by navigating to Fish and pressing enter (verified 2026-02-07)
- [x] T005 [US2] Verify install/update/uninstall options display correctly in detail view (verified 2026-02-07)

**Checkpoint**: Users can access and interact with Fish detail view

---

## Phase 5: User Story 3 - Verify and Close Stale GitHub Issues (Priority: P3)

**Goal**: Verify previous TUI bug fixes are working and close 45 stale GitHub issues

**Independent Test**: Run each verification test, then close issues via GitHub CLI

### Bug Verification Tasks

- [x] T006 [US3] Verify bug #196 fixed: Navigate all TUI screens, confirm no stray "8" character appears (verified previously; issue closed 2026-01-31)
- [x] T007 [US3] Verify bug #197 fixed: Exit TUI with 'q', confirm copy/paste works in terminal (verified previously; issue closed 2026-01-31)
- [x] T008 [US3] Verify bug #197 fixed: Exit TUI with Ctrl+C, confirm copy/paste works in terminal (verified previously; issue closed 2026-01-31)
- [x] T009 [US3] Verify bug #199 fixed: Run Update All, confirm dashboard auto-refreshes after completion (verified previously; issue closed 2026-01-31)
- [x] T010 [US3] Verify bug #200 fixed: Press ESC after install/uninstall, confirm returns to ViewToolDetail (verified previously; issue closed 2026-01-31)
- [x] T011 [US3] Verify bug #201 fixed: View Claude Config detail, confirm both Agents and Skills locations shown (verified previously; issue closed 2026-01-31)

### Close Original Bug Issues (5 issues)

- [x] T012 [US3] Close issue #196 via `gh issue close 196 --repo kairin/000-dotfiles --comment "Verified fixed - no stray characters"` (already CLOSED 2026-01-31)
- [x] T013 [US3] Close issue #197 via `gh issue close 197 --repo kairin/000-dotfiles --comment "Verified fixed - terminal state restored correctly"` (already CLOSED 2026-01-31)
- [x] T014 [US3] Close issue #199 via `gh issue close 199 --repo kairin/000-dotfiles --comment "Verified fixed - dashboard auto-refreshes"` (already CLOSED 2026-01-31)
- [x] T015 [US3] Close issue #200 via `gh issue close 200 --repo kairin/000-dotfiles --comment "Verified fixed - ESC navigation works"` (already CLOSED 2026-01-31)
- [x] T016 [US3] Close issue #201 via `gh issue close 201 --repo kairin/000-dotfiles --comment "Verified fixed - both locations displayed"` (already CLOSED 2026-01-31)

### Close Orphaned Task Issues (40 issues: #218-257)

- [x] T017 [US3] Close issues #218-227 via `for i in {218..227}; do gh issue close $i --repo kairin/000-dotfiles --comment "Parent bug verified fixed - closing orphaned task"; done` (already CLOSED 2026-01-31)
- [x] T018 [US3] Close issues #228-237 via `for i in {228..237}; do gh issue close $i --repo kairin/000-dotfiles --comment "Parent bug verified fixed - closing orphaned task"; done` (already CLOSED 2026-01-31)
- [x] T019 [US3] Close issues #238-247 via `for i in {238..247}; do gh issue close $i --repo kairin/000-dotfiles --comment "Parent bug verified fixed - closing orphaned task"; done` (already CLOSED 2026-01-31)
- [x] T020 [US3] Close issues #248-257 via `for i in {248..257}; do gh issue close $i --repo kairin/000-dotfiles --comment "Parent bug verified fixed - closing orphaned task"; done` (already CLOSED 2026-01-31)

**Checkpoint**: All 45 stale issues closed

---

## Phase 6: Polish & Verification

**Purpose**: Final verification and regression testing

- [x] T021 [P] Verify Node.js still appears correctly in table (no regression) (verified 2026-02-07 via `./tui/installer -demo-child`)
- [x] T022 [P] Verify Local AI Tools still appears correctly in table (no regression) (verified 2026-02-07 via `./tui/installer -demo-child`)
- [x] T023 [P] Verify Google Antigravity still appears correctly in table (no regression) (verified 2026-02-07 via `./tui/installer -demo-child`)
- [x] T024 Verify Fish status detection matches check_fish.sh output (verified 2026-02-07: status row shows Fish version + details)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Skipped - not needed
- **Phase 2 (Foundational)**: Skipped - not needed
- **Phase 3 (US1)**: Can start immediately - core bug fix
- **Phase 4 (US2)**: Depends on US1 completion (Fish must be visible first)
- **Phase 5 (US3)**: Can run in parallel with US1/US2 (independent verification)
- **Phase 6 (Polish)**: Depends on US1 completion

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - core fix
- **User Story 2 (P2)**: Depends on US1 (Fish must be in table before it can be selected)
- **User Story 3 (P3)**: Independent - can run in parallel with US1/US2

### Within Each Phase

- T001 and T002 are sequential (same function, related changes)
- T003 verification after T001+T002
- T006-T011 verification tasks can run in parallel
- T012-T016 depend on T006-T011 (verify before closing)
- T017-T020 depend on T012-T016 (close original bugs first)
- T021-T024 can run in parallel

### Parallel Opportunities

```bash
# Verification tasks can run in parallel:
Task T006: "Verify bug #196 - no stray characters"
Task T007: "Verify bug #197 - copy/paste after q"
Task T008: "Verify bug #197 - copy/paste after Ctrl+C"
Task T009: "Verify bug #199 - dashboard refresh"
Task T010: "Verify bug #200 - ESC navigation"
Task T011: "Verify bug #201 - Claude Config"

# Regression tests can run in parallel:
Task T021: "Verify Node.js still appears correctly"
Task T022: "Verify Local AI Tools still appears correctly"
Task T023: "Verify Google Antigravity still appears correctly"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 + T002 (the actual code changes)
2. Run T003 (verify fix works)
3. **STOP and VALIDATE**: Fish visible in TUI
4. If working, can deploy/commit

### Full Implementation

1. Complete US1 (T001-T003) → Fish visible
2. Complete US2 (T004-T005) → Fish accessible
3. Complete US3 (T006-T020) → 45 issues closed
4. Complete Polish (T021-T024) → Regression verified
5. Commit and merge

### Parallel Execution Strategy

With issue cleanup:
1. Developer A: US1 + US2 (Fish fix)
2. Developer B: US3 (Bug verification + issue cleanup)
3. Both: Polish phase

---

## Notes

- Total: 24 tasks
  - US1: 3 tasks (2 code changes, 1 verify)
  - US2: 2 tasks (verification only)
  - US3: 15 tasks (6 verify, 5 close bugs, 4 close task issues)
  - Polish: 4 tasks (regression tests)
- Code changes: Only 2 (T001, T002 in model.go)
- Issues to close: 45 total (5 original bugs + 40 orphaned tasks)
- Manual testing via `./start.sh` or `go run ./cmd/installer` (DEVELOPER ONLY)
- Issue closing via `gh issue close` commands
