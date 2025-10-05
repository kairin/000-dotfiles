# 000 Dotfiles

LLM CLI tools sudoers configuration and system setup for Ubuntu 25.04+ with uv package manager integration.

## 🎯 Purpose

This repository manages sudoers configurations that enable AI-powered CLI tools (Claude Code, Copilot CLI, Gemini CLI) to execute system commands without password prompts, streamlining development workflows across multiple machines. Part of the unified system management suite alongside 001-agents-manager and 002-mcp-manager.

## Contents

- `sudoers/llm-cli-tools` - Sudoers configuration allowing LLM tools to run specific commands without password
- `scripts/deploy-sudoers.sh` - Deployment script for other machines
- `install.sh` - One-line wget installer for quick setup on any Ubuntu machine

## Installation

### Quick Install (Recommended for Office Machines)

**One-line installation using wget** (Ubuntu 25.04+):

```bash
wget -qO- https://raw.githubusercontent.com/kairin/000-dotfiles/main/install.sh | bash
```

**What this script does:**
- ✓ Installs `uv` package manager (if not present)
- ✓ Verifies system Python installation (uses Ubuntu's system Python only)
- ✓ Downloads sudoers configuration from this repository
- ✓ Automatically customizes for your username
- ✓ Validates syntax before applying (safe - won't break your sudo)
- ✓ Performs rollback if validation fails
- ✓ No git clone required - completely standalone

**Requirements:**
- Ubuntu 25.04+ (or other Ubuntu versions)
- Internet connection
- sudo privileges


### Manual Installation

#### On this machine (localhost)

```bash
sudo cp ~/dotfiles/sudoers/llm-cli-tools /etc/sudoers.d/
sudo chmod 440 /etc/sudoers.d/llm-cli-tools
sudo chown root:root /etc/sudoers.d/llm-cli-tools
sudo visudo -c  # Verify syntax
```

### On other machines (if repo is already cloned)

#### Option 1: Using the wget installer (Easiest)
```bash
# No need to clone - just run:
wget -qO- https://raw.githubusercontent.com/kairin/000-dotfiles/main/install.sh | bash
```

#### Option 2: Using deployment script (for multiple machines)
```bash
cd ~/dotfiles
./scripts/deploy-sudoers.sh hostname1 hostname2 hostname3
```

#### Option 3: Manual deployment
```bash
# On each machine, clone this repo first
git clone ~/dotfiles  # Or from remote if pushed

# Then install
sudo cp ~/dotfiles/sudoers/llm-cli-tools /etc/sudoers.d/
sudo chmod 440 /etc/sudoers.d/llm-cli-tools
sudo chown root:root /etc/sudoers.d/llm-cli-tools
```

## Adding New Commands

Edit `sudoers/llm-cli-tools` and add commands in the format:
```
username ALL=(ALL) NOPASSWD: /full/path/to/command
```

Find command paths with: `which command_name`

After editing:
```bash
git add sudoers/llm-cli-tools
git commit -m "Add new sudo command: xyz"
```

Then redeploy to other machines.

## Requirements

- **OS:** Ubuntu 25.04+ (compatible with earlier Ubuntu versions)
- **Python:** System Python 3 (automatically verified by installer)
- **Package Manager:** `uv` (automatically installed by installer if missing)
- **Permissions:** sudo access for installation

## Security

- `.gitignore` is configured to prevent committing secrets
- Only configuration files are tracked, never credentials
- Before committing new files: `git add -n .` (dry-run check)
- Installer validates sudoers syntax before applying (prevents breaking sudo)
- Automatic rollback on validation failure
- Whitelisted commands only - no blanket sudo access

## Whitelisted Commands

Currently allows passwordless sudo for the following commands:

| Category | Commands |
|----------|----------|
| **Package Management** | `apt`, `apt-get`, `dpkg`, `snap` |
| **Container Management** | `docker`, `docker-compose` |
| **System Services** | `systemctl` |
| **User Management** | `usermod`, `groupadd` |
| **File Operations** | `install`, `mkdir`, `chmod`, `chown`, `tee` |
| **Network Tools** | `curl`, `wget` |

These commands can be executed by LLM CLI tools without password prompts.

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

## Contributing

When adding new configurations:
1. Test locally first
2. Update CHANGELOG.md under `[Unreleased]`
3. Update README.md if adding new features
4. Commit with descriptive message (format: "Add/Update/Fix: description")
5. Deploy to other machines as needed

### Adding New Sudo Commands

1. Find the command path:
   ```bash
   which command_name
   ```

2. Edit `sudoers/llm-cli-tools`:
   ```
   username ALL=(ALL) NOPASSWD: /full/path/to/command
   ```

3. Test locally:
   ```bash
   sudo cp sudoers/llm-cli-tools /etc/sudoers.d/
   sudo chmod 440 /etc/sudoers.d/llm-cli-tools
   sudo chown root:root /etc/sudoers.d/llm-cli-tools
   sudo visudo -c  # Verify syntax
   ```

4. Commit and push:
   ```bash
   git add sudoers/llm-cli-tools CHANGELOG.md
   git commit -m "Add sudo command: command_name"
   git push
   ```

5. Redeploy to office machines:
   ```bash
   # They can just re-run the installer
   wget -qO- https://raw.githubusercontent.com/kairin/000-dotfiles/main/install.sh | bash
   ```

## License

Personal configuration files - use at your own discretion.
