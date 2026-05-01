# Research: Dotfiles Bootstrap Validation

## Decision: Runtime code uses Python standard library only

**Rationale**: The repository needs safe local tooling that works on new machines
with minimal setup. The standard library provides argparse, json, pathlib,
shutil, hashlib, unittest, tempfile, tomllib, and filecmp functionality needed
for manifest loading, planning, applying, parsing, and tests.

**Alternatives considered**:
- Add a CLI framework: rejected because it creates a runtime dependency and lock
  file pressure before the CLI surface is complex enough to need it.
- Add JSON schema validation dependency: rejected for first increment; manifest
  validation is small and can be explicit in code while publishing a schema
  contract for humans and future tooling.

## Decision: Use `uv` for Python command execution and dependency-backed coverage

**Rationale**: The constitution requires `uv` for Python-related workflows. Tests
can run with `uv run python -m unittest discover -s tests`. Coverage can use
`uv run --with coverage coverage run -m unittest discover -s tests` and
`uv run --with coverage coverage xml`, which avoids runtime dependency changes.

**Alternatives considered**:
- `python3 -m unittest` directly: rejected because it bypasses the repo-level
  uv workflow rule.
- Add `coverage` as a runtime dependency: rejected because coverage is
  measurement tooling, not runtime functionality.

## Decision: Manifest lives at `dotfiles-manifest.json`

**Rationale**: A root JSON manifest is easy to inspect, parse with the standard
library, review in diffs, and use as the source of truth for README examples,
doctor checks, plan/apply operations, and protected/manual behavior.

**Alternatives considered**:
- Derive targets from README copy commands: rejected because documentation is
  not a stable machine-readable source of truth.
- Python manifest module: rejected because data should remain inspectable and
  editable without executing repository code.

## Decision: Manifest entries use stable unique IDs

**Rationale**: Protected target opt-in must be explicit and machine-independent.
Stable IDs such as `git.config` and `fish.plugins` are safer than expanded home
paths and easier to test than free-form source-path matching.

**Alternatives considered**:
- Opt in by destination path: rejected because target paths vary by machine and
  are easier to mistype.
- Opt in by repository source path: rejected because source paths can be
  refactored and do not clearly express install intent.

## Decision: Reports are human-readable by default with stable JSON via `--json`

**Rationale**: The tool is used interactively by a maintainer, but tests,
automation, and CI need stable fields instead of scraping prose. Each command
should generate the same report model and render it in human or JSON form.

**Alternatives considered**:
- Human-only output: rejected because it makes reliable tests and downstream
  automation brittle.
- JSON-only output: rejected because the default user path should be readable
  during manual bootstrap and drift review.

## Decision: Apply stops on first failed write and reports partial apply

**Rationale**: Automatic rollback of dotfile writes can create more risk than it
removes, especially when files may already have been backed up or externally
modified. A conservative stop preserves completed changes and backups while
making failure state explicit.

**Alternatives considered**:
- Roll back all completed writes: rejected because rollback can damage local
  customizations and complicate failure handling.
- Continue all remaining writes: rejected because later operations may depend on
  earlier directory or file state and would make recovery harder.

## Decision: CI uploads coverage only after generating `coverage.xml`

**Rationale**: Codacy expects a supported report. The workflow should first run
real validation tests, then generate `coverage.xml`, and only upload when the
token is configured so fork or local runs do not fail.

**Alternatives considered**:
- Enable coverage gates immediately: rejected until at least one PR shows a
  successful coverage upload and Codacy emits the expected checks.
- Upload without token gating: rejected because missing secrets should not fail
  validation-only runs.
