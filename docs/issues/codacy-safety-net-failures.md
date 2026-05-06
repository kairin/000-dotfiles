# Root Cause: Deprecated Codacy API Endpoint (codacy-safety-net Failures)

**Status:** Issue identified and documented
**Affects:** 10 PRs (#181, #182, #183, #188, #204, #207, #212, #215, #220, #221)
**Root Cause:** Pinned action version uses deprecated Codacy API endpoint

## The Problem

The `codacy-coverage-reporter-action` is pinned to commit `89d6c85c` (version v14.1.3) in `.github/workflows/dotfiles-validation.yml` at line 83. This version calls the deprecated Codacy API endpoint `https://api.codacy.com/2.0/`, which no longer exists and returns a 404 error.

The error message returned is:
```
Request URL not found. Check if the API Token you are using and the API base URL are valid.
```

When the coverage upload step executes, this deprecated endpoint call fails, causing the entire workflow to exit with status 1, marking the build as failed.

## Affected PRs

The following 10 pull requests were affected by this issue:

- PR #181 — merged
- PR #182 — merged
- PR #183 — merged
- PR #188 — merged
- PR #204 — merged
- PR #207 — merged
- PR #212 — merged
- PR #215 — merged
- PR #220 — merged
- PR #221 — merged

All affected PRs were eventually merged despite the workflow failure, as the issue was understood to be a tooling/version compatibility problem rather than a code quality issue.

## Why This Happens

The workflow's "Codacy Safety Net" has a two-step process:

1. **Status Check Step** (lines 24-40): Before running analysis or uploading coverage, the workflow polls the Codacy API to check if this commit has already been analyzed. The query is:
   ```bash
   curl -s -H "api-token: $CODACY_PROJECT_TOKEN" \
     "https://api.codacy.com/2.0/commit/$SHA/quality-status"
   ```

2. **Conditional Execution**: If Codacy already has data for the commit (status = "analyzed"), the workflow skips the analysis and upload steps. If not, it proceeds.

The issue manifests in step 2:

- When the pre-push hook did not run locally (e.g., commit made without local analysis), the workflow proceeds to the "Upload coverage to Codacy" step.
- This step (line 83) uses the pinned `codacy-coverage-reporter-action@89d6c85c` action.
- The action internally attempts to post coverage data to the deprecated API endpoint `https://api.codacy.com/2.0/`, which returns 404.
- The workflow fails, even though the underlying coverage analysis was generated successfully.

This is a **version/upgrade issue**: the action was pinned to an old commit that targets the deprecated Codacy API. The current version of the action supports the modern Codacy platform (api.codacy.com or the current endpoint), but the pin prevents it from being used.

## Evidence

**Workflow pinning:**
File: `.github/workflows/dotfiles-validation.yml` line 83
```yaml
uses: codacy/codacy-coverage-reporter-action@89d6c85cfafaec52c72b6c5e8b2878d33104c699
```

This commit SHA (`89d6c85c...`) corresponds to tag v14.1.3 of the codacy-coverage-reporter-action repository.

**API endpoint in initial check:**
File: `.github/workflows/dotfiles-validation.yml` lines 32-33
```bash
curl -s -H "api-token: $CODACY_PROJECT_TOKEN" \
  "https://api.codacy.com/2.0/commit/$SHA/quality-status"
```

**Error observed in logs:**
```
Request URL not found. Check if the API Token you are using and the API base URL are valid.
```

## Fix Required

1. **Update the action pin** to a newer version that supports the current Codacy API:
   - Current pinned version: `89d6c85c` (v14.1.3) — targets deprecated `api.codacy.com/2.0/`
   - Recommended: Update to the latest stable release (use GitHub release tags or commits from the main branch)

2. **Verify CODACY_PROJECT_TOKEN**:
   - Ensure the token is valid for the current Codacy platform (app.codacy.com)
   - Regenerate if necessary from the project settings in the current Codacy dashboard

3. **Testing**:
   - After updating the action version, push a test commit to verify the workflow completes successfully
   - Confirm that coverage reports are properly uploaded to Codacy

4. **Consider deprecating the initial API check** (lines 32-33):
   - This step also uses the deprecated endpoint (`https://api.codacy.com/2.0/commit/$SHA/quality-status`)
   - It currently fails silently (caught by `|| echo "missing"`), defaulting to status "missing" and proceeding with upload
   - Updating this to the current endpoint would provide proper status checking

## References

- Action repository: https://github.com/codacy/codacy-coverage-reporter-action
- Workflow file: `.github/workflows/dotfiles-validation.yml`
- Codacy platform: https://app.codacy.com/
