# Issue: menu option numbers change between first and subsequent runs

**Status:** Fixed in PR #82 — stable 5-option menu with [recommended] tag  
**Affects:** Users who run setup more than once

## Problem

On first run (tools missing), "Install/update developer tools" is option 1.
After tools are installed, the menu reorders: option 1 becomes "Apply safe changes"
and "Install/update developer tools" moves to option 5. Muscle memory breaks.

## Root cause

The menu is state-aware: it promotes the most relevant action to option 1 based
on whether tools are missing. This is intentional but there is no warning that
options will shift after a successful install.

## Fix applied

Implemented stable 5-option menu regardless of machine state:

```
1. Install / update developer tools  [recommended when tools missing]
2. Apply safe non-protected dotfiles  [recommended when tools present]
3. Show full technical details
4. Show tool and sign-in guidance
5. Exit without writing
```

Option numbers are fixed on every run. The `[recommended]` tag moves to indicate
the best action for the current state (option 1 when tools are missing, option 2
when tools are present and configs have drifted). A user who ran option 1 on
first run finds option 1 in the same position on every subsequent run.
