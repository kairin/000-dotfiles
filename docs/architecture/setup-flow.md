# Setup Flow

`./setup` inspects the machine, prints a recommendation-aware summary, and then shows the stable 5-option menu.
The recommended option changes with the audited state, but the option numbers stay fixed so the menu remains learnable.

## Core Flow

```mermaid
flowchart TD
  A[Run ./setup] --> B[Audit machine state]
  B --> C[Print summary with recommended option]
  C --> D[Show 5-option menu]
  D --> E{User choice}
  E -->|1| F[Preview and apply tool updates]
  E -->|2| G[Apply safe dotfiles and font recipes]
  E -->|3| H[Show full technical details]
  E -->|4| I[Show tool and sign-in guidance]
  E -->|5| J[Exit without writing]
  F --> K[Refresh summary and menu]
  G --> J
  H --> D
  I --> D
  K --> C
```

## Recommendation States

- `1` - missing or unverified developer tools
- `2` - safe non-protected dotfiles or font work is pending
- `3` - audit failure, blockers, or manual-only work needs inspection
- `4` - tool and sign-in guidance is the useful next step
- `5` - the machine is already current

## Why The Refresh Matters

Option 1 can change the machine state before the user returns to the menu.
The wrapper refreshes the summary after cancel or completion so the recommended option does not stay stale.
