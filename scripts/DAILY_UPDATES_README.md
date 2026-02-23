# Daily Updates System

Automated update orchestration for installed tools in `000-dotfiles`.

## Quick Start

```bash
# Check for available updates
./scripts/check_updates.sh

# Apply updates interactively
./scripts/daily-updates.sh

# Preview only (no changes)
./scripts/daily-updates.sh --dry-run
```

## Optional Aliases (Zsh)

After running `./start.sh` (or `./scripts/configure_zsh.sh`), these aliases are available:

| Alias | Description |
|-------|-------------|
| `update-all` | Run `./scripts/daily-updates.sh` |
| `update-check` | Run `./scripts/check_updates.sh` |
| `update-logs` | Show latest update summary from `.runners-local/logs/` |

## Update Workflow

`./scripts/daily-updates.sh` performs:

1. Detect updates using `./scripts/check_updates.sh --json`
2. Prompt for confirmation (unless `--non-interactive`)
3. Apply updates via existing `scripts/004-reinstall/install_*.sh` scripts
4. Run local validation with `./.runners-local/workflows/gh-workflow-local.sh all` (unless `--skip-validation`)
5. Write update summary logs

### Modes

```bash
# Interactive (default)
./scripts/daily-updates.sh

# Cron-friendly (no prompts)
./scripts/daily-updates.sh --non-interactive

# Dry run
./scripts/daily-updates.sh --dry-run

# Install daily cron at 9:00
./scripts/daily-updates.sh --install-cron
```

## Logs

Primary locations:

- `.runners-local/logs/update-summary-YYYYMMDD-HHMMSS.log`
- `.runners-local/logs/cron-updates.log` (when cron is enabled)

Useful commands:

```bash
# Latest summary via helper
source ./scripts/006-logs/logger.sh && show_latest_update_summary

# List summary files
ls -1 .runners-local/logs/update-summary-*.log
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All updates succeeded (or dry-run complete) |
| 1 | One or more updates failed |
| 2 | Post-update validation failed |
| 3 | Another update process is already running |
| 4 | Prerequisites missing |

## Supported Tools

Updates are applied by existing reinstall scripts in `scripts/004-reinstall/`, including:

- AI tools
- Fastfetch
- Feh
- Fish
- Glow
- Go
- Gum
- Nerd Fonts
- Node.js
- Python/uv
- VHS
- Zsh

## Troubleshooting

### Lock file exists

```bash
rm -f /tmp/daily-updates.lock
```

### Validation failed

```bash
./.runners-local/workflows/gh-workflow-local.sh all
```

### No updates detected

This is normal when installed tools already match latest available versions.

## Related

- [Scripts Directory Index](README.md)
- [Update Scripts](007-update/README.md)
- [Logging Guide](../.claude/instructions-for-agents/guides/LOGGING_GUIDE.md)
