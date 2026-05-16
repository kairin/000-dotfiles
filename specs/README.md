# specs/ — Design documentation

This folder contains the complete design specifications, implementation plans, and
task tracking for the dotfiles project. Three specs live here:

- `001-dotfiles-bootstrap-validation/` — the initial bootstrap, manifest, and
  doctor/plan/apply CLI surface (v0.1.x).
- `002-setup-menu-recommendation/` — state-aware setup menu with `[recommended]`
  tagging and the machine-summary engine.
- `002-setup-optional-integrations/` — GitHub / HuggingFace / Codacy optional
  integration management surfaced through the setup menu and `dotfiles_tools`.

## What's in each spec folder?

Each `00N-*/` folder follows the same Spec Kit layout:

- **spec.md** — Full specification with user stories, acceptance scenarios, functional
  requirements, and success criteria
- **plan.md** — Implementation plan with architectural decisions, module inventory, phase
  summaries
- **tasks.md** — Task list with dependency tracking and checkbox status
- **data-model.md** — Formal definitions of core data structures
- **research.md** — Key architectural decisions with rationale and alternatives considered
- **quickstart.md** — Validation guide covering unit tests, doctor, plan, apply flows
- **contracts/** — Formal contracts for the CLI and manifest format (JSON Schema)
- **checklists/** — Specification quality gates

## Status (2026-05-17)

- `001-dotfiles-bootstrap-validation`: complete (63/63 tasks).
- `002-setup-optional-integrations`: complete (42/42 tasks).
- `002-setup-menu-recommendation`: code-canonical, `tasks.md` stale —
  see the SUPERSEDED-BY-CODE banner at the top of that spec's `spec.md`.

Consolidated design history: [../ARCHITECTURE.md#design-history](../ARCHITECTURE.md#design-history).

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
