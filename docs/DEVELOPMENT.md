# Development Guide

This document is the **Single Source of Truth** for developers and AI assistants working on the Procedure Suite.

## Core Mandates

1.  **Main Application**: Always edit `app/api/fastapi_app.py`. Never edit `api/app.py` (deprecated).
2.  **Coding Service**: Use `CodingService` from `app/coder/application/coding_service.py`. The old `app.coder.engine.CoderEngine` is deprecated.
3.  **Registry Service**: Use `RegistryService` from `app/registry/application/registry_service.py`.
4.  **Knowledge Base**: The source of truth for coding rules is `data/knowledge/ip_coding_billing_v3_0.json`.
5.  **Tests**: Preserve existing tests. Run `make test` before committing.

---

## System Architecture

### Directory Structure

| Directory | Status | Purpose |
|-----------|--------|---------|
| `app/api/` | **ACTIVE** | Main FastAPI app (`fastapi_app.py`) |
| `app/coder/` | **ACTIVE** | CPT Coding Engine with CodingService (8-step pipeline) |
| `app/coder/parallel_pathway/` | **EXPERIMENTAL** | Parallel NER+ML pathway for extraction-first coding |
| `app/ner/` | **EXPERIMENTAL** | Granular NER model (DistilBERT for entity extraction) |
| `ml/lib/ml_coder/` | **ACTIVE** | ML-based code prediction and training |
| `app/registry/` | **ACTIVE** | Registry extraction with RegistryService and RegistryEngine |
| `app/registry/ner_mapping/` | **EXPERIMENTAL** | NER-to-Registry entity mapping |
| `app/agents/` | **ACTIVE** | 3-agent pipeline (Parser, Summarizer, Structurer) |
| `app/reporter/` | **ACTIVE** | Report generation with Jinja templates |
| `app/common/` | **ACTIVE** | Shared utilities, logging, exceptions |
| `app/domain/` | **ACTIVE** | Domain models and business rules |
| `api/` | **DEPRECATED** | Old API entry point. Do not use. |

### Key Services

| Service | Location | Purpose |
|---------|----------|---------|
| `CodingService` | `app/coder/application/coding_service.py` | 8-step CPT coding pipeline |
| `RegistryService` | `app/registry/application/registry_service.py` | Hybrid-first registry extraction |
| `SmartHybridOrchestrator` | `app/coder/application/smart_hybrid_policy.py` | ML-first hybrid coding |
| `RegistryEngine` | `app/registry/engine.py` | LLM-based field extraction |
| `ParallelPathwayOrchestrator` | `app/coder/parallel_pathway/orchestrator.py` | NER+ML parallel pathway (experimental) |
| `GranularNERPredictor` | `app/ner/inference.py` | DistilBERT NER inference |
| `NERToRegistryMapper` | `app/registry/ner_mapping/entity_to_registry.py` | Map NER entities to registry fields |

### Data Flow

```
[Procedure Note]
       │
       ▼
[API Layer] (app/api/fastapi_app.py)
       │
       ├─> [CodingService] ──> [SmartHybridOrchestrator] ──> [Codes + RVUs]
       │        │                    │
       │        │                    ├── ML Prediction
       │        │                    ├── Rules Engine
       │        │                    └── LLM Advisor (fallback)
       │        │
       │        └──> NCCI/MER Compliance ──> Final Codes
       │
       ├─> [RegistryService] ──> [CPT Mapping + LLM Extraction] ──> [Registry Record]
       │
       └─> [Reporter] ──────> [Jinja Templates] ───> [Synoptic Report]
```

---

## AI Agent Roles

### 1. Coder Agent

**Focus**: `app/coder/`

**Key Files:**
- `app/coder/application/coding_service.py` - Main orchestrator
- `app/coder/application/smart_hybrid_policy.py` - Hybrid decision logic
- `app/coder/domain_rules/` - NCCI bundling, domain rules
- `app/coder/rules_engine.py` - Rule-based inference

**Responsibilities:**
- Maintain the 8-step coding pipeline in `CodingService`
- Update domain rules in `app/coder/domain_rules/`
- Ensure NCCI/MER compliance logic is correct
- Keep confidence thresholds tuned in `ml/lib/ml_coder/thresholds.py`

**Rule**: Do not scatter logic. Keep business rules central in the Knowledge Base or `app/coder/domain_rules/`.

### 2. Registry Agent

**Focus**: `app/registry/`

**Key Files:**
- `app/registry/application/registry_service.py` - Main service
- `app/registry/application/cpt_registry_mapping.py` - CPT → registry mapping
- `app/registry/engine.py` - LLM extraction engine
- `app/registry/prompts.py` - LLM prompts
- `app/registry/schema.py` - RegistryRecord model
- `app/registry/v2_booleans.py` - V2→V3 boolean mapping for ML
- `app/registry/postprocess.py` - Output normalization

**Responsibilities:**
- Maintain schema definitions in `schema.py` and `schema_granular.py`
- Update LLM prompts in `prompts.py`
- Handle LLM list outputs by adding normalizers in `postprocess.py`
- Keep CPT-to-registry mapping current in `cpt_registry_mapping.py`
- Update V2→V3 boolean mapping in `v2_booleans.py` when schema changes

**Critical (v3 / extraction-first)**: When changing the registry schema, update:
1. `data/knowledge/IP_Registry.json` - Canonical v3 nested schema (drives dynamic `RegistryRecord`)
2. `app/registry/schema.py` / `app/registry/schema_granular.py` - Custom type overrides + granular helpers
3. `app/registry/v2_booleans.py` - Boolean field list (ML label order)
4. `app/registry/application/cpt_registry_mapping.py` - CPT mappings

