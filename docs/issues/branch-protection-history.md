# Branch Protection History

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
