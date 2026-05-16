# Codacy & GitHub Protection Issues: Comprehensive Report

> **Superseded for protection policy by PR #254 (2026-05-16).** The
> remediation plan in this report (including the P2 recommendation to restore
> protection with "conditional check enforcement") was the picture in early
> May. PR #254 reversed that direction: `main` now requires all four Codacy
> contexts unconditionally, with `./setup ship` performing the canonical
> admin-bypass when the merge state lands `BLOCKED` solely because of the
> solo-reviewer requirement. Treat the protection sections of this report as
> historical context, not a remediation playbook.

**Report Date:** 2026-05-06  
**Status:** 13 PRs merged; 6 root causes identified; 3 priority fixes recommended (protection-policy items superseded — see banner above)  
**Prepared by:** Multi-agent parallel investigation and documentation

---

## Executive Summary

On 2026-05-06, a critical confluence of Codacy integration failures and overly-restrictive GitHub branch protection rules created a merge bottleneck. **31 PRs were stuck**, with only 13 cleanly mergeable. After removing branch protection, those 13 were successfully merged, but investigations revealed **6 distinct root causes** spanning deprecated API endpoints, stale check results, misconfigured tokens, and unconditional check enforcement.

This report documents all findings and provides prioritized remediation steps.

### Quick Facts

- **Scope:** 13 PRs merged to main after protection removal
- **Root causes identified:** 6
- **Affected systems:** Codacy coverage reporting, GitHub branch protection, GitHub Actions CI
- **Key dates:**
  - PRs merged: 2026-05-05 (protection removed same day)
  - Investigation completed: 2026-05-06
- **Priority fixes:** 3 (P0, P1, P2)

---

## Root Causes

### 1. Deprecated Codacy API Endpoint (P0 — Critical)

**Status:** 6 PRs failed; merge blocker removed  
**Impact:** High — workflow failures on every PR using coverage upload  
**Severity:** CRITICAL

The `codacy-coverage-reporter-action` in `.github/workflows/dotfiles-validation.yml` is pinned to commit `89d6c85c` (v14.1.3). This version calls the deprecated Codacy API endpoint `https://api.codacy.com/2.0/`, which no longer exists and returns HTTP 404.

**Affected PRs:** #204, #207, #212, #215, #220, #221 (6 total)

**Error message:**
```
Request URL not found. Check if the API Token you are using and the API base URL are valid.
```

**Why it matters:** The "Codacy Safety Net" job runs on every PR that hasn't been pre-analyzed locally. When the pre-push hook doesn't run (e.g., direct commits or rebases), the workflow attempts to upload coverage. The old action version fails immediately, marking the job as FAILED even though the code quality itself is fine.

**Fix:** Update the action pin to a newer version supporting the current Codacy API. See detailed analysis in [`docs/issues/codacy-safety-net-failures.md`](issues/codacy-safety-net-failures.md).

---

### 2. Stale/Recycled Codacy Check Results (P3 — Informational)

**Status:** 5 PRs merged with stale checks; may self-correct  
**Impact:** Medium — false confidence in code quality  
**Severity:** MEDIUM

PRs #207, #212, #215, #220, #221 all showed passing Codacy checks (Static Analysis, Diff Coverage, Coverage Variation), but the check results were recycled from different PR numbers:

| PR | Stale Check Source |
|----|-------------------|
| #207 | PR #165 |
| #212 | PR #116 |
| #215 | PR #182 |
| #220 | PR #188 |
| #221 | PR #181 |

**Why it matters:** These PRs merged with check marks that weren't fresh analysis of their actual changes. The GitHub App posted results, but they were computed for unrelated PRs.

**Root cause:** Likely a timing or webhook-redelivery issue in how Codacy or GitHub posts check updates.

**Mitigation:** This pattern may self-correct once the API endpoint is fixed. Verify by re-running these PRs through the quality pipeline.

See detailed analysis in [`docs/issues/codacy-stale-checks.md`](issues/codacy-stale-checks.md).

---

### 3. Codacy Project Not Registered in API (P1 — High)

**Status:** Project invisible via Codacy API  
**Impact:** High — token validation and project setup unclear  
**Severity:** HIGH

The Codacy MCP query `codacy_list_organization_repositories` returns **0 repositories** for the `kairin` org, despite the org being registered (Codacy id 175394). The GitHub App successfully posts checks to PRs, but the project is not visible via the Codacy API.

