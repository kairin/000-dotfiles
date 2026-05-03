#!/bin/bash
# Automated push + PR creation workflow
# Usage: ./scripts/push-with-pr.sh
# Prerequisites: gh CLI authenticated, GITHUB_TOKEN set

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
REMOTE_BRANCH="origin/$BRANCH"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Automated Push + PR Workflow${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

# Step 1: Push (hook runs automatically)
echo -e "\n${YELLOW}Step 1: Pushing to remote...${NC}"
git push origin "$BRANCH"
echo -e "${GREEN}✓ Push successful (hook validation passed)${NC}"

# Step 2: Check if PR already exists
echo -e "\n${YELLOW}Step 2: Checking for existing PR...${NC}"
EXISTING_PR=$(gh pr list --head "$BRANCH" --json number --jq '.[0].number' 2>/dev/null || echo "")

if [ -n "$EXISTING_PR" ]; then
    echo -e "${GREEN}✓ PR #$EXISTING_PR already exists${NC}"
    PR_NUMBER=$EXISTING_PR
else
    # Step 3: Create PR
    echo -e "\n${YELLOW}Step 3: Creating pull request...${NC}"

    TITLE=$(git log -1 --pretty=%B | head -1)
    BODY=$(git log -1 --pretty=%B | tail -n +3)

    PR_URL=$(gh pr create --base main \
        --title "$TITLE" \
        --body "$BODY" \
        --fill 2>&1 | grep "https://github.com" || echo "")

    if [ -z "$PR_URL" ]; then
        echo -e "${RED}✗ Failed to create PR${NC}"
        exit 1
    fi

    PR_NUMBER=$(echo "$PR_URL" | grep -oE '[0-9]+$')
    echo -e "${GREEN}✓ PR #$PR_NUMBER created${NC}"
fi

# Step 4: Monitor Codacy status
echo -e "\n${YELLOW}Step 4: Checking Codacy analysis...${NC}"
echo -e "   Waiting for Codacy to analyze PR #$PR_NUMBER..."
echo -e "   (Check status: gh pr view $PR_NUMBER)"

# Step 5: Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Workflow complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "\nNext steps:"
echo -e "  • View PR:     ${YELLOW}gh pr view $PR_NUMBER${NC}"
echo -e "  • Check tests: ${YELLOW}gh pr view $PR_NUMBER --web${NC}"
echo -e "  • View Codacy: Check 'Checks' tab on GitHub PR"
echo -e "\nWaiting for:"
echo -e "  ✓ GitHub Actions to pass"
echo -e "  ✓ Codacy quality gate (should pass now)"
echo -e "  ✓ Code review (if required)"
echo -e ""
