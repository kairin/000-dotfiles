#!/bin/bash
# install_deps_fish.sh - Install dependencies for Fish shell
source "$(dirname "$0")/../006-logs/logger.sh"

log "INFO" "Installing dependencies for Fish shell..."

# Smart apt update - skip if cache is fresh (< 5 min)
APT_LISTS="/var/lib/apt/lists"
CACHE_AGE=$(($(date +%s) - $(stat -c%Y "$APT_LISTS" 2>/dev/null || echo 0)))
if [[ $CACHE_AGE -gt 300 ]]; then
    sudo stdbuf -oL apt-get update
else
    log "INFO" "APT cache fresh (${CACHE_AGE}s ago), skipping update"
fi

# Fish dependencies: curl (for Fisher), git (for plugins)
DEPS="curl git"
MISSING_DEPS=""

for dep in $DEPS; do
    if ! command -v "$dep" &> /dev/null; then
        MISSING_DEPS="$MISSING_DEPS $dep"
    fi
done

if [ -n "$MISSING_DEPS" ]; then
    log "INFO" "Installing missing dependencies:$MISSING_DEPS"
    sudo stdbuf -oL apt-get install -y "$MISSING_DEPS"
fi

log "SUCCESS" "Dependencies check complete (curl, git available)"
