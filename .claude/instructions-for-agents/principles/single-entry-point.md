# Constitutional Principle: Single Entry Point Enforcement

**Status**: MANDATORY - CONSTITUTIONAL REQUIREMENT
**Enforcement**: Documentation review
**Last Updated**: 2026-01-31
**Authority**: User Constitutional Requirement

---

## Core Principle

> `./start.sh` is the ONLY command to communicate to end users.
>
> Developer commands must ALWAYS be labeled "DEVELOPER ONLY" when documented.

This principle is **NON-NEGOTIABLE** and applies to **ALL** AI assistants (Claude, Gemini, ChatGPT, etc.) working on this repository.

---

## Mandatory Rules

### Rule 1: User-Facing Documentation

**All user-facing documentation MUST use:**

```bash
./start.sh
```

**Examples of user-facing contexts:**
- README.md Quick Start sections
- Installation guides for end users
- One-liner installation instructions
- Quick reference cards

### Rule 2: Developer Documentation

**Developer commands MAY appear but MUST be labeled:**

```bash
cd tui && go run ./cmd/installer  # DEVELOPER ONLY
./tui/dotfiles-installer          # DEVELOPER ONLY (compiled binary)
```

**Examples of developer contexts:**
- Spec quickstart files (for contributors)
- Development guides
- Debugging documentation
- Build verification steps

### Rule 3: AGENTS.md/CLAUDE.md/GEMINI.md

The LLM instructions file should show both entry points with clear labels:

```markdown
### TUI Installer

**For Users:**
```bash
./start.sh                          # One-command setup (RECOMMENDED)
```

**For Developers:**
```bash
cd tui && go run ./cmd/installer    # DEVELOPER ONLY - Run from source
./tui/dotfiles-installer            # DEVELOPER ONLY - Run compiled binary
```
```

---

## Validation Checklist

**Before committing documentation changes, verify:**

### User-Facing Files
- [ ] **README.md**: Uses `./start.sh` for all user instructions
- [ ] **Quick Start sections**: Use `./start.sh` only
- [ ] **Installation guides**: Use `./start.sh` only

### Developer Files (specs/, internal docs)
- [ ] **All `go run` commands**: Labeled with `# DEVELOPER ONLY`
- [ ] **All binary execution**: Labeled with `# DEVELOPER ONLY`
- [ ] **Context is clear**: Developer vs user audience is obvious

### Verification Command

```bash
# Check for unlabeled developer commands in user-facing docs
grep -r "go run ./cmd/installer" --include="*.md" | grep -v "DEVELOPER"

# Should return empty (all labeled)
```

---

## Rationale

### Why This Matters

1. **User Experience**: End users should have ONE clear command to remember
2. **Confusion Prevention**: Multiple entry points lead to support issues
3. **Single Source of Truth**: `./start.sh` handles all setup logic
4. **Developer Flexibility**: Developers can still use direct commands when needed

### What `./start.sh` Does

- Detects if Go is installed
- Builds TUI if source changed
- Launches the interactive installer
- Handles first-time setup
- Provides consistent experience

### When Developers Need Direct Commands

- Rapid iteration during development
- Debugging specific components
- Running from source without building
- Testing specific changes

---

## Enforcement

### Documentation Review

All documentation changes should be reviewed for:
1. Entry point consistency
2. Proper labeling of developer commands
3. Clear audience indication

### Automated Verification

```bash
# Add to CI/CD validation
grep -r "go run ./cmd/installer" --include="*.md" | grep -v "DEVELOPER" && exit 1 || true
```

---

## Examples

### CORRECT: README.md

```markdown
## Quick Start

```bash
./start.sh
```

The script handles everything automatically.
```

### CORRECT: Spec Quickstart

```markdown
## Verification

### For Users
```bash
./start.sh
```

### For Developers
```bash
cd tui && go run ./cmd/installer  # DEVELOPER ONLY
```
```

### INCORRECT: Missing Label

```markdown
## Quick Start

```bash
cd tui && go run ./cmd/installer
```
```

**Problem**: Developer command in user context without label.

### INCORRECT: README.md with Developer Commands

```markdown
## Quick Start

For quick testing:
```bash
cd tui && go run ./cmd/installer  # DEVELOPER ONLY
```
```

**Problem**: Developer command in user-facing README, even with label.
README should use `./start.sh` exclusively.

---

## Related Principles

- **Script Proliferation Prevention**: Enhances existing scripts
- **Single Source of Truth**: `./start.sh` as canonical entry point
- **User Experience**: Clear, simple instructions

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-01-31 | Initial constitutional principle established |

---

**Status**: ACTIVE - MANDATORY COMPLIANCE
**Enforcement**: Documentation review
