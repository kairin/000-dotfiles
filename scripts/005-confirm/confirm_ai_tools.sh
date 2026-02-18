#!/bin/bash
# confirm_ai_tools.sh - Verify AI CLI installation (targeted by TOOL_ID; aggregate fallback)

tool_key_from_id() {
    case "${TOOL_ID:-ai_tools}" in
        ai_claude) echo "claude" ;;
        ai_gemini) echo "gemini" ;;
        ai_codex) echo "codex" ;;
        ai_copilot) echo "copilot" ;;
        *) echo "all" ;;
    esac
}

# Ensure npm global bin is in PATH
if command -v npm &> /dev/null; then
    NPM_BIN=$(npm config get prefix 2>/dev/null)/bin
    export PATH="$NPM_BIN:$PATH"
fi
if command -v fnm &> /dev/null; then
    eval "$(fnm env --shell bash 2>/dev/null)" || true
fi

print_tool_status() {
    local label="$1"
    local cmd="$2"
    local hint="$3"
    local manifest="$4"
    local method="$5"

    echo -n "${label}: "
    if command -v "$cmd" &> /dev/null; then
        local ver
        ver=$("$cmd" --version 2>/dev/null | head -n 1 || echo "installed")
        echo "INSTALLED (${ver})"
        if [[ -n "$manifest" ]]; then
            SCRIPT_DIR="$(dirname "$0")"
            raw_ver=$("$cmd" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' || echo "unknown")
            "$SCRIPT_DIR/generate_manifest.sh" "$manifest" "$raw_ver" "$method" > /dev/null 2>&1 || true
        fi
        if [[ -n "$hint" ]]; then
            echo "  ${hint}"
        fi
        return 0
    fi

    echo "NOT INSTALLED"
    return 1
}

TARGET="$(tool_key_from_id)"
INSTALLED=0
TOTAL=0

echo "Verifying AI CLI installation for ${TARGET}..."
echo ""

case "$TARGET" in
    claude)
        TOTAL=1
        print_tool_status "Claude Code" "claude" "Run 'claude' to authenticate with Anthropic" "ai_tools_claude" "npm" && INSTALLED=1
        ;;
    gemini)
        TOTAL=1
        print_tool_status "Gemini CLI" "gemini" "Export GOOGLE_API_KEY in your shell profile" "ai_tools_gemini" "npm" && INSTALLED=1
        ;;
    codex)
        TOTAL=1
        if print_tool_status "OpenAI Codex CLI" "codex" "Run 'codex' to authenticate and start" "" "npm"; then
            INSTALLED=1
            echo "  Spec-Kit auto setup per project:"
            echo "    echo 'export CODEX_HOME=\"\$PWD/.codex\"' > .envrc"
            echo "    direnv allow"
        fi
        ;;
    copilot)
        TOTAL=1
        print_tool_status "GitHub Copilot CLI" "copilot" "Run 'copilot' and use /login to authenticate with GitHub" "ai_tools_copilot" "npm" && INSTALLED=1
        ;;
    all)
        TOTAL=4
        print_tool_status "Claude Code" "claude" "Run 'claude' to authenticate with Anthropic" "ai_tools_claude" "npm" && INSTALLED=$((INSTALLED + 1))
        print_tool_status "Gemini CLI" "gemini" "Export GOOGLE_API_KEY in your shell profile" "ai_tools_gemini" "npm" && INSTALLED=$((INSTALLED + 1))
        if print_tool_status "OpenAI Codex CLI" "codex" "Run 'codex' to authenticate and start" "" "npm"; then
            INSTALLED=$((INSTALLED + 1))
            echo "  Spec-Kit auto setup per project:"
            echo "    echo 'export CODEX_HOME=\"\$PWD/.codex\"' > .envrc"
            echo "    direnv allow"
        fi
        print_tool_status "GitHub Copilot CLI" "copilot" "Run 'copilot' and use /login to authenticate with GitHub" "ai_tools_copilot" "npm" && INSTALLED=$((INSTALLED + 1))
        ;;
esac

echo ""
echo "Summary: $INSTALLED/$TOTAL installed."

if [[ "$TARGET" == "claude" || "$TARGET" == "all" ]]; then
    if command -v claude &> /dev/null; then
        echo ""
        echo "MCP configuration check:"
        SCRIPT_DIR="$(dirname "$0")"
        REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
        if [ -f "$REPO_DIR/.mcp.json" ]; then
            echo "  ✓ MCP configuration exists"
        else
            echo "  ⚠ MCP config missing (optional for CLI installation)"
        fi
    fi
fi

if [[ $INSTALLED -eq 0 ]]; then
    exit 1
fi
