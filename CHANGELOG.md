# Changelog

All notable changes to this project are documented here.

## [0.1.x] — 2026-05-02

### Added

- **Copilot CLI** (GitHub Copilot) added to baseline with npm installer and auth guidance
- **SpecKit CLI** (`specify`) added to baseline with new `uv_tool` install method
- **Stable menu numbering**: fixed option numbers 1–5 regardless of state; `[recommended]`
  tag moves to highlight the best action instead of reordering options
- **Exit code propagation** in bash menu: tool install failures properly signal errors
- **103 unit tests** across all modules; Codacy coverage integration configured
- Comprehensive documentation: specs folder with implementation design, contracts, data model,
  task tracking

### Fixed

- **dnsutils virtual package resolution** (Ubuntu 22.04+): baseline now checks for
  `bind9-dnsutils` (concrete package) instead of virtual `dnsutils`
- **Claude keybindings.json template**: corrected from `[]` to `{ "bindings": [] }`

### Technical

- Added `_install_uv_tool()` executor in tool_installer.py to support uv-managed tool updates
- Implemented mode-aware command dispatch: separate `uv tool install` for new tools vs `uv tool upgrade` for updates
- Added sudo handling for tools that require elevated privileges

---

## [0.1.0-alpha] — 2026-04

Initial release. Core functionality:

### Features

- **Machine doctor** (`dotfiles_tools doctor`): non-destructive audit of current vs desired state
- **Setup plan** (`dotfiles_tools plan`): preview of all planned operations without writing
- **Config apply** (`dotfiles_tools apply`): deploy configs with backups before overwrite
- **Project bootstrap** (`dotfiles_tools init-project`): scaffold `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` in any project
- **Tool installer** (`dotfiles_tools bootstrap-plan`/`bootstrap-apply`): install and upgrade a curated baseline of developer tools (uv, git, gh, fish, direnv, claude, codex, gemini, and more)
- **Font catalog**: automatic download and install of 4 Nerd Font families (JetBrainsMono, FiraCode, Hack, MesloLGS) and 4 apt fallback fonts (Noto Color Emoji, Symbola, GNU FreeFont, DejaVu)
- **Multi-platform support**: Linux, WSL (with Windows host font management), Raspberry Pi, Pixel Terminal, Pixel AVF
- **Manifest-driven deployment**: single source of truth in `dotfiles-manifest.json` for what installs where
- **Protected files**: sensitive targets (git config, fish plugin list) never auto-overwritten without explicit inclusion
- **Bash entrypoint** (`./setup`): state-aware menu wrapper with bootstrap, drift audit, plan, and apply modes
- **Agent doc symlinks**: root-level `CLAUDE.md` and `GEMINI.md` symlink to `AGENTS.md` (single source of truth per scope)

### Design & Validation

- Complete specification in `specs/001-dotfiles-bootstrap-validation/` with user stories, acceptance criteria, and functional requirements
- Full task tracking: 63 tasks across 8 implementation phases, all marked complete
- Comprehensive test suite: unit tests for all major components (doctor, plan, apply, fonts, project bootstrap)
- CI/CD: GitHub Actions validation on push and PR, Codacy coverage reporting
