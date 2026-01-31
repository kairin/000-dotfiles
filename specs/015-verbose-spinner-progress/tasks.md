# Tasks: Verbose Spinner Progress for All TUI Components

**Input**: Design documents from `/specs/015-verbose-spinner-progress/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), quickstart.md (complete)

**Tests**: Not explicitly requested - omitted per specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Project structure**: `tui/internal/ui/` (existing TUI package)
- **Reference implementation**: `tui/internal/ui/diagnostics.go:380-446`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify build environment and reference pattern

- [ ] T001 Verify Go build works with `cd tui && go build ./cmd/installer`
- [ ] T002 Review reference implementation in tui/internal/ui/diagnostics.go:380-446 (renderScanningProgress pattern)

---

## Phase 2: Foundational (No Blocking Prerequisites)

**Purpose**: This feature modifies existing UI components - no new shared infrastructure needed

**Note**: All user stories can proceed immediately after Phase 1 since each modifies a different file. The only shared dependency is understanding the diagnostics.go pattern (T002).

**Checkpoint**: Ready to proceed to user stories

---

## Phase 3: User Story 1 - Per-Item Progress During Multi-Item Loading (Priority: P1) 🎯 MVP

**Goal**: Transform opaque "Loading..." into transparent per-item feedback showing exactly what's happening in NerdFonts and MCPServers views

**Independent Test**: Navigate to NerdFonts view, observe 8 fonts listed with individual status indicators (○ pending, ⠋ loading, ✓ installed, ✗ not installed) and descriptions during loading phase

### Implementation for User Story 1

#### NerdFonts Component (P1.1 - nerdfonts.go)

- [ ] T003 [P] [US1] Add fontDescriptions constant map with 8 font descriptions in tui/internal/ui/nerdfonts.go
- [ ] T004 [P] [US1] Add FontItemStatus enum (Pending, Loading, Complete, Failed) in tui/internal/ui/nerdfonts.go
- [ ] T005 [US1] Add fontStatuses []FontItemStatus field to NerdFontsModel in tui/internal/ui/nerdfonts.go
- [ ] T006 [US1] Add fontSpinners []spinner.Model field to NerdFontsModel in tui/internal/ui/nerdfonts.go
- [ ] T007 [US1] Initialize per-font spinners in NewNerdFontsModel() in tui/internal/ui/nerdfonts.go
- [ ] T008 [US1] Add renderVerboseProgress() method following diagnostics.go:380-446 pattern in tui/internal/ui/nerdfonts.go
- [ ] T009 [US1] Modify Update() to handle per-font spinner.TickMsg and status updates in tui/internal/ui/nerdfonts.go
- [ ] T010 [US1] Modify View() to call renderVerboseProgress() when loading=true in tui/internal/ui/nerdfonts.go

**Checkpoint (NerdFonts)**: Navigate to Nerd Fonts → observe per-font progress with spinners and descriptions

#### MCPServers Component (P1.2 - mcpservers.go)

- [ ] T011 [P] [US1] Add ServerItemStatus enum (Pending, Loading, Complete, Failed) in tui/internal/ui/mcpservers.go
- [ ] T012 [US1] Add serverStatuses []ServerItemStatus field to MCPServersModel in tui/internal/ui/mcpservers.go
- [ ] T013 [US1] Add serverSpinners []spinner.Model field to MCPServersModel in tui/internal/ui/mcpservers.go
- [ ] T014 [US1] Initialize per-server spinners in NewMCPServersModel() in tui/internal/ui/mcpservers.go
- [ ] T015 [US1] Add renderVerboseProgress() method (servers have Description in registry) in tui/internal/ui/mcpservers.go
- [ ] T016 [US1] Modify Update() to handle per-server spinner.TickMsg and status updates in tui/internal/ui/mcpservers.go
- [ ] T017 [US1] Modify View() to call renderVerboseProgress() when loading=true in tui/internal/ui/mcpservers.go

**Checkpoint (MCPServers)**: Navigate to Extras → MCP Servers → observe per-server progress with spinners and descriptions

**Checkpoint**: User Story 1 complete - NerdFonts and MCPServers show per-item progress with spinners, names, and descriptions

---

## Phase 4: User Story 4 - Per-Tool Status in Extras Menu (Priority: P1)

**Goal**: Show status indicators for each tool inline with menu items so users can quickly identify which tools are installed, loading, or need attention

**Independent Test**: Navigate to Extras menu and observe that each tool menu item has a leading status indicator (○/⠋/✓/✗) while status checks run in background

### Implementation for User Story 4

- [ ] T018 [P] [US4] Add ToolMenuStatus enum (Pending, Loading, Complete, Failed) in tui/internal/ui/extras.go
- [ ] T019 [US4] Add toolMenuStatuses []ToolMenuStatus field to ExtrasModel in tui/internal/ui/extras.go
- [ ] T020 [US4] Add toolMenuSpinners []spinner.Model field to ExtrasModel in tui/internal/ui/extras.go
- [ ] T021 [US4] Initialize per-tool menu spinners in NewExtrasModel() matching tools count in tui/internal/ui/extras.go
- [ ] T022 [US4] Modify Update() to track per-tool status from extrasStatusLoadedMsg in tui/internal/ui/extras.go
- [ ] T023 [US4] Modify Update() to handle per-tool spinner.TickMsg updates in tui/internal/ui/extras.go
- [ ] T024 [US4] Modify renderExtrasMenu() to prefix each tool with status icon (○/⠋/✓/✗) in tui/internal/ui/extras.go
- [ ] T025 [US4] Add visual separator (─────────────) between tools and action menu items in renderExtrasMenu() in tui/internal/ui/extras.go
- [ ] T026 [US4] Modify View() header to show progress during loading "⠋ Loading... (X/9 complete)" in tui/internal/ui/extras.go
- [ ] T027 [US4] Add completedCount int field to ExtrasModel for tracking progress in tui/internal/ui/extras.go

**Checkpoint**: User Story 4 complete - Extras menu shows per-tool status indicators with progress header

---

## Phase 5: User Story 2 - Per-Stage Progress During Installation (Priority: P2)

**Goal**: Show individual stage progress with descriptions during tool installation so users understand what's happening at each step

**Independent Test**: Initiate any tool installation → observe all stages listed with pending status, spinner on active stage, checkmarks on completed stages, and one-line descriptions

### Implementation for User Story 2

- [ ] T028 [P] [US2] Add stageDescriptions constant map with 8 stage descriptions in tui/internal/ui/installer.go
- [ ] T029 [US2] Add stageSpinners []spinner.Model field to InstallerModel in tui/internal/ui/installer.go
- [ ] T030 [US2] Initialize per-stage spinners in NewInstallerModel() and variants in tui/internal/ui/installer.go
- [ ] T031 [US2] Modify renderProgressBar() to show verbose stage list with descriptions in tui/internal/ui/installer.go
- [ ] T032 [US2] Add stage icon/spinner rendering (○ pending, ⠋ loading, ✓ complete, ✗ failed) in renderProgressBar() in tui/internal/ui/installer.go
- [ ] T033 [US2] Modify Update() to handle per-stage spinner.TickMsg for active stage in tui/internal/ui/installer.go
- [ ] T034 [US2] Ensure output log (TailSpinner) remains visible alongside stage progress in tui/internal/ui/installer.go

**Checkpoint**: User Story 2 complete - installation shows per-stage verbose progress with descriptions

---

## Phase 6: User Story 3 - Real-Time Item Count During Batch Operations (Priority: P3)

**Goal**: Show running count of completed items and found issues during batch operations

**Independent Test**: Trigger any multi-item operation → observe "Progress: X/Y complete" summary line updating as items complete

### Implementation for User Story 3

#### NerdFonts Progress Summary

- [ ] T035 [P] [US3] Add completedCount int field to NerdFontsModel in tui/internal/ui/nerdfonts.go
- [ ] T036 [US3] Update completedCount in Update() when font status changes to Complete/Failed in tui/internal/ui/nerdfonts.go
- [ ] T037 [US3] Add progress summary line "Progress: X/8 complete" in renderVerboseProgress() in tui/internal/ui/nerdfonts.go

#### MCPServers Progress Summary

- [ ] T038 [P] [US3] Add completedCount int field to MCPServersModel in tui/internal/ui/mcpservers.go
- [ ] T039 [US3] Update completedCount in Update() when server status changes to Complete/Failed in tui/internal/ui/mcpservers.go
- [ ] T040 [US3] Add progress summary line "Progress: X/7 complete" in renderVerboseProgress() in tui/internal/ui/mcpservers.go

**Checkpoint**: User Story 3 complete - all progress summaries update in real-time

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and consistency checks

### Consistency Verification

- [ ] T041 [P] Verify spinner.Dot style used consistently across all enhanced components in tui/internal/ui/
- [ ] T042 [P] Verify status icons (✓, ✗, ○) match diagnostics.go pattern in tui/internal/ui/
- [ ] T043 [P] Verify fixed-width name columns (20 chars) for alignment in all components in tui/internal/ui/

### ESC Cancellation Testing

- [ ] T044 Test ESC cancellation works during loading in NerdFonts view
- [ ] T045 Test ESC cancellation works during loading in MCPServers view
- [ ] T046 Test ESC cancellation works during loading in Extras menu view
- [ ] T047 Test ESC cancellation works during installation in Installer view

### Edge Case Testing

- [ ] T048 Test terminal resize (80x24) during progress display re-renders correctly
- [ ] T049 Test timeout handling shows ✗ icon and continues with other items

### Final Validation

- [ ] T050 Build and run full visual test: `cd tui && go build ./cmd/installer && ./dotfiles-installer`
- [ ] T051 Run quickstart.md validation workflow
- [ ] T052 Verify SC-001 through SC-006 success criteria from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - PASS-THROUGH (no blocking tasks)
- **User Stories (Phase 3-6)**: Can start immediately after Phase 1
  - US1, US4, US2 can proceed in parallel (different files)
  - US3 depends on US1 structures (adds completedCount to existing models)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Files Modified | Dependencies |
|-------|----------|----------------|--------------|
| US1 | P1 | nerdfonts.go, mcpservers.go | None |
| US4 | P1 | extras.go | None |
| US2 | P2 | installer.go | None |
| US3 | P3 | nerdfonts.go, mcpservers.go | US1 (extends structures) |

### Within Each User Story

1. Constants/enums first (parallelizable with [P])
2. Model fields after enums
3. Spinner initialization after fields
4. Rendering methods after initialization
5. Update() integration last

### Parallel Opportunities

**Cross-Story Parallelism (different files, no conflicts):**
```
US1 (nerdfonts.go) ↔ US1 (mcpservers.go) ↔ US4 (extras.go) ↔ US2 (installer.go)
```

**Within User Story 1 (NerdFonts + MCPServers in parallel):**
```
T003-T010 (NerdFonts) ↔ T011-T017 (MCPServers)
```

**Constants parallelism:**
```
T003 (font descriptions) ↔ T011 (server enum) ↔ T018 (tool enum) ↔ T028 (stage descriptions)
```

---

## Parallel Example: All P1 Components

```bash
# All these components can be developed in parallel (different files):

