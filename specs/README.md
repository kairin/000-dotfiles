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

## Status (2026-05-15)

- `001-dotfiles-bootstrap-validation`: **complete**. All 63 tasks marked `[x]`.
  Specification validated.
- `002-setup-optional-integrations`: **complete**. All 42 tasks marked `[x]`.
- `002-setup-menu-recommendation`: **implementation shipped, task checklist
  stale**. The state-aware menu and the machine-summary recommendation engine
  are live (see `dotfiles_tools/machine_summary.py`), but the 29-task checklist
  in `tasks.md` is still all `[ ]`. Treat the implementation as canonical;
  refresh the checklist before relying on it as a progress signal.

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
