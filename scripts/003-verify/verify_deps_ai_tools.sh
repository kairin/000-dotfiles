#!/bin/bash
# verify_deps_ai_tools.sh - Verify dependencies for AI CLI tools (targeted by TOOL_ID)

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

MISSING=0

if [[ "$need_curl" -eq 1 ]] && ! command -v curl &> /dev/null; then
    echo "curl missing (required for Claude Code installer)"
    MISSING=1
fi

if [[ "$need_node" -eq 1 ]] && ! command -v node &> /dev/null; then
    echo "Node.js missing (required for npm-based AI CLIs)"
    MISSING=1
fi
if [[ "$need_node" -eq 1 ]] && ! command -v npm &> /dev/null; then
    echo "npm missing (required for npm-based AI CLIs)"
    MISSING=1
fi

if [[ $MISSING -eq 1 ]]; then
    echo "Some dependencies are missing."
    echo "Please install Node.js first from the main menu for npm-based tools."
    exit 1
fi

echo "Dependencies verified for ${TOOL_ID:-ai_tools}:"
if [[ "$need_curl" -eq 1 ]]; then
    echo "  curl: $(curl --version | head -n 1 | cut -d' ' -f1-2)"
fi
if [[ "$need_node" -eq 1 ]]; then
    echo "  Node.js: $(node -v)"
    echo "  npm: $(npm -v)"
fi
