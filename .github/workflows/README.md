# GitHub Workflows

This repository uses a local-first CI/CD model.

## Policy

1. Run local workflow first:
```bash
./.runners-local/workflows/gh-workflow-local.sh all
```
2. Use GitHub workflows mainly for remote validation/deployment.
3. Preserve branch history (no auto-delete without explicit request).

## Workflow Files

Current workflow definitions in this directory include:
- `validation-tests.yml`
- `build-feature-branches.yml`
- `deploy-pages.yml`
- `zero-cost-compliance.yml`
- `astro-build-deploy.yml`
- `astro-deploy.yml`
- `astro-pages-self-hosted.yml`
- `deploy-astro.yml`
- `codacy-coverage.yml`

Some are active and some are kept for compatibility/history. Validate trigger rules before enabling or editing deployment workflows.

## Critical Checks

- Preserve `docs/.nojekyll` for Pages asset loading.
- Keep shell/script validation in PR workflows.
- Keep workflow costs within expected free-tier usage.

## Related

- `.runners-local/README.md`
- `AGENTS.md`
- `.claude/instructions-for-agents/requirements/local-cicd-operations.md`
