# Stale Codacy App Check Results

> **Historical investigation (archived 2026-05-17).** This documents a past
> failure mode that has since been resolved. Not current guidance. For the
> canonical Codacy CLI configuration and the four required checks, see
> [../../ARCHITECTURE.md#codacy-cli-configuration](../../ARCHITECTURE.md#codacy-cli-configuration).

Several PRs merged with false "passing" signals from the Codacy app check integration. These checks were not fresh analyses of the current branch, but rather recycled results from older PR numbers. This masked the true status of code quality on the merged branches and could have hidden real issues if the code had diverged since the original check.

## The Pattern

When a PR branch is re-pushed or rebased, GitHub may keep old check results if the check comes from the same source. In our case, the Codacy app check results are tied to the PR number, not the commit hash. When PRs are auto-opened (like those created by the Codex agent) but based on old commits, the Codacy checks reference the old PR numbers instead of analyzing the current PR's actual code.

This happens because:
- The Codacy app integrates with GitHub at the PR level, recording results against a specific PR number
- When a new PR is created from an old branch, GitHub's check reconciliation system may associate the new PR with pre-existing check results if the run ID matches
- The checks appear to pass without fresh analysis, creating a false sense of code quality assurance

## Affected PRs & Their Sources

| Current PR | Original PR (check source) | Codacy Check Timestamp | Status |
|---|---|---|---|
| #207 | #165 | 2026-05-02 | Passed (stale) |
| #212 | #116 | 2026-05-02 | Passed (stale) |
| #215 | #182 | 2026-05-04 | Passed (stale) |
| #220 | #188 | 2026-05-04 | Passed (stale) |
| #221 | #181 | 2026-05-02 | Passed (stale) |

All five of these PRs were merged without receiving fresh Codacy analysis of their actual branches.

## Why This Is Problematic

These PRs passed their Codacy checks according to GitHub's status checks, but the checks weren't fresh analyses of the current branch code. Instead, the checks were recycled from analysis runs on completely different PRs. This means:

- **False confidence**: Merging appears safe because all checks pass, but the code wasn't actually validated
- **Diverged branches**: If the current PR's branch had diverged significantly from the original PR that was checked, the stale check masks potential new issues
- **Lost audit trail**: The check results don't reflect what was actually merged, making post-incident analysis harder

## What to Look For

### Identifying Stale Checks

You can identify stale Codacy checks by examining the check URL in GitHub:

1. Open the PR in GitHub and view the Checks tab
2. Click on the Codacy app check result
3. Look at the URL in the Codacy dashboard — it will contain `pull-requests/NNN` where `NNN` is the PR number
4. Compare `NNN` to the current PR number:
   - If they match: the check is fresh
   - If they differ: the check is stale and should not be trusted

### How to Handle Stale Checks

If you encounter a stale Codacy check:

1. **Ignore the stale result** — do not merge based on a passing stale check
2. **Rebase or re-push the PR** — force GitHub to request a fresh check run from Codacy
3. **Wait for fresh results** — only merge once Codacy has analyzed the actual current branch code
4. **Verify the check URL** — confirm the new check references the correct PR number before merging

For future prevention, ensure that:
- Auto-created PRs use the latest commits from their base branches
- Check results are validated to reference the current PR number before relying on them for merge decisions
- Codacy integration is configured to always run fresh analysis rather than reusing results from other PRs
