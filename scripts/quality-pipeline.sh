#!/usr/bin/env bash
# Local quality pipeline: tests -> coverage -> static analysis -> upload to Codacy.
# Invoked from scripts/hooks/pre-push and `setup quality`.
# Fails fast on any step. Blocks if Codacy upload fails.
#
# Exit codes:
#   0  pipeline passed (reserved; not used while Stage 7 is a manual gate)
#   1  a stage failed (tests, coverage, analysis, upload)
#   2  local stages 1-5 passed but Stage 7 is a manual Codacy MCP gate
#      (callers know auto-pass did NOT happen; operator must verify)
#   3  prerequisite missing (tool not on PATH, or required env var unset)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# ----------------------------------------------------------------------------
# Prerequisite validation: check everything up front, report all problems,
# then exit 3 if anything is missing. Avoids the "fix one, hit the next" loop.
# ----------------------------------------------------------------------------
missing=()

for cmd in gh uv codacy-cli; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing+=("command not on PATH: $cmd")
  fi
done

# CODACY_PROJECT_TOKEN is what `codacy-cli upload` actually uses.
# CODACY_ACCOUNT_TOKEN gates Codacy MCP availability for the operator.
# GITHUB_TOKEN gates gh CLI auth and any GitHub MCP usage from agents.
for var in CODACY_PROJECT_TOKEN CODACY_ACCOUNT_TOKEN GITHUB_TOKEN; do
  if [[ -z "${!var:-}" ]]; then
    missing+=("env var unset or empty: $var")
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

SHA="$(git rev-parse HEAD)"
TOKEN="$CODACY_PROJECT_TOKEN"

# ----------------------------------------------------------------------------
# Pipeline stages
# ----------------------------------------------------------------------------
echo "[1/5] Running unit tests..."
uv run python -m unittest discover -s tests

echo "[2/5] Generating coverage..."
uv run --with coverage==7.5.4 coverage run -m unittest discover -s tests
uv run --with coverage==7.5.4 coverage xml

echo "[3/5] Running pylint analysis..."
codacy-cli analyze --tool pylint --format sarif -o pylint.sarif

echo "[4/5] Uploading coverage to Codacy (commit $SHA)..."
codacy-cli upload -s coverage.xml -c "$SHA" -t "$TOKEN"

echo "[5/5] Uploading pylint analysis to Codacy (commit $SHA)..."
codacy-cli upload -s pylint.sarif -c "$SHA" -t "$TOKEN"

echo ""
echo "Stage 7 (Codacy server-side gate): MANUAL"
echo "  Local stages 1-5 passed. Codacy will process the uploaded artifacts"
echo "  asynchronously. To verify the gate result, invoke the Codacy MCP tool"
echo "  'codacy_get_repository_pull_request' from a Claude Code session, or"
echo "  watch the GitHub PR status checks."
echo ""
echo "Exiting 2: local stages succeeded but Stage 7 is a manual gate, NOT an auto-pass."
exit 2
