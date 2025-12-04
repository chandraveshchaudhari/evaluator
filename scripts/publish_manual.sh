#!/bin/bash

# Manual Publish Script
# This script manually publishes the current version to PyPI
# Usage: ./publish_manual.sh [version]

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Get version from pyproject.toml if not provided
VERSION="${1:-$(grep -oP 'version\s*=\s*"\K[^"]+' pyproject.toml | head -1)}"

echo "🚀 Publishing instantgrade v$VERSION to PyPI"
echo "================================================"

# Check if tag exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "✅ Tag v$VERSION exists locally"
else
    echo "⚠️  Tag v$VERSION does not exist locally. Creating it..."
    git tag -a "v$VERSION" -m "Release v$VERSION"
fi

# Check if tag is on remote
if git rev-parse "origin/v$VERSION" >/dev/null 2>&1; then
    echo "✅ Tag v$VERSION exists on remote"
else
    echo "📤 Pushing tag v$VERSION to remote..."
    git push origin "v$VERSION"
fi

# Ensure GitHub release exists
echo "📋 Checking GitHub release..."
if gh release view "v$VERSION" 2>/dev/null; then
    echo "✅ Release v$VERSION already exists on GitHub"
else
    echo "📝 Creating GitHub release v$VERSION..."
    gh release create "v$VERSION" \
        --title "Release v$VERSION" \
        --notes "Release of instantgrade v$VERSION" \
        --repo chandraveshchaudhari/instantgrade
fi

echo ""
echo "✅ All steps completed!"
echo ""
echo "Next steps:"
echo "1. Check GitHub Actions: https://github.com/chandraveshchaudhari/instantgrade/actions"
echo "2. Verify PyPI: https://pypi.org/project/instantgrade/"
echo "3. Install: pip install --upgrade instantgrade"
echo ""
