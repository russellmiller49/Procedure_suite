# Procedure Suite Agent Guide

This repo is transitioning to **zero‑knowledge client‑side pseudonymization**:
the browser scrubs PHI and the server acts as a **stateless logic engine** (Text In → Codes Out).

## Quick Commands

- Dev server: `./scripts/devserver.sh` (serves UI at `/ui/` and API docs at `/docs`)
- Tests: `make test`
- Lint/typecheck (optional): `make lint`, `make typecheck`
- Smoke test (single note): `python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct`
- Smoke test (batch): `python scripts/registry_pipeline_smoke_batch.py --count 30 --self-correct --output my_results.txt`

## Required Runtime Configuration

Startup validation enforces these invariants (see `modules/api/fastapi_app.py`):

- `PROCSUITE_PIPELINE_MODE=extraction_first` (required; service fails to start otherwise)
- In production (`CODER_REQUIRE_PHI_REVIEW=true` or `PROCSUITE_ENV=production`), also require:
  - `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
  - `REGISTRY_SCHEMA_VERSION=v3`
  - `REGISTRY_AUDITOR_SOURCE=raw_ml`

`.env` is loaded automatically unless `PROCSUITE_SKIP_DOTENV=1`. Shell env vars take precedence.
Keep secrets (e.g., `OPENAI_API_KEY`) out of git; prefer shell env vars or an untracked local `.env`.

## Primary API Surface

- **Authoritative endpoint:** `POST /api/v1/process` (`modules/api/routes/unified_process.py`)
  - If `CODER_REQUIRE_PHI_REVIEW=true`, keep the endpoint enabled but return:
    - `review_status=pending_phi_review`
    - `needs_manual_review=true`
- **Legacy endpoints** are gated (feature flags):
  - `PROCSUITE_ALLOW_LEGACY_ENDPOINTS` controls ID-based extraction endpoints (expected to be locked out in prod).
  - `PROCSUITE_ALLOW_REQUEST_MODE_OVERRIDE` controls request-mode overrides.

## Extraction‑First Pipeline Notes

Key path: `modules/registry/application/registry_service.py:_extract_fields_extraction_first()`

- `REGISTRY_EXTRACTION_ENGINE=parallel_ner` runs:
  - Path A: Granular NER → registry mapping → deterministic registry→CPT rules
  - Path B: registry ML predictor (if available); falls back safely when unavailable
- **Deterministic uplift:** in `parallel_ner`, common missed flags are filled from deterministic extractors
  (BAL/EBBx/radial EBUS/cryotherapy + navigational bronchoscopy backstops + pleural chest tube/pigtail + IPC/tunneled pleural catheter + chest ultrasound) and evidence spans are attached.
- **Context/negation guardrails (extraction quality):**
  - **Stents**: inspection-only phrases (e.g., “stent … in good position”) should *not* trigger stent placement (`31636`).
  - **Chest tubes**: discontinue/removal phrases (e.g., “D/c chest tube”) should *not* trigger insertion (`32551`).
  - **TBNA**: EBUS-TBNA should *not* populate `tbna_conventional`. Use `peripheral_tbna` for lung/lesion TBNA; when peripheral TBNA co-occurs with EBUS (`31652/31653`), keep `31629` with Modifier `59` (distinct site).
  - **Radial EBUS**: explicit “radial probe …” language should set `radial_ebus.performed` even without concentric/eccentric markers.
  - **Menu masking**: `mask_extraction_noise()` strips CPT/menu blocks (e.g., `IP ... CODE MOD DETAILS`) before extraction to prevent “menu reading” hallucinations.
- **Omission scan:** `modules/registry/self_correction/keyword_guard.py:scan_for_omissions()` emits
  `SILENT_FAILURE:` warnings for high-value missed procedures; these should surface to the UI via `/api/v1/process`.
- **LLM self-correction:** enable with `REGISTRY_SELF_CORRECT_ENABLED=1` (recommended). For faster responses, set
  `PROCSUITE_FAST_MODE=1` or `REGISTRY_SELF_CORRECT_ENABLED=0`.
  - Self-correction only triggers when the RAW-ML auditor emits `high_conf_omissions`, and it is gated by a CPT keyword guard.
  - If you see `SELF_CORRECT_SKIPPED: <CPT>: keyword guard failed (...)`, update `modules/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.

## Evidence Contract (UI Highlighting)

The UI expects V3 evidence items shaped like:
`{"source": "...", "text": "...", "span": [start, end], "confidence": 0.0-1.0}`

See `modules/api/adapters/response_adapter.py:build_v3_evidence_payload()`.

## Granular NER Model Workflow

- Train: see `docs/GRANULAR_NER_UPDATE_WORKFLOW.md`
- Stent labels: `DEV_STENT` (device interaction) vs `NEG_STENT` (explicit absence) vs `CTX_STENT_PRESENT` (present/in good position, no intervention).
- Auto-label helper: `python scripts/label_neg_stent.py` (dry-run by default; use `--write` to persist).
- Training allowlist lives in `scripts/train_registry_ner.py:ALLOWED_LABEL_TYPES`.
- Typical command:
  - `python scripts/train_registry_ner.py --data data/ml_training/granular_ner/ner_bio_format_refined.jsonl --output-dir artifacts/registry_biomedbert_ner_v2 ...`
- Run server with the model:
  - set `GRANULAR_NER_MODEL_DIR=artifacts/registry_biomedbert_ner` (in `.env` or shell)

## Common Pitfalls

- Don’t confuse **pipeline mode** with **extraction engine**:
  - pipeline mode is `extraction_first`
  - extraction engine is `parallel_ner`
- Avoid reintroducing duplicate routes: `/api/v1/process` lives in the router module and is the single source of truth.
