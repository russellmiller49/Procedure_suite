# Archive

This folder contains outdated scripts, documents, and files that are no longer actively used but kept for reference.

**Archived on:** December 17, 2025

## Contents

### scripts/
Superseded or one-time scripts:

| File | Reason |
|------|--------|
| `Smart_splitter_updated.py` | Superseded by `scripts/Smart_splitter.py` |
| `Smart_splitter_updated_v2.py` | Superseded by `scripts/Smart_splitter.py` |
| `clean_and_split_data_updated.py` | Superseded by `scripts/clean_and_split_data.py` |
| `clean_and_split_data_updated_v2.py` | Superseded by `scripts/clean_and_split_data.py` |
| `data_generators_updated.py` | Superseded by `scripts/data_generators.py` |
| `data_generators_updated_v2.py` | Superseded by `scripts/data_generators.py` |
| `apply_patch.py` | One-time patch script |
| `cleanup_v4_branch.sh` | One-time v4 migration script |
| `verify_active_app.sh` | One-time verification script |
| `verify_v4_enhancements.sh` | One-time v4 verification script |
| `fix_ml_data.py` | One-time data fix |
| `fix_registry_data.py` | One-time data fix |
| `immediate_csv_fix.py` | One-time CSV fix |
| `run_cleaning_pipeline.py` | Superseded by updated pipeline |
| `validate_registry2.py` | Superseded by `validate_golden_extractions.py` |
| `data_generators.py` | Superseded by `modules/ml_coder/data_prep.py` |
| `clean_and_split_data.py` | Superseded by `modules/ml_coder/data_prep.py` |
| `Smart_splitter.py` | Superseded by `modules/ml_coder/data_prep.py` |
| `clean_ip_registry.py` | One-time registry cleanup script |

### docs/
Completed plans and temporary files:

| File | Reason |
|------|--------|
| `CODEX_IMPLEMENTATION_PLAN.md` | Completed implementation plan |
| `CODEX_IMPLEMENTATION_PLAN_v5_POST.md` | Completed implementation plan |
| `CODEX_PR_CHECKLIST.md` | Completed PR checklist |
| `Validation_fix_plan_12_6_25.md` | Completed validation fix plan |
| `main v13._diff.txt` | Temporary diff file |

### root/
Test/utility scripts that were in the repo root:

| File | Reason |
|------|--------|
| `geminiquota.py` | Gemini quota checking utility |
| `test_gemini_simple.py` | Simple Gemini test script |

### knowledge/
Outdated knowledge base files:

| File | Reason |
|------|--------|
| `ip_coding_billing_v2_8.json` | Superseded by `data/knowledge/ip_coding_billing_v2_9.json` |

## Restoring Files

If you need to restore any file, simply move it back to its original location:

```bash
# Example: restore a script
mv archive/scripts/some_script.py scripts/

# Example: restore a doc
mv archive/docs/some_doc.md docs/

# Example: restore a knowledge file
mv archive/knowledge/ip_coding_billing_v2_8.json data/knowledge/
```
