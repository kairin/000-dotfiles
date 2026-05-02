# Scaffold Flow

`./setup init` renders project agent docs from a project metadata file and then verifies the result.

## Flow

```mermaid
flowchart TD
  A[Run ./setup init] --> B{project-vars.json present?}
  B -->|Yes| C[Use the discovered vars file]
  B -->|No| D[Infer defaults from project files]
  D --> E[Persist or use inferred vars]
  C --> F[Run dotfiles_tools init-project]
  E --> F
  F --> G[Write AGENTS.md]
  F --> H[Write CLAUDE.md symlink]
  F --> I[Write GEMINI.md symlink]
  F --> J[Optional Copilot instructions]
  F --> K[Verify the rendered project docs]
```

## What Gets Generated

- `AGENTS.md` for shared project guidance
- `CLAUDE.md` and `GEMINI.md` as symlinks to `AGENTS.md`
- optional Copilot instructions when requested

## Default Inference

When no vars file is supplied, the wrapper infers defaults from common project files such as `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, and `Makefile`.
