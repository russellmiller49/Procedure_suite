# Procedure Suite Migration Guide

## Purpose
This guide maps the repository reorganization from legacy paths to the new structure and records the finalized canonical paths after legacy wrappers were removed.

## Target Top-Level Layout

```text
app/      # Runtime application code
ui/       # Consolidated UI assets + source
ml/       # ML libraries, training, evaluation, data-prep
ops/      # Operational scripts and tooling
tests/    # Test suite
archive/  # Deprecated, one-off, and historical artifacts
```

## 1) Runtime Code Migration (`modules/*` -> `app/*`)

### Primary runtime packages
| Legacy path | New canonical path |
|---|---|
| `modules/api` | `app/api` |
| `modules/coder` | `app/coder` |
| `modules/registry` | `app/registry` |
| `modules/reporter` | `app/reporter` |
| `modules/reporting` | `app/reporting` |
| `modules/domain` | `app/domain` |
| `modules/phi` | `app/phi` |
| `modules/common` | `app/common` |
| `modules/agents` | `app/agents` |

### Additional runtime packages moved
| Legacy path | New canonical path |
|---|---|
| `modules/autocode` | `app/autocode` |
| `modules/extraction` | `app/extraction` |
| `modules/infra` | `app/infra` |
| `modules/llm` | `app/llm` |
| `modules/ner` | `app/ner` |
| `modules/proc_ml_advisor` | `app/proc_ml_advisor` |
| `modules/registry_cleaning` | `app/registry_cleaning` |
| `modules/registry_store` | `app/registry_store` |

### Import migration
- Replace `from modules.<pkg>...` -> `from app.<pkg>...` for runtime code.
- Example: `from modules.api.fastapi_app import app` -> `from app.api.fastapi_app import app`.

## 2) UI Consolidation

| Legacy path | New canonical path |
|---|---|
| `modules/api/static` | `ui/static` |
| `frontend` | `ui/source` |
| `frontend/registry_grid` | `ui/source/registry_grid` |
| `updated IU componenets` | `archive/potential_ui_updates/updated_IU_components` |

### Notes
- Server static references now resolve to `ui/static`.
- The current Vite source tree lives at `ui/source/registry_grid`.

## 3) ML Separation (`modules/ml_coder` and training scripts)

| Legacy path | New canonical path |
|---|---|
| `modules/ml_coder` | `ml/lib/ml_coder` |
| training/eval scripts in `scripts/` | `ml/scripts/` |
| training data helpers and migration data | `ml/data/` |

### Import migration
- Replace `modules.ml_coder` -> `ml.lib.ml_coder`.
- Example: `from modules.ml_coder.registry_predictor import RegistryMLPredictor` -> `from ml.lib.ml_coder.registry_predictor import RegistryMLPredictor`.

### Artifact compatibility note
- Legacy model artifacts were regenerated so serialized references now resolve to canonical modules (`ml.lib.ml_coder.*`).

## 4) Ops and Tooling Split

| Legacy path | New canonical path |
|---|---|
| `scripts/devserver.sh` | `ops/devserver.sh` |
| `scripts/railway_start.sh` | `ops/railway_start.sh` |
| `scripts/railway_start_gunicorn.sh` | `ops/railway_start_gunicorn.sh` |
| `scripts/preflight.py` | `ops/preflight.py` |
| `scripts/warm_models.py` | `ops/warm_models.py` |
| infra/tooling scripts in `scripts/` | `ops/tools/` |

### Entrypoint policy
- Use canonical entrypoints directly (`ops/*`, `ops/tools/*`, `ml/scripts/*`).

## 5) Scripts Reclassification

### ML-focused scripts
Moved under `ml/scripts` (examples):
- `train_*.py`
- `evaluate_*.py` / `eval_*.py`
- `prepare_data.py`
- `split_phi_gold.py`
- `distill_*.py`

### One-off or throwaway scripts
Archived under `archive/scripts` (examples):
- `test_debulk.py`
- `debug_ner.py`
- `add_case_*.py`

### Compatibility behavior
- Legacy `scripts/*` forwarding wrappers are removed in the finalized migration.

## 6) Archive / Attic Mapping

| Legacy source | New canonical path |
|---|---|
| `legacy_files/` | `archive/legacy_files/` |
| one-off scripts | `archive/scripts/` |
| root clutter (`*.txt`, `gitingest*.md`, `stats.json`, logs) | `archive/root_clutter/` |
| potential UI experiments (`updated IU componenets`) | `archive/potential_ui_updates/updated_IU_components/` |

## 7) High-Impact Path Changes to Update in Integrations

1. Python imports:
   - `modules.*` -> `app.*`
   - `modules.ml_coder.*` -> `ml.lib.ml_coder.*`
2. Static asset assumptions:
   - `modules/api/static/...` -> `ui/static/...`
3. Script references in docs/CI:
   - Prefer canonical locations under `ops/` and `ml/scripts/`
   - Do not rely on legacy `scripts/*` wrappers.

## 8) Recommended Migration Checklist

1. Update all direct imports to canonical `app/*` and `ml/lib/*` paths.
2. Update any hardcoded static UI paths to `ui/static`.
3. Validate command references:
   - runtime ops from `ops/*`
   - ML/training from `ml/scripts/*`
4. Verify downstream consumers no longer depend on legacy wrapper paths.
5. Run regression suite: `make test`.

## 9) Current Status

- Reorg is active with canonical roots: `app/`, `ui/`, `ml/`, `ops/`, `archive/`.
- Legacy `modules/` compatibility shim is removed.
- Legacy `scripts/*` forwarding wrappers are removed.
