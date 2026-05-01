# Tasks: Dotfiles Bootstrap Validation

**Input**: Design documents from `/specs/001-dotfiles-bootstrap-validation/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: Required by the feature specification and constitution. Write tests before implementation for each story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the package, test layout, manifest, and workflow paths used by all stories.

- [X] T001 Create Python package entry files in `dotfiles_tools/__init__.py`, `dotfiles_tools/__main__.py`, and `dotfiles_tools/cli.py`
- [X] T002 Create shared test helpers and fixture utilities in `tests/helpers.py`
- [X] T003 Create root manifest with current repo entries, protected IDs, profiles, and project-init defaults in `dotfiles-manifest.json`
- [X] T004 Create placeholder module files for planned components in `dotfiles_tools/manifest.py`, `dotfiles_tools/reports.py`, `dotfiles_tools/templates.py`, `dotfiles_tools/placeholders.py`, `dotfiles_tools/secrets.py`, `dotfiles_tools/doctor.py`, `dotfiles_tools/installer.py`, `dotfiles_tools/backups.py`, and `dotfiles_tools/project_init.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared validation, rendering, parsing, and CLI foundations that all user stories depend on.

**CRITICAL**: No user story implementation can begin until this phase is complete.

### Tests for Foundational Components

- [X] T005 [P] Add manifest validation tests for source paths, target paths, duplicate IDs, profile references, and protected manual reasons in `tests/test_manifest.py`
- [X] T006 [P] Add template parseability and placeholder detection tests for JSON, TOML, unresolved placeholders, and allowed examples in `tests/test_templates.py`
- [X] T007 [P] Add secret scanning tests for real-looking token fixtures and documented placeholder examples in `tests/test_secrets.py`
- [X] T008 [P] Add stable JSON and human report rendering tests for common report fields and status values in `tests/test_cli_reports.py`

### Implementation for Foundational Components

- [X] T009 Implement manifest loading, dataclasses, path safety checks, profile validation, and protected-entry validation in `dotfiles_tools/manifest.py`
- [X] T010 Implement placeholder discovery, variable substitution, unresolved-placeholder errors, and allowed-example handling in `dotfiles_tools/placeholders.py`
- [X] T011 Implement secret-like content scanning with placeholder allowlist behavior in `dotfiles_tools/secrets.py`
- [X] T012 Implement JSON and TOML parseability checks plus source rendering helpers in `dotfiles_tools/templates.py`
- [X] T013 Implement report objects, summary counts, stable JSON rendering, and human-readable rendering in `dotfiles_tools/reports.py`
- [X] T014 Implement argparse command skeleton, common `--repo` and `--json` options, exit-status handling, and command dispatch in `dotfiles_tools/cli.py`
- [X] T015 Wire module execution to CLI dispatch in `dotfiles_tools/__main__.py`

**Checkpoint**: Manifest, template, placeholder, secret, report, and CLI skeleton tests pass independently.

---

## Phase 3: User Story 1 - Doctor Machine Readiness (Priority: P1) MVP

**Goal**: A maintainer can run `doctor` against a target home directory and receive a non-writing readiness report.

**Independent Test**: With only foundational components plus this phase, `doctor` can evaluate a temporary home directory for missing, current, drifted, protected, invalid, and symlink states without writes.

### Tests for User Story 1

- [X] T016 [P] [US1] Add `doctor` tests for empty temp home missing targets and zero writes in `tests/test_doctor.py`
- [X] T017 [P] [US1] Add `doctor` tests for intact and broken root/project symlink conventions in `tests/test_doctor_symlinks.py`
- [X] T018 [P] [US1] Add `doctor` JSON report tests for missing, current, drifted, protected, invalid, and blocked target states in `tests/test_doctor_reports.py`

### Implementation for User Story 1