**Why it matters:** This indicates one of two problems:
1. The `CODACY_PROJECT_TOKEN` is stale or incorrectly scoped
2. The project was set up on an old Codacy platform and not migrated to the current one

Either way, the GitHub integration works (checks are posted), but backend operations (coverage upload, status queries) are either failing silently or hitting the wrong endpoint.

**Root causes:** Likely a missing re-registration or token rotation after a platform migration.

**Fix:** 5-step remediation plan — verify token, check project visibility, re-register if needed. See [`docs/issues/codacy-registration.md`](issues/codacy-registration.md).

---

### 4. Overly-Strict Branch Protection Rules (P2 — High)

**Status:** Protection removed; restoration plan pending  
**Impact:** Very High — all 31 PRs were blocked  
**Severity:** CRITICAL (but now mitigated)

The GitHub branch protection ruleset required three Codacy checks on **every PR unconditionally**:
- ✓ Codacy Static Code Analysis (required)
- ✓ Codacy Diff Coverage (required)
- ✓ Codacy Coverage Variation (required)

However, the "Codacy Static Code Analysis" check is only generated for PRs that modify Python code. Bash-only, documentation-only, and config-only PRs never trigger this check, resulting in **"Required status check missing"** failures.

**Why it matters:** This created an unsolvable catch-22:
- If the check is required, bash/docs PRs can never pass (check is never generated)
- If all PRs must have checks, bash/docs PRs are stuck
- The only solution was to remove protection entirely

**Original protection config:** Ruleset id 15807535 (removed 2026-05-06)

**Backup location:** `~/branch-protection-backup-2026-05-06/`

**Fix:** Restore protection with **conditional** check enforcement. Codacy checks should only be required on PRs that modify Python/code files. See [`docs/issues/branch-protection-history.md`](issues/branch-protection-history.md).

---

### 5. Workflow Job Rename Causing Dual Check Presence (P3 — Informational)

**Status:** Documented; may require clarification  
**Impact:** Low — confusion about which check is authoritative  
**Severity:** LOW

The CI workflow's main job was refactored from `validate` to `codacy-safety-net`. PRs that existed across this rename show **both job names** in their check rollup:
- Old `validate` job: shows SUCCESS (pre-rename runs)
- New `codacy-safety-net` job: shows FAILURE (post-rename runs)

This created ambiguity about which check result was authoritative.

**Why it matters:** Low immediate impact since branch protection is now removed. However, once protection is restored, the dual-job presence could cause confusion about which check is actually required.

**Fix:** Clean up old check runs once the rename is fully rolled out. GitHub's check system will eventually hide old checks, but manual cleanup may be needed.

---

### 6. Missing Codacy Static Code Analysis Check on Bash/Docs PRs (P2 — Included in #4)

**Status:** Not a bug; expected behavior  
**Impact:** Part of the branch protection problem  
**Severity:** LOW (addressed by conditional protection)

The "Codacy Static Code Analysis" check is conditionally generated only for PRs that modify code files. When a PR touches only bash scripts, documentation, or config, no check is generated at all.

This is correct behavior (bash scripts aren't analyzed by Codacy's Python-focused linters). However, when branch protection **required** this check on all PRs, it created unsolvable failures.

**Fix:** Addressed by restoration of conditional branch protection (PR must modify Python code to require the check).

---

## All Merged PRs Audit

A complete audit of the 13 successfully-merged PRs, including Codacy check statuses and stale-check flags, is available in [`docs/issues/codacy-pr-audit.md`](issues/codacy-pr-audit.md).

Key findings from the audit:
- **6 PRs** failed the Codacy Safety-Net job (deprecated API)
- **5 PRs** had stale/recycled check results (false passing signals)
- **8 PRs** had clean, fresh checks
- **All 13** required branch protection removal to merge

---

## Remediation Plan

### Priority P0: Fix Deprecated API Endpoint (Critical, 15 min est.)

**Action:** Update the `codacy-coverage-reporter-action` pin in `.github/workflows/dotfiles-validation.yml` line 83.

**Current:**
```yaml
uses: codacy/codacy-coverage-reporter-action@89d6c85cfafaec52c72b6c5e8b2878d33104c699
```

