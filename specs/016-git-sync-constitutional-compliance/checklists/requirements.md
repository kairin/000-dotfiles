# Requirements Checklist: Git-Sync Constitutional Compliance

**Spec**: 016-git-sync-constitutional-compliance
**Status**: Ready for Implementation

---

## Functional Requirements Verification

### Spec Branch Recognition
- [ ] FR-001: Skill recognizes spec branch format (`NNN-description`) as valid
- [ ] FR-002: Skill does not show branch format warning for spec branches
- [ ] FR-003: Skill validates constitutional branch format for feature branches

### Special Branch Handling
- [ ] FR-004: Skill recognizes `main` and `master` as valid
- [ ] FR-005: Skill shows branch validation status in report for all branch types

### Commit Delegation
- [ ] FR-006: Skill detects uncommitted changes (staged and unstaged)
- [ ] FR-007: Skill offers handoff to `/001-commit` when uncommitted changes detected
- [ ] FR-008: Skill continues sync if user declines commit delegation
- [ ] FR-009: Skill shows uncommitted changes in report regardless of delegation choice

### Scope Clarification
- [ ] FR-010: Skill output includes scope statement clarifying sync-only purpose
- [ ] FR-011: Skill clearly suggests next skills in workflow (handoffs section)
- [ ] FR-012: Skill description explicitly states sync-only scope

---

## Success Criteria Verification

- [ ] SC-001: Git-sync on spec branch (e.g., `015-*`) produces no branch format warning
- [ ] SC-002: Git-sync with uncommitted changes shows offer to delegate to `/001-commit`
- [ ] SC-003: Git-sync output includes clear scope statement
- [ ] SC-004: All recognized branch patterns show PASS in validation

---

## Acceptance Scenario Verification

### User Story 1 - Spec Branch Recognition
- [ ] Spec branch `015-verbose-spinner-progress` shows no warning
- [ ] Spec branch `016-git-sync-constitutional-compliance` shows PASS
- [ ] Branch `main` shows PASS
- [ ] Branch `random-feature` shows WARNING

### User Story 2 - Commit Delegation
- [ ] Uncommitted changes shown and delegation offered
- [ ] Untracked files reported
- [ ] Sync continues if delegation declined
- [ ] Handoff suggestion shown if accepted

### User Story 3 - Scope Clarification
- [ ] Scope statement appears in output
- [ ] Next steps suggest `/001-commit` when appropriate
- [ ] Handoffs section shows `/001-04-full-workflow`

---

## Edge Cases Verified

- [ ] `main` branch shows PASS
- [ ] `master` branch shows PASS
- [ ] Constitutional branch (YYYYMMDD-HHMMSS-type-desc) shows PASS
- [ ] Invalid spec number (e.g., `1-feature`) shows WARNING
- [ ] Both staged and unstaged changes reported correctly

---

## Sign-off

- [ ] All functional requirements implemented
- [ ] All success criteria met
- [ ] All acceptance scenarios pass
- [ ] All edge cases handled
