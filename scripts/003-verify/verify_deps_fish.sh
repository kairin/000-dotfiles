#!/bin/bash
# verify_deps_fish.sh - Verify dependencies for Fish shell

MISSING=""

if ! command -v curl &> /dev/null; then
    MISSING="$MISSING curl"
fi

if ! command -v git &> /dev/null; then
    MISSING="$MISSING git"
fi

if [ -n "$MISSING" ]; then
    echo "Missing dependencies:$MISSING"
    exit 1
fi

echo "Dependencies verified."
