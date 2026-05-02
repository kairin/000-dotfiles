# Feature Specification: Optional Setup Integrations Menu

**Feature Branch**: `20260504-setup-optional-integrations`
**Created**: 2026-05-02
**Status**: Draft
**Input**: User description: "The `./setup` single entrypoint needs a non-critical optional menu that opens multiple secondary options. One secondary option is managing Codacy API access. The Codacy flow must preserve the current token behavior while fitting cleanly into the project setup flow."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover Optional Project Integrations (Priority: P1)

As a developer using the single `./setup` entrypoint for a project, I want non-critical integrations grouped behind one optional menu entry so the main project setup flow stays focused on agent docs, verification, and metadata.

**Why this priority**: This defines the menu shape. Without this, optional integrations compete with core setup actions and make the entrypoint harder to understand.

**Independent Test**: Start project setup for both an empty project and an existing project, verify the top-level project menu shows a general optional integrations entry, and verify choosing it opens a secondary menu without changing project files.

**Acceptance Scenarios**:

1. **Given** an empty project folder, **When** the user runs project setup, **Then** the top-level menu includes core bootstrap choices plus one general optional integrations entry.
2. **Given** an existing project folder, **When** the user runs project setup, **Then** the top-level menu includes verify/repair choices plus one general optional integrations entry.
3. **Given** the optional integrations submenu is open, **When** the user chooses Back, **Then** the user returns to the project setup menu without writing token, environment, or agent-doc changes; EOF or empty input exits safely without writing.

---

### User Story 2 - Manage Codacy API Access From The Optional Menu (Priority: P2)

As a developer who wants LLM agents to inspect Codacy information for a project, I want the optional integrations menu to guide me through repository-token or account-token setup without requiring me to remember environment variable names.

**Why this priority**: Codacy API setup is useful for some projects but not mandatory for every project, so it belongs in the optional submenu while still being easy to complete when needed.

**Independent Test**: Open the optional integrations menu, choose Codacy API management, complete repository-token setup, then repeat for account-token setup and verify the exposed variables, project metadata, and storage locations match the selected mode.

**Acceptance Scenarios**:

1. **Given** a project with a GitHub owner and repository, **When** the user chooses repository-token Codacy setup, **Then** the project environment exposes `CODACY_PROJECT_TOKEN`, `CODACY_ORGANIZATION_PROVIDER`, `CODACY_USERNAME`, and `CODACY_PROJECT_NAME`.
2. **Given** a project that should use account-token automation, **When** the user chooses account-token Codacy setup, **Then** the project environment exposes `CODACY_API_TOKEN`, `CODACY_ORGANIZATION_PROVIDER`, `CODACY_USERNAME`, and `CODACY_PROJECT_NAME`.
3. **Given** Codacy setup is in progress, **When** the user cancels before confirming a token mode, **Then** no token files or project environment files are created or changed.
4. **Given** Codacy setup is ready to write environment changes, **When** the user declines final confirmation, **Then** no token files, project environment files, or backups are created or changed.

---

### User Story 3 - Keep Secret Handling Safe And Agent-Discoverable (Priority: P3)

As a developer working with multiple LLM agents, I want generated project guidance to explain which Codacy variables may exist while preventing agents from reading, printing, or committing token values.

**Why this priority**: The feature is only useful if agents can discover safe access patterns, but secret exposure would make the setup unacceptable.

**Independent Test**: Complete Codacy setup, inspect project files and generated agent guidance, and verify token values are outside the repository while variable names and safety rules are visible.

**Acceptance Scenarios**:

1. **Given** a Codacy token has been configured, **When** project files are inspected, **Then** no project file contains the token value.
2. **Given** project agent docs have been generated, **When** an LLM agent reads them, **Then** it can identify the supported Codacy environment variables and the rule not to read or print local secret files.
3. **Given** the user reruns Codacy setup for the same project, **When** the same mode is configured again, **Then** the managed Codacy environment section is updated without duplicate blocks.

### Edge Cases

