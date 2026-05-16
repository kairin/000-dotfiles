# Feature Specification: Setup Menu Recommendation Guidance

> **Spec status (2026-05-17): SUPERSEDED-BY-CODE.** Implementation
> shipped. Canonical reference: `dotfiles_tools/machine_summary.py`
> (`render_machine_summary` at line 23, `_recommendation_for_auth_guidance`
> at line 132). The `tasks.md` checklist in this directory is stale; do
> not update the checkboxes. Architectural context lives in
> [../../ARCHITECTURE.md#design-history](../../ARCHITECTURE.md#design-history).

**Feature Branch**: `20260503-setup-menu-recommendation`
**Created**: 2026-05-02
**Status**: Draft
**Input**: User description: "Review the current implementation, the ./setup menu is supposed to provide the recommendation highlighting which step should be used depending on the user's existing system status, this is to minimise guess work. However, I don't think I saw this highlight of the menu item to guide me. Identify how it should be done, think through the process and expected flow of using ./setup and identify the areas on how to implement it. Take reference to all documentation so that this is grounded requirement."

## Grounding Context

The README and getting-started guide promise that `./setup` audits the machine,
shows a stable five-option menu, and marks the option that fits the current
machine state with `[recommended]`. They describe a fresh-machine flow where
option 1 is recommended while developer tools are missing, then the menu
returns and option 2 is recommended after tools are installed. They also
describe an existing-machine flow where option 2 is recommended when safe
dotfile or font changes are pending.

The current behavior already has a recommendation concept, but the user-visible
experience needs to make the recommendation unmistakable, keep the summary and
menu consistent, and cover every common machine state so users do not have to
infer the next step from raw status details.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See The Recommended Next Step (Priority: P1)

A maintainer runs `./setup` on a machine and wants the menu to clearly identify
which action to choose next, so setup can proceed without guessing from the
status summary.

**Why this priority**: The recommendation is the primary navigation aid for the
interactive setup flow and is explicitly promised in user-facing documentation.

**Independent Test**: Can be tested by running the setup flow against simulated
machine states and verifying that exactly one visible recommendation appears,
with a reason that matches the audited state.

**Acceptance Scenarios**:

1. **Given** one or more developer tools are missing, **When** the maintainer
   reaches the machine setup menu, **Then** option 1 is visibly marked as the
   recommended option and the menu explains that tool installation or update is
   the next step.
2. **Given** developer tools are present and safe non-protected dotfile or font
   changes are pending, **When** the maintainer reaches the machine setup menu,
   **Then** option 2 is visibly marked as the recommended option and the menu
   explains that safe setup changes are pending.
3. **Given** blocking setup issues are present, **When** the maintainer reaches
   the machine setup menu, **Then** the recommendation guides the maintainer to
   inspect details before applying changes and the blocking reason remains
   visible.
4. **Given** the machine state cannot be fully evaluated because a status
   command fails, **When** the maintainer reaches the machine setup menu,
   **Then** option 3 is recommended and the menu explains that the audit is
   incomplete.
5. **Given** no tool, safe dotfile, font, blocker, or auth-guidance action is
   pending, **When** the maintainer reaches the machine setup menu, **Then** the
   menu clearly states that setup is current and recommends exiting without
   writing.

---

### User Story 2 - Follow The Fresh-Machine Flow (Priority: P1)

A maintainer sets up a new machine and wants the menu to move from installing
tools to applying configs in the same guided session, so they can complete setup
without restarting the command or rereading documentation.

**Why this priority**: The fresh-machine flow is the main quick-start path and
the README describes a two-step sequence: install tools first, then return to
apply safe dotfiles and fonts.

**Independent Test**: Can be tested with a simulated fresh machine where tools
are initially missing, then become present after the install action, and the
menu is shown again with an updated recommendation. It can also be tested when
tool installation is canceled or partial, and when a failed status audit falls
back to option 3.

**Acceptance Scenarios**:

1. **Given** tools are missing, **When** the maintainer chooses the recommended
   tool install action and confirms it, **Then** setup returns to an updated
   machine summary and menu after the action completes.
2. **Given** tool installation completed successfully, **When** the updated menu
   is shown, **Then** option 2 is recommended if safe dotfile or font changes
   remain.
3. **Given** the maintainer declines the tool install confirmation, **When** no
   tool changes are applied, **Then** setup returns to the menu with the same
   recommendation and no files are written.
4. **Given** the machine state cannot be fully evaluated or changes after a
   menu action, **When** the menu is re-rendered, **Then** the refreshed
   recommendation reflects the latest audited state instead of staying stale.

---

### User Story 3 - Keep Documentation And Menu Behavior Aligned (Priority: P2)

A maintainer reads the README or getting-started guide before running setup and
wants the actual menu to match the documented examples, so the documentation is
a reliable guide rather than a separate idealized flow.

**Why this priority**: The issue was discovered through a mismatch between the
expected documented guidance and what the maintainer noticed in the interactive
menu.

**Independent Test**: Can be tested by checking that documentation examples,
setup output examples, and automated menu-state checks use the same option
labels, recommendation wording, and state transitions.

**Acceptance Scenarios**:

1. **Given** the README describes a fresh-machine menu, **When** the setup menu
   is shown for missing tools, **Then** the option label and recommendation text
   match the documented intent.
2. **Given** the getting-started guide describes option 2 as highlighted after
   tools are installed, **When** setup returns after tool installation, **Then**
   the updated menu reflects that documented state.
3. **Given** a menu option label changes, **When** documentation and tests are
   reviewed, **Then** stale examples are identified before the change is
   accepted.

### Edge Cases

- The machine state cannot be fully evaluated because a status command fails.
- The terminal does not display colors or styling.
- Tool installation is canceled after the preview.
- Tool installation succeeds for some tools but leaves at least one tool
  missing or unverified.
- Safe dotfile or font actions are pending while protected/manual files are also
  present.
- Only protected/manual files are pending.
- Authentication guidance is available but no writable setup action is pending.
- The machine is fully current and choosing apply would perform no useful work.
- Blocking issues exist that would make apply stop before completing.
- The menu is re-rendered after an action and the audited state changed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The machine setup menu MUST display exactly one recommended option
  for every evaluated machine state.
- **FR-002**: The recommendation MUST be visible in plain text and MUST NOT rely
  only on color, cursor position, or terminal styling.
- **FR-003**: The recommendation MUST include both a menu-option marker and a
  short reason near the menu, so users understand why that option is next.
- **FR-004**: When developer tools are missing or unverified after an install
  attempt, the menu MUST recommend the tool install/update option.
- **FR-005**: When developer tools are present and safe non-protected dotfile or
  font actions are pending, the menu MUST recommend the safe apply option.
- **FR-006**: When blocking setup issues are present, the menu MUST recommend
  inspecting full details before applying changes.
- **FR-007**: When no setup, tool, font, blocker, or auth-guidance action is
  pending, the menu MUST recommend exiting without writing.
- **FR-008**: When only manual authentication guidance is pending, the menu MUST
  recommend viewing tool and sign-in guidance instead of applying changes.
- **FR-009**: The machine setup summary and the menu recommendation MUST agree
  about the next action; the summary MUST NOT describe only option 2 when a
  different option is recommended.
- **FR-010**: After the user completes or cancels the tool install/update
  action, setup MUST return to a refreshed machine summary and menu rather than
  ending the guided session.
- **FR-011**: The menu option numbers MUST remain stable across states: option 1
  for tool install/update, option 2 for safe apply, option 3 for full details,
  option 4 for tool/sign-in guidance, and option 5 for exit.
- **FR-012**: Choosing a non-recommended option MUST remain allowed; the
  recommendation guides the default path but does not block deliberate user
  choices.
- **FR-013**: Safe apply behavior MUST continue to require explicit confirmation
  and MUST preserve backup and protected-file behavior.
- **FR-014**: The recommendation decision MUST be derived from the same audited
  machine status that is shown to the user.
- **FR-015**: Documentation MUST describe the same recommendation states,
  option labels, and fresh-machine transition that users see in the setup menu.
- **FR-016**: Automated validation MUST cover at least the missing-tools,
  safe-changes-pending, blockers-present, auth-guidance-only, and fully-current
  menu states.
- **FR-017**: When required status data cannot be collected or the machine
  state is incomplete, the menu MUST recommend option 3 and explain that full
  details should be inspected before applying changes.

### Key Entities

- **Machine Setup State**: The evaluated condition of the user's machine,
  including tool availability, safe writable changes, protected/manual items,
  blockers, font actions, and authentication guidance.
- **Recommended Option**: The single menu option that best matches the current
  machine setup state, including its option number, label, and reason.
- **Machine Setup Menu**: The stable five-option interactive menu shown by
  `./setup` for machine setup.
- **Guided Setup Session**: The sequence from status audit to menu choice, action
  preview, confirmation, action result, and any refreshed follow-up menu.
- **Documentation Example**: README or getting-started guidance that describes
  the expected menu labels, recommendation marker, and state transition.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated checks for missing tools, 100% of setup menu outputs
  mark option 1 as recommended and do not mark any other option as recommended.
- **SC-002**: In automated checks for pending safe dotfile or font changes with
  tools present, 100% of setup menu outputs mark option 2 as recommended and do
  not mark any other option as recommended.
- **SC-003**: In automated checks for blocking issues, 100% of setup menu
  outputs recommend inspecting full details before apply.
- **SC-004**: In automated checks for fully current machines, 100% of setup menu
  outputs state that no write action is needed and recommend exiting without
  writing.
- **SC-005**: In automated checks for auth-guidance-only machines, 100% of setup
  menu outputs recommend viewing tool and sign-in guidance.
- **SC-006**: In the fresh-machine flow, after a confirmed tool install action,
  setup shows a refreshed machine summary and menu in the same session in 100%
  of successful test runs.
- **SC-007**: Every recommendation is visible in plain captured output without
  relying on color or styling.
- **SC-008**: README and getting-started examples match the implemented menu
  option labels and recommendation states in all automated documentation checks.
- **SC-009**: In automated checks for incomplete or failed status audits, 100%
  of setup menu outputs recommend option 3 and include a reason that the audit
  is incomplete.

## Assumptions

- The scope is the machine setup flow shown by running `./setup` with no
  arguments; project-folder menus are out of scope for this feature.
- The five existing menu option numbers remain stable to preserve documented
  muscle memory.
- A recommendation may guide users to inspect details or exit when applying
  changes would be unsafe or unnecessary.
- Existing protected-file, backup, explicit-confirmation, and no-secret
  guarantees remain unchanged.
- Plain-text visibility is required even if terminal color is later added.
