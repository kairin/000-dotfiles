# Research: Setup Menu Recommendation Guidance

## Decision: Use One Structured Recommendation Decision

The menu recommendation will be represented as a single structured decision
containing option number, label, reason, and state category. The machine summary
and shell menu should render this same decision instead of independently
recomputing recommendation text.

**Rationale**: The current behavior can tag option 1 or option 2, but the
summary still frames everything as "Option 2 will". A single decision prevents
the summary and menu from disagreeing and makes the behavior easier to test.

**Alternatives considered**:

- Keep Bash-only branching. Rejected because it duplicates the state decision
  outside the audited Python report path.
- Only change documentation. Rejected because the reported user issue is an
  interactive guidance gap, not just a documentation wording issue.

## Decision: Recommendation Must Be Plain Text Plus Reason

The menu will keep a visible `[recommended]` marker on exactly one option and
also print a nearby "Recommended next step" reason line before the prompt.
Color or styling may be added later, but plain text remains the contract.

**Rationale**: Captured output, low-color terminals, and screen readers need the
recommendation to be visible without styling. A reason reduces guesswork when
the recommended option is details, auth guidance, or exit.

**Alternatives considered**:

- Use color-only highlighting. Rejected because some terminals and captured
  test output would not show it.
- Use only `[recommended]`. Rejected because it does not explain why an option
  is recommended.

## Decision: Recommendation Priority Order

Recommendation precedence will be:

1. Blocking audit/plan issues: recommend option 3, full details.
2. Missing or unverified developer tools: recommend option 1, install/update tools.
3. Safe non-protected dotfile or font actions: recommend option 2, apply safe changes.
4. Auth-guidance-only state: recommend option 4, tool/sign-in guidance.
5. Protected/manual-only state: recommend option 3, full details.
6. Fully current state: recommend option 5, exit without writing.

**Rationale**: Blocking issues must be inspected before writes. Missing tools
come before config apply in the documented fresh-machine flow. Safe writes
remain the main configured-machine action. Auth and protected/manual states need
guidance but should not imply a safe apply will help. Fully current systems
should not be nudged into a no-op write path.

**Alternatives considered**:

- Always recommend option 2 when tools are present. Rejected because it
  misguides users in blocker, auth-only, protected-only, and fully current
  states.
- Recommend exit for protected/manual-only states. Rejected because the user
  may need to inspect why items were not applied.

## Decision: Refresh Menu After Tool Install/Update

After option 1 completes or is canceled, `./setup` will return to a refreshed
machine summary and menu instead of ending the guided session.

**Rationale**: README and getting-started documentation describe a fresh-machine
flow where the menu returns and option 2 becomes recommended after tools are
installed. Re-rendering also handles partial install results and cancellation
without guessing stale state.

**Alternatives considered**:

- End after tool install and require users to rerun `./setup`. Rejected because
  it contradicts documented flow and increases guesswork.
- Blindly show option 2 after tool install. Rejected because partial failures
  or unverified tools may mean option 1 remains the right recommendation.

## Decision: Keep Project Menus Out Of Scope

This feature covers only the machine setup menu shown by `./setup` with no
arguments.

**Rationale**: The reported gap and documentation references are specifically
about the machine setup flow and its five-option menu. Project-folder menus have
different choices and state checks.

**Alternatives considered**:

- Redesign all interactive menus. Rejected because it expands scope beyond the
  grounded requirement.
