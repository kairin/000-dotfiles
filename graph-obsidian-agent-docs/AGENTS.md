# {{PROJECT_NAME}} - AI Agent Guidelines

Single source of truth for LLM agents working in this repository. Replace every
`{{UPPER_SNAKE_CASE}}` marker before using this file in a project.

`CLAUDE.md` and `GEMINI.md` should point at this file when the project uses
multiple agent entrypoints. If a project cannot use symlinks, document the
sync process in `{{AGENT_DOC_SYNC_COMMAND_OR_POLICY}}`.

## Project Context

- Project name: `{{PROJECT_NAME}}`
- Repository path: `{{PROJECT_ROOT_PATH}}`
- Primary purpose: {{PROJECT_PURPOSE}}
- Product or package name: `{{PRODUCT_OR_PACKAGE_NAME}}`
- Primary languages/frameworks: {{PRIMARY_LANGUAGES_AND_FRAMEWORKS}}
- Runtime/toolchain manager: {{RUNTIME_OR_TOOLCHAIN_MANAGER}}
- Main source directories: {{MAIN_SOURCE_DIRECTORIES}}
- Main documentation entrypoints: {{MAIN_DOCUMENTATION_ENTRYPOINTS}}
- Primary configuration files: {{PRIMARY_CONFIGURATION_FILES}}

<!-- SPECKIT START -->
For additional context about technologies, project structure, shell commands,
and current implementation scope, read the current plan:
`{{CURRENT_SPEC_OR_PLAN_PATH}}`
<!-- SPECKIT END -->

## Setup And Local Commands

- Install dependencies: `{{INSTALL_DEPENDENCIES_COMMAND}}`
- Run the app or service: `{{RUN_APP_COMMAND}}`
- Run the narrowest useful tests: `{{RUN_NARROW_TESTS_COMMAND}}`
- Run the full verification suite: `{{RUN_FULL_VERIFICATION_COMMAND}}`
- Lint/typecheck/build: `{{RUN_LINT_TYPECHECK_BUILD_COMMANDS}}`
- Regenerate docs, skills, or generated files: `{{REGENERATION_COMMANDS_OR_NONE}}`
- Seed or refresh project documentation: `{{PROJECT_DOC_SEED_COMMAND_OR_NONE}}`

Prefer the commands above over ad hoc alternatives unless the repository itself
shows that the command has changed. If a command fails because local setup is
missing, report the exact missing prerequisite and the least invasive fix.

## Project Boundaries

- Data scope: {{DATA_SCOPE_BOUNDARY}}
- External services: {{EXTERNAL_SERVICE_POLICY}}
- Cost/network policy: {{COST_OR_NETWORK_CONSENT_POLICY}}
- Generated artifacts: {{GENERATED_ARTIFACT_POLICY}}
- Local state that must not be overwritten: {{LOCAL_STATE_PROTECTION_POLICY}}
- Secrets and credentials: never print, commit, or move real secrets. Use
  `{{SECRET_PLACEHOLDER_FORMAT}}` for examples.

If a tool can operate globally or across multiple projects, choose the
project-scoped configuration first. If project scoping is unavailable, stop and
ask before running the tool.

## Retrieval And Knowledge Tools

Use the cheapest, most local, and most accurately scoped retrieval path that
can answer the request.

| Question shape | Preferred route |
|---|---|
| Exact text, file, symbol, or single-document lookup | {{LOCAL_SEARCH_OR_INDEX_TOOL}} |
| Project-scoped semantic lookup | {{PROJECT_SCOPED_SEMANTIC_TOOL_OR_NONE}} |
| Cross-document synthesis or global themes | {{SYNTHESIS_TOOL_OR_NONE}} |
| Ambiguous request with multiple possible tools | Ask the user to choose the scope before spending tokens or using remote services |

Project-scoped knowledge configuration:

- Index name: `{{PROJECT_INDEX_NAME_OR_NONE}}`
- Collection/workspace name: `{{PROJECT_COLLECTION_OR_WORKSPACE_NAME_OR_NONE}}`
- Status/check command: `{{PROJECT_INDEX_STATUS_COMMAND_OR_NONE}}`
- Rebuild command: `{{PROJECT_INDEX_REBUILD_COMMAND_OR_NONE}}`

Do not use shared/default indexes for multi-project work unless the user
explicitly approves that boundary.

## Agent Working Rules

- `AGENTS.md` is the canonical, committed source of truth for repo agent
  behavior.
- Keep `CLAUDE.md` and `GEMINI.md` as symlinks or synchronized derivatives of
  `AGENTS.md` according to `{{AGENT_DOC_SYNC_COMMAND_OR_POLICY}}`; do not edit
  generated derivatives directly.
- `{{AGENT_BEHAVIOR_BASELINE_PATH_OR_NONE}}` is the baseline for expected agent
  behavior. Keep it unchanged unless the user explicitly asks to update the
  baseline.
