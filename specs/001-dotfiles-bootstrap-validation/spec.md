# Feature Specification: Dotfiles Bootstrap Validation

**Feature Branch**: `001-dotfiles-bootstrap-validation`
**Created**: 2026-05-01
**Status**: Draft
**Input**: User description: "Build a real validation/setup layer for 000-dotfiles so the repo has meaningful testable code, can configure new machines, verify drift on existing machines, initialize project agent docs, and generate legitimate coverage reports only after validation tests exist."

## Clarifications

### Session 2026-05-01

- Q: What report interface should `doctor`, `plan`, `apply`, and `init-project` expose for users and automation? → A: Human output by default, plus stable `--json` for every command report.
- Q: What identifier must users provide when opting into protected target writes? → A: Exact manifest entry ID.
- Q: What should apply do when one write operation fails after earlier operations succeeded? → A: Stop on first failed write; preserve completed changes/backups; report partial apply.
- Q: What command names are canonical for the user-facing CLI? → A: `doctor`, `plan`, `apply`, and `init-project`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Doctor Machine Readiness (Priority: P1)

A maintainer wants to inspect a new or existing computer against the dotfiles repository before changing anything, so they can understand missing files, drifted files, protected files, broken symlinks, invalid templates, and secret risks.

**Why this priority**: Safe `doctor` checks are the foundation for every other setup action and satisfy the dry-run-first constitution requirement.

**Independent Test**: Can be fully tested with a temporary home directory containing missing, current, drifted, and protected targets; the `doctor` command reports each state without modifying any file.

**Acceptance Scenarios**:

1. **Given** a target home directory with no dotfiles installed, **When** the user runs `doctor`, **Then** the report lists expected missing targets and protected/manual targets without writing to the home directory.
2. **Given** repository symlinks are intact, **When** the user runs `doctor`, **Then** the report marks the root and project agent-doc symlink conventions as valid.
3. **Given** a repository symlink is broken, **When** the user runs `doctor`, **Then** the report identifies the broken symlink and returns an unsuccessful status.
4. **Given** a template contains unresolved placeholders or invalid parseable structure, **When** the user runs `doctor`, **Then** the report identifies the affected source file and the reason.

---

### User Story 2 - Plan And Apply Machine Setup (Priority: P1)

A maintainer wants to plan exact setup operations, then explicitly apply safe changes with backups, so a new device can be configured without overwriting local customizations blindly.

**Why this priority**: The primary value of the feature is turning manual copy commands into a reliable setup workflow that works on both new and partially configured machines.

**Independent Test**: Can be fully tested with a temporary home directory; `plan` produces an operation list without writes, and `apply` creates directories, installs expected targets, and backs up drifted files before replacement.

**Acceptance Scenarios**:

1. **Given** a target home directory with missing install targets, **When** the user runs `plan`, **Then** the report lists all copy and directory-creation operations without writing files.
2. **Given** the user has approved apply and a target file is missing, **When** setup is applied, **Then** the target directory is created if needed and the file is installed.
3. **Given** the user has approved apply and a target file differs from the repository source, **When** setup is applied, **Then** the existing target is copied to the backup location before replacement.
4. **Given** the user has not approved apply, **When** setup is requested, **Then** the workflow refuses to write targets and explains the approval requirement.

---

### User Story 3 - Preserve Protected Manual Files (Priority: P1)

A maintainer wants identity-sensitive and manually curated files to remain protected by default, so setup never silently changes committer identity, fish plugin state, ignore rules, or symlinked agent templates.

**Why this priority**: Protected-file handling is a constitution gate and a safety boundary for using the tooling on real machines.

**Independent Test**: Can be fully tested by including protected targets in the manifest and verifying that `plan` reports them as manual by default and `apply` refuses them unless explicitly included.

**Acceptance Scenarios**:

1. **Given** a manifest entry is protected, **When** the user runs `plan` without explicit inclusion, **Then** the entry is reported as protected/manual and no write operation is planned.
2. **Given** a manifest entry is protected, **When** the user applies setup without explicit inclusion, **Then** the workflow refuses to overwrite that target.
3. **Given** the user explicitly includes a protected target by exact manifest entry ID and approves apply, **When** setup is applied, **Then** backup behavior still occurs before any differing target is replaced.

---

### User Story 4 - Initialize Project Agent Docs (Priority: P2)

