# Workflow Architecture

## Local-First Flow

```text
Change -> Local CI/CD (required) -> Branch push -> PR checks -> Merge -> Optional deploy workflow
```

## Stages

1. Local validation (`gh-workflow-local.sh all`)
2. GitHub PR validation workflows
3. Merge to `main`
4. Deployment workflow (if enabled/configured)

## Design Constraints

- Minimize GitHub Actions usage.
- Keep Pages deployment safeguards (`docs/.nojekyll`).
- Keep workflow changes auditable and branch-preserving.
- Prefer deterministic script checks over ad-hoc commands.

## Operational Notes

- Verify each workflow trigger and path filter after edits.
- Do not assume all workflows are active; inspect `on:` blocks.
- Re-run local checks after any workflow modification.

```bash
./.runners-local/workflows/gh-workflow-local.sh all
```
