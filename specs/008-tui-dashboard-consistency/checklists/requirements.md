# TUI Dashboard Consistency - Requirements Checklist

## Functional Requirements Verification

### FR-001: Table Tools Navigate to ViewToolDetail
- [x] Node.js (nvm) selection → ViewToolDetail
- [x] Local AI Tools selection → ViewToolDetail
- [x] Google Antigravity selection → ViewToolDetail
- [ ] ViewToolDetail shows correct status info
- [ ] Actions work from ViewToolDetail

### FR-002: ViewAppMenu Deprecated
- [ ] ViewAppMenu removed from View enum
- [ ] viewAppMenu() function removed
- [ ] handleAppMenuEnter() function removed
- [ ] No code references ViewAppMenu

### FR-003: Update All Shows Preview
- [ ] "Update All" → ViewBatchPreview (not ViewInstaller)
- [ ] Preview lists tools with versions
- [ ] Cancel returns to Dashboard
- [ ] Confirm triggers batch update

### FR-004: Install All (Extras) Shows Preview
- [x] "Install All" in Extras → ViewBatchPreview
- [ ] Preview distinguishes installed vs missing
- [x] Cancel returns to Extras
- [ ] Confirm triggers batch install

### FR-005: Install All (Nerd Fonts) Shows Preview
- [x] "Install All" in Nerd Fonts → ViewBatchPreview
- [x] Preview lists fonts with status
- [x] Cancel returns to Nerd Fonts
- [ ] Confirm triggers batch install

### FR-006: Install Claude Config Uses ViewInstaller
- [x] Claude Config registered as tool
- [x] Selection triggers ViewInstaller
- [x] Progress displayed in TUI
- [x] TUI does not exit during operation

### FR-007: Preview Screens Have Confirm/Cancel
- [x] ViewBatchPreview has Cancel button
- [x] ViewBatchPreview has Confirm button
- [ ] Keyboard navigation works
- [x] ESC triggers Cancel

### FR-008: Visual Feedback for All Operations
- [ ] No operation starts without intermediate screen
- [ ] All operations show progress
- [ ] Success/failure displayed in TUI

### FR-009: Consistent Navigation Flow
- [ ] Dashboard → Detail → Action → Progress → Result
- [ ] Pattern consistent across all tools
- [ ] Back navigation correct at each step

### FR-010: Keyboard Shortcuts Work
- [ ] 'r' refreshes status (Dashboard, Extras, etc.)
- [ ] 'u' triggers Update All (with preview)
- [ ] ESC goes back at all levels
- [ ] Arrow keys navigate menus

---

## Non-Functional Requirements Verification

### NFR-001: No Immediate Execution
- [ ] "Update All" shows preview first
- [x] "Install All" (Extras) shows preview first
- [x] "Install All" (Nerd Fonts) shows preview first
- [ ] No batch operation starts without confirmation

### NFR-002: Cancel Before Execution
- [x] Preview screens have Cancel option
- [x] Cancel returns to previous view
- [ ] No partial work done on Cancel

### NFR-003: Responsive Transitions
- [ ] View transitions feel instant
- [ ] No visible lag between screens
- [ ] Spinner shown during loading

---

## Success Criteria Verification

### SC-001: 100% Tools Through ViewToolDetail
- [x] 3 table tools use ViewToolDetail
- [ ] 2 menu tools use ViewToolDetail
- [ ] 7 extras tools use ViewToolDetail
- [ ] Total: 12/12 (100%)

### SC-002: 100% Batch Operations Show Preview
- [ ] Update All shows preview
- [x] Install All (Extras) shows preview
- [x] Install All (Nerd Fonts) shows preview
- [ ] Total: 3/3 (100%)

### SC-003: 0 Unexpected TUI Exits
- [x] Install Claude Config stays in TUI
- [ ] Only sudo auth uses tea.ExecProcess
- [ ] No other tea.ExecProcess for user ops

### SC-004: 26 Menu Items Documented
- [ ] All items in screens.md
- [ ] Navigation targets documented
- [ ] Expected behavior documented

### SC-005: ViewAppMenu Usage = 0
- [ ] No code uses ViewAppMenu
- [ ] Enum value removed
- [ ] Related functions removed

### SC-006: Preview Cancel Works
- [ ] Update All preview → Cancel → Dashboard
- [x] Install All (Extras) preview → Cancel → Extras
- [x] Install All (Nerd Fonts) preview → Cancel → Nerd Fonts

### SC-007: Code Compiles
- [ ] `go build ./...` succeeds
- [ ] No compile errors
- [ ] No warnings

---

## Complete Menu Item Verification

### Dashboard Table (3 items)
| Item | ViewToolDetail? | Actions Work? |
|------|-----------------|---------------|
| Node.js (nvm) | [x] | [ ] |
| Local AI Tools | [x] | [ ] |
| Google Antigravity | [x] | [ ] |

### Dashboard Menu (7 items)
| Item | Correct Navigation? |
|------|---------------------|
| Ghostty | [ ] ViewToolDetail |
| Feh | [x] ViewToolDetail |
| Update All | [ ] ViewBatchPreview |
| Nerd Fonts | [x] ViewNerdFonts |
| Extras | [x] ViewExtras |
| Boot Diagnostics | [x] ViewDiagnostics |
| Exit | [x] Quit |

### Extras Menu (11 items)
| Item | Correct Navigation? |
|------|---------------------|
| Fastfetch | [x] ViewToolDetail |
| Glow | [x] ViewToolDetail |
| Go | [x] ViewToolDetail |
| Gum | [x] ViewToolDetail |
| Python/uv | [x] ViewToolDetail |
| VHS | [x] ViewToolDetail |
| ZSH | [x] ViewToolDetail |
| Install All | [x] ViewBatchPreview |
| Install Claude Config | [x] ViewInstaller |
| MCP Servers | [x] ViewMCPServers |
| Back | [x] ViewDashboard |

### Nerd Fonts Menu (3 items)
| Item | Correct Navigation? |
|------|---------------------|
| Font families (8) | [ ] Action menu → ViewInstaller |
| Install All | [x] ViewBatchPreview |
| Back | [x] ViewDashboard |

### MCP Servers Menu (3 items)
| Item | Correct Navigation? |
|------|---------------------|
| Servers (7) | [x] Action menu |
| Setup Secrets | [ ] ViewSecretsWizard |
| Back | [ ] ViewExtras |

---

## Final Verification

- [ ] All functional requirements met
- [ ] All non-functional requirements met
- [ ] All success criteria met
- [ ] All 26 menu items verified
- [ ] Code compiles and tests pass
- [ ] Documentation updated
- [ ] Manual testing complete
