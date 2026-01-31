# Quickstart: Verbose Spinner Progress

**Feature**: 015-verbose-spinner-progress
**Purpose**: Quick validation workflow for verbose spinner progress implementation

---

## Build & Launch

```bash
cd tui && go build ./cmd/installer && ./dotfiles-installer
```

---

## Validation Workflow

### 1. NerdFonts View

**Navigate**: Main Menu → Nerd Fonts

**Expected during loading**:
```
⠋ Loading font statuses...

  ○ JetBrainsMono      IDE-optimized with ligatures
  ⠋ FiraCode           Programming ligatures pioneer
  ✓ Hack               Clear, readable, no ligatures
  ...

Progress: 2/8 complete
```

**Verify**:
- [ ] All 8 fonts listed immediately
- [ ] Individual spinners animate for loading fonts
- [ ] Status icons (○/⠋/✓/✗) display correctly
- [ ] Progress summary updates as fonts complete
- [ ] ESC cancels and returns to menu

---

### 2. MCPServers View

**Navigate**: Main Menu → Extras → MCP Servers

**Expected during loading**:
```
⠋ Checking MCP server status...

  ○ Context7           Documentation lookup
  ⠋ GitHub             Repository operations
  ✓ Playwright         Browser automation
  ...

Progress: 2/7 complete
```

**Verify**:
- [ ] All 7 servers listed immediately
- [ ] Individual spinners animate
- [ ] Status icons display correctly
- [ ] Progress summary updates
- [ ] ESC cancels and returns

---

### 3. Extras Menu

**Navigate**: Main Menu → Extras

**Expected during loading**:
```
Extras Tools • ⠋ Loading... (3/9 complete)

Choose:
> ✓ Glow
  ✓ Gum
  ⠋ Fastfetch
  ○ VHS
  ○ Atuin
  ○ Carapace
  ○ TV
  ○ Fish
  ○ Claude Code
  ─────────────
    Install All
    Install Claude Config
    MCP Servers
    SpecKit Updater
    Back
```

**Verify**:
- [ ] Header shows loading progress
- [ ] Each tool has status indicator prefix
- [ ] Spinner animates for loading tools
- [ ] Separator visible between tools and actions
- [ ] Progress updates as tools complete

---

### 4. Installer (any tool)

**Navigate**: Select any tool → Install

**Expected during installation**:
```
Installing Glow...

  ✓ Check            Verifying prerequisites
  ⠋ InstallDeps      Installing dependencies
  ○ VerifyDeps       Confirming dependencies
  ○ Install          Installing tool
  ○ Confirm          Verifying installation

[Output log continues below]
```

**Verify**:
- [ ] All stages listed with descriptions
- [ ] Current stage shows spinner
- [ ] Completed stages show checkmark
- [ ] Output log remains visible
- [ ] ESC cancels installation

---

## Edge Case Tests

### Terminal Resize
- [ ] Resize terminal during loading → re-renders correctly

### Timeout Handling
- [ ] Slow network → timeout icon (✗) shows, others continue

### All Items Fail
- [ ] Network disconnected → all show ✗, error message displays

---

## Success Criteria

| Criterion | Test |
|-----------|------|
| SC-001: Identify loading item in <1s | Visual confirmation |
| SC-002: No horizontal scroll (80x24) | Resize terminal to 80x24 |
| SC-003: Updates within 100ms | Perceived as instant |
| SC-004: ESC responds in <500ms | Feel for responsiveness |
| SC-005: Visual consistency | Compare all views |
| SC-006: Output logs visible | Installer view |

---

## Quick Commands

```bash
# Build only
cd tui && go build ./cmd/installer

# Build and run
cd tui && go build ./cmd/installer && ./dotfiles-installer

# Run without rebuild
./tui/dotfiles-installer

# Check for Go errors
cd tui && go vet ./...
```
