# Quickstart: Fix TUI Bugs

**Feature**: 002-fix-tui-bugs
**Date**: 2026-01-29

## Overview

This document provides verification steps for testing the 5 TUI bug fixes.

## Prerequisites

- Go 1.23+ installed
- Terminal emulator (Ghostty recommended)
- Repository cloned with `002-fix-tui-bugs` branch

## Build & Run

**For Users:**
```bash
./start.sh
```

**For Developers:**
```bash
cd tui && go run ./cmd/installer  # DEVELOPER ONLY
```

The `start.sh` script automatically:
- Detects if source code changed and rebuilds
- Installs Go if not present
- Builds the binary on first run

## Verification Test Cases

### Test 1: Terminal State Restoration (Bug #197)

**Purpose**: Verify copy/paste works after TUI exit

**Steps**:
1. Open a fresh terminal
2. Copy some text to clipboard (e.g., "hello world")
3. Run TUI: `./start.sh` (or `cd tui && go run ./cmd/installer` for developers)
4. Navigate around the TUI (Dashboard, Extras, etc.)
5. Exit TUI with `q`
6. Try to paste with Ctrl+V

**Expected**: Pasted text appears correctly

**Additional Test**:
1. Run TUI
2. Press Ctrl+C to force quit
3. Try to paste with Ctrl+V

**Expected**: Pasted text still works

---

### Test 2: Dashboard Auto-Refresh (Bug #199)

**Purpose**: Verify dashboard refreshes after Update All

**Prerequisites**: At least one tool shows "Update available"

**Steps**:
1. Run TUI
2. Dashboard should show "X update available"
3. Select "Update All" from menu
4. Confirm the update in BatchPreview
5. Wait for all updates to complete
6. Observe dashboard after return

**Expected**:
- Loading spinner appears briefly
- Dashboard shows updated status (no pending updates)
- No need to press 'r' to refresh

---

### Test 3: ESC Navigation After Install (Bug #200)

**Purpose**: Verify ESC returns to tool detail after install

**Steps**:
1. Run TUI
2. Navigate to Extras → Select a tool (e.g., Fastfetch)
3. ViewToolDetail appears
4. Select "Install" or "Uninstall"
5. Wait for operation to complete
6. Press ESC

**Expected**: Returns to ViewToolDetail showing updated status

**Continue**:
7. Press ESC again

**Expected**: Returns to Extras menu

---

### Test 4: Multi-Line Location Display (Bug #201)

**Purpose**: Verify Claude Config shows both Skills and Agents locations

**Prerequisites**: Claude Config installed

**Steps**:
1. Run TUI
2. Navigate to Extras → Claude Config
3. ViewToolDetail appears
4. Look at "Location" field

**Expected**:
```
Location:    Skills: /home/user/.claude/commands
             Agents: /home/user/.claude/agents
```

Both lines should be visible.

---

### Test 5: Stray Character Elimination (Bug #196)

**Purpose**: Verify no stray "8" or other characters appear

**Steps**:
1. Run TUI
2. Navigate through all screens:
   - Dashboard (table and menu)
   - Extras menu
   - Tool detail views
   - BatchPreview (if available)
3. Resize terminal window during operation
4. Wait for any spinners to complete

**Expected**: No unexpected characters appear on any screen

---

## Regression Tests

After all fixes, verify these basic functions still work:

- [ ] Dashboard displays tool status correctly
- [ ] Navigation with arrow keys works
- [ ] ESC key returns to previous view
- [ ] Install/Uninstall operations complete successfully
- [ ] Nerd Fonts menu accessible
- [ ] MCP Servers menu accessible
- [ ] 'r' key refreshes dashboard
- [ ] 'q' key quits cleanly

## Build Verification

```bash
cd tui

# Format check
go fmt ./...

# Static analysis
go vet ./...

# Build check
go build ./...
```

All commands should complete without errors.
