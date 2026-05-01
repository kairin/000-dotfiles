# Codacy Branch Protection Checklist

Public-safe checklist for asking an LLM or operator to verify and enable GitHub
branch protection so Codacy reports the default branch as fully protected.

This document stores command patterns only. It must not contain GitHub tokens,
Codacy tokens, private repository names, or one-off local paths.

## Goal

For each repository, the default branch should be protected by both:

- Classic GitHub branch protection.
- An active repository ruleset targeting the default branch.

Both protection layers should require every Codacy gate that is active and
meaningful for the repository.

For docs/config/template repositories without a real test and coverage pipeline,
the correct gate set is usually:

```text
Codacy Static Code Analysis
```

For code repositories with real tests, coverage reports, and Codacy coverage
upload configured, the correct gate set is usually:

```text
Codacy Static Code Analysis
Codacy Coverage Variation
Codacy Diff Coverage
```

Codacy may still show partial protection if only one of these checks is
required while the matching coverage gates are enabled in Codacy, even when
GitHub says the branch is protected.

Do not require coverage checks for a repository that cannot emit real coverage
statuses. That blocks normal PR merges and encourages admin bypasses or fake
coverage. For docs/config/template repositories, disable Codacy coverage gates in
Codacy settings and require only the static analysis gate in GitHub protection.

## Inputs

Set these per repository:

```bash
OWNER="{{GITHUB_OWNER}}"
REPO="{{GITHUB_REPO}}"
BRANCH="$(gh repo view "$OWNER/$REPO" --json defaultBranchRef --jq '.defaultBranchRef.name')"
CODACY_APP_ID="56611"
RULESET_NAME="Protect default branch"
```

`56611` is the GitHub App id observed for `codacy-production`. If a repository
uses a different Codacy GitHub App, verify the id from an existing Codacy check:

```bash
gh api "repos/$OWNER/$REPO/commits/$BRANCH/check-runs" \
  --jq '.check_runs[] | select(.name | startswith("Codacy")) | {name, app_id: .app.id, app_slug: .app.slug}'
```

## Verify Current State

```bash
gh repo view "$OWNER/$REPO" --json nameWithOwner,defaultBranchRef,viewerPermission

gh api "repos/$OWNER/$REPO/branches/$BRANCH" \
  --jq '{name, protected, protection: .protection}'

gh api "repos/$OWNER/$REPO/branches/$BRANCH/protection" \
  --jq '{required_status_checks, required_pull_request_reviews, enforce_admins, allow_force_pushes, allow_deletions}'

gh api "repos/$OWNER/$REPO/rulesets" \
  --jq '.[] | {id, name, target, enforcement, conditions, rules: [.rules[] | {type, parameters}]}'

gh api "repos/$OWNER/$REPO/rules/branches/$BRANCH" \
  --jq '[.[] | {type, parameters}]'
```

Expected protected state:

- Branch API reports `protected: true`.
- Classic branch protection requires every active Codacy context for the chosen
  profile.
- Classic branch protection has `strict: true`.
- Admin enforcement is enabled.
- Force pushes and deletions are disabled.
- Effective branch rules include `deletion`, `non_fast_forward`,
  `pull_request`, and `required_status_checks`.
- Effective rules require every active Codacy context for the chosen profile
  with strict status checks.

## Choose The Protection Profile

Use the static-only profile when the repository is mostly documentation,
configuration, templates, prompts, or other content that does not have meaningful
coverage.

Use the coverage-enabled profile only when all of these are true:

- The repository has a real test suite.
- CI generates a coverage report such as LCOV, Cobertura, JaCoCo, or coverage
  XML.
- CI uploads that report to Codacy for pull requests.
- Codacy emits `Codacy Coverage Variation` and `Codacy Diff Coverage` check
  runs on pull requests.

If a repository starts as static-only and later gains real test coverage, enable
the Codacy coverage gates first, verify the two coverage checks appear on a PR,
then add those contexts to GitHub branch protection and the ruleset.

## Enable Classic Branch Protection

Run this for the default branch. It requires pull requests, enforces protection
for admins, and blocks force pushes/deletions.

Static-only profile for docs/config/template repositories:

```bash
gh api --method PUT "repos/$OWNER/$REPO/branches/$BRANCH/protection" --input - <<JSON
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Codacy Static Code Analysis"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0,
    "require_last_push_approval": false,
    "required_review_thread_resolution": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": false
}
JSON
```

Coverage-enabled profile for code repositories with real coverage upload:

```bash
gh api --method PUT "repos/$OWNER/$REPO/branches/$BRANCH/protection" --input - <<JSON
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Codacy Static Code Analysis",
      "Codacy Coverage Variation",
      "Codacy Diff Coverage"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0,
    "require_last_push_approval": false,
    "required_review_thread_resolution": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": false
}
JSON
```

Classic protection may show `app_id: null` for Codacy coverage checks until
Codacy emits those checks on a pull request. The context names still matter.

## Create Or Update The Ruleset

Find an existing ruleset targeting the default branch:

```bash
RULESET_ID="$(gh api "repos/$OWNER/$REPO/rulesets" \
  --jq '.[] | select(.target == "branch" and .conditions.ref_name.include[]? == "~DEFAULT_BRANCH") | .id' \
  | head -n 1)"
```

If no suitable ruleset exists, create one.

Static-only profile for docs/config/template repositories:

```bash
gh api --method POST "repos/$OWNER/$REPO/rulesets" --input - <<JSON
{
  "name": "$RULESET_NAME",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "Codacy Static Code Analysis", "integration_id": $CODACY_APP_ID }
        ]
      }
    }
  ],
  "bypass_actors": []
}
JSON
```

Coverage-enabled profile for code repositories with real coverage upload:

```bash
gh api --method POST "repos/$OWNER/$REPO/rulesets" --input - <<JSON
{
  "name": "$RULESET_NAME",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "Codacy Static Code Analysis", "integration_id": $CODACY_APP_ID },
          { "context": "Codacy Coverage Variation", "integration_id": $CODACY_APP_ID },
          { "context": "Codacy Diff Coverage", "integration_id": $CODACY_APP_ID }
        ]
      }
    }
  ],
  "bypass_actors": []
}
JSON
```

If a suitable ruleset already exists, update it:

Static-only profile for docs/config/template repositories:

```bash
gh api --method PUT "repos/$OWNER/$REPO/rulesets/$RULESET_ID" --input - <<JSON
{
  "name": "$RULESET_NAME",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "Codacy Static Code Analysis", "integration_id": $CODACY_APP_ID }
        ]
      }
    }
  ],
  "bypass_actors": []
}
JSON
```

Coverage-enabled profile for code repositories with real coverage upload:

```bash
gh api --method PUT "repos/$OWNER/$REPO/rulesets/$RULESET_ID" --input - <<JSON
{
  "name": "$RULESET_NAME",
  "target": "branch",
  "enforcement": "active",
  "conditions": {
    "ref_name": {
      "include": ["~DEFAULT_BRANCH"],
      "exclude": []
    }
  },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "required_status_checks": [
          { "context": "Codacy Static Code Analysis", "integration_id": $CODACY_APP_ID },
          { "context": "Codacy Coverage Variation", "integration_id": $CODACY_APP_ID },
          { "context": "Codacy Diff Coverage", "integration_id": $CODACY_APP_ID }
        ]
      }
    }
  ],
  "bypass_actors": []
}
JSON
```

Do not use `null` for `integration_id` in a ruleset. GitHub rejects that shape
for required status check rules.

## Final Verification

```bash
gh api "repos/$OWNER/$REPO/branches/$BRANCH" \
  --jq '{name, protected, protection: .protection}'

gh api "repos/$OWNER/$REPO/branches/$BRANCH/protection/required_status_checks" \
  --jq '{strict, contexts, checks}'

gh api "repos/$OWNER/$REPO/rules/branches/$BRANCH" \
  --jq '[.[] | {type, parameters}]'
```

The final output should show:

- `protected: true`.
- Classic contexts include every active Codacy check for the chosen profile.
- Effective rules include every active Codacy check for the chosen profile.
- Strict status check policy is enabled in both classic protection and ruleset
  protection.

If Codacy still reports partial protection after GitHub shows the expected
state, compare Codacy's active gates against the required GitHub contexts:

- If coverage gates are enabled in Codacy, either configure real coverage upload
  and require the coverage contexts, or disable those coverage gates for a
  docs/config/template repository.
- If coverage gates are disabled in Codacy, require only the static analysis
  context and trigger a new pull request or reanalysis.

## Public-Safety Rules

- Never store `gh auth token`, Codacy API tokens, or private repository lists in
  this file.
- Keep repository names as placeholders unless documenting a public example.
- Do not paste raw `gh auth status` output if it contains token metadata.
- Prefer one-repository-at-a-time changes unless the user explicitly approves a
  bulk rollout.