- [X] T019 [US1] Implement repository integrity, root symlink, and project template symlink checks in `dotfiles_tools/doctor.py`
- [X] T020 [US1] Implement target state evaluation for missing, current, drifted, protected, invalid, and blocked states in `dotfiles_tools/doctor.py`
- [X] T021 [US1] Implement parseability, placeholder, and secret validation integration for `doctor` in `dotfiles_tools/doctor.py`
- [X] T022 [US1] Wire `doctor --repo PATH --home PATH --profile ID --json` through argparse in `dotfiles_tools/cli.py`
- [X] T023 [US1] Add human-readable `doctor` report sections for repo checks, target states, and errors in `dotfiles_tools/reports.py`

**Checkpoint**: `uv run python -m dotfiles_tools doctor --repo . --home <temp>` works and performs zero writes.

---

## Phase 4: User Story 2 - Plan And Apply Machine Setup (Priority: P1)

**Goal**: A maintainer can preview exact operations with `plan` and apply non-protected machine setup with backups and explicit approval.

**Independent Test**: With foundational components plus this phase, `plan` emits operations without writes, and `apply --yes` installs non-protected entries into a temporary home with backups for drifted targets.

### Tests for User Story 2

- [X] T024 [P] [US2] Add `plan` tests for directory creation, copy, skip, backup, and refusal operation ordering in `tests/test_plan_operations.py`
- [X] T025 [P] [US2] Add `apply` tests for missing target installation and directory creation in `tests/test_apply_install.py`
- [X] T026 [P] [US2] Add `apply` tests for drifted target backup before replacement and current target no-op behavior in `tests/test_apply_backups.py`
- [X] T027 [P] [US2] Add `apply` tests for missing `--yes` refusal and partial-apply stop-on-first-failure behavior in `tests/test_apply_failures.py`

### Implementation for User Story 2

- [X] T028 [US2] Implement operation planning for mkdir, copy, symlink, backup, skip, and refuse operations in `dotfiles_tools/installer.py`
- [X] T029 [US2] Implement backup target naming, backup directory validation, and backup copy behavior in `dotfiles_tools/backups.py`
- [X] T030 [US2] Implement approved apply execution, `--yes` gating, idempotent current-target skipping, and stop-on-first-failure partial status in `dotfiles_tools/installer.py`
- [X] T031 [US2] Wire `plan --repo PATH --home PATH --profile ID --include-protected ID --json` through argparse in `dotfiles_tools/cli.py`
- [X] T032 [US2] Wire `apply --repo PATH --home PATH --profile ID --backup-dir PATH --yes --include-protected ID --json` through argparse in `dotfiles_tools/cli.py`
- [X] T033 [US2] Add operations, backups, failed operation, and partial status rendering in `dotfiles_tools/reports.py`

**Checkpoint**: `plan` writes nothing, and `apply --yes` installs non-protected manifest entries into a temporary home with backups for drift.

---

## Phase 5: User Story 3 - Preserve Protected Manual Files (Priority: P1)

**Goal**: Protected identity/plugin/ignore/symlink-template files remain manual by default and can only be included by exact manifest entry ID.

**Independent Test**: With foundational components plus operation planning/apply, protected entries are reported but not written unless included by exact manifest ID.

### Tests for User Story 3

- [X] T034 [P] [US3] Add protected-entry manifest fixture tests for `git.config`, `fish.plugins`, `repo.gitignore`, `agents.claude-template`, and `agents.gemini-template` in `tests/test_protected_manifest.py`
- [X] T035 [P] [US3] Add protected `plan` tests proving protected entries produce no write operations without exact ID inclusion in `tests/test_protected_plan.py`
- [X] T036 [P] [US3] Add protected `apply` tests proving exact manifest entry IDs are required for successful protected writes in `tests/test_protected_apply.py`

### Implementation for User Story 3

- [X] T037 [US3] Verify and refine protected manifest metadata and manual reasons for identity, plugin, ignore, and symlink-template files in `dotfiles-manifest.json`
- [X] T038 [US3] Enforce exact manifest entry ID validation for `--include-protected` in `dotfiles_tools/manifest.py`
- [X] T039 [US3] Enforce protected skip/refuse behavior during operation planning and apply execution in `dotfiles_tools/installer.py`
- [X] T040 [US3] Include protected entry IDs and manual reasons in human and JSON report output in `dotfiles_tools/reports.py`

