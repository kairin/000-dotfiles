# Implementation Plan: Dotfiles Bootstrap Validation

**Branch**: `001-dotfiles-bootstrap-validation` | **Date**: 2026-05-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-dotfiles-bootstrap-validation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a manifest-backed validation and setup CLI for this dotfiles repository. The
CLI will expose canonical commands `doctor`, `plan`, `apply`, and
`init-project`, use human-readable output by default, and provide stable JSON
reports for tests and automation. Implementation uses a standard-library Python
package at repository root, with `uv` used for all Python command execution and
coverage measurement. The plan includes a root manifest, safe protected-file
handling, backup-before-replace apply semantics, project agent-doc
initialization, a unittest suite using temporary directories, and a GitHub
Actions workflow that generates `coverage.xml` before optional Codacy upload.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Python standard library only for runtime; `coverage` only for measurement in CI/local coverage commands
**Storage**: Repository files, target home/project files, timestamped backup files, and JSON reports; no database
**Testing**: `uv run python -m unittest discover -s tests`; coverage via `uv run --with coverage coverage ...`
**Target Platform**: Linux-like developer machines and GitHub Actions runners
**Project Type**: Single repository CLI/tooling package
**Performance Goals**: Complete `doctor` or `plan` for the current manifest in under 2 seconds on a typical developer machine; avoid unnecessary rewrites of current files
**Constraints**: No runtime third-party dependencies; no lock file unless runtime dependencies are introduced later; never touch the real user home in tests; protected targets are manual by default; apply writes require explicit `--yes`; partial apply stops on the first failed write
**Scale/Scope**: One machine profile and one project initialization workflow in the first increment; manifest entries cover the current repo templates and protected/manual files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Template Source of Truth**: PASS. `.template` files remain copy-and-customize sources; root and project agent symlink conventions are validated and preserved.
- **Secret-Free and Identity-Safe**: PASS. Secret scanning is a required validation surface; protected identity targets remain manual by default.
- **Protected Files**: PASS. `git/config`, `fish/fish_plugins`, `.gitignore`, and symlinked agent templates are protected/manual by default and require exact manifest entry ID opt-in.
- **Reproducible Bootstrap**: PASS. Setup is manifest-driven, dry-run capable through `doctor` and `plan`, idempotent, and backs up differing targets before writes.
- **Validation Before Coverage**: PASS. Runtime validation code and tests are planned before `coverage.xml` generation and optional Codacy upload.
- **uv Python Workflow**: PASS. Python test and coverage commands use `uv`; runtime code uses the standard library.

## Project Structure

### Documentation (this feature)

```text
specs/001-dotfiles-bootstrap-validation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── manifest.schema.json
└── tasks.md
```

### Source Code (repository root)

The first increment delivered the canonical `doctor`/`plan`/`apply`/`init-project`
commands. Subsequent increments added the `./setup` entrypoint, machine summary
dashboard, baseline tool checks, and platform-aware font recipes. The current
module inventory below is the as-built state.

```text
dotfiles-manifest.json
setup                   # bash entrypoint that wraps dotfiles_tools with sensible defaults
dotfiles_tools/
├── __init__.py
├── __main__.py
├── cli.py              # argparse dispatch
├── manifest.py         # manifest dataclasses, validation, path resolution
├── doctor.py           # repo + symlink + target-state evaluation
├── installer.py        # plan/apply for manifest entries (mkdir/copy/symlink/backup)
├── bootstrap.py        # orchestrates manifest installer + font recipes
├── backups.py          # timestamped backup paths and copy semantics
├── reports.py          # human + stable JSON renderer; summary computation
├── templates.py        # template rendering and parseability checks
├── placeholders.py     # placeholder discovery and substitution
├── secrets.py          # secret-like content scanner with allowlist behavior
├── project_init.py     # AGENTS.md render + CLAUDE.md/GEMINI.md symlinks
├── baseline.py         # PATH-based tool checks and auth guidance
├── machine_summary.py  # concise change summary used by the ./setup menu
├── fonts.py            # font plan + execute (Nerd Fonts and apt fallbacks)
├── font_catalog.py     # Nerd Font + apt catalog constants
├── font_context.py     # platform detection (linux/wsl/pi/pixel-terminal/pixel-avf)
├── font_assets.py      # ttyd HTML/service generation for Pixel Terminal
├── font_pixel.py       # Pixel Terminal ttyd plan composition
├── font_records.py     # font summary records and version persistence
├── font_runner.py      # subprocess + http abstraction for tests
└── font_windows.py     # WSL host plan + Windows Terminal settings update

tests/
├── helpers.py
├── test_apply_backups.py
├── test_apply_failures.py
├── test_apply_install.py
├── test_cli_reports.py
├── test_docs.py
├── test_doctor.py
├── test_doctor_reports.py
├── test_doctor_symlinks.py
├── test_fonts.py
├── test_machine_summary.py
├── test_manifest.py
├── test_plan_operations.py
├── test_project_init_backups.py
├── test_project_init_placeholders.py
├── test_project_init_reports.py
├── test_project_init_success.py
├── test_protected_apply.py
├── test_protected_manifest.py
├── test_protected_plan.py
├── test_secrets.py
├── test_setup_script.py
├── test_templates.py
└── test_workflow.py

.github/
└── workflows/
    └── dotfiles-validation.yml
```

**Structure Decision**: Use a root Python package runnable as
`python -m dotfiles_tools` without packaging metadata. This keeps runtime
dependency management simple, allows `uv run python -m dotfiles_tools ...`, and
avoids lock files until a real runtime dependency exists.

## Phase 0: Research

Research decisions are captured in [research.md](./research.md). All planning
unknowns are resolved:

- Runtime dependency policy: standard library only.
- CLI/report format: human-readable by default with stable JSON via `--json`.
- Manifest format: root `dotfiles-manifest.json` with stable entry IDs.
- Apply failure semantics: stop on first failed write and report partial apply.
- Coverage execution: `uv run --with coverage coverage ...`, no runtime lock file.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md): manifest entries, target state, operation plan, backup record, project variables, validation report.
- [contracts/cli.md](./contracts/cli.md): command arguments, exit status, and JSON report contract for `doctor`, `plan`, `apply`, and `init-project`.
- [contracts/manifest.schema.json](./contracts/manifest.schema.json): manifest structure contract.
- [quickstart.md](./quickstart.md): local validation, dry-run, temp-home apply, project-init, coverage, and CI expectations.

## Constitution Check - Post-Design

- **Template Source of Truth**: PASS. Data model and CLI contracts preserve template behavior and symlink checks.
- **Secret-Free and Identity-Safe**: PASS. Secret scanning is represented in the data model, CLI reports, and quickstart validation flow.
- **Protected Files**: PASS. Manifest schema requires IDs and supports protected/manual entries; CLI contract requires exact ID opt-in.
- **Reproducible Bootstrap**: PASS. `doctor`, `plan`, `apply`, backups, partial apply, and idempotence are covered by contracts and quickstart scenarios.
- **Validation Before Coverage**: PASS. Quickstart and plan require tests before coverage upload; CI uploads only when token exists.
- **uv Python Workflow**: PASS. All Python commands in quickstart use `uv`.

Post-design verification on 2026-05-01 confirmed the implementation and Codacy
coverage upload path after PR #69 and PR #70.

## Complexity Tracking

No constitution violations are accepted for this feature.