- Think before coding: state assumptions, surface tradeoffs, and ask when the
  request has multiple plausible interpretations.
- Simplicity first: write the minimum code or documentation that solves the
  request; avoid speculative features, abstractions, and configurability.
- Surgical changes: touch only the files and lines needed for the task,
  preserve existing style, and do not refactor or delete unrelated code.
- Clean up only changes you introduced; mention unrelated dead code or stale
  docs instead of removing them unless asked.
- Define success criteria for non-trivial work, then verify with the narrowest
  useful checks before reporting done.
- Keep every changed line traceable to the user's request and this project's
  stated boundaries: {{PROJECT_SPECIFIC_BOUNDARY_SUMMARY}}.

## Protected Files

Read these files freely for context, but do not modify them unless the user
gives an explicit per-file directive.

| File | Why protected |
|---|---|
| `{{PROTECTED_FILE_1}}` | {{PROTECTED_FILE_1_REASON}} |
| `{{PROTECTED_FILE_2_OR_NONE}}` | {{PROTECTED_FILE_2_REASON_OR_NONE}} |
| `{{PROTECTED_FILE_3_OR_NONE}}` | {{PROTECTED_FILE_3_REASON_OR_NONE}} |

If a task seems to require touching a protected file, stop and ask. Use
`git show origin/main:<file>` as the authoritative original when available.

## Repository Structure

```text
{{REPO_TREE_SUMMARY}}
```

Update this section when adding or removing top-level project areas that future
agents need to understand.

## Coding And Documentation Conventions

- Follow the existing style in nearby files before introducing a new pattern.
- Prefer repository-local helpers, scripts, and abstractions over new tooling.
- Keep user-facing text accurate to the current app behavior and setup flow.
- Document durable workflows in the repo instead of leaving them only in chat.
- Do not silently change public APIs, command names, environment variables, or
  file formats. Call out compatibility implications before making the change.
- For templates, placeholders use `{{UPPER_SNAKE_CASE}}` and must be replaced
  before use.

## Verification

Before reporting done, run the narrowest useful checks for the files changed.

Suggested verification order:

1. `{{FORMAT_OR_STATIC_CHECK_COMMAND_OR_NONE}}`
2. `{{NARROW_TEST_COMMAND_OR_NONE}}`
3. `{{FULL_TEST_COMMAND_OR_NONE}}`
4. `{{BUILD_COMMAND_OR_NONE}}`
5. `{{DOC_OR_GENERATED_CONTENT_CHECK_COMMAND_OR_NONE}}`

If a check cannot be run, say why and identify the residual risk.

## Git And Publishing

- Check `git status --short` before editing and before final reporting.
- Stage specific files only; do not use `git add -A`.
- Review `git diff --staged` before committing, especially for secrets,
  generated files, personal paths, and unrelated edits.
- Keep commits scoped to the user's requested change.
- Do not overwrite, revert, or clean up user changes unless explicitly asked.
- Publishing workflow: {{PUBLISHING_WORKFLOW_OR_NONE}}.

## Project-Specific Workflows

Replace this section with the project's actual reusable workflows, synced skill
blocks, or agent procedures.

<!-- BEGIN-PROJECT-SPECIFIC-WORKFLOWS -->

{{PROJECT_SPECIFIC_WORKFLOWS_OR_SYNCED_SKILLS_BLOCK}}

<!-- END-PROJECT-SPECIFIC-WORKFLOWS -->

## Placeholder Checklist

Before using this template in a project, replace these marker groups:

- Identity: `{{PROJECT_NAME}}`, `{{PROJECT_ROOT_PATH}}`,
  `{{PROJECT_PURPOSE}}`, `{{PRODUCT_OR_PACKAGE_NAME}}`
- Tooling: `{{PRIMARY_LANGUAGES_AND_FRAMEWORKS}}`,
  `{{RUNTIME_OR_TOOLCHAIN_MANAGER}}`, `{{INSTALL_DEPENDENCIES_COMMAND}}`,
  `{{RUN_APP_COMMAND}}`
- Verification: `{{RUN_NARROW_TESTS_COMMAND}}`,
  `{{RUN_FULL_VERIFICATION_COMMAND}}`,
  `{{RUN_LINT_TYPECHECK_BUILD_COMMANDS}}`
- Boundaries: `{{DATA_SCOPE_BOUNDARY}}`,
  `{{EXTERNAL_SERVICE_POLICY}}`, `{{COST_OR_NETWORK_CONSENT_POLICY}}`,
  `{{LOCAL_STATE_PROTECTION_POLICY}}`
- Agent docs: `{{AGENT_DOC_SYNC_COMMAND_OR_POLICY}}`,
  `{{AGENT_BEHAVIOR_BASELINE_PATH_OR_NONE}}`
- Repository details: `{{REPO_TREE_SUMMARY}}`,
  `{{PROTECTED_FILE_1}}`, `{{PROJECT_SPECIFIC_WORKFLOWS_OR_SYNCED_SKILLS_BLOCK}}`
