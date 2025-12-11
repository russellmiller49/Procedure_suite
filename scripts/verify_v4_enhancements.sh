#!/usr/bin/env bash
# Verify that all v4 enhancements are in the enhanced version

set -e

echo "=== Verifying v4 Enhancements ==="
echo ""

# Check if we're on v4 branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "v4" ]; then
    echo "⚠️  Warning: Not on v4 branch (currently on $CURRENT_BRANCH)"
    echo ""
fi

echo "1. Checking EnhancedCPTCoder integration..."
if grep -q "EnhancedCPTCoder" modules/api/fastapi_app.py; then
    echo "   ✅ EnhancedCPTCoder is used in main app"
else
    echo "   ❌ EnhancedCPTCoder NOT found in main app"
fi

echo ""

echo "2. Checking for old CoderEngine usage..."
if grep -q "from modules.coder.engine import CoderEngine" modules/api/fastapi_app.py; then
    echo "   ❌ Still using old CoderEngine - needs migration"
else
    echo "   ✅ Not using old CoderEngine"
fi

echo ""

echo "3. Checking RVU calculator integration..."
if grep -q "ProcedureRVUCalculator\|rvu_calc" modules/api/fastapi_app.py; then
    echo "   ✅ RVU calculator integrated"
else
    echo "   ⚠️  RVU calculator not found in main app"
fi

echo ""

echo "4. Checking frontend RVU display..."
if grep -q "financials\|RVU\|total_work_rvu" modules/api/static/app.js; then
    echo "   ✅ Frontend displays RVU data"
else
    echo "   ⚠️  Frontend may not display RVU data"
fi

echo ""

echo "5. Checking for deprecated files..."
DEPRECATED_FOUND=0

if [ -f "api/app.py" ]; then
    if grep -q "DEPRECATED" api/app.py; then
        echo "   ✅ api/app.py is marked as deprecated"
    else
        echo "   ⚠️  api/app.py exists but not marked"
        DEPRECATED_FOUND=1
    fi
fi

if [ -f "api/enhanced_coder_routes.py" ]; then
    echo "   ⚠️  api/enhanced_coder_routes.py exists (may be deprecated if routes are integrated)"
    DEPRECATED_FOUND=1
fi

echo ""

echo "6. Checking EnhancedCPTCoder file..."
if [ -f "proc_autocode/coder.py" ]; then
    if grep -q "class EnhancedCPTCoder" proc_autocode/coder.py; then
        echo "   ✅ EnhancedCPTCoder exists"
    else
        echo "   ❌ EnhancedCPTCoder not found"
    fi
else
    echo "   ❌ proc_autocode/coder.py not found"
fi

echo ""

echo "7. Comparing v3 vs v4 key files..."
echo "   Files changed in v4:"
git diff v3..HEAD --name-only 2>/dev/null | grep -E "(api|modules/api|proc_autocode)" | head -10 || echo "   (Cannot compare with v3)"

echo ""

echo "=== Summary ==="
if [ $DEPRECATED_FOUND -eq 0 ]; then
    echo "✅ All checks passed - enhancements appear to be integrated"
else
    echo "⚠️  Some deprecated files may need cleanup"
fi

echo ""
echo "To see full diff: git diff v3..v4"
echo "To see new files: git diff v3..v4 --name-status | grep '^A'"











