#!/usr/bin/env bash
# Verification script to check which FastAPI app is active

echo "=== Procedure Suite - Active App Verification ==="
echo ""

# Check running server
echo "1. Checking running server..."
if pgrep -f "uvicorn.*fastapi_app" > /dev/null; then
    RUNNING=$(ps aux | grep "uvicorn.*fastapi_app" | grep -v grep | head -1)
    if echo "$RUNNING" | grep -q "modules.api.fastapi_app"; then
        echo "   ✅ CORRECT: Running modules.api.fastapi_app"
    else
        echo "   ❌ WRONG: Running different app"
        echo "   $RUNNING"
    fi
else
    echo "   ⚠️  No server running"
fi

echo ""

# Check API version
echo "2. Checking API version..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    VERSION=$(curl -s http://localhost:8000/ | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'unknown'))" 2>/dev/null)
    if [ "$VERSION" = "0.3.0" ]; then
        echo "   ✅ CORRECT: API version 0.3.0 (CodingService hexagonal architecture)"
    else
        echo "   ⚠️  API version: $VERSION (expected 0.3.0)"
    fi
else
    echo "   ⚠️  Cannot connect to API (server may not be running)"
fi

echo ""

# Check which coder is imported
echo "3. Checking coder implementation..."
if grep -q "CodingService" modules/api/fastapi_app.py && grep -q "get_coding_service" modules/api/fastapi_app.py; then
    echo "   ✅ CORRECT: Using CodingService (hexagonal architecture)"
else
    echo "   ❌ WRONG: Not using CodingService"
fi

if grep -q "EnhancedCPTCoder" modules/api/fastapi_app.py; then
    echo "   ❌ ERROR: Still importing legacy EnhancedCPTCoder"
fi

if grep -q "CoderEngine" modules/api/fastapi_app.py && ! grep -q "#.*CoderEngine" modules/api/fastapi_app.py; then
    echo "   ⚠️  WARNING: Still importing CoderEngine (may be legacy)"
fi

echo ""

# Check for deprecated app
echo "4. Checking for deprecated files..."
if [ -f "api/app.py" ]; then
    if grep -q "DEPRECATED" api/app.py; then
        echo "   ✅ api/app.py is marked as deprecated"
    else
        echo "   ⚠️  api/app.py exists but not marked as deprecated"
    fi
fi

echo ""
echo "=== Summary ==="
echo "Active app: modules/api/fastapi_app.py"
echo "Deprecated: api/app.py"
echo ""
echo "For details, see: AI_ASSISTANT_GUIDE.md"






