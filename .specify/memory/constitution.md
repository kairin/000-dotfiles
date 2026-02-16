<!--
SYNC IMPACT REPORT
==================
Version change: 2.0.0 -> 3.0.0 (MAJOR - replaced project scope and redefined core principles)

Modified principles:
- I. Script Consolidation -> I. Single User Entry Point
- II. Branch Preservation -> II. Script Proliferation Prevention
- III. Local-First CI/CD -> III. Branch Preservation and Traceability
- IV. Modularity Limits -> IV. Local-First Validation and Cost Control
- V. Symlink Single Source -> V. Documentation Currency and Evidence
- (new) VI. Instruction Source Integrity and Symlink Architecture

Added sections:
- Additional Constraints (rewritten for repository-specific controls)
- Development Workflow and Quality Gates (expanded with explicit verification workflow)
- Governance (expanded with amendment workflow, compliance cadence, and violation handling)

Removed sections:
- Technology Stack section with Ghostty-specific requirements

Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/*.md: ⚠ pending (directory does not exist in this repository)

Runtime guidance requiring updates:
- README.md: ✅ updated
- AGENTS.md: ✅ no change required (already aligned with updated principles)

Follow-up TODOs:
- TODO(COMMAND_TEMPLATES_PATH): create or restore `.specify/templates/commands/` if SpecKit command templates are expected in this repo.
-->

# 000-Dotfiles Constitution

## Core Principles

### I. Single User Entry Point

User-facing documentation and user-facing workflows MUST use `./start.sh` as the
only entry point. Developer-only commands MAY be documented only when labeled
`DEVELOPER ONLY` and MUST not replace `./start.sh` in user guidance.

Rationale: keeps onboarding deterministic and avoids divergent setup paths.

### II. Script Proliferation Prevention

The repository MUST extend existing scripts before creating new shell scripts.
New wrapper/helper scripts are prohibited outside `tests/` unless a documented
justification proves no existing script can be safely extended.

Rationale: controls maintenance cost and prevents script sprawl.

### III. Branch Preservation and Traceability

Branches MUST be named with the timestamped format
`YYYYMMDD-HHMMSS-type-description`, merged with `--no-ff`, and preserved after
merge unless explicit user approval authorizes deletion.

Rationale: preserves auditability and rollback history for configuration changes.

### IV. Local-First Validation and Cost Control

Any configuration or workflow change MUST run local validation before remote
operations. Minimum gates are:
- `./.runners-local/workflows/gh-workflow-local.sh all`
- `./.runners-local/workflows/health-check.sh --workstation-audit`

GitHub Actions usage MUST remain a final-stage check, not the primary
validation path.

Rationale: enforces reliability while protecting zero-cost CI/CD goals.

### V. Documentation Currency and Evidence

Status documents MUST reflect current, verifiable state.
- Documents that describe historical system states (for example RAID snapshots)
  MUST include clear historical labeling and verification dates.
- Roadmap references to specs, tasks, and issues MUST map to existing files and
  active tracking artifacts.
- Temporary audit folders (for example `01/`, `02/`) MUST be resolved by either
  promoting content into maintained documentation locations or explicitly
  excluding them with rationale.

Rationale: prevents operational drift and reduces decision errors from stale docs.

### VI. Instruction Source Integrity and Symlink Architecture

`AGENTS.md` is the single source of truth for assistant instructions.
`CLAUDE.md` and `GEMINI.md` MUST remain symlinks to `AGENTS.md` and MUST never
be converted into regular files.

Rationale: keeps assistant behavior consistent across toolchains.

## Additional Constraints

### Security and Secrets

- Secrets, tokens, credentials, and private keys MUST NOT be committed.
- Sensitive outputs MUST be redacted in logs and audit artifacts.
- Operations that can destroy data or history MUST require explicit user
  approval before execution.

### Operational Documentation Placement

- Repeatable verification outputs SHOULD be stored in maintained paths under
  repository documentation or spec artifacts.
- Ad-hoc root folders for operational notes MUST NOT remain indefinitely
  unowned and undocumented.

### Current Compliance Gaps (2026-02-16)

- Workstation audit reports missing Claude Context7 configuration.
- `ROADMAP.md` contains references to non-existent spec directories.
- `RAID_SETUP_SUMMARY.md` is historical while current host state has no active
  RAID arrays.
- Root-level untracked audit folders (`01/`, `02/`) require disposition.

## Development Workflow and Quality Gates

1. Classify change scope and impacted artifacts before implementation.
2. Implement changes with script consolidation and single-entry-point rules.
3. Run required local validation gates.
4. Update affected docs, roadmap links, and status summaries in the same change.
5. Confirm symlink integrity for `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` when
   instruction docs are touched.
6. Record unresolved drift in issues or TODOs with owner and next action.

## Governance

This constitution is authoritative for repository process and quality gates.
When conflicts occur, this file takes precedence over feature specs, plans,
and task lists.

### Amendment Process

1. Propose amendment with explicit rationale and impact scope.
2. Classify semantic version bump (`MAJOR`, `MINOR`, `PATCH`).
3. Update dependent templates and guidance in the same change.
4. Record a sync impact report at the top of this constitution.

### Versioning Policy

- `MAJOR`: backward incompatible governance or principle redefinition/removal.
- `MINOR`: new principle or materially expanded mandatory guidance.
- `PATCH`: clarifications, wording, or non-semantic refinements.

### Compliance Review Expectations

- Compliance MUST be reviewed on each change touching behavior, automation,
  documentation, or governance artifacts.
- A monthly governance audit SHOULD confirm roadmap/spec alignment, unresolved
  operational drift, and local CI/CD health.
- Constitutional violations MUST be escalated to the user immediately and MUST
  NOT be silently bypassed.

**Version**: 3.0.0 | **Ratified**: 2025-11-18 | **Last Amended**: 2026-02-16
