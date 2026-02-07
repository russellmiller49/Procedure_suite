# Procedure Suite — Repo Guide (End-to-End)

This is the **single “how the repo works”** document. It’s designed so a new engineer can understand the system from documentation alone, with links to deeper docs where needed.

## Goals and operating model

### What Procedure Suite does

Procedure Suite reads interventional pulmonology (IP) procedure notes and produces:

- A **registry-shaped structured record** (IP Registry V3 is the current direction)
- A set of **CPT codes** (plus traceability metadata where available)
- Optional **financial estimates** (RVU-based)
- Optional **reporting artifacts** (synoptic report generation exists, but the production direction is “Text In → Codes Out”)

### Security / PHI posture (direction of travel)

The repo is transitioning toward **zero-knowledge client-side pseudonymization**:

- The browser UI scrubs/redacts PHI client-side.
- The server acts as a **stateless logic engine** over scrubbed text.

Server-side PHI scrubbing still exists for back-compat and for workflows that aren’t fully client-scrubbed yet.

## Start here (minimal “run it” recipe)

1. Setup environment and dependencies: see [`docs/INSTALLATION.md`](INSTALLATION.md)
2. Start dev server: `./ops/devserver.sh`
3. Open:
   - UI: `http://localhost:8000/ui/`
   - API docs (Swagger): `http://localhost:8000/docs`

## Repository map (what lives where)

High-signal map: [`docs/REPO_INDEX.md`](REPO_INDEX.md)

At a glance:

- `app/` — runtime backend (FastAPI app, pipelines, adapters, guardrails)
- `proc_schemas/` — Pydantic schema definitions (registry v2/v3, coding, shared types)
- `data/` — knowledge base JSON, models, training data, corpora (many files are large)
- `ml/scripts/` — ML training/eval/data-prep scripts
- `ops/` — runtime/devops entrypoints and tooling (`ops/tools/`)
- `tests/` — test suites (prefer adding tests adjacent to the module you change)
- `docs/` — documentation

## “Source of truth” entrypoints (code chokepoints)

If you only memorize 5 files, make them these:

- FastAPI wiring + startup validation: `app/api/fastapi_app.py`
- Authoritative API endpoint: `app/api/routes/unified_process.py` (`POST /api/v1/process`)
- Extraction-first orchestration: `app/registry/application/registry_service.py`
- Deterministic registry → CPT derivation (no note parsing): `app/coder/domain_rules/registry_to_cpt/coding_rules.py`
- UI static app: `ui/static/phi_redactor/` (served at `/ui/`)

## Runtime configuration (what must be set)

### Mandatory invariant (startup-enforced)

The app refuses to start unless:

- `PROCSUITE_PIPELINE_MODE=extraction_first`

Enforcement lives in `app/api/fastapi_app.py:_validate_startup_env()`.

### Production invariants (startup-enforced)

When `CODER_REQUIRE_PHI_REVIEW=true` **or** `PROCSUITE_ENV=production`, startup enforces:

- `REGISTRY_EXTRACTION_ENGINE=parallel_ner` (unless `PROCSUITE_ALLOW_REGISTRY_ENGINE_OVERRIDE=true`)
- `REGISTRY_SCHEMA_VERSION=v3`
- `REGISTRY_AUDITOR_SOURCE=raw_ml`

### `.env` loading rule

- `./ops/devserver.sh` sources `.env` if present.
- `app/api/fastapi_app.py` also loads `.env` via `python-dotenv` unless `PROCSUITE_SKIP_DOTENV=true`.
- OS env vars win over `.env` values (dotenv loads with `override=False`).

Keep secrets out of git. Prefer shell env vars or an untracked local `.env`.

## The production API: `POST /api/v1/process`

### Request/response contracts

The API is defined by Pydantic schemas in `app/api/schemas/base.py`:

- `UnifiedProcessRequest`
- `UnifiedProcessResponse`

The implementation is `app/api/routes/unified_process.py:unified_process()`.

### High-level flow (what happens on each request)

