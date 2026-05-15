# Documentation Reconciliation Follow-Ups

**Status:** Phase 2 complete; P1/P2/P3 items remain
**Date:** 2026-05-15 (Phase 1) / 2026-05-16 (Phase 2)
**Context:** PR #244 reconciled the first round of doc drift and was merged with
`./setup ship 244`. The pre-push hook ran 292 unit tests successfully. Before
merge, `gh pr checks` showed the Codacy app checks and `codacy-safety-net` all
passing; `./setup ship` resolved only the currently required GitHub check
(`codacy-safety-net`) and merged the PR.

Branch `20260515-083922-docs-followups` resolved the remaining P0 items and
several P2 items (see "Phase 2 Resolutions" below).

## Phase 1 Resolutions (PR #244)

- **Fish bootstrap contract** (P1): RESOLVED — `env.fish` moved to `conf.d/` for
  auto-load pattern; manifest updated; docs updated.
- **Spec hygiene** (P2): RESOLVED — `specs/002-setup-menu-recommendation/tasks.md`
  reconciled with shipped implementation; `specs/README.md` updated.
- **CHANGELOG.md "four required checks"**: RESOLVED — fixed to dynamic language
  throughout.

## Phase 2 Resolutions (branch 20260515-083922-docs-followups)

- **`./setup ship` contract** (P0): RESOLVED — `ship_upload_sarif` is now wired
  into `cmd_ship` as step 4d (HEAD commit) and 4h (merge-base); `codacy-cli
  analyze` runs before the required-check polling loop; `CODACY_PROJECT_TOKEN`
  is loaded via direnv and documented as a ship prerequisite.
- **Required checks policy** (P0): RESOLVED — `codacy-safety-net` confirmed as
  the only required GitHub check via active ruleset "Protect main" (ID
  16046743). Codacy app checks (Static Code Analysis, Coverage Variation, Diff
  Coverage) documented as advisory throughout; `codacy-rollout.json` updated to
  distinguish required from advisory checks.
- **Doc invariant tests** (P2): RESOLVED — T021 (`fish/env.fish` target is
  `conf.d/`), T022 (`codacy-rollout.json` has `required_checks` field), T025
  (`quality-pipeline.sh` contains no "four required" literal) added to
  `tests/test_docs.py`; `conf.d/env.fish` assertion added to
  `tests/test_apply_install.py`.

## Remaining Items

| Priority | Area | Issue | Status | Next action |
|---|---|---|---|---|
| P1 | Coverage upload semantics | Docs say coverage upload is push-only to avoid duplicate reports, while PRs still show Codacy coverage checks. The relationship between GitHub Actions coverage upload and Codacy app PR checks is easy to misread. | PARTIALLY ADDRESSED — README.md and AGENTS.md updated to distinguish GH Actions upload path from Codacy app advisory checks. | Add a short clarification note (one paragraph) to AGENTS.md or a dedicated doc that explicitly names the two paths and when each check appears. |
| P1 | gstack learning log dependency | Docker-backed gstack setup is documented in `docs/operations/gstack-browser-docker-rollout.md`; the container includes Bun, Codex, Claude, Playwright Chromium, and `browse`. Native host helpers can still fail if they require Bun outside the container. | DEFERRED — native host Bun fallback is out of scope; Docker container handles browser-backed workflows. | No action needed unless native learning capture is explicitly requested. |
| P2 | Human polling command | The ad hoc check polling command used `grep -qv pending`; that can finish too early if any check is no longer pending while another is still pending. | OPEN | Prefer `gh pr checks --watch`, `./setup ship`, or a JSON-based loop that requires every required check to be `SUCCESS`. Replace the grep pattern wherever it appears in docs or scripts. |
| P3 | Historical Codacy docs | Some audit docs intentionally describe old failures, deprecated action behavior, or branch-protection removal. They are useful history but can be confused with current guidance. | ACKNOWLEDGED / LOW PRIORITY | Add "historical" banners or cross-links from old audit files to the current Codacy workflow and branch-protection docs. |

## Suggested Next PR Shape

P0 items are resolved. The next PR should be narrow and focused on the
remaining gaps:

1. **P1 — Coverage upload semantics**: Add one paragraph to `AGENTS.md` (or a
   dedicated `docs/operations/coverage-upload.md`) that explicitly names the two
   paths: (a) GitHub Actions workflow uploads `coverage.xml` on push; (b) the
   Codacy app independently computes diff/variation for PR advisory checks from
   that baseline. These are separate code paths and separate check surfaces.

2. **P2 — Human polling command**: Find every occurrence of the `grep -qv
   pending` pattern in docs and scripts and replace with `gh pr checks --watch`
   or `./setup ship`. Add a note in AGENTS.md discouraging the grep pattern.

3. **P3 — Historical Codacy docs banners**: Add a one-line "Historical — not
   current guidance" callout at the top of audit docs that describe removed
   branch-protection rules or deprecated action behavior.

The gstack native-host Bun dependency remains deferred; the Docker-backed
workflow handles all browser-backed use cases.

## Phase 2 Completion Note

**Date:** 2026-05-16
**Branch:** `20260515-083922-docs-followups`

Shipped in this phase:
- `cmd_ship` in `setup` wired to call `ship_upload_sarif` at steps 4d and 4h,
  making `CODACY_PROJECT_TOKEN` a documented ship prerequisite.
- Required-check policy clarified: ruleset "Protect main" (ID 16046743) requires
  only `codacy-safety-net`; Codacy app checks are advisory.
- Doc invariant tests T021, T022, T025 added to `tests/test_docs.py`.
- `conf.d/env.fish` assertion added to `tests/test_apply_install.py`.
