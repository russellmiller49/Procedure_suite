# Repo Index — Procedure Suite

This is a **high-signal map** of the repository: where the main entrypoints live, what each top-level folder is for, and which files to touch for common changes.

## Top-level layout (what lives where)

- **`modules/`**: Core runtime code (API, pipeline services, domain logic).
- **`data/`**: Knowledge, models, training data, and large corpora used by pipelines.
- **`configs/`**: Config files used by the structured reporter (template configs + Jinja).
- **`proc_schemas/`**: Pydantic schemas (registry v2/v3, coding schemas, shared types).
- **`config/`**: Runtime settings (`pydantic-settings`) and configuration helpers.
- **`scripts/`**: Dev scripts, evaluation utilities, CLI helpers.
- **`tests/`**: Test suites (coder, registry, reporter, etc.).
- **`docs/`**: Documentation (guides, architecture notes, workflows).

## Run / entrypoints

- **Dev server**: `./scripts/devserver.sh`
  - Starts `uvicorn modules.api.fastapi_app:app` with reload.
  - Sets `PSUITE_KNOWLEDGE_FILE` (defaults to `data/knowledge/ip_coding_billing_v3_0.json`).

- **Main FastAPI app**: `modules/api/fastapi_app.py`
  - Wires routers, readiness/warmup, serves UI at `/ui/`.

## Primary API surface (what the UI hits)

- **Unified pipeline endpoint**: `POST /api/v1/process`
  - Implementation: `modules/api/routes/unified_process.py`
  - Flow (high level):
    - Optional PHI redaction (server-side if `already_scrubbed=false`)
    - Registry extraction via `RegistryService`
    - Deterministic registry→CPT derivation (and enrichment for UI)
    - Response shaping + evidence payload for UI highlighting

## Core pipelines (where the “real work” happens)

### Registry extraction

- **Service/orchestrator**: `modules/registry/application/registry_service.py`
  - Entry points: `RegistryService.extract_fields(...)` and `extract_fields_extraction_first(...)`
  - Produces a `RegistryRecord` + evidence + CPT codes (depending on mode/engine).

- **LLM engine**: `modules/registry/engine.py`
  - Used when running LLM-based extraction paths.

- **Deterministic/postprocessing guardrails**:
  - `modules/extraction/postprocessing/clinical_guardrails.py`
  - `modules/registry/postprocess.py`
  - `modules/registry/processing/*` (focus/targets/navigation helpers)

### CPT coding

- **Coding orchestrator**: `modules/coder/application/coding_service.py`
  - Drives extraction-first coding (registry → deterministic CPT derivation + audit metadata).

- **Rules + bundling/validation**:
  - `modules/coder/rules_engine.py` (deterministic validation, hierarchy normalization, NCCI bundling gatekeeper)
  - `modules/domain/coding_rules/*` (rule engine + NCCI/MER utilities)

### Structured reporter (synoptic note generation)

- **Renderer**: `modules/reporting/engine.py`
  - Loads template configs from `configs/report_templates/`
  - Renders templates in `modules/reporting/templates/`
  - Uses add-on snippets from `data/knowledge/ip_addon_templates_parsed.json`

- **Template config root**: `configs/report_templates/`
  - Includes `procedure_order.json` and per-procedure YAML/JSON config files.

## Knowledge / “source of truth” assets used at runtime

### Coding + terminology KB

- **Primary KB JSON**: `data/knowledge/ip_coding_billing_v3_0.json`
  - Used by:
    - `modules/common/knowledge.py` (KB loading helpers: RVUs, synonyms, bundling rules, etc.)
    - `modules/coder/adapters/persistence/csv_kb_adapter.py` (CodingService KB repository)
    - `modules/autocode/ip_kb/ip_kb.py` (terminology/synonym-driven group detection)

### Registry schema

- **Canonical schema JSON**: `data/knowledge/IP_Registry.json`
  - Used by legacy/dynamic schema tooling and prompt helpers (see `modules/registry/schema/v2_dynamic.py`, `modules/registry/prompts.py`).
  - Note: V2/V3 Pydantic models are in `proc_schemas/registry/`.

### Bundling / hierarchy configuration

- **NCCI PTP config**: `data/knowledge/ncci_ptp.v1.json` (loaded by `modules/coder/ncci.py`)
- **Code family config**: `data/knowledge/code_families.v1.json` (loaded by `modules/coder/code_families.py`)

### Reporter add-on snippets

- **Add-on templates JSON**: `data/knowledge/ip_addon_templates_parsed.json` (loaded by `modules/reporting/ip_addons.py`)

### Keyword mappings (evidence verification)

- **Mappings dir**: `data/keyword_mappings/*.yaml` (loaded by `modules/coder/adapters/nlp/keyword_mapping_loader.py`)

### RVU locality list (API helper)

- **GPCI CSV**: `data/RVU_files/gpci_2025.csv` (used by `/v1/coder/localities` in `modules/api/fastapi_app.py`)

## UI (PHI redactor / clinical dashboard)

- **Static UI assets**: `modules/api/static/phi_redactor/`
  - Served at `http://localhost:8000/ui/` by `modules/api/fastapi_app.py`.

## Tests (where to look)

- **Coder tests**: `tests/coder/`
- **Registry tests**: `tests/registry/`
- **Reporter tests**: `tests/reporter/`

## “Where do I edit…?”

- **Add/adjust CPT metadata, RVUs, synonyms, bundling rules**: `data/knowledge/ip_coding_billing_v3_0.json`
- **Adjust deterministic coding rules from registry → CPT**: `modules/coder/domain_rules/registry_to_cpt/`
- **Adjust registry extraction behavior / guardrails**: `modules/registry/application/registry_service.py`, `modules/extraction/postprocessing/clinical_guardrails.py`, `modules/registry/postprocess.py`
- **Adjust report output formatting**: `modules/reporting/templates/` (Jinja) and `configs/report_templates/` (template configs)
- **Adjust API shapes/endpoints**: `modules/api/fastapi_app.py`, `modules/api/routes/`

## Related “deeper dive” docs

- **Architecture**: `docs/ARCHITECTURE.md`
- **Development rules**: `docs/DEVELOPMENT.md`
- **Knowledge source-of-truth policy**: `docs/KNOWLEDGE_INVENTORY.md`
- **User guide**: `docs/USER_GUIDE.md`

