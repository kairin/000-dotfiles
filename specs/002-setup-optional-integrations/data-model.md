# Data Model: Optional Setup Integrations Menu

## Project Setup Session

Represents one `./setup /path/to/project` interaction.

Fields:

- `project_path`: target project folder.
- `project_state`: `empty` or `existing`.
- `metadata_path`: resolved project metadata file.
- `top_level_choice`: selected project setup menu action.
- `optional_choice`: selected optional integration action when the submenu is opened.

Validation rules:

- `project_path` must exist before project setup continues.
- Core project actions remain available regardless of optional integration state.
- Optional integration cancellation must not modify project files.

## Optional Integration

Represents a non-critical project capability reachable from the secondary menu.

Fields:

- `id`: stable identifier, initially `codacy`.
- `label`: user-facing menu label.
- `criticality`: `optional`.
- `status`: `available`, `configured`, `cancelled`, or `failed`.

Validation rules:

- Optional integrations do not receive the main project menu recommendation by default.
- Optional integration labels must be generic enough to support future additions.

## Codacy Credential Mode

Represents the selected Codacy access pattern.

Fields:

- `mode`: `repository_token` or `account_token`.
- `token_variable`: `CODACY_PROJECT_TOKEN` or `CODACY_API_TOKEN`.
- `metadata_variables`: `CODACY_ORGANIZATION_PROVIDER`, `CODACY_USERNAME`, `CODACY_PROJECT_NAME`.
- `token_file`: user-private file path outside the project repository.

Validation rules:

- `repository_token` exposes `CODACY_PROJECT_TOKEN`.
- `account_token` exposes `CODACY_API_TOKEN`.
- Both modes expose repository identity metadata.
- Token values must never be rendered into project files or output.

## Project Repository Identity

Represents the Codacy target repository.

Fields:

- `provider`: expected provider code, normally `gh`.
- `owner`: GitHub user or organization.
- `repository`: repository name.
- `source`: detected from remote or user-provided.

Validation rules:

- Owner and repository must be confirmed before writing configuration.
- If detection fails, user-provided values are required.
- File-safe token storage names may be normalized, but displayed metadata must preserve the confirmed values.

## Secret Storage Location

Represents where token values live outside the repository.

Fields:

- `path`: user-private token file path.
- `mode`: intended file permission state.
- `exists_before_setup`: whether a prior token file exists.
- `updated`: whether the current run wrote a new value.

Validation rules:

- Token files are outside `project_path`.
- Blank token input keeps an existing token file.
- Blank token input with no existing token file results in guidance, not a project file containing a token.

## Project Environment Bridge

Represents project files that expose environment variables without storing token values.

Fields:

- `primary_env_file`: project `.envrc`.
- `local_env_file`: project `.envrc.local`.
- `managed_section`: Codacy-delimited export block.
- `loader_present`: whether the primary file loads the local file.

Validation rules:

- Primary environment file contains no token values.
- Local environment file contains no token values when the token is stored in `~/.codacy/`.
- Existing non-managed local content is preserved.
- Repeat setup produces exactly one managed Codacy section.

## Agent Guidance

Represents generated instructions for LLM agents.

Fields:

- `document`: generated project `AGENTS.md`.
- `supported_variables`: Codacy environment variables that agents may check.
- `secret_rules`: rules for not reading, printing, or committing token values.

Validation rules:

- Guidance includes variable names and purpose.
- Guidance forbids reading or printing local secret files.
- Guidance contains no actual token value.
