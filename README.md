# dotfiles

Config templates for AI coding tools and shell environment.

## What's here

| Directory | Target path | Contents |
|---|---|---|
| `agents/` | project root | `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` / `copilot-instructions.md` templates |
| `claude/` | `~/.claude/` | `settings.json`, `keybindings.json`, global `CLAUDE.md` |
| `codex/` | `~/.codex/` | `config.toml`, `rules/default.rules` |
| `gemini/` | `~/.gemini/` | `settings.json`, global `GEMINI.md` |
| `gh/` | `~/.config/gh/` | `config.yml`, Codacy branch protection checklist |
| `fish/` | `~/.config/fish/` | `fish_plugins`, `functions/direnv.fish`, `env.fish` |
| `git/` | `~/.config/git/` | `config` |

The filenames listed above are installed target filenames. Source files in this
repo may carry a `.template` suffix before they are copied or rendered to those
targets.

## Conventions

**`.template` suffix** — copy to the target path and fill in any `{{PLACEHOLDERS}}`.

**Symlinks** — `CLAUDE.md` and `GEMINI.md` always symlink to `AGENTS.md` so there is one source of truth per project:

```bash
ln -sf AGENTS.md CLAUDE.md
ln -sf AGENTS.md GEMINI.md
```

**Secrets** — no tokens, passwords, or API keys are ever stored here. Auth files (`hosts.yml`, `auth.json`, `oauth_creds.json`, `token`) are excluded. Use `huggingface-cli login`, `gh auth login`, `codex auth`, and env vars loaded from files outside this repo.

## Bootstrap a new machine

The root `./setup` script is the fresh-machine entrypoint:

```bash
./setup
```

With no arguments, it first ensures `uv` is available. If `uv` is missing, it
runs the official standalone installer with `curl` or `wget`, refreshes the
current process `PATH`, verifies `uv --version`, then continues. If `uv` is
already installed, it runs `uv self update` first; package-manager installations
that cannot self-update are warned about and reused when `uv --version` still
works.

After the uv-first bootstrap, `./setup` uses the machine doctor and bootstrap
plan internally, but the default screen is a short decision summary. It groups
the pending work into files that will be updated with backups, files that will
be created, protected/manual files that will not be touched, a dedicated Fonts
section, and baseline tool/auth guidance for `uv`, `git`, `gh`, `fish`,
`direnv`, `codex`, `claude`, and `gemini`. It then offers:

1. apply safe non-protected dotfiles plus approved install/update recipes,
2. show the full diagnostic output, including font detection,
3. show tool and sign-in guidance,
4. exit without writing.

The Fonts stage is catalog driven. On standard Ubuntu-style Linux it manages
the Nerd Fonts release assets `JetBrainsMono.zip`, `FiraCode.zip`, `Hack.zip`,
and `Meslo.zip`, caching archives under `~/.cache/000-dotfiles/fonts/` and
installing each family under `~/.local/share/fonts/`. Terminal checks and
settings always use `* Nerd Font Mono` faces, never Propo faces. The same stage
also installs or updates apt fallback packages for emoji and symbols:
`fonts-noto-color-emoji`, `fonts-symbola`, `fonts-freefont-ttf`, and
`fonts-dejavu-core`.

Platform-specific handling stays explicit. WSL installs all Nerd Font families
Linux-side, installs JetBrainsMono Nerd Font Mono on the Windows host when
PowerShell is available, and updates Windows Terminal defaults when its settings
JSON is discoverable. Raspberry Pi installs all Nerd Font families plus Noto
Color Emoji, Symbola, and FreeFont, and verifies `MesloLGS Nerd Font Mono`.
Pixel Terminal embeds a `JBMono NF` subset of JetBrainsMono Nerd Font Mono into
ttyd and installs `fonts-noto-color-emoji`. Pixel AVF skips Nerd Font UI setup
because `weston-terminal` ignores it, and writes a plain prompt fallback
instead.

The underlying commands remain available directly:

```bash
uv run python -m dotfiles_tools doctor --repo . --home "$HOME"
uv run python -m dotfiles_tools plan --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools bootstrap-plan --repo . --home "$HOME" --json
uv run python -m dotfiles_tools bootstrap-apply --repo . --home "$HOME" --yes
```

`dotfiles-manifest.json` is the source of truth for machine targets. `doctor`
audits without writing, `plan` prints exact operations, and `apply` writes only
after `--yes`. Existing differing files are backed up before replacement.
`bootstrap-plan` and `bootstrap-apply` wrap the same manifest operations and add
install recipes such as fonts.

Protected entries are reported but skipped by default:

