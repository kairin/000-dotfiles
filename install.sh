#!/bin/bash
# One-line installer for LLM CLI tools sudoers configuration
# Compatible with Ubuntu 25.04 and other Ubuntu versions
# Usage: wget -qO- https://raw.githubusercontent.com/kairin/000-dotfiles/main/install.sh | bash

set -e

echo "=== LLM CLI Tools Sudoers Configuration Installer ==="
echo "Compatible with Ubuntu 25.04+"
echo ""

# Detect current user
CURRENT_USER="${SUDO_USER:-$USER}"
echo "Installing for user: $CURRENT_USER"

# Check if running on Ubuntu
if [ ! -f /etc/os-release ]; then
    echo "Error: Cannot detect OS. This script is for Ubuntu only."
    exit 1
fi

source /etc/os-release
if [[ "$ID" != "ubuntu" ]]; then
    echo "Error: This script is designed for Ubuntu. Detected: $ID"
    exit 1
fi

echo "Detected: Ubuntu $VERSION_ID"

# Install uv if not present (using system Python)
if ! command -v uv &> /dev/null; then
    echo ""
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add uv to current session PATH
    export PATH="$HOME/.local/bin:$PATH"

    echo "uv installed successfully"
else
    echo "uv is already installed"
fi

# Verify uv installation
if ! command -v uv &> /dev/null; then
    echo "Error: uv installation failed or not in PATH"
    echo "Please add ~/.local/bin to your PATH and rerun"
    exit 1
fi

# Ensure system Python is available
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "Installing system Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

PYTHON_VERSION=$(python3 --version)
echo "Using system Python: $PYTHON_VERSION"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

cd "$TEMP_DIR"

# Download sudoers configuration
echo ""
echo "Downloading sudoers configuration..."
REPO_RAW_URL="https://raw.githubusercontent.com/kairin/000-dotfiles/main"

# Download the sudoers file
curl -fsSL "$REPO_RAW_URL/sudoers/llm-cli-tools" -o llm-cli-tools

# Verify download
if [ ! -f llm-cli-tools ]; then
    echo "Error: Failed to download sudoers configuration"
    exit 1
fi

# Replace placeholder username with actual username
sed -i "s/kkk/$CURRENT_USER/g" llm-cli-tools

echo "Downloaded and customized for user: $CURRENT_USER"

# Validate sudoers syntax before installing
echo ""
echo "Validating sudoers syntax..."
if ! visudo -c -f llm-cli-tools; then
    echo "Error: Invalid sudoers syntax"
    exit 1
fi

echo "Syntax validation passed"

# Install sudoers configuration
echo ""
echo "Installing sudoers configuration (requires sudo)..."
sudo cp llm-cli-tools /etc/sudoers.d/llm-cli-tools
sudo chmod 440 /etc/sudoers.d/llm-cli-tools
sudo chown root:root /etc/sudoers.d/llm-cli-tools

# Final validation
echo ""
echo "Performing final system validation..."
if ! sudo visudo -c; then
    echo "Error: Sudoers configuration is invalid. Rolling back..."
    sudo rm -f /etc/sudoers.d/llm-cli-tools
    exit 1
fi

echo ""
echo "✓ Installation completed successfully!"
echo ""
echo "The following commands can now run without password for user '$CURRENT_USER':"
echo "  - Package management: apt, apt-get, dpkg, snap"
echo "  - Docker: docker, docker-compose"
echo "  - System services: systemctl"
echo "  - User management: usermod, groupadd"
echo "  - File operations: install, mkdir, chmod, chown, tee"
echo "  - Network: curl, wget"
echo ""
echo "uv is installed at: $(which uv)"
echo "System Python: $PYTHON_VERSION"
echo ""
echo "You can now use LLM CLI tools (Claude Code, Copilot CLI, Gemini CLI)"
echo "without password prompts for whitelisted commands."
