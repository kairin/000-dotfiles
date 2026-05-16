# dotfiles — AI Agent Guidelines

Single source of truth for LLM agents. `CLAUDE.md` and `GEMINI.md` symlink to this file.

For human-facing setup instructions (quick start, scenarios, command reference), see `README.md`. For deep system-design and convention claims, see [ARCHITECTURE.md](ARCHITECTURE.md). This file focuses on the conventions agents must respect.

## What this repo is <!-- anchor: what-this-repo-is -->

A collection of config templates for AI coding tools (Claude Code, Codex, Gemini CLI, gh CLI) and shell environment (fish, git), plus a small Python CLI (`dotfiles_tools`) and a bash entrypoint (`./setup`) that audit and apply those templates. Every file with a `.template` suffix is meant to be copied to its target path and customized — it is never executed or sourced directly from here.

## Protected Files — NEVER Modify Without Explicit Per-File Directive <!-- anchor: protected-files -->

<!-- mirrors: ARCHITECTURE.md#protected-files-canonical-list -->

| File | Why protected |
|---|---|
| `git/config` | Contains committer identity; silent changes affect all git operations. |
| `fish/fish_plugins` | Plugin list is manually curated; additions require a `fisher update` run. |
| `.gitignore` | Changing exclusion rules can accidentally expose secrets to git history. |
| `agents/CLAUDE.md.template`, `agents/GEMINI.md.template` | These are symlinks — rewriting them as regular files breaks the single-source pattern. |

**Rules:**
- Read any file freely for context. Do not write without explicit instruction.
- If a task seems to require touching a protected file, stop and ask.
- `git show origin/main:<file>` is the authoritative original.

## Key paths <!-- anchor: key-paths -->

```
agents/                       Project-level agent doc templates (AGENTS.md, CLAUDE.md, GEMINI.md, copilot-instructions.md)
claude/                       ~/.claude/ templates (settings.json, keybindings.json, CLAUDE.md)
codex/                        ~/.codex/ templates (config.toml, rules/default.rules)
gemini/                       ~/.gemini/ templates (settings.json, GEMINI.md)
copilot/                      GitHub Copilot CLI template (copilot-instructions.md.template)
gh/                           ~/.config/gh/ templates (config.yml)
fish/                         ~/.config/fish/ templates and live files (fish_plugins, conf.d/direnv.fish, conf.d/env.fish)
git/                          ~/.config/git/ live files (config)
dotfiles_tools/               Python validation/setup CLI (stdlib only)
scripts/                      Helper shell scripts (install-hooks.sh, quality-pipeline.sh, push-with-pr.sh, hooks/)
tests/                        unittest suite (uv-managed)
specs/                        Spec Kit feature specs (001-bootstrap-validation, 002-menu-recommendation, 002-optional-integrations)
docs/                         Operational docs (e.g. Codacy coverage rollout)
docker/                       Dockerfiles and compose configs (gstack-browser/ for Ubuntu 24.04 container)
graph-obsidian-agent-docs/    Reference agent docs from the graph-obsidian project (read-only context)
setup                         Bash entrypoint that wraps dotfiles_tools with sensible defaults
dotfiles-manifest.json        Source of truth for what installs where
ARCHITECTURE.md               Canonical hub for system design and convention claims
```

Dot-prefixed directories (`.claude/`, `.codex/`, `.codacy/`, `.gstack/`, `.specify/`, `.agents/`, `.github/`, `.vscode/`) are tool state or CI config, intentionally excluded from this layout list.

## MCP Tool Availability <!-- anchor: mcp -->

<!-- mirrors: ARCHITECTURE.md#mcp-tool-availability -->

Two MCP servers are available to agents when the required tokens are set.

### Token loading — automatic

