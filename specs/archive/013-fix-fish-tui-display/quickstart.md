# Quickstart: Fix Fish Shell TUI Display

**Date**: 2026-01-31
**Feature**: 003-fix-fish-tui-display

## Prerequisites

- Go 1.23+ installed
- Repository cloned with TUI code

## Quick Fix

### 1. Edit the file

```bash
# Open the file
vim tui/internal/ui/model.go
# Or use your preferred editor
```

### 2. Find getTableTools() (~line 1543)

```go
func (m Model) getTableTools() []*registry.Tool {
    allMain := registry.GetMainTools()
    tableTools := make([]*registry.Tool, 0, 3)  // Change to 4
    // Filter: only show nodejs, ai_tools, antigravity in table
    for _, tool := range allMain {
        if tool.ID == "nodejs" || tool.ID == "ai_tools" || tool.ID == "antigravity" {  // Add fish
            tableTools = append(tableTools, tool)
        }
    }
    return tableTools
}
```

### 3. Make the changes

1. Change capacity from `3` to `4`
2. Add `|| tool.ID == "fish"` to the condition

### 4. Verify

**For Users:**
```bash
./start.sh
```

**For Developers:**
```bash
cd tui && go run ./cmd/installer  # DEVELOPER ONLY
```

Fish should now appear in the main tools table.

## Expected Result

```
╭────────────────────────────────────────────────────────────────
│  APP                      STATUS         VERSION
│ ───────────────────────────────────────────────────────────────
│  Node.js                   INSTALLED     v25.5.0
│  Local AI Tools            INSTALLED     1/3 tools
│  Google Antigravity        INSTALLED     1.15.8
│  Fish + Fisher             NOT INSTALLED -           <-- NEW
╰────────────────────────────────────────────────────────────────
```
