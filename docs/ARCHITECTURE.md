# Procedure Suite Architecture

This document describes the system architecture, module organization, and data flow of the Procedure Suite.

## Overview

The Procedure Suite is a modular system for automated medical coding, registry extraction, and report generation. It follows a **hexagonal architecture** pattern with clear separation between:

- **Domain logic** (business rules, schemas)
- **Application services** (orchestration, workflows)
- **Adapters** (LLM, ML, database, API)

> **Current Production Mode (2026-01):** The server enforces
> `PROCSUITE_PIPELINE_MODE=extraction_first` at startup. The authoritative
> endpoint is `POST /api/v1/process`, and its primary pipeline is
> **Extraction‑First**: **Registry extraction → deterministic Registry→CPT**
> (with auditing + optional self-correction).
>
> **Legacy note:** CPT-first / hybrid-first flows still exist in code for older
> endpoints and tooling, but are expected to be gated/disabled in production.

## Directory Structure

```
Procedure_suite/
├── app/                    # Core application modules
│   ├── api/                    # FastAPI endpoints and routes
│   ├── coder/                  # CPT coding engine
│   ├── ml_coder/               # ML-based prediction
│   ├── registry/               # Registry extraction
│   ├── agents/                 # 3-agent pipeline
│   ├── reporter/               # Report generation
│   ├── common/                 # Shared utilities
│   ├── domain/                 # Domain models and rules
│   └── phi/                    # PHI handling
├── data/
│   └── knowledge/              # Knowledge bases and training data
├── schemas/                    # JSON Schema definitions
├── proc_schemas/               # Pydantic schema definitions
├── config/                     # Configuration settings
├── scripts/                    # CLI tools and utilities
├── tests/                      # Test suites
└── docs/                       # Documentation
```

## Core Modules

### 1. API Layer (`app/api/`)

The FastAPI application serving REST endpoints.

**Key Files:**
- `fastapi_app.py` - Main application with route registration
- `routes/` - Endpoint handlers
- `schemas/` - Request/response models
- `dependencies.py` - Dependency injection

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/process` | POST | **Authoritative** unified extraction-first pipeline (UI uses this) |
| `/v1/coder/run` | POST | Legacy CPT coding endpoint (gated in production) |
| `/v1/registry/run` | POST | Legacy registry extraction endpoint (gated in production) |
| `/v1/report/render` | POST | Generate synoptic report |
| `/health` | GET | Health check |

### 2. Coder Module (`app/coder/`)

CPT code prediction using rules, ML, and LLM.

**Architecture:**
```
app/coder/
├── application/
│   ├── coding_service.py       # Main orchestrator (8-step pipeline)
│   └── smart_hybrid_policy.py  # ML-first hybrid decision logic
├── adapters/
│   ├── llm/                    # LLM advisor adapter
│   ├── nlp/                    # Keyword mapping, negation detection
│   └── ml_ranker.py            # ML prediction adapter
├── domain_rules/               # NCCI bundling + deterministic registry→CPT
├── rules_engine.py             # Rule-based code inference
└── engine.py                   # Legacy coder (deprecated)
```

**CodingService 8-Step Pipeline (legacy coding endpoints / tooling):**
1. Rule engine → rule_codes + confidence
2. (Optional) ML ranker → ml_confidence
3. LLM advisor → advisor_codes + confidence
4. Smart hybrid merge → HybridDecision flags
5. Evidence validation → verify codes in text
6. Non-negotiable rules (NCCI/MER) → remove invalid combos
7. Confidence aggregation → final_confidence, review_flag
8. Build CodeSuggestion[] → return for review

### 3. ML Coder Module (`ml/lib/ml_coder/`)

Machine learning models for CPT and registry prediction.

**Key Files:**
- `predictor.py` - CPT code predictor
- `registry_predictor.py` - Registry field predictor
- `training.py` - Model training pipeline
- `registry_training.py` - Registry ML training
- `data_prep.py` - Data preparation utilities
- `thresholds.py` - Confidence thresholds

**ML-First Hybrid Policy:**
```
Note → ML Predict → Classify Difficulty → Decision Gate → Final Codes
                         ↓
         HIGH_CONF: ML + Rules (fast path)
         GRAY_ZONE: LLM as judge
         LOW_CONF:  LLM primary