A user-global `SessionStart` hook (`~/.claude/hooks/load-project-env.sh`) loads
each project's `.envrc` / `.envrc.local` at session start and exports the token
allowlist into every Bash tool call for the session. The allowlist covers:
`CODACY_ACCOUNT_TOKEN`, `CODACY_API_TOKEN`, `CODACY_PROJECT_TOKEN`,
`CODACY_USERNAME`, `CODACY_PROJECT_NAME`, `CODACY_ORGANIZATION_PROVIDER`,
`GITHUB_TOKEN`, `GH_TOKEN`, `HF_TOKEN`, `HUGGINGFACE_TOKEN`.

**Do not run `direnv allow`, `source .envrc.local`, or `cat ~/.codacy/...`.**
Use `codacy-cli`, Codacy MCP, and `gh` directly — tokens are already in env.

If a tool returns 401/404/auth-error: look for a `[claude-env]` diagnostic in
the session-start output. Recovery: `./setup repair-codacy-env`.

Per-project extra variables: create `.claude/env-allowlist` with one variable
name per line; the hook merges those into the forwarded set.

### GitHub MCP (`mcp__github__*`) <!-- anchor: mcp-github -->

Available when `GITHUB_TOKEN` is set. `$GITHUB_TOKEN` is automatically loaded by the SessionStart hook from `.envrc.local` — no manual sourcing needed.

Key tools: `create_issue`, `list_issues`, `create_pull_request`, `list_pull_requests`, `get_pull_request`, `get_pull_request_files`, `get_pull_request_reviews`, `get_pull_request_status`, `push_files`, `search_code`, `search_repositories`.

Prerequisite: `gh auth login` must have been run. If `gh` is not authenticated, `GITHUB_TOKEN` silently becomes an empty string and all GitHub MCP calls will fail — run `gh auth status` to verify.

### Codacy MCP (`mcp__codacy__*`) <!-- anchor: mcp-codacy -->

Available when `CODACY_ACCOUNT_TOKEN` is set. The token is a machine-level account token stored at `~/.codacy/account-token`. It is automatically loaded into `$CODACY_ACCOUNT_TOKEN` by the SessionStart hook — no manual sourcing needed. A project-level token alone is insufficient.

Key tools: `codacy_list_repository_issues`, `codacy_get_file_issues`, `codacy_get_file_coverage`, `codacy_get_pull_request_files_coverage`, `codacy_cli_analyze`, `codacy_setup_repository`.

