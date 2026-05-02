# Contract: `./setup` Machine Menu Recommendation

This contract defines the user-visible behavior for running `./setup` with no
arguments.

## Stable Menu Options

The machine setup menu must expose these option numbers:

```text
1. Install / update developer tools
2. Apply safe non-protected dotfiles
3. Show full technical details
4. Show tool and sign-in guidance
5. Exit without writing
```

Labels may include short clarifying suffixes, but the option purpose and number
must remain stable.

## Recommendation Rendering

Every menu render must include:

```text
Recommended next step: <N>. <label> - <reason>
```

Exactly one menu option must include:

```text
[recommended]
```

The recommendation must remain visible in plain captured output without color.

## State-To-Recommendation Contract

| Machine state | Recommended option | Required reason |
| --- | --- | --- |
| Status command fails or required status data is incomplete | 3 | Explain that details should be inspected because the audit is incomplete |
| Blocking audit or plan issues exist | 3 | Explain that details should be inspected before applying |
| One or more developer tools are missing or unverified | 1 | Explain that tools should be installed or updated first |
| Tools are present and safe dotfile or font actions are pending | 2 | Explain that safe non-protected setup changes are pending |
| Only manual sign-in guidance is pending | 4 | Explain that sign-in guidance is the useful next step |
| Only protected/manual items are pending | 3 | Explain that manual items need inspection and are not applied automatically |
| No useful setup action is pending | 5 | Explain that setup is current and no write action is needed |

## Fresh-Machine Session Contract

When option 1 is selected:

1. The tool install/update preview is shown.
2. The user is asked for confirmation before writes.
3. If the user confirms, the action runs and reports the result.
4. If the user declines, no tool changes are applied.
5. In both cases, `./setup` re-runs the machine summary and renders a fresh
   recommendation unless the process cannot continue.

## Safety Contract

- Option 2 still requires explicit apply confirmation before writes.
- Protected/manual files remain untouched unless separately and explicitly
  included by protected entry ID outside the safe menu path.
- Backups remain required before replacing differing files.
- Choosing a non-recommended option remains allowed.
