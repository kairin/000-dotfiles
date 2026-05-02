# Implementation Plan: Optional Setup Integrations Menu

**Branch**: `20260504-setup-optional-integrations` | **Date**: 2026-05-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-setup-optional-integrations/spec.md`

## Summary

Move non-critical project integrations behind a secondary project setup submenu while preserving `./setup` as the single entrypoint. Codacy API management becomes one option inside that submenu and keeps the existing safe token behavior: repository tokens expose `CODACY_PROJECT_TOKEN`, account tokens expose `CODACY_API_TOKEN` plus repository metadata, token values stay outside the repository, project files contain only environment bridges and agent-readable guidance, and writes require preview, final confirmation, and backups for existing environment files.

## Technical Context

**Language/Version**: Bash entrypoint plus Python 3 standard-library validation tooling  
**Primary Dependencies**: Existing `uv` developer workflow, shell utilities already used by `setup`, optional user-side `direnv` activation  
**Storage**: Project `.envrc`, project `.envrc.local`, and user-private `~/.codacy/` token files; no tracked secret storage  
**Testing**: `bash -n setup`; `uv run python -m unittest tests.test_setup_script tests.test_docs tests.test_project_init_success`; `uv run python -m unittest discover -s tests`  
**Target Platform**: Developer machine shell workflow, primarily Linux/WSL-compatible project setup  
**Project Type**: Dotfiles/bootstrap CLI with interactive project setup menus  
**Performance Goals**: Optional submenu opens immediately and Codacy setup completes in under 3 minutes after the user has a token  
**Constraints**: No token values in tracked files, command output, generated docs, or tests; preserve core project setup choices; preview and confirm before Codacy writes; back up existing environment files before mutation; no new runtime dependencies or lock files  
**Scale/Scope**: One nested optional integrations submenu, with Codacy API management as the first optional integration and room for future non-critical project integrations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Template Source of Truth**: PASS. The design updates generated project guidance through `agents/AGENTS.md.template` while preserving CLAUDE/GEMINI symlink conventions and never treating templates as live configuration.
- **Secret-Free and Identity-Safe**: PASS. Token values remain outside the repository, setup output must not print tokens, and tracked files only describe variable names and safe loading patterns.
- **Protected Files**: PASS. The planned work does not require `git/config`, `fish/fish_plugins`, `.gitignore`, `agents/CLAUDE.md.template`, or `agents/GEMINI.md.template`.
- **Reproducible Bootstrap**: PASS. The feature affects interactive project setup only; writes require explicit user menu choice plus final confirmation, preview/no-write behavior must be available, existing environment files are backed up before mutation, and managed Codacy sections must be idempotent.
- **Validation Before Coverage**: PASS. Setup-script, docs, and project-init tests will validate behavior before any coverage upload concerns.
- **uv Python Workflow**: PASS. Python validation continues through `uv run python -m unittest`; no runtime dependency is added.

## Project Structure

### Documentation (this feature)

```text
specs/002-setup-optional-integrations/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── codacy-environment.md
│   └── project-setup-menu.md
└── tasks.md
```

### Source Code (repository root)

```text
setup
agents/
└── AGENTS.md.template
fish/
└── env.fish.template
docs/
├── codacy-coverage-rollout.md
└── getting-started.md
tests/
├── test_setup_script.py
├── test_docs.py
└── test_project_init_success.py
```

**Structure Decision**: Keep the change in the existing shell entrypoint and documentation/test surfaces. No new package, module, dependency, or machine manifest entry is needed because this is a project-menu interaction and local environment handoff, not a machine bootstrap target. A small in-script optional-integration registry is acceptable for this feature because optional integrations are secondary project actions; it must remain idempotent, previewable, explicitly confirmed before writes, backed up when mutating existing project files, and covered by tests.

## Phase 0: Research

Research completed in [research.md](./research.md). Decisions cover submenu placement, Codacy credential modes, local secret storage, environment bridge behavior, cancellation/idempotency, and validation scope.

## Phase 1: Design

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/project-setup-menu.md](./contracts/project-setup-menu.md)
- [contracts/codacy-environment.md](./contracts/codacy-environment.md)
- [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

- **Template Source of Truth**: PASS. Contracted generated guidance remains sourced from `agents/AGENTS.md.template`; symlinked template files are not touched.
- **Secret-Free and Identity-Safe**: PASS. Contracts explicitly forbid token values in project files, generated docs, output, and tests.
- **Protected Files**: PASS. Protected files remain outside the write scope.
- **Reproducible Bootstrap**: PASS. Menu contracts specify explicit choices, preview/no-write behavior, final confirmation, backup expectations, cancel behavior, and idempotent managed-section replacement.
- **Validation Before Coverage**: PASS. Quickstart and tasks-ready validation include targeted setup/docs tests plus full suite.
- **uv Python Workflow**: PASS. Validation commands use `uv`; no new dependency or lock file is planned.

## Complexity Tracking

No constitution violations.
