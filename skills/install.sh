#!/usr/bin/env bash
# Install BCM Codex skills into the current user's Codex home.
# Source of truth: this repository's skills/ directory.

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST_DIR="${CODEX_HOME:-$HOME/.codex}/skills"

skills=(
  "bcm-direnv-codacy"
  "bcm-github-cicd"
)

mkdir -p "$DEST_DIR"

for skill in "${skills[@]}"; do
  src="$SCRIPT_DIR/$skill"
  dest="$DEST_DIR/$skill"

  if [[ ! -d "$src" ]]; then
    echo "ERROR: missing skill directory: $src" >&2
    exit 1
  fi

  rm -rf "$dest"
  cp -R "$src" "$dest"
  echo "Installed $skill -> $dest"
done

echo "All BCM skills are installed in $DEST_DIR"
