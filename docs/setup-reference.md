# Setup Reference

This page documents the `./setup` wrapper and the stable `dotfiles_tools` commands it exposes.

## `./setup` Commands

| Command | What it does |
|---|---|
| `./setup` | Audit the machine, present the recommendation-aware menu, and optionally apply tool or config changes |
| `./setup /path/to/project` | Inspect a project folder and offer agent-doc actions |
| `./setup init [--project PATH] [--vars FILE] [--copilot] --yes` | Render project agent docs and symlinks |
| `./setup verify [--project PATH] [--copilot]` | Read-only project doc validation |
| `./setup doctor [--home PATH] [--profile NAME]` | Read-only machine audit |

## Direct CLI

These are the stable commands that `./setup` wraps:

```bash
uv run python -m dotfiles_tools doctor --repo . --home "$HOME"
uv run python -m dotfiles_tools plan --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools bootstrap-plan --repo . --home "$HOME" --json
uv run python -m dotfiles_tools bootstrap-apply --repo . --home "$HOME" --yes
uv run python -m dotfiles_tools init-project --repo . --project /path/to/project --vars project-vars.json --yes
```

`doctor` audits without writing. `plan` prints exact operations. `apply` writes only after `--yes` and creates backups first.
`bootstrap-plan` and `bootstrap-apply` include the font recipes used by the interactive machine menu.

## PATH Installation

Install the wrapper on your `PATH` with a symlink:

```bash
ln -s /path/to/000-dotfiles/setup ~/.local/bin/dotfiles-setup
dotfiles-setup verify --project ~/code/my-app
```

## Recommendation Menu

The interactive menu always keeps the option numbers stable:

1. Install / update developer tools
2. Apply safe non-protected dotfiles
3. Show full technical details
4. Show tool and sign-in guidance
5. Exit without writing

The summary line marks one option as recommended based on the audited state.
