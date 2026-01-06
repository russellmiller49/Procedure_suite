# Procedure Suite

**Automated CPT Coding, Registry Extraction, and Synoptic Reporting for Interventional Pulmonology.**

This toolkit enables:
1.  **Predict CPT Codes**: Analyze procedure notes using ML + LLM hybrid pipeline to generate billing codes with RVU calculations.
2.  **Extract Registry Data**: Use deterministic extractors and LLMs to extract structured clinical data (EBUS stations, complications, demographics) into a validated schema.
3.  **Generate Reports**: Create standardized, human-readable procedure reports from structured data.

## Documentation

- **[Installation & Setup](docs/INSTALLATION.md)**: Setup guide for Python, spaCy models, and API keys.
- **[User Guide](docs/USER_GUIDE.md)**: How to use the CLI tools and API endpoints.
- **[Registry Prodigy Workflow](docs/REGISTRY_PRODIGY_WORKFLOW.md)**: Human-in-the-loop “Diamond Loop” for the registry procedure classifier.
- **[Development Guide](docs/DEVELOPMENT.md)**: **CRITICAL** for contributors and AI Agents. Defines the system architecture and coding standards.
- **[Architecture](docs/ARCHITECTURE.md)**: System design, module breakdown, and data flow.
- **[Agents](docs/AGENTS.md)**: Multi-agent pipeline documentation for Parser, Summarizer, and Structurer.
- **[Registry API](docs/Registry_API.md)**: Registry extraction service API documentation.
- **[CPT Reference](docs/REFERENCES.md)**: List of supported codes.

## Quick Start

1.  **Install**:
    ```bash
    micromamba activate medparse-py311
    make install
    make preflight
    ```

2.  **Configure**:
    Create `.env` with your `GEMINI_API_KEY`.

3.  **Run**:
    ```bash
    # Start the API/Dev Server
    ./scripts/devserver.sh
    ```

## Key Modules

| Module | Description |
|--------|-------------|
| **`modules/api/fastapi_app.py`** | Main FastAPI backend |
| **`modules/coder/`** | CPT coding engine with CodingService (8-step pipeline) |
| **`modules/ml_coder/`** | ML-based code predictor and training pipeline |
| **`modules/registry/`** | Registry extraction with RegistryService and RegistryEngine |
| **`modules/agents/`** | 3-agent pipeline: Parser → Summarizer → Structurer |
| **`modules/reporter/`** | Template-based synoptic report generator |
| **`/ui/phi_demo.html`** | Synthetic PHI demo UI for scrubbing → vault → review → reidentify |

## System Architecture

> **Note:** The repository is in an architectural pivot toward **Extraction‑First**
> (Registry extraction → deterministic CPT rules). The current production pipeline
> remains ML‑First for CPT and hybrid‑first for registry; sections below describe
> current behavior unless explicitly labeled as “Target.”

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Procedure Note                               │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Layer (modules/api/)                      │
│  • /v1/coder/run - CPT coding endpoint                              │
│  • /v1/registry/run - Registry extraction endpoint                  │
│  • /v1/report/render - Report generation endpoint                   │
└─────────────────────────────────────────────────────────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  CodingService  │    │ RegistryService │    │    Reporter     │
│  (8-step pipe)  │    │ (Hybrid-first)  │    │ (Jinja temps)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │
         ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│ SmartHybrid     │    │ RegistryEngine  │
│ Orchestrator    │    │ (LLM Extract)   │
│ ML→Rules→LLM    │    │                 │
└─────────────────┘    └─────────────────┘
```

### ML-First Hybrid Pipeline (CodingService)

The coding system uses a **SmartHybridOrchestrator** that prioritizes ML predictions:

1. **ML Prediction** → Predict CPT codes with confidence scores
2. **Difficulty Classification** → HIGH_CONF / GRAY_ZONE / LOW_CONF
3. **Decision Gate**:
   - HIGH_CONF + rules pass → Use ML codes directly (fast path, no LLM)
   - GRAY_ZONE or rules fail → LLM as judge
   - LOW_CONF → LLM as primary coder
4. **Rules Validation** → NCCI/MER compliance checks
5. **Final Codes** → CodeSuggestion objects for review

### Hybrid-First Registry Extraction (RegistryService)

Registry extraction follows a hybrid approach:

1. **CPT Coding** → Get codes from SmartHybridOrchestrator
2. **CPT Mapping** → Map CPT codes to registry boolean flags
3. **LLM Extraction** → Extract additional fields via RegistryEngine
4. **Reconciliation** → Merge CPT-derived and LLM-extracted fields
5. **Validation** → Validate against IP_Registry.json schema

## Data & Schemas

| File | Purpose |
|------|---------|
| `data/knowledge/ip_coding_billing_v2_9.json` | CPT codes, RVUs, bundling rules |
| `data/knowledge/IP_Registry.json` | Registry schema definition |
| `data/knowledge/golden_extractions/` | Training data for ML models |
| `schemas/IP_Registry.json` | JSON Schema for validation |

## Testing

```bash
# Run all tests
make test

