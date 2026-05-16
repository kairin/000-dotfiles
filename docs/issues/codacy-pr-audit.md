# PR Audit: Codacy and GitHub Protection Issues Summary

> **Superseded by PR #254 (2026-05-16).** The "Restoration Plan" and
> Priority P2 entries below recommended conditional check enforcement
> (Codacy checks only for Python PRs). That direction was abandoned.
> All four Codacy checks are now required unconditionally on `main`.
> Treat the action items as historical record; do not act on them.

**Status:** Comprehensive audit of 13 merged PRs conducted
**Date:** 2026-05-06
**Scope:** All PRs merged to main after branch protection removal

## Merged PRs Summary

The following 13 PRs were successfully merged to main after branch protection was removed on 2026-05-06:

| PR # | Title | Codacy Static Analysis | Diff Coverage | Coverage Variation | Codacy Safety-Net | Stale Checks | Notes |
|------|-------|:----------------------:|:--------------:|:------------------:|:-----------------:|:------------:|-------|
| #197 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✓ Pass | — | Clean merge |
| #198 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✓ Pass | — | Clean merge |
| #200 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✓ Pass | — | Clean merge |
| #201 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✓ Pass | — | Clean merge |
| #202 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✓ Pass | — | Clean merge |
| #204 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✗ Failed | — | Safety-net failure (deprecated API); merged despite failure |
| #207 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✗ Failed | ⚠ Recycled | Safety-net failure; checks from PR #165; merged despite failure |
| #212 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✗ Failed | ⚠ Recycled | Safety-net failure; checks from PR #116; merged despite failure |
| #215 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✗ Failed | ⚠ Recycled | Safety-net failure; checks from PR #182; merged despite failure |
| #220 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✗ Failed | ⚠ Recycled | Safety-net failure; checks from PR #188; merged despite failure |
| #221 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✗ Failed | ⚠ Recycled | Safety-net failure; checks from PR #181; merged despite failure |
| #223 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✓ Pass | — | Clean merge |
| #224 | — | ✓ Pass | ✓ Pass | ✓ Pass | ✓ Pass | — | Clean merge |

**Legend:**
- ✓ Pass = Check passed and was fresh/valid
- ✗ Failed = Check failed (Codacy Safety-Net due to deprecated API endpoint)
- ⚠ Recycled = Check result was recycled from a different PR (stale check result)
- — = No issue detected or N/A

## Key Findings

### Safety-Net Failures (6 PRs)
PRs #204, #207, #212, #215, #220, #221 all failed the `codacy-safety-net` job due to the deprecated Codacy API endpoint being called by `codacy-coverage-reporter-action@89d6c85c`.

**Root Cause:** The pinned action version targets the deprecated `https://api.codacy.com/2.0/` endpoint, which no longer exists.

**Impact:** Workflow failures forced manual merge intervention, but underlying code quality was not compromised.

**Fix:** Update action pin to a newer version supporting the current Codacy API.

See: [`docs/issues/codacy-safety-net-failures.md`](codacy-safety-net-failures.md)

### Stale Check Results (5 PRs)
PRs #207, #212, #215, #220, #221 showed passing Codacy app checks (Static Analysis, Diff Coverage, Coverage Variation) but the check results were recycled from unrelated PRs:

- PR #207 checks from PR #165
- PR #212 checks from PR #116
- PR #215 checks from PR #182
- PR #220 checks from PR #188
- PR #221 checks from PR #181

**Root Cause:** GitHub Actions or Codacy's check-posting mechanism reused stale results instead of triggering fresh analysis.

**Impact:** These 5 PRs merged with false confidence — the passing checks were not fresh analysis of the actual PR changes.

**Mitigation:** Verify code quality with local pre-push hooks before future merges.

See: [`docs/issues/codacy-stale-checks.md`](codacy-stale-checks.md)

### Branch Protection Removal (All PRs)
All 13 PRs required branch protection to be removed to complete the merge. The original ruleset required:
- Codacy Static Code Analysis (required on all PRs)
- Codacy Diff Coverage (required on all PRs)
- Codacy Coverage Variation (required on all PRs)

**Issue:** These checks were not appearing on bash/docs-only PRs, causing "Required status check missing" failures.

**Resolution:** Branch protection was removed entirely on 2026-05-06.

**Restoration Plan:** Re-enable protection with conditional checks (Python/code files only).

See: [`docs/issues/branch-protection-history.md`](branch-protection-history.md)

## Codacy Registration Gap

The Codacy MCP query returns 0 repositories for the `kairin` org, despite the org being registered (id 175394). The GitHub App posts checks, but the project is not visible via the Codacy API.

**Impact:** CODACY_PROJECT_TOKEN may be stale or incorrectly configured.

**Investigation:** 5-step remediation plan documented.

See: [`docs/issues/codacy-registration.md`](codacy-registration.md)

## Recommendation Summary

| Priority | Issue | Action | Est. Effort |
|----------|-------|--------|-------------|
| P0 | Deprecated API endpoint (6 PRs failed) | Update `codacy-coverage-reporter-action` pin to current version | 15 min |
| P1 | Codacy not visible via API (0 repos) | Verify CODACY_PROJECT_TOKEN; re-register project if needed | 30 min |
| P2 | Branch protection too strict (all PRs blocked) | Restore with conditional checks (code files only) | 20 min |
| P3 | Stale check recycling (5 PRs merged with false positives) | Monitor; may self-correct with API fix | — |

## Files and References

- Workflow: `.github/workflows/dotfiles-validation.yml` (lines 32-40 and 83)
- Local pipeline: `scripts/quality-pipeline.sh`
- Codacy action: https://github.com/codacy/codacy-coverage-reporter-action
- Branch protection backup: `~/branch-protection-backup-2026-05-06/`

## Next Steps

1. Implement P0 fix (update action version)
2. Test with a new PR merge
3. Implement P1 fix (verify Codacy registration)
4. Implement P2 fix (restore branch protection with conditional checks)
5. Monitor for further stale check incidents