1. **PHI step (optional)**
   - If `payload.already_scrubbed=true`, the server uses the note as-is.
   - Otherwise server-side PHI redaction runs via:
     - `app/api/phi_redaction.py:apply_phi_redaction()`

2. **Registry extraction (the “real work”)**
   - The server calls `RegistryService.extract_fields(note_text)` via `run_cpu(...)`.
   - In extraction-first mode, `RegistryService` routes based on `REGISTRY_EXTRACTION_ENGINE` (see below).

3. **Deterministic CPT derivation**
   - The unified endpoint ensures CPT codes are present:
     - Uses `result.cpt_codes` if present, otherwise derives codes from the extracted `RegistryRecord`.
   - Deterministic derivation entrypoint:
     - `app/coder/domain_rules/registry_to_cpt/coding_rules.py:derive_all_codes_with_meta()`
   - Constraint: deterministic derivation must accept only `RegistryRecord` (no raw note parsing).

4. **Evidence payload for UI highlighting**
   - Evidence items are normalized to the UI contract by:
     - `app/api/adapters/response_adapter.py:build_v3_evidence_payload()`
   - Evidence contract (per evidence item):
     - `{"source": "...", "text": "...", "span": [start, end], "confidence": 0.0-1.0}`

5. **PHI review gating (production safety)**
   - When `CODER_REQUIRE_PHI_REVIEW=true`, the endpoint stays enabled but forces:
     - `review_status="pending_phi_review"`
     - `needs_manual_review=true`
   - Gating helper: `app/coder/phi_gating.py:is_phi_review_required()`

### Output shape (what the UI expects)

`UnifiedProcessResponse` includes, at minimum:

- `registry` — JSON-serializable registry record (V3-shaped)
- `cpt_codes` — list of CPT codes (strings)
- `suggestions[]` — codes + descriptions + rationales + confidence + review flag
- `evidence` — evidence items keyed by field name (for UI highlighting)
- `audit_warnings` and `validation_errors` — surfaced to the UI
- `review_status` + `needs_manual_review` — review workflow controls

## API contract examples (`/api/v1/process`)

These examples are intentionally **synthetic** (no PHI).

### Example 1: Scrubbed note (recommended)

Request body fields (most used):

- `note` (required)
- `already_scrubbed=true` (skip server-side scrubbing)
- `include_financials` (defaults to `true`)
- `explain` (defaults to `false`)
- `locality` (defaults to `"00"`)

`curl`:

```bash
curl -sS http://localhost:8000/api/v1/process \
  -H 'Content-Type: application/json' \
  -d '{
    "note": "PROCEDURE: Bronchoscopy\\nFINDINGS: ...\\nPerformed BAL in RML. Linear EBUS with TBNA of stations 4R and 7.\\nNo complications.",
    "already_scrubbed": true,
    "include_financials": true,
    "explain": true,
    "locality": "00"
  }'
```

Response shape (representative; keys may be empty depending on engine/mode):

```json
{
  "registry": { "...": "..." },
  "evidence": {
    "procedures_performed.linear_ebus.performed": [
      { "source": "registry_span", "text": "Linear EBUS ...", "span": [123, 156], "confidence": 1.0 }
    ]
  },
  "cpt_codes": ["31653", "31624"],
  "suggestions": [
    { "code": "31653", "description": "…", "confidence": 0.95, "rationale": "…", "review_flag": "optional" }
  ],
  "total_work_rvu": 0.0,
  "estimated_payment": 0.0,
  "per_code_billing": [
    { "cpt_code": "31653", "description": "…", "units": 1, "work_rvu": 0.0, "total_facility_rvu": 0.0, "facility_payment": 0.0 }
  ],
  "pipeline_mode": "extraction_first",
  "coder_difficulty": "HIGH_CONF",
  "needs_manual_review": false,
  "audit_warnings": [],
  "validation_errors": [],
  "review_status": "finalized",
  "kb_version": "…",
  "policy_version": "extraction_first_v1",
  "processing_time_ms": 123.45
}
```

Notes:

- `review_status` is:
  - `"pending_phi_review"` when `CODER_REQUIRE_PHI_REVIEW=true`
  - otherwise `"unverified"` or `"finalized"` depending on review requirements