# Developer A: NerdFonts (nerdfonts.go)
Task: "Add fontDescriptions constant map in tui/internal/ui/nerdfonts.go"
Task: "Add FontItemStatus enum in tui/internal/ui/nerdfonts.go"
# ... T003-T010

# Developer B: MCPServers (mcpservers.go)
Task: "Add ServerItemStatus enum in tui/internal/ui/mcpservers.go"
Task: "Add serverStatuses field in tui/internal/ui/mcpservers.go"
# ... T011-T017

# Developer C: Extras Menu (extras.go)
Task: "Add ToolMenuStatus enum in tui/internal/ui/extras.go"
Task: "Modify renderExtrasMenu() for inline status in tui/internal/ui/extras.go"
# ... T018-T027

# Developer D: Installer (installer.go) - can start immediately
Task: "Add stageDescriptions constant map in tui/internal/ui/installer.go"
Task: "Modify renderProgressBar() for verbose stage list in tui/internal/ui/installer.go"
# ... T028-T034
```

---

## Implementation Strategy

### MVP First (User Story 1 - NerdFonts Only)

1. Complete Phase 1: Setup (T001-T002)
2. Skip Phase 2: No blocking tasks
3. Complete NerdFonts only (T003-T010)
4. **STOP and VALIDATE**: Test NerdFonts verbose progress independently
5. Continue with MCPServers (T011-T017) if NerdFonts pattern works

### Incremental Delivery

1. NerdFonts verbose progress → Validate pattern works → ✓
2. MCPServers verbose progress → Validate consistency → ✓
3. Extras menu inline status → Validate menu experience → ✓
4. Installer stage progress → Validate independently → ✓
5. Progress summary counts → Validate real-time updates → ✓
6. Polish phase → Final validation → ✓

### Recommended Execution Order

```
T001 → T002 (Setup)
   ↓
T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 (NerdFonts MVP)
   ↓
VALIDATE: Test NerdFonts loading
   ↓
T011 → T012 → T013 → T014 → T015 → T016 → T017 (MCPServers)
   ↓
T018 → T019 → T020 → T021 → T022 → T023 → T024 → T025 → T026 → T027 (Extras Menu)
   ↓
VALIDATE: All P1 views working
   ↓
T028 → T029 → T030 → T031 → T032 → T033 → T034 (Installer - US2)
   ↓
VALIDATE: Installer stage progress
   ↓
T035 → T036 → T037 (NerdFonts count) + T038 → T039 → T040 (MCPServers count) (US3)
   ↓
T041 → T042 → T043 → ... → T052 (Polish)
```

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Reference implementation: `tui/internal/ui/diagnostics.go:380-446`
- Commit after each component (NerdFonts, MCPServers, Extras, Installer)
- Stop at any checkpoint to validate story independently
- Extras component: Menu items get inline status indicators, not a separate table view
- US4 is listed as Phase 4 despite being P1 priority to keep Extras changes grouped logically
