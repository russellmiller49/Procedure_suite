# Registry Schema Refactor Notes (2026-01-25)

## Goals
- Remove duplicated model definitions (notably EBUS node-event types).
- Separate granular schema models from derivation logic.
- Keep `app.registry.schema` and `app.registry.schema_granular` import paths stable.
- Reduce “two `ip_v3.py`” ambiguity by naming the extraction schema explicitly.

## Inventory (repo-wide searches, pre-change)
- `app.registry.schema.ip_v3` / `schema.ip_v3` imports found in:
  - `scripts/ingest_phase0_data.py`
  - `scripts/eval_registry_granular.py`
  - `app/registry/extractors/v3_extractor.py`
  - `app/registry/evidence/verifier.py`
  - `app/registry/adapters/v3_to_v2.py`
  - `app/registry/pipelines/v3_pipeline.py`
  - `docs/REGISTRY_V3_IMPLEMENTATION_GUIDE.md`
- `NodeInteraction` / `NodeActionType` / `NodeOutcomeType` definitions found in:
  - `app/registry/schema.py`
  - `proc_schemas/registry/ip_v3.py`
- `schema_granular` imports found across runtime + tests (examples):
  - `app/registry/schema.py`
  - `app/registry/application/registry_service.py`
  - `app/api/normalization.py`
  - `app/registry/postprocess.py`
  - `tests/registry/test_granular_registry_models.py`

## File operations
**Added**
- `proc_schemas/shared/__init__.py`
- `proc_schemas/shared/ebus_events.py`
- `app/registry/schema/ebus_events.py` (re-export)
- `app/registry/schema/granular_logic.py`
- `app/registry/schema_granular.py` (compat shim)
- `app/registry/schema/ip_v3.py` (compat stub)
- `app/registry/schema.py` (thin entrypoint wrapper)
- `app/registry/adapters/v3_to_v2.py` (compat shim)
- `tests/registry/test_schema_refactor_smoke.py`

**Moved/Renamed**
- `app/registry/schema_granular.py` → `app/registry/schema/granular_models.py`
- `app/registry/schema.py` → `app/registry/schema/v2_dynamic.py`
- `app/registry/schema/ip_v3.py` → `app/registry/schema/ip_v3_extraction.py`
- `app/registry/adapters/v3_to_v2.py` → `app/registry/schema/adapters/v3_to_v2.py`

## Import changes (high level)
- EBUS node-event primitives:
  - Canonical: `proc_schemas.shared.ebus_events`
  - Registry-layer re-export: `app.registry.schema.ebus_events`
- Granular models/logic:
  - Models: `app.registry.schema.granular_models`
  - Logic: `app.registry.schema.granular_logic`
  - Stable compat import path kept: `app.registry.schema_granular`
- V2 dynamic RegistryRecord builder:
  - Implementation: `app.registry.schema.v2_dynamic`
  - Stable entrypoint kept: `app.registry.schema`
- V3 extraction event-log schema:
  - Implementation: `app.registry.schema.ip_v3_extraction`
  - Old import kept: `app.registry.schema.ip_v3` (compat re-export)
- V3 → V2 projection:
  - Implementation: `app.registry.schema.adapters.v3_to_v2`
  - Old import kept: `app.registry.adapters.v3_to_v2` (compat shim)

## Compatibility constraints verified
- No `app/registry/schema/__init__.py` added (preserves `schema.py` import resolution).
- `app.registry.schema` remains importable and supports `app.registry.schema.<submodule>` via `__path__`.
- `app.registry.schema_granular` remains importable and exports the same names.