- `audit_warnings` should be treated as “read this before accepting output” (these are UI-surfaced safety signals, including `SILENT_FAILURE:`).
- Financial values depend on what CPT codes are returned and what RVU metadata exists for them.

### Example 2: Unscrubbed note (server-side redaction)

If the client cannot scrub, you can send:

```json
{ "note": "…raw note…", "already_scrubbed": false }
```

The server will run server-side PHI redaction before extraction (see `app/api/phi_redaction.py`), but the long-term direction is still **client-side scrubbing** so the server never receives PHI.

### Error responses (common)

- `503` with “Upstream LLM rate limited”: an upstream LLM call returned 429 and the API is asking you to retry.
- `503` with a configuration detail: startup/runtime configuration is invalid (commonly env var invariants).
- `500`: unexpected internal error.

## Extraction-first: engines and guardrails

`REGISTRY_EXTRACTION_ENGINE` controls how `RegistryService` extracts a `RegistryRecord` from note text.

### `parallel_ner` (recommended; production-required)

This is the current production direction: “split brain” extraction with safety nets.

Conceptually:

1. **Path A (granular NER → registry mapping → deterministic rules)**
2. **Path B (registry ML predictor/auditor when available)**
3. **Guardrails + omission scan**
4. **Optional self-correction (LLM as judge)**

Key properties:

- Deterministic rules aim to prevent “silent misses” for high-value procedures.
- Context/negation guardrails aim to prevent “keyword-only hallucinations”.
- Omission scanning emits `SILENT_FAILURE:` warnings that must reach the UI.

### `engine` (LLM-based extractor)

Uses the `RegistryEngine` LLM extractor:

- Engine: `app/registry/engine.py`
- Prompts: `app/registry/prompts.py`

This is primarily a dev / legacy mode; production is moving toward deterministic extraction-first.

### `agents_focus_then_engine`

Uses agent-assisted focusing (section slicing) before running the deterministic engine:

- Focusing helper: `app/registry/extraction/focus.py`
- Agent docs: [`docs/AGENTS.md`](AGENTS.md)

Guardrail: auditing must run on the **full raw note**, never the focused text.

### `agents_structurer`

Present as a mode, but intentionally guarded: the “Structurer” agent is not a production extractor.

## Deterministic guardrails (important)

These are the “don’t hallucinate / don’t overcode” protections that run in Python:

- Clinical guardrails: `app/extraction/postprocessing/clinical_guardrails.py`
- Evidence integrity verification: `app/registry/evidence/verifier.py`
- Omission scanning + keyword gating: `app/registry/self_correction/keyword_guard.py`

If you change extraction, make sure these guardrails still fire, and update tests accordingly.

## Modules walkthrough (what each `app/*` package owns)

This is a “where do I look” guide for the backend packages. For deeper design discussion, see [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) and [`docs/DEVELOPMENT.md`](DEVELOPMENT.md).

### `app/api/` — FastAPI surface + UI serving

- Owns: HTTP endpoints, request/response schemas, dependency wiring, readiness, and static UI serving.
- Key files:
  - `app/api/fastapi_app.py` — app wiring + startup env validation + readiness/warmup.
  - `app/api/routes/unified_process.py` — `POST /api/v1/process` implementation.
  - `app/api/schemas/base.py` — `UnifiedProcessRequest/Response` and other API schemas.
  - `ui/static/phi_redactor/` — client UI (served at `/ui/`).

### `app/registry/` — extraction-first registry orchestration

- Owns: extracting a `RegistryRecord` from note text, applying guardrails, auditing, and packaging warnings/evidence.
- Key files:
  - `app/registry/application/registry_service.py` — main orchestrator (`RegistryService.extract_fields`).
  - `app/registry/engine.py` — LLM-based extraction engine (when `REGISTRY_EXTRACTION_ENGINE=engine`).
  - `app/registry/processing/masking.py` — `mask_extraction_noise()` (menu/CPT block stripping).
  - `app/registry/evidence/` — evidence verification / integrity checks.
  - `app/registry/self_correction/` — omission scan + (optional) self-correction loop.
  - `app/registry/schema/` — extraction schema tooling and compat shims (distinct from `proc_schemas/`).

