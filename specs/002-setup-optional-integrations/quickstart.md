# Quickstart: Optional Setup Integrations Menu

## Manual Flow Check

1. Use an empty temporary project:

   ```bash
   mkdir -p /tmp/dotfiles-empty-project
   ./setup /tmp/dotfiles-empty-project
   ```

2. Confirm the top-level menu shows one generic optional integrations entry and does not expose Codacy directly at top level.

3. Choose the optional integrations entry.

4. Confirm the secondary menu includes `Manage Codacy API access` and a back/cancel option.

5. Cancel from the submenu and confirm no Codacy files were written.

## Repository Token Flow

1. Use an existing GitHub project folder:

   ```bash
   ./setup /path/to/project
   ```

2. Choose `Optional integrations and APIs`, then `Manage Codacy API access`.

3. Choose repository-token mode.

4. Confirm owner and repository.

5. Paste a repository token when prompted.

6. Review the token-free preview and approve the final confirmation.

7. Verify:

   ```bash
   test -f /path/to/project/.envrc
   test -f /path/to/project/.envrc.local
   test -f "$HOME/.codacy/<owner>-<repo>.project-token"
   grep -q CODACY_PROJECT_TOKEN /path/to/project/.envrc.local
   ```

8. Confirm the token value does not appear in project files or command output.

9. If `.envrc` or `.envrc.local` existed before setup, confirm a
   `.envrc.bak.<timestamp>` or `.envrc.local.bak.<timestamp>` backup exists
   before the changed content.

10. Run the activation step shown by setup, for example:

   ```bash
   direnv allow /path/to/project
   ```

## Account Token Flow

1. Repeat the project setup flow and choose account-token mode.

2. Confirm owner and repository.

3. Paste an account token when prompted.

4. Review the token-free preview and approve the final confirmation.

5. Verify `.envrc.local` exposes:

   ```text
   CODACY_API_TOKEN
   CODACY_ORGANIZATION_PROVIDER
   CODACY_USERNAME
   CODACY_PROJECT_NAME
   ```

6. Confirm the token value is stored under `~/.codacy/` and not in the project.

## Blank Token Flow

1. Repeat the project setup flow and leave the token prompt blank.

2. If the token file already exists, confirm setup reuses it.

3. If the token file does not exist, confirm `.envrc.local` does not contain an
   active `CODACY_PROJECT_TOKEN` or `CODACY_API_TOKEN` export pointing at a
   missing file, and confirm setup reports that a token is required before
   activation.

## Automated Validation

```bash
bash -n setup
uv run python -m unittest tests.test_setup_script tests.test_docs tests.test_project_init_success
uv run python -m unittest discover -s tests
```

Expected result: all tests pass, and no test fixture or captured output contains a real token value.
