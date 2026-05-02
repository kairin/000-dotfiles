# Issue: menu option numbers change between first and subsequent runs

**Status:** Open — by design, but disorienting  
**Affects:** Users who run setup more than once

## Problem

On first run (tools missing), "Install/update developer tools" is option 1.
After tools are installed, the menu reorders: option 1 becomes "Apply safe changes"
and "Install/update developer tools" moves to option 5. Muscle memory breaks.

## Root cause

The menu is state-aware: it promotes the most relevant action to option 1 based
on whether tools are missing. This is intentional but there is no warning that
options will shift after a successful install.

## Agreed fix direction

Stable option numbers regardless of state. The recommended action for the current
state is highlighted (e.g. `[recommended]` tag or visual indicator), but option
numbers never change between runs.

## Expected outcome

A user who ran option 1 on first run finds option 1 in the same position on every
subsequent run. The currently-recommended action is visually distinct but the
numbering is stable.
