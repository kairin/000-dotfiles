# Issue: dev_base always reports needs_update (dnsutils alias)

**Status:** Open — bug in baseline.py package check  
**Affects:** All users on Ubuntu 22.04+ and WSL

## Problem

`dotfiles_tools` always reports `tools.dev_base: needs_update` and
`network 3/4 installed (missing: dnsutils)`, even on fully configured machines.
This prompts unnecessary reinstall attempts on every run.

## Root cause

`dotfiles_tools/baseline.py:178` lists `"dnsutils"` as a required network package.
On Ubuntu 22.04+, `dnsutils` is a virtual package that apt resolves to
`bind9-dnsutils`. The tool checks for the literal name `dnsutils`, which is never
reported as installed, so `dev_base` always shows missing.

## Fix required

`dotfiles_tools/baseline.py:178` — replace `"dnsutils"` with `"bind9-dnsutils"`,
or add virtual-package alias resolution so apt-resolved names are accepted.

## Expected outcome

`tools.dev_base` reports `installed` on Ubuntu 22.04+ machines where
`bind9-dnsutils` is present. No spurious update prompts.
