#!/bin/bash
# check_fish.sh - Check Fish shell, Fisher plugin manager, and plugins

if command -v fish &> /dev/null; then
    # Get Fish version
    VERSION=$(fish --version 2>/dev/null | grep -oP '\d+(\.\d+)+' | head -1 || echo "Unknown")
    LOCATION=$(command -v fish)

    # Detect installation method
    if [[ "$LOCATION" == *"/usr/bin/"* ]] && dpkg -l fish &>/dev/null; then
        METHOD="APT"
    elif [[ "$LOCATION" == *"/snap/"* ]]; then
        METHOD="Snap"
    elif [[ "$LOCATION" == *"/usr/local/"* ]]; then
        METHOD="Source"
    else
        METHOD="Other"
    fi

    # Check for Fisher plugin manager
    FISHER_STATUS="no"
    FISHER_FUNCS="$HOME/.config/fish/functions/fisher.fish"
    if [ -f "$FISHER_FUNCS" ]; then
        FISHER_STATUS="yes"
    fi

    # Count installed plugins
    PLUGIN_COUNT=0
    FISH_PLUGINS_FILE="$HOME/.config/fish/fish_plugins"
    if [ -f "$FISH_PLUGINS_FILE" ]; then
        # Count non-empty, non-comment lines
        PLUGIN_COUNT=$(grep -cEv '^(#|$)' "$FISH_PLUGINS_FILE")
    fi

    # Check for Tide theme
    TIDE_STATUS="no"
    if fish -c 'functions -q _tide_prompt' 2>/dev/null; then
        TIDE_STATUS="yes"
    fi

    # Build extra info string
    EXTRA="^fisher:$FISHER_STATUS^plugins:$PLUGIN_COUNT^tide:$TIDE_STATUS"

    # Get latest version from apt
    LATEST=$(apt-cache policy fish 2>/dev/null | grep "Candidate:" | awk '{print $2}' | grep -oP '\d+(\.\d+)+' | head -1 || echo "-")

    echo "INSTALLED|$VERSION|$METHOD|$LOCATION$EXTRA|$LATEST"
else
    echo "NOT_INSTALLED|-|-|-|-"
fi
