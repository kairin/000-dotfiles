# specs/ — Design documentation

This folder contains the complete design specification, implementation plan, and
task tracking for the initial **dotfiles-bootstrap-validation** project.

## What's here?

The folder `001-dotfiles-bootstrap-validation/` contains:

- **spec.md** — Full feature specification with user stories (US1–US5), acceptance scenarios, functional requirements (FR-001–FR-024), and success criteria
- **plan.md** — Implementation plan with architectural decisions, module inventory, and phase summaries
- **tasks.md** — Complete task list (63 tasks across 8 phases) with dependency tracking
- **data-model.md** — Formal definitions of Manifest, Entry, Operation, Report, and other core data structures
- **research.md** — Key architectural decisions with rationale and alternatives considered
- **quickstart.md** — Local validation guide covering unit tests, doctor, plan, apply, and end-to-end flows
- **contracts/** — Formal contracts for the CLI and manifest format (JSON Schema, command reference)
- **checklists/** — Specification quality gates (completed ✓)

## Status

**Implementation complete.** All 63 tasks marked `[x]`. Specification validated.
Date: 2026-05-01.

## How to use this folder

**For developers working on the repo:**
- Read `spec.md` to understand the original requirements and acceptance criteria
- Consult `plan.md` for architectural context (why certain decisions were made)
- Check `contracts/` for formal API and data format definitions

**For users:** You don't need to read this folder. Start with [CHANGELOG.md](../CHANGELOG.md)
for what was built and [docs/getting-started.md](../docs/getting-started.md) for how to use it.

**For future implementations:**
- These specs document the design of the **initial release** (v0.1.x)
- Use `tasks.md` and the completed task tracking as a reference for similar projects
- `research.md` explains the architectural decisions; consider them before deviating

## See also

- [CHANGELOG.md](../CHANGELOG.md) — User-visible version history and feature summary
- [docs/getting-started.md](../docs/getting-started.md) — First-time setup guide for new users
