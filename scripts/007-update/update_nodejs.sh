#!/bin/bash
# update_nodejs.sh - Update Node.js via fnm WITHOUT losing npm global packages
#
# This script performs an in-place update by:
# 1. Installing the new Node.js version alongside existing ones
# 2. Switching to the new version
# 3. Preserving all npm global packages

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../006-logs/logger.sh"

# Initialize fnm environment (and bootstrap if missing).
# Note: fnm binary is installed to ~/.local/bin by scripts/004-reinstall/install_nodejs.sh.
export PATH="$HOME/.local/bin:$PATH"

if ! command -v fnm &> /dev/null; then
    log "WARNING" "fnm not found in PATH; installing fnm to $HOME/.local/bin..."
    if ! curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir "$HOME/.local/bin" --skip-shell; then
        log "ERROR" "fnm install failed"
        exit 1
    fi
fi

if ! command -v fnm &> /dev/null; then
    log "ERROR" "fnm still not available after install"
    exit 1
fi

eval "$(fnm env --shell bash --use-on-cd 2>/dev/null)"

# Get target version (major version)
TARGET_VERSION="25"

log "INFO" "Current Node.js version: $(node --version 2>/dev/null || echo 'none')"
log "INFO" "Current npm version: $(npm --version 2>/dev/null || echo 'none')"

# List current npm globals before update
log "INFO" "Recording current npm global packages..."
NPM_GLOBALS_BEFORE=$(npm list -g --depth=0 2>/dev/null || echo "")

log "INFO" "Updating to Node.js v${TARGET_VERSION}..."

# Install new version (fnm keeps old versions, preserving npm globals)
fnm install "$TARGET_VERSION" || {
    log "ERROR" "Failed to install Node.js v${TARGET_VERSION}"
    exit 1
}

# Switch to new version
fnm use "$TARGET_VERSION" || {
    log "ERROR" "Failed to switch to Node.js v${TARGET_VERSION}"
    exit 1
}

# Set as default
fnm default "$TARGET_VERSION"

log "SUCCESS" "Updated to Node.js $(node --version)"
log "INFO" "npm version: $(npm --version)"

# Verify npm globals still exist
log "INFO" "Verifying npm global packages..."
npm list -g --depth=0 2>/dev/null

log "SUCCESS" "Node.js update complete - npm globals preserved"
