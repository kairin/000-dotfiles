---
name: dotfiles-apply
description: Use when syncing machine state with dotfiles (installing tools, applying config files, validating setup) using the doctor/plan/apply workflow
tags: [dotfiles, setup, installation, validation, configuration]
---

# Dotfiles Apply

## Overview

Orchestrates the dotfiles validation and application workflow: **doctor** (diagnose current state) → **plan** (show what will change) → **apply** (make changes). Safe by default (backs up before overwriting), stops on first failure, and preserves user customizations.

This skill wraps the `dotfiles_tools` Python CLI which powers the `./setup` entrypoint.

## When to Use

Use this skill when:
- First machine setup (after git clone)
- Syncing after pulling dotfiles updates
- Adding new config files to manifest
- Validating that dotfiles are correctly applied
- Recovering from manual config changes

**NOT for:**
- One-off file edits (edit directly instead)
- Temporary testing (changes are persistent)
- Emergency hotfixes (manual edits faster)

## The Three Phases

### Phase 1: Doctor (Diagnose)
Scans current state without making changes. Reports:
- Missing files or symlinks
- Files that differ from source
- Protected files needing manual review
- Validation errors (templates, secrets, syntax)

```bash
uv run python -m dotfiles_tools doctor --repo . --home $HOME
```

**Output:** Report of all issues, categorized by severity

### Phase 2: Plan (Preview)
Shows exactly what `apply` will do (without doing it):
- Which files will be backed up
- Which files will be overwritten
- Which protected files are skipped
- Which symlinks will be created

```bash
uv run python -m dotfiles_tools plan --repo . --home $HOME --profile machine
```

**Output:** Ordered list of operations with backup paths

### Phase 3: Apply (Execute)
Actually makes the changes:
1. Backs up changed files to `~/.dotfiles-backups/`
2. Applies files in order
3. Stops immediately on first failure (backups intact)
4. Reports what succeeded and what failed

```bash
uv run python -m dotfiles_tools apply --repo . --home $HOME --profile machine --yes
```

**Output:** Operation log showing what changed, what failed, where backups are

## Quick Reference

| Command | What It Does | Output |
|---------|-------------|--------|
| `doctor` | Scan without changes | Status report (no changes made) |
| `plan` | Show what will change | List of operations (no changes made) |
| `apply` | Actually apply changes | Log of successes + failures |

**Golden rule:** Always run `doctor` then `plan` before `apply`.

## How to Run

### From Claude Code
```
/dotfiles-apply
```
(Will prompt: which phase do you want to run?)

### From Terminal
```bash
cd ~/Apps/000-dotfiles-main

# Phase 1: Diagnose
uv run python -m dotfiles_tools doctor --repo . --home $HOME

# Phase 2: Preview
uv run python -m dotfiles_tools plan --repo . --home $HOME --profile machine

# Phase 3: Apply (if you trust the plan)
uv run python -m dotfiles_tools apply --repo . --home $HOME --profile machine --yes
```

### Via Setup Menu
```bash
./setup
# Select Option 2: "Apply safe non-protected dotfiles"
# Automatically runs doctor → plan → apply with safe defaults
```

## Common Mistakes

**Running `apply` without first running `doctor` and `plan`**
- Result: Changes made without understanding impact
- Fix: Always do doctor → plan → apply in sequence

**Applying without backing up important files**
- Result: Overwritten files lost
- Fix: `apply` automatically backs up before overwriting; backups in `~/.dotfiles-backups/`

**Ignoring protected file warnings**
- Result: Critical files (git config, fish_plugins) accidentally overwritten
- Fix: Protected files require explicit approval via `--include-protected flag`

**Re-applying after manual edits without running doctor first**
- Result: Your manual changes get overwritten
- Fix: Always run doctor to see what changed; plan before applying

**Assuming profile doesn't matter ("it's just config")**
- Result: Wrong profile applied (e.g., machine tools installed when only user profile intended)
- Fix: Specify correct profile (`--profile machine` or `--profile user`)

## Expected Output

### Doctor Output
```
Scanning ~/Apps/000-dotfiles-main → ~

✓ Symlinks valid (4/4)
⚠ Drifted files (2):
  • ~/.config/fish/env.fish (user customizations preserved)
  • ~/.config/git/config (committed changes override local)
⚠ Protected files (3 - manual review required):
  • agents/CLAUDE.md.template → symlink target change
  • git/config → committer identity
  • fish/fish_plugins → manual fisher update needed

Status: ⚠ needs_merge (can apply)
```

### Plan Output
```
Applying machine profile:
  1. Backup ~/.config/fish/env.fish → ~/.dotfiles-backups/20250503/env.fish
  2. Update ~/.config/fish/env.fish (changed: direnv.fish auto-source)
  3. Update ~/.config/git/config (changed: 2 new tool sections)
  4. Create symlink: CLAUDE.md → AGENTS.md

Total: 4 changes, 1 backup, 0 failures (estimated)
```

### Apply Output
```
Applying 4 operations...
  ✓ Backed up ~/.config/fish/env.fish
  ✓ Updated ~/.config/fish/env.fish
  ✓ Updated ~/.config/git/config
  ✓ Created symlink: CLAUDE.md → AGENTS.md

Status: ✓ applied (all 4 operations succeeded)
Backups: ~/.dotfiles-backups/20250503/
```

## Profiles Explained

- **`machine`** — Tools + system config (git, fish, shell env, direnv)
  - Use when: Setting up a new machine or after major OS update
  - Scope: System-wide tools and shell configuration

- **`user`** — User-facing editor/IDE config (Claude Code, Codex, Gemini, VS Code)
  - Use when: Setting up IDE on an existing machine
  - Scope: Editor config and AI tool settings

Choose based on what changed or what you're setting up.

## Troubleshooting

**"Protected file: agents/CLAUDE.md.template (symlink)"**
- Meaning: This is a special file that's a symlink; changing it breaks the single-source-of-truth pattern
- Fix: Never directly edit; understand why it's protected, then acknowledge with `--include-protected agents/CLAUDE.md.template`

**"Validation error: secret-like finding in dotfiles_tools/doctor.py line 42"**
- Meaning: Detector found something that looks like a secret (API key, token, password)
- Fix: Check if it's a real secret (NEVER commit); if false positive, document in git history why it's there

**"User customization: ~/.config/fish/env.fish"**
- Meaning: File has user edits; applying dotfiles source will overwrite them
- Fix: Manually merge changes, or keep user version and skip dotfiles update

**"Apply failed: Backup directory not writable"**
- Meaning: Can't write to ~/.dotfiles-backups/ (permission issue)
- Fix: `mkdir -p ~/.dotfiles-backups && chmod 700 ~/.dotfiles-backups`

## Real-World Impact

Before dotfiles apply:
- Manual file copying
- Easy to miss updates
- Hard to undo changes
- No backup safety
- Result: Hours of manual setup

After dotfiles apply:
- One command syncs everything
- Doctor shows what changed
- Plan previews impact
- Apply backs up automatically
- Result: 2-3 minutes, safe, reversible