```

### 4. Registry Module (`app/registry/`)

Registry data extraction from procedure notes.

**Architecture:**
```
app/registry/
├── application/
│   ├── registry_service.py     # Main service (extraction-first; hybrid-first legacy still present)
│   ├── registry_builder.py     # Build registry entries
│   └── cpt_registry_mapping.py # CPT → registry field mapping
├── adapters/
│   └── schema_registry.py      # Schema validation
├── engine.py                   # LLM extraction engine
├── prompts.py                  # LLM prompts
├── schema.py                   # RegistryRecord model
├── schema_granular.py          # Granular per-site data
├── v2_booleans.py              # V2→V3 boolean mapping for ML
├── deterministic_extractors.py # Rule-based extractors
├── normalization.py            # Field normalization
└── postprocess.py              # Output post-processing
```

**Hybrid-First Extraction Flow:**
1. CPT Coding (SmartHybridOrchestrator)
2. CPT Mapping (aggregate_registry_fields)
3. LLM Extraction (RegistryEngine)
4. Reconciliation (merge CPT-derived + LLM-extracted)
5. Validation (IP_Registry.json schema)
6. ML Audit (compare CPT-derived vs ML predictions)

**Target: Extraction-First Registry Flow (feature-flagged)**
1. Registry extraction from raw note text (no CPT hints)
2. Granular → aggregate propagation (`derive_procedures_from_granular`)
3. Deterministic RegistryRecord → CPT derivation (no note text)
4. RAW-ML auditor calls `MLCoderPredictor.classify_case(raw_note_text)` directly (no orchestrator/rules)
5. Compare deterministic CPT vs RAW-ML audit set and report discrepancies
6. Optional guarded self-correction loop (default off)

### 5. Agents Module (`app/agents/`)

3-agent pipeline for structured note processing.

**Current usage:**
- `ParserAgent` is used as a deterministic sectionizer and can be used to *focus* the note text for registry extraction (see `app/registry/extraction/focus.py`).
- The full `Parser → Summarizer → Structurer` pipeline exists, but `StructurerAgent` is currently a placeholder and is **not** used for production registry extraction.

**Architecture:**
```
app/agents/
├── contracts.py                # I/O schemas (Pydantic)
├── run_pipeline.py             # Pipeline orchestration
├── parser/
│   └── parser_agent.py         # Segment extraction
├── summarizer/
│   └── summarizer_agent.py     # Section summarization
└── structurer/
    └── structurer_agent.py     # Registry mapping
```

**Pipeline Flow:**
```
Raw Text → Parser → Segments/Entities
                        ↓
              Summarizer → Section Summaries
                              ↓
                    Structurer → Registry + Codes
```

See [AGENTS.md](AGENTS.md) for detailed agent documentation.

### 6. Reporter Module (`app/reporter/`)

Synoptic report generation from structured data.

**Key Components:**
- Jinja2 templates for report formatting
- Validation logic for required fields
- Inference logic for derived fields

## Data Flow

### CPT Coding Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Raw Note  │ ──▶ │  ML Predict │ ──▶ │   Classify  │
└─────────────┘     └─────────────┘     │  Difficulty │
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌────────────────┐       ┌─────────────────┐       ┌────────────────┐
           │   HIGH_CONF    │       │    GRAY_ZONE    │       │   LOW_CONF     │
           │ ML + Rules     │       │  LLM as Judge   │       │ LLM Primary    │
           └───────┬────────┘       └────────┬────────┘       └───────┬────────┘
                   │                         │                        │
                   └─────────────────────────┼────────────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ NCCI/MER Rules  │
                                    │  (Compliance)   │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Final Codes    │
                                    │ CodeSuggestion[]│
                                    └─────────────────┘
```

### Registry Extraction Flow

```
┌───────────────┐
│    Raw Note   │
└───────┬───────┘
        │
        ▼
┌──────────────────────────────────────────┐
│ Registry extraction (engine selected by  │
│ REGISTRY_EXTRACTION_ENGINE; production   │
│ requires parallel_ner)                   │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────┐
│ RegistryRecord (V3-shaped)   │
└───────────────┬──────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│ Deterministic Registry→CPT derivation    │
│ (no raw note parsing)                    │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│ Audit + guardrails + optional self-fix   │
│ (RAW-ML auditor, keyword guard, etc.)    │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────┐
│ Codes + evidence + review    │
│ flags (returned by /process) │
└──────────────────────────────┘
```

## Schema System

### JSON Schemas
- `schemas/IP_Registry.json` - Registry entry validation
- `data/knowledge/IP_Registry.json` - Registry schema (dynamic model)

