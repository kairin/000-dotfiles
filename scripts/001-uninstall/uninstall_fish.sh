#!/bin/bash
# uninstall_fish.sh - Uninstall Fish shell
source "$(dirname "$0")/../006-logs/logger.sh"

log "INFO" "Removing Fish shell installations..."

removed_count=0

# Safety check: Don't uninstall if Fish is the current default shell
CURRENT_SHELL=$(getent passwd "$USER" | cut -d: -f7)
if [[ "$CURRENT_SHELL" == *"fish"* ]]; then
    log "ERROR" "Fish is your default shell!"
    log "ERROR" "Change your default shell first: chsh -s /bin/bash"
    log "ERROR" "Then re-run uninstall"
    exit 1
fi

# 1. Remove Fisher plugins first (if Fisher exists)
FISHER_FUNCS="$HOME/.config/fish/functions/fisher.fish"
if [ -f "$FISHER_FUNCS" ]; then
    log "INFO" "Removing Fisher plugins..."
    # List and remove all plugins
    if fish -c 'fisher list' &>/dev/null; then
        PLUGINS=$(fish -c 'fisher list' 2>/dev/null | grep -v '^jorgebucaran/fisher$')
        for plugin in $PLUGINS; do
            log "INFO" "Removing plugin: $plugin"
            fish -c "fisher remove $plugin" 2>/dev/null || true
        done
        # Remove Fisher itself last
        fish -c "fisher remove jorgebucaran/fisher" 2>/dev/null || true
        log "SUCCESS" "Fisher plugins removed"
    fi
fi

# 2. Remove APT package if installed
if dpkg -l fish 2>/dev/null | grep -q '^ii'; then
    log "INFO" "Found fish apt package, removing..."
    if sudo apt-get remove -y fish; then
        ((removed_count++))
        log "SUCCESS" "Fish APT package removed"
    else
        log "WARNING" "Failed to remove fish apt package"
    fi
fi

# 3. Remove Snap if installed
if snap list fish 2>/dev/null | grep -q fish; then
    log "INFO" "Found fish snap package, removing..."
    if sudo snap remove fish; then
        ((removed_count++))
        log "SUCCESS" "Snap package removed"
    else
        log "WARNING" "Failed to remove snap package"
    fi
fi

# 4. Remove fzf from git install (if installed there)
FZF_DIR="$HOME/.fzf"
if [ -d "$FZF_DIR" ]; then
    log "INFO" "Found fzf at $FZF_DIR"
    # Only remove if no zsh depends on it
    if [ ! -f "$HOME/.zshrc" ] || ! grep -q '\.fzf\.zsh' "$HOME/.zshrc" 2>/dev/null; then
        log "INFO" "Removing fzf..."
        rm -rf "$FZF_DIR"
        rm -f "$HOME/.fzf.bash" "$HOME/.fzf.zsh"
        log "SUCCESS" "fzf removed"
    else
        log "INFO" "Keeping fzf (ZSH depends on it)"
    fi
fi

# 5. Check for any other fish binaries in PATH
if command -v fish &>/dev/null; then
    remaining=$(which fish)
    log "WARNING" "fish still found at: $remaining"
    log "WARNING" "Manual cleanup may be required"
fi

# 6. Report results
if [ $removed_count -eq 0 ]; then
    if ! command -v fish &>/dev/null; then
        log "INFO" "Fish is not installed, nothing to do"
    else
        remaining=$(which fish)
        log "WARNING" "Fish still found at: $remaining"
    fi
else
    if ! command -v fish &>/dev/null; then
        log "SUCCESS" "Fish removed successfully ($removed_count methods cleaned)"
    else
        remaining=$(which fish)
        log "WARNING" "Removed $removed_count installations, but fish still found at: $remaining"
    fi
fi

log "INFO" ""
log "INFO" "Note: Fish configuration preserved at ~/.config/fish/"
log "INFO" "To remove configs: rm -rf ~/.config/fish"
