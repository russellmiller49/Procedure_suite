# Registry Schema Refactor Notes (2026-01-25)

## Goals
- Remove duplicated model definitions (notably EBUS node-event types).
- Separate granular schema models from derivation logic.
- Keep `modules.registry.schema` and `modules.registry.schema_granular` import paths stable.
- Reduce “two `ip_v3.py`” ambiguity by naming the extraction schema explicitly.

## Inventory (repo-wide searches, pre-change)
- `modules.registry.schema.ip_v3` / `schema.ip_v3` imports found in:
  - `scripts/ingest_phase0_data.py`
  - `scripts/eval_registry_granular.py`
  - `modules/registry/extractors/v3_extractor.py`
  - `modules/registry/evidence/verifier.py`
  - `modules/registry/adapters/v3_to_v2.py`
  - `modules/registry/pipelines/v3_pipeline.py`
  - `docs/REGISTRY_V3_IMPLEMENTATION_GUIDE.md`
- `NodeInteraction` / `NodeActionType` / `NodeOutcomeType` definitions found in:
  - `modules/registry/schema.py`
  - `proc_schemas/registry/ip_v3.py`
- `schema_granular` imports found across runtime + tests (examples):
  - `modules/registry/schema.py`
  - `modules/registry/application/registry_service.py`
  - `modules/api/normalization.py`
  - `modules/registry/postprocess.py`
  - `tests/registry/test_granular_registry_models.py`

## File operations
**Added**
- `proc_schemas/shared/__init__.py`
- `proc_schemas/shared/ebus_events.py`
- `modules/registry/schema/ebus_events.py` (re-export)
- `modules/registry/schema/granular_logic.py`
- `modules/registry/schema_granular.py` (compat shim)
- `modules/registry/schema/ip_v3.py` (compat stub)
- `modules/registry/schema.py` (thin entrypoint wrapper)
- `modules/registry/adapters/v3_to_v2.py` (compat shim)
- `tests/registry/test_schema_refactor_smoke.py`

**Moved/Renamed**
- `modules/registry/schema_granular.py` → `modules/registry/schema/granular_models.py`
- `modules/registry/schema.py` → `modules/registry/schema/v2_dynamic.py`
- `modules/registry/schema/ip_v3.py` → `modules/registry/schema/ip_v3_extraction.py`
- `modules/registry/adapters/v3_to_v2.py` → `modules/registry/schema/adapters/v3_to_v2.py`

## Import changes (high level)
- EBUS node-event primitives:
  - Canonical: `proc_schemas.shared.ebus_events`
  - Registry-layer re-export: `modules.registry.schema.ebus_events`
- Granular models/logic:
  - Models: `modules.registry.schema.granular_models`
  - Logic: `modules.registry.schema.granular_logic`
  - Stable compat import path kept: `modules.registry.schema_granular`
- V2 dynamic RegistryRecord builder:
  - Implementation: `modules.registry.schema.v2_dynamic`
  - Stable entrypoint kept: `modules.registry.schema`
- V3 extraction event-log schema:
  - Implementation: `modules.registry.schema.ip_v3_extraction`
  - Old import kept: `modules.registry.schema.ip_v3` (compat re-export)
- V3 → V2 projection:
  - Implementation: `modules.registry.schema.adapters.v3_to_v2`
  - Old import kept: `modules.registry.adapters.v3_to_v2` (compat shim)

## Compatibility constraints verified
- No `modules/registry/schema/__init__.py` added (preserves `schema.py` import resolution).
- `modules.registry.schema` remains importable and supports `modules.registry.schema.<submodule>` via `__path__`.
- `modules.registry.schema_granular` remains importable and exports the same names.

