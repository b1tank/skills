#!/bin/bash
# sync.sh - Sync agents and prompts from ~/skills to a target repo
#
# Usage: ./sync.sh <target-repo-path>
# Example: ./sync.sh ~/my-project
#
# This copies:
#   agents/*.agent.md  → <target>/.github/agents/
#   prompts/*.prompt.md → <target>/.github/prompts/
#
# Note: Skills are installed via `npx skills add b1tank/skills`

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$1" ]; then
    echo "Usage: $0 <target-repo-path>"
    echo "Example: $0 ~/my-project"
    exit 1
fi

TARGET="$1"

if [ ! -d "$TARGET" ]; then
    echo "Error: Target directory does not exist: $TARGET"
    exit 1
fi

# Create target directories if they don't exist
mkdir -p "$TARGET/.github/agents"
mkdir -p "$TARGET/.github/prompts"

echo "Syncing from $SCRIPT_DIR to $TARGET/.github/"
echo ""

# Sync agents
echo "Syncing agents..."
for file in "$SCRIPT_DIR/agents/"*.agent.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$TARGET/.github/agents/$filename"
        echo "  ✓ $filename"
    fi
done

# Sync prompts
echo ""
echo "Syncing prompts..."
for file in "$SCRIPT_DIR/prompts/"*.prompt.md; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        cp "$file" "$TARGET/.github/prompts/$filename"
        echo "  ✓ $filename"
    fi
done

echo ""
echo "Done! Synced to $TARGET/.github/"
echo ""
echo "Next steps:"
echo "  1. Review changes: cd $TARGET && git status"
echo "  2. Commit: git add .github/agents .github/prompts && git commit -m 'chore: sync agents and prompts from b1tank/skills'"