**Checkpoint**: Protected targets are visible in reports but cannot be written unless named by exact manifest entry ID.

---

## Phase 6: User Story 4 - Initialize Project Agent Docs (Priority: P2)

**Goal**: A maintainer can initialize project-level agent docs from this repo with placeholder replacement, symlinks, optional Copilot instructions, and backup behavior.

**Independent Test**: With foundational components plus this phase, `init-project` succeeds in a temporary project with complete variables and fails when placeholders remain unresolved.

### Tests for User Story 4

- [X] T041 [P] [US4] Add `init-project` success tests for `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` symlinks in `tests/test_project_init_success.py`
- [X] T042 [P] [US4] Add `init-project` unresolved placeholder failure tests using variables JSON fixtures in `tests/test_project_init_placeholders.py`
- [X] T043 [P] [US4] Add `init-project` backup and optional Copilot instruction tests in `tests/test_project_init_backups.py`
- [X] T044 [P] [US4] Add `init-project` JSON report tests for written files, symlinks, backups, and unresolved placeholders in `tests/test_project_init_reports.py`

### Implementation for User Story 4

- [X] T045 [US4] Implement project variable JSON loading and placeholder rendering in `dotfiles_tools/project_init.py`
- [X] T046 [US4] Implement project `AGENTS.md` write, `CLAUDE.md` and `GEMINI.md` symlink creation, and backup-before-replace behavior in `dotfiles_tools/project_init.py`
- [X] T047 [US4] Implement optional `.github/copilot-instructions.md` initialization and parent directory creation in `dotfiles_tools/project_init.py`
- [X] T048 [US4] Wire `init-project --repo PATH --project PATH --vars PATH --backup-dir PATH --yes --copilot --json` through argparse in `dotfiles_tools/cli.py`
- [X] T049 [US4] Add project initialization fields and symlink details to report rendering in `dotfiles_tools/reports.py`

**Checkpoint**: `init-project` can initialize a temporary project and refuses unresolved required placeholders.

---

## Phase 7: User Story 5 - Produce Legitimate Coverage Signals (Priority: P3)

**Goal**: CI runs real validation tests, generates `coverage.xml`, and uploads coverage only when the Codacy token is configured.

**Independent Test**: With previous validation code and tests in place, the workflow can be inspected and local coverage commands produce `coverage.xml`.

### Tests for User Story 5

- [X] T050 [P] [US5] Add workflow text validation tests for unittest execution, `coverage.xml` generation, and token-gated Codacy upload in `tests/test_workflow.py`
- [X] T051 [P] [US5] Add README command validation tests for canonical `doctor`, `plan`, `apply`, `init-project`, and coverage commands in `tests/test_docs.py`

### Implementation for User Story 5

- [X] T052 [US5] Create GitHub Actions workflow with uv setup, unittest execution, coverage XML generation, and token-gated Codacy upload in `.github/workflows/dotfiles-validation.yml`
- [X] T053 [US5] Update machine bootstrap documentation to use manifest-backed `doctor`, `plan`, and `apply` commands in `README.md`
- [X] T054 [US5] Update project initialization documentation to use `init-project` and placeholder variables in `README.md`
- [X] T055 [US5] Update validation and coverage documentation with uv-based test and coverage commands in `README.md`
- [X] T056 [US5] Update runtime agent guidance with uv-based validation commands and no-lock-file constraints in `AGENTS.md`

**Checkpoint**: Local coverage produces `coverage.xml`, and workflow upload is skipped safely without `CODACY_COVERAGE_API_TOKEN`.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validate the full feature, keep docs aligned, and prepare for implementation closeout.

