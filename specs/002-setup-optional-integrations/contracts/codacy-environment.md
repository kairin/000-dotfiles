# Contract: Codacy Environment Management

## Entry Point

User path:

```text
./setup /path/to/project
-> Optional integrations and APIs
-> Manage Codacy API access
```

## Credential Modes

### Repository Token Mode

Required project environment variables:

```text
CODACY_PROJECT_TOKEN
CODACY_ORGANIZATION_PROVIDER
CODACY_USERNAME
CODACY_PROJECT_NAME
```

Required behavior:

- Token value is stored outside the project repository.
- Project environment exports `CODACY_PROJECT_TOKEN` by reading the external token file.
- Provider is `gh` unless the user confirms another supported provider in a future feature.
- Owner and repository are detected from the project when possible and confirmed by the user.

### Account Token Mode

Required project environment variables:

```text
CODACY_API_TOKEN
CODACY_ORGANIZATION_PROVIDER
CODACY_USERNAME
CODACY_PROJECT_NAME
```

Required behavior:

- Token value is stored outside the project repository.
- Project environment exports `CODACY_API_TOKEN` by reading the external token file.
- Owner and repository are detected from the project when possible and confirmed by the user.

## File Contract

Project files:

```text
.envrc
.envrc.local
```

User-private files:

```text
~/.codacy/<owner>-<repo>.project-token
~/.codacy/account-token
```

Rules:

- `.envrc` contains only a loader for `.envrc.local` and non-secret user content.
- `.envrc.local` contains a managed Codacy section with exports that read user-private token files.
- Token values are not written to `.envrc`, `.envrc.local`, generated docs, command output, or tests.
- Before writing, the flow shows a token-free preview of project files and user-private token paths that would be created or changed.
- Writing requires explicit final confirmation after preview.
- Existing `.envrc` and `.envrc.local` files are backed up before mutation.
- Existing non-managed `.envrc.local` content is preserved.
- Repeat setup replaces exactly the managed Codacy section.
- `.envrc` is made read-only after setup when it is created or changed by setup.
- `.envrc.local` is local and permission-restricted.
- If no token file exists and token input is blank, the flow does not write an active token export that points to a missing file and reports that a token is required before activation.

## User Feedback Contract

Successful setup output includes:

- which credential mode was configured
- where the token is stored, without printing token value
- which project environment files were prepared
- the remaining activation step for the user's shell

Failure output includes:

- what could not be prepared
- what the user must fix before retrying
- no token value
