# Dotfiles Repository

Configuration files for LLM CLI tools (Claude Code, Copilot CLI, Gemini CLI) across Ubuntu machines.

## Contents

- `sudoers/llm-cli-tools` - Sudoers configuration allowing LLM tools to run specific commands without password
- `scripts/deploy-sudoers.sh` - Deployment script for other machines

## Installation

### On this machine (localhost)

```bash
sudo cp ~/dotfiles/sudoers/llm-cli-tools /etc/sudoers.d/
sudo chmod 440 /etc/sudoers.d/llm-cli-tools
sudo chown root:root /etc/sudoers.d/llm-cli-tools
sudo visudo -c  # Verify syntax
```

### On other machines

#### Option 1: Using deployment script
```bash
cd ~/dotfiles
./scripts/deploy-sudoers.sh hostname1 hostname2 hostname3
```

#### Option 2: Manual deployment
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

## Security

- `.gitignore` is configured to prevent committing secrets
- Only configuration files are tracked, never credentials
- Before committing new files: `git add -n .` (dry-run check)

## Whitelisted Commands

Currently allows passwordless sudo for:
- Package management: apt, snap, dpkg
- Docker: docker, docker-compose
- System services: systemctl
- User management: usermod, groupadd
- File operations: install, mkdir, chmod, chown, tee
- Network: curl, wget
