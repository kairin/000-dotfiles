# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CHANGELOG.md to track project changes
- `install.sh` - One-line wget installer for quick setup on office machines
  - Automatic `uv` package manager installation
  - System Python verification (uses Ubuntu's system Python only)
  - Username auto-detection and customization
  - Sudoers syntax validation before applying
  - Automatic rollback on validation failure
  - Ubuntu 25.04+ compatibility
  - Completely standalone - no git clone required
- Enhanced README with comprehensive documentation:
  - Quick install section with detailed feature list
  - Requirements section
  - Enhanced security notes
  - Formatted whitelisted commands table
  - Step-by-step guide for adding new sudo commands
  - Contributing guidelines with commit message format
- Better structured installation options (3 methods documented)

## [1.0.0] - 2025-10-05

### Added
- Deployment script (`scripts/deploy-sudoers.sh`) for remote machine installation
- Comprehensive README.md with installation and usage instructions
- `.gitignore` configuration to prevent committing secrets

### Changed
- Improved documentation structure

## [0.1.0] - 2025-10-05

### Added
- Initial sudoers configuration file (`sudoers/llm-cli-tools`)
- Passwordless sudo access for LLM CLI tools (Claude Code, Copilot CLI, Gemini CLI)
- Whitelisted commands:
  - Package management: apt, apt-get, dpkg, snap
  - Docker: docker, docker-compose
  - System services: systemctl
  - User management: usermod, groupadd
  - File operations: install, mkdir, chmod, chown, tee
  - Network: curl, wget

[Unreleased]: https://github.com/kairin/000-dotfiles/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/kairin/000-dotfiles/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/kairin/000-dotfiles/releases/tag/v0.1.0
