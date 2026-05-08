# Issue: menu option numbers change between first and subsequent runs

**Status:** Fixed in PR #82 — stable 6-option menu with [recommended] tag
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

Implemented stable 6-option menu regardless of machine state:

```
1. Install / update developer tools  [recommended when tools missing]
2. Apply safe non-protected dotfiles  [recommended when tools present]
3. Show full technical details
4. Show tool and sign-in guidance
5. Configure / verify API tokens
6. Exit without writing
```

Option numbers are fixed on every run. The `[recommended]` tag moves to indicate
the best action for the current state (option 1 when tools are missing, option 2
when tools are present and configs have drifted). Option 1 now opens a phased
submenu so the tool install/update work can be split into dev-base packages,
tool installers, and post-install verification without changing the top-level
menu numbers. Option 5 now opens a second submenu so verification-only,
auto post-install actions, and manual guidance can be inspected separately.
