# Codacy Integration Guide

Complete documentation for Codacy setup, token management, and CI/CD integration in this project and for generalizing to other repositories.

## Table of Contents

1. [Overview](#overview)
2. [LLM Agent Workflow](#llm-agent-workflow)
3. [Issues Fixed](#issues-fixed)
4. [Token Management](#token-management)
5. [Local Development](#local-development)
6. [CI/CD Workflow (GitHub Actions)](#cicd-workflow-github-actions)
7. [Troubleshooting](#troubleshooting)
8. [Generalizing to Other Projects](#generalizing-to-other-projects)

---

## Overview

### What This Project Uses

- **Codacy Static Code Analysis** — Python (pylint), shell scripts, configuration files
- **SARIF Upload** — Standard Analysis Results Format for uploading analysis to Codacy
- **Quality Pipeline** — Local validation before push via `scripts/quality-pipeline.sh`
- **GitHub Actions** — Automated analysis on PR push and main branch updates
- **MCP (Model Context Protocol)** — Available via Hugging Face for programmatic access

### Architecture

```
Local Development                    GitHub Actions CI
┌─────────────────────┐             ┌──────────────────────────────┐
│ ~/.codacy/          │             │ secrets.CODACY_PROJECT_TOKEN │
│  ├─ account-token   │◄────────────┤ secrets.CODACY_ACCOUNT_TOKEN │
│  └─ {org}-{repo}.   │             │                              │
│     project-token   │             │ Environment Variables:       │
└─────────────────────┘             │  ├─ CODACY_USERNAME          │
         ▲                           │  ├─ CODACY_PROJECT_NAME      │
         │                           │  └─ CODACY_ORG_PROVIDER      │
         │                           └──────────────────────────────┘
    .envrc.local                                  ▼
    (sourced by direnv)             .github/workflows/
                                    dotfiles-validation.yml
         ▼                                        │
scripts/quality-pipeline.sh ◄───────────────────┘
 (codacy-cli analyze)
 (codacy-cli upload)
```

---

## LLM Agent Workflow

This section is written for Claude Code agents (and similar LLMs). It documents
the correct interaction pattern for Codacy operations.

### Token Loading Is Automatic

A user-global `SessionStart` hook (`~/.claude/hooks/load-project-env.sh`)
sources each project's `.envrc` / `.envrc.local` at session start and exports
the token allowlist into every Bash tool call. Variables loaded automatically:
`CODACY_ACCOUNT_TOKEN`, `CODACY_PROJECT_TOKEN`, `CODACY_USERNAME`,
`CODACY_PROJECT_NAME`, `CODACY_ORGANIZATION_PROVIDER`, `GITHUB_TOKEN`.

**Do not run `direnv allow`, `source .envrc.local`, or `cat ~/.codacy/...`.**
Tokens are already in the environment. Use tools directly.

If a tool returns 401/404: look for a `[claude-env]` diagnostic in session-start
output. Recovery command: `./setup repair-codacy-env`.

### Preferred Tool Order for Codacy Operations

1. **Read** — use Codacy MCP first:
   - `mcp__codacy__codacy_list_pull_request_issues` — issues blocking a PR
   - `mcp__codacy__codacy_get_repository_pull_request` — PR quality status
   - `mcp__codacy__codacy_get_file_issues` — issues in a specific file

2. **Analyze + upload** — use CLI + pipeline:
   - `scripts/quality-pipeline.sh --codacy-only` — analyze and upload current HEAD
   - `./setup ship <PR#>` — complete merge workflow (SARIF upload + poll + merge)

3. **Diagnose env** — only if tokens are missing:
   - `./setup repair-codacy-env` — rebuild `.envrc.local` from token files on disk
   - `./scripts/codacy-setup status` — check what's loaded/missing
   - `./scripts/codacy-setup repair` — auto-fix common issues

### Merging a PR via `setup ship`

`./setup ship <PR#>` is the canonical merge command. It:
1. Verifies `CODACY_PROJECT_TOKEN` is set (exits with repair hint if not)
2. Updates the branch against main
3. Runs `codacy-cli analyze --tool pylint --format sarif`
4. Uploads SARIF for HEAD and base SHA with `-o/-p/-r/-c/-t` flags
5. Polls the four required GitHub checks until all turn green
6. Squash-merges when status is CLEAN or UNSTABLE-but-green

Do not try to manually re-run individual steps unless `ship` itself is broken.

---

## Issues Fixed

### Problem 1: Missing Codacy Environment Variables

**Symptom:** `Error: failed to get page: request to https://app.codacy.com/api/v3/tools//patterns failed with status 404`

**Root Cause:** `codacy-cli` requires organization/project context to fetch tool patterns from Codacy API. Without these, it defaults to empty values, resulting in malformed URLs (`/tools//patterns`).

**Solution:**

```yaml
# .github/workflows/dotfiles-validation.yml
env:
  CODACY_ORGANIZATION_PROVIDER: gh        # GitHub
  CODACY_USERNAME: kairin                 # Your GitHub username
  CODACY_PROJECT_NAME: 000-dotfiles       # Repository name
  CODACY_ACCOUNT_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
  CODACY_API_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
  CODACY_PROJECT_TOKEN: ${{ secrets.CODACY_PROJECT_TOKEN }}
```

**When Applied:**
- GitHub Actions CI only (environment variables not needed locally if using `.envrc.local`)

**Generalization:**
- Replace `kairin` with your username
- Replace `000-dotfiles` with your repository name
- `CODACY_ORGANIZATION_PROVIDER` is `gh` for GitHub, `gl` for GitLab, `bb` for Bitbucket

---

### Problem 2: Missing GitHub Secrets

**Symptom:** `CODACY_PROJECT_TOKEN: ***` but upload still fails with 404

**Root Cause:** GitHub Actions doesn't have the token values. The `***` masking indicates the secret is defined but missing or empty.

**Solution:**

```bash
# Set secrets from local token files
gh secret set CODACY_PROJECT_TOKEN < ~/.codacy/{owner}-{repo}.project-token
gh secret set CODACY_ACCOUNT_TOKEN < ~/.codacy/account-token
```

**Verification:**
```bash
gh secret list | grep CODACY
```

**When Applied:**
- Once per repository, before first CI run

**Generalization:**
- For any repo integrating with Codacy, you need TWO secrets:
  - Project token (repo-specific, for uploading results)
  - Account token (org-wide, for fetching configuration and patterns)

---

### Problem 3: Missing Upload Flags

**Symptom:** Analysis runs but SARIF upload returns 404 after retries

**Root Cause:** `codacy-cli upload` command wasn't passing required `-o` (owner), `-p` (provider), `-r` (repository) flags. The command line becomes:
```bash
# WRONG
codacy-cli upload -s file.sarif -c {sha} -t {token}

# CORRECT
codacy-cli upload -s file.sarif -c {sha} -t {token} \
  -o {owner} -p {provider} -r {repo}
```

**Solution:**

```bash
# scripts/quality-pipeline.sh, upload_with_retry()
if codacy-cli upload \
  -s "$SARIF" \
  -c "$sha" \
  -t "$TOKEN" \
  -o "${CODACY_USERNAME:-}" \
  -p "${CODACY_ORGANIZATION_PROVIDER:-gh}" \
  -r "${CODACY_PROJECT_NAME:-}"; then
  return 0
fi
```

**When Applied:**
- Always, both local and CI
- Uses environment variables for values (set in `.envrc.local` locally, via env vars in CI)

**Generalization:**
- Any `codacy-cli upload` call requires these flags
- Can pass via CLI flags or environment variables (Codacy reads both)

---

### Problem 4: Shallow Clone Merge-Base Failure

**Symptom:** `DEBUG: BASE_SHA=origin/main` instead of actual commit hash

**Root Cause:** GitHub Actions uses `fetch-depth: 1` (shallow clone) to save bandwidth. In shallow clones:
- `git merge-base HEAD origin/main` fails (no shared history)
- Fallback `git rev-parse origin/main` may return string instead of hash
- Script tries to upload with "origin/main" as commit SHA → API returns 404

**Solution:**

```yaml
# .github/workflows/dotfiles-validation.yml
- name: Check out repository
  uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd
  with:
    fetch-depth: 0  # Full history, not shallow
```

AND

```bash
# scripts/quality-pipeline.sh
BASE_SHA=""
if git merge-base HEAD origin/main >/dev/null 2>&1; then
  BASE_SHA="$(git merge-base HEAD origin/main)"
elif git rev-parse origin/main >/dev/null 2>&1; then
  BASE_SHA="$(git rev-parse origin/main --quiet 2>/dev/null || echo "")"
fi
# BASE_SHA now safely empty if merge-base fails
```

**When Applied:**
- GitHub Actions: Use `fetch-depth: 0` to fetch full history
- Quality pipeline: Gracefully handle empty BASE_SHA (skip base upload if unavailable)

**Generalization:**
- Shallow clones (any CI with `fetch-depth: 1`) require special handling
- Options:
  1. **Recommended:** Use `fetch-depth: 0` (full history, still fast for most repos)
  2. **Alternative:** Gracefully fall back to HEAD-only upload if merge-base unavailable
  3. **Not Recommended:** Ignore failures silently (leads to silent data corruption)

### Root Cause Catalog

The following table maps recurring failures to their fixes. Each fix is in a
separate PR. This catalog exists to prevent re-discovering the same root causes.

| Issue | Symptom | Root Cause | Fix PR |
|-------|---------|------------|--------|
| Empty SARIF upload / 404 on upload | `codacy-cli upload` returns 404 | Missing `-o/-p/-r` flags; Codacy can't identify project | #192, fixed in ship-flags PR |
| Auth errors in fresh agent sessions | Agent can't use codacy-cli or Codacy MCP | `direnv` hasn't fired; tokens not in env | #192/#197, fixed by SessionStart hook |
| Stale `.envrc.local` | CODACY_PROJECT_TOKEN not exported | Managed block missing project token | #197/#198, fixed by `repair-codacy-env` |
| Shallow clone merge-base failure | `BASE_SHA=origin/main` (string, not SHA) | `fetch-depth: 1` in GitHub Actions | #192, fixed by `fetch-depth: 0` |
| codacy-cli 404 on analyze | `request to ...tools//patterns failed` | Missing org/project env vars for CLI auth | #192, fixed by env vars in CI workflow |
| Command injection warning | Codacy blocks PR for security violation | `subprocess.run(list(verify))` without validation | #192, fixed by type-checking verify arg |

---

## Token Management

### Local Setup

#### Step 1: Create Token Directory

```bash
mkdir -p ~/.codacy
chmod 700 ~/.codacy
```

#### Step 2: Obtain Tokens from Codacy Dashboard

**Account Token** (org-wide, for API access):
1. Navigate to https://app.codacy.com/account/settings/tokens
2. Generate API token
3. Save to `~/.codacy/account-token`

**Project Token** (repo-specific, for SARIF upload):
1. Navigate to https://app.codacy.com/gh/{owner}/{repo}/settings/integrations/github
2. Copy project token
3. Save to `~/.codacy/{owner}-{repo}.project-token` (e.g., `~/.codacy/kairin-000-dotfiles.project-token`)

#### Step 3: Set File Permissions

```bash
chmod 600 ~/.codacy/account-token
chmod 600 ~/.codacy/{owner}-{repo}.project-token
```

#### Step 4: Create `.envrc.local` (direnv)

```bash
cd /path/to/project
./setup repair-codacy-env
# OR manually:
cat > .envrc.local << 'EOF'
# BEGIN DOTFILES CODACY
export CODACY_ORGANIZATION_PROVIDER="gh"
export CODACY_USERNAME="your-github-username"
export CODACY_PROJECT_NAME="repo-name"
export CODACY_ACCOUNT_TOKEN="$(cat "$HOME/.codacy/account-token")"
export CODACY_API_TOKEN="$(cat "$HOME/.codacy/account-token")"
export CODACY_PROJECT_TOKEN="$(cat "$HOME/.codacy/your-username-repo-name.project-token")"
# END DOTFILES CODACY
EOF
direnv allow
```

#### Step 5: Verify Setup

```bash
# Check tokens are loaded
echo "Account: ${#CODACY_ACCOUNT_TOKEN}"   # Should print number (20-40)
echo "Project: ${#CODACY_PROJECT_TOKEN}"   # Should print number (32+)

# Check codacy-cli is available
codacy-cli --version
```

### CI Setup (GitHub Actions)

#### Step 1: Add Repository Secrets

```bash
# From local machine
gh secret set CODACY_PROJECT_TOKEN < ~/.codacy/{owner}-{repo}.project-token
gh secret set CODACY_ACCOUNT_TOKEN < ~/.codacy/account-token

# Verify
gh secret list | grep CODACY
```

#### Step 2: Configure Workflow Environment Variables

Already done in `.github/workflows/dotfiles-validation.yml`:
```yaml
env:
  CODACY_ORGANIZATION_PROVIDER: gh
  CODACY_USERNAME: your-username
  CODACY_PROJECT_NAME: repo-name
  CODACY_ACCOUNT_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
  CODACY_API_TOKEN: ${{ secrets.CODACY_ACCOUNT_TOKEN }}
  CODACY_PROJECT_TOKEN: ${{ secrets.CODACY_PROJECT_TOKEN }}
```

**Note:** Don't commit actual values; use `${{ secrets.NAME }}` syntax.

### Token Rotation

When rotating tokens:

```bash
# 1. Generate new token in Codacy dashboard
# 2. Update local file
echo "new-token-value" > ~/.codacy/account-token

# 3. Update GitHub secret
gh secret set CODACY_ACCOUNT_TOKEN < ~/.codacy/account-token

# 4. Verify in next CI run
```

---

## Local Development

### Before Pushing

```bash
# Source the environment
direnv allow
source .envrc.local

# Run quality pipeline
./setup quality

# OR manually
bash scripts/quality-pipeline.sh

# Expected output:
# ✓ Quality pipeline complete
# (Response: 200 OK from both HEAD and BASE uploads)
```

### Debugging

#### Check Token Access

```bash
# Verify tokens are readable
wc -c ~/.codacy/account-token ~/.codacy/kairin-000-dotfiles.project-token

# Test API access
TOKEN=$(cat ~/.codacy/kairin-000-dotfiles.project-token)
curl -H "api-token: $TOKEN" \
  "https://api.codacy.com/2.0/commit/$(git rev-parse HEAD)/quality-status"
```

#### Check SARIF Generation

```bash
# Run pylint directly
codacy-cli analyze --tool pylint --format sarif -o /tmp/test.sarif

# Verify SARIF file exists and has content
ls -lh /tmp/test.sarif
jq '.version' /tmp/test.sarif  # Should print "2.1.0"
```

#### Check merge-base Resolution

```bash
# Verify both SHAs are valid
git rev-parse HEAD
git merge-base HEAD origin/main 2>/dev/null || echo "merge-base failed"
git rev-parse origin/main
```

---

## CI/CD Workflow (GitHub Actions)

### Workflow File Location

`.github/workflows/dotfiles-validation.yml`

### Execution Flow

1. **Trigger:** Push to PR or main branch
2. **Checkout:** Full history (`fetch-depth: 0`)
3. **Codacy Status Check:** Query API for existing results
4. **Unit Tests:** `uv run python -m unittest discover -s tests`
5. **Coverage:** `coverage xml`
6. **Codacy CLI Download:** Latest codacy-cli-v2 from GitHub releases
7. **SARIF Analysis:** `codacy-cli analyze --tool pylint --format sarif`
8. **SARIF Upload (HEAD):** `codacy-cli upload -c {HEAD_SHA} ...`
9. **SARIF Upload (BASE):** `codacy-cli upload -c {BASE_SHA} ...`
10. **Coverage Upload:** `codacy/codacy-coverage-reporter-action`
11. **Status Check:** Query Codacy API for final status

### Key Environment Variables Set

| Variable | Value | Source | Purpose |
|----------|-------|--------|---------|
| `CODACY_ORGANIZATION_PROVIDER` | `gh` | Hardcoded | GitHub provider identifier |
| `CODACY_USERNAME` | `kairin` | Hardcoded | GitHub username |
| `CODACY_PROJECT_NAME` | `000-dotfiles` | Hardcoded | Repository name |
| `CODACY_PROJECT_TOKEN` | `***` | `secrets.CODACY_PROJECT_TOKEN` | Authenticate SARIF uploads |
| `CODACY_ACCOUNT_TOKEN` | `***` | `secrets.CODACY_ACCOUNT_TOKEN` | Fetch API patterns/config |
| `CODACY_API_TOKEN` | `***` | `secrets.CODACY_ACCOUNT_TOKEN` | Alias for account token |
| `GH_TOKEN` | `${{ github.token }}` | GitHub Actions | Git operations |

### Preventing Silent Failures

The pipeline includes safeguards:

```bash
# validate_sha() in scripts/quality-pipeline.sh
# Fails immediately if SHA is not 40-char hex (catches "origin/main" mistakes)
if [[ ! "$sha" =~ ^[0-9a-f]{40}$ ]]; then
  echo "FATAL: Invalid commit SHA: '$sha'"
  echo "This usually means git merge-base failed in a shallow clone."
  exit 1
fi
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (tests + coverage + Codacy upload all passed) |
| 1 | Failure (tests, coverage, analysis, or upload failed) |
| 3 | Prerequisite missing (tool not on PATH, env var unset) |

---

## Troubleshooting

### Symptom: "codacy-cli-v2 binary not found after install"

**Cause:** Download failed or curl had no internet

**Fix:**
```bash
# In .github/workflows/dotfiles-validation.yml
# Ensure curl is available and network is working
bash <(curl -Ls https://raw.githubusercontent.com/codacy/codacy-cli-v2/main/codacy-cli.sh) download
```

### Symptom: "Error sending results, status code: 404"

**Causes:**
1. Invalid commit SHA (e.g., "origin/main" instead of hash)
2. Project token doesn't match the organization/project
3. Commit isn't registered in Codacy yet

**Fixes:**
- Check SHA with: `git rev-parse HEAD` (should be 40-char hex)
- Verify token at: https://app.codacy.com/account/settings/tokens
- For new repos, Codacy needs webhook to register commits

### Symptom: "CODACY_PROJECT_TOKEN not configured"

**Cause:** Secret not set in GitHub repository settings

**Fix:**
```bash
gh secret set CODACY_PROJECT_TOKEN < ~/.codacy/kairin-000-dotfiles.project-token
```

### Symptom: "tools//patterns failed with status 404"

**Cause:** Missing environment variables (`CODACY_USERNAME`, `CODACY_PROJECT_NAME`)

**Note:** This is a warning and non-fatal. The upload still proceeds.

**Fix:** Ensure workflow has:
```yaml
env:
  CODACY_ORGANIZATION_PROVIDER: gh
  CODACY_USERNAME: your-username
  CODACY_PROJECT_NAME: repo-name
```

### Symptom: "Upload attempt 1 failed for origin/main"

**Cause:** Shallow clone + `git merge-base` failed, resulting in "origin/main" as SHA string

**Fix:**
```yaml
# In checkout step:
with:
  fetch-depth: 0  # Use full history
```

---

## Generalizing to Other Projects

### Checklist for Adding Codacy to a New Repository

#### 1. Setup Codacy Project

- [ ] Create project at https://app.codacy.com
- [ ] Generate project token in repository settings
- [ ] Generate account token at https://app.codacy.com/account/settings/tokens

#### 2. Local Development

- [ ] Create `~/.codacy/account-token` with account token
- [ ] Create `~/.codacy/{owner}-{repo}.project-token` with project token
- [ ] Add to `.envrc.local`:
  ```bash
  export CODACY_ORGANIZATION_PROVIDER="gh"  # or "gl", "bb"
  export CODACY_USERNAME="your-username"
  export CODACY_PROJECT_NAME="repo-name"
  export CODACY_ACCOUNT_TOKEN="$(cat ~/.codacy/account-token)"
  export CODACY_API_TOKEN="$(cat ~/.codacy/account-token)"
  export CODACY_PROJECT_TOKEN="$(cat ~/.codacy/{owner}-{repo}.project-token)"
  ```

#### 3. GitHub Actions Workflow

- [ ] Create `.github/workflows/codacy-validation.yml` with:
  - Checkout with `fetch-depth: 0`
  - `CODACY_*` environment variables (hardcoded values)
  - Token secrets from `secrets.CODACY_PROJECT_TOKEN` and `secrets.CODACY_ACCOUNT_TOKEN`
  - Download and run `codacy-cli analyze`
  - Upload SARIF with `codacy-cli upload` (include `-o`, `-p`, `-r` flags)

#### 4. GitHub Repository Settings

- [ ] Add secret: `CODACY_PROJECT_TOKEN`
- [ ] Add secret: `CODACY_ACCOUNT_TOKEN`

#### 5. Quality Pipeline Script

- [ ] Create `scripts/quality-pipeline.sh` (or use template from this repo)
- [ ] Include SHA validation: `validate_sha()` function
- [ ] Include graceful fallback for `BASE_SHA` in shallow clones
- [ ] Run locally before pushing: `./setup quality` or `bash scripts/quality-pipeline.sh`

### Differences by Provider

#### GitHub

```
Organization Provider: gh
Username: GitHub username
Project Name: Repository name
URL Pattern: https://api.codacy.com/...
```

#### GitLab

```
Organization Provider: gl
Username: GitLab username
Project Name: Repository slug or ID
URL Pattern: https://api.codacy.com/... (same API)
```

#### Bitbucket

```
Organization Provider: bb
Username: Bitbucket workspace
Project Name: Repository slug
URL Pattern: https://api.codacy.com/... (same API)
```

### Configuration Variations by Language

#### Python (Like This Project)

```bash
codacy-cli analyze --tool pylint --format sarif -o /tmp/pylint.sarif
```

#### JavaScript/TypeScript

```bash
codacy-cli analyze --tool eslint --format sarif -o /tmp/eslint.sarif
```

#### Go

```bash
codacy-cli analyze --tool golint --format sarif -o /tmp/golint.sarif
```

#### Multiple Tools

```bash
# Run all configured tools (via .codacy/codacy.yaml)
codacy-cli analyze --format sarif -o /tmp/analysis.sarif
```

---

## Key Takeaways

1. **Tokens Are Critical:** Two tokens (account + project) are required, and they're environment-specific
2. **Environment Variables Are Required:** `codacy-cli` needs organization/project context or it fails silently
3. **Upload Requires Flags:** Always pass `-o`, `-p`, `-r` to `codacy-cli upload`
4. **Shallow Clones Are Problematic:** Use `fetch-depth: 0` in CI or handle merge-base failures gracefully
5. **Validate Early:** Use `validate_sha()` to fail fast on invalid commit hashes
6. **Test Locally First:** Run `./setup quality` before pushing to catch issues early

---

## Related Files

- Workflow: `.github/workflows/dotfiles-validation.yml`
- Pipeline Script: `scripts/quality-pipeline.sh`
- Codacy Config: `.codacy.yml`, `.codacy/codacy.yaml`
- Envrc Template: `claude/codacy-envrc.template` (if applicable)
- Environment Setup: `.envrc.local` (local development only, not in git)
