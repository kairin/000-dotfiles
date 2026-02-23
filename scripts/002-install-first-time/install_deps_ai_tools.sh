#!/bin/bash
# install_deps_ai_tools.sh - Install dependencies for AI CLI tools (targeted by TOOL_ID)

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

need_node=0
need_curl=0

case "$(tool_key_from_id)" in
    claude) need_curl=1 ;;
    gemini|codex|copilot) need_node=1 ;;
    all)
        need_curl=1
        need_node=1
        ;;
esac

log "INFO" "Checking dependencies for ${TOOL_ID:-ai_tools}..."

if [[ "$need_node" -eq 1 ]]; then
    if ! command -v node &> /dev/null; then
        log "ERROR" "Node.js is required but not installed."
        log "ERROR" "Please install Node.js first from the main menu."
        exit 1
    fi
    if ! command -v npm &> /dev/null; then
        log "ERROR" "npm is required but not installed."
        log "ERROR" "npm should come with Node.js - please reinstall Node.js."
        exit 1
    fi
    log "SUCCESS" "Node.js $(node -v) available"
    log "SUCCESS" "npm $(npm -v) available"
fi

if [[ "$need_curl" -eq 1 ]]; then
    if ! command -v curl &> /dev/null; then
        log "ERROR" "curl is required but not installed."
        log "INFO" "Installing curl..."
        sudo apt-get update && sudo apt-get install -y curl
    fi
    log "SUCCESS" "curl available"
fi

log "SUCCESS" "Dependencies for ${TOOL_ID:-ai_tools} are ready."
