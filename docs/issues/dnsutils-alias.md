# Issue: dev_base always reports needs_update (dnsutils alias)

**Status:** Fixed in PR #82 — baseline.py updated to use bind9-dnsutils  
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

## Fix applied

`dotfiles_tools/baseline.py:215` — changed from `"dnsutils"` to `"bind9-dnsutils"`.
Ubuntu 22.04+ resolves the virtual package `dnsutils` to `bind9-dnsutils`; the
baseline now checks for the concrete package name so machines are never reported
as having a missing network package when it's actually installed.

## Expected outcome

`tools.dev_base` reports `installed` on Ubuntu 22.04+ machines where
`bind9-dnsutils` is present. No spurious update prompts.
