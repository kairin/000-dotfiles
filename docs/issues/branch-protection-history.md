# Branch Protection History

> **Phase 3 Reversal (2026-05-16, PR #254):** The "Restored: 2026-05-16"
> section below describes an interim "safety-net only" state that was
> superseded later that same day by PR #254. Branch protection now requires
> all four Codacy checks unconditionally. `./setup ship` is the canonical
> merge path. Treat this file as a historical log; do not act on its policy
> or configuration claims.

## Original Configuration (Removed 2026-05-06)

The main branch had two layers of protection configured:

### Classic Branch Protection (DELETED)
- Enforced for admins: Yes
- Force pushes: Disabled
- Deletions: Disabled
- Required status checks:
  1. **Codacy Static Code Analysis**
  2. **Codacy Diff Coverage**
  3. **Codacy Coverage Variation**

### Repository Ruleset "Protect main" (ID: 15807535, DELETED)
- Enforced the same three Codacy status checks across all pull requests
- Prevented merges without passing checks

### Backup Location
Configuration backups preserved at:
- `~/branch-protection-backup-2026-05-06/classic-protection.json`
- `~/branch-protection-backup-2026-05-06/ruleset-15807535.json`

## Why Protection Was Removed

### The Problem
1. **Codacy Static Code Analysis check never triggers on bash-only or docs-only PRs**
   - The Codacy integration is configured to analyze Python code
   - When a PR contains only bash scripts, documentation, or non-Python files, Codacy does not run
   
2. **GitHub's required status check behavior is unforgiving**
   - If a required check does not report any status (neither pass nor fail), GitHub treats it as "missing"
   - GitHub does not distinguish between "check ran and failed" vs "check doesn't apply to this change"
   - Both scenarios block the PR from merging

3. **Result: All 31 open PRs were blocked indefinitely**
   - Most PRs were bash/docs-only changes (setup scripts, configuration, documentation)
   - The Codacy checks would never report status, causing permanent merge blocks
   - No workaround existed without removing branch protection

### Pragmatic Decision
Removed branch protection on 2026-05-06 to:
- Unblock all 31 pending PRs immediately
- Allow continued development and releases
- Buy time to fix the Codacy integration
- Restore proper protection once Codacy is correctly configured

## Current State (2026-05-06 onward)

- **Main branch has NO branch protection**
- All PRs can be merged regardless of check status
- Risk: without automated checks, quality-breaking changes can land without review
- This is a temporary state to unblock development; restoration is planned

## Restoration Plan

Once the Codacy integration is fixed, branch protection will be restored following these steps:

### 1. Verify Codacy Setup
- [ ] Confirm Codacy project is registered in the organization
- [ ] Validate Codacy API token and credentials
- [ ] Test that Codacy can analyze pull requests

### 2. Update Codacy Integration
- [ ] Upgrade `codacy-coverage-reporter-action` from deprecated version to current stable
- [ ] Verify action version is compatible with current GitHub Actions runtime
- [ ] Test in a dry-run PR to confirm checks report status

### 3. Configure Smart Check Rules
- [ ] Update ruleset to run Codacy checks conditionally:
  - Only on PRs that modify Python files
  - Skip checks for bash-only, docs-only, or config-only changes
- Alternative: Accept that checks may not run on non-Python PRs, but do not block merges
  - Requires separate discussion with team on quality/risk trade-off

### 4. Restore Branch Protection
Choose one approach:
- **Option A**: Restore the original ruleset (ID: 15807535) with updated Codacy action
- **Option B**: Restore classic branch protection with conditional checks
- **Option C**: Implement new ruleset with Codacy checks only on Python files

### 5. Monitor and Iterate
- Track merge rate and check pass rate in first week
- Collect feedback from team on false positives or false negatives
- Adjust rules if checks prove too restrictive or permissive

## References

- GitHub issue: [Link to tracking issue if exists]
- Codacy project: https://app.codacy.com/[organization]/[repository]
- Backup files: `~/branch-protection-backup-2026-05-06/`

## Restored: 2026-05-16 (interim, superseded same day)

> **Superseded by PR #254 — see "Reversal: 2026-05-16 (PR #254)" below.** This
> "Decision D2=A" approach was the interim state between the original block
> and the final four-check policy. The text is preserved as a log; do not act
> on its policy claims.

### Approach taken (Decision D2=A) — interim only

Instead of restoring the original three Codacy app checks, only `codacy-safety-net` is required. This check is workflow-based (`.github/workflows/codacy-safety-net.yml`) and fires on every PR regardless of which files changed.

### Ruleset created: "Protect main" (ID: 16046743)

- **Target:** default branch (`~DEFAULT_BRANCH`)
- **Enforcement:** active
- **Required status checks (interim):** `codacy-safety-net` only
  - `strict_required_status_checks_policy`: false (no requirement to be up-to-date before merge)
- **Additional rules:** deletion prevention, non-fast-forward prevention, pull request required
- **Interim non-required (now required after PR #254):** Codacy Static Code Analysis, Codacy Coverage Variation, Codacy Diff Coverage

### Why this approach — and why it was reversed

The interim rationale was: the three Codacy app checks do not trigger on
bash-only or docs-only PRs (no Python files changed), so requiring them
would reproduce the original blocking problem. In practice this caused
Codacy's repository dashboard to flag `main` as "not protected by Codacy
checks" and prompted PR #254 (same day) to make all four required and rely
on `./setup ship`'s admin-bypass path for any `BLOCKED` merge state caused by
the solo-reviewer requirement.

### Verification (interim — historical only)

```bash
gh api repos/kairin/000-dotfiles/rulesets --jq '.[].name'
# → Protect main

gh api repos/kairin/000-dotfiles/rulesets/16046743 \
  --jq '.rules[] | select(.type == "required_status_checks") | .parameters.required_status_checks'
# Interim output (now superseded):
# → [{"context":"codacy-safety-net","integration_id":15368}]
```

## Reversal: 2026-05-16 (PR #254)

The "Decision D2=A" interim policy above was reversed on the same day.
Branch protection (classic + ruleset `Protect main`, id `16046743`) now
requires all **four** contexts:

- `codacy-safety-net` (app_id `15368` — GitHub Actions)
- `Codacy Static Code Analysis` (app_id `56611` — Codacy app)
- `Codacy Coverage Variation` (app_id `56611` — Codacy app)
- `Codacy Diff Coverage` (app_id `56611` — Codacy app)

`./setup ship` resolves the required set dynamically from the GitHub API
and admin-bypasses the merge when `mergeStateStatus=BLOCKED` solely because
of the solo-reviewer requirement and every required check is green.

Current verification:

```bash
gh api repos/kairin/000-dotfiles/branches/main/protection \
  --jq '.required_status_checks.contexts | sort'
# → ["Codacy Coverage Variation","Codacy Diff Coverage","Codacy Static Code Analysis","codacy-safety-net"]

gh api repos/kairin/000-dotfiles/rulesets/16046743 \
  --jq '.rules[] | select(.type == "required_status_checks") | .parameters.required_status_checks | sort_by(.context)'
# → [{"context":"Codacy Coverage Variation","integration_id":56611},
#    {"context":"Codacy Diff Coverage","integration_id":56611},
#    {"context":"Codacy Static Code Analysis","integration_id":56611},
#    {"context":"codacy-safety-net","integration_id":15368}]
```
