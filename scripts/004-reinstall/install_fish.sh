#!/bin/bash
# install_fish.sh - Install Fish shell, Fisher plugin manager, and plugins
source "$(dirname "$0")/../006-logs/logger.sh"

FISH_CONFIG_DIR="$HOME/.config/fish"
SCRIPT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
CONFIGS_DIR="$SCRIPT_DIR/configs/fish"

# ==============================================================================
# Stage 1: Install Fish Shell
# ==============================================================================
log "INFO" "Checking Fish shell installation..."

if ! command -v fish &> /dev/null; then
    log "INFO" "Installing Fish shell..."

    # Smart apt update - skip if cache is fresh (< 5 min)
    APT_LISTS="/var/lib/apt/lists"
    CACHE_AGE=$(($(date +%s) - $(stat -c%Y "$APT_LISTS" 2>/dev/null || echo 0)))
    if [[ $CACHE_AGE -gt 300 ]]; then
        sudo stdbuf -oL apt-get update
    else
        log "INFO" "APT cache fresh (${CACHE_AGE}s ago), skipping update"
    fi

    sudo stdbuf -oL apt-get install -y fish

    if command -v fish &> /dev/null; then
        log "SUCCESS" "Fish shell installed: $(fish --version)"
    else
        log "ERROR" "Failed to install Fish shell"
        exit 1
    fi
else
    log "SUCCESS" "Fish shell already installed: $(fish --version)"
fi

# ==============================================================================
# Stage 2: Create Config Directories
# ==============================================================================
log "INFO" "Setting up Fish configuration directories..."

mkdir -p "$FISH_CONFIG_DIR/functions"
mkdir -p "$FISH_CONFIG_DIR/completions"
mkdir -p "$FISH_CONFIG_DIR/conf.d"

log "SUCCESS" "Fish config directories created at $FISH_CONFIG_DIR"

# ==============================================================================
# Stage 3: Install Fisher Plugin Manager
# ==============================================================================
log "INFO" "Checking Fisher plugin manager..."

FISHER_FUNCS="$FISH_CONFIG_DIR/functions/fisher.fish"

if [ -f "$FISHER_FUNCS" ]; then
    log "INFO" "Fisher already installed. Updating..."
    fish -c 'fisher update jorgebucaran/fisher' 2>/dev/null || true
    log "SUCCESS" "Fisher updated"
else
    log "INFO" "Installing Fisher..."

    # Install Fisher using the recommended method
    fish -c 'curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher'

    if [ -f "$FISHER_FUNCS" ]; then
        log "SUCCESS" "Fisher installed"
    else
        log "ERROR" "Failed to install Fisher"
        exit 1
    fi
fi

# ==============================================================================
# Stage 4: Install fzf (Required for fzf.fish plugin)
# ==============================================================================
log "INFO" "Checking fzf installation..."

if ! command -v fzf &> /dev/null; then
    log "INFO" "Installing fzf..."

    # Try apt first (simpler)
    if sudo apt-get install -y fzf 2>/dev/null; then
        log "SUCCESS" "fzf installed via apt"
    else
        # Fall back to git install
        FZF_DIR="$HOME/.fzf"
        if [ ! -d "$FZF_DIR" ]; then
            git clone --depth 1 https://github.com/junegunn/fzf.git "$FZF_DIR"
        fi
        "$FZF_DIR/install" --key-bindings --completion --no-update-rc --no-bash --no-zsh
        log "SUCCESS" "fzf installed from git"
    fi
else
    log "SUCCESS" "fzf already installed: $(fzf --version | head -1)"
fi

# ==============================================================================
# Stage 5: Install Fish Plugins
# ==============================================================================
log "INFO" "Installing Fish plugins..."

# Define plugins to install
PLUGINS=(
    "PatrickF1/fzf.fish"       # fzf integration (Ctrl+R, Ctrl+T)
    "jethrokuan/z"             # Directory jumping
    "jorgebucaran/autopair.fish"  # Auto-close brackets
    "IlanCosman/tide"          # Modern prompt theme
    "edc/bass"                 # Run bash scripts in Fish
    "franciscolourenco/done"   # Command completion notifications
)

for plugin in "${PLUGINS[@]}"; do
    plugin_name=$(basename "$plugin" | sed 's/\.fish$//')
    log "INFO" "Installing $plugin_name..."

    if fish -c "fisher install $plugin" 2>/dev/null; then
        log "SUCCESS" "$plugin_name installed"
    else
        log "WARNING" "Failed to install $plugin_name"
    fi
done

# ==============================================================================
# Stage 6: Configure Tide Theme (if installed)
# ==============================================================================
log "INFO" "Configuring Tide theme..."

if fish -c 'functions -q _tide_prompt' 2>/dev/null; then
    # Configure Tide with a clean, informative prompt
    # Note: Full customization requires interactive 'tide configure'
    log "SUCCESS" "Tide theme is ready"
    log "INFO" "Run 'tide configure' in Fish to customize your prompt"
else
    log "WARNING" "Tide theme not fully installed - run 'fisher install IlanCosman/tide' in Fish"
fi

# ==============================================================================
# Stage 7: Copy Default config.fish (if not exists)
# ==============================================================================
log "INFO" "Checking config.fish..."

CONFIG_FISH="$FISH_CONFIG_DIR/config.fish"

if [ ! -f "$CONFIG_FISH" ]; then
    if [ -f "$CONFIGS_DIR/config.fish" ]; then
        cp "$CONFIGS_DIR/config.fish" "$CONFIG_FISH"
        log "SUCCESS" "Installed default config.fish"
    else
        log "WARNING" "Default config.fish not found, Fish will use defaults"
    fi
else
    log "INFO" "config.fish already exists (keeping user configuration)"
fi

# ==============================================================================
# Summary
# ==============================================================================
log "SUCCESS" "Fish shell environment installation complete!"
log "INFO" ""
log "INFO" "Components installed:"
log "INFO" "  - Fish: $(fish --version | head -1)"
log "INFO" "  - Fisher: plugin manager"
log "INFO" "  - Plugins:"
for plugin in "${PLUGINS[@]}"; do
    log "INFO" "    - $(basename "$plugin" | sed 's/\.fish$//')"
done
log "INFO" ""
log "INFO" "Next steps:"
log "INFO" "  1. Run 'Configure' to set up completions and aliases"
log "INFO" "  2. Try Fish: fish"
log "INFO" "  3. Customize prompt: tide configure"
log "INFO" "  4. Set as default shell: chsh -s \$(which fish)"
log "INFO" ""
log "INFO" "Note: Fish uses its own syntax. Use 'bass' plugin to run bash scripts:"
log "INFO" "  bass source ./some-bash-script.sh"
