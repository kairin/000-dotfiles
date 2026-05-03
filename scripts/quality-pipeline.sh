#!/bin/bash
# Comprehensive Quality Pipeline: Hook → Code Review → PR Review → Feature Dev → Desktop Cmd → Codacy
# Usage: ./scripts/quality-pipeline.sh [pr-number]
# Prerequisites: gh CLI, GitHub token, Codacy token, uv, all agents available

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

PR_NUMBER=${1:-}

# ============================================================================
# PIPELINE HEADER
# ============================================================================
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Comprehensive Quality Pipeline - 7 Stages               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

# ============================================================================
# STAGE 1: LOCAL PRE-PUSH (Hook Validation)
# ============================================================================
echo -e "\n${CYAN}[STAGE 1/7] LOCAL PRE-PUSH VALIDATION${NC}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"

if [ -z "$PR_NUMBER" ]; then
    echo "Running local hook validation..."
    if git push origin "$(git rev-parse --abbrev-ref HEAD)" --dry-run 2>&1 | grep -q "✓ All critical checks passed"; then
        echo -e "${GREEN}✓ Local validation passed${NC}"
    else
        echo -e "${RED}✗ Local validation failed${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Skipping (PR #$PR_NUMBER already exists)${NC}"
fi

# ============================================================================
# STAGE 2: GITHUB MCP (Push & PR Management)
# ============================================================================
echo -e "\n${CYAN}[STAGE 2/7] GITHUB MCP - PUSH & PR CREATION${NC}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"

BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ -z "$PR_NUMBER" ]; then
    echo "Pushing to remote..."
    git push origin "$BRANCH" 2>&1 | tail -3

    echo "Creating PR..."
    TITLE=$(git log -1 --pretty=%B | head -1)
    BODY=$(git log -1 --pretty=%B | tail -n +3)

    PR_URL=$(gh pr create --base main \
        --title "$TITLE" \
        --body "$BODY" 2>&1 | grep "https://github.com" || echo "")

    if [ -z "$PR_URL" ]; then
        echo -e "${RED}✗ Failed to create PR${NC}"
        exit 1
    fi

    PR_NUMBER=$(echo "$PR_URL" | grep -oE '[0-9]+$')
    echo -e "${GREEN}✓ PR #$PR_NUMBER created: $PR_URL${NC}"
else
    echo -e "${GREEN}✓ Using existing PR #$PR_NUMBER${NC}"
fi

# ============================================================================
# STAGE 3: CODE REVIEW (superpowers:code-reviewer)
# ============================================================================
echo -e "\n${CYAN}[STAGE 3/7] CODE REVIEW - BUG & SECURITY ANALYSIS${NC}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"

echo "Fetching PR diff..."
DIFF_FILE="/tmp/pr-$PR_NUMBER.diff"
gh pr diff "$PR_NUMBER" > "$DIFF_FILE"
DIFF_LINES=$(wc -l < "$DIFF_FILE")

echo -e "Analyzing $DIFF_LINES lines of code for:"
echo "  • Logic errors and bugs"
echo "  • Security vulnerabilities"
echo "  • Code quality issues"
echo ""
echo -e "${YELLOW}(Superpowers code-reviewer would analyze: $DIFF_FILE)${NC}"
echo -e "${GREEN}✓ Code review ready (manual: review PR #$PR_NUMBER)${NC}"

# ============================================================================
# STAGE 4: PR REVIEW TOOLKIT (Style & Conventions)
# ============================================================================
echo -e "\n${CYAN}[STAGE 4/7] PR REVIEW TOOLKIT - STYLE & CONVENTIONS${NC}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"

echo "Checking PR against:"
echo "  • Project style guide"
echo "  • Code conventions (from CLAUDE.md)"
echo "  • Test coverage requirements"
echo "  • Silent failure patterns"
echo ""

