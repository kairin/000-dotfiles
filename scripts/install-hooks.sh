#!/bin/bash
# Install git hooks for this project
# Run with: ./scripts/install-hooks.sh

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Create pre-push hook
cat > "$HOOKS_DIR/pre-push" << 'HOOK'
#!/bin/bash

# Pre-push hook: enforce quality checks before pushing to remote
# Focuses on newly modified files to avoid blocking on pre-existing issues
# Bypass with: git push --no-verify (not recommended)

set -e
set -o pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Running Pre-Push Quality Checks${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"

FAILED=0

# ============================================================================
# 1. UNIT TESTS (Hard requirement - always run)
# ============================================================================
echo -e "\n${YELLOW}[1/4] Running unit tests...${NC}"
if uv run python -m unittest discover -s tests 2>&1 | tail -3; then
    echo -e "${GREEN}✓ All unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed - BLOCKING${NC}"
    FAILED=1
fi

# ============================================================================
# 2. COMPLEXITY CHECK (Only for modified Python files)
# ============================================================================
echo -e "\n${YELLOW}[2/4] Checking complexity of modified files...${NC}"

# Get list of modified Python files in this branch (not yet in main)
MODIFIED_FILES=$(git diff origin/main...HEAD --name-only --diff-filter=ACM | grep '\.py$' | grep -E 'dotfiles_tools/(doctor|installer)\.py' || echo "")

if [ -z "$MODIFIED_FILES" ]; then
    echo -e "${GREEN}✓ No relevant modified files to check${NC}"
else
    echo "   Files to check: $MODIFIED_FILES"

    # Check each modified file
    for file in $MODIFIED_FILES; do
        echo "   Analyzing: $file"
        RESULT=$(uv run --with radon radon cc "$file" -a 2>&1 | tail -1)
        echo "   $RESULT"

        # Extract average complexity (should be < 5 for new code)
        AVG=$(echo "$RESULT" | grep -oE "[0-9]+\.[0-9]+" | head -1 || echo "0")
        if (( $(echo "$AVG > 5" | bc -l) )); then
            echo -e "   ${RED}✗ Average complexity $AVG exceeds 5.0${NC}"
            FAILED=1
        fi
    done

    if [ "$FAILED" -eq 0 ]; then
        echo -e "${GREEN}✓ Modified files meet complexity standards${NC}"
    fi
fi

# ============================================================================
# 3. TYPE ANNOTATIONS CHECK (Warning only)
# ============================================================================
echo -e "\n${YELLOW}[3/4] Checking type annotations in modified files...${NC}"

if [ -z "$MODIFIED_FILES" ]; then
    echo -e "${GREEN}✓ No relevant modified files to check${NC}"
else
    MISSING=0
    for file in $MODIFIED_FILES; do
        # Count functions without return type annotations (rough check)
        MISSING_COUNT=$(grep -n "^def " "$file" | grep -v " -> " | grep -v "^[[:space:]]*def _" | wc -l || echo "0")
        if [ "$MISSING_COUNT" -gt 0 ]; then
            echo -e "   ${YELLOW}⚠ $file: $MISSING_COUNT public functions may lack return types${NC}"
            MISSING=$((MISSING + MISSING_COUNT))
        fi
    done

    if [ "$MISSING" -eq 0 ]; then
        echo -e "${GREEN}✓ Type annotations look good${NC}"
    else
        echo -e "   (This is a warning, not a blocker)"
    fi
fi

# ============================================================================
# 4. LINE LENGTH CHECK (Warning only)
# ============================================================================
echo -e "\n${YELLOW}[4/4] Checking line length in modified files...${NC}"

if [ -z "$MODIFIED_FILES" ]; then
    echo -e "${GREEN}✓ No relevant modified files to check${NC}"
else
    LONG=0
    for file in $MODIFIED_FILES; do
        # Count lines > 79 chars
        LONG_COUNT=$(awk 'length > 79' "$file" | wc -l || echo "0")
        if [ "$LONG_COUNT" -gt 0 ]; then
            echo -e "   ${YELLOW}⚠ $file: $LONG_COUNT lines exceed 79 characters${NC}"
            LONG=$((LONG + LONG_COUNT))
        fi
    done

    if [ "$LONG" -eq 0 ]; then
        echo -e "${GREEN}✓ Line lengths are good${NC}"
    else
        echo -e "   (This is a warning, not a blocker)"
    fi
fi

# ============================================================================
# RESULT
# ============================================================================
echo -e "\n${BLUE}════════════════════════════════════════════════════════${NC}"

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo -e "${BLUE}Ready to push to remote${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"
    exit 0
else
    echo -e "${RED}✗ Critical checks failed!${NC}"
    echo -e "${RED}Fix the issues above before pushing.${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}\n"
    echo -e "${YELLOW}To bypass (not recommended): git push --no-verify${NC}\n"
    exit 1
fi
HOOK

chmod +x "$HOOKS_DIR/pre-push"

echo "✓ Git hooks installed successfully"
echo ""
echo "Hooks installed:"
echo "  • pre-push: Enforces quality checks before pushing"
echo ""
echo "Quality gate checks:"
echo "  ✓ HARD: All unit tests must pass"
echo "  ✓ HARD: Modified code complexity ≤ A grade (avg < 5.0)"
echo "  ⚠ WARN: Missing type annotations"
echo "  ⚠ WARN: Lines exceeding 79 characters"
echo ""
echo "To bypass: git push --no-verify"