### Pydantic Schemas
- `proc_schemas/coding.py` - CodeSuggestion, CodingResult
- `proc_schemas/registry/ip_v2.py` - IPRegistryV2
- `proc_schemas/registry/ip_v3.py` - IPRegistryV3
- `app/registry/schema.py` - RegistryRecord (extraction record model)

### Registry Procedure Flags

The registry uses 30 boolean procedure presence flags for ML training:

**Bronchoscopy Procedures (23):**
- diagnostic_bronchoscopy, bal, bronchial_wash, brushings
- endobronchial_biopsy, tbna_conventional, linear_ebus, radial_ebus
- navigational_bronchoscopy, transbronchial_biopsy, transbronchial_cryobiopsy
- therapeutic_aspiration, foreign_body_removal, airway_dilation, airway_stent
- thermal_ablation, tumor_debulking_non_thermal, cryotherapy, blvr, peripheral_ablation
- bronchial_thermoplasty, whole_lung_lavage, rigid_bronchoscopy

**Pleural Procedures (7):**
- thoracentesis, chest_tube, ipc, medical_thoracoscopy
- pleurodesis, pleural_biopsy, fibrinolytic_therapy

See `app/registry/v2_booleans.py` for the canonical V2→V3 mapping.

## Configuration

### Settings (`config/settings.py`)

Key configuration classes:
- `CoderSettings` - Coder thresholds and behavior
- `RegistrySettings` - Registry extraction settings
- `MLSettings` - ML model paths and parameters

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | LLM backend: `gemini` or `openai_compat` |
| `GEMINI_API_KEY` | Gemini LLM API key |
| `GEMINI_OFFLINE` | Skip LLM calls (use stubs) |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry |
| `OPENAI_API_KEY` | API key for OpenAI-protocol backend (openai_compat) |
| `OPENAI_BASE_URL` | Base URL for OpenAI-protocol backend (no `/v1`) |
| `OPENAI_MODEL` | Default model name for openai_compat |
| `OPENAI_MODEL_SUMMARIZER` | Model override for summarizer/focusing tasks (openai_compat only) |
| `OPENAI_MODEL_STRUCTURER` | Model override for structurer tasks (openai_compat only) |
| `OPENAI_MODEL_JUDGE` | Model override for self-correction judge (openai_compat only) |
| `OPENAI_OFFLINE` | Disable openai_compat network calls (use stubs) |
| `OPENAI_PRIMARY_API` | Primary API: `responses` or `chat` (default: `responses`) |
| `OPENAI_RESPONSES_FALLBACK_TO_CHAT` | Fall back to Chat Completions on 404 (default: `1`) |
| `OPENAI_TIMEOUT_READ_REGISTRY_SECONDS` | Read timeout for registry tasks (default: `180`) |
| `OPENAI_TIMEOUT_READ_DEFAULT_SECONDS` | Read timeout for default tasks (default: `60`) |
| `PROCSUITE_SKIP_WARMUP` | Skip model warmup |
| `PROCSUITE_PIPELINE_MODE` | **Startup-enforced:** must be `extraction_first` |
| `REGISTRY_EXTRACTION_ENGINE` | Extraction engine (production requires `parallel_ner`) |
| `REGISTRY_SCHEMA_VERSION` | Registry schema version (production requires `v3`) |
| `REGISTRY_AUDITOR_SOURCE` | Auditor source (production requires `raw_ml`) |

## Dependencies

### External Services
- **OpenAI-compatible API** (`LLM_PROVIDER=openai_compat`) - LLM judge/self-correction and (in legacy modes) extraction
- **Gemini API** (optional) - Alternative LLM provider for extraction/self-correction in non-openai_compat setups
- **spaCy** - NLP for entity extraction

### Key Libraries
- FastAPI - Web framework
- Pydantic - Data validation
- scikit-learn - ML models
- onnxruntime - ONNX model inference (when `MODEL_BACKEND=onnx`)
- Jinja2 - Report templating

## Testing Strategy

### Test Organization
```
tests/
├── coder/           # CodingService tests
├── registry/        # RegistryService tests
├── ml_coder/        # ML predictor tests
├── agents/          # Agent pipeline tests
└── api/             # API endpoint tests
```

### Test Categories
- **Unit tests** - Individual function testing
- **Integration tests** - Service-level testing
- **Contract tests** - Schema validation
- **Validation tests** - Ground truth comparison

### Running Tests
```bash
make test                           # All tests
pytest tests/coder/ -v              # Coder only
pytest tests/registry/ -v           # Registry only
make validate-registry              # Registry validation
```

---

*Last updated: 2026-01-30*