# Run specific test suites
pytest tests/coder/ -v          # Coder tests
pytest tests/registry/ -v       # Registry tests
pytest tests/ml_coder/ -v       # ML coder tests

# Validate registry extraction
make validate-registry

# Run preflight checks
make preflight
```

## Note for AI Assistants

**Please read [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) before making changes.**

- Always edit `modules/api/fastapi_app.py` (not `api/app.py` - deprecated)
- Use `CodingService` from `modules/coder/application/coding_service.py`
- Use `RegistryService` from `modules/registry/application/registry_service.py`
- Knowledge base is at `data/knowledge/ip_coding_billing_v2_9.json`
- Run `make test` before committing

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | LLM backend: `gemini` or `openai_compat` | `gemini` |
| `GEMINI_API_KEY` | API key for Gemini LLM | Required for LLM features |
| `GEMINI_OFFLINE` | Disable LLM calls (use stubs) | `1` |
| `REGISTRY_USE_STUB_LLM` | Use stub LLM for registry tests | `1` |
| `OPENAI_API_KEY` | API key for OpenAI-protocol backend (openai_compat) | Required unless `OPENAI_OFFLINE=1` |
| `OPENAI_BASE_URL` | Base URL for OpenAI-protocol backend (no `/v1`) | `https://api.openai.com` |
| `OPENAI_MODEL` | Default model name for openai_compat | Required unless `OPENAI_OFFLINE=1` |
| `OPENAI_MODEL_SUMMARIZER` | Model override for summarizer/focusing tasks (openai_compat only) | `OPENAI_MODEL` |
| `OPENAI_MODEL_STRUCTURER` | Model override for structurer tasks (openai_compat only) | `OPENAI_MODEL` |
| `OPENAI_MODEL_JUDGE` | Model override for self-correction judge (openai_compat only) | `OPENAI_MODEL` |
| `OPENAI_OFFLINE` | Disable openai_compat network calls (use stubs) | `0` |
| `OPENAI_PRIMARY_API` | Primary API: `responses` or `chat` | `responses` |
| `OPENAI_RESPONSES_FALLBACK_TO_CHAT` | Fall back to Chat Completions on 404 | `1` |
| `OPENAI_TIMEOUT_READ_REGISTRY_SECONDS` | Read timeout for registry tasks (seconds) | `180` |
| `OPENAI_TIMEOUT_READ_DEFAULT_SECONDS` | Read timeout for default tasks (seconds) | `60` |
| `PROCSUITE_SKIP_WARMUP` | Skip NLP model loading at startup | `false` |
| `PROCSUITE_PIPELINE_MODE` | Pipeline mode: `current` or `extraction_first` | `current` |
| `REGISTRY_EXTRACTION_ENGINE` | Registry extraction engine: `engine`, `agents_focus_then_engine`, or `agents_structurer` | `engine` |
| `REGISTRY_AUDITOR_SOURCE` | Registry auditor source (extraction-first): `raw_ml` or `disabled` | `raw_ml` |
| `REGISTRY_ML_AUDIT_USE_BUCKETS` | Audit set = `high_conf + gray_zone` when `1`; else use `top_k + min_prob` | `1` |
| `REGISTRY_ML_AUDIT_TOP_K` | Audit top-k predictions when buckets disabled | `25` |
| `REGISTRY_ML_AUDIT_MIN_PROB` | Audit minimum probability when buckets disabled | `0.50` |
| `REGISTRY_ML_SELF_CORRECT_MIN_PROB` | Min prob for self-correction trigger candidates | `0.95` |
| `REGISTRY_SELF_CORRECT_ENABLED` | Enable guarded self-correction loop | `0` |
| `REGISTRY_SELF_CORRECT_ALLOWLIST` | Comma-separated JSON Pointer allowlist for self-correction patch paths (default: `modules/registry/self_correction/validation.py` `ALLOWED_PATHS`) | `builtin` |
| `REGISTRY_SELF_CORRECT_MAX_ATTEMPTS` | Max successful auto-corrections per case | `1` |
| `REGISTRY_SELF_CORRECT_MAX_PATCH_OPS` | Max JSON Patch ops per proposal | `5` |

---

*Last updated: December 2025*
