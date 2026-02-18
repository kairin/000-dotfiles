#!/bin/bash
# check_ai_tools.sh - Check status of AI CLI tools (aggregate or per-tool via TOOL_ID)
# Supported TOOL_ID values:
# - ai_claude, ai_gemini, ai_codex, ai_copilot
# - ai_tools (aggregate legacy mode)

set -u

# Ensure fnm environment is loaded
if command -v fnm &> /dev/null; then
    eval "$(fnm env --use-on-cd 2>/dev/null)" || true
fi

# Ensure npm global bin is in PATH
if command -v npm &> /dev/null; then
    NPM_BIN=$(npm config get prefix 2>/dev/null)/bin
    export PATH="$NPM_BIN:$PATH"
fi

tool_key_from_id() {
    case "${TOOL_ID:-ai_tools}" in
        ai_claude) echo "claude" ;;
        ai_gemini) echo "gemini" ;;
        ai_codex) echo "codex" ;;
        ai_copilot) echo "copilot" ;;
        *) echo "all" ;;
    esac
}

check_tool() {
    local key="$1"
    case "$key" in
        claude)
            if command -v claude &> /dev/null; then
                local ver
                ver=$(claude --version 2>/dev/null | head -n 1 | grep -oP '\d+\.\d+\.\d+' || echo "installed")
                echo "1|$ver|$(command -v claude)"
            else
                echo "0|-|-"
            fi
            ;;
        gemini)
            if command -v gemini &> /dev/null; then
                local ver
                ver=$(gemini --version 2>/dev/null | head -n 1 | grep -oP '\d+\.\d+\.\d+' || echo "installed")
                echo "1|$ver|$(command -v gemini)"
            else
                echo "0|-|-"
            fi
            ;;
        codex)
            if command -v codex &> /dev/null; then
                local ver
                ver=$(codex --version 2>/dev/null | head -n 1 | grep -oP '\d+\.\d+\.\d+' || echo "installed")
                echo "1|$ver|$(command -v codex)"
            else
                echo "0|-|-"
            fi
            ;;
        copilot)
            if command -v copilot &> /dev/null; then
                local ver
                ver=$(copilot --version 2>/dev/null | head -n 1 | grep -oP '\d+\.\d+\.\d+' || echo "installed")
                echo "1|$ver|$(command -v copilot)"
            else
                echo "0|-|-"
            fi
            ;;
    esac
}

latest_version() {
    local key="$1"
    case "$key" in
        claude)
            timeout 5 curl -sL "https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/latest/manifest.json" 2>/dev/null | \
                grep -oP '"version":\s*"\K[^"]+' || echo "-"
            ;;
        gemini)
            if command -v npm &> /dev/null; then
                timeout 5 npm view @google/gemini-cli version 2>/dev/null || echo "-"
            else
                echo "-"
            fi
            ;;
        codex)
            if command -v npm &> /dev/null; then
                timeout 5 npm view @openai/codex version 2>/dev/null || echo "-"
            else
                echo "-"
            fi
            ;;
        copilot)
            if command -v npm &> /dev/null; then
                timeout 5 npm view @github/copilot version 2>/dev/null || echo "-"
            else
                echo "-"
            fi
            ;;
    esac
}

emit_single_tool() {
    local key="$1"
    local label="$2"
    local method="$3"

    IFS='|' read -r installed ver loc <<< "$(check_tool "$key")"
    local latest="-"
    latest=$(latest_version "$key")

    if [[ "$installed" == "1" ]]; then
        if [[ "$key" == "codex" ]]; then
            loc="$loc^Spec-Kit auto setup:^  echo 'export CODEX_HOME=\"\$PWD/.codex\"' > .envrc^  direnv allow"
        fi
        echo "INSTALLED|$ver|$method|$loc|$latest"
    else
        echo "NOT_INSTALLED|-|$method|-|$latest"
    fi
}

emit_aggregate() {
    IFS='|' read -r claude_i claude_v _ <<< "$(check_tool claude)"
    IFS='|' read -r gemini_i gemini_v _ <<< "$(check_tool gemini)"
    IFS='|' read -r codex_i codex_v _ <<< "$(check_tool codex)"
    IFS='|' read -r copilot_i copilot_v _ <<< "$(check_tool copilot)"

    local total=$((claude_i + gemini_i + codex_i + copilot_i))
    local status="NOT_INSTALLED"
    local version="-"
    local method="-"
    local location="-"

    if [[ $total -gt 0 ]]; then
        status="INSTALLED"
        version="${total}/4 tools"
        method="mixed"
        location="curl+npm^tools:^     $([[ $claude_i -eq 1 ]] && echo "✓ Claude Code v${claude_v}" || echo "✗ Claude Code")^     $([[ $gemini_i -eq 1 ]] && echo "✓ Gemini CLI v${gemini_v}" || echo "✗ Gemini CLI")^     $([[ $codex_i -eq 1 ]] && echo "✓ OpenAI Codex CLI v${codex_v}" || echo "✗ OpenAI Codex CLI")^     $([[ $copilot_i -eq 1 ]] && echo "✓ GitHub Copilot CLI v${copilot_v}" || echo "✗ GitHub Copilot CLI")"
    fi

    local latest="-"
    if [[ "$claude_i" -eq 1 ]] && [[ "$(latest_version claude)" != "$claude_v" ]] && [[ "$(latest_version claude)" != "-" ]]; then
        latest="updates"
    fi
    if [[ "$gemini_i" -eq 1 ]] && [[ "$(latest_version gemini)" != "$gemini_v" ]] && [[ "$(latest_version gemini)" != "-" ]]; then
        latest="updates"
    fi
    if [[ "$codex_i" -eq 1 ]] && [[ "$(latest_version codex)" != "$codex_v" ]] && [[ "$(latest_version codex)" != "-" ]]; then
        latest="updates"
    fi
    if [[ "$copilot_i" -eq 1 ]] && [[ "$(latest_version copilot)" != "$copilot_v" ]] && [[ "$(latest_version copilot)" != "-" ]]; then
        latest="updates"
    fi

    echo "${status}|${version}|${method}|${location}|${latest}"
}

case "$(tool_key_from_id)" in
    claude) emit_single_tool "claude" "Claude Code" "curl" ;;
    gemini) emit_single_tool "gemini" "Gemini CLI" "npm" ;;
    codex) emit_single_tool "codex" "OpenAI Codex CLI" "npm" ;;
    copilot) emit_single_tool "copilot" "GitHub Copilot CLI" "npm" ;;
    *) emit_aggregate ;;
esac
