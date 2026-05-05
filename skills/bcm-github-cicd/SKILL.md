---
name: bcm-github-cicd
description: Safely handle BCM git commits, pushes, PRs, CI checks, and merges to main.
---

# BCM GitHub CI/CD Flow

Use this skill when the task involves committing, pushing, opening a PR, responding to CI, or merging to `main`.

## Operating Rules

1. Never commit to `main` unless the user explicitly asks for it and the repo is validated.
2. Start from a clean tree. If needed, inspect `git status --short --branch` and `git diff --stat`.
3. Use a timestamped branch name: `git checkout -b $(date +%Y%m%d-%H%M%S)`.
4. Commit messages for feature work must start with the Spec ID, for example `[Spec 001] feat: ...`.
5. Run the repo's validation before push. Capture proof of success.
6. Push with `git push -u origin <branch>`.
7. Open a draft PR first. Use `gh pr create --draft` unless the user asked for a ready PR.
8. Check CI with `gh pr checks` or `gh run list` / `gh run view`.
9. If CI fails, read the failing log, fix the smallest correct scope, and rerun the relevant validation.
10. Merge only after green CI and any required review. Prefer `gh pr merge --merge --delete-branch`.

## High-Risk Cases

- Treat `.github/workflows/*.yml` changes as high-risk and review them carefully.
- Never force-push or rewrite `main` without explicit instruction.
- If the branch is behind `main`, rebase or merge only if that is the repo's chosen flow.

## Useful Commands

```bash
git status --short --branch
git branch --show-current
git log -1 --oneline
gh pr create --draft
gh pr checks
gh run list --limit 10
gh run view <run-id> --log-failed
gh pr merge --merge --delete-branch
```

## Done Criteria

Do not claim completion until the branch is pushed, the PR exists, CI status is known, and the final validation evidence is recorded.
