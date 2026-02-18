# Tool Implementation Reference

Reference index for tools managed by the installer pipeline.

## Managed Tools

Main:
- `feh`
- `nerdfonts`
- `nodejs`
- `ai_claude`
- `ai_gemini`
- `ai_codex`
- `ai_copilot`
- `antigravity`
- `fish`

Extras:
- `fastfetch`
- `glow`
- `go`
- `gum`
- `python-uv`
- `vhs`
- `zsh`
- `shellcheck`
- `icon_cache`

## Script Lifecycle

Tool scripts follow staged directories under `scripts/`:
- `000-check`
- `001-uninstall`
- `002-install-first-time`
- `003-verify`
- `004-reinstall`
- `005-confirm`
- `007-update`

## Entry Point

For users, always document `./start.sh` as the installation and management command.

## Key References

- [AI CLI Tools](ai-cli-tools.md)
- [Node.js](nodejs.md)
- [Fish](fish.md)
- [ZSH](zsh.md)
- [Nerd Fonts](nerdfonts.md)
