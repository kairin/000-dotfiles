# Issue: keybindings.json rejected by /doctor

**Status:** Template fix applied — live file patched, source template corrected  
**Affects:** Any user running `dotfiles apply` then `/doctor`

## Problem

`claude/keybindings.json.template` previously contained `[]`. Claude Code's
`/doctor` rejects a bare JSON array and requires the object form
`{ "bindings": [] }`, producing:

```
✘ keybindings.json must have a "bindings" array
  Use format: { "bindings": [ ... ] }
```

## Root cause

`claude/keybindings.json.template` line 1 was `[]` instead of `{ "bindings": [] }`.
When `dotfiles apply` deployed this file, it created a malformed
`~/.claude/keybindings.json` that `/doctor` rejected.

## Fix applied

`claude/keybindings.json.template` has been corrected:
- Before: `[]`
- After:  `{ "bindings": [] }`

## Expected outcome

`/doctor` reports no keybinding error after `dotfiles apply`.
