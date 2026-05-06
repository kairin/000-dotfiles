# Codacy Registration & Token Status

## The Discovery

During investigation of Codacy integration failures, the Codacy MCP tool was invoked to list repositories under the organization "kairin":

```
codacy_list_organization_repositories(provider=gh, org=kairin) → returned 0 repositories
```

Despite verification that the organization "kairin" is registered in Codacy (id 175394, joined 2025-08-05), the repository **000-dotfiles** does not appear in the platform's API response. This critical finding explains why the Codacy GitHub App continues to post checks on pull requests while the project remains completely invisible through the programmatic API.

## What This Means

The situation reveals a split between two Codacy integration pathways:

1. **GitHub App Integration (Working)**: The Codacy GitHub App successfully posts status checks and pull request reviews on commits. This functionality persists despite the registration issue.

2. **Platform API Integration (Broken)**: The project is either:
   - Not fully configured in Codacy's current platform infrastructure
   - Using an expired or invalidated `CODACY_PROJECT_TOKEN`
   - Not synchronized following a Codacy service migration, major platform update, or account restructuring

This dual failure mode is what makes it particularly insidious: surface-level PR checks pass, masking the underlying registration gap until you attempt to use API endpoints (coverage uploads, policy enforcement, programmatic analysis).

## CODACY_PROJECT_TOKEN Validity

The project token is:
- Stored in GitHub repository secrets
- Exported locally from `~/.codacy/<owner>-<repo>.project-token`
- Used by CI/CD systems for coverage upload and API communication

Evidence that the token may be stale or invalid:

1. **Coverage upload failures (HTTP 404)**: Repeated 404 responses from the coverage API endpoint suggest the token points to a deprecated or decomissioned API version, or the project is not found under that token's authorization scope.

2. **MCP 0-repos finding**: The organization-level API query with current credentials confirms the project is not accessible via the current authentication chain. If the token were valid and the project properly registered, it would appear in this list.

3. **Token age unknown**: Without access to the token's creation date or rotation history, there's no way to confirm whether it predates a Codacy platform migration, service incident, or account restructuring.

## Environment Variable State

The current environment exports the following related variables (derived from repository metadata and GitHub secrets):

```
CODACY_ORGANIZATION_PROVIDER=gh          # Derived from GITHUB_SERVER_URL
CODACY_USERNAME=kairin                   # Repository owner
CODACY_PROJECT_NAME=000-dotfiles         # Repository name
CODACY_PROJECT_TOKEN=<value from secrets> # Stored in GitHub, source of validity question
```

These values are **syntactically correct**, but correctness of form does not guarantee correctness of substance. The environment variables properly identify the project, but they cannot compensate for:
- A registration that never happened on the Codacy platform
- A project that was archived or migrated and not re-registered
- A token that is no longer accepted by the API (expired, revoked, or points to a defunct endpoint)

## What Needs to Happen

### Step 1: Verify Project Registration

Visit https://app.codacy.com and confirm whether **kairin/000-dotfiles** appears in your organization's repository list. This is the ground truth check.

- If **present**: Skip to Step 3 (token validation).
- If **absent**: Proceed to Step 2 (manual registration).

### Step 2: Register the Project (If Missing)

If the project is not listed:

1. Navigate to **Add Repository** in the Codacy UI
2. Select **GitHub** as the source
3. Search for or select **kairin/000-dotfiles**
4. Complete the initial setup flow

This step reconnects the project to Codacy's current platform and ensures it appears in API queries.

### Step 3: Generate or Verify CODACY_PROJECT_TOKEN

Once the project is confirmed present:

1. Open the project in Codacy
2. Navigate to **Project Settings** → **Integrations** or **API**
3. Look for the **Project API Token** section (not account-level tokens)
4. If no token exists, generate one
5. If a token exists, note its creation date to determine if it predates known Codacy incidents

**Important**: This token must be **project-level**, not account-level. Account tokens have different scopes and may not grant the necessary permissions for coverage upload and status checks.

### Step 4: Update GitHub Secrets

Once a valid project token is obtained:

1. Navigate to your repository's GitHub settings → **Secrets and variables** → **Actions**
2. Update (or create) the `CODACY_PROJECT_TOKEN` secret with the new token
3. Ensure no other CI/CD systems are caching an older version

The token should be available in the environment for CI workflows immediately after update.

### Step 5: Use the Automated Local Setup (Optional)

The dotfiles repository includes an experimental repair subcommand (from PR #198):

```bash
./setup repair-codacy-env
```

This subcommand attempts to automate the local token export and credential setup based on GitHub secrets. It can be used after Step 4 to verify the token is properly available in local shell environments.

## Connection Between Issues

The deprecated API endpoint failures (10+ 404 errors across coverage uploads) and the stale project registration are **symptoms of the same root cause**, not separate bugs:

1. **Old API endpoint would never validate the token anyway** if the project is not recognized by the platform. The 404 responses are correct behavior — they're saying "we don't know this project."

2. **The project registration gap explains coverage upload failure**: Without the project in the platform's registry, any token (new or old) will be rejected at the authorization layer before it even reaches the deprecated endpoint.

3. **These are related symptoms of platform migration or account restructuring**: If Codacy underwent a migration (e.g., consolidating old instances, sunsetting legacy APIs, restructuring organization hierarchies), both the project registration and the token's API version could become stale in tandem.

Fixing one issue in isolation (e.g., getting a new token without re-registering the project) will not resolve the coverage upload failures. Both the registration and the token must be addressed together.

## Summary

| Item | Status | Action |
|------|--------|--------|
| Project registered in Codacy | ❌ Not confirmed | Verify at https://app.codacy.com, register if missing |
| CODACY_PROJECT_TOKEN validity | ❓ Unknown | Check token creation date, generate new if stale |
| Environment variables (naming) | ✓ Correct | No change needed |
| GitHub App checks | ✓ Working | No action required (separate pathway) |
| Coverage upload API | ❌ 404 errors | Will resolve once project and token are valid |
| CI/CD integration | ❌ Blocked | Unblock after Steps 1–4 complete |
