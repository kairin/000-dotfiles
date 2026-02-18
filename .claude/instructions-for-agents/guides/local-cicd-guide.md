# Local CI/CD Guide

Practical command reference for local-first validation.

## Daily Commands

```bash
# Full required workflow
./.runners-local/workflows/gh-workflow-local.sh all

# Fast validation loop
./.runners-local/workflows/gh-workflow-local.sh validate

# Status and billing
./.runners-local/workflows/gh-workflow-local.sh status
./.runners-local/workflows/gh-workflow-local.sh billing
```

## Troubleshooting

- If validation fails, open `.runners-local/logs/` and inspect the newest workflow log.
- Fix the failing script/config/doc and rerun `validate`.
- Run `all` before commit or push.

## Related

- [Local CI/CD Operations](../requirements/local-cicd-operations.md)
- [Git Strategy](../requirements/git-strategy.md)
