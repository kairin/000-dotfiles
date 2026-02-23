#!/bin/bash
# update_ai_tools.sh - Update AI CLIs in place (targeted by TOOL_ID; aggregate fallback)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
source "$SCRIPT_DIR/../006-logs/logger.sh"

tool_key_from_id() {
    case "${TOOL_ID:-ai_tools}" in
        ai_claude) echo "claude" ;;
        ai_gemini) echo "gemini" ;;
        ai_codex) echo "codex" ;;
        ai_copilot) echo "copilot" ;;
        *) echo "all" ;;
    esac
}

FNM_PATH="$HOME/.local/share/fnm"
if [[ -d "$FNM_PATH" ]]; then
    export PATH="$FNM_PATH:$PATH"
    eval "$(fnm env --use-on-cd 2>/dev/null)"
fi

if command -v npm &> /dev/null; then
    NPM_BIN=$(npm config get prefix 2>/dev/null)/bin
    export PATH="$NPM_BIN:$PATH"
fi

UPDATED=0
TARGET="$(tool_key_from_id)"

update_claude() {
    if command -v claude &> /dev/null; then
        log "INFO" "Updating Claude Code..."
        local before after
        before=$(claude --version 2>/dev/null | head -n 1)
        if curl -fsSL https://claude.ai/install.sh | bash; then
            after=$(claude --version 2>/dev/null | head -n 1)
            log "SUCCESS" "Claude Code: $before -> $after"
            UPDATED=$((UPDATED + 1))
        else
            log "WARNING" "Claude Code update failed"
        fi
    else
        log "INFO" "Claude Code not installed, skipping"
    fi
}

update_gemini() {
    if command -v npm &> /dev/null && npm list -g @google/gemini-cli &> /dev/null; then
        log "INFO" "Updating Gemini CLI..."
        local before after
        before=$(gemini --version 2>/dev/null | head -n 1)
        if npm update -g @google/gemini-cli 2>/dev/null || npm install -g @google/gemini-cli@latest; then
            after=$(gemini --version 2>/dev/null | head -n 1)
            log "SUCCESS" "Gemini CLI: $before -> $after"
            UPDATED=$((UPDATED + 1))
        else
            log "WARNING" "Gemini CLI update failed"
        fi
    else
        log "INFO" "Gemini CLI not installed, skipping"
    fi
}

update_codex() {
    if command -v npm &> /dev/null && npm list -g @openai/codex &> /dev/null; then
        log "INFO" "Updating OpenAI Codex CLI..."
        local before after
        before=$(codex --version 2>/dev/null | head -n 1 || echo "installed")
        if npm update -g @openai/codex 2>/dev/null || npm install -g @openai/codex@latest; then
            after=$(codex --version 2>/dev/null | head -n 1 || echo "installed")
            log "SUCCESS" "OpenAI Codex CLI: $before -> $after"
            UPDATED=$((UPDATED + 1))
        else
            log "WARNING" "OpenAI Codex CLI update failed"
        fi
    else
        log "INFO" "OpenAI Codex CLI not installed, skipping"
    fi

    if command -v uv &> /dev/null; then
        log "INFO" "Updating Spec Kit CLI..."
        local before after
        before=$(specify --version 2>/dev/null | head -n 1 || echo "not-installed")
        if uv tool install --upgrade specify-cli --from git+https://github.com/github/spec-kit.git; then
            after=$(specify --version 2>/dev/null | head -n 1 || echo "installed")
            log "SUCCESS" "Spec Kit CLI: $before -> $after"
            UPDATED=$((UPDATED + 1))
        else
            log "WARNING" "Spec Kit CLI update failed"
        fi
    else
        log "INFO" "uv not available, skipping Spec Kit CLI"
    fi

    if [[ ! -f "$REPO_ROOT/.envrc" ]]; then
        printf "export CODEX_HOME=\"\$PWD/.codex\"\n" > "$REPO_ROOT/.envrc"
        log "SUCCESS" "Created .envrc with CODEX_HOME at repository root"
    fi
}

update_copilot() {
    if command -v npm &> /dev/null && npm list -g @github/copilot &> /dev/null; then
        log "INFO" "Updating GitHub Copilot CLI..."
        local before after
        before=$(copilot --version 2>/dev/null | head -n 1)
        if npm update -g @github/copilot 2>/dev/null || npm install -g @github/copilot@latest; then
            after=$(copilot --version 2>/dev/null | head -n 1)
            log "SUCCESS" "GitHub Copilot CLI: $before -> $after"
            UPDATED=$((UPDATED + 1))
        else
            log "WARNING" "GitHub Copilot CLI update failed"
        fi
    else
        log "INFO" "GitHub Copilot CLI not installed, skipping"
    fi
}

log "INFO" "Updating AI CLI target: ${TARGET}"

case "$TARGET" in
    claude) update_claude ;;
    gemini) update_gemini ;;
    codex) update_codex ;;
    copilot) update_copilot ;;
    all)
        update_claude
        update_gemini
        update_codex
        update_copilot
        ;;
esac

if [[ $UPDATED -gt 0 ]]; then
    log "SUCCESS" "Updated $UPDATED component(s) for ${TARGET}"
else
    log "INFO" "No components were updated for ${TARGET}"
fi
