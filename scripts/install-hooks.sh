#!/bin/bash
# Install git hooks for this project
# Run with: ./scripts/install-hooks.sh

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Copy pre-push hook from scripts directory
HOOK_SOURCE="$REPO_ROOT/scripts/hooks/pre-push"

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "Error: Hook source not found at $HOOK_SOURCE"
    exit 1
fi

cp "$HOOK_SOURCE" "$HOOKS_DIR/pre-push"
chmod +x "$HOOKS_DIR/pre-push"

echo "✓ Git hooks installed successfully"
echo ""
echo "Hooks installed:"
echo "  • pre-push: Enforces quality checks and blocks direct pushes to main"
echo ""
echo "Quality gate checks:"
echo "  ✓ HARD: All unit tests must pass"
echo "  ✓ HARD: Modified code complexity ≤ A grade (avg < 5.0)"
echo "  ✓ HARD: Pushes to refs/heads/main are blocked; feature branches are allowed"
echo "  ⚠ WARN: Missing type annotations"
echo "  ⚠ WARN: Lines exceeding 79 characters"
echo ""
echo "Installed at: $HOOKS_DIR/pre-push"
echo "To bypass: git push --no-verify"
