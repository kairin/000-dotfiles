# Feature Specification: Git-Sync Constitutional Compliance

**Feature Branch**: `016-git-sync-constitutional-compliance`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "Enhance the /001-03-git-sync skill to recognize spec branch patterns, offer commit delegation for uncommitted changes, and clarify its sync-only scope"

---

## Problem Statement

The `/001-03-git-sync` skill was designed as a sync-only utility but doesn't fully comply with constitutional requirements or handle common developer workflows:

| Issue | Current Behavior | Expected Behavior |
|-------|------------------|-------------------|
| Spec branch format | Not recognized | Should recognize `NNN-description` as valid |
| Non-compliant branches | Only warns | Should clarify warning is informational for sync |
| Uncommitted changes | Only reports | Should offer to delegate to `/001-commit` |
| Scope | Implied sync-only | Should explicitly document sync-only scope |

**Current git-sync warning on spec branches:**

```
Branch Validation:
------------------
| Check           | Status          |
|-----------------|-----------------|
| Name format     | WARNING         |

WARNING: Branch name does not follow YYYYMMDD-HHMMSS-type-description format
Current: 015-verbose-spinner-progress
```

This warning is confusing because spec branches (`NNN-description`) are a valid pattern for feature development work.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sync Without Warning on Spec Branches (Priority: P1)

As a developer working on a spec branch, I want git-sync to recognize my branch format as valid so I don't see unnecessary warnings during routine synchronization.

**Why this priority**: Spec branches are the primary development pattern. False warnings add noise and confusion.

**Independent Test**: Run `/001-03-git-sync` on a branch named `015-verbose-spinner-progress` and observe no branch format warning.

**Acceptance Scenarios**:

1. **Given** current branch is `015-verbose-spinner-progress`, **When** git-sync runs, **Then** no branch format warning is displayed
2. **Given** current branch is `016-git-sync-constitutional-compliance`, **When** git-sync runs, **Then** branch validation shows PASS
3. **Given** current branch is `main`, **When** git-sync runs, **Then** branch validation shows PASS (special branch)
4. **Given** current branch is `random-feature`, **When** git-sync runs, **Then** branch validation shows WARNING (not a recognized format)

---

### User Story 2 - Offer Commit Delegation for Uncommitted Changes (Priority: P2)

As a developer with uncommitted changes, I want git-sync to offer to delegate to the commit workflow so I can maintain proper commit hygiene before syncing.

**Why this priority**: Uncommitted changes are a common state. Offering workflow integration improves developer experience without forcing manual skill switching.

**Independent Test**: Run `/001-03-git-sync` with uncommitted changes and observe an offer to run `/001-commit` first.

**Acceptance Scenarios**:

1. **Given** there are uncommitted changes, **When** git-sync runs, **Then** it shows uncommitted files and offers to delegate to `/001-commit`
2. **Given** there are untracked files, **When** git-sync runs, **Then** it shows untracked files in the report
3. **Given** user declines commit delegation, **When** git-sync continues, **Then** sync proceeds with warning about uncommitted changes
4. **Given** user accepts commit delegation, **When** handoff occurs, **Then** skill suggests running `/001-commit` first

---

### User Story 3 - Clear Scope Documentation (Priority: P3)

As a developer, I want git-sync to clearly communicate its scope so I understand it handles synchronization only, not the full development workflow.

**Why this priority**: Clear scope prevents confusion about what git-sync does vs. other skills.

**Independent Test**: Read `/001-03-git-sync` output and observe clear scope statement distinguishing it from full workflow skills.

**Acceptance Scenarios**:

1. **Given** git-sync completes successfully, **When** output is displayed, **Then** a scope clarification appears (e.g., "Git-sync handles remote synchronization only")
2. **Given** git-sync encounters uncommitted changes, **When** report is displayed, **Then** next steps clearly suggest `/001-commit` for commit workflow
3. **Given** git-sync completes, **When** handoffs are shown, **Then** `/001-04-full-workflow` is offered for complete development cycle

---

### Edge Cases

- What happens if branch is `main` or `master`?
  - Show PASS for branch validation (special protected branches)
- What happens if branch matches constitutional format?
  - Show PASS (already compliant)
- What happens if branch matches spec format but has invalid number?
  - Show PASS (number validation is not git-sync's responsibility)
- What happens if there are both staged and unstaged changes?
  - Report both clearly, offer commit delegation

---

## Requirements *(mandatory)*

### Functional Requirements

**Spec Branch Recognition:**
- **FR-001**: Skill MUST recognize spec branch format (`NNN-description` where NNN is 3 digits) as valid
- **FR-002**: Skill MUST NOT show branch format warning for spec branches
- **FR-003**: Skill MUST continue to validate constitutional branch format for feature branches

**Special Branch Handling:**
- **FR-004**: Skill MUST recognize `main` and `master` as valid (no warning)
- **FR-005**: Skill MUST show branch validation status in report for all branch types

**Commit Delegation:**
- **FR-006**: Skill MUST detect uncommitted changes (staged and unstaged)
- **FR-007**: Skill MUST offer handoff to `/001-commit` when uncommitted changes detected
- **FR-008**: Skill MUST continue sync if user declines commit delegation
- **FR-009**: Skill MUST show uncommitted changes in report regardless of delegation choice

**Scope Clarification:**
- **FR-010**: Skill output MUST include scope statement clarifying sync-only purpose
- **FR-011**: Skill MUST clearly suggest next skills in workflow (handoffs section)
- **FR-012**: Skill description MUST explicitly state sync-only scope

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running git-sync on a spec branch (e.g., `015-*`) produces no branch format warning
- **SC-002**: Running git-sync with uncommitted changes shows offer to delegate to `/001-commit`
- **SC-003**: Git-sync output includes clear scope statement distinguishing from full workflow
- **SC-004**: All recognized branch patterns (spec, constitutional, main/master) show PASS in validation

---

## Assumptions

- Spec branch format is `NNN-description` where NNN is 3 digits (001-999)
- Constitutional branch format is `YYYYMMDD-HHMMSS-type-description`
- `/001-commit` skill is available for delegation
- Skill handoffs mechanism already exists in skill definition format

---

## Out of Scope

- Modifying the `/001-commit` skill
- Adding new branch validation rules beyond pattern recognition
- Enforcing commit before sync (only offering, not requiring)
- Modifying git operations (fetch, pull, push logic remains unchanged)

---

## Files to Modify

| File | Change |
|------|--------|
| `.claude/skill-sources/001-03-git-sync.md` | Update branch validation regex, add commit delegation offer, clarify scope |

---

## Specification Quality Checklist

**Purpose**: Validate specification completeness and quality before proceeding to planning

### Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

### Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

---

## Next Step

Run `/speckit.plan` to generate the implementation plan.
