#!/usr/bin/env bash
# Cleanup script to remove deprecated files from v4 branch
# These files are preserved in v3 branch on GitHub

set -e

echo "=== v4 Branch Cleanup Script ==="
echo ""
echo "This script will remove deprecated files from v4 branch."
echo "All files are preserved in v3 branch on GitHub."
echo ""

# Check if we're on v4 branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "v4" ]; then
    echo "❌ Error: Not on v4 branch (currently on $CURRENT_BRANCH)"
    echo "Please switch to v4 branch first: git checkout v4"
    exit 1
fi

echo "Current branch: $CURRENT_BRANCH"
echo ""

# List of files to potentially remove
FILES_TO_REMOVE=()

# Check if api/enhanced_coder_routes.py is used
if grep -q "enhanced_coder_routes\|enhanced_coder_router" modules/api/fastapi_app.py; then
    echo "⚠️  api/enhanced_coder_routes.py is still imported - checking if needed..."
    if grep -q "include_router.*enhanced" modules/api/fastapi_app.py; then
        echo "   ⚠️  Still using enhanced_coder_routes - DO NOT REMOVE"
    else
        echo "   ✅ Not used - can be removed"
        FILES_TO_REMOVE+=("api/enhanced_coder_routes.py")
    fi
else
    echo "   ✅ Not imported - can be removed"
    FILES_TO_REMOVE+=("api/enhanced_coder_routes.py")
fi

# Check api/app.py
if [ -f "api/app.py" ]; then
    if grep -q "DEPRECATED" api/app.py; then
        echo "✅ api/app.py is marked as deprecated - can be removed"
        FILES_TO_REMOVE+=("api/app.py")
    else
        echo "⚠️  api/app.py exists but not marked - review before removing"
    fi
fi

echo ""
echo "=== Files to Remove ==="
if [ ${#FILES_TO_REMOVE[@]} -eq 0 ]; then
    echo "No deprecated files found to remove."
else
    for file in "${FILES_TO_REMOVE[@]}"; do
        echo "  - $file"
    done
fi

echo ""
read -p "Do you want to remove these files? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Removing files..."
    for file in "${FILES_TO_REMOVE[@]}"; do
        if [ -f "$file" ]; then
            echo "  Removing $file..."
            rm "$file"
        else
            echo "  ⚠️  $file not found (may already be removed)"
        fi
    done
    
    echo ""
    echo "✅ Cleanup complete!"
    echo ""
    echo "Files removed from v4 branch (still in v3 branch on GitHub):"
    for file in "${FILES_TO_REMOVE[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Test the application: ./scripts/devserver.sh"
    echo "  3. Commit if satisfied: git add -A && git commit -m 'Remove deprecated files'"
else
    echo "Cleanup cancelled."
fi

