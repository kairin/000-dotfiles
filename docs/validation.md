# Validation

This repo uses unit tests, coverage, and a GitHub Actions workflow to validate the setup code and docs contract.

## Local Commands

```bash
uv run python -m unittest discover -s tests
uv run --with coverage==7.5.4 coverage run -m unittest discover -s tests
uv run --with coverage==7.5.4 coverage xml
```

## Coverage Scope

Coverage is source-scoped to `dotfiles_tools/` through `.coveragerc`.
That keeps the report focused on production Python code instead of tests, docs, or spec artifacts.

## CI Workflow

`.github/workflows/dotfiles-validation.yml` runs tests on push and pull request events.
It uploads `coverage.xml` to Codacy on push events when `CODACY_PROJECT_TOKEN` is configured.
The workflow uses concurrency cancellation so stale runs do not pile up.

## Codacy Checks

The repo expects the following Codacy contexts when coverage is enabled:

- `Codacy Static Code Analysis`
- `Codacy Coverage Variation`
- `Codacy Diff Coverage`

The docs in `docs/codacy-coverage-rollout.md` describe the rollout pattern in more detail.
