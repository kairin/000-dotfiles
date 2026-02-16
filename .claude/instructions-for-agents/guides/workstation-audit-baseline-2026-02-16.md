---
title: Workstation Audit Baseline (2026-02-16)
category: guides
linked-from: AGENTS.md
status: ACTIVE
last-updated: 2026-02-16
---

# Workstation Audit Baseline (2026-02-16)

[← Back to AGENTS.md](../../../../AGENTS.md)

This document consolidates findings previously captured in ad-hoc root folders
`01/` and `02/`.

## Purpose

- Preserve actionable verification evidence in a maintained documentation path.
- Track unresolved drift items with concrete next steps.
- Standardize repeat-audit commands.

## Consolidated Inputs

- Prior ad-hoc verifier: `01/setup-doctor.sh` (now superseded by official audit)
- Exported setup notes and guide drafts from `02/`
- Local workstation checks run on 2026-02-16

## Current Findings (2026-02-16)

### Repository State

- `RAID_SETUP_SUMMARY.md` and `ROADMAP.md` are tracked.
- `CLAUDE.md` and `GEMINI.md` are symlinks to `AGENTS.md` (correct).
- Active spec work remains:
  - `specs/015-verbose-spinner-progress/tasks.md`: 0 done / 52 pending
  - `specs/008-mcp-server-dashboard/tasks.md`: 0 done / 100 pending

### Workstation Audit Status

Command:

```bash
./.runners-local/workflows/health-check.sh --workstation-audit
```

Observed summary (initial run, 2026-02-16):

- PASS=17
- WARN=1
- FAIL=3

Initial failing checks:

- `gh auth`
- `context7 (claude)`
- `context7 (codex)`

Remediation applied on 2026-02-16:

- Added Context7 MCP to Claude user config:
  `claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp`
- Added Context7 MCP to Codex global config:
  `codex mcp add context7 --url https://mcp.context7.com/mcp`

Post-remediation summary (after Context7 configuration):

- PASS=18
- WARN=2
- FAIL=1

Current remaining failure:

- `gh auth` (token invalid; refresh/login blocked by current network connectivity to GitHub)

Final verification summary (retry with network available, 2026-02-16):

- PASS=20
- WARN=1
- FAIL=0

Resolved item:

- `gh auth` now passes (`logged in as kairin`)

### RAID State

Historical RAID setup exists in `RAID_SETUP_SUMMARY.md`, but on this host
(checked 2026-02-16) no active mdraid arrays are present in `/proc/mdstat`.

### Roadmap Drift

Historical entries referenced missing spec directories:

- `specs/001-foundation-fixes/`
- `specs/006-tui-detail-views/`

Roadmap references were updated to mark these as archived/historical.

## Standard Repeat-Audit Commands

```bash
# Full local validation workflow
./.runners-local/workflows/gh-workflow-local.sh all

# Secret-safe workstation audit
./.runners-local/workflows/health-check.sh --workstation-audit

# Quick active spec workload snapshot
printf "015 done=%s pending=%s\n" "$(rg -n "^- \[x\]" specs/015-verbose-spinner-progress/tasks.md | wc -l)" "$(rg -n "^- \[ \]" specs/015-verbose-spinner-progress/tasks.md | wc -l)"
printf "008 done=%s pending=%s\n" "$(rg -n "^- \[x\]" specs/008-mcp-server-dashboard/tasks.md | wc -l)" "$(rg -n "^- \[ \]" specs/008-mcp-server-dashboard/tasks.md | wc -l)"
```

## Next Steps

1. Set `CONTEXT7_API_KEY` in shell environment to clear the remaining warning.
2. Re-run workstation audit after shell/session updates and record counts.

---

This baseline supersedes the temporary `01/` and `02/` working folders.
