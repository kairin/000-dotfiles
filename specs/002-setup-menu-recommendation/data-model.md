# Data Model: Setup Menu Recommendation Guidance

## Machine Setup State

Represents the audited status used to choose the next menu action.

Fields:

- `tool_status`: Summary of missing, installed, unverified, or unsupported
  developer tools.
- `safe_file_actions`: Count and labels of non-protected dotfile actions that
  can be applied with approval and backups.
- `font_actions`: Count and labels of font install/update actions.
- `protected_manual_items`: Count and reasons for protected/manual files that
  will not be applied automatically.
- `blockers`: Count and reasons for audit or plan failures that require
  inspection before writes.
- `auth_guidance_available`: Whether installed tools have manual sign-in
  guidance to show.
- `is_current`: Whether no useful setup action remains.

Validation rules:

- State must be derived from the same audit/plan data shown in the machine
  summary.
- Blocking issues must remain visible even when another action is recommended.
- Protected/manual items must not be counted as safe writable changes.

## Recommended Option

Represents the single next option highlighted in the machine menu.

Fields:

- `option_number`: One of `1`, `2`, `3`, `4`, or `5`.
- `label`: The stable menu label for the option.
- `reason`: Plain-language explanation for why this option is recommended.
- `state_category`: One of `blocked`, `tools_missing`, `safe_changes`,
  `auth_guidance`, `manual_only`, or `current`.

Validation rules:

- Exactly one recommendation must exist for each machine setup state.
- The option number must correspond to a visible stable menu option.
- The reason must be visible in plain captured output.

State transitions:

- `blocked` -> remains until blockers are fixed.
- `tools_missing` -> `safe_changes`, `auth_guidance`, `manual_only`, or
  `current` after tool install/update is re-audited.
- `safe_changes` -> `auth_guidance`, `manual_only`, or `current` after approved
  apply succeeds.
- `auth_guidance` -> `current` after the user completes manual sign-in outside
  setup, if no other actions remain.
- `manual_only` -> `current` only if protected/manual state is intentionally
  resolved outside the safe apply path.

## Machine Setup Menu

Represents the stable interactive menu shown by `./setup` with no arguments.

Fields:

- `options`: Five stable option labels.
- `recommended_option`: The single recommended option.
- `prompt`: The user input prompt.
- `non_writing_choices`: Choices that inspect or exit without writes.
- `write_choices`: Choices that still require explicit confirmation before
  writes.

Validation rules:

- Option numbers must remain stable across all states.
- Only the recommended option may include `[recommended]`.
- Non-recommended options remain selectable.
- Write choices must preserve existing confirmation, backup, and protected-file
  behavior.

## Guided Setup Session

Represents one interactive run of the machine setup flow.

Fields:

- `initial_state`: State before the first menu render.
- `selected_option`: User-selected menu option.
- `action_result`: Completed, canceled, failed, or no-op result.
- `refreshed_state`: State after a menu action that can change setup status.
- `next_recommendation`: Recommendation shown after refresh.

Validation rules:

- Tool install/update completion or cancellation must refresh state and return
  to the menu.
- Full details and auth guidance may return to the menu after display.
- Exit must not write files.

## Documentation Example

Represents README or getting-started content that documents expected menu
behavior.

Fields:

- `document_path`: Documentation file path.
- `scenario`: Fresh machine, configured machine, current machine, or issue flow.
- `expected_recommendation`: Option number and reason described by the example.
- `menu_labels`: Stable option labels shown in the example.

Validation rules:

- Documentation examples must match current option labels.
- Fresh-machine documentation must show option 1 first, then option 2 after
  tool installation.
- Documentation must not imply protected/manual files are applied
  automatically.
