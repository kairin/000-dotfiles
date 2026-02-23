# AI CLI Tools

AI CLI tooling managed by the installer pipeline.

## Supported CLIs

| Tool | Package / Method |
|------|------------------|
| Claude Code | `@anthropic-ai/claude-code` (installer script via curl + npm) |
| Gemini CLI | `@google/gemini-cli` |
| OpenAI Codex CLI | `@openai/codex` |
| GitHub Copilot CLI | `@github/copilot` |
| Spec-Kit CLI | `specify-cli` via `uv tool` |

## Script Coverage

| Stage | Script |
|-------|--------|
| Check | `scripts/000-check/check_ai_tools.sh` |
| Uninstall | `scripts/001-uninstall/uninstall_ai_tools.sh` |
| Install deps | `scripts/002-install-first-time/install_deps_ai_tools.sh` |
| Verify deps | `scripts/003-verify/verify_deps_ai_tools.sh` |
| Install/Reinstall | `scripts/004-reinstall/install_ai_tools.sh` |
| Confirm | `scripts/005-confirm/confirm_ai_tools.sh` |
| Update | `scripts/007-update/update_ai_tools.sh` |

## Spec-Kit with Codex

For per-project command discovery, set `CODEX_HOME` with `direnv` in each project:

```bash
echo 'export CODEX_HOME="$PWD/.codex"' > .envrc
direnv allow
```

## Verify Installed Versions

```bash
claude --version
gemini --version
codex --version
copilot --version
specify --version
```
