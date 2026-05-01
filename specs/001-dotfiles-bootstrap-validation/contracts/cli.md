# CLI Contract: `dotfiles_tools`

All commands are runnable from the repository root with `uv`:

```bash
uv run python -m dotfiles_tools <command> [options]
```

Each command renders human-readable output by default. Passing `--json` renders
a stable JSON validation report with the common report shape below.

## Common Options

| Option | Required | Description |
|---|---:|---|
| `--repo PATH` | Yes | Repository root containing `dotfiles-manifest.json` |
| `--json` | No | Emit stable JSON report instead of human-readable text |

## Profiles

- `machine`: default home bootstrap profile for installing and validating
  dotfiles under the selected `--home` directory.
- `repo`: repository-local protected checks for `.gitignore` and agent template
  symlinks. This profile is for repository validation and maintenance, not
  normal machine installation.

## Common JSON Report

```json
{
  "command": "doctor",
  "status": "ok",
  "repo": "/path/to/repo",
  "home": "/tmp/home",
  "project": null,
  "profile": "machine",
  "summary": {
    "missing": 0,
    "current": 0,
    "drifted": 0,
    "protected": 0,
    "invalid": 0,
    "blocked": 0,
    "installed": 0,
    "needs_update": 0,
    "manual": 0,
    "unsupported": 0,
    "operations": 0,
    "backups": 0,
    "errors": 0
  },
  "entries": [],
  "operations": [],
  "backups": [],
  "errors": []
}
```

Status values:
- `ok`: command completed with no invalid, blocked, failed, or drift requiring action.
- `warning`: command completed and found missing, drifted, or protected/manual items.
- `failed`: command could not complete the requested validation or write.
- `partial`: `apply` stopped after one failed write and earlier writes may have completed.

## `doctor`

Validates repository and target state without writing.

```bash
uv run python -m dotfiles_tools doctor --repo . --home "$HOME"
uv run python -m dotfiles_tools doctor --repo . --home "$HOME" --json
```

Options:

| Option | Required | Description |
|---|---:|---|
| `--home PATH` | Yes | Target home directory to evaluate |
| `--profile ID` | No | Manifest profile to evaluate; default `machine` |

Exit status:
- `0`: no invalid repository state and no failed validation.
- `1`: invalid manifest, broken symlink, parse error, secret finding, or blocked path.

JSON requirements:
- `entries[]` contains one object per evaluated manifest entry.
- Each entry includes `entry_id`, `state`, `protected`, `source`, `target`, and `reason`.

## `plan`

Prints exact setup operations without writing.

```bash
uv run python -m dotfiles_tools plan --repo . --home "$HOME" --profile machine
uv run python -m dotfiles_tools plan --repo . --home "$HOME" --profile machine --json
```

Options:

| Option | Required | Description |
|---|---:|---|
| `--home PATH` | Yes | Target home directory |
| `--profile ID` | No | Manifest profile; default `machine` |
| `--include-protected ID` | No | Exact protected manifest entry ID to include; repeatable |

Exit status:
- `0`: plan generated successfully.
- `1`: manifest or target validation prevents planning.

JSON requirements:
- `operations[]` is ordered.
- Protected entries not explicitly included produce `skip` or `refuse`, not writes.
- Drifted writable entries include a `backup` operation before replacement.

## `apply`

Applies the operation plan after explicit approval.

```bash
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes
uv run python -m dotfiles_tools apply --repo . --home "$HOME" --profile machine --backup-dir "$HOME/.dotfiles-backups" --yes --json
```

Options:

| Option | Required | Description |
|---|---:|---|
| `--home PATH` | Yes | Target home directory |
| `--profile ID` | No | Manifest profile; default `machine` |
| `--backup-dir PATH` | Yes | Directory where existing differing targets are backed up |
| `--yes` | Yes for writes | Approval flag required before any write |
| `--include-protected ID` | No | Exact protected manifest entry ID to include; repeatable |

Exit status:
- `0`: apply completed without failed writes.
- `1`: approval missing, validation failed, write failed, or partial apply occurred.

JSON requirements:
- `backups[]` records every attempted backup.
- If a write fails after earlier writes completed, `status` is `partial`,
  operations after the failed write are not executed, and errors identify the
  failed operation.

## `bootstrap-plan`

