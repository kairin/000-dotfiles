# Quickstart: Dotfiles Bootstrap Validation

This quickstart is written for the planned implementation. It must run without
touching the user's real home directory unless the maintainer explicitly points
commands at it.

## 1. Run Unit Tests

```bash
uv run python -m unittest discover -s tests
```

Expected result: all tests pass using temporary home/project directories.

## 2. Run Doctor Against A Temporary Home

```bash
TEMP_HOME="$(mktemp -d)"
uv run python -m dotfiles_tools doctor --repo . --home "$TEMP_HOME"
uv run python -m dotfiles_tools doctor --repo . --home "$TEMP_HOME" --json
```

Expected result: missing managed targets are reported; protected/manual targets
are reported without writes.

## 3. Plan Machine Setup

```bash
TEMP_HOME="$(mktemp -d)"
uv run python -m dotfiles_tools plan --repo . --home "$TEMP_HOME" --profile machine
uv run python -m dotfiles_tools plan --repo . --home "$TEMP_HOME" --profile machine --json
```

Expected result: output lists directory creation, copy, skip, backup, and
protected/manual actions with no filesystem writes.

## 4. Apply Machine Setup With Backups

```bash
TEMP_HOME="$(mktemp -d)"
BACKUPS="$TEMP_HOME/.dotfiles-backups"
uv run python -m dotfiles_tools apply --repo . --home "$TEMP_HOME" --profile machine --backup-dir "$BACKUPS" --yes
uv run python -m dotfiles_tools doctor --repo . --home "$TEMP_HOME" --json
```

Expected result: non-protected managed targets are installed; a second `doctor`
run reports no drift for those targets. Protected targets remain untouched unless
included by exact manifest entry ID.

## 5. Apply A Protected Target Explicitly

```bash
TEMP_HOME="$(mktemp -d)"
BACKUPS="$TEMP_HOME/.dotfiles-backups"
uv run python -m dotfiles_tools apply --repo . --home "$TEMP_HOME" --profile machine --backup-dir "$BACKUPS" --include-protected git.config --yes
```

Expected result: the protected entry is included only when its exact manifest ID
is provided, and backup behavior still applies to drifted targets.

## 6. Initialize Project Agent Docs

```bash
TEMP_PROJECT="$(mktemp -d)"
printf '{"PROJECT_NAME":"Example Project","PROJECT_DESCRIPTION":"Example"}\n' > "$TEMP_PROJECT/project-vars.json"
uv run python -m dotfiles_tools init-project --repo . --project "$TEMP_PROJECT" --vars "$TEMP_PROJECT/project-vars.json" --yes
ls -la "$TEMP_PROJECT/AGENTS.md" "$TEMP_PROJECT/CLAUDE.md" "$TEMP_PROJECT/GEMINI.md"
```

Expected result: `AGENTS.md` exists, `CLAUDE.md` and `GEMINI.md` point to it,
and unresolved required placeholders fail the command.

## 7. Generate Coverage

```bash
uv run --with coverage coverage run -m unittest discover -s tests
uv run --with coverage coverage xml
test -f coverage.xml
```

Expected result: `coverage.xml` exists after tests pass.

## 8. CI Behavior

The GitHub Actions workflow should:

1. Run the unit tests.
2. Generate `coverage.xml`.
3. Upload coverage to Codacy only when `CODACY_API_TOKEN` is configured.
4. Skip coverage upload without failing validation when the token is absent.
