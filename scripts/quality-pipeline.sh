#!/usr/bin/env bash
# Local quality pipeline: tests → coverage → static analysis → upload to Codacy.
# Invoked from scripts/hooks/pre-push and `setup quality`.
# Fails fast on any step. Blocks if Codacy upload fails.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

SHA="$(git rev-parse HEAD)"
TOKEN="${CODACY_PROJECT_TOKEN:?CODACY_PROJECT_TOKEN must be set (source .envrc.local?)}"

if ! command -v codacy-cli >/dev/null 2>&1; then
  echo "ERROR: codacy-cli not found in PATH. Install via setup bootstrap." >&2
  exit 1
fi

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

echo "Pipeline complete. Codacy will post status checks to GitHub when processing finishes."
