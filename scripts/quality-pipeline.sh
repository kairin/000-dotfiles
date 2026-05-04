#!/usr/bin/env bash
# Local quality pipeline.
#
# Stages:
#   1. Unit tests
#   2. Coverage XML
#   3. Pylint analysis (SARIF)
#   4. Coverage upload to Codacy
#   5. SARIF upload to Codacy (HEAD)
#   6. SARIF upload to Codacy (merge-base) -- so PR diff has a baseline
#   7. Codacy server-side gate (informational)
#
# Modes:
#   (default)        run stages 1-7
#   --codacy-only    run only stages 3, 5, 6, 7 against working tree HEAD.
#                    Used by the pre-push hook so the static-analysis SARIF
#                    is uploaded BEFORE the push completes; lets the four
#                    required GitHub checks go green automatically.
#
# Exit codes:
#   0  pipeline passed
#   1  a stage failed (tests, coverage, analysis, upload)
#   3  prerequisite missing (tool not on PATH, or required env var unset)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

CODACY_ONLY=0
if [[ "${1:-}" == "--codacy-only" ]]; then
  CODACY_ONLY=1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# ----------------------------------------------------------------------------
# Prerequisite validation
# ----------------------------------------------------------------------------
missing=()

required_cmds=(codacy-cli)
if (( CODACY_ONLY == 0 )); then
  required_cmds=(gh uv codacy-cli)
fi

for cmd in "${required_cmds[@]}"; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing+=("command not on PATH: $cmd")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo "ERROR: quality pipeline prerequisites are not satisfied:" >&2
  for item in "${missing[@]}"; do
    echo "  - $item" >&2
  done
  echo "" >&2
  echo "Hint: ensure tools are bootstrapped (./setup install-tools) and that" >&2
  echo "      .envrc.local has been sourced (direnv allow, or 'source .envrc.local')." >&2
  exit 3
fi

# Token may be absent in local dev; we skip the upload then rather than fail.
TOKEN="${CODACY_PROJECT_TOKEN:-}"

# ----------------------------------------------------------------------------
# Stages 1-2: tests + coverage (skipped in --codacy-only mode)
# ----------------------------------------------------------------------------
if (( CODACY_ONLY == 0 )); then
  echo -e "${CYAN}[STAGE 1/7] Running unit tests...${NC}"
  uv run python -m unittest discover -s tests

  echo -e "${CYAN}[STAGE 2/7] Generating coverage XML...${NC}"
  uv run --with coverage==7.5.4 coverage run -m unittest discover -s tests
  uv run --with coverage==7.5.4 coverage xml
fi

# ----------------------------------------------------------------------------
# Stage 3: pylint SARIF analysis
# ----------------------------------------------------------------------------
echo -e "\n${CYAN}[STAGE 3/7] Running pylint analysis...${NC}"
SARIF="/tmp/pylint-$$.sarif"
codacy-cli analyze --tool pylint --format sarif -o "$SARIF"

# ----------------------------------------------------------------------------
# Stage 4: coverage upload — handled by .github/workflows/dotfiles-validation.yml
# via codacy/codacy-coverage-reporter-action. We do NOT upload coverage here:
# `codacy-cli upload` accepts only SARIF, not coverage.xml, and would die with
# "invalid character '<'", killing the pipeline before SARIF upload runs.
# Local push: the workflow uploads coverage on its own schedule.
# ----------------------------------------------------------------------------
HEAD_SHA="$(git rev-parse HEAD)"

# ----------------------------------------------------------------------------
# Stages 5-6: SARIF upload for HEAD and merge-base (with retry)
# ----------------------------------------------------------------------------
echo -e "\n${CYAN}[STAGE 5/7] CODACY STATIC CODE ANALYSIS — SARIF UPLOAD${NC}"

if [[ -z "$TOKEN" ]]; then
  echo -e "${YELLOW}⚠ CODACY_PROJECT_TOKEN not set — skipping SARIF upload (the GH App may not post the static-analysis check without it).${NC}"
elif [[ "${SKIP_CODACY_UPLOAD:-0}" = "1" ]]; then
  echo -e "${YELLOW}⚠ SKIP_CODACY_UPLOAD=1 — skipping SARIF upload by request.${NC}"
else
  # Robustly resolve the base branch for multi-commit uploads.
  # On GitHub Actions, GITHUB_BASE_REF is set for pull requests.
  TARGET_BRANCH="${GITHUB_BASE_REF:-main}"
  BASE_REF="origin/$TARGET_BRANCH"
  if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
    BASE_REF="$TARGET_BRANCH"
  fi

  BASE_SHA="$(git merge-base HEAD "$BASE_REF" 2>/dev/null || git rev-parse "$BASE_REF" 2>/dev/null || echo "")"

  upload_with_retry() {
    local sha="$1"
    local attempt

    # Validation: Codacy API requires a full 40-character hex SHA.
    if [[ ! "$sha" =~ ^[0-9a-f]{40}$ ]]; then
      echo -e "${YELLOW}⚠ Skipping upload for invalid SHA: '$sha' (expected 40-character hex).${NC}"
      # If this is the HEAD upload, we might want to fail, but if it's the 
      # merge-base and we can't find it, we just warn and continue.
      return 0
    fi

    for attempt in 1 2; do
      if codacy-cli upload -s "$SARIF" -c "$sha" -t "$TOKEN"; then
        return 0
      fi
      echo -e "${YELLOW}Upload attempt $attempt failed for $sha; retrying in 5s...${NC}"
      sleep 5
    done
    echo -e "${RED}✗ Codacy upload failed twice for $sha${NC}"
    return 1
  }

  upload_with_retry "$HEAD_SHA" || exit 1

  echo -e "\n${CYAN}[STAGE 6/7] SARIF upload for merge-base...${NC}"
  if [[ -n "$BASE_SHA" && "$BASE_SHA" != "$HEAD_SHA" ]]; then
    upload_with_retry "$BASE_SHA" || exit 1
    echo -e "${GREEN}✓ SARIF uploaded for HEAD ($HEAD_SHA) and base ($BASE_SHA).${NC}"
  else
    echo -e "${GREEN}✓ HEAD is the merge-base; single upload covers PR diff.${NC}"
  fi
fi

rm -f "$SARIF"

# ----------------------------------------------------------------------------
# Stage 7: server-side gate (informational)
# ----------------------------------------------------------------------------
echo -e "\n${CYAN}[STAGE 7/7] Codacy server-side gate (informational)${NC}"
echo "  Codacy processes the uploaded artifacts asynchronously."
echo "  The four required GitHub checks (incl. 'Codacy Static Code Analysis')"
echo "  will turn green automatically once Codacy finishes processing."

echo ""
echo -e "${GREEN}✓ Quality pipeline complete${NC}"
exit 0
