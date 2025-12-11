# Procedure Suite Architecture

This document describes the system architecture, module organization, and data flow of the Procedure Suite.

## Overview

The Procedure Suite is a modular system for automated medical coding, registry extraction, and report generation. It follows a **hexagonal architecture** pattern with clear separation between:

- **Domain logic** (business rules, schemas)
- **Application services** (orchestration, workflows)
- **Adapters** (LLM, ML, database, API)

> **Architectural Pivot:** The system is currently **ML‑First** for CPT coding and
> **hybrid‑first** for registry extraction. A pivot to **Extraction‑First**
> (registry → deterministic CPT) is in progress; “Target” sections in docs
> describe that end state.

## Directory Structure

```
Procedure_suite/
├── modules/                    # Core application modules
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

### 1. API Layer (`modules/api/`)

The FastAPI application serving REST endpoints.

**Key Files:**
- `fastapi_app.py` - Main application with route registration
- `routes/` - Endpoint handlers
- `schemas/` - Request/response models
- `dependencies.py` - Dependency injection

**Endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/coder/run` | POST | Run CPT coding on procedure note |
| `/v1/registry/run` | POST | Extract registry data from note |
| `/v1/report/render` | POST | Generate synoptic report |
| `/health` | GET | Health check |

### 2. Coder Module (`modules/coder/`)

CPT code prediction using rules, ML, and LLM.

**Architecture:**
```
modules/coder/
├── application/
│   ├── coding_service.py       # Main orchestrator (8-step pipeline)
│   └── smart_hybrid_policy.py  # ML-first hybrid decision logic
├── adapters/
│   ├── llm/                    # LLM advisor adapter
│   ├── nlp/                    # Keyword mapping, negation detection
│   └── ml_ranker.py            # ML prediction adapter
├── domain_rules.py             # NCCI bundling, EBUS rules
├── rules_engine.py             # Rule-based code inference
└── engine.py                   # Legacy coder (deprecated)
```

**CodingService 8-Step Pipeline:**
1. Rule engine → rule_codes + confidence
2. (Optional) ML ranker → ml_confidence
3. LLM advisor → advisor_codes + confidence
4. Smart hybrid merge → HybridDecision flags
5. Evidence validation → verify codes in text
6. Non-negotiable rules (NCCI/MER) → remove invalid combos
7. Confidence aggregation → final_confidence, review_flag
8. Build CodeSuggestion[] → return for review

### 3. ML Coder Module (`modules/ml_coder/`)

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

### 4. Registry Module (`modules/registry/`)

Registry data extraction from procedure notes.

**Architecture:**
```
modules/registry/
├── application/
│   ├── registry_service.py     # Main service (hybrid-first)
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

### 5. Agents Module (`modules/agents/`)

3-agent pipeline for structured note processing.

**Architecture:**
```
modules/agents/
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

### 6. Reporter Module (`modules/reporter/`)

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
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Raw Note  │ ──▶ │  CPT Coder  │ ──▶ │ CPT Mapping │
└─────────────┘     └─────────────┘     │ (Bool Flags)│
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌────────────────┐       ┌─────────────────┐       ┌────────────────┐
           │  CPT-Derived   │       │ Deterministic   │       │  LLM Extract   │
           │    Fields      │       │   Extractors    │       │  (Engine)      │
           └───────┬────────┘       └────────┬────────┘       └───────┬────────┘
                   │                         │                        │
                   └─────────────────────────┼────────────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │  Reconciliation │
                                    │  (Merge Fields) │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │   Validation    │
                                    │ (JSON Schema)   │
                                    └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ RegistryRecord  │
                                    └─────────────────┘
```

## Schema System

### JSON Schemas
- `schemas/IP_Registry.json` - Registry entry validation
- `data/knowledge/IP_Registry.json` - Registry schema (dynamic model)

### Pydantic Schemas
- `proc_schemas/coding.py` - CodeSuggestion, CodingResult
- `proc_schemas/registry/ip_v2.py` - IPRegistryV2
- `proc_schemas/registry/ip_v3.py` - IPRegistryV3
- `modules/registry/schema.py` - RegistryRecord (dynamic)

### Registry Procedure Flags

The registry uses 29 boolean procedure presence flags for ML training:

**Bronchoscopy Procedures (22):**
- diagnostic_bronchoscopy, bal, bronchial_wash, brushings
- endobronchial_biopsy, tbna_conventional, linear_ebus, radial_ebus
- navigational_bronchoscopy, transbronchial_biopsy, transbronchial_cryobiopsy
- therapeutic_aspiration, foreign_body_removal, airway_dilation, airway_stent
- thermal_ablation, cryotherapy, blvr, peripheral_ablation
- bronchial_thermoplasty, whole_lung_lavage, rigid_bronchoscopy

**Pleural Procedures (7):**
- thoracentesis, chest_tube, ipc, medical_thoracoscopy
- pleurodesis, pleural_biopsy, fibrinolytic_therapy

See `modules/registry/v2_booleans.py` for the canonical V2→V3 mapping.

## Configuration

### Settings (`config/settings.py`)

Key configuration classes:
- `CoderSettings` - Coder thresholds and behavior
- `RegistrySettings` - Registry extraction settings
- `MLSettings` - ML model paths and parameters

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Gemini LLM API key |
| `GEMINI_OFFLINE` | Skip LLM calls (use stubs) |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry |
| `PROCSUITE_SKIP_WARMUP` | Skip model warmup |

## Dependencies

### External Services
- **Gemini API** - LLM for code suggestion and extraction
- **spaCy** - NLP for entity extraction

### Key Libraries
- FastAPI - Web framework
- Pydantic - Data validation
- scikit-learn - ML models
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

*Last updated: December 2025*