A maintainer wants to initialize a separate project repository with agent instructions from these templates, so each project can start with an `AGENTS.md` source file and compatible `CLAUDE.md` and `GEMINI.md` symlinks.

**Why this priority**: Project-level initialization is a common reuse path for this dotfiles repo but is separate from configuring a machine.

**Independent Test**: Can be fully tested with a temporary project directory and a variables file; initialization creates expected files and symlinks, replaces placeholders, and fails when required placeholders remain unresolved.

**Acceptance Scenarios**:

1. **Given** a project directory and complete placeholder values, **When** project initialization is approved, **Then** the project receives `AGENTS.md` and `CLAUDE.md`/`GEMINI.md` symlinks that point to it.
2. **Given** optional Copilot instructions are requested, **When** project initialization is approved, **Then** the project receives the Copilot instruction file in the expected project location.
3. **Given** a required placeholder value is missing, **When** project initialization runs, **Then** it fails before completion and reports the unresolved placeholder.
4. **Given** target project files already exist and differ, **When** project initialization is approved, **Then** differing files are backed up before replacement.

---

### User Story 5 - Produce Legitimate Coverage Signals (Priority: P3)

A maintainer wants CI to run validation tests and produce a supported coverage report before uploading coverage data, so coverage gates are based on real validation code rather than placeholder metrics.

**Why this priority**: Coverage is valuable only after the validation layer exists; it should not block the core local bootstrap workflow.

**Independent Test**: Can be fully tested by running the validation test suite locally and confirming that a coverage report file is produced, and by reviewing that coverage upload is skipped when the required token is unavailable.

**Acceptance Scenarios**:

1. **Given** validation tests exist, **When** the automated validation workflow runs, **Then** it executes the tests and produces a supported coverage report file.
2. **Given** the Codacy token is configured, **When** the automated validation workflow completes successfully, **Then** the workflow attempts to upload the supported coverage report.
3. **Given** the Codacy token is absent, **When** the automated validation workflow completes successfully, **Then** coverage upload is skipped without failing the validation workflow.

### Edge Cases

- The repository manifest references a source path that does not exist.
- The repository manifest references an unsafe or empty target path.
- A target path exists as a directory when a file install is expected.
- A target file differs but the backup directory is missing or not writable.
- An apply operation fails after earlier operations have already completed.
- A target file is already current and must not be rewritten.
- A protected target is explicitly included but still differs from the repository source.
- A template contains placeholder examples that are allowed, while target-bound templates contain unresolved required placeholders that are not allowed.
- A source file contains a real-looking token, key, or credential.
- A parseable template format is invalid.
- A project initialization target already has real files where symlinks are expected.
- The automated validation workflow has no coverage token configured.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a `doctor` command that validates repository integrity, expected symlinks, manifest entries, template parseability, missing targets, drifted targets, protected/manual targets, unresolved placeholders, and secret-like content without writing files.
- **FR-002**: The system MUST provide a `plan` command that lists exact setup operations for a selected profile without writing to the target home directory.
- **FR-003**: The system MUST use a machine-readable manifest as the source of truth for installable source files, target paths, profiles, template status, and protected/manual behavior.
- **FR-004**: The system MUST classify target state as missing, current, drifted, protected/manual, invalid, or blocked with an explanation.
- **FR-005**: The system MUST require explicit apply approval before writing machine or project targets.
- **FR-006**: The system MUST create missing target directories during approved apply operations.
- **FR-007**: The system MUST back up existing differing target files before replacement during approved apply operations.
- **FR-008**: The system MUST refuse protected targets by default, including `git/config`, `fish/fish_plugins`, `.gitignore`, and symlinked agent templates.
- **FR-009**: The system MUST allow protected targets only when the user explicitly includes the exact protected target by manifest entry ID.
- **FR-010**: The system MUST preserve the root and project-level `AGENTS.md` symlink conventions during validation and project initialization.
- **FR-011**: The system MUST initialize project-level agent docs from `agents/AGENTS.md.template` with supplied placeholder values.
- **FR-012**: The system MUST create project-level `CLAUDE.md` and `GEMINI.md` symlinks pointing to `AGENTS.md`.
- **FR-013**: The system MUST optionally initialize GitHub Copilot instructions from the project template when requested.
- **FR-014**: The system MUST fail project initialization when required placeholders remain unresolved after variable substitution.
- **FR-015**: The system MUST validate structured templates that have supported parseable formats.
- **FR-016**: The system MUST reject real-looking secrets while allowing documented placeholder examples.
- **FR-017**: The system MUST provide a local validation test suite that exercises manifest validation, drift detection, apply behavior, project initialization, placeholder checks, parseability checks, symlink checks, and secret scanning without touching the user's real home directory.
- **FR-018**: The automated validation workflow MUST run the validation test suite and generate a supported coverage report file.
- **FR-019**: The automated validation workflow MUST upload coverage only when the required Codacy token is configured.
- **FR-020**: README bootstrap guidance MUST align with the manifest-backed setup workflow and clearly distinguish `doctor`, `plan`, `apply`, `init-project`, protected files, and backups.
- **FR-021**: Runtime agent guidance MUST document the validation and coverage commands once they exist.
- **FR-022**: `doctor`, `plan`, `apply`, and `init-project` reports MUST use human-readable output by default and MUST offer a stable JSON output mode for tests and automation.
- **FR-023**: If an approved apply operation fails after earlier writes have completed, the system MUST stop on the first failed write, preserve completed changes and backups, and report partial-apply status.
- **FR-024**: The user-facing CLI command names MUST be `doctor`, `plan`, `apply`, and `init-project`; documentation MUST use those names as canonical.

