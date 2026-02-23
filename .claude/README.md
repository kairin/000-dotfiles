# .claude Directory

Agent-related documentation and source templates used in this repository.

## Purpose

- Store agent instruction sources and operational docs.
- Keep `AGENTS.md` as the single source of truth for cross-assistant rules.
- Provide install/sync helpers for user-level Claude assets.

## Important Rules

- Do not replace symlinks `CLAUDE.md` and `GEMINI.md` with regular files.
- Edit `AGENTS.md` for shared policy changes.
- Prefer existing scripts; avoid creating new helper wrappers.

## Common Commands

```bash
# Install Claude assets to user profile
./scripts/install-claude-config.sh

# Check status
./scripts/status-claude-config.sh

# Remove installed assets
./scripts/uninstall-claude-config.sh
```

## Related

- `AGENTS.md`
- `.claude/instructions-for-agents/README.md`
