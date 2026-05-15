> **Checklist refreshed 2026-05-16.** Implementation shipped before task formalization.
> Marks reflect verified state as of PR merge. T021–T022 remain open (doc invariant tests not yet written).

# Tasks: Setup Menu Recommendation Guidance

**Input**: Design documents from `/specs/002-setup-menu-recommendation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/setup-menu.md, quickstart.md

**Tests**: Tests are required for this feature because the specification requires automated validation of recommendation states and the constitution requires validation for setup behavior.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Shell wrapper: `setup`
- Python recommendation logic and summary rendering: `dotfiles_tools/machine_summary.py`
- Existing setup/action planning support: `dotfiles_tools/bootstrap.py`, `dotfiles_tools/tool_installer.py`, `dotfiles_tools/baseline.py`
- Tests: `tests/test_machine_summary.py`, `tests/test_setup_script.py`, `tests/test_docs.py`
- User docs: `README.md`, `docs/getting-started.md`
- Feature docs: `specs/002-setup-menu-recommendation/`

## Dotfiles Constitution Gates

- Preserve `.template` source behavior and AGENTS.md symlink conventions.
- Do not edit protected files: `git/config`, `fish/fish_plugins`, `.gitignore`, `agents/CLAUDE.md.template`, or `agents/GEMINI.md.template`.
- Preserve explicit write approval, backup behavior, and protected/manual file handling.
- Use `uv` for Python validation commands.
- Do not add lock files or runtime dependencies.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm requirement quality and prepare the existing test surfaces for story work.

- [x] T001 Review `specs/002-setup-menu-recommendation/checklists/menu-recommendation.md` and update `specs/002-setup-menu-recommendation/spec.md` or `specs/002-setup-menu-recommendation/contracts/setup-menu.md` for any failed requirements-quality checklist item before coding. This is a governance gate, not a user-story implementation task. (completed as part of normal development)
- [x] T002 [P] Add shared assertion helpers for recommended option markers and reason text to `tests/test_machine_summary.py`. (completed as part of normal development)
- [x] T003 [P] Add shared setup-output assertion helpers for exactly one `[recommended]` marker to `tests/test_setup_script.py`. (completed as part of normal development)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish one recommendation model used by summary rendering and the shell menu.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Define a recommendation decision representation with option number, label, reason, and state category in `dotfiles_tools/machine_summary.py`.
- [x] T005 Implement machine-state extraction helpers for blockers, missing/unverified tools, status-audit failures, safe file actions, font actions, protected/manual items, auth guidance, and current state in `dotfiles_tools/machine_summary.py`.
- [x] T006 Implement recommendation priority ordering from `specs/002-setup-menu-recommendation/contracts/setup-menu.md` in `dotfiles_tools/machine_summary.py`.
- [x] T007 Add a machine summary CLI mode that emits the recommended option and reason for shell consumption in `dotfiles_tools/machine_summary.py`.

**Checkpoint**: Recommendation data can be derived without changing the existing interactive flow.

---

## Phase 3: User Story 1 - See The Recommended Next Step (Priority: P1) MVP

**Goal**: The machine setup menu clearly identifies the single recommended next step for the current audited machine state.

**Independent Test**: Run focused unit tests for recommendation states and setup-output tests proving exactly one visible recommendation appears with a matching reason.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Add unit tests for missing-tools, safe-changes, blockers-present, auth-guidance-only, manual-only, fully-current, and incomplete-status-data recommendation decisions in `tests/test_machine_summary.py`.
- [x] T009 [P] [US1] Add summary rendering tests for the plain-text `Recommended next step:` line and exact `[recommended]` marker behavior in `tests/test_machine_summary.py`.
- [x] T010 [P] [US1] Add setup wrapper output tests for option 1, option 2, option 3, option 4, option 5, and incomplete-status-data recommendation markers in `tests/test_setup_script.py`.

### Implementation for User Story 1

- [x] T011 [US1] Update `render_reports` so the machine summary includes the same recommended option and reason used by the menu in `dotfiles_tools/machine_summary.py`.
- [x] T012 [US1] Update `machine_menu_loop` to accept a recommended option and reason, print `Recommended next step:`, and mark only that option with `[recommended]` in `setup`.
- [x] T013 [US1] Replace `run_machine_menu_mode` and `run_machine_missing_tool_count` usage with the new recommendation output path in `setup`.
- [x] T014 [US1] Preserve existing non-recommended option behavior for choices 1 through 5 while using the new recommendation marker in `setup`.

**Checkpoint**: User Story 1 is complete when the menu always shows exactly one plain-text recommendation that agrees with the summary.

---

## Phase 4: User Story 2 - Follow The Fresh-Machine Flow (Priority: P1)

**Goal**: A fresh-machine session moves from tool install/update guidance to an updated apply recommendation without requiring the user to rerun `./setup`.

**Independent Test**: Run setup wrapper tests that simulate missing tools, declined tool install, and completed tool install, then verify the summary/menu refreshes in the same session.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T015 [P] [US2] Add a setup wrapper test proving declined option 1 tool install returns to a refreshed menu without writes in `tests/test_setup_script.py`.
- [x] T016 [P] [US2] Add a setup wrapper test proving completed option 1 tool install returns to a refreshed summary and updated recommendation in `tests/test_setup_script.py`.
- [x] T017 [P] [US2] Add a setup wrapper test for partial or unverified tool installation keeping option 1 recommended after refresh in `tests/test_setup_script.py`.

### Implementation for User Story 2

- [x] T018 [US2] Refactor `cmd_machine_setup` so each interactive iteration refreshes the machine summary and recommendation before rendering the menu in `setup`.
- [x] T019 [US2] Change option 1 handling so `run_machine_install_tools_with_confirm` returns to the machine menu after completion or cancellation instead of exiting the guided session in `setup`.
- [x] T020 [US2] Ensure option 3 full details and option 4 tool/sign-in guidance return to the refreshed menu while option 5 exits without writes in `setup`.

**Checkpoint**: User Story 2 is complete when the documented fresh-machine flow works in one `./setup` session.

---

## Phase 5: User Story 3 - Keep Documentation And Menu Behavior Aligned (Priority: P2)

**Goal**: README and getting-started examples match the implemented menu labels, recommendation wording, and fresh-machine transition.

**Independent Test**: Run documentation checks proving docs mention the stable option labels, `Recommended next step:`, and the option 1 to option 2 transition.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T021 [P] [US3] Add README documentation checks for stable option labels, `Recommended next step:`, and fresh-machine option 1 then option 2 flow in `tests/test_docs.py`.
- [ ] T022 [P] [US3] Add getting-started documentation checks for stable option labels, `Recommended next step:`, and refreshed-menu behavior in `tests/test_docs.py`.

### Implementation for User Story 3

- [x] T023 [US3] Update fresh-machine and configured-machine menu examples to include `Recommended next step:` and exact recommendation markers in `README.md`.
- [x] T024 [US3] Update first-time setup and ongoing maintenance menu examples to include `Recommended next step:` and refreshed-menu behavior in `docs/getting-started.md`.
- [ ] T025 [US3] Align `specs/002-setup-menu-recommendation/quickstart.md` with the final menu wording if implementation changes the planned recommendation text.

**Checkpoint**: User Story 3 is complete when docs and automated documentation checks match the implemented menu contract.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature and preserve repo safety rules.

- [x] T026 Run supplemental focused validation command `uv run python -m unittest tests.test_machine_summary tests.test_setup_script tests.test_docs` and fix failures in `dotfiles_tools/machine_summary.py`, `setup`, `tests/test_machine_summary.py`, `tests/test_setup_script.py`, or `tests/test_docs.py`.
- [x] T027 Run full validation command `uv run python -m unittest discover -s tests` and fix any regressions in `dotfiles_tools/`, `setup`, or `tests/`.
- [x] T028 Run quickstart review from `specs/002-setup-menu-recommendation/quickstart.md` and update `README.md`, `docs/getting-started.md`, or `specs/002-setup-menu-recommendation/quickstart.md` if observed wording differs.
- [x] T029 Review `git diff -- setup dotfiles_tools/machine_summary.py tests/test_machine_summary.py tests/test_setup_script.py tests/test_docs.py README.md docs/getting-started.md specs/002-setup-menu-recommendation` for protected-file edits, secrets, lock files, and unintended scope.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; complete before implementation work.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2; MVP and prerequisite for user-visible recommendation behavior.
- **User Story 2 (Phase 4)**: Depends on Phase 3 because it reuses the new recommendation rendering.
- **User Story 3 (Phase 5)**: Can begin after Phase 3 output wording stabilizes; docs should finish after Phase 4 refresh behavior is implemented.
- **Polish (Phase 6)**: Depends on all selected user stories.

### User Story Dependencies

- **US1 - See The Recommended Next Step (P1)**: Starts after foundational recommendation model; no dependency on US2 or US3.
- **US2 - Follow The Fresh-Machine Flow (P1)**: Depends on US1 recommendation rendering so refreshed menus use the same contract.
- **US3 - Keep Documentation And Menu Behavior Aligned (P2)**: Depends on final wording from US1 and final refreshed-menu behavior from US2.

### Within Each User Story

- Write the test tasks first and confirm they fail for missing behavior.
- Implement the smallest story-specific code path.
- Stop at each checkpoint and run the independent test command for that story.

### Parallel Opportunities

- T002 and T003 can run in parallel because they touch different test files.
- T008, T009, and T010 can run in parallel after Phase 2 because they cover separate test assertions.
- T015, T016, and T017 can run in parallel because they add separate wrapper scenarios.
- T021 and T022 can run in parallel because they add separate documentation checks.
- US3 documentation edits T023 and T024 can run in parallel after wording is stable.

---

## Parallel Example: User Story 1

```bash
Task: "T008 [P] [US1] Add unit tests for missing-tools, safe-changes, blockers-present, auth-guidance-only, manual-only, and fully-current recommendation decisions in tests/test_machine_summary.py"
Task: "T009 [P] [US1] Add summary rendering tests for the plain-text Recommended next step line and exact recommended marker behavior in tests/test_machine_summary.py"
Task: "T010 [P] [US1] Add setup wrapper output tests for option 1, option 2, option 3, option 4, and option 5 recommendation markers in tests/test_setup_script.py"
```

## Parallel Example: User Story 2

```bash
Task: "T015 [P] [US2] Add a setup wrapper test proving declined option 1 tool install returns to a refreshed menu without writes in tests/test_setup_script.py"
Task: "T016 [P] [US2] Add a setup wrapper test proving completed option 1 tool install returns to a refreshed summary and updated recommendation in tests/test_setup_script.py"
Task: "T017 [P] [US2] Add a setup wrapper test for partial or unverified tool installation keeping option 1 recommended after refresh in tests/test_setup_script.py"
```

## Parallel Example: User Story 3

```bash
Task: "T021 [P] [US3] Add README documentation checks for stable option labels, Recommended next step, and fresh-machine option 1 then option 2 flow in tests/test_docs.py"
Task: "T022 [P] [US3] Add getting-started documentation checks for stable option labels, Recommended next step, and refreshed-menu behavior in tests/test_docs.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tests and implementation.
3. Run focused tests for `tests.test_machine_summary` and the relevant setup-output tests.
4. Validate that every menu render has one visible recommendation that agrees with the summary.

### Incremental Delivery

1. Add the shared recommendation decision model.
2. Deliver US1 so the menu always highlights the right next step.
3. Deliver US2 so the fresh-machine session refreshes after tool install/update.
4. Deliver US3 so docs and documentation checks match the implemented behavior.
5. Run focused and full validation before merging.

### Parallel Team Strategy

With multiple implementers:

1. One person owns `dotfiles_tools/machine_summary.py` recommendation logic.
2. One person owns `setup` shell refresh behavior after the foundational model is available.
3. One person owns documentation and `tests/test_docs.py` after wording stabilizes.

## Notes

- `[P]` tasks target separate files or independent test scenarios.
- Story labels map tasks to the user stories in `spec.md`.
- Do not edit protected files.
- Do not add runtime dependencies or lock files.
- Keep all Python validation commands under `uv`.
