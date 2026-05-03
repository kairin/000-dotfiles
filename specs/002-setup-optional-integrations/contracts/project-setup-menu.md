# Contract: Project Setup Menu

## Entry Point

Command:

```bash
./setup /path/to/project
```

The command remains the single entrypoint for project setup. It detects whether the project is empty or existing, resolves project metadata, and displays the appropriate top-level project menu.

## Empty Project Top-Level Menu

Required visible choices:

1. Bootstrap `AGENTS.md` plus `CLAUDE.md`/`GEMINI.md` symlinks.
2. Bootstrap agent docs plus Copilot instructions.
3. Open optional integrations and APIs.
4. Show inferred project metadata.
5. Exit.

Contract rules:

- The optional integrations choice is generic; it must not be Codacy-specific.
- Choosing metadata must not write agent docs or integration files.
- Choosing exit must not write agent docs or integration files.

## Existing Project Top-Level Menu

Required visible choices:

1. Verify agent docs.
2. Repair/bootstrap `AGENTS.md` plus `CLAUDE.md`/`GEMINI.md` symlinks.
3. Add or refresh Copilot instructions.
4. Open optional integrations and APIs.
5. Show project metadata.
6. Exit.

Contract rules:

- Verification remains read-only.
- Optional integrations do not replace verification or repair actions.
- Existing project verification may run before the menu as today, but optional integrations remain user-selected.

## Optional Integrations Submenu

Required visible choices:

1. Manage Codacy API access.
2. Back to project setup.

Contract rules:

- Back returns to the project setup menu without Codacy-specific writes.
- EOF or empty input exits safely without Codacy-specific writes.
- The submenu may grow with more optional integrations later without changing the top-level project menu shape.
- Optional integrations are not required to complete project agent-doc setup.

## Recommendation Behavior

The top-level project setup recommendation, if displayed, continues to reflect core setup state. Optional integrations must not be highlighted as required merely because they are unconfigured.

## Cancellation Contract

Back/cancel behavior is deterministic:

- Back from the optional integrations submenu returns to the project setup menu.
- Cancel from Codacy credential mode selection returns to the optional integrations submenu.
- EOF or empty input exits safely.

Cancellation before final confirmation causes no Codacy-specific writes:

- no token file creation
- no `.envrc` change
- no `.envrc.local` change
- no agent-doc change
- no backup creation
