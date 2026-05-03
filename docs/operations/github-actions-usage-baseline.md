# GitHub Actions Usage Baseline

This document records the current GitHub Actions billing baseline for the repo family before moving any heavy work to a local machine or self-hosted runner.

It is intentionally conservative:

- live GitHub billing API data is used for repo-level totals
- downloaded billing CSVs are used only where the API does not expose workflow-level detail
- all figures below were captured before any local-runner migration work

## What The Live API Can Show

The GitHub billing API can return usage by:

- date
- repo
- product / SKU
- minute or request quantity

It does not expose `workflow_path`, so workflow-level attribution still requires the downloaded billing CSV export.

## Current Snapshot

Captured from the live billing API on `2026-05-03` for the available history window:

| Month | Actions minutes | Gross | Net |
|---|---:|---:|---:|
| `2025-11` | `3303.000` | `$26.481` | `$0.000` |
| `2025-12` | `1910.000` | `$15.285` | `$0.000` |
| `2026-01` | `1982.000` | `$11.897` | `$0.000` |
| `2026-02` | `2154.000` | `$14.240` | `$0.000` |
| `2026-03` | `503.000` | `$3.018` | `$0.000` |
| `2026-04` | `1730.000` | `$10.380` | `$0.000` |
| `2026-05` | `803.000` | `$4.818` | `$0.000` |

`2026-05` is partial and reflects the live data available on `2026-05-03`.

## Active Repo Baseline

Totals below exclude archived repositories and are aggregated from the live monthly snapshots.

| Repo | Total minutes |
|---|---:|
| `ghostty-config-files` | `3252.000` |
| `win-qemu` | `2679.000` |
| `002-mcp-manager` | `1601.000` |
| `caption` | `1421.000` |
| `graph-obsidian` | `528.000` |
| `000-dotfiles` | `367.000` |
| `signage-1` | `297.000` |
| `supplier-invoices` | `247.000` |
| `oneTBB` | `247.000` |
| `MetaSpec-Kyocera` | `125.000` |
| `image-tools` | `111.000` |
| `BCM-private` | `96.000` |
| `google-gemini-codes` | `78.000` |
| `civit-download` | `41.000` |
| `civitai` | `33.000` |

## `000-dotfiles` Baseline

This is the repo that matters for the local-runner migration work.

| Date / period | Actions minutes | Notes |
|---|---:|---|
| `2026-04` | `10.000` | Live API monthly snapshot |
| `2026-05-01` | `134.000` | Daily live API snapshot |
| `2026-05-02` | `157.000` | Daily live API snapshot |
| `2026-05-03` | `66.000` | Daily live API snapshot |
| `2026-05` | `357.000` | Monthly live API snapshot |

## Why This Is Useful

After moving work to a local machine or self-hosted runner, the same live billing queries can be rerun and compared directly against this baseline.

That comparison will show:

- whether `000-dotfiles` Actions usage drops
- whether the current split between coverage and Codacy static analysis still makes sense
- whether the remaining GitHub-hosted work is worth keeping

## Refresh Commands

Use the billing token stored in `~/.config/github/billing-token`:

```bash
GH_TOKEN="$(tr -d '\n' < ~/.config/github/billing-token)" gh api /users/kairin/settings/billing/usage?year=2026\&month=5
GH_TOKEN="$(tr -d '\n' < ~/.config/github/billing-token)" gh api /users/kairin/settings/billing/usage?year=2026\&month=5\&day=3
```

For repo-level comparisons, inspect the `repositoryName` field in the JSON output.

