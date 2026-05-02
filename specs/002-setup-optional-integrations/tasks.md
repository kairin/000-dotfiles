# Tasks: Optional Setup Integrations Menu

**Input**: Design documents from `/specs/002-setup-optional-integrations/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by FR-016 and the dotfiles constitution because this feature touches setup behavior, generated project guidance, local environment files, and secret-safety boundaries.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Review requirement quality and prepare the existing setup/docs test surfaces.

- [X] T001 Review `specs/002-setup-optional-integrations/checklists/requirements.md` and `specs/002-setup-optional-integrations/checklists/optional-integrations.md`; update `specs/002-setup-optional-integrations/spec.md` for any failed requirements-quality item before coding.
- [X] T002 [P] Inspect current project menu tests in `tests/test_setup_script.py` and identify assertions that must change from direct Codacy menu placement to optional integrations submenu placement.
- [X] T003 [P] Inspect generated guidance checks in `tests/test_project_init_success.py` and docs checks in `tests/test_docs.py` for existing Codacy variable coverage.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared setup-script helpers and safe file contracts used by all story work.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Add or refine reusable menu helper functions in `setup` for opening a project optional integrations submenu without duplicating empty-project and existing-project menu loops.
- [X] T005 Add or refine reusable Codacy environment helper functions in `setup` for deriving repository identity, normalizing token storage names, previewing planned writes, backing up existing environment files, preserving managed sections, writing token files after confirmation, and avoiding token output.
- [X] T006 [P] Add shared fixture/helper coverage in `tests/test_setup_script.py` for creating clean projects, fake homes, fake `uv`, and reusable Codacy token input without exposing secret values in assertions.
- [X] T007 [P] Add shared documentation assertions in `tests/test_docs.py` for the optional integrations terminology and Codacy environment variable list.

**Checkpoint**: Setup-script helper surface and shared test fixtures are ready.

---

## Phase 3: User Story 1 - Discover Optional Project Integrations (Priority: P1) MVP

**Goal**: The project setup flow exposes one generic optional integrations submenu entry while keeping the top-level menu focused on core setup actions.

**Independent Test**: Run `./setup /path/to/empty-project` and `./setup /path/to/existing-project`; verify each top-level menu has one generic optional integrations entry, that Codacy is not exposed directly at top level, and that cancelling/backing out causes no Codacy-specific writes.

### Tests for User Story 1

- [X] T008 [P] [US1] Add empty-project menu contract test in `tests/test_setup_script.py` for the generic optional integrations top-level entry, absence of a direct Codacy top-level item, unchanged core bootstrap choices, and recommendation/highlight behavior that continues to point at required core setup rather than unconfigured optional integrations.
- [X] T009 [P] [US1] Add existing-project menu contract test in `tests/test_setup_script.py` for the generic optional integrations top-level entry, absence of a direct Codacy top-level item, unchanged verify/repair/Copilot/metadata choices, and recommendation/highlight behavior that continues to point at required core setup rather than unconfigured optional integrations.
- [X] T010 [P] [US1] Add optional integrations submenu Back/EOF test in `tests/test_setup_script.py` proving Back returns to project setup and EOF/empty exits without creating `.envrc`, `.envrc.local`, backups, or `~/.codacy/` token files.

### Implementation for User Story 1

- [X] T011 [US1] Update `empty_project_menu` in `setup` to replace the direct Codacy option with a generic optional integrations/API submenu entry while preserving bootstrap, Copilot, metadata, and exit choices.
- [X] T012 [US1] Update `existing_project_menu` in `setup` to replace the direct Codacy option with a generic optional integrations/API submenu entry while preserving verify, repair, Copilot, metadata, and exit choices.
- [X] T013 [US1] Implement the optional integrations submenu in `setup` with `Manage Codacy API access` and `Back to project setup` choices.
- [X] T014 [US1] Ensure optional integrations Back behavior in `setup` returns to the project setup menu and EOF/empty input exits cleanly without Codacy-specific writes.

**Checkpoint**: User Story 1 is independently testable and delivers the MVP menu shape.

---

## Phase 4: User Story 2 - Manage Codacy API Access From The Optional Menu (Priority: P2)

**Goal**: Codacy API setup is reachable from the optional integrations submenu and supports repository-token and account-token modes with safe external token storage.

**Independent Test**: From the optional integrations submenu, choose Codacy API management, complete repository-token mode and account-token mode separately, and verify variables, metadata, storage locations, cancellation, and output secrecy.

### Tests for User Story 2

- [X] T015 [P] [US2] Add repository-token Codacy submenu test in `tests/test_setup_script.py` covering `CODACY_PROJECT_TOKEN`, repository metadata variables, external token file path, `.envrc` loader, `.envrc.local` bridge, file permissions, and absence of token value in output.
- [X] T016 [P] [US2] Add account-token Codacy submenu test in `tests/test_setup_script.py` covering `CODACY_API_TOKEN`, repository metadata variables, external account-token file path, `.envrc` loader, `.envrc.local` bridge, file permissions, and absence of token value in output.
- [X] T017 [P] [US2] Add Codacy mode-cancel test in `tests/test_setup_script.py` proving cancellation before a credential mode returns to the optional integrations submenu and causes no Codacy-specific file changes.
- [X] T018 [P] [US2] Add Codacy identity fallback test in `tests/test_setup_script.py` covering projects without a parseable GitHub remote and requiring user-provided owner/repository values.
- [X] T019 [P] [US2] Add Codacy preview/final-confirmation cancellation test in `tests/test_setup_script.py` proving declined confirmation creates no token files, project environment files, or backups.
- [X] T020 [P] [US2] Add blank-token-without-existing-file test in `tests/test_setup_script.py` proving no active Codacy token export points to a missing token file and user guidance explains that a token is required.
- [X] T021 [P] [US2] Add existing-env-file backup test in `tests/test_setup_script.py` proving modified `.envrc` and `.envrc.local` files are backed up before content changes.

### Implementation for User Story 2

- [X] T022 [US2] Wire `Manage Codacy API access` from the optional integrations submenu in `setup` to the existing Codacy credential mode selection flow.
- [X] T023 [US2] Update `configure_codacy_env` in `setup` so credential mode cancellation returns to the optional integrations submenu without writing token, `.envrc`, or `.envrc.local` files.
- [X] T024 [US2] Add token-free preview and explicit final confirmation in `setup` before writing Codacy token files, `.envrc`, or `.envrc.local`.
- [X] T025 [US2] Update repository-token handling in `setup` to preserve the contract for `CODACY_PROJECT_TOKEN`, metadata variables, external project-token storage, token-free output, preview, confirmation, and backup behavior.
- [X] T026 [US2] Update account-token handling in `setup` to preserve the contract for `CODACY_API_TOKEN`, metadata variables, external account-token storage, token-free output, preview, confirmation, and backup behavior.
- [X] T027 [US2] Update repository identity prompt handling in `setup` so detected values can be confirmed and missing/unparseable values can be supplied without corrupting captured variable values.
- [X] T028 [US2] Ensure `.envrc` and `.envrc.local` writes in `setup` preserve non-managed user content, back up existing files before mutation, and set intended permissions after successful setup.
- [X] T029 [US2] Update blank-token handling in `setup` so missing token files do not produce active Codacy token exports and the user receives token-required guidance.

**Checkpoint**: Codacy API management works from the optional submenu with both credential modes.

---

## Phase 5: User Story 3 - Keep Secret Handling Safe And Agent-Discoverable (Priority: P3)

**Goal**: Generated project guidance and docs explain safe Codacy variable discovery while preventing token values from being read, printed, or committed.

**Independent Test**: Generate project agent docs, inspect docs and project files, and verify Codacy variable names and safety rules are present while token values remain outside repository files and output.

### Tests for User Story 3

- [X] T030 [P] [US3] Add generated agent guidance test in `tests/test_project_init_success.py` for optional integrations wording, supported Codacy variables, and the rule not to read or print local secret files.
- [X] T031 [P] [US3] Add docs coverage in `tests/test_docs.py` for the project setup optional integrations flow, Codacy token modes, external `~/.codacy/` storage, preview/confirmation, backup behavior, and shell activation guidance.
- [X] T032 [P] [US3] Add idempotent managed-section test in `tests/test_setup_script.py` proving repeated Codacy setup leaves exactly one managed Codacy section and preserves unrelated `.envrc.local` content.

### Implementation for User Story 3

- [X] T033 [US3] Update `agents/AGENTS.md.template` so generated project guidance describes optional Codacy variables, safe presence checks, and the prohibition on reading or printing local secret files.
- [X] T034 [US3] Update `docs/getting-started.md` to show the optional integrations submenu path for Codacy API access, preview/final-confirmation behavior, backup behavior, and the expected activation step.
- [X] T035 [US3] Update `docs/codacy-coverage-rollout.md` to align the local agent/API access instructions with the optional integrations submenu, both credential modes, preview/confirmation, and backups.
- [X] T036 [US3] Update `fish/env.fish.template` comments to point users to the project optional integrations menu instead of suggesting global token exports as the primary path.

**Checkpoint**: Agents and users can discover the safe Codacy access pattern without exposing token values.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and Spec Kit artifact alignment.

- [X] T037 Run syntax validation `bash -n setup` and fix any shell syntax failures in `setup`.
- [X] T038 Run focused validation `uv run python -m unittest tests.test_setup_script tests.test_docs tests.test_project_init_success` and fix failures in `setup`, `tests/test_setup_script.py`, `tests/test_docs.py`, `tests/test_project_init_success.py`, `agents/AGENTS.md.template`, `docs/getting-started.md`, `docs/codacy-coverage-rollout.md`, or `fish/env.fish.template`.
- [X] T039 Run full validation `uv run python -m unittest discover -s tests` and fix any regressions in `setup`, `dotfiles_tools/`, `tests/`, or docs/templates.
- [X] T040 [P] Review `git diff --check -- setup agents/AGENTS.md.template fish/env.fish.template docs/ tests/ specs/002-setup-optional-integrations/` output and fix whitespace or conflict-marker issues in changed files.
- [X] T041 [P] Review `specs/002-setup-optional-integrations/quickstart.md` against implemented behavior and update it for the optional integrations path, preview/final-confirmation step, backup expectations, and activation checks if the user-facing flow changed during implementation.
- [X] T042 Ensure `.coverage` or other generated local artifacts remain untracked by staging only intentional files in `.specify/`, `specs/002-setup-optional-integrations/`, `setup`, `agents/AGENTS.md.template`, `fish/env.fish.template`, `docs/`, and `tests/`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Phase 1 completion and blocks user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2; provides MVP menu shape.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because Codacy must be reachable from the optional submenu.
- **User Story 3 (Phase 5)**: Can start after Phase 2 for docs/template updates, but final wording should align with User Story 1 and User Story 2 labels.
- **Polish (Phase 6)**: Depends on selected stories being complete.

### User Story Dependencies

- **US1**: No dependency on US2 or US3; should be delivered first.
- **US2**: Depends on US1 submenu placement.
- **US3**: Depends on the final user-facing labels from US1 and the Codacy modes from US2.

### Parallel Opportunities

- T002 and T003 can run in parallel.
- T006 and T007 can run in parallel after T004/T005 direction is understood.
- T008, T009, and T010 can be written in parallel because they cover separate menu scenarios in `tests/test_setup_script.py`; coordinate edits to avoid same-line conflicts.
- T015, T016, T017, T018, T019, T020, and T021 can be designed in parallel because they cover separate Codacy scenarios; coordinate final placement in `tests/test_setup_script.py`.
- T030, T031, and T032 can run in parallel because they touch different validation concerns.
- T040 and T041 can run in parallel after implementation validation.

---

## Parallel Example: User Story 1

```text
Task: "Add empty-project menu contract test in tests/test_setup_script.py"
Task: "Add existing-project menu contract test in tests/test_setup_script.py"
Task: "Add optional integrations submenu cancellation test in tests/test_setup_script.py"
```

## Parallel Example: User Story 2

```text
Task: "Add repository-token Codacy submenu test in tests/test_setup_script.py"
Task: "Add account-token Codacy submenu test in tests/test_setup_script.py"
Task: "Add Codacy mode-cancel test in tests/test_setup_script.py"
Task: "Add Codacy identity fallback test in tests/test_setup_script.py"
Task: "Add Codacy preview/final-confirmation cancellation test in tests/test_setup_script.py"
Task: "Add blank-token-without-existing-file test in tests/test_setup_script.py"
Task: "Add existing-env-file backup test in tests/test_setup_script.py"
```

## Parallel Example: User Story 3

```text
Task: "Add generated agent guidance test in tests/test_project_init_success.py"
Task: "Add docs coverage in tests/test_docs.py"
Task: "Add idempotent managed-section test in tests/test_setup_script.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete User Story 1 tests and implementation.
3. Validate that top-level project menus use one generic optional integrations entry and that Codacy is no longer top-level.
4. Stop and review before adding Codacy mode behavior if a smaller MVP is desired.

### Incremental Delivery

1. Deliver US1 to establish the correct menu hierarchy.
2. Deliver US2 to move Codacy API management under that hierarchy while preserving safe token behavior.
3. Deliver US3 to align generated guidance and docs with the final flow.
4. Run Phase 6 validation before merge.

### Notes

- `[P]` tasks indicate different files or separable scenarios; when multiple tasks touch `tests/test_setup_script.py`, coordinate line placement to avoid conflicts.
- Story labels map tasks back to the prioritized user stories in [spec.md](./spec.md).
- Do not add dependencies or lock files for this feature.
- Do not stage `.coverage` or token files.
