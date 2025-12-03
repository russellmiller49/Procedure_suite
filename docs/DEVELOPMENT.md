# Development Guide

This document is the **Single Source of Truth** for developers and AI assistants working on the Procedure Suite.

## 🎯 Core Mandates

1.  **Main Application**: Always edit `modules/api/fastapi_app.py`. Never edit `api/app.py` (deprecated).
2.  **Enhanced Coder**: Use `proc_autocode.coder.EnhancedCPTCoder`. Do not use `modules.coder.engine.CoderEngine`.
3.  **Knowledge Base**: The source of truth for coding rules is `data/knowledge/ip_coding_billing.v2_7.json`.
4.  **Tests**: Preserve existing tests. Run `make test` before committing.

---

## 🏗️ System Architecture

### Directory Structure

| Directory | Status | Purpose |
|-----------|--------|---------|
| `modules/api/` | ✅ **ACTIVE** | Main FastAPI app (`fastapi_app.py`) |
| `proc_autocode/` | ✅ **ACTIVE** | CPT Coding Engine (`coder.py`, `ip_kb/`, `rvu/`) |
| `proc_report/` | ✅ **ACTIVE** | Reporter Engine (templates, validation, inference) |
| `modules/registry/`| ✅ **ACTIVE** | Registry Extraction logic (LLM extractors) |
| `proc_registry/` | ✅ **ACTIVE** | Adapters for export/schema conversion |
| `api/` | ❌ **DEPRECATED**| Old API entry point. Do not use. |

### Data Flow

```
[Procedure Note]
       │
       ▼
[API Layer] (modules/api/fastapi_app.py)
       │
       ├─> [Registry Engine] ──> [LLM Extraction] ──> [Structured Record]
       │
       ├─> [CPT Coder] ──────> [EnhancedCPTCoder] ──> [Codes + RVUs]
       │                          (Uses ip_coding_billing.v2_7.json)
       │
       └─> [Reporter] ───────> [Jinja Templates] ───> [Synoptic Report]
```

---

## 🤖 AI Agent Roles

### 1. Coder Agent
**Focus**: `proc_autocode/`
- Maintain `EnhancedCPTCoder`.
- Update rules in `proc_autocode/ip_kb/ip_kb.py` or `data/knowledge/ip_coding_billing.v2_7.json`.
- Ensure RVU calculations are correct (`proc_autocode/rvu/`).
- **Rule**: Do not scatter logic. Keep it central in the Knowledge Base or `ip_kb.py`.

### 2. Registry Agent
**Focus**: `modules/registry/` & `proc_registry/`
- Maintain schema definitions in `modules/registry/schema.py`.
- Update prompts in `modules/registry/prompts.py`.
- **Critical**: Handle LLM list outputs (comma-separated strings) by adding normalizers in `modules/registry/postprocess.py`.

### 3. Reporter Agent
**Focus**: `proc_report/`
- Edit templates in `proc_report/templates/`.
- Maintain validation logic (`validation.py`) and inference logic (`inference.py`).
- **Rule**: Use `{% if %}` guards in templates. Never output "None" or "missing" in final reports.

### 4. DevOps/API Agent
**Focus**: `modules/api/`
- Maintain `fastapi_app.py`.
- Ensure endpoints `/v1/coder/run`, `/v1/registry/run`, `/report/render` are working.
- **Warning**: Do not create duplicate routes. Check existing endpoints first.

---

## 🔄 Merging & Workflow

### Working with Multiple Versions
If you encounter code that seems to use `api/app.py` or `CoderEngine`:
1.  **Stop**. Do not edit those files.
2.  **Migrate** valuable logic to `modules/api/fastapi_app.py` or `proc_autocode/coder.py`.
3.  **Verify** using `./scripts/verify_active_app.sh`.

### Testing
- **Unit Tests**: `make test`
- **Contract Tests**: `make contracts`
- **Pre-flight**: `make preflight`
- **Linting**: `make lint`

**Note on LLM Tests**: By default, tests run in offline mode. To test actual extraction:
```bash
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="..."
pytest tests/registry/test_extraction.py
```

---

## 📝 Development Checklist

Before committing changes:
- [ ] I am editing `modules/api/fastapi_app.py` (not `api/app.py`).
- [ ] I am using `EnhancedCPTCoder`.
- [ ] I have run `make test` (or relevant unit tests).
- [ ] I have checked `scripts/devserver.sh` to ensure the app starts.
- [ ] I have not committed any PHI (Real patient data).