- `git.config` -> `~/.config/git/config`
- `fish.plugins` -> `~/.config/fish/fish_plugins`
- `repo.gitignore` -> repository `.gitignore`
- `agents.claude-template` and `agents.gemini-template` -> symlink templates

To include a protected machine target, name the exact manifest ID:

```bash
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --include-protected git.config --yes
```

## Bootstrap a new project repo

The `./setup` entrypoint at the repo root is the recommended way to scaffold or
verify agent docs in a project that lives in any folder. It self-locates this
dotfiles repo so it works directly or via a `PATH` symlink.

Passing a project path keeps project setup separate from machine setup:

```bash
./setup ~/Apps/my-project
```

Empty folders get agent-doc bootstrap options. Existing projects get verify,
repair/bootstrap, and Copilot options. When no variables file exists, inferred
metadata is saved to `.dotfiles/project-vars.json` in the target project.

What `./setup` can complete:

| Command | What it completes | Notes |
|---|---|---|
| `./setup` | Prepares/checks this computer, including uv bootstrap, machine doctor, bootstrap plan, font recipes, and safe apply options. | This is the fresh-machine flow. `uv` and approved setup recipes such as fonts may be installed automatically. |
| `./setup /path/to/project` | Inspects a project folder and offers project agent-doc actions. | Stores inferred metadata in `.dotfiles/project-vars.json` when needed. |
| `./setup init --yes` | Renders project `AGENTS.md`, creates `CLAUDE.md` and `GEMINI.md` symlinks to `AGENTS.md`, then automatically runs `verify`. | Uses `project-vars.json` from the project root or `.dotfiles/` unless `--vars` is provided. Requires `uv` because it wraps `dotfiles_tools init-project`. |
| `./setup init --copilot --yes` | Completes the same agent-doc bootstrap plus `.github/copilot-instructions.md`, then verifies all generated agent docs. | Use when the project should also receive Copilot instructions from this repo's template. |
| `./setup verify` | Performs a read-only project check for `AGENTS.md`, `CLAUDE.md`/`GEMINI.md` symlink targets, and unresolved `{{PLACEHOLDER}}` values. | Does not require `uv` or Python, so it is suitable for quick local checks, CI, or pre-commit hooks. Add `--copilot` to require and check `.github/copilot-instructions.md`. |
| `./setup doctor` | Runs the repo's machine-home audit with sensible defaults. | Wraps `dotfiles_tools doctor --repo <this repo> --home "$HOME" --profile machine`; this is read-only and requires `uv`. |

```bash
cd path/to/your-project
cat > project-vars.json <<'JSON'
{
  "PROJECT_NAME": "Example Project",
  "PROJECT_DESCRIPTION": "a concise project description",
  "LANGUAGE": "Python",
  "PACKAGE_MANAGER": "uv",
  "RUNTIME_DESCRIPTION": "local CLI",
  "INSTALL_CMD": "uv run python -m unittest discover -s tests",
  "RUN_CMD": "uv run python -m dotfiles_tools doctor --repo . --home \"$HOME\"",
  "TEST_CMD": "uv run python -m unittest discover -s tests"
}
JSON

/path/to/000-dotfiles/setup init --yes              # bootstrap + auto-verify
/path/to/000-dotfiles/setup verify                  # read-only re-check
/path/to/000-dotfiles/setup init --copilot --yes    # also write copilot file
```

`init` defaults `--project` to the current directory and auto-discovers
`project-vars.json` (or `.dotfiles/project-vars.json`). It renders
`agents/AGENTS.md.template`, creates `CLAUDE.md` and `GEMINI.md` symlinks to
`AGENTS.md`, and fails if required placeholders remain. `verify` is a fast
read-only check (no writes) suitable for CI or pre-commit.

### Install on `PATH`

```bash
ln -s /path/to/000-dotfiles/setup ~/.local/bin/dotfiles-setup
dotfiles-setup verify --project ~/code/my-app
```

### Direct CLI (advanced)

```bash
uv run python -m dotfiles_tools init-project --repo path/to/dotfiles --project . --vars project-vars.json --yes
uv run python -m dotfiles_tools init-project --repo path/to/dotfiles --project . --vars project-vars.json --copilot --yes
```

## Validation and coverage

```bash
uv run python -m unittest discover -s tests
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
test -f coverage.xml
```

CI runs the same validation suite and generates `coverage.xml`. Codacy upload is
attempted only when the `CODACY_COVERAGE_API_TOKEN` GitHub Actions secret is
configured.

For the reusable setup checklist and current Codacy rollout status, see
`docs/codacy-coverage-rollout.md`.
