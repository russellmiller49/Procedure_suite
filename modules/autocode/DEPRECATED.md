# ⚠️ DEPRECATED: proc_autocode Module

**This folder contains legacy code that is NOT actively maintained in this branch.**

## Status

The `proc_autocode` module (including `EnhancedCPTCoder`, `ip_kb`, `rvu`) is preserved
for reference and backward compatibility with the legacy Git branch, but it is **not
used by the active API pipeline** in this branch.

## New Architecture

The canonical implementation for CPT coding now lives in the hexagonal architecture:

| Component | Legacy Location | New Location |
|-----------|-----------------|--------------|
| Coder service | `proc_autocode/coder.py` → `EnhancedCPTCoder` | `modules/coder/application/coding_service.py` → `CodingService` |
| Knowledge base | `proc_autocode/ip_kb/` | `modules/domain/knowledge_base/` + `data/knowledge/*.json` |
| LLM integration | `modules/coder/llm_coder.py` | `modules/coder/adapters/llm/gemini_advisor.py` → `LLMAdvisorPort` |
| RVU data | `proc_autocode/rvu/` | `data/RVU_files/` (standalone CSV files) |
| Rules engine | `proc_autocode/ip_kb/canonical_rules.py` | `modules/domain/coding_rules/` |

## Do Not

- ❌ Do not add new rules or codes to `proc_autocode/ip_kb/`
- ❌ Do not import `EnhancedCPTCoder` in new code
- ❌ Do not reference `proc_autocode` from `modules/api/*` or `modules/coder/application/*`

## If You Need To...

- **Add a new CPT code**: Update `data/knowledge/ip_coding_billing_v2_8.json`
- **Modify coding rules**: Update `modules/domain/coding_rules/`
- **Update RVU data**: Update files in `data/RVU_files/`
- **Modify LLM prompts**: Update `modules/coder/adapters/llm/gemini_advisor.py`

## Tests

Some legacy tests in `tests/coder/test_*.py` still reference `proc_autocode` for
regression testing against historical behavior. These tests should be gradually
migrated to use `CodingService` instead.
