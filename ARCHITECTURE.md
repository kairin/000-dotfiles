# Architecture — dotfiles

> Hub document. All system-design and convention claims live here.
> Satellite documents (README.md, AGENTS.md, docs/*) link back via anchors
> instead of repeating content. See [Drift Prevention](#drift-prevention) for
> the rule satellites must follow.

Every H2 below carries a `<!-- anchor: kebab-slug -->` comment on the line
immediately following the heading. The HTML comment is invisible to human
readers and is parsed by `tests/test_architecture.py`; the canonical URL
satellites link to is GitHub's auto-derived slug from the heading text.

## Table of Contents
<!-- anchor: toc -->
- [Overview](#overview) — what this repo is and is not
- [System Design](#system-design) — bootstrap, drift detection, safe changes, validation
- [Tool Catalog](#tool-catalog) — the 13 entries in `TOOL_BASELINE`
- [Auth Guidance](#auth-guidance) — tool sign-in (`AUTH_GUIDANCE`) plus project token bridges
- [Protected Files Canonical List](#protected-files-canonical-list) — the 4 files agents must never modify silently
- [MCP Tool Availability](#mcp-tool-availability) — GitHub MCP, Codacy MCP, SessionStart token loader
- [Template Convention](#template-convention) — the `.template` suffix and `{{PLACEHOLDER}}` pattern
- [Symlink Convention](#symlink-convention) — `CLAUDE.md`/`GEMINI.md` → `AGENTS.md`
- [Development Workflow](#development-workflow) — local pipeline, pre-push hook, `./setup ship`
- [Python Module Architecture](#python-module-architecture) — the `dotfiles_tools/` package
- [Docker-based Browser Automation](#docker-based-browser-automation) — `gstack-browser` container
- [Coverage Upload Methods](#coverage-upload-methods) — GitHub Actions baseline, Coverage Reporter, SARIF for analysis
- [Hook Trigger Map](#hook-trigger-map) — Git hook vs CLI tool hooks
- [Drift Prevention](#drift-prevention) — how satellites stay aligned with this hub
- [Design History](#design-history) — completed specs + reconciliation log

---

## Overview
<!-- anchor: overview -->
This repository is a collection of config templates for AI coding tools
(Claude Code, Codex, Gemini CLI, Copilot CLI, gh CLI) plus shell environment
(fish, git, direnv), together with a stdlib-only Python CLI
(`dotfiles_tools/`) and a bash entrypoint (`./setup`) that audit, install,
and apply those templates.

**Goals:**
- Idempotent bootstrap of a developer machine from a single repo.
- Drift detection that distinguishes user-customizable from policy-managed files.
- Project-level AI agent doc scaffolding via `agents/*.template`.

**Non-goals:** This is not a package manager, not a secret store, and not a CI
replacement. Templates with the `.template` suffix are copied and customized
into their target paths; they are never executed or sourced directly from
this repo.

---

## System Design
<!-- anchor: system-design -->
Four sub-flows: bootstrap, drift detection, safe changes, validation.

### Bootstrap
<!-- anchor: bootstrap -->
The 13-entry `TOOL_BASELINE` (`dotfiles_tools/baseline.py:11-289`) declares
every tool that should be present on a developer machine, its `install_method`
(`apt`, `apt_keyring`, `npm`, `uv_tool`, `curl_installer`, `manual`), and any
`post_install` actions. `collect_tool_baseline()` (`baseline.py:360`) detects
which tools are missing and which are present; `render_setup_guidance()`
(`baseline.py:368`) produces the human-readable terminal output the menu uses.
The actual installation is dispatched from bash (`setup` script) for the
options that need `sudo` (`apt`, `apt_keyring`); Python validates state but
does not invoke `sudo` directly.

### Drift detection
<!-- anchor: drift-detection -->
`run_doctor()` (`dotfiles_tools/doctor.py:211`) compares every manifest entry
against its on-disk target. For each entry it computes `expected_text()`
(`dotfiles_tools/templates.py:19`) — the rendered template — and compares it
to the file on disk. Entries marked `user_customizable: true` are never
flagged as drifted regardless of content; entries marked `protected: true`
are also never auto-overwritten. The doctor returns a `Report` whose `extra`
dict carries `auth_guidance` for the menu summary.

### Safe changes
<!-- anchor: safe-changes -->
`./setup` option 2 ("Apply safe dotfiles updates") has a sub-menu that
separates ordinary dotfiles from font installation. Every overwrite is
preceded by a backup written under `$HOME/.dotfiles-backups/` via
`create_backup()` (`dotfiles_tools/backups.py:18`). The `--include-protected`
flag is an explicit opt-in that allows overwriting protected files; without
it the protected files are skipped.

### Validation
<!-- anchor: validation -->
Two read-only audit entry points:

- `./setup verify` (no `uv` required, CI-safe).
- `./setup doctor` and `uv run python -m dotfiles_tools doctor --repo . --home "$HOME"` for full Python-side audit.

```
./setup
  ├─ menu
  │   ├─ option 1  Install missing tools          → bash dispatch + dotfiles_tools.bootstrap
  │   ├─ option 2  Safe dotfiles updates          → dotfiles_tools.installer with backups
  │   ├─ option 3  Audit drift                    → dotfiles_tools.doctor
  │   ├─ option 4  Tool auth sign-ins             → dotfiles_tools.baseline render_setup_guidance
  │   ├─ option 5  Optional integrations          → bash configure_gh_auth / configure_codacy_env / configure_hf_token
  │   ├─ option 6  Project bootstrap              → dotfiles_tools.project_init
  │   └─ option 7  Quit
  └─ direct subcommands (advanced)
      ├─ verify, doctor, plan, apply, init-project, ship, hooks
      └─ codacy-plan, gstack-exec, gstack-setup, gstack-shell, repair-codacy-env, repair-gemini-ripgrep, docker-build
```

---

## Tool Catalog
<!-- anchor: tool-catalog -->
The canonical enumeration of every tool the bootstrap manages. Source of
truth: `TOOL_BASELINE` at `dotfiles_tools/baseline.py:11-289`.

| ID | Command | `install_method` | `requires_sudo` | `post_install` |
|---|---|---|---|---|
| uv | `uv` | manual | no | — |
| git | `git` | apt | yes | guidance |
| gh | `gh` | apt_keyring | yes | guidance |
| docker | `docker` | apt_keyring | yes | auto + guidance |
| fish | `fish` | apt | yes | 3 × auto |
| direnv | `direnv` | apt | yes | — |
| codex | `codex` | npm | no | guidance |
| claude | `claude` | curl_installer | no | guidance |
| gemini | `gemini` | npm | no | guidance |
| copilot | `copilot` | npm | no | guidance |
| specify | `specify` | uv_tool | no | guidance |
| huggingface | `hf` | uv_tool | no | guidance |
| codacy-cli | `codacy-cli` | curl_installer | no | — |

Notes:
- `curl_installer` entries must declare `interpreter` if the script needs
  bash (Ubuntu's default `/bin/sh` is `dash` and rejects bash extensions).
- `post_install` of kind `auto` runs unattended when the user passes `--yes`;
  kind `guidance` only prints the follow-up command.
- Each tool's config template (e.g. `claude/settings.json.template`,
  `codex/config.toml.template`) lives in the same-named directory at the
  repo root; see [Repo layout](README.md#repo-layout) in the satellite.

---

## Auth Guidance
<!-- anchor: auth-guidance -->
Auth coverage has two parts: per-tool sign-in checks (`AUTH_GUIDANCE`) and
project-level token bridges (`.envrc`, Codacy, repair helpers).

### Tool sign-ins
<!-- anchor: auth-tool-signins -->
The 7-entry `AUTH_GUIDANCE` tuple at `dotfiles_tools/baseline.py:311-357`
drives the `[+]/[ ]/[?]` status display in option 4 and the auth context
lines in the menu summary banner.

| ID | Tool | Sign-in command | Verify mechanism |
|---|---|---|---|
| gh | `gh` | `gh auth login` | `gh auth status` (CLI exit code) |
| codex | `codex` | `codex auth` | JSON file `~/.codex/auth.json` (paths `tokens.access_token` + `tokens.refresh_token`) |
| claude | `claude` | `claude login` | `claude auth status` (CLI exit code) |
| gemini | `gemini` | `gemini` | JSON file `~/.gemini/oauth_creds.json` (paths `access_token` + `refresh_token`) |
| copilot | `copilot` | `copilot /login` | interactive-only (no programmatic verify) |
| codacy | `codacy-cli` | `codacy-cli auth` | text file `~/.codacy/account-token` (non-empty) |
| huggingface | `hf` | `hf auth status` | `hf auth status` (CLI exit code) |

State semantics: each entry resolves to one of four states —
`signed_in`, `available` (verifiable but not signed in), `interactive_only`
(no programmatic verify possible), or `tool_missing`. The four-way
partition lives at `_partition_auth_items()` (`baseline.py:405`) for option 4
live display, and at `_partition_auth_guidance()`
(`dotfiles_tools/machine_summary.py:238`) for the menu summary banner.

The `[recommended]` tag on menu option 4 is gated by
`_recommendation_for_auth_guidance()` (`machine_summary.py:132`), which fires
only when at least one verifiable tool is pending sign-in.

### Project Token Bridges
<!-- anchor: token-bridges -->
Distinct from per-tool sign-ins. Two scopes:

- **Machine-level account tokens.** Codacy `~/.codacy/account-token` (text);
  HuggingFace `~/.cache/huggingface/token` (text). These survive across
  projects. The SessionStart hook exports them into agent shells.

- **Project-level tokens via `.envrc.local`.** Per-repo Codacy project
  tokens, GitHub PATs scoped to a specific repo, etc. Created by
  `configure_codacy_env()` (`setup:2097-2278`), repaired by
  `cmd_repair_codacy_env()` (`setup:2280-2383`). The `.envrc` bridge that
  forwards `~/.codacy/account-token` into a project's environment is
  written by `bridge_codacy_account_token()` (`setup:1862-1875`).

**Rules for agents (also in [AGENTS.md](AGENTS.md#local-api-access)):**
1. Do not run `direnv allow`, edit `.envrc`, or source `.envrc.local`
   manually — the SessionStart hook loads them automatically.
2. Do not print token contents (no `cat ~/.codacy/...`, no `echo $CODACY_*`).
3. If a tool returns 401/404, look for `[claude-env]` lines in the
   session-start output; recovery is `./setup repair-codacy-env`.

---

## Protected Files Canonical List
<!-- anchor: protected-files-canonical-list -->
Four files are protected. Agents may read them freely; writing requires an
explicit per-file directive from the user. The full why and the agent-facing
rules live in [AGENTS.md#protected-files](AGENTS.md#protected-files-never-modify-without-explicit-per-file-directive).

- `git/config` — committer identity; silent changes affect every git op.
- `fish/fish_plugins` — manually curated plugin list; additions require
  `fisher update`.
- `.gitignore` — silent edits can leak secrets into git history.
- `agents/CLAUDE.md.template` and `agents/GEMINI.md.template` — these are
  symlinks; rewriting as regular files breaks the single-source pattern.

The bootstrap respects this list via the `protected: true` field in
`dotfiles-manifest.json` entries; opt-in overwrite is the explicit
`--include-protected <id>` flag on `./setup apply`.

---

## MCP Tool Availability
<!-- anchor: mcp-tool-availability -->
Two MCP servers are auto-registered when their tokens are present.

### Token loading via SessionStart hook
<!-- anchor: mcp-token-loading -->
`~/.claude/hooks/load-project-env.sh` runs at every Claude Code session
start. It reads the current project's `.envrc` / `.envrc.local` and exports
an allowlisted set of variables into every Bash tool call for the session.
The allowlist covers: `CODACY_ACCOUNT_TOKEN`, `CODACY_API_TOKEN`,
`CODACY_PROJECT_TOKEN`, `CODACY_USERNAME`, `CODACY_PROJECT_NAME`,
`CODACY_ORGANIZATION_PROVIDER`, `GITHUB_TOKEN`, `GH_TOKEN`, `HF_TOKEN`,
`HUGGINGFACE_TOKEN`. Per-project extras: create `.claude/env-allowlist`
with one variable name per line; the hook merges them into the forwarded
set.

The bash function `ensure_mcp_servers()` at `setup:598-622` registers the
GitHub and Codacy MCP servers with `claude mcp add`. This is bash, not
Python; the function is invoked once at the end of `cmd_apply` via
`setup:1561`.

### GitHub MCP
<!-- anchor: mcp-github -->
Available when `GITHUB_TOKEN` is set (auto-loaded by the SessionStart
hook). Namespace `mcp__github__*`. Prerequisite: `gh auth login` must have
been run; if not, `GITHUB_TOKEN` is empty and all GitHub MCP calls fail
silently. Verify with `gh auth status`. Key tools: `create_issue`,
`list_issues`, `create_pull_request`, `get_pull_request`,
`get_pull_request_status`, `push_files`, `search_code`,
`search_repositories`.

### Codacy MCP
<!-- anchor: mcp-codacy -->
Available when `CODACY_ACCOUNT_TOKEN` is set. The token is a machine-level
account token stored at `~/.codacy/account-token`; a project-level token
(`CODACY_PROJECT_TOKEN`) alone is not enough. Namespace `mcp__codacy__*`.
Key tools: `codacy_list_repository_issues`, `codacy_get_file_coverage`,
`codacy_get_pull_request_files_coverage`, `codacy_cli_analyze`,
`codacy_setup_repository`.

---

## Template Convention
<!-- anchor: template-convention -->
Files ending in `.template` are copy-and-customize. Never source or execute
from this repo. Placeholders follow `{{UPPER_SNAKE_CASE}}` (double-braces,
no spaces) and must all be replaced before the rendered file becomes a
target. `expected_text()` (`templates.py:19`) performs the substitution;
`validate_template()` (`templates.py:25`) checks that no unresolved
placeholders remain and that no secrets pattern leaks through (delegates
to `dotfiles_tools/secrets.py`).

Edge case: the literal `{ {UPPER_SNAKE_CASE} }` form (with spaces) appears
inside `AGENTS.md.template` to avoid false-positive matching during the
template's own self-documentation. See `CHANGELOG.md` entry under
"Template self-documentation guard".

---

## Symlink Convention
<!-- anchor: symlink-convention -->
Two scopes, four symlinks:

| Symlink | Target | Scope |
|---|---|---|
| `CLAUDE.md` | `AGENTS.md` | repo root — Claude Code auto-loads this |
| `GEMINI.md` | `AGENTS.md` | repo root — Gemini CLI auto-loads this |
| `agents/CLAUDE.md.template` | `agents/AGENTS.md.template` | project scaffold |
| `agents/GEMINI.md.template` | `agents/AGENTS.md.template` | project scaffold |

Verify with `ls -la CLAUDE.md GEMINI.md` — both should print
`-> AGENTS.md`. These MUST remain symlinks; rewriting either as a regular
file breaks the single-source pattern and is enforced by the
[Protected Files](#protected-files-canonical-list) list.

---

## Development Workflow
<!-- anchor: development-workflow -->
Three layers: local commands, the pre-push hook, and `./setup ship`.

### Local commands
<!-- anchor: dev-local -->
```bash
git status
git diff
git add <specific files>          # never -A
git commit -m "..."

# Validation (read-only)
uv run python -m dotfiles_tools doctor --repo . --home "$HOME"
uv run python -m dotfiles_tools plan  --repo . --home "$HOME" --profile machine

# Apply (writes; backs up first)
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine \
  --backup-dir "$HOME/.dotfiles-backups" --yes

# Per-project scaffolding
uv run python -m dotfiles_tools init-project \
  --repo . --project /path/to/project --vars project-vars.json --yes

# Tests + coverage
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
```

### Pre-push hook
<!-- anchor: pre-push -->
Installed via `./setup hooks` or `./scripts/install-hooks.sh`. Runs on
every `git push` regardless of which CLI initiated the push. Four steps,
all in `scripts/hooks/pre-push:1-142`:

| # | Step | Lines | Behavior |
|---|---|---|---|
| 0 | Protected-branch guard | 22-36 | Hard refusal to push `refs/heads/main` |
| 1 | Unit tests | 38-61 | `uv run python -m unittest discover -s tests`; BLOCKING |
| 2 | Complexity check | 63-79 | radon CC ≤ 5 on modified `dotfiles_tools/*.py` |
| 3 | Type annotations | 82-105 | warning only |
| 4 | Line length | 107-140 | warning only |

**The pre-push hook does NOT upload coverage or SARIF.** Coverage upload
and analysis are handled separately by `scripts/quality-pipeline.sh` (static
analysis via codacy-cli) and `./setup ship` (coverage via Codacy Coverage Reporter).

### Local quality pipeline
<!-- anchor: quality-pipeline -->
`scripts/quality-pipeline.sh` is the developer-side static-analysis helper
(distinct from the pre-push hook). 7 stages, documented in the script
header:

1. Unit tests
2. Coverage XML
3. Pylint analysis → SARIF (for code-quality checks)
4. Coverage upload to Codacy (via Coverage Reporter)
5. SARIF upload to Codacy (static-analysis for HEAD)
6. SARIF upload to Codacy (merge-base — so PR diff has a baseline for analysis)
7. Codacy server-side gate (informational)

Modes: default runs stages 1–7; `--codacy-only` runs only 3, 5, 6, 7.
Exit codes: 0 pass, 1 stage failed, 3 prerequisite missing (PATH or env).

**Note:** Stage 4 (coverage upload) is supplementary. The required baseline
is established by the GitHub Actions workflow (Path A). Stage 3, 5, 6 handle
static-analysis SARIF, which is separate from coverage metrics.

### `./setup ship`
<!-- anchor: ship -->
Canonical merge path. Defined at `cmd_ship()` (`setup:1195`). Requires an
authenticated `gh` and `CODACY_PROJECT_TOKEN` exported (auto-loaded by
direnv).

Flow:

1. Verify on a feature branch (refuse on `main`).
2. Resolve PR number (argument or from current branch).
3. If `gh pr view --json mergeStateStatus` returns `BEHIND`, run
   `gh pr update-branch`.
4. Step 4d: upload coverage via Codacy Coverage Reporter (when
   `CODACY_PROJECT_TOKEN` and `coverage.xml` are present). This uses
   `bash <(curl -Ls https://coverage.codacy.com/get.sh)` to submit the
   local coverage report for diff-coverage computation. If the upload fails
   (e.g., token missing), the step logs a warning but does not block; the
   required baseline is still established by the GitHub Actions workflow.
5. Poll all four required checks: `codacy-safety-net` (GitHub Actions),
   plus the three Codacy app checks `Codacy Static Code Analysis`,
   `Codacy Coverage Variation`, `Codacy Diff Coverage`. The required set
   is resolved dynamically from branch protection or rulesets via the
   GitHub API; poll until each reports `success`.
6. Squash-merge when `mergeStateStatus` is `CLEAN` or `UNSTABLE`. When
   it is `BLOCKED` after all required checks pass, add `--admin` to
   bypass the remaining gate (`setup:1374-1393`). The code does not
   introspect the BLOCKED reason; in practice this gate is the missing
   PR-review requirement on solo-author PRs, but the design treats any
   post-checks BLOCKED state as eligible for admin bypass.

---

## Python Module Architecture
<!-- anchor: python-module-architecture -->
Stdlib only — no runtime dependencies. Validation tooling is `uv`-managed
(`uv run python -m unittest discover -s tests`), but the `dotfiles_tools/`
package itself never imports anything outside the standard library.

| Module | Purpose | Key API |
|---|---|---|
| `__main__.py` | CLI entry point | `python -m dotfiles_tools <subcommand>` |
| `cli.py` | Subcommand dispatcher | `main()`, argparse |
| `manifest.py` | Manifest loading & validation | `load_manifest`, `ManifestEntry`, `validate_included_protected`, `resolve_source`, `resolve_target` |
| `baseline.py` | Tool & auth baseline | `TOOL_BASELINE`, `AUTH_GUIDANCE`, `collect_tool_baseline` (line 360), `render_setup_guidance` (line 368) |
| `doctor.py` | Drift audit | `run_doctor` (line 211) returning `Report` |
| `tool_installer.py` | Per-method install executors | `_install_apt`, `_install_npm`, `_install_curl`, `_install_uv_tool` |
| `installer.py` | Config file copier with backup | dispatches to `backups.py` |
| `backups.py` | Backup before overwrite | `backup_path_for` (line 12), `create_backup` (line 18) |
| `templates.py` | Template rendering & validation | `expected_text` (line 19), `validate_template` (line 25) |
| `placeholders.py` | Placeholder regex | matches `{{UPPER_SNAKE_CASE}}` |
| `project_init.py` | Per-project scaffolding | `init_project` |
| `machine_summary.py` | Menu state summary + recommendations | `render_machine_summary` (line 23), `_recommendation_for_auth_guidance` (line 132), `_partition_auth_guidance` (line 238) |
| `bootstrap.py` | Tool bootstrap orchestration | `run_bootstrap` |
| `fonts.py` + `font_*` | Font catalog & install | one module per OS concern |
| `codacy_rollout.py` | Reads `codacy-rollout.json` | used by `codacy-plan` subcommand |
| `reports.py` | Output formatters | JSON + text renderers |
| `secrets.py` | Secret-pattern guards | used by `validate_template` |

Architectural invariants:
- Stdlib only — no runtime deps; tests run via `python -m unittest`, not pytest.
- Python never invokes `sudo`; tasks that need root are dispatched by
  `setup` (bash) which Python advises but does not call.
- `_recommendation_for_*` helpers feed the menu's `[recommended]` tag
  without mutating state.

MCP server registration is a bash concern and lives in
`ensure_mcp_servers()` at `setup:598-622`, not in `dotfiles_tools/`. The
Python side validates token presence; the bash side runs `claude mcp add`.

---

## Docker-based Browser Automation
<!-- anchor: docker-based-browser-automation -->
Playwright lacks prebuilt Chromium binaries for Ubuntu 26.04
(`microsoft/playwright#40117`). To unblock gstack browser skills (`/qa`,
`/browse`, `/qa-only`) on Ubuntu 26.04 hosts, this repo ships an
Ubuntu 24.04 Docker container.

### Daily commands
<!-- anchor: docker-daily -->
```bash
./setup                              # installs docker via TOOL_BASELINE (apt_keyring)
./setup docker-build                 # builds gstack-browser:latest (~5 min first time)
./setup gstack-setup /home/kkk/Apps/gstack
./setup gstack-codex   /home/kkk/Apps/gstack
./setup gstack-shell                 # enters a shell inside the running container
./setup gstack-exec -- <command>     # runs <command> inside the container
```

### Container settings
<!-- anchor: docker-settings -->
Nine load-bearing settings live in `docker/gstack-browser/docker-compose.yml`:

1. `shm_size: "2gb"` — required for Chromium stability (default 64 MB causes renderer crashes).
2. `GSTACK_CONTAINER=1` — env var; wrapper commands use this to detect container context.
3. `HOME`, `USER`, `LOGNAME` — set to match host user so tool state resolves correctly.
4. `~/.gitconfig` mounted read-only — prevents container from modifying host git identity.
5. Bind mounts: `~/Apps`, `~/.codex`, `~/.claude`, `~/.gstack`, `~/.config/gh` at identical paths.
6. UID 1000 alignment — the Playwright base image's `ubuntu` user is remapped to host UID/GID.
7. Path-preservation invariant — container paths match host paths exactly (`/home/$USER/...`).
   Do not change container `HOME` or mount paths; skill files reference absolute paths.
8. `.env` regenerated per run from direnv allowlist (file is gitignored).
9. Tokens forwarded: `GITHUB_TOKEN`, `CODACY_*`, `HF_*`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_*`.

### Verified state
<!-- anchor: docker-verified -->
As of 2026-05-17: Docker Engine 29.5.0 works without host `sudo` after
`newgrp docker`; `gstack-browser:latest` builds; `gstack-dev` runs;
`./setup gstack-setup` completed inside the container; Codex CLI 0.130.0,
passwordless sudo, Playwright Chromium, and the `browse` binary at
`/home/kkk/Apps/gstack/browse/dist/browse` are available. The container
mounts at identical paths so absolute paths inside gstack skill files keep
working without translation.

When Playwright issue #40117 is resolved, the Docker workflow becomes
optional — host browser skills will work natively again.

Files: `docker/gstack-browser/Dockerfile`,
`docker/gstack-browser/docker-compose.yml`,
`docker/gstack-browser/README.md` (humans-only operational overview).

---

## Coverage Upload Methods
<!-- anchor: coverage-upload-methods -->
Coverage reporting reaches Codacy via complementary paths; static analysis
uses separate SARIF-based workflows. Understanding the distinction prevents
misattribution of what drives required checks.

### Path A — GitHub Actions baseline
<!-- anchor: coverage-path-a -->
`.github/workflows/codacy-safety-net.yml` runs on every push and PR:

```yaml
- name: Run unit tests with coverage
  run: uv run --with coverage==7.5.4 coverage run -m unittest discover -s tests

- name: Generate coverage XML
  run: uv run --with coverage==7.5.4 coverage xml

- name: Upload coverage to Codacy
  run: bash <(curl -Ls https://coverage.codacy.com/get.sh) report \
    --api-token "$CODACY_ACCOUNT_TOKEN" \
    -r coverage.xml
```

This produces the `codacy-safety-net` required check and establishes the
baseline for Codacy server-side diff calculations. **This is the required,
authoritative coverage baseline.**

### Path B — Codacy server-side diff
<!-- anchor: coverage-path-b -->
The Codacy app independently computes:
- Diff coverage (lines changed that lack coverage)
- Coverage variation (increase/decrease vs baseline)

These power the `Codacy Diff Coverage` and `Codacy Coverage Variation`
required checks. No local upload needed; the server calculates from Path A.

### Supplementary — Local coverage upload via `./setup ship` (optional)
<!-- anchor: coverage-supplementary -->
When `CODACY_PROJECT_TOKEN` and `coverage.xml` exist, step 4d uploads via
Codacy Coverage Reporter:

```bash
bash <(curl -Ls https://coverage.codacy.com/get.sh) report \
  --api-token "$CODACY_PROJECT_TOKEN" \
  -r coverage.xml
```

This allows the Codacy server to recompute diff metrics with fresh data
before the PR checks run. If this step fails (e.g., token missing), the
workflow's Path A baseline still provides all required checks—the local
upload is supplementary only.

### Static analysis — Separate from coverage
<!-- anchor: static-analysis-separate -->
`scripts/quality-pipeline.sh` stages 3, 5, 6 use `codacy-cli analyze
--tool pylint --format sarif` to generate SARIF for code-quality checks.
The `.codacy/codacy.yaml` config is ephemeral (Pattern A: created, used,
deleted in one invocation). This is **not** a coverage mechanism; SARIF
uploads are independent of the coverage baseline.

Known non-fatal messages when running codacy-cli: `tools//patterns failed
with status 404` (codacy-cli bug, ignorable), `"Repository Analysis" is
disabled` (Codacy server notice; `200 OK` on upload = SARIF accepted).
Neither blocks required checks on the PR.

See `~/.claude/skills/codacy/SKILL.md` for procedures and the runbooks at
`docs/codacy-handling-*.md` for command transcripts.

---

## Hook Trigger Map
<!-- anchor: hook-trigger-map -->
Use these layers precisely: tool instructions are Markdown context files,
tool hooks are CLI-specific session/tool hooks, and the repo hook is the
Git hook that runs for any caller.

| CLI | What it auto-loads | Tool-specific hooks | Pushes to `main` |
|---|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md`, project `CLAUDE.md` | `/hooks` slash command; `SessionStart` (`load-project-env.sh`) | blocked by `.git/hooks/pre-push` |
| Gemini CLI | `~/.gemini/GEMINI.md`, project `GEMINI.md` | `gemini hooks --help`; do **not** run `gemini hooks migrate` | blocked by `.git/hooks/pre-push` |
| Codex CLI | `~/.codex/AGENTS.md`, project `AGENTS.md` | (no Codex hook surface used in this repo) | blocked by `.git/hooks/pre-push` |
| Copilot CLI | `~/.copilot/copilot-instructions.md`, `COPILOT_CUSTOM_INSTRUCTIONS_DIRS` | `/instructions`, `/env` | blocked by `.git/hooks/pre-push` |

Install the Git hook in each repo with `./setup hooks` or
`./scripts/install-hooks.sh`. Git triggers `.git/hooks/pre-push`
automatically on every push, regardless of which CLI initiated it. The
hook itself lives at `scripts/hooks/pre-push:1-142`; the protected-branch
guard is at lines 22-36.

---

## Drift Prevention
<!-- anchor: drift-prevention -->
Three layers keep satellites aligned with this hub.

### Layer 1 — Convention comments (zero-cost)
<!-- anchor: drift-comments -->
Every H2 in `ARCHITECTURE.md` carries a same-line `<!-- anchor: slug -->`
comment. Satellites that mirror a hub concept carry a
`<!-- mirrors: ARCHITECTURE.md#slug -->` comment near the mirrored content,
so a doc-test can find both ends of the relationship.

### Layer 2 — Doc owner map + tests
<!-- anchor: drift-owner-map -->
`dotfiles_tools/doc_owners.py` is a data file enumerating
`(canonical_anchor, owning_file, mirror_files)` tuples. Tests assert:

- `tests/test_architecture.py::test_every_h2_has_anchor_comment` —
  every H2 in `ARCHITECTURE.md` ends with a `<!-- anchor: ... -->` comment
  on the same line.
- `tests/test_architecture.py::test_mirror_comments_resolve` — every
  `<!-- mirrors: ARCHITECTURE.md#x -->` in a satellite has a matching
  `<!-- anchor: x -->` in the hub.
- `tests/test_docs.py::test_architecture_anchors_present` — extends the
  existing load-bearing test file with a sentinel that catches deletion
  of the new `tests/test_architecture.py` (it is harder for a future
  contributor to remove the assertion when it lives alongside other
  doc-content assertions).

Pre-push hook step 1 runs `unittest discover` (`scripts/hooks/pre-push:38-61`),
so the new tests block any push that breaks drift contracts.

### Layer 3 — Doctor-style validation (optional)
<!-- anchor: drift-doctor -->
Future work: extend `dotfiles_tools/doctor.py` with a `--check-docs`
flag that scans for broken intra-document anchor links and stale
`<!-- mirrors: -->` references. Deferred to a follow-up; not required
for the initial hub-and-spoke landing.

---

## Design History
<!-- anchor: design-history -->
Three completed Spec Kit specs and one documentation reconciliation
record. Full task lists stay in `specs/` and `docs/issues/`; this section
points to them and summarizes the outcome.

- **001 — Bootstrap & Validation** (2026-04, complete; 63/63 tasks).
  Manifest + `doctor`/`plan`/`apply` CLI surface. Canonical implementation:
  `dotfiles_tools/`. See `specs/001-dotfiles-bootstrap-validation/spec.md`.

- **002 — Setup Menu Recommendation** (2026-04 → 2026-05, code-canonical,
  `tasks.md` stale). The state-aware `[recommended]` tag on menu options.
  Canonical implementation: `dotfiles_tools/machine_summary.py`
  (`render_machine_summary` at line 23). The `tasks.md` checklist is stale
  and intentionally not maintained.

- **002 — Optional Integrations** (2026-05, complete; 42/42 tasks).
  GitHub / HuggingFace / Codacy optional integrations menu. See
  `specs/002-setup-optional-integrations/spec.md`.

- **Documentation reconciliation Phase 1–3** (2026-05-15 → 2026-05-16,
  PR #244 and PR #254). Established "all four Codacy checks required" as
  the canonical rule and restored it after a Phase 3 reversal. The
  reconciliation log lives at `docs/issues/docs-reconciliation-followups.md`
  with its existing historical banner.

Historical investigation logs (`docs/issues/codacy-*.md`,
`docs/issues/branch-protection-history.md`, `docs/issues/menu-renumbering.md`,
`docs/issues/dnsutils-alias.md`, `docs/issues/keybinding-issues.md`,
`docs/issues/speckit-installation.md`) carry per-file banners marking them
as historical. They are kept under `docs/issues/` for audit-trail value;
they are not current guidance.

---

<!-- canonical: ARCHITECTURE.md -->
**Last updated:** 2026-05-17. Update this footer when a section's anchor
slug or owner changes.