### `app/coder/` — CPT derivation + KB-driven coding utilities

- Owns: deterministic CPT derivation and coding-related policy (including PHI gating and “parallel pathway” logic).
- Key files:
  - `app/coder/application/coding_service.py` — `CodingService` (KB access + coding helpers).
  - `app/coder/domain_rules/registry_to_cpt/coding_rules.py` — deterministic registry → CPT (must not parse raw note text).
  - `app/coder/phi_gating.py` — production review gating (`CODER_REQUIRE_PHI_REVIEW`).
  - `app/coder/parallel_pathway/` — `ParallelPathwayOrchestrator` (NER/rules path + ML path).

### `ml/lib/ml_coder/` — ML prediction + training/eval helpers

- Owns: ML models/predictors for CPT and registry auditing, plus training pipelines.
- Key files:
  - `ml/lib/ml_coder/predictor.py` — CPT predictor.
  - `ml/lib/ml_coder/registry_predictor.py` — registry ML predictor/auditor.

### `app/ner/` — granular NER runtime

- Owns: loading/running the granular NER model that emits entity spans used by `parallel_ner`.
- Key files:
  - `app/ner/inference.py` — inference entrypoint(s) for granular NER.

### `app/extraction/` — shared postprocessing guardrails

- Owns: reusable “clinical guardrails” that sanitize/normalize extraction outputs.
- Key files:
  - `app/extraction/postprocessing/clinical_guardrails.py` — anti-hallucination and context/negation protections.

### `app/reporting/` — structured report generation (Jinja)

- Owns: turning structured extraction (and patches) into human-readable reports.
- Key files:
  - `app/reporting/engine.py` — `ReporterEngine` + composition helpers.
  - `app/reporting/inference.py` — `InferenceEngine` (derived fields).
  - `app/reporting/validation.py` — `ValidationEngine` (required fields).
  - `app/reporting/templates/` — Jinja templates.

### `app/reporter/` — legacy/alternate reporter components

- Contains older reporting code and CLI helpers. Prefer `app/reporting/` for new work unless a workflow explicitly uses `app/reporter/`.

### `app/phi/` — PHI detection, scrubbing, and storage helpers

- Owns: PHI-related models and utilities used by server-side redaction and PHI review workflows.
- Related docs: [`docs/phi_review_system/README.md`](phi_review_system/README.md)

### `app/agents/` — parser/summarizer/structurer pipeline (mostly focusing)

- Owns: the agent contracts and the optional focusing workflow used by some extraction modes.
- Key docs: [`docs/AGENTS.md`](AGENTS.md)

### `app/common/`, `app/domain/`, `app/infra/`, `app/llm/` — shared foundations

- `app/common/`: logging, exceptions, KB helpers, span utilities.
- `app/domain/`: domain-layer abstractions (rules, stores, text, RVU, reasoning).
- `app/infra/`: settings, warmup, executors/concurrency utilities.
- `app/llm/`: LLM provider integration and adapter code.

### `app/registry_cleaning/`, `app/autocode/`, `app/proc_ml_advisor/` — specialized/legacy

- `app/registry_cleaning/`: legacy registry cleaning pipeline (not the main extraction-first path).
- `app/autocode/`: KB/synonym-driven autocode utilities (`app/autocode/ip_kb/`).
- `app/proc_ml_advisor/`: ML advisor utilities/routers (used for some dev tooling).

## Self-correction (optional; quality vs latency tradeoff)

When enabled, self-correction asks an external LLM (on scrubbed text) to propose small patches to the extracted registry record.

Key points:

- Enable: `REGISTRY_SELF_CORRECT_ENABLED=1`
- Fast disable: `PROCSUITE_FAST_MODE=1` (devserver forces self-correction off when set)
- Gated by:
  - RAW-ML auditor (`REGISTRY_AUDITOR_SOURCE=raw_ml`) producing high-confidence omissions
  - Keyword guard allowlist (prevents “random patching”)
