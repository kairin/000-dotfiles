<!--
Sync Impact Report
Version change: template -> 1.0.0
Modified principles:
- Placeholder Principle 1 -> Template Source of Truth
- Placeholder Principle 2 -> Secret-Free and Identity-Safe
- Placeholder Principle 3 -> Protected Files Require Explicit Per-File Approval
- Placeholder Principle 4 -> Reproducible Bootstrap
- Placeholder Principle 5 -> Validation Before Coverage
Added sections:
- Operational Constraints
- Spec Kit Workflow Gates
Removed sections:
- Placeholder section names and example comments from the template
Templates requiring updates:
- .specify/templates/plan-template.md: updated
- .specify/templates/spec-template.md: updated
- .specify/templates/tasks-template.md: updated
- .specify/templates/commands/*.md: not present in this installation
Runtime guidance:
- AGENTS.md: updated
Follow-up TODOs:
- None
-->
# dotfiles Constitution

## Core Principles

### I. Template Source of Truth
Files ending in `.template` are copy-and-customize sources. They MUST NOT be
executed, sourced, or treated as live configuration from this repository path.
Any placeholder using the `{{UPPER_SNAKE_CASE}}` form MUST be replaced before
the target file is used. Root-level `CLAUDE.md` and `GEMINI.md`, and the
project-level `agents/CLAUDE.md.template` and `agents/GEMINI.md.template`,
MUST preserve the `AGENTS.md` symlink source-of-truth pattern.

Rationale: this repository stores reusable templates, not active machine state.
Keeping one agent-doc source per scope prevents conflicting instructions.

### II. Secret-Free and Identity-Safe
No credentials, tokens, private authentication files, API keys, or secret-like
values MAY be introduced into tracked files. Auth state MUST remain outside the
repository and covered by ignore rules. Changes that affect committer identity,
global tool identity, or machine-wide authentication behavior MUST be explicit
and reviewable.

Rationale: dotfiles are copied across machines, so a single accidental secret or
identity edit can leak broadly or alter unrelated Git/tool operations.

### III. Protected Files Require Explicit Per-File Approval
The files `git/config`, `fish/fish_plugins`, `.gitignore`,
`agents/CLAUDE.md.template`, and `agents/GEMINI.md.template` are protected.
They MUST NOT be modified unless the user explicitly names the exact file and
authorizes the change. Automated setup MUST treat protected files as manual by
default, and any opt-in mechanism MUST name the protected target being included.

Rationale: these files affect identity, plugin management, secret exposure, or
the repository's single-source symlink convention.

### IV. Reproducible Bootstrap
Machine and project setup MUST be manifest-driven, dry-run capable, and
idempotent. Audit and plan commands MUST report intended operations without
writing. Apply commands MUST require explicit approval such as `--yes` before
writing user machine or project targets, and MUST back up existing differing
targets before replacement. Reports MUST distinguish missing, current, drifted,
and protected/manual targets.

Rationale: the same repository must be safe to use on new devices and on
machines that already contain local customizations.

### V. Validation Before Coverage
Coverage reporting is valid only for real validation or setup code in this
repository. CI MUST run tests for that code and generate `coverage.xml` before
any Codacy coverage upload. The coverage upload MUST be skipped safely when the
required Codacy token is absent. Tests for bootstrap tooling MUST cover manifest
validation, drift detection, apply behavior, project initialization, placeholder
resolution, and secret scanning.

Rationale: coverage without meaningful executable validation creates false
confidence and weakens branch-protection signals.

## Operational Constraints

- Python tooling SHOULD use the standard library unless a runtime dependency is
  justified in the plan.
- All Python-related commands, dependency management, and developer workflows
  MUST use `uv` when project tooling or dependencies are involved.
- Lock files MUST NOT be added unless runtime dependencies are introduced and
  the plan explains why a lock file is needed.
- Automated setup MUST NOT overwrite user machine files without explicit apply
  approval and backup behavior.
- The bootstrap manifest is the source of truth for machine target paths and
  install behavior.
- README bootstrap examples MUST align with the manifest-backed behavior.

## Spec Kit Workflow Gates

- Specifications for setup or validation features MUST define protected-file
  behavior, failure modes, dry-run behavior, apply behavior, and backup
  expectations.
- Implementation plans MUST include validation strategy, rollback or backup
  behavior, uv command usage, and any justified dependency or lock-file changes.
- Task lists MUST include tests for manifest validation, drift detection, apply
  behavior, project initialization, placeholder checks, and secret scanning
  when those surfaces are in scope.
- A feature MUST NOT proceed to implementation with unresolved constitution
  conflicts unless the plan records a justified exception and a simpler
  alternative that was rejected.

## Governance

This constitution supersedes conflicting repo practices, generated templates, and
feature plans. Amendments require an explicit constitution update, a semantic
version change, and review of dependent Spec Kit templates and runtime guidance.

Versioning policy:
- MAJOR: backward-incompatible governance changes or removed principles.
- MINOR: new principles, new required gates, or materially expanded constraints.
- PATCH: clarifications, wording fixes, or non-semantic refinements.

Compliance review is required during specification, planning, task generation,
and implementation closeout. Reviewers MUST verify that protected files,
secret-safety, reproducible bootstrap behavior, and validation-before-coverage
rules are addressed before accepting feature work.

**Version**: 1.0.0 | **Ratified**: 2026-05-01 | **Last Amended**: 2026-05-01
