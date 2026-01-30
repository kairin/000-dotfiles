#!/bin/bash
# update_fish.sh - Update Fish shell and plugins
#
# Updates:
# - Fish shell via apt
# - Fisher plugins via fisher update

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../006-logs/logger.sh"

log "INFO" "Current Fish version: $(fish --version 2>/dev/null || echo 'not installed')"

# ==============================================================================
# Step 1: Update Fish Shell via APT
# ==============================================================================
log "INFO" "Updating package lists..."
sudo apt-get update -qq

log "INFO" "Updating Fish shell..."
if sudo apt-get install -y fish; then
    log "SUCCESS" "Fish updated"
    log "INFO" "New version: $(fish --version 2>/dev/null)"
else
    log "ERROR" "Fish update failed"
    exit 1
fi

# ==============================================================================
# Step 2: Update Fisher Plugins
# ==============================================================================
FISHER_FUNCS="$HOME/.config/fish/functions/fisher.fish"

if [ -f "$FISHER_FUNCS" ]; then
    log "INFO" "Updating Fisher plugins..."

    if fish -c 'fisher update' 2>/dev/null; then
        log "SUCCESS" "Fisher plugins updated"

        # List updated plugins
        log "INFO" "Installed plugins:"
        fish -c 'fisher list' 2>/dev/null | while read -r plugin; do
            log "INFO" "  - $plugin"
        done
    else
        log "WARNING" "Fisher update had issues (may need manual intervention)"
    fi
else
    log "INFO" "Fisher not installed, skipping plugin updates"
fi

# ==============================================================================
# Step 3: Update fzf (if git-installed)
# ==============================================================================
FZF_DIR="$HOME/.fzf"
if [ -d "$FZF_DIR/.git" ]; then
    log "INFO" "Updating fzf..."
    git -C "$FZF_DIR" pull --quiet 2>/dev/null
    "$FZF_DIR/install" --key-bindings --completion --no-update-rc --no-bash --no-zsh 2>/dev/null
    log "SUCCESS" "fzf updated"
fi

log "SUCCESS" "Fish update complete"