- Smoke visibility:
  - `python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct`

## UI: PHI redactor / clinical dashboard

The UI is a static app served by FastAPI at `/ui/` from `ui/static/phi_redactor/`.

Notable UX behaviors (important for correctness and training workflows):

- **New Note** clears editor + prior outputs (prevents cross-case confusion).
- **Flattened Tables (Editable)** is collapsed by default; edits generate a second “training” payload:
  - `edited_for_training=true`
  - `edited_at`
  - `edited_source=ui_flattened_tables`
  - `edited_tables[]`
- **Export JSON** downloads the raw API response.
- **Export Tables** downloads flattened tables as an Excel-readable `.xls` (HTML).

## Knowledge base and schemas

### Billing / terminology knowledge base

Primary KB (runtime source-of-truth):

- `data/knowledge/ip_coding_billing_v3_0.json`

This KB drives:

- CPT metadata + RVUs
- bundling and code-family logic
- synonym phrase lists and terminology normalization

Release hygiene:

- Inventory: [`docs/KNOWLEDGE_INVENTORY.md`](KNOWLEDGE_INVENTORY.md)
- Checklist: [`docs/KNOWLEDGE_RELEASE_CHECKLIST.md`](KNOWLEDGE_RELEASE_CHECKLIST.md)
- Validation command: `make validate-knowledge-release`

### Registry schema

There are two “layers”:

- **Rich Pydantic schemas** in `proc_schemas/registry/` (V2/V3)
- **Extraction schema tooling** under `app/registry/schema/` (used to build/validate extraction payloads and compat shims)

Schema refactor notes:

- [`NOTES_SCHEMA_REFACTOR.md`](../NOTES_SCHEMA_REFACTOR.md)
- Tests: `tests/registry/test_schema_refactor_smoke.py`

## Common workflows (commands that matter)

### Local dev server

- `./ops/devserver.sh`

### Tests and quality

- `make test`
- `make lint` (optional)
- `make typecheck` (optional)

### Smoke test a single note (diagnostic)

- `python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct`

### Smoke test a batch (diagnostic)

- `python ops/tools/registry_pipeline_smoke_batch.py --count 30 --self-correct --output my_results.txt`

## Deployment & operations

Start with:

- [`docs/DEPLOYMENT.md`](DEPLOYMENT.md) — Supabase + metrics + CI patterns
- [`docs/DEPLOY_RAILWAY.md`](DEPLOY_RAILWAY.md) — Railway-specific notes (if used)
- [`docs/GRAFANA_DASHBOARDS.md`](GRAFANA_DASHBOARDS.md) — observability

## “Where do I change X?”

- Add/adjust CPT metadata / RVUs / synonyms / bundling rules:
  - `data/knowledge/ip_coding_billing_v3_0.json`
- Adjust deterministic registry → CPT rules:
  - `app/coder/domain_rules/registry_to_cpt/`
- Adjust extraction behavior / guardrails:
  - `app/registry/application/registry_service.py`
  - `app/extraction/postprocessing/clinical_guardrails.py`
  - `app/registry/postprocess.py`
- Adjust UI behaviors:
  - `ui/static/phi_redactor/app.js`
  - `ui/static/phi_redactor/protectedVeto.js`

## Troubleshooting (common “it won’t start” issues)

- Startup failure: `PROCSUITE_PIPELINE_MODE must be 'extraction_first'`
  - Fix env var: `PROCSUITE_PIPELINE_MODE=extraction_first`
- Production startup failure: `REGISTRY_EXTRACTION_ENGINE must be 'parallel_ner' in production`
  - Fix env var: `REGISTRY_EXTRACTION_ENGINE=parallel_ner` (or explicitly opt out with `PROCSUITE_ALLOW_REGISTRY_ENGINE_OVERRIDE=true`)
- Model/runtime bundle validation errors
  - Happens during app lifespan init in `app/api/fastapi_app.py` via `app/registry/model_runtime.py:verify_registry_runtime_bundle()`
  - Usually indicates missing/invalid model artifacts or misconfigured model backend.

---

Last updated: 2026-01-30
