#!/bin/bash
# Deploy LLM CLI tools sudoers configuration to other Ubuntu machines
# Usage: ./deploy-sudoers.sh [hostname1] [hostname2] ...
# Or edit HOSTS variable below and run without arguments

set -e

# Define your hosts here (space-separated)
HOSTS_INPUT=""
HOSTS=()

# Use command-line arguments if provided
if [ $# -gt 0 ]; then
    HOSTS=("$@")
elif [ -n "$HOSTS_INPUT" ]; then
    read -r -a HOSTS <<< "$HOSTS_INPUT"
fi

if [ ${#HOSTS[@]} -eq 0 ]; then
    echo "Error: No hosts specified."
    echo "Usage: $0 hostname1 hostname2 ..."
    echo "Or edit the HOSTS_INPUT variable in this script"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUDOERS_FILE="$SCRIPT_DIR/../sudoers/llm-cli-tools"

if [ ! -f "$SUDOERS_FILE" ]; then
    echo "Error: Sudoers file not found at $SUDOERS_FILE"
    exit 1
fi

echo "Deploying sudoers configuration to: ${HOSTS[*]}"
echo "Sudoers file: $SUDOERS_FILE"
echo ""

for host in "${HOSTS[@]}"; do
    echo ">>> Deploying to $host..."

    # Copy file to remote temp location
    scp "$SUDOERS_FILE" "$host:/tmp/llm-cli-tools" || {
        echo "Failed to copy to $host"
        continue
    }

    # Move to sudoers.d with proper permissions
    ssh "$host" "sudo mv /tmp/llm-cli-tools /etc/sudoers.d/ && \
                 sudo chmod 440 /etc/sudoers.d/llm-cli-tools && \
                 sudo chown root:root /etc/sudoers.d/llm-cli-tools && \
                 sudo visudo -c" || {
        echo "Failed to install on $host"
        continue
    }

    echo "✓ Successfully deployed to $host"
    echo ""
done

echo "Deployment complete!"
