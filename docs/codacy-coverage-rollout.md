# Codacy Coverage Rollout

This repo now has real validation code and test coverage upload wired to Codacy.
Use this document as the checklist for applying the same pattern to other repos.

## What Was Implemented Here

1. Added meaningful Python validation/setup code in `dotfiles_tools/`.
   - `doctor` audits repo integrity, symlinks, template parseability, missing targets, drifted targets, and protected/manual files.
   - `plan` prints setup operations without writing.
   - `apply` writes approved operations, creates parent directories, and backs up drifted files before replacement.
   - `init-project` renders project agent docs, creates `CLAUDE.md` and `GEMINI.md` symlinks, and fails on unresolved placeholders.
2. Added `dotfiles-manifest.json` as the source of truth for bootstrap targets.
3. Added `tests/` with `unittest` coverage for manifest validation, template parsing, secret scanning, drift detection, apply behavior, protected targets, project initialization, docs, and workflow behavior.
4. Added `.github/workflows/dotfiles-validation.yml`.
   - Runs the unit tests with `coverage.py`.
   - Generates `coverage.xml`.
   - Uploads `coverage.xml` to Codacy on push events only when `CODACY_PROJECT_TOKEN` is configured.
5. Added the GitHub Actions secret `CODACY_PROJECT_TOKEN`.
6. Updated the workflow to use Codacy's repository-token input:
   - `project-token: ${{ secrets.CODACY_PROJECT_TOKEN }}`
7. Verified the workflow on `main`.
   - Run: `https://github.com/kairin/000-dotfiles/actions/runs/25203399909`
   - Commit: `29f7529c100b6b2c6ae7aa9fcc6aa1ea1b60a5e8`
   - Result: tests passed, `coverage.xml` generated, Codacy upload step passed.
8. Verified Codacy received the report.
   - Branch: `main`
   - Commit: `29f7529`
   - Language: Python
   - Status: `Processed`
9. Verified pull requests emitted the required Codacy coverage checks.
   - `Codacy Static Code Analysis`
   - `Codacy Coverage Variation`
   - `Codacy Diff Coverage`
10. Updated GitHub protection after coverage checks were proven.
   - Classic `main` branch protection requires all three Codacy contexts.
   - The active default-branch ruleset requires the same three Codacy contexts.
   - Both protection layers use strict status checks.

## Reuse Steps For Another Repo

1. Make sure the repo has real tests worth measuring.
   - For Python, prefer a command that can run locally and in CI.
   - Example:
     ```bash
     uv run python -m unittest discover -s tests
     ```
2. Generate a Codacy-supported coverage report.
   - For Python, `coverage.py` can generate `coverage.xml`.
   - Example:
     ```bash
     uv run --with coverage coverage run -m unittest discover -s tests
     uv run --with coverage coverage xml
     test -f coverage.xml
     ```
3. Add a GitHub Actions workflow that runs tests and generates coverage.
   - Start from this repo's `.github/workflows/dotfiles-validation.yml`.
   - Change the test command if the target repo uses a different test runner.
4. Add the coverage token as a GitHub Actions secret in the target repo.
   - Use the same secret name for consistency:
     ```bash
     gh secret set CODACY_PROJECT_TOKEN --repo OWNER/REPO
     ```
   - Paste the Codacy repository API token when prompted.
   - If the target repo uses a Codacy account token instead, keep it in a
     GitHub secret and use the action's `api-token` input plus the required
     provider, owner, and repository metadata.
   - Do not commit the token to any file.
5. Use the repository-token input in the workflow.
   - Required workflow shape:
     ```yaml
     env:
       CODACY_PROJECT_TOKEN: ${{ secrets.CODACY_PROJECT_TOKEN }}

     - name: Upload coverage to Codacy
       if: ${{ github.event_name == 'push' && env.CODACY_PROJECT_TOKEN != '' }}
       uses: codacy/codacy-coverage-reporter-action@89d6c85cfafaec52c72b6c5e8b2878d33104c699
       with:
         project-token: ${{ secrets.CODACY_PROJECT_TOKEN }}
         coverage-reports: coverage.xml
     ```
6. Commit through a pull request.
   - Let the target repo's normal branch protection and Codacy static analysis run.
7. After merge, verify the push workflow.
   - Example:
     ```bash
     gh run list --repo OWNER/REPO --workflow "Dotfiles Validation" --branch main --limit 5
     gh run view RUN_ID --repo OWNER/REPO --json conclusion,jobs
     ```
   - Confirm these steps passed:
     - test run
     - coverage XML generation
     - Codacy coverage upload
8. Check Codacy's coverage page.
   - Confirm the report is received for the expected commit and branch.
   - Expected status after processing: `Processed`.
9. Open or update a pull request and confirm Codacy emits the coverage checks.
   - Required check names for the coverage-enabled profile:
     - `Codacy Static Code Analysis`
     - `Codacy Coverage Variation`
     - `Codacy Diff Coverage`
10. Configure Codacy gates for the target repo.
    - Static analysis gates should match the repo's quality policy.
    - Coverage gates only block when thresholds are set in Codacy.
    - Coverage percentage and file coverage goals are reporting signals until
      coverage gates are configured.
11. Apply GitHub protection after the checks are visible.
    - Use `gh/codacy-branch-protection.md`.
    - Require all active Codacy contexts in classic branch protection.
    - Require the same contexts in the active default-branch ruleset.
    - Keep both protection layers on strict status checks.

## Pending / Optional Follow-Up

1. Apply this same workflow pattern repo by repo.
   - Each target repo needs its own test command and workflow name adjusted.
2. Decide whether to use repo-specific Codacy project tokens or one shared account token.
   - This repo uses a repository token stored as `CODACY_PROJECT_TOKEN`.
   - If a repo uses a Codacy account token instead, the action input should be `api-token`, not `project-token`.
3. Enable strict coverage gates only after coverage upload is stable.
   - First confirm a few PRs upload coverage consistently.
   - Then set a reasonable threshold in Codacy.
   - After thresholds are set, require `Codacy Coverage Variation` and
     `Codacy Diff Coverage` in GitHub branch protection and the ruleset.
4. Decide whether coverage should upload on every `push`, every `pull_request`, or only protected branches.
   - This repo runs validation on both `push` and `pull_request`, but uploads coverage on `push` only to avoid duplicate reports for the same commit.
5. Keep static analysis and coverage separate.
   - Codacy static analysis is handled by the Codacy GitHub app/check.
   - Coverage upload is handled by the GitHub Actions workflow and `CODACY_PROJECT_TOKEN`.
