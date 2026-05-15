# dotfiles — AI Agent Guidelines

Single source of truth for LLM agents. `CLAUDE.md` and `GEMINI.md` symlink to this file.

For human-facing setup instructions (quick start, scenarios, command reference), see `README.md`. This file focuses on conventions agents must respect.

## What this repo is

A collection of config templates for AI coding tools (Claude Code, Codex, Gemini CLI, gh CLI) and shell environment (fish, git), plus a small Python CLI (`dotfiles_tools`) and a bash entrypoint (`./setup`) that audit and apply those templates. Every file with a `.template` suffix is meant to be copied to its target path and customized — it is never executed or sourced directly from here.

## Protected Files — NEVER Modify Without Explicit Per-File Directive

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

## Key paths

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
```

Dot-prefixed directories (`.claude/`, `.codex/`, `.codacy/`, `.gstack/`, `.specify/`, `.agents/`, `.github/`, `.vscode/`) are tool state or CI config, intentionally excluded from this layout list.

## MCP Tool Availability

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

### GitHub MCP (`mcp__github__*`)

Available when `GITHUB_TOKEN` is set. `$GITHUB_TOKEN` is automatically loaded by the SessionStart hook from `.envrc.local` — no manual sourcing needed.

Key tools: `create_issue`, `list_issues`, `create_pull_request`, `list_pull_requests`, `get_pull_request`, `get_pull_request_files`, `get_pull_request_reviews`, `get_pull_request_status`, `push_files`, `search_code`, `search_repositories`.

Prerequisite: `gh auth login` must have been run. If `gh` is not authenticated, `GITHUB_TOKEN` silently becomes an empty string and all GitHub MCP calls will fail — run `gh auth status` to verify.

### Codacy MCP (`mcp__codacy__*`)

Available when `CODACY_ACCOUNT_TOKEN` is set. The token is a machine-level account token stored at `~/.codacy/account-token`. It is automatically loaded into `$CODACY_ACCOUNT_TOKEN` by the SessionStart hook — no manual sourcing needed. A project-level token alone is insufficient.

Key tools: `codacy_list_repository_issues`, `codacy_get_file_issues`, `codacy_get_file_coverage`, `codacy_get_pull_request_files_coverage`, `codacy_cli_analyze`, `codacy_setup_repository`.

## Template Convention

- Files ending in `.template` are copy-and-customize — never source or execute from this path.
- Placeholders follow the pattern `{{UPPER_SNAKE_CASE}}` (double-braces, no spaces) and must all be replaced before use.
- No secrets, tokens, or API keys are stored anywhere in this repo. Auth files are excluded by `.gitignore` and the global git ignore.

## Local API Access

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

## Symlink Convention

`CLAUDE.md` and `GEMINI.md` at the repo root are symlinks to `AGENTS.md`. At the project level, `agents/CLAUDE.md.template` and `agents/GEMINI.md.template` are symlinks to `agents/AGENTS.md.template`. This keeps one source of truth per scope.

To verify the symlinks are intact:
```bash
ls -la CLAUDE.md GEMINI.md
# expected: both point to AGENTS.md
```

## Making Changes

- Adding a new tool config: create a `<tool>/` directory with `<file>.template` files; update `README.md` table and the bootstrap commands.
- Updating an existing template: edit the `.template` file directly; note in the commit message if any placeholder names changed.
- Never commit files containing real credentials. Run `git diff --staged` before every commit and check for tokens, keys, or personal paths.
- Adding a curl-based installer to `TOOL_BASELINE`: declare `"interpreter": "..."` in `install_args` if the script is anything other than bash. `_execute_curl` runs the script under that interpreter (Ubuntu's default `/bin/sh` is dash and rejects bash extensions).
- Adding a new bootstrap tool to `TOOL_BASELINE`: declare a `post_install` tuple (may be empty) listing follow-up actions. `kind="auto"` runs when the user passes `--yes`; `kind="guidance"` only prints the command. Templates may use `{which:<name>}` and `{user}` placeholders; unresolved placeholders downgrade to guidance automatically.

## Development Workflow

```bash
git status                    # check what changed
git diff                      # review before staging
git add <specific files>      # never git add -A
git commit -m "..."
```

Finalizing a PR: `./setup ship` is the canonical way to merge. It runs
`gh pr update-branch` if the branch is `BEHIND` its base, then step 4d
runs `codacy-cli analyze` and uploads SARIF using `CODACY_PROJECT_TOKEN`
before check polling begins. `codacy-safety-net` is the single required
GitHub check (enforced by branch protection); the three Codacy app checks
(`Codacy Static Code Analysis`, `Codacy Coverage Variation`, `Codacy Diff
Coverage`) are advisory — they appear on PRs once Codacy processes uploaded
artifacts but are not enforced and do not block merges. `./setup ship`
resolves required checks dynamically from branch protection or rulesets,
polls until they report `success`, and squash-merges only when the PR is
`CLEAN` or `UNSTABLE`. Requires an authenticated `gh` and `CODACY_PROJECT_TOKEN`.

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

## Docker-based browser automation

`gstack` skills that drive a browser (`/qa`, `/browse`, `/qa-only`) use Playwright. Playwright does not ship prebuilt Chromium binaries for Ubuntu 26.04 (tracked at [microsoft/playwright#40117](https://github.com/microsoft/playwright/issues/40117)). To unblock browser skills on hosts where Playwright lacks support, this repo ships an Ubuntu 24.04 Docker container that runs gstack + Playwright + Chromium natively.

```bash
./setup                 # installs docker via TOOL_BASELINE (apt_keyring)
./setup docker-build    # builds gstack-browser:latest (~5 min first time)
./setup gstack-setup /home/kkk/Apps/gstack
./setup gstack-codex /home/kkk/Apps/gstack
./setup gstack-shell    # enters a shell inside the running container
```

Verified state as of 2026-05-16: Docker Engine 29.5.0 works without host `sudo` after `newgrp docker`; `gstack-browser:latest` builds; `gstack-dev` runs; `./setup gstack-setup` completed inside the container; Codex CLI 0.130.0, passwordless sudo, Playwright Chromium, and `/home/kkk/Apps/gstack/browse/dist/browse` are available in the container. The completion record is `docs/operations/gstack-browser-docker-rollout.md`.

On Ubuntu 26.04, do not run `/home/kkk/Apps/gstack/./setup` on the host for browser-backed setup; run `./setup gstack-setup /home/kkk/Apps/gstack` from this repo so Playwright Chromium is verified inside Ubuntu 24.04. Normal git operations against `/home/kkk/Apps/gstack` still happen on the host.

Inside the container, run `codex` directly or use `./setup gstack-codex`; the wrapper detects `gstack-dev` and does not require Docker there. `claude`, `/qa`, `/review`, etc. work the same as natively. The container mounts the host's `~/Apps`, `~/.codex`, `~/.claude`, and `~/.gstack` at identical paths so absolute paths inside gstack skill files keep working without translation.

**Path preservation invariant:** Container paths match host paths exactly (`/home/$USER/...`). Do not change container HOME or mount paths or skill bash commands referencing absolute paths will break.

**Files:**
- `docker/gstack-browser/Dockerfile` — image definition
- `docker/gstack-browser/docker-compose.yml` — long-running container with volume mounts; notable settings:
  - `shm_size: "2gb"` — required for Chromium stability (default 64 MB causes renderer crashes)
  - `GSTACK_CONTAINER=1` env var — set automatically; wrapper commands detect container context via this
  - `HOME`, `USER`, `LOGNAME` env vars — set to match host user so tool state resolves correctly
  - `~/.gitconfig` mounted read-only — prevents container from modifying host git identity
- `docker/gstack-browser/README.md` — humans-only operational overview

**Tokens:** gstack container commands regenerate `docker/gstack-browser/.env` from the direnv-loaded project environment on each run, forwarding only allowlisted values such as `GITHUB_TOKEN`, `CODACY_*`, `HF_*`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GOOGLE_*`. The `.env` file is gitignored.

