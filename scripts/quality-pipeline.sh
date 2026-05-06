#!/usr/bin/env bash
# Local quality pipeline.
#
# Stages:
#   1. Unit tests
#   2. Coverage XML
#   3. Pylint analysis (SARIF)           -- skipped when no token
#   4. (reserved: coverage upload via CI workflow action)
#   5. SARIF upload to Codacy (HEAD)     -- skipped when no token
#   6. SARIF upload to Codacy (merge-base)
#   7. Codacy server-side gate (informational)
#
# Modes:
#   (default)        run stages 1-7 (stages 3-7 need CODACY_PROJECT_TOKEN)
#   --codacy-only    run only stages 3, 5, 6, 7 against working tree HEAD.
#                    Used by ./setup ship and the pre-push hook.
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

# Token may be absent in CI; affects which stages run.
TOKEN="${CODACY_PROJECT_TOKEN:-}"

# ----------------------------------------------------------------------------
# Prerequisite validation
# ----------------------------------------------------------------------------
missing=()

if (( CODACY_ONLY == 1 )); then
  required_cmds=(codacy-cli)
elif [[ -n "$TOKEN" ]]; then
  required_cmds=(uv codacy-cli)
else
  required_cmds=(uv)
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

# ----------------------------------------------------------------------------
# Stages 1-2: tests + coverage (skipped in --codacy-only mode)
# ----------------------------------------------------------------------------
if (( CODACY_ONLY == 0 )); then
  echo -e "${CYAN}[STAGE 1/7] Running unit tests...${NC}"
  uv run python -m unittest discover -s tests

  echo -e "${CYAN}[STAGE 2/7] Generating coverage XML...${NC}"
  uv run --with coverage==7.5.4 coverage run -m unittest discover -s tests
  uv run --with coverage==7.5.4 coverage xml

  if [[ -z "$TOKEN" ]]; then
    echo -e "\n${YELLOW}No CODACY_PROJECT_TOKEN — skipping Codacy analysis and upload.${NC}"
    echo "  Run: ./setup ship <PR#>   (uploads SARIF and merges via the full pipeline)"
    echo ""
    echo -e "${GREEN}✓ Quality pipeline complete (tests + coverage)${NC}"
    exit 0
  fi
fi

# ----------------------------------------------------------------------------
# Stage 3: pylint SARIF analysis
# ----------------------------------------------------------------------------
echo -e "\n${CYAN}[STAGE 3/7] Running pylint analysis...${NC}"
SARIF="/tmp/pylint-$$.sarif"
# codacy-cli analyze propagates pylint's bitmask exit code (28 = W+R+C found),
# which is not a pipeline failure — violations are expected and reported via
# SARIF. Only fail if the SARIF file was not produced at all.
analyze_rc=0
codacy-cli analyze --tool pylint --format sarif -o "$SARIF" || analyze_rc=$?
if (( analyze_rc != 0 )); then
  echo -e "${YELLOW}⚠ codacy-cli analyze exited $analyze_rc (pylint violations found; will be uploaded to Codacy)${NC}"
fi
[[ -s "$SARIF" ]] || { echo -e "${RED}✗ codacy-cli analyze produced no SARIF output${NC}" >&2; exit 1; }

# ----------------------------------------------------------------------------
# Stage 4: coverage upload — handled by .github/workflows/dotfiles-validation.yml
# via codacy/codacy-coverage-reporter-action. We do NOT upload coverage here.
# ----------------------------------------------------------------------------
HEAD_SHA="$(git rev-parse HEAD)"

# ----------------------------------------------------------------------------
# Stages 5-6: SARIF upload for HEAD and merge-base (with retry)
# ----------------------------------------------------------------------------
echo -e "\n${CYAN}[STAGE 5/7] CODACY STATIC CODE ANALYSIS — SARIF UPLOAD${NC}"
echo "DEBUG: HEAD_SHA=$HEAD_SHA" >&2

if [[ "${SKIP_CODACY_UPLOAD:-0}" = "1" ]]; then
  echo -e "${YELLOW}⚠ SKIP_CODACY_UPLOAD=1 — skipping SARIF upload by request.${NC}"
else
  BASE_SHA="$(git merge-base HEAD origin/main 2>/dev/null || git rev-parse origin/main 2>/dev/null || echo "")"
  echo "DEBUG: BASE_SHA=$BASE_SHA" >&2

  upload_with_retry() {
    local sha="$1"
    local attempt
    for attempt in 1 2; do
      if codacy-cli upload \
        -s "$SARIF" \
        -c "$sha" \
        -t "$TOKEN" \
        -o "${CODACY_USERNAME:-}" \
        -p "${CODACY_ORGANIZATION_PROVIDER:-gh}" \
        -r "${CODACY_PROJECT_NAME:-}"; then
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