Prints the machine setup plan including manifest-backed dotfiles and approved
install/update recipes such as fonts.

```bash
uv run python -m dotfiles_tools bootstrap-plan --repo . --home "$HOME" --json
```

Options:

| Option | Required | Description |
|---|---:|---|
| `--home PATH` | Yes | Target home directory |
| `--profile ID` | No | Manifest profile; default `machine` |
| `--include-protected ID` | No | Exact protected manifest entry ID to include; repeatable |

JSON requirements:
- `entries[]` includes normal manifest entries plus recipe entries.
- Font recipe entries use states such as `missing`, `installed`,
  `needs_update`, `manual`, and `unsupported`.
- Top-level `fonts[]` has one record per applicable catalog item. Each record
  includes `family`, `source_type`, `state`, `installed_version`,
  `latest_version` for Nerd Font assets or `candidate_version` for apt
  packages, `target`, and `terminal_face`.

## `bootstrap-apply`

Applies the combined machine bootstrap plan after explicit approval.

```bash
uv run python -m dotfiles_tools bootstrap-apply --repo . --home "$HOME" --yes
uv run python -m dotfiles_tools bootstrap-apply --repo . --home "$HOME" --backup-dir "$HOME/.dotfiles-backups" --yes --json
```

Options:

| Option | Required | Description |
|---|---:|---|
| `--home PATH` | Yes | Target home directory |
| `--profile ID` | No | Manifest profile; default `machine` |
| `--backup-dir PATH` | No | Backup directory; defaults to `<home>/.dotfiles-backups` |
| `--yes` | Yes for writes | Approval flag required before any write |
| `--include-protected ID` | No | Exact protected manifest entry ID to include; repeatable |

Font recipe requirements:
- Standard Ubuntu-style Linux plans `JetBrainsMono.zip`, `FiraCode.zip`,
  `Hack.zip`, and `Meslo.zip` from the latest Nerd Fonts release and installs
  each family under `~/.local/share/fonts/`.
- Terminal checks and generated settings always use `* Nerd Font Mono` faces;
  Propo faces may be installed from the full archives but are never selected
  for terminal configuration.
- Apt package records use `dpkg-query` for `installed_version` and
  `apt-cache policy` for `candidate_version`; missing or stale packages are
  installed with `apt-get install -y`.
- Standard Ubuntu-style Linux installs or updates `fonts-noto-color-emoji`,
  `fonts-symbola`, `fonts-freefont-ttf`, and `fonts-dejavu-core`.
- In WSL, all Nerd Font families are installed Linux-side. PowerShell Windows
  host installation is limited to JetBrainsMono Nerd Font Mono and Windows
  Terminal is updated only when the settings JSON is discoverable.
- On Raspberry Pi, all four Nerd Font families are installed with Noto Color
  Emoji, Symbola, and FreeFont apt fallbacks, and `MesloLGS Nerd Font Mono` is
  verified through fontconfig when available.
- On Pixel Terminal, backs up ttyd HTML/service files before sudo writes and
  orders systemd daemon reload before service restart. The embedded `JBMono NF`
  face is a subset/alias of JetBrainsMono Nerd Font Mono, and
  `fonts-noto-color-emoji` is installed through apt.
- On Pixel AVF, skips Tide/Nerd Font UI setup and writes a plain prompt
  fallback instead.

## `init-project`

Initializes project-level agent docs from this repository.

```bash
uv run python -m dotfiles_tools init-project --repo . --project /path/to/project --vars project-vars.json --yes
uv run python -m dotfiles_tools init-project --repo . --project /path/to/project --vars project-vars.json --yes --copilot --json
```

Options:

| Option | Required | Description |
|---|---:|---|
| `--project PATH` | Yes | Target project directory |
| `--vars PATH` | Yes | JSON file containing placeholder values |
| `--backup-dir PATH` | No | Backup directory; default under the project |
| `--yes` | Yes for writes | Approval flag required before any write |
| `--copilot` | No | Also create `.github/copilot-instructions.md` |

Exit status:
- `0`: project initialization completed.
- `1`: approval missing, unresolved placeholder, backup failure, or write failure.

JSON requirements:
- Report includes written files, created symlinks, backups, and unresolved
  placeholders.
- `CLAUDE.md` and `GEMINI.md` symlink targets are reported explicitly.