- [X] T057 [P] Ensure all public CLI examples in `specs/001-dotfiles-bootstrap-validation/quickstart.md` match README and implemented arguments in `dotfiles_tools/cli.py`
- [X] T058 [P] Ensure manifest examples and protected IDs in `specs/001-dotfiles-bootstrap-validation/contracts/manifest.schema.json`, `dotfiles-manifest.json`, and `README.md` use the same names
- [X] T059 Run `uv run python -m unittest discover -s tests` and fix failures in `tests/`
- [X] T060 Run `uv run --with coverage coverage run -m unittest discover -s tests` and `uv run --with coverage coverage xml`, then verify `coverage.xml`
- [X] T061 Run `uv run python -m dotfiles_tools doctor --repo . --home "$(mktemp -d)" --json` and verify report behavior against `specs/001-dotfiles-bootstrap-validation/quickstart.md`
- [X] T062 Run `uv run python -m dotfiles_tools plan --repo . --home "$(mktemp -d)" --profile machine --json` and verify operation behavior against `specs/001-dotfiles-bootstrap-validation/quickstart.md`
- [X] T063 Review `git diff -- AGENTS.md README.md dotfiles-manifest.json dotfiles_tools tests .github/workflows/dotfiles-validation.yml specs/001-dotfiles-bootstrap-validation/tasks.md` for secrets, protected-file edits, and unintended scope

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user stories.
- **US1 Doctor (Phase 3)**: Depends on Phase 2; MVP slice.
- **US2 Plan/Apply (Phase 4)**: Depends on Phase 2; can start after foundational modules exist, but benefits from US1 target-state behavior.
- **US3 Protected Files (Phase 5)**: Depends on Phase 2 and uses US2 planner/apply enforcement.
- **US4 Init Project (Phase 6)**: Depends on Phase 2; independent of machine apply.
- **US5 Coverage (Phase 7)**: Depends on meaningful tests from previous phases.
- **Polish (Phase 8)**: Depends on all selected user stories.

### User Story Dependencies

- **US1 (P1)**: MVP; can be delivered after foundational work.
- **US2 (P1)**: Can be delivered after foundational work and shares target-state concepts with US1.
- **US3 (P1)**: Requires US2 operation planning/apply paths for enforcement.
- **US4 (P2)**: Can be delivered after foundational work independently of machine setup.
- **US5 (P3)**: Requires real tests from US1-US4 before coverage is meaningful.

### Within Each User Story

- Tests must be written first and fail for the missing behavior.
- Implement shared models/helpers before command wiring.
- Wire CLI arguments only after command behavior exists.
- Validate JSON reports for every command before updating docs.

## Parallel Opportunities

- T005-T008 can run in parallel because they target separate test files.
- T016-T018 can run in parallel while implementing US1 behavior afterward.
- T024-T027 can run in parallel as independent installer behavior tests.
- T034-T036 can run in parallel because they target separate protected-behavior test files.
- T041-T044 can run in parallel because they target separate project-init test files.
- T050-T051 can run in parallel because they target separate test files.
- T057-T058 can run in parallel during polish because they inspect different documentation/contract alignment surfaces.

## Parallel Example: User Story 1

```text
Task: "T016 [US1] Add doctor tests for empty temp home missing targets and zero writes in tests/test_doctor.py"
Task: "T017 [US1] Add doctor tests for intact and broken root/project symlink conventions in tests/test_doctor_symlinks.py"
Task: "T018 [US1] Add doctor JSON report tests for missing, current, drifted, protected, invalid, and blocked target states in tests/test_doctor_reports.py"
```

## Parallel Example: User Story 4

```text
Task: "T041 [US4] Add init-project success tests for AGENTS.md, CLAUDE.md, and GEMINI.md symlinks in tests/test_project_init_success.py"
Task: "T042 [US4] Add init-project unresolved placeholder failure tests using variables JSON fixtures in tests/test_project_init_placeholders.py"
Task: "T043 [US4] Add init-project backup and optional Copilot instruction tests in tests/test_project_init_backups.py"
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1 Doctor.
4. Validate `doctor` against a temporary home and review JSON report output.

### Incremental Delivery

1. Add `doctor` for safe non-writing audits.
2. Add `plan` and `apply` for manifest-backed machine setup.
3. Enforce protected-file opt-in by manifest entry ID.
4. Add `init-project` for project agent docs.
5. Add coverage workflow only after validation tests exist.

### Final Validation

Run the uv-based unittest and coverage commands from quickstart, inspect
`coverage.xml`, and review the diff for secrets and protected-file changes
before publishing.
