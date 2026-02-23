# Directory Structure

High-level structure for the repository.

```text
000-dotfiles/
├── AGENTS.md
├── CLAUDE.md -> AGENTS.md
├── GEMINI.md -> AGENTS.md
├── README.md
├── start.sh
├── install.sh
├── .claude/
│   ├── instructions-for-agents/
│   ├── agent-sources/
│   └── skill-sources/
├── .codex/
│   └── skills/
├── .runners-local/
│   ├── workflows/
│   └── logs/
├── configs/
│   ├── mcp/
│   └── zsh/
├── scripts/
│   ├── 000-check/
│   ├── 001-uninstall/
│   ├── 002-install-first-time/
│   ├── 003-verify/
│   ├── 004-reinstall/
│   ├── 005-confirm/
│   ├── 006-logs/
│   ├── 007-diagnostics/
│   ├── 007-update/
│   └── vhs/
└── tui/
    ├── cmd/installer/
    └── internal/
```

## Notes

- Use `./start.sh` for user instructions.
- `scripts/` is the canonical automation layer.
- `tui/internal/registry/` is the source of truth for installable tool definitions.