- The project has no GitHub remote or the remote cannot be parsed; the flow asks the user for owner and repository values.
- The project already has an `.envrc`; the flow preserves existing non-managed content and only adds the local environment loader when needed.
- The project already has an `.envrc.local`; the flow preserves unrelated content and replaces only the managed Codacy section.
- A token file already exists and the user leaves the token prompt blank; the flow keeps the existing token file and refreshes project metadata.
- A token file does not exist and the user leaves the token prompt blank; the flow does not write an active Codacy token export pointing to a missing token file and reports that a token is required before activation.
- The user cancels from the optional integrations menu or Codacy mode selection; no Codacy-specific writes occur.
- The project `.envrc` is protected or read-only; the flow either updates it safely with explicit feedback or reports what the user must fix before retrying.
- Owner or repository names contain characters that are unsafe for file names; the token storage name is normalized while preserving the displayed project metadata.
- `direnv` is not installed or not active; the flow still prepares files and tells the user what command or reload step remains.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project setup flow MUST remain reachable through the single `./setup` entrypoint for both empty and existing project folders.
- **FR-002**: The top-level project setup menu MUST group non-critical project integrations behind one general optional integrations entry instead of exposing Codacy directly at top level.
- **FR-003**: The optional integrations submenu MUST include a Codacy API management option and a clear cancel/back option.
- **FR-004**: Optional integrations MUST NOT block or displace the core project setup actions for verification, agent-doc bootstrap, Copilot instructions, or project metadata review.
- **FR-005**: Codacy API management MUST support a repository-token mode that exposes `CODACY_PROJECT_TOKEN` for the selected project.
- **FR-006**: Codacy API management MUST support an account-token mode that exposes `CODACY_API_TOKEN` for the selected project.
- **FR-007**: Both Codacy modes MUST expose `CODACY_ORGANIZATION_PROVIDER`, `CODACY_USERNAME`, and `CODACY_PROJECT_NAME` so agents can identify the target repository without guessing.
- **FR-008**: The Codacy flow MUST derive repository owner/name from the project when possible and ask the user to confirm or provide values before writing configuration.
- **FR-009**: Codacy token values MUST be stored outside the project repository in user-private storage and MUST NOT be written to project files, generated docs, command output, or test fixtures.
- **FR-010**: The project environment bridge MUST load project-local secret exports while keeping the primary project environment file free of secret values.
- **FR-011**: The project environment bridge MUST preserve existing user-managed content and update only the managed Codacy section on repeat runs.
- **FR-012**: The setup flow MUST avoid printing token values, including after successful configuration and in error output.
- **FR-013**: If the user selects Back from the optional integrations submenu, the flow MUST return to the project setup menu without Codacy-specific writes; if the user cancels Codacy mode selection, the flow MUST return to the optional integrations submenu without Codacy-specific writes; EOF or empty input MUST exit safely without writing.
- **FR-014**: Generated project agent guidance MUST document the supported Codacy variable names, their purpose, and the rule that agents must not read or print local secret files.
- **FR-015**: After successful Codacy setup, the flow MUST tell the user what remains to make the environment active in their shell.
- **FR-016**: Automated validation MUST cover the empty-project menu, existing-project menu, repository-token Codacy mode, account-token Codacy mode, cancel behavior, idempotent rerun behavior, and absence of token values in project files/output.
- **FR-017**: Optional integrations menu labels MUST be stable enough that existing users can predict where optional project tooling lives, even as more optional integrations are added later.
- **FR-018**: The recommendation/highlight behavior for the main project setup menu MUST continue to prioritize core setup state, not optional integrations that are not required for every user.
- **FR-019**: Before writing Codacy environment changes, the setup flow MUST show a preview of files and token-storage paths that would be created or changed without printing token values.
- **FR-020**: Codacy environment changes MUST require explicit final confirmation before writing `.envrc`, `.envrc.local`, or token files.
- **FR-021**: When an existing `.envrc` or `.envrc.local` would be modified, the setup flow MUST create a backup before replacement or mutation.
- **FR-022**: If no prior token file exists and the user leaves the token prompt blank, the setup flow MUST NOT write an active Codacy token export and MUST tell the user that a token is required before the environment can be activated.

### Key Entities

- **Project Setup Session**: The user's interaction with `./setup` for a specific project folder, including whether the project is empty or existing.
- **Optional Integration**: A non-critical project capability available from a secondary menu; Codacy API management is the first required integration.
- **Codacy Credential Mode**: The selected Codacy access pattern, either repository token or account token, with its required environment variables.
- **Project Repository Identity**: The provider, owner, and repository name that let agents know which Codacy project the token applies to.
- **Secret Storage Location**: A user-private location outside the project repository that stores token values.
- **Project Environment Bridge**: The project-level environment files that expose variable names in a shell session without committing token values.
- **Agent Guidance**: Generated project instructions that tell LLM agents which Codacy variables may be available and how to handle them safely.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of empty-project and existing-project setup sessions, optional integrations are reachable through one general submenu entry rather than a Codacy-specific top-level item.
- **SC-002**: A user can complete either Codacy credential mode from the project setup entrypoint in under 3 minutes after obtaining the token.
- **SC-003**: In automated checks, 0 token values appear in project files, generated agent docs, standard output, or error output after Codacy setup.
- **SC-004**: In automated checks, rerunning Codacy setup for the same project produces exactly one managed Codacy environment section.
- **SC-005**: In automated checks, cancelling from the optional integrations submenu or Codacy mode selection causes 0 Codacy-specific file changes.
- **SC-006**: In automated checks, all existing core project setup actions remain selectable and keep their expected behavior after the optional submenu is added.
- **SC-007**: In automated checks, the existing core project setup labels for bootstrap, Copilot, verify, repair, metadata, and exit remain unchanged; only the former direct Codacy top-level item is replaced by the generic optional integrations entry.
- **SC-008**: In automated checks, preview/cancel paths create 0 project environment files, token files, or backups.
- **SC-009**: In automated checks, modifying an existing `.envrc` or `.envrc.local` creates a backup before changing content.

## Assumptions

- Optional integrations belong in the project setup flow because Codacy API access is project-scoped rather than a global machine requirement.
- Codacy API management is the first optional integration, but the submenu should be named generically so future non-critical integrations can be added without another top-level menu change.
- Repository-token setup is the recommended Codacy mode for one project; account-token setup is available for users who need broader automation.
- The project may use direnv or another shell reload mechanism, but the setup flow only needs to prepare the environment bridge and explain the activation step.
- Existing generated project agent docs are the correct place to teach LLM agents about safe Codacy variable discovery.
