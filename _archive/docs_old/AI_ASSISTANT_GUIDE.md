# AI Assistant Guide - Source of Truth

**Last Updated**: 2024-12-23

This document specifies the **single source of truth** for AI assistants (Codex, Gemini CLI, Claude, Cursor, etc.) working on this codebase.

## 🎯 CRITICAL: Which Files to Edit

### ✅ MAIN FastAPI Application (USE THIS)
- **File**: `modules/api/fastapi_app.py`
- **Status**: ✅ **ACTIVE - This is the running application**
- **Port**: 8000 (via `scripts/devserver.sh`)
- **Coder**: Uses `EnhancedCPTCoder` from `proc_autocode/coder.py`
- **Routes**: `/v1/coder/run`, `/v1/registry/run`, `/v1/coder/localities`, etc.

### ❌ OLD FastAPI Application (DO NOT USE)
- **File**: `api/app.py`
- **Status**: ❌ **DEPRECATED - Not running, do not edit**
- **Note**: This file exists but is not used. Any changes here will be ignored.

## 📍 Key Files and Their Status

### FastAPI & API Layer
| File | Status | Purpose |
|------|--------|---------|
| `modules/api/fastapi_app.py` | ✅ **MAIN** | Primary FastAPI application (running on port 8000) |
| `api/app.py` | ❌ **IGNORE** | Old/unused FastAPI app - do not edit |
| `api/enhanced_coder_routes.py` | ⚠️ **DEPRECATED** | Routes now integrated into main app |
| `modules/api/schemas.py` | ✅ **MAIN** | API request/response schemas |
| `modules/api/static/` | ✅ **MAIN** | Frontend UI files |

### Coder Implementation
| File | Status | Purpose |
|------|--------|---------|
| `proc_autocode/coder.py` | ✅ **MAIN** | EnhancedCPTCoder - used by API |
| `modules/coder/engine.py` | ⚠️ **LEGACY** | Old CoderEngine - being phased out |
| `modules/coder/schema.py` | ✅ **MAIN** | CoderOutput schema definitions |

### Server Startup
| File | Status | Purpose |
|------|--------|---------|
| `scripts/devserver.sh` | ✅ **MAIN** | Starts the server: `uvicorn modules.api.fastapi_app:app` |
| `user_guide.md` | ✅ **REFERENCE** | Shows: `uvicorn modules.api.fastapi_app:app --reload` |

## 🔍 How to Verify You're Working on the Right Version

### 1. Check Which Server is Running
```bash
ps aux | grep uvicorn
# Should show: uvicorn modules.api.fastapi_app:app
```

### 2. Check Active Routes
```bash
curl http://localhost:8000/ | jq
# Should show version "0.2.0" and note about EnhancedCPTCoder
```

### 3. Check Which Coder is Used
```bash
grep -n "EnhancedCPTCoder\|CoderEngine" modules/api/fastapi_app.py
# Should show: EnhancedCPTCoder (not CoderEngine)
```

## 📝 Rules for AI Assistants

### ✅ DO:
1. **Edit `modules/api/fastapi_app.py`** for API changes
2. **Edit `proc_autocode/coder.py`** for coder logic
3. **Edit `modules/api/static/`** for frontend changes
4. **Check `scripts/devserver.sh`** to see how the server starts
5. **Read `agents.md`** for detailed module structure

### ❌ DON'T:
1. **Don't edit `api/app.py`** - it's not used
2. **Don't create new FastAPI apps** - use the existing one
3. **Don't use `CoderEngine`** - use `EnhancedCPTCoder`
4. **Don't create duplicate routes** - check existing routes first

## 🔄 Current Architecture (v0.2.0)

```
┌─────────────────────────────────────────┐
│  modules/api/fastapi_app.py (MAIN)     │
│  ┌───────────────────────────────────┐   │
│  │  /v1/coder/run                   │   │
│  │  └─> EnhancedCPTCoder           │   │
│  │  /v1/coder/localities            │   │
│  │  /v1/registry/run                │   │
│  │  /report/verify                   │   │
│  │  /report/render                   │   │
│  └───────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  proc_autocode/coder.py                  │
│  └─> EnhancedCPTCoder                    │
│      ├─> IP Knowledge Base               │
│      └─> RVU Calculator                  │
└─────────────────────────────────────────┘
```

## 🚨 Common Mistakes to Avoid

1. **Editing the wrong FastAPI app**
   - ❌ Wrong: Editing `api/app.py`
   - ✅ Right: Editing `modules/api/fastapi_app.py`

2. **Using the wrong coder**
   - ❌ Wrong: `from modules.coder.engine import CoderEngine`
   - ✅ Right: `from proc_autocode.coder import EnhancedCPTCoder`

3. **Creating duplicate routes**
   - ❌ Wrong: Adding `/proc/enhanced/*` routes
   - ✅ Right: Use existing `/v1/coder/run` endpoint

4. **Not checking what's running**
   - ❌ Wrong: Assuming changes are live
   - ✅ Right: Check `ps aux | grep uvicorn` and verify routes

## 📋 Quick Reference Checklist

Before making changes, verify:
- [ ] I'm editing `modules/api/fastapi_app.py` (not `api/app.py`)
- [ ] I'm using `EnhancedCPTCoder` (not `CoderEngine`)
- [ ] I've checked existing routes to avoid duplicates
- [ ] I've tested the changes with the running server
- [ ] I've updated this guide if I changed the architecture

## 🔗 Related Documentation

- `agents.md` - Detailed agent instructions and module structure
- `user_guide.md` - User-facing documentation
- `README.md` - Project overview
- `GEMINI_SETUP.md` - Gemini API configuration

## 📞 If You're Unsure

1. Check `scripts/devserver.sh` - shows what's actually running
2. Check `modules/api/fastapi_app.py` - this is the main app
3. Run `curl http://localhost:8000/` - see current API version
4. Read `agents.md` - comprehensive module documentation

---

**Remember**: When in doubt, check `modules/api/fastapi_app.py` - that's the source of truth!