Note: `schemas/IP_Registry.json` is a legacy flat schema used by `app/registry_cleaning/`. Do not try to keep it identical to the v3 schema unless you also migrate the cleaning pipeline.

### 3. ML Agent

**Focus**: `ml/lib/ml_coder/`

**Key Files:**
- `ml/lib/ml_coder/predictor.py` - CPT code predictor
- `ml/lib/ml_coder/registry_predictor.py` - Registry field predictor
- `ml/lib/ml_coder/training.py` - Model training
- `ml/lib/ml_coder/data_prep.py` - Data preparation
- `ml/lib/ml_coder/thresholds.py` - Confidence thresholds

**Responsibilities:**
- Maintain ML model training pipelines
- Tune confidence thresholds for hybrid policy
- Prepare training data from golden extractions
- Ensure ML predictions align with registry schema

### 4. Reporter Agent

**Focus**: `app/reporter/`

**Responsibilities:**
- Edit Jinja templates for report formatting
- Maintain validation logic for required fields
- Ensure inference logic derives fields correctly
- **Rule**: Use `{% if %}` guards in templates. Never output "None" or "missing" in final reports.

### 5. DevOps/API Agent

**Focus**: `app/api/`

**Responsibilities:**
- Maintain `fastapi_app.py`
- Ensure endpoints `/v1/coder/run`, `/v1/registry/run`, `/report/render` work correctly
- **Warning**: Do not create duplicate routes. Check existing endpoints first.

---

## Module Dependencies

```
app/api/
    └── depends on: app/coder/, app/registry/, app/reporter/

app/coder/
    ├── depends on: ml/lib/ml_coder/, app/domain/, app/phi/
    └── provides: CodingService, SmartHybridOrchestrator

app/registry/
    ├── depends on: app/coder/, ml/lib/ml_coder/
    └── provides: RegistryService, RegistryEngine

ml/lib/ml_coder/
    └── provides: MLPredictor, RegistryMLPredictor

app/agents/
    └── provides: run_pipeline(), ParserAgent, SummarizerAgent, StructurerAgent
```

---

## Testing

### Test Commands

```bash
# All tests
make test

# Specific test suites
pytest tests/coder/ -v              # Coder tests
pytest tests/registry/ -v           # Registry tests
pytest tests/ml_coder/ -v           # ML coder tests
pytest tests/api/ -v                # API tests

# Validation
make validate-registry              # Registry extraction validation
make preflight                      # Pre-flight checks
make lint                           # Linting
```

### LLM Tests

By default, tests run in offline mode with stub LLMs. To test actual extraction:

```bash
# Gemini
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="..."
pytest tests/registry/test_extraction.py

# OpenAI (uses Responses API by default)
export OPENAI_OFFLINE=0
export OPENAI_API_KEY="..."
export OPENAI_MODEL="gpt-4o"
pytest tests/unit/test_openai_responses_primary.py

# OpenAI with Chat Completions API (legacy mode)
export OPENAI_PRIMARY_API=chat
pytest tests/unit/test_openai_timeouts.py
```

**Note**: The OpenAI integration uses the Responses API (`/v1/responses`) by default. When writing tests that mock httpx for OpenAI, set `OPENAI_PRIMARY_API=chat` to use the Chat Completions path if your mock expects that format.

### Test Data

- Golden extractions: `data/knowledge/golden_extractions/`
- Synthetic test data: Use fixtures in test files
- **Never** commit PHI (real patient data)

---

## Development Workflow

### Before Making Changes

1. Read relevant documentation:
   - [ARCHITECTURE.md](ARCHITECTURE.md) for system design
   - [AGENTS.md](AGENTS.md) for multi-agent pipeline
   - [Registry_API.md](Registry_API.md) for registry service

2. Understand the data flow:
   - Trace the code path from API endpoint to service to engine
   - Identify which module owns the logic you're changing

3. Check existing tests:
   - Run relevant test suite before changes
   - Understand what behavior is expected

### Making Changes

1. **Edit the correct files**:
   - API: `app/api/fastapi_app.py` (not `api/app.py`)
   - Coder: `app/coder/` (not legacy engine)
   - Registry: `app/registry/`

2. **Follow the architecture**:
   - Services orchestrate, engines execute
   - Keep business rules in domain modules
   - Use adapters for external dependencies

3. **Maintain contracts**:
   - Don't break existing API contracts
   - Update Pydantic schemas if needed
   - Add deprecation warnings, not breaking changes

### After Making Changes

1. Run tests: `make test` or specific test suite
2. Run linting: `make lint`
3. Test the dev server: `./scripts/devserver.sh`
4. Verify no PHI was committed

---

## Development Checklist

Before committing changes:

- [ ] I am editing `app/api/fastapi_app.py` (not `api/app.py`)
- [ ] I am using `CodingService` (not legacy `CoderEngine`)
- [ ] I am using `RegistryService` (not direct engine calls)
- [ ] I have run `make test` (or relevant unit tests)
- [ ] I have checked `scripts/devserver.sh` to ensure the app starts
- [ ] I have not committed any PHI (real patient data)
- [ ] I have updated documentation if changing APIs or schemas

---

## Common Pitfalls

1. **Editing deprecated files**: Always check if a file is deprecated before editing
2. **Duplicate routes**: Check existing endpoints before adding new ones
3. **Breaking contracts**: Don't change API response shapes without versioning
4. **Scattered logic**: Keep business rules in domain modules, not scattered across services
5. **Missing normalization**: LLM outputs often need post-processing in `postprocess.py`
6. **Schema drift**: When changing registry schema, update all dependent files

---

*Last updated: December 2025*