When Playwright issue #40117 is resolved, the Docker workflow becomes optional — host browser skills will work natively again. The container path can stay as a fallback.

## Hook Trigger Map

Use these layers precisely: tool instructions are Markdown context files, tool hooks are CLI-specific session/tool hooks, and repo hooks are Git hooks that run for any caller.

- **Claude Code:** Claude hooks are configured through Claude settings files and can be inspected with `/hooks`. `~/.claude/hooks/load-project-env.sh` is only active when a Claude settings file registers it.
- **Gemini CLI:** Gemini CLI does not run Claude Code hooks automatically. Use Gemini's own hook surface only if intentionally configured. Verify and manage hooks using the interactive `/hooks` slash command inside a session, or `gemini hooks --help` in the shell. Do not run `gemini hooks migrate` unless the user explicitly asks to migrate Claude hooks into Gemini.
- **Codex CLI:** Codex loads global and project `AGENTS.md` context.
- **Copilot CLI:** Copilot auto-loads instruction files and extra directories from `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`; inspect loaded context with `/instructions` or `/env`.

Main-branch push prevention is enforced by Git's repo hook (`.git/hooks/pre-push`), not by any tool-specific hook. Run `./setup hooks` or `./scripts/install-hooks.sh` in each repo that needs protection; Git runs that hook automatically for every `git push` regardless of the caller.

Do not add lock files unless runtime dependencies are introduced and the Spec
Kit plan explains why they are needed. Coverage is only meaningful for real
validation/setup code and must generate `coverage.xml` before Codacy upload.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, see the spec documents in
`specs/`. Spec status (2026-05-15): `001-dotfiles-bootstrap-validation` is
complete; `002-setup-optional-integrations` is complete; `002-setup-menu-recommendation`
has shipped code (see `dotfiles_tools/machine_summary.py`) but its `tasks.md`
checklist is unchecked — treat the implementation as canonical, the task list as
stale. Check `specs/` for any new active specifications or design documents.
<!-- SPECKIT END -->
