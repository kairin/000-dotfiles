# Data Model: Fix Fish Shell TUI Display

**Date**: 2026-01-31
**Feature**: 003-fix-fish-tui-display

## Entities

This is a UI-only fix with no data model changes.

### Existing Entities (No Changes)

#### Tool (registry.Tool)

Fish is already defined in the registry with all required fields:

| Field | Value | Notes |
|-------|-------|-------|
| ID | "fish" | Unique identifier |
| DisplayName | "Fish + Fisher" | Shown in UI |
| Description | "Fish shell + Fisher + Tide theme" | Detail view |
| Category | CategoryMain | Already correct |
| Method | MethodAPT | Installation method |
| Scripts | All defined | check, install, uninstall, configure, update |

#### UI Filter (getTableTools)

Current filter returns: `nodejs`, `ai_tools`, `antigravity`
Required filter returns: `nodejs`, `ai_tools`, `antigravity`, `fish`

## State Transitions

N/A - No state changes, only display logic fix.

## Validation Rules

N/A - Using existing validation from registry.
