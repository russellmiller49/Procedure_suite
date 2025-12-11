# Development Guide

This document is the **Single Source of Truth** for developers and AI assistants working on the Procedure Suite.

## Core Mandates

1.  **Main Application**: Always edit `modules/api/fastapi_app.py`. Never edit `api/app.py` (deprecated).
2.  **Coding Service**: Use `CodingService` from `modules/coder/application/coding_service.py`. The old `modules.coder.engine.CoderEngine` is deprecated.
3.  **Registry Service**: Use `RegistryService` from `modules/registry/application/registry_service.py`.
4.  **Knowledge Base**: The source of truth for coding rules is `data/knowledge/ip_coding_billing_v2_8.json`.
5.  **Tests**: Preserve existing tests. Run `make test` before committing.

---

## System Architecture

### Directory Structure

| Directory | Status | Purpose |
|-----------|--------|---------|
| `modules/api/` | **ACTIVE** | Main FastAPI app (`fastapi_app.py`) |
| `modules/coder/` | **ACTIVE** | CPT Coding Engine with CodingService (8-step pipeline) |
| `modules/ml_coder/` | **ACTIVE** | ML-based code prediction and training |
| `modules/registry/` | **ACTIVE** | Registry extraction with RegistryService and RegistryEngine |
| `modules/agents/` | **ACTIVE** | 3-agent pipeline (Parser, Summarizer, Structurer) |
| `modules/reporter/` | **ACTIVE** | Report generation with Jinja templates |
| `modules/common/` | **ACTIVE** | Shared utilities, logging, exceptions |
| `modules/domain/` | **ACTIVE** | Domain models and business rules |
| `api/` | **DEPRECATED** | Old API entry point. Do not use. |

### Key Services

| Service | Location | Purpose |
|---------|----------|---------|
| `CodingService` | `modules/coder/application/coding_service.py` | 8-step CPT coding pipeline |
| `RegistryService` | `modules/registry/application/registry_service.py` | Hybrid-first registry extraction |
| `SmartHybridOrchestrator` | `modules/coder/application/smart_hybrid_policy.py` | ML-first hybrid coding |
| `RegistryEngine` | `modules/registry/engine.py` | LLM-based field extraction |

### Data Flow

```
[Procedure Note]
       │
       ▼
[API Layer] (modules/api/fastapi_app.py)
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

**Focus**: `modules/coder/`

**Key Files:**
- `modules/coder/application/coding_service.py` - Main orchestrator
- `modules/coder/application/smart_hybrid_policy.py` - Hybrid decision logic
- `modules/coder/domain_rules.py` - NCCI bundling, domain rules
- `modules/coder/rules_engine.py` - Rule-based inference

**Responsibilities:**
- Maintain the 8-step coding pipeline in `CodingService`
- Update domain rules in `domain_rules.py`
- Ensure NCCI/MER compliance logic is correct
- Keep confidence thresholds tuned in `modules/ml_coder/thresholds.py`

**Rule**: Do not scatter logic. Keep business rules central in the Knowledge Base or domain_rules.py.

### 2. Registry Agent

**Focus**: `modules/registry/`

**Key Files:**
- `modules/registry/application/registry_service.py` - Main service
- `modules/registry/application/cpt_registry_mapping.py` - CPT → registry mapping
- `modules/registry/engine.py` - LLM extraction engine
- `modules/registry/prompts.py` - LLM prompts
- `modules/registry/schema.py` - RegistryRecord model
- `modules/registry/v2_booleans.py` - V2→V3 boolean mapping for ML
- `modules/registry/postprocess.py` - Output normalization

**Responsibilities:**
- Maintain schema definitions in `schema.py` and `schema_granular.py`
- Update LLM prompts in `prompts.py`
- Handle LLM list outputs by adding normalizers in `postprocess.py`
- Keep CPT-to-registry mapping current in `cpt_registry_mapping.py`
- Update V2→V3 boolean mapping in `v2_booleans.py` when schema changes

**Critical**: When changing the registry schema, update:
1. `data/knowledge/IP_Registry.json` - Schema definition
2. `schemas/IP_Registry.json` - JSON Schema for validation
3. `modules/registry/v2_booleans.py` - Boolean field list
4. `modules/registry/application/cpt_registry_mapping.py` - CPT mappings

### 3. ML Agent

**Focus**: `modules/ml_coder/`

**Key Files:**
- `modules/ml_coder/predictor.py` - CPT code predictor
- `modules/ml_coder/registry_predictor.py` - Registry field predictor
- `modules/ml_coder/training.py` - Model training
- `modules/ml_coder/data_prep.py` - Data preparation
- `modules/ml_coder/thresholds.py` - Confidence thresholds

**Responsibilities:**
- Maintain ML model training pipelines
- Tune confidence thresholds for hybrid policy
- Prepare training data from golden extractions
- Ensure ML predictions align with registry schema

### 4. Reporter Agent

**Focus**: `modules/reporter/`

**Responsibilities:**
- Edit Jinja templates for report formatting
- Maintain validation logic for required fields
- Ensure inference logic derives fields correctly
- **Rule**: Use `{% if %}` guards in templates. Never output "None" or "missing" in final reports.

### 5. DevOps/API Agent

**Focus**: `modules/api/`

**Responsibilities:**
- Maintain `fastapi_app.py`
- Ensure endpoints `/v1/coder/run`, `/v1/registry/run`, `/report/render` work correctly
- **Warning**: Do not create duplicate routes. Check existing endpoints first.

---

## Module Dependencies

```
modules/api/
    └── depends on: modules/coder/, modules/registry/, modules/reporter/

modules/coder/
    ├── depends on: modules/ml_coder/, modules/domain/, modules/phi/
    └── provides: CodingService, SmartHybridOrchestrator

modules/registry/
    ├── depends on: modules/coder/, modules/ml_coder/
    └── provides: RegistryService, RegistryEngine

modules/ml_coder/
    └── provides: MLPredictor, RegistryMLPredictor

modules/agents/
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
export GEMINI_OFFLINE=0
export REGISTRY_USE_STUB_LLM=0
export GEMINI_API_KEY="..."
pytest tests/registry/test_extraction.py
```

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
   - API: `modules/api/fastapi_app.py` (not `api/app.py`)
   - Coder: `modules/coder/` (not legacy engine)
   - Registry: `modules/registry/`

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

- [ ] I am editing `modules/api/fastapi_app.py` (not `api/app.py`)
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
