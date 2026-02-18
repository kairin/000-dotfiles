# Go TUI Architecture

Architecture notes for the installer in `tui/`.

## Purpose

The Go TUI provides interactive installation, update, and uninstall flows backed by existing shell scripts.

## Core Layout

- `tui/cmd/installer`: app entry point
- `tui/internal/registry`: tool and MCP registries
- `tui/internal/ui`: Bubble Tea views and interaction model
- `tui/internal/executor`: script execution and streaming output
- `tui/internal/detector`: installed-state checks
- `tui/internal/diagnostics`: boot diagnostics integration
- `tui/internal/cache`: status caching

## Data-Driven Tool Registry

Tool definitions include:
- tool ID
- display name
- category (main/extras)
- script bindings for lifecycle actions

Current main tools include:
- Feh, Nerd Fonts, Node.js
- Claude Code, Gemini CLI, OpenAI Codex CLI, GitHub Copilot CLI
- Google Antigravity, Fish + Fisher

Extras include Fastfetch, Glow, Go, Gum, Python/uv, VHS, Zsh, ShellCheck, and icon cache utilities.

## Execution Model

- Installer triggers shell scripts under `scripts/`.
- Script stdout/stderr is streamed into the TUI for visibility.
- Status checks are cached to avoid repeated expensive probes.

## Build and Run

```bash
cd tui
go run ./cmd/installer
```

User-facing invocation remains:

```bash
./start.sh
```
