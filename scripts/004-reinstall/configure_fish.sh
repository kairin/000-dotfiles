#!/bin/bash
# configure_fish.sh - Configure Fish shell with completions, aliases, and PATH
# Strategy: Add configuration blocks to config.fish using marker comments
source "$(dirname "$0")/../006-logs/logger.sh"

CONFIG_FISH="$HOME/.config/fish/config.fish"
BACKUP_DIR="$HOME/.config/fish/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
CONFIGS_DIR="$SCRIPT_DIR/configs/fish"

# ==============================================================================
# Pre-flight Checks
# ==============================================================================
if ! command -v fish &> /dev/null; then
    log "ERROR" "Fish shell not installed"
    log "INFO" "Please run 'Install' first to set up Fish"
    exit 1
fi

# ==============================================================================
# Step 1: Create Backup
# ==============================================================================
log "INFO" "Creating backup of config.fish..."
mkdir -p "$BACKUP_DIR"

if [ -f "$CONFIG_FISH" ]; then
    cp "$CONFIG_FISH" "$BACKUP_DIR/config.fish.$TIMESTAMP"
    log "SUCCESS" "Backed up to $BACKUP_DIR/config.fish.$TIMESTAMP"
else
    # Create initial config if missing
    touch "$CONFIG_FISH"
    log "INFO" "Created new config.fish"
fi

# ==============================================================================
# Step 2: Add PATH Configuration
# ==============================================================================
log "INFO" "Configuring PATH..."

if grep -q 'dotfiles-config:path' "$CONFIG_FISH"; then
    log "INFO" "PATH configuration already present"
else
    cat >> "$CONFIG_FISH" << 'EOF'

# >>> dotfiles-config:path >>>
# PATH configuration added by 000-dotfiles TUI installer

# ~/.local/bin (pip packages, fnm, npm globals, uv tools, etc.)
fish_add_path -g $HOME/.local/bin

# Cargo (Rust)
if test -d $HOME/.cargo/bin
    fish_add_path -g $HOME/.cargo/bin
end

# Go
if test -d $HOME/go/bin
    fish_add_path -g $HOME/go/bin
end
if test -d /usr/local/go/bin
    fish_add_path -g /usr/local/go/bin
end
# <<< dotfiles-config:path <<<
EOF
    log "SUCCESS" "Added PATH configuration"
fi

# ==============================================================================
# Step 3: Add Tool Completions
# ==============================================================================
log "INFO" "Configuring tool completions..."

if grep -q 'dotfiles-config:completions' "$CONFIG_FISH"; then
    log "INFO" "Tool completions already present"
else
    cat >> "$CONFIG_FISH" << 'EOF'

# >>> dotfiles-config:completions >>>
# Shell completions for installed tools

# uv (Python package manager)
if command -q uv
    uv generate-shell-completion fish | source
end

# gh (GitHub CLI)
if command -q gh
    gh completion -s fish | source
end

# gum (TUI component library)
if command -q gum
    gum completion fish | source
end

# glow (Markdown renderer)
if command -q glow
    glow completion fish | source
end

# fnm (Fast Node Manager)
if command -q fnm
    fnm env --use-on-cd --shell fish | source
end
# <<< dotfiles-config:completions <<<
EOF
    log "SUCCESS" "Added tool completions"
fi

# ==============================================================================
# Step 4: Add Modern CLI Aliases
# ==============================================================================
log "INFO" "Configuring modern CLI aliases..."

if grep -q 'dotfiles-config:aliases' "$CONFIG_FISH"; then
    log "INFO" "Aliases already present"
else
    cat >> "$CONFIG_FISH" << 'EOF'

# >>> dotfiles-config:aliases >>>
# Modern CLI tool aliases

# bat (better cat) - https://github.com/sharkdp/bat
if command -q bat
    alias cat 'bat --paging=never'
    alias catp 'bat'  # cat with paging
end

# eza (better ls) - https://github.com/eza-community/eza
if command -q eza
    alias ls 'eza --icons --group-directories-first'
    alias ll 'eza -l --icons --group-directories-first --git'
    alias la 'eza -la --icons --group-directories-first --git'
    alias lt 'eza --tree --icons --level=2'
end

# fd (better find) - https://github.com/sharkdp/fd
if command -q fd
    alias find 'fd'
end

# ripgrep (better grep) - https://github.com/BurntSushi/ripgrep
if command -q rg
    alias grep 'rg'
end

# zoxide (better cd) - https://github.com/ajeetdsouza/zoxide
if command -q zoxide
    zoxide init fish | source
end
# <<< dotfiles-config:aliases <<<
EOF
    log "SUCCESS" "Added modern CLI aliases"
fi

# ==============================================================================
# Step 5: Add Useful Functions
# ==============================================================================
log "INFO" "Configuring useful functions..."

if grep -q 'dotfiles-config:functions' "$CONFIG_FISH"; then
    log "INFO" "Functions already present"
else
    cat >> "$CONFIG_FISH" << 'EOF'

# >>> dotfiles-config:functions >>>
# Useful shell functions

# Create directory and cd into it
function mkcd
    mkdir -p $argv[1] && cd $argv[1]
end

# Quick navigation
function ..
    cd ..
end
function ...
    cd ../..
end
function ....
    cd ../../..
end

# Disable greeting
set -g fish_greeting
# <<< dotfiles-config:functions <<<
EOF
    log "SUCCESS" "Added useful functions"
fi

# ==============================================================================
# Step 6: Configure Fish Variables
# ==============================================================================
log "INFO" "Configuring Fish variables..."

if grep -q 'dotfiles-config:variables' "$CONFIG_FISH"; then
    log "INFO" "Variables already present"
else
    cat >> "$CONFIG_FISH" << 'EOF'

# >>> dotfiles-config:variables >>>
# Environment variables

# Editor preference
set -gx EDITOR vim
if command -q nvim
    set -gx EDITOR nvim
end

# Less options for better paging
set -gx LESS '-R --mouse --wheel-lines=3'
# <<< dotfiles-config:variables <<<
EOF
    log "SUCCESS" "Added environment variables"
fi

# ==============================================================================
# Summary
# ==============================================================================
log "SUCCESS" "Fish configuration complete!"
log "INFO" ""
log "INFO" "Changes made:"
log "INFO" "  - Added PATH (~/.local/bin, cargo, go)"
log "INFO" "  - Added completions (uv, gh, gum, glow, fnm)"
log "INFO" "  - Added modern CLI aliases (bat, eza, fd, rg, zoxide)"
log "INFO" "  - Added utility functions (mkcd, .., ..., ....)"
log "INFO" "  - Set environment variables (EDITOR, LESS)"
log "INFO" ""
log "INFO" "Backup location: $BACKUP_DIR/config.fish.$TIMESTAMP"
log "INFO" ""
log "INFO" "To apply changes:"
log "INFO" "  1. Start Fish: fish"
log "INFO" "  2. Or reload: source ~/.config/fish/config.fish"
log "INFO" ""
log "INFO" "To customize your prompt:"
log "INFO" "  tide configure"
log "INFO" ""
log "INFO" "To restore previous config:"
log "INFO" "  cp $BACKUP_DIR/config.fish.$TIMESTAMP ~/.config/fish/config.fish"
