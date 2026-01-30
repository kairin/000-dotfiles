# Fish Shell Tool Documentation

## Overview

**Fish** (Friendly Interactive Shell) is a smart, user-friendly command line shell with powerful features out of the box. This tool installs Fish with the Fisher plugin manager and a curated set of plugins for optimal productivity.

## Components

| Component | Description | Source |
|-----------|-------------|--------|
| Fish shell | Modern shell with autosuggestions, syntax highlighting | apt |
| Fisher | Plugin manager for Fish | curl script |
| fzf.fish | Fuzzy finder integration | Fisher plugin |
| z | Directory jumping | Fisher plugin |
| autopair.fish | Auto-close brackets/quotes | Fisher plugin |
| Tide | Modern prompt theme | Fisher plugin |
| bass | Run bash scripts in Fish | Fisher plugin |
| done | Command completion notifications | Fisher plugin |

## Installation Method

- **Primary**: APT package manager
- **Fisher**: Installed via curl script into Fish
- **Plugins**: Installed via Fisher

## Version Detection

```bash
fish --version
# Output: fish, version 3.7.0
```

## Check Script Output Format

```
INSTALLED|<version>|<method>|<location>^fisher:<yes/no>^plugins:<n>^tide:<yes/no>|<latest>
```

Example:
```
INSTALLED|3.7.0|APT|/usr/bin/fish^fisher:yes^plugins:7^tide:yes|3.7.0
```

## Key Features

### Built-in Features (No Plugins Needed)
- **Autosuggestions**: Fish suggests commands as you type based on history
- **Syntax highlighting**: Commands are colored (red = invalid, blue = valid)
- **Tab completions**: Intelligent completions for commands, paths, options
- **Web-based configuration**: `fish_config` opens a browser-based config UI

### Plugin Features
- **fzf.fish**: Press `Ctrl+R` for fuzzy history, `Ctrl+T` for file finder
- **z**: Type `z partial-dir-name` to jump to frequently used directories
- **autopair**: Brackets, quotes, and parentheses auto-close
- **Tide**: Beautiful, informative prompt with git status, execution time
- **bass**: Run bash scripts: `bass source ./some-bash-script.sh`
- **done**: Get notifications when long commands finish

## Configuration

### Config Location
- Main config: `~/.config/fish/config.fish`
- Functions: `~/.config/fish/functions/`
- Completions: `~/.config/fish/completions/`
- Plugins: `~/.config/fish/fish_plugins`

### TUI Configure Action
The Configure action adds:
- PATH configuration (~/.local/bin, cargo, go)
- Tool completions (uv, gh, gum, glow, fnm)
- Modern CLI aliases (bat, eza, fd, rg, zoxide)
- Utility functions (mkcd, .., ...)

## Usage Examples

### Basic Usage
```fish
# Fish autosuggests as you type - press → to accept
cd ~/Ap  # Fish suggests: cd ~/Apps/

# Use z for quick navigation
z dotfiles  # Jumps to ~/Apps/000-dotfiles

# Fuzzy find in history
# Press Ctrl+R, then type partial command
```

### Running Bash Scripts
```fish
# Fish is NOT POSIX-compliant, so bash scripts need special handling
bass source ./activate.sh
bass ./build.sh --option
```

### Tide Configuration
```fish
# Interactive prompt customization
tide configure
```

## Troubleshooting

### Fisher Not Installing Plugins
```fish
# Reinstall Fisher
curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && fisher install jorgebucaran/fisher

# Reinstall all plugins
fisher update
```

### Tide Prompt Not Showing
```fish
# Ensure Tide is installed
fisher install IlanCosman/tide

# Reconfigure
tide configure
```

### fzf Not Working
```fish
# Ensure fzf is installed
sudo apt install fzf

# Reinstall fzf.fish plugin
fisher install PatrickF1/fzf.fish
```

### Bash Script Compatibility
Fish syntax differs from bash. For scripts that must run in bash:
1. Use `#!/bin/bash` shebang
2. Run via bass: `bass source ./script.sh`
3. Or explicitly: `bash ./script.sh`

## Default Shell

The TUI does NOT automatically set Fish as the default shell. To make Fish your default:

```bash
# Add Fish to valid shells (if not already)
command -v fish | sudo tee -a /etc/shells

# Set as default
chsh -s $(which fish)

# Log out and back in for changes to take effect
```

To revert:
```bash
chsh -s /bin/bash
```

## Uninstall Behavior

The uninstall script:
1. Removes Fisher plugins first
2. Removes Fish apt package
3. Preserves `~/.config/fish/` for user config backup

To completely remove:
```bash
rm -rf ~/.config/fish
```

## Related Tools

- **ZSH**: Alternative shell with Oh My Zsh (available in TUI Extras)
- **fzf**: Fuzzy finder (installed as dependency)
- **bat, eza, fd, rg**: Modern CLI tools (aliases configured)

## References

- [Fish Shell Documentation](https://fishshell.com/docs/current/)
- [Fisher Plugin Manager](https://github.com/jorgebucaran/fisher)
- [Tide Theme](https://github.com/IlanCosman/tide)
- [fzf.fish Plugin](https://github.com/PatrickF1/fzf.fish)
