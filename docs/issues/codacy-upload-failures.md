# Review: Preventing Codacy Upload Failures

This document reviews the root causes of recent `codacy-cli upload` failures in CI and provides guidelines to prevent them in the future.

## Incident Analysis: PR #184

In PR #184, the `codacy-safety-net` workflow failed during the `Codacy Static Code Analysis` stage.

### Root Cause 1: Shallow Checkouts & Invalid SHAs
The `scripts/quality-pipeline.sh` script attempts to determine a `BASE_SHA` for a two-way upload (HEAD and merge-base). This ensures that Codacy can calculate the diff coverage and issues correctly.

```bash
BASE_SHA="$(git merge-base HEAD origin/main 2>/dev/null || git rev-parse origin/main 2>/dev/null || echo "")"
```

In the GitHub Actions environment, `actions/checkout@v4` defaults to `fetch-depth: 1`. This shallow checkout often contains only the single commit being tested. Consequently:
1. `git merge-base` fails because the common ancestor is not in the local history.
2. `git rev-parse origin/main` may return the literal string `origin/main` or fail if the remote branch wasn't fetched.

When the script then calls `codacy-cli upload -c "$BASE_SHA"`, it passes an invalid identifier (like `origin/main`). The Codacy API expects a 40-character hex SHA and returns a **404 Not Found** when it receives a branch name or invalid ref.

### Root Cause 2: CLI Internal Tool Mapping (Non-Fatal)
Confusion was also caused by the following error log:
`Error: failed to get page: request to https://app.codacy.com/api/v3/tools//patterns failed with status 404`

This appears to be a non-fatal warning in `codacy-cli` v2 when it tries to fetch patterns for enrichment but fails to resolve a specific tool ID (e.g., mapping `pylint` to an internal Codacy ID). While confusing, this did not cause the upload failure; the failure was caused by the 404 on the commit results endpoint.

## Prevention Guidelines

### 1. Ensure Adequate Fetch Depth in CI
Workflows that perform diff-based analysis or multi-commit uploads MUST fetch enough history to resolve the base branch.

**Recommendation:** Set `fetch-depth: 0` for quality pipelines.

```yaml
- name: Check out repository
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
```

### 2. Validate SHAs Before Upload
Scripts should verify that they have a valid 40-character hex SHA before attempting to call `codacy-cli upload`.

**Recommendation:** Add a validation step in `quality-pipeline.sh`.

```bash
if [[ ! "$SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Error: Invalid SHA identifier: $SHA"
  exit 1
fi
```

### 3. Prefer API over UI URLs for Configuration
If configuring `CODACY_API_BASE_URL`, ensure it points to `api.codacy.com` (for Cloud) or the appropriate enterprise API endpoint.

### 4. Robust Base Branch Resolution
When running in GitHub Actions, use environment variables like `GITHUB_BASE_REF` to find the target branch instead of assuming `origin/main`.

```bash
TARGET_BRANCH="${GITHUB_BASE_REF:-main}"
BASE_SHA=$(git rev-parse "origin/$TARGET_BRANCH")
```

## Summary of Action for PR #184
1. Update `.github/workflows/dotfiles-validation.yml` to use `fetch-depth: 0`.
2. Update `scripts/quality-pipeline.sh` to validate `$BASE_SHA` and use more robust resolution logic.
