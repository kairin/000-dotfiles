# Research: Optional Setup Integrations Menu

## Decision: Place Optional Integrations Behind A Project Submenu

**Rationale**: Codacy API access is project-scoped and useful only for some projects. Keeping it as a top-level project setup item makes it look as important as agent-doc bootstrap or verification. A generic optional integrations submenu keeps `./setup /path/to/project` as the single entrypoint while preventing non-critical features from crowding the primary flow.

**Alternatives considered**:

- Keep Codacy as a top-level project menu item: rejected because it over-promotes a non-critical capability.
- Move Codacy to a separate command: rejected because it fragments the single-entrypoint setup model.
- Put Codacy in the machine setup menu: rejected because token metadata and repository identity are project-specific.

## Decision: Keep Codacy As The First Optional Integration

**Rationale**: The user explicitly needs Codacy API setup, but the menu label should be future-proof. A submenu can start with Codacy and later accept other optional integrations without changing the top-level project flow again.

**Alternatives considered**:

- Name the top-level item "Codacy": rejected because the user clarified that this is not critical for everyone.
- Create many top-level optional items: rejected because it increases guesswork and weakens the main setup guidance.

## Decision: Support Repository Token And Account Token Modes

**Rationale**: Codacy uses repository tokens for per-repository coverage/reporting flows and account tokens for broader API access. The setup flow should ask which mode the user wants and expose the expected environment variables for that mode.

**Alternatives considered**:

- Repository token only: rejected because the user has account API access and may need broader Codacy inspection.
- Account token only: rejected because repository tokens are safer and more scoped for most projects.

## Decision: Store Token Values Outside The Repository

**Rationale**: The constitution forbids tracked secrets. Token values should live in user-private storage such as `~/.codacy/`, while project files contain only commands that read those token files. This keeps LLM agents able to discover variable names without seeing token values.

**Alternatives considered**:

- Store direct exports in `.envrc.local`: rejected because it places secret values next to the project and makes accidental reading/printing more likely.
- Store tokens in tracked project docs: rejected by the secret-free constitution gate.
- Require GitHub Actions secrets only: rejected because the requested use case is local LLM access to Codacy data.

## Decision: Use A Managed Environment Section For Idempotency

**Rationale**: Repeat setup should update Codacy metadata without duplicating exports or deleting unrelated user content. A clearly delimited managed Codacy section gives the setup flow a bounded update target.

**Alternatives considered**:

- Rewrite the entire local environment file: rejected because it risks user-managed content loss.
- Append on every run: rejected because duplicate exports make behavior harder to reason about.

## Decision: Validate Through Existing Setup And Docs Tests

**Rationale**: The behavior is user-facing menu text, local file creation, and generated guidance. Existing setup-script and docs test surfaces can validate the flow without adding new dependencies.

**Alternatives considered**:

- Add a new test runner or shell testing framework: rejected because the repo currently uses standard-library unittest and shell subprocess tests.
- Rely on manual testing only: rejected because token-safety and menu stability need automated regression coverage.
