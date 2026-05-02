# Implementation Plan: Setup Menu Recommendation Guidance

**Branch**: `20260503-setup-menu-recommendation` | **Date**: 2026-05-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-setup-menu-recommendation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Make the interactive `./setup` machine menu show one unmistakable recommended
next step for the user's current system state. The recommendation will be
derived from the same audited tool, dotfile, font, blocker, auth-guidance, and
incomplete/failed status-audit states shown in the machine summary, then
rendered consistently in the summary and stable five-option menu. The guided
fresh-machine path will return to a refreshed summary and menu after the tool
install/update step, matching the README and getting-started documentation.

## Technical Context

**Language/Version**: Bash for the `./setup` wrapper; Python 3.11+ standard library for `dotfiles_tools`
**Primary Dependencies**: Python standard library and existing shell tools only; no new runtime dependencies
**Storage**: No new persistent storage; reads existing manifest/status data and writes only existing setup artifacts during approved setup actions
**Testing**: `uv run python -m unittest discover -s tests`; supplemental focused checks in existing `tests/test_machine_summary.py`, `tests/test_setup_script.py`, and `tests/test_docs.py`
**Target Platform**: Linux-like developer machines supported by the existing setup flow, including Ubuntu, WSL, Raspberry Pi, Pixel Terminal, and Pixel AVF
**Project Type**: Repository-local CLI and shell wrapper enhancement
**Performance Goals**: Recommendation decision adds no meaningful delay beyond the existing summary audit; no duplicate expensive probes in the common menu path
**Constraints**: Keep option numbers stable; recommendation must be plain-text visible; no protected-file edits; no lock file; no new runtime dependency; writes still require explicit confirmation and backups
**Scale/Scope**: Machine setup menu invoked by `./setup` with no arguments; project-folder menus are out of scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Template Source of Truth**: PASS. The feature does not edit `.template`
  files or AGENTS.md symlink conventions.
- **Secret-Free and Identity-Safe**: PASS. The feature changes menu guidance
  only and does not add credentials, auth files, tokens, or identity behavior.
- **Protected Files**: PASS. `git/config`, `fish/fish_plugins`, `.gitignore`,
  and symlinked agent templates remain untouched.
- **Reproducible Bootstrap**: PASS. Recommendation is derived from existing
  manifest-backed audit/plan data, keeps dry-run visibility, and preserves
  explicit apply approval plus backup behavior.
- **Validation Before Coverage**: PASS. Planning requires focused tests for the
  new recommendation states before any coverage signal is relevant.
- **uv Python Workflow**: PASS. Validation commands use `uv`; runtime code uses
  only the Python standard library and existing Bash wrapper.

## Project Structure

### Documentation (this feature)

```text
specs/002-setup-menu-recommendation/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── setup-menu.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
setup

dotfiles_tools/
├── machine_summary.py
├── bootstrap.py
├── tool_installer.py
├── baseline.py
└── reports.py

tests/
├── test_machine_summary.py
├── test_setup_script.py
└── test_docs.py

README.md
docs/
└── getting-started.md
```

**Structure Decision**: Extend the existing setup wrapper and
`dotfiles_tools.machine_summary` recommendation path. Keep recommendation
calculation in Python so tests can exercise state combinations without driving
the whole shell menu, and keep shell changes limited to rendering and looping
around the existing actions.

## Phase 0: Research

Research decisions are captured in [research.md](./research.md). Key resolved
decisions:

- Use one structured recommendation decision as the source of truth for summary
  and menu rendering.
- Preserve a plain `[recommended]` marker and add a nearby reason line.
- Use a documented priority order for incomplete/failed status audits,
  blockers, missing tools, safe writes, auth-only guidance,
  protected/manual-only states, and fully current state.
- Return to the machine summary/menu after tool install/update completes or is
  canceled.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md): machine setup state, recommendation,
  menu option, guided session, and documentation example.
- [contracts/setup-menu.md](./contracts/setup-menu.md): user-visible menu
  output and state-to-recommendation contract.
- [quickstart.md](./quickstart.md): validation commands and manual smoke flows.

## Constitution Check - Post-Design

- **Template Source of Truth**: PASS. Design does not alter template execution
  semantics or symlink source-of-truth rules.
- **Secret-Free and Identity-Safe**: PASS. Contracts and quickstart contain no
  secrets and do not change auth storage; auth remains manual guidance.
- **Protected Files**: PASS. Design keeps protected/manual files visible and
  excludes them from automatic safe apply behavior.
- **Reproducible Bootstrap**: PASS. Recommendation states are tied to existing
  audit/plan data and keep explicit apply confirmation and backup guarantees.
- **Validation Before Coverage**: PASS. Quickstart and plan call for focused
  unit tests before coverage.
- **uv Python Workflow**: PASS. All Python validation commands use `uv` and no
  runtime dependency or lock-file change is introduced.

## Complexity Tracking

No constitution violations are accepted for this feature.