### Protected Entry Classification

Manifest entries SHOULD be classified as protected when automatic writes could
change local identity, expose secrets or generated artifacts, require external
or manual tool actions after installation, or break symlink/source-of-truth
invariants.

### Key Entities

- **Manifest**: The repository-owned source of truth describing setup profiles, source files, target paths, template handling, and protected/manual entries.
- **Manifest Entry**: A single installable or manual item with a stable unique ID, source path, target path, profile membership, protection status, and validation rules.
- **Target State**: The evaluated state of a target path, including whether it is missing, current, drifted, protected/manual, invalid, or blocked.
- **Operation Plan**: The ordered set of directory creation, copy, backup, skip, refusal, and partial-apply actions produced by `plan` or `apply` workflows.
- **Backup Record**: Evidence that an existing differing target was preserved before replacement, including original target and backup location.
- **Project Variables**: User-supplied values used to replace placeholders in project agent documentation templates.
- **Validation Report**: Human-readable default output and stable JSON output from `doctor`, `plan`, `apply`, `init-project`, or automated validation workflows.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On a temporary empty home directory, `doctor` reports all expected missing machine targets and performs zero writes.
- **SC-002**: On a temporary home directory, `plan` reports every planned directory creation, copy, skip, backup, and protected/manual refusal before apply is allowed.
- **SC-003**: On a temporary home directory, approved apply installs all non-protected expected machine targets and leaves protected targets untouched unless explicitly included.
- **SC-004**: When a drifted target exists, approved apply creates a backup before replacement in 100% of tested drift cases.
- **SC-005**: After approved apply on a temporary home directory, a second `doctor` run reports no drift for non-protected managed targets.
- **SC-006**: Project initialization creates `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` correctly in a temporary project directory in 100% of tested successful runs.
- **SC-007**: Project initialization fails in 100% of tested cases where required placeholders remain unresolved.
- **SC-008**: Secret scanning rejects real-looking token/key fixtures and allows documented placeholder examples in the validation suite.
- **SC-009**: The validation test suite can run without accessing the user's actual home directory.
- **SC-010**: The automated validation workflow produces a supported coverage report file after tests pass.
- **SC-011**: The automated validation workflow skips coverage upload without failure when the Codacy token is absent.
- **SC-012**: JSON reports expose stable status fields for `doctor`, `plan`, `apply`, and `init-project` in 100% of validation tests that assert report output.
- **SC-013**: Protected target apply tests require exact manifest entry IDs in 100% of successful protected-write cases.
- **SC-014**: Partial-apply failure tests stop at the first failed write and report completed, backed-up, and failed operations in 100% of tested cases.

## Assumptions

- The first feature increment covers one machine setup profile and one project initialization workflow.
- Protected files remain present in the manifest but are manual by default.
- Existing local auth state and the untracked `.codex` file are out of scope.
- Coverage gates are not enabled as required branch checks until a successful coverage upload is visible on a pull request.
- The README can describe the manifest-backed workflow even if examples are not literally generated from the manifest in the first increment.
