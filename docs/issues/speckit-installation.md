# Issue: SpecKit CLI not in baseline; per-project files must not be committed

**Status:** Fixed — added specify to baseline, added .gitignore entries
**Affects:** Any user on a fresh machine who tries to use $speckit-* skills

## Problem

`specify` (SpecKit CLI) is not in the dotfiles baseline. On a fresh machine,
`./setup` never installs it, so `$speckit-*` skills fail with:

    specify: command not found

Additionally, running `specify init --here` on the dotfiles repo itself created
185+ per-project scaffolding files (`.specify/`, `.agents/skills/speckit-*`).
These are not dotfiles to distribute — committing them would force a specific
coding-agent integration (e.g. codex) onto every user.

## Root cause

Two gaps:
1. `dotfiles_tools/baseline.py` has no entry for `specify`.
2. `.gitignore` has no entry for `.specify/` or `.agents/`.

## Fix applied

- `specify` added to `TOOL_BASELINE` with `uv_tool` install method.
- `.specify/` and `.agents/` added to `.gitignore`.
- Post-install guidance: run `specify init --here` in each project to choose
  your preferred coding-agent integration (codex, claude, gemini, etc.).

## Expected outcome

`./setup` installs `specify` on a fresh machine. Per-project SpecKit files
are never tracked by git. Users run `specify init --here` in their own
projects to set up the integration they want.