Background and the broader auth surface (project token bridges, machine-level vs project-level tokens): see [ARCHITECTURE.md#auth-guidance](ARCHITECTURE.md#auth-guidance) and [ARCHITECTURE.md#token-bridges](ARCHITECTURE.md#project-token-bridges).

## Template Convention <!-- anchor: templates -->

<!-- mirrors: ARCHITECTURE.md#template-convention -->

- Files ending in `.template` are copy-and-customize — never source or execute from this path.
- Placeholders follow the pattern `{{UPPER_SNAKE_CASE}}` (double-braces, no spaces) and must all be replaced before use.
- No secrets, tokens, or API keys are stored anywhere in this repo. Auth files are excluded by `.gitignore` and the global git ignore.

## Local API Access <!-- anchor: local-api -->

When this repo is opened in a shell that has loaded `.envrc` and `.envrc.local`,
agents may use the following environment variables for local Codacy and GitHub
billing workflows:

- `CODACY_ACCOUNT_TOKEN`
- `CODACY_ORGANIZATION_PROVIDER`
- `CODACY_PROJECT_NAME`
- `CODACY_PROJECT_TOKEN`
- `CODACY_USERNAME`
- `GH_TOKEN` (also used by `gh` CLI; the GitHub Actions billing audit at `docs/operations/github-actions-usage-baseline.md` uses a file-backed copy of this token)

These values come from direnv-managed local environment files, not from the
repository. Do not commit them, print them, or add them to tracked config. If
the shell output shows `direnv: export ...`, treat those exports as available
for the current session only.

## Symlink Convention <!-- anchor: symlinks -->

<!-- mirrors: ARCHITECTURE.md#symlink-convention -->

`CLAUDE.md` and `GEMINI.md` at the repo root are symlinks to `AGENTS.md`. At the project level, `agents/CLAUDE.md.template` and `agents/GEMINI.md.template` are symlinks to `agents/AGENTS.md.template`. This keeps one source of truth per scope.

To verify the symlinks are intact:
```bash
ls -la CLAUDE.md GEMINI.md
# expected: both point to AGENTS.md
```

## Making Changes <!-- anchor: making-changes -->

- Adding a new tool config: create a `<tool>/` directory with `<file>.template` files; update `README.md` table and the bootstrap commands.
- Updating an existing template: edit the `.template` file directly; note in the commit message if any placeholder names changed.
- Never commit files containing real credentials. Run `git diff --staged` before every commit and check for tokens, keys, or personal paths.
- Adding a curl-based installer to `TOOL_BASELINE`: declare `"interpreter": "..."` in `install_args` if the script is anything other than bash. `_execute_curl` runs the script under that interpreter (Ubuntu's default `/bin/sh` is dash and rejects bash extensions).
- Adding a new bootstrap tool to `TOOL_BASELINE`: declare a `post_install` tuple (may be empty) listing follow-up actions. `kind="auto"` runs when the user passes `--yes`; `kind="guidance"` only prints the command. Templates may use `{which:<name>}` and `{user}` placeholders; unresolved placeholders downgrade to guidance automatically.

## Development Workflow <!-- anchor: dev-workflow -->

<!-- mirrors: ARCHITECTURE.md#development-workflow -->

```bash
git status                    # check what changed
git diff                      # review before staging
git add <specific files>      # never git add -A
git commit -m "..."
```

Finalizing a PR: `./setup ship` is the canonical way to merge. It runs
`gh pr update-branch` if the branch is `BEHIND` its base, then step 4d
runs `codacy-cli analyze` and uploads SARIF using `CODACY_PROJECT_TOKEN`
before check polling begins. All four Codacy checks are required:
`codacy-safety-net` (GitHub Actions workflow), and the three Codacy app
checks `Codacy Static Code Analysis`, `Codacy Coverage Variation`, and
`Codacy Diff Coverage`. `./setup ship` resolves the full required set from
the GitHub API dynamically (branch protection or rulesets) and polls every
check until they report `success` before squash-merging when the PR is
`CLEAN` or `UNSTABLE`. When `mergeStateStatus` is `BLOCKED` after all four
required checks pass, ship adds `--admin` to bypass the remaining gate
(`setup:1287-1296`); the code does not introspect the BLOCKED reason, so
treat admin bypass as eligible whenever required checks are green and the
PR has no other blocking signal. Requires an authenticated `gh` and
`CODACY_PROJECT_TOKEN`.

Runtime validation tooling uses Python standard library modules and uv-managed
developer commands:

```bash
uv run python -m dotfiles_tools doctor --repo . --home "$HOME"
uv run python -m dotfiles_tools plan --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools init-project --repo . --project /path/to/project --vars project-vars.json --yes
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
```

Pre-push hook details (5 steps; does NOT upload Codacy SARIF) and the local
quality pipeline (7 stages) are documented at
[ARCHITECTURE.md#pre-push](ARCHITECTURE.md#pre-push-hook) and
[ARCHITECTURE.md#quality-pipeline](ARCHITECTURE.md#local-quality-pipeline).

## Docker-based browser automation <!-- anchor: docker-browser -->

<!-- mirrors: ARCHITECTURE.md#docker-based-browser-automation -->

When Playwright lacks Ubuntu 26.04 binaries, gstack browser skills run inside
an Ubuntu 24.04 container. From the host: `./setup docker-build`,
`./setup gstack-setup`, `./setup gstack-codex`, `./setup gstack-shell`,
`./setup gstack-exec`. **Path-preservation invariant:** container paths
must match host paths exactly; do not change container `HOME` or mount
paths, or skill commands that reference absolute paths will break. For
the 9 docker-compose settings, mount list, verified-state record, and
file inventory, see
[ARCHITECTURE.md#docker-based-browser-automation](ARCHITECTURE.md#docker-based-browser-automation).

## Codacy CLI Configuration Constraint <!-- anchor: codacy-cli -->

<!-- mirrors: ARCHITECTURE.md#codacy-cli-configuration -->

`codacy-cli analyze` silently exits 0 and produces an empty SARIF file when
`.codacy/codacy.yaml` does not exist. It prints "No configuration file was found,
execute init command first." but does **not** return a non-zero exit code.

`.codacy/` is gitignored (`.gitignore` line 27, commit 46af6c8). Do not attempt to
restore a committed `.codacy/codacy.yaml` — prior commits 81b38aa, 8d47730 did this
and were removed when `.codacy/` was gitignored. The file gets silently untracked.

Two patterns for ephemerally providing the config (DO NOT mix these):

**In `scripts/quality-pipeline.sh`** (`CODACY_ACCOUNT_TOKEN` must NOT appear — test enforced):
```bash
mkdir -p .codacy
printf -- '---\ntools:\n  - name: pylint\n' > .codacy/codacy.yaml
codacy-cli analyze --tool pylint --format sarif -o "$SARIF"
rm -f .codacy/codacy.yaml
```

**In `./setup ship` step 4d** (`CODACY_ACCOUNT_TOKEN` available via direnv):
```bash
codacy-cli init --api-token "${CODACY_ACCOUNT_TOKEN:-}" --provider gh \
  --organization "${CODACY_USERNAME:-}" --repository "${CODACY_PROJECT_NAME:-}" 2>/dev/null || true
codacy-cli analyze --tool pylint --format sarif -o "$SARIF"
```

The `/codacy` skill (`~/.claude/skills/codacy/SKILL.md`) documents all procedures
and troubleshooting. Invoke it before running `codacy-cli`.

Known non-fatal messages: `tools//patterns failed with status 404` (codacy-cli bug),
`"Repository Analysis" is disabled` (informational Codacy server notice; 200 OK
on the upload response = SARIF accepted). Neither blocks the four required Codacy
checks from running on the PR.

Coverage upload paths (Path A: GitHub Actions baseline / Path B: Codacy
server diff) are documented at [ARCHITECTURE.md#codacy-coverage-paths](ARCHITECTURE.md#coverage-upload-paths).

## Hook Trigger Map <!-- anchor: hooks -->

<!-- mirrors: ARCHITECTURE.md#hook-trigger-map -->

The Git repo hook (`.git/hooks/pre-push`) blocks direct pushes to `main`
regardless of which CLI initiated the push. Install once per repo with
`./setup hooks` or `./scripts/install-hooks.sh`. CLI-specific tool hooks
are a separate layer:

- **Claude Code:** `/hooks` slash command; SessionStart hook.
- **Gemini CLI:** `gemini hooks --help`; do NOT run `gemini hooks migrate`.
- **Codex CLI:** loads `AGENTS.md` context only (no tool-hook surface used here).
- **Copilot CLI:** `/instructions`, `/env`; `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`.

For the full 4-CLI matrix and per-CLI hook details, see
[ARCHITECTURE.md#hook-trigger-map](ARCHITECTURE.md#hook-trigger-map).

Do not add lock files unless runtime dependencies are introduced and the Spec
Kit plan explains why they are needed. Coverage is only meaningful for real
validation/setup code and must generate `coverage.xml` before Codacy upload.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, see the spec documents in
`specs/`. Spec status (2026-05-17): `001-dotfiles-bootstrap-validation` is
complete; `002-setup-optional-integrations` is complete; `002-setup-menu-recommendation`
has shipped code (see `dotfiles_tools/machine_summary.py`) but its `tasks.md`
checklist is unchecked — treat the implementation as canonical, the task list as
stale. Check `specs/` for any new active specifications or design documents.
Consolidated design history: [ARCHITECTURE.md#design-history](ARCHITECTURE.md#design-history).
<!-- SPECKIT END -->
