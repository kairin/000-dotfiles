# Protected Files

Some files in this repo are reported by validation, but the setup flow does not overwrite them automatically.
They either contain local identity, are manually curated, or are symlink anchors that must stay consistent.

## Protected Targets In This Repo

- `git/config` - git identity and credential helper behavior
- `fish/fish_plugins` - manually curated plugin list
- `.gitignore` - ignore rules that should be edited intentionally
- `agents/CLAUDE.md.template` - symlink anchor for project-level agent docs
- `agents/GEMINI.md.template` - symlink anchor for project-level agent docs

## Why They Stay Protected

- `git/config` affects all git operations for the user.
- `fish/fish_plugins` may require a manual `fisher update`.
- `.gitignore` changes can expose secrets or noisy files.
- The agent template symlinks keep one source of truth for project docs.

## How To Override

Protected items stay visible in the plan, but they are not auto-written unless you explicitly include them in the apply command by manifest ID.
Use the direct CLI only when you intend to replace one of these files and are prepared to review the backup behavior first.
