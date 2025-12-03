# v4 Branch Cleanup Guide

## Overview

This guide helps you clean up the v4 branch by removing deprecated files that are no longer needed. **All files are safely preserved in the v3 branch on GitHub**, so you can safely delete them from v4.

## Verification: All Enhancements Are Integrated ✅

Run the verification script to confirm all v4 enhancements are in the enhanced version:

```bash
./scripts/verify_v4_enhancements.sh
```

**Current Status:**
- ✅ EnhancedCPTCoder is used in main app
- ✅ Not using old CoderEngine  
- ✅ RVU calculator integrated
- ✅ Frontend displays RVU data
- ✅ EnhancedCPTCoder exists

## Files That Can Be Safely Removed

### 1. `api/enhanced_coder_routes.py` ⚠️
**Status**: Routes are now integrated into `modules/api/fastapi_app.py`
**Action**: Can be removed (routes are no longer separate)

**Verification:**
```bash
# Check if it's still imported
grep -r "enhanced_coder_routes" modules/api/fastapi_app.py
# Should return nothing (not imported)
```

### 2. `api/app.py` ❌
**Status**: Deprecated, marked with warning header
**Action**: Can be removed (not used, main app is `modules/api/fastapi_app.py`)

**Verification:**
```bash
# Check if it's used anywhere
grep -r "from api.app import\|import api.app" .
# Should return nothing
```

## Files to Keep (Even if Modified)

### `modules/coder/engine.py` ⚠️
**Status**: Legacy but may still be used by tests or CLI
**Action**: Keep for now, but don't use in new code

### `modules/api/fastapi_app.py` ✅
**Status**: Main application - DO NOT REMOVE
**Action**: This is the active FastAPI app

### `proc_autocode/coder.py` ✅
**Status**: Enhanced coder implementation - DO NOT REMOVE
**Action**: This is the active coder

## Automated Cleanup

Run the cleanup script:

```bash
./scripts/cleanup_v4_branch.sh
```

This script will:
1. Check which deprecated files exist
2. Verify they're not being used
3. Ask for confirmation before removing
4. Remove only safe-to-delete files

## Manual Cleanup Steps

If you prefer to do it manually:

### Step 1: Verify Files Are Not Used

```bash
# Check if enhanced_coder_routes is imported
grep -r "enhanced_coder_routes" modules/api/

# Check if api/app.py is imported anywhere
grep -r "from api.app\|import api.app" .
```

### Step 2: Remove Deprecated Files

```bash
# Remove deprecated files
rm api/enhanced_coder_routes.py
rm api/app.py

# Verify they're gone
git status
```

### Step 3: Test Everything Still Works

```bash
# Start server
./scripts/devserver.sh

# In another terminal, test API
curl http://localhost:8000/
curl -X POST http://localhost:8000/v1/coder/run \
  -H "Content-Type: application/json" \
  -d '{"note": "test", "locality": "00", "setting": "facility"}'
```

### Step 4: Commit Changes

```bash
git add -A
git commit -m "Remove deprecated files from v4 branch

- Removed api/app.py (deprecated, main app is modules/api/fastapi_app.py)
- Removed api/enhanced_coder_routes.py (routes integrated into main app)
- All files preserved in v3 branch on GitHub"
```

## Comparison: v3 vs v4

To see what's different between branches:

```bash
# See all changes
git diff v3..v4 --stat

# See new files
git diff v3..v4 --name-status | grep '^A'

# See modified files
git diff v3..v4 --name-status | grep '^M'
```

## Key Enhancements in v4

All of these are integrated into the enhanced version:

1. **EnhancedCPTCoder** (`proc_autocode/coder.py`)
   - ✅ Integrated into `modules/api/fastapi_app.py`
   - ✅ Uses IP knowledge base for code detection
   - ✅ Includes RVU calculations

2. **RVU Calculator** (`proc_autocode/rvu/`)
   - ✅ Integrated and working
   - ✅ Frontend displays RVU data

3. **Frontend Enhancements** (`modules/api/static/`)
   - ✅ Locality and setting inputs
   - ✅ RVU display in results

4. **API Consolidation**
   - ✅ Single FastAPI app (`modules/api/fastapi_app.py`)
   - ✅ All routes in one place

## Safety: Files Are Preserved in v3

**Important**: All files you remove from v4 are still in v3 branch on GitHub:

```bash
# Verify files exist in v3
git show v3:api/app.py > /dev/null && echo "✅ api/app.py exists in v3"
git show v3:api/enhanced_coder_routes.py > /dev/null && echo "✅ enhanced_coder_routes.py exists in v3"
```

## After Cleanup

1. ✅ Run verification: `./scripts/verify_v4_enhancements.sh`
2. ✅ Test the application: `./scripts/devserver.sh`
3. ✅ Check git status: `git status`
4. ✅ Commit changes if satisfied

## Questions?

- See `AI_ASSISTANT_GUIDE.md` for architecture details
- See `MERGING_CHANGES.md` for merging guidance
- Run `./scripts/verify_active_app.sh` to check current state

---

**Remember**: v3 branch on GitHub preserves all old files. You can safely clean up v4!


