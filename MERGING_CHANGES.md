# Merging Changes from Multiple AI Assistants

If Codex and Gemini CLI have been working on different versions, follow this guide to consolidate their changes.

## Quick Check: Which Version is Active?

Run the verification script:
```bash
./scripts/verify_active_app.sh
```

This will tell you:
- Which FastAPI app is running
- Which coder implementation is active
- If deprecated files are being used

## Current Active Version (v0.2.0)

✅ **Active Files:**
- `modules/api/fastapi_app.py` - Main FastAPI application
- `proc_autocode/coder.py` - EnhancedCPTCoder implementation
- `modules/api/static/` - Frontend UI

❌ **Deprecated Files (DO NOT EDIT):**
- `api/app.py` - Old FastAPI app (not running)
- `modules/coder/engine.py` - Old CoderEngine (being phased out)

## How to Merge Changes

### Step 1: Identify Where Changes Were Made

Check git status:
```bash
git status
```

Look for changes in:
- ✅ `modules/api/fastapi_app.py` - Good, this is the active app
- ❌ `api/app.py` - Bad, this is deprecated
- ⚠️ `modules/coder/engine.py` - May need migration to EnhancedCPTCoder

### Step 2: Review Changes in Deprecated Files

If changes were made to `api/app.py`:

1. **Check what was changed:**
   ```bash
   git diff api/app.py
   ```

2. **Determine if the changes are needed:**
   - If it's a new endpoint → Add it to `modules/api/fastapi_app.py`
   - If it's a bug fix → Apply to `modules/api/fastapi_app.py`
   - If it's documentation → Update `AI_ASSISTANT_GUIDE.md`

3. **Migrate the changes:**
   - Copy the logic to `modules/api/fastapi_app.py`
   - Update imports to use `EnhancedCPTCoder` instead of old coder
   - Test the changes

### Step 3: Review Changes in Active Files

If changes were made to `modules/api/fastapi_app.py`:

1. **Verify the changes are correct:**
   ```bash
   git diff modules/api/fastapi_app.py
   ```

2. **Check for conflicts:**
   - Look for duplicate routes
   - Check if EnhancedCPTCoder is still being used
   - Verify no imports of deprecated CoderEngine

3. **Test the changes:**
   ```bash
   # Restart server if needed
   ./scripts/devserver.sh
   
   # Test endpoint
   curl -X POST http://localhost:8000/v1/coder/run \
     -H "Content-Type: application/json" \
     -d '{"note": "test", "locality": "00", "setting": "facility"}'
   ```

### Step 4: Consolidate Coder Changes

If changes were made to both:
- `modules/coder/engine.py` (old)
- `proc_autocode/coder.py` (new)

1. **Review old coder changes:**
   ```bash
   git diff modules/coder/engine.py
   ```

2. **Determine if features need migration:**
   - New intent detection → May need to add to IP knowledge base
   - New bundling rules → Add to `data/knowledge/ip_coding_billing.v2_7.json`
   - RVU calculations → Should already be in EnhancedCPTCoder

3. **Migrate to EnhancedCPTCoder:**
   - Add features to `proc_autocode/coder.py`
   - Update IP knowledge base if needed
   - Test with the active API

## Common Scenarios

### Scenario 1: Changes Only in Active Files ✅
**Status**: Good! Changes are already in the right place.
**Action**: Review and test, then commit.

### Scenario 2: Changes Only in Deprecated Files ❌
**Status**: Changes need migration.
**Action**: 
1. Review what was changed
2. Migrate to active files
3. Test thoroughly
4. Mark deprecated file as reviewed

### Scenario 3: Changes in Both ⚠️
**Status**: Potential conflicts.
**Action**:
1. Compare changes in both files
2. Merge logic into active files
3. Remove or update deprecated file changes
4. Test everything

### Scenario 4: New Files Created
**Status**: Need to verify location.
**Action**:
1. Check if file should be in `modules/` or `proc_*`
2. Verify it's not duplicating existing functionality
3. Update `AI_ASSISTANT_GUIDE.md` if architecture changes

## Verification Checklist

Before committing merged changes:

- [ ] Run `./scripts/verify_active_app.sh` - all checks pass
- [ ] Server starts: `./scripts/devserver.sh`
- [ ] API responds: `curl http://localhost:8000/`
- [ ] Coder endpoint works: `curl -X POST http://localhost:8000/v1/coder/run ...`
- [ ] No imports of deprecated `CoderEngine` in active files
- [ ] No edits to `api/app.py` (or they're marked as deprecated)
- [ ] Documentation updated if architecture changed

## Quick Reference

| Question | Answer |
|----------|--------|
| Which FastAPI app to edit? | `modules/api/fastapi_app.py` |
| Which coder to use? | `proc_autocode.coder.EnhancedCPTCoder` |
| How to verify? | `./scripts/verify_active_app.sh` |
| Where's the guide? | `AI_ASSISTANT_GUIDE.md` |
| How to start server? | `./scripts/devserver.sh` |

## Getting Help

If you're unsure about merging changes:

1. Read `AI_ASSISTANT_GUIDE.md` - comprehensive guide
2. Check `agents.md` - module structure details
3. Run verification script - see current state
4. Review git diff - understand what changed

---

**Remember**: Always work in `modules/api/fastapi_app.py`, never in `api/app.py`!


