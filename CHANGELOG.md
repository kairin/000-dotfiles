# Changelog

All notable changes to this project are documented here.

## [0.1.x] — 2026-05-03

### Added

- **GitHub MCP auto-registration** — after machine bootstrap, setup auto-registers
  `@modelcontextprotocol/server-github` via `claude mcp add --scope user` so the GitHub
  MCP is available in all Claude Code sessions without manual configuration
- **Codacy MCP + account token** — machine-level Codacy account token support added
  (`~/.codacy/account-token`); `@codacy/codacy-mcp@latest` auto-registered via
  `claude mcp add --scope user`; setup "Configure API tokens" menu includes a
  dedicated "Codacy" option
- **direnv fish hook** — `fish/conf.d/direnv.fish` added to auto-source the direnv hook
  in interactive fish shells; `direnv allow` is run automatically after Codacy project
  setup completes
- **HuggingFace CLI renamed** — CLI command updated from `huggingface-cli` to `hf`;
  login command updated to `hf auth login`
- **GITHUB_TOKEN in .envrc.local** — project `.envrc.local` now exports `GITHUB_TOKEN`
  via `$(gh auth token 2>/dev/null)` so tools that read the standard env var get a
  valid token without manual configuration
- **User customizable config files** — 10 user-facing config files (claude/settings.json,
  claude/keybindings.json, claude/CLAUDE.md, codex/config.toml, codex/default.rules,
  gemini/settings.json, gemini/GEMINI.md, gh/config.yml, fish/env.fish,
  fish/functions/direnv.fish) are now marked `user_customizable` in the manifest and will
  never be auto-overwritten by option 2 (apply dotfiles), even if they differ from
  their templates
- **Optional integrations menu** — GitHub (gh) and HuggingFace token options now appear
  dynamically in the optional integrations menu (only when not yet configured), alongside
  Codacy; users can configure multiple API credentials from one place
- **Auto-install missing CLIs** — When selecting GitHub or HuggingFace from optional
  integrations, setup offers to install the missing CLI: `sudo apt install -y gh` for
  GitHub, or `uv tool install huggingface-hub` for HuggingFace
- **Readline support in menu prompts** — All interactive menu prompts now use `read -r -e`,
  enabling arrow key navigation and readline editing instead of raw escape sequences

### Fixed

- **Menu loop behavior** — Option 2 (apply dotfiles) now returns to the main menu instead
  of exiting, matching option 1 (install tools) behavior
- **Placeholder documentation** — AGENTS.md.template and CLAUDE.md now correctly document
  the placeholder format as `{ {UPPER_SNAKE_CASE} }` (with spaces) to avoid false-positive
  pattern matching in documentation
- **API credential status visibility** — `./setup verify` now appends a 3-row credential
  table (GitHub, HuggingFace, Codacy) showing configuration status when verification passes

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
