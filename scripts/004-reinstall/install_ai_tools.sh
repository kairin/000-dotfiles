#!/bin/bash
# install_ai_tools.sh - Install AI CLIs (targeted by TOOL_ID; aggregate fallback)

source "$(dirname "$0")/../006-logs/logger.sh"

tool_key_from_id() {
    case "${TOOL_ID:-ai_tools}" in
        ai_claude) echo "claude" ;;
        ai_gemini) echo "gemini" ;;
        ai_codex) echo "codex" ;;
        ai_copilot) echo "copilot" ;;
        *) echo "all" ;;
    esac
}

# Ensure fnm environment is loaded
if command -v fnm &> /dev/null; then
    eval "$(fnm env --use-on-cd 2>/dev/null)" || true
fi

# Ensure npm global bin is in PATH
if command -v npm &> /dev/null; then
    NPM_BIN=$(npm config get prefix 2>/dev/null)/bin
    export PATH="$NPM_BIN:$PATH"
fi

install_claude() {
    echo ""
    log "INFO" "Installing Claude Code..."
    npm uninstall -g @anthropic-ai/claude-code 2>/dev/null || true
    if curl -fsSL https://claude.ai/install.sh | bash; then
        log "SUCCESS" "Claude Code installed successfully."
        echo "  Run 'claude' to authenticate with Anthropic."
    else
        log "ERROR" "Failed to install Claude Code."
        return 1
    fi
}

install_gemini() {
    echo ""
    log "INFO" "Installing Gemini CLI..."
    npm uninstall -g @google/generative-ai-cli 2>/dev/null || true
    if npm install -g @google/gemini-cli@latest; then
        log "SUCCESS" "Gemini CLI installed successfully."
        echo "  Run 'gemini' to start."
    else
        log "ERROR" "Failed to install Gemini CLI."
        return 1
    fi
}

install_codex() {
    echo ""
    log "INFO" "Installing OpenAI Codex CLI..."
    if npm install -g @openai/codex@latest; then
        log "SUCCESS" "OpenAI Codex CLI installed successfully."
        echo "  Run 'codex' to start."
        echo "  For Spec-Kit projects, set CODEX_HOME automatically with direnv:"
        echo "    echo 'export CODEX_HOME=\"\$PWD/.codex\"' > .envrc"
        echo "    direnv allow"
    else
        log "ERROR" "Failed to install OpenAI Codex CLI."
        return 1
    fi
}

install_copilot() {
    echo ""
    log "INFO" "Installing GitHub Copilot CLI..."
    if command -v gh &> /dev/null && gh extension list 2>/dev/null | grep -q "copilot"; then
        log "INFO" "Removing old gh extension..."
        gh extension remove gh-copilot 2>/dev/null || true
    fi
    if npm install -g @github/copilot@latest; then
        log "SUCCESS" "GitHub Copilot CLI installed successfully."
        echo "  Run 'copilot' and use /login to authenticate."
    else
        log "ERROR" "Failed to install GitHub Copilot CLI."
        return 1
    fi
}

install_specify() {
    echo ""
    log "INFO" "Installing Spec Kit CLI..."
    if ! command -v uv &> /dev/null; then
        log "WARNING" "uv is not installed, skipping Spec Kit CLI"
        return 0
    fi
    if uv tool install --upgrade specify-cli --from git+https://github.com/github/spec-kit.git; then
        log "SUCCESS" "Spec Kit CLI installed successfully."
        echo "  Run 'specify --help' to verify."
    else
        log "ERROR" "Failed to install Spec Kit CLI."
        return 1
    fi
}

TARGET="$(tool_key_from_id)"
log "INFO" "Installing AI CLI target: ${TARGET}"

case "$TARGET" in
    claude) install_claude ;;
    gemini) install_gemini ;;
    codex)
        install_codex
        install_specify
        ;;
    copilot) install_copilot ;;
    all)
        install_claude
        install_gemini
        install_codex
        install_copilot
        install_specify
        ;;
esac

echo ""
log "SUCCESS" "AI CLI installation complete for ${TARGET}."
show_shell_reload_instructions
