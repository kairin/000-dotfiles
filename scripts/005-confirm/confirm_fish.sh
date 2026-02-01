#!/bin/bash
# confirm_fish.sh - Verify Fish shell, Fisher, plugins, and configuration
source "$(dirname "$0")/../006-logs/logger.sh"

FISH_CONFIG_DIR="$HOME/.config/fish"
CONFIG_FISH="$FISH_CONFIG_DIR/config.fish"
ERRORS=0

log "INFO" "Confirming Fish shell environment installation..."
log "INFO" ""

# ==============================================================================
# 1. Check Fish Binary
# ==============================================================================
log "INFO" "[1/6] Checking Fish binary..."
if command -v fish &> /dev/null; then
    VERSION=$(fish --version 2>/dev/null | head -1)
    PATH_LOC=$(command -v fish)
    log "SUCCESS" "Fish installed at $PATH_LOC"
    log "INFO" "        Version: $VERSION"
else
    log "ERROR" "Fish is NOT installed"
    ((ERRORS++))
fi

# ==============================================================================
# 2. Check Fisher Plugin Manager
# ==============================================================================
log "INFO" "[2/6] Checking Fisher plugin manager..."
FISHER_FUNCS="$FISH_CONFIG_DIR/functions/fisher.fish"
if [ -f "$FISHER_FUNCS" ]; then
    log "SUCCESS" "Fisher installed"

    # Get Fisher version
    FISHER_VERSION=$(fish -c 'fisher --version' 2>/dev/null || echo "unknown")
    log "INFO" "        Version: $FISHER_VERSION"
else
    log "ERROR" "Fisher is NOT installed"
    ((ERRORS++))
fi

# ==============================================================================
# 3. Check Plugins
# ==============================================================================
log "INFO" "[3/6] Checking installed plugins..."

FISH_PLUGINS_FILE="$FISH_CONFIG_DIR/fish_plugins"
if [ -f "$FISH_PLUGINS_FILE" ]; then
    PLUGIN_COUNT=$(grep -cEv '^(#|$)' "$FISH_PLUGINS_FILE")
    log "SUCCESS" "$PLUGIN_COUNT plugins installed"

    # List key plugins
    while IFS= read -r plugin; do
        [[ "$plugin" =~ ^#.*$ || -z "$plugin" ]] && continue
        plugin_name=$(basename "$plugin" | sed 's/\.fish$//')
        log "INFO" "        - $plugin_name"
    done < "$FISH_PLUGINS_FILE"
else
    log "WARNING" "No fish_plugins file found"
fi

# Check for critical plugins
CRITICAL_PLUGINS=("fzf.fish" "tide" "z" "autopair.fish" "bass" "done")
MISSING_CRITICAL=0
for critical in "${CRITICAL_PLUGINS[@]}"; do
    if ! grep -q "$critical" "$FISH_PLUGINS_FILE" 2>/dev/null; then
        log "WARNING" "Missing recommended plugin: $critical"
        ((MISSING_CRITICAL++))
    fi
done

if [ $MISSING_CRITICAL -eq 0 ]; then
    log "SUCCESS" "All recommended plugins present"
fi

# ==============================================================================
# 4. Check Tide Theme
# ==============================================================================
log "INFO" "[4/6] Checking Tide theme..."
if fish -c 'functions -q _tide_prompt' 2>/dev/null; then
    log "SUCCESS" "Tide theme installed and active"
    log "INFO" "        Customize with: tide configure"
else
    log "WARNING" "Tide theme not fully configured"
    log "INFO" "        Run in Fish: tide configure"
fi

# ==============================================================================
# 5. Check config.fish
# ==============================================================================
log "INFO" "[5/6] Checking config.fish..."
if [ -f "$CONFIG_FISH" ]; then
    log "SUCCESS" "config.fish exists"

    # Check for key configurations
    if grep -q 'dotfiles-config:path' "$CONFIG_FISH"; then
        log "SUCCESS" "PATH configuration present"
    else
        log "WARNING" "PATH configuration NOT present (run Configure)"
    fi

    if grep -q 'dotfiles-config:completions' "$CONFIG_FISH"; then
        log "SUCCESS" "Tool completions configured"
    else
        log "WARNING" "Tool completions NOT configured (run Configure)"
    fi

    if grep -q 'dotfiles-config:aliases' "$CONFIG_FISH"; then
        log "SUCCESS" "Modern CLI aliases configured"
    else
        log "WARNING" "Aliases NOT configured (run Configure)"
    fi
else
    log "WARNING" "config.fish does NOT exist"
    log "INFO" "        Run 'Configure' to create it"
fi

# ==============================================================================
# 6. Check Default Shell
# ==============================================================================
log "INFO" "[6/6] Checking default shell..."
CURRENT_SHELL=$(getent passwd "$USER" | cut -d: -f7)
if [[ "$CURRENT_SHELL" == *"fish"* ]]; then
    log "SUCCESS" "Default shell is Fish ($CURRENT_SHELL)"
else
    log "INFO" "Default shell is $CURRENT_SHELL (not Fish)"
    log "INFO" "        To change: chsh -s \$(which fish)"
fi

# ==============================================================================
# Summary
# ==============================================================================
log "INFO" ""
log "INFO" "=========================================="
if [ $ERRORS -eq 0 ]; then
    log "SUCCESS" "Fish environment verification complete!"
    log "INFO" ""
    log "INFO" "Quick test commands (in Fish shell):"
    log "INFO" "  - Press Ctrl+R for fuzzy history search"
    log "INFO" "  - Press Ctrl+T for fuzzy file finder"
    log "INFO" "  - Type 'z <partial>' to jump to directories"
    log "INFO" "  - Type '(' to see autopair in action"
    log "INFO" ""
    log "INFO" "To run bash scripts in Fish:"
    log "INFO" "  bass source ./some-script.sh"
else
    log "ERROR" "Verification completed with $ERRORS error(s)"
    exit 1
fi

# Generate artifact manifest for future verification
SCRIPT_DIR="$(dirname "$0")"
VERSION_NUM=$(fish --version 2>/dev/null | grep -oP '\d+\.\d+' | head -1 || echo "unknown")
"$SCRIPT_DIR/generate_manifest.sh" fish "$VERSION_NUM" apt > /dev/null 2>&1 || true
