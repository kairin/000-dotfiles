# Troubleshooting

Common failures are usually one of four things: a missing `uv`, a tool install problem, config drift, or a font issue.

## `uv: command not found`

`./setup` installs `uv` if it is missing. If the bootstrap step fails, verify the install path and reload your shell.

```bash
which uv
exec fish
```

## Tool Install Failed

Most tool installs come from `apt`, `npm`, or `uv`.
Use option 3 in `./setup` or `./setup doctor` to inspect the current state, then retry the installer once the missing prerequisite is present.

## Config Drift

If the menu reports drift, choose option 2 to review the pending changes.
Backups are created before overwrite and are stored in `~/.dotfiles-backups/` by default.

## Font Icons Look Broken

Set your terminal font to a `* Nerd Font Mono` face such as `JetBrainsMono Nerd Font Mono`.
If the terminal does not show that font, choose a different installed Nerd Font Mono variant.

## Restore A File

If you overwrite a file you wanted to keep, restore it from the backup directory.

```bash
ls ~/.dotfiles-backups/
cp ~/.dotfiles-backups/settings.json ~/.claude/settings.json
```