**Recommended:**
Update to the latest stable release using a version tag (e.g., `v14.10.5` or current main). Check the [codacy-coverage-reporter-action releases](https://github.com/codacy/codacy-coverage-reporter-action/releases).

**Also:** Update the deprecated endpoint call in lines 32-33 from `https://api.codacy.com/2.0/` to the current endpoint.

**Verification:**
- Push a test PR and verify `codacy-safety-net` job completes successfully
- Confirm coverage reports appear in Codacy

---

### Priority P1: Verify Codacy Registration & Token (High, 30 min est.)

**Action:** Confirm `CODACY_PROJECT_TOKEN` is valid and project is registered.

**Steps:**
1. Log into https://app.codacy.com/ and verify the project is visible in the org dashboard
2. Regenerate the project token in settings if not visible
3. Update the `CODACY_PROJECT_TOKEN` secret in GitHub Actions if regenerated
4. Run `uv run dotfiles_tools <command>` (check CLAUDE.md for verification command) to confirm API access

**Verification:**
- Codacy MCP query returns >0 repositories for org
- Coverage uploads succeed after P0 fix is applied

---

### Priority P2: Restore Branch Protection with Conditional Checks (High, 20 min est.)

**Action:** Re-enable branch protection with checks conditionally required based on file type.

**Configuration:**
- Restore ruleset id 15807535 (backup available in `~/branch-protection-backup-2026-05-06/`)
- Modify check requirements: Codacy checks should only be required if the PR modifies `.py` files or `scripts/` directory
- Keep the ruleset disabled for bash/docs/config-only PRs

**Alternative:** If GitHub's rulesets don't support conditional checks by file type, consider:
- Create a separate rule for Python files
- Create a simpler rule for docs/bash files with no Codacy checks required

**Verification:**
- Push a test Python PR; verify all 3 Codacy checks are required and blocking
- Push a test bash/docs PR; verify Codacy checks are not required (or not blocking if generated)

---

## Files and References

### Issue Documentation (in `docs/issues/`)
1. [`codacy-safety-net-failures.md`](issues/codacy-safety-net-failures.md) — Detailed analysis of the deprecated API endpoint issue
2. [`codacy-stale-checks.md`](issues/codacy-stale-checks.md) — Investigation of recycled check results
3. [`branch-protection-history.md`](issues/branch-protection-history.md) — Original protection config and removal reason
4. [`codacy-registration.md`](issues/codacy-registration.md) — Codacy API registration gap and token analysis
5. [`codacy-pr-audit.md`](issues/codacy-pr-audit.md) — Per-PR audit table with check statuses

### Key Files in Codebase
- `.github/workflows/dotfiles-validation.yml` — The failing CI workflow
- `scripts/quality-pipeline.sh` — Local pre-push quality pipeline
- `setup` — Main setup script (contains ./setup ship command for PR merge + Codacy upload)

### External Resources
- Codacy coverage reporter action: https://github.com/codacy/codacy-coverage-reporter-action
- Codacy platform: https://app.codacy.com/
- GitHub branch protection docs: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets

---

## Timeline

| Date | Event |
|------|-------|
| 2026-05-05 | 31 PRs stuck due to Codacy failures and branch protection blocks |
| 2026-05-05 (evening) | Branch protection removed to unblock merges |
| 2026-05-05 (late) | 13 cleanly-mergeable PRs merged to main |
| 2026-05-06 (morning) | Investigation began via parallel multi-agent research |
| 2026-05-06 (midday) | All 6 root causes identified and documented |
| 2026-05-06 (this report) | Comprehensive remediation plan compiled |

---

## Conclusion

The merge bottleneck was caused by a **convergence of three issues:**

1. **Deprecated API endpoint** made the Codacy workflow fail on every PR without pre-push analysis
2. **Overly-strict branch protection** required checks that can never be generated on non-Python PRs
3. **Stale check results** meant that passing checks weren't fresh analysis

All three must be fixed to prevent recurrence:
- **P0 (API):** Enables the workflow to succeed again
- **P1 (Token/Registration):** Ensures backend integration is working
- **P2 (Protection):** Prevents re-blocking of bash/docs/config PRs

Estimated total remediation time: **~1 hour** (mostly testing).

**Next step:** Implement P0 fix, test with a new PR, then proceed with P1 and P2.

---

**Report compiled:** 2026-05-06 by multi-agent parallel investigation  
**Agent contributors:** Safety-Net Deep-Dive, Stale Checks, Branch Protection, Registration, PR Audit  
**Prepared for:** kairin (project owner)
