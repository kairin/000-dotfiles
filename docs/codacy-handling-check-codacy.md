# Codacy Handling: Check Codacy

This file records the local investigation into Codacy status and branch protection for `kairin/000-dotfiles`.

## Summary

- `main` and `origin/main` were synchronized at `2d2f8836e5dbed2a3a02758fac3f94b629afe876`.
- There were no open PRs for the merged feature branch.
- GitHub reported no classic branch protection on `main` at first, but a repository ruleset existed.
- The active ruleset originally required only `codacy-safety-net`.
- The rollout doc expected full Codacy protection:
  - `Codacy Static Code Analysis`
  - `Codacy Coverage Variation`
  - `Codacy Diff Coverage`
  - strict checks
  - classic protection plus a matching ruleset

## What Was Implemented

- Real validation/setup code in `dotfiles_tools/`.
- `dotfiles-manifest.json` as the source of truth.
- A `.github/workflows/dotfiles-validation.yml` workflow that runs tests and uploads `coverage.xml`.
- Local Codacy setup support in `./setup`.
- Codacy coverage checks on PRs.

## Outstanding Gap (historical, superseded 2026-05-16)

The repo was not fully protected by the rollout definition until the branch
protection and ruleset were updated to require every Codacy gate. The original
gap described "the three Codacy contexts"; PR #254 (2026-05-16) extended the
required set to four — see "Final Live State" below.

## Final Live State (2026-05-16, PR #254)

- Classic branch protection on `main` requires all four required gates:
  - `codacy-safety-net` (GitHub Actions workflow, app_id `15368`)
  - `Codacy Static Code Analysis` (Codacy app, app_id `56611`)
  - `Codacy Coverage Variation` (Codacy app, app_id `56611`)
  - `Codacy Diff Coverage` (Codacy app, app_id `56611`)
- Ruleset `Protect main` (id `16046743`) requires the same four contexts with
  `strict_required_status_checks_policy: true`.
- `./setup ship` resolves the required set dynamically from the GitHub API and
  polls every check to green before squash-merging. When `mergeStateStatus` is
  `BLOCKED` solely because of the solo-reviewer requirement, ship uses the
  canonical admin-bypass path (`gh pr merge --admin` invoked by `./setup ship`,
  not by hand).