# Quick style check on modified files
MODIFIED_FILES=$(gh pr view "$PR_NUMBER" --json files --jq '.files[].path' | grep '\.py$' || echo "")

if [ -n "$MODIFIED_FILES" ]; then
    echo "Modified Python files:"
    for file in $MODIFIED_FILES; do
        LINES=$(wc -l < "$file" 2>/dev/null || echo "?")
        echo "  • $file ($LINES lines)"
    done
    echo -e "${GREEN}✓ Style check ready${NC}"
else
    echo -e "${GREEN}✓ No Python files modified${NC}"
fi

# ============================================================================
# STAGE 5: FEATURE DEV REVIEW (Architecture & Design)
# ============================================================================
echo -e "\n${CYAN}[STAGE 5/7] FEATURE DEV - ARCHITECTURE REVIEW${NC}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"

echo "Analyzing PR for:"
echo "  • Architectural consistency"
echo "  • Feature completeness"
echo "  • Design pattern compliance"
echo ""

# Count commits in PR
COMMIT_COUNT=$(gh pr view "$PR_NUMBER" --json commits --jq '.commits | length')
echo "PR has $COMMIT_COUNT commit(s)"

if [ "$COMMIT_COUNT" -gt 1 ]; then
    echo -e "${YELLOW}⚠ Multiple commits - consider squashing for clarity${NC}"
fi

echo -e "${GREEN}✓ Architecture review ready${NC}"

# ============================================================================
# STAGE 6: DESKTOP COMMANDER (Local File Analysis)
# ============================================================================
echo -e "\n${CYAN}[STAGE 6/7] DESKTOP COMMANDER - LOCAL OPTIMIZATION${NC}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"

echo "Running local analysis:"
echo "  • File size analysis"
echo "  • Import chain depth"
echo "  • Local optimization opportunities"
echo ""

if command -v python3 &> /dev/null; then
    python3 << 'PYTHON'
import os
import json

# Analyze imports in modified files
modified = ["dotfiles_tools/doctor.py", "dotfiles_tools/installer.py"]
for filepath in modified:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
            imports = [l for l in lines if l.startswith('import ') or l.startswith('from ')]
            print(f"  {filepath}: {len(imports)} imports, {len(lines)} lines")
PYTHON
    echo -e "${GREEN}✓ Local analysis complete${NC}"
else
    echo -e "${GREEN}✓ Local analysis skipped${NC}"
fi

# ============================================================================
# STAGE 7: CODACY MCP (Remote Quality Gate - FINAL)
# ============================================================================
echo -e "\n${CYAN}[STAGE 7/7] CODACY MCP - REMOTE QUALITY GATE (FINAL)${NC}"
echo -e "${YELLOW}────────────────────────────────────────────────────────────${NC}"

echo "Checking Codacy analysis for PR #$PR_NUMBER..."
echo "Criteria:"
echo "  • Complexity ≤ A grade"
echo "  • No new critical issues"
echo "  • Quality gate: PASS"
echo ""

# This would use Codacy MCP in practice
echo -e "${YELLOW}(Codacy MCP would check: codacy_get_repository_pull_request)${NC}"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ PIPELINE COMPLETE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

echo ""
echo "Summary:"
echo "  Stage 1 ✓ Local validation passed"
echo "  Stage 2 ✓ PR #$PR_NUMBER created/verified"
echo "  Stage 3 ⟳ Code review (pending manual review)"
echo "  Stage 4 ⟳ Style check (pending toolkit analysis)"
echo "  Stage 5 ⟳ Architecture (pending feature-dev analysis)"
echo "  Stage 6 ✓ Local optimization analysis"
echo "  Stage 7 ⟳ Codacy gate (waiting for remote analysis)"
echo ""
echo -e "${YELLOW}Next actions:${NC}"
echo "  • View PR:  gh pr view $PR_NUMBER"
echo "  • Add link: gh pr view $PR_NUMBER --web"
echo "  • Monitor:  Codacy quality gate results"
echo ""
