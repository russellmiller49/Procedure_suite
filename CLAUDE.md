# Procedure Suite (Claude Guide)

## What This Service Does

- The server is a **stateless coding engine**: **scrubbed note text in → registry fields + CPT codes out**.
- The primary UI/API entrypoint is `POST /api/v1/process` (`modules/api/routes/unified_process.py`).

## How To Run Locally

```bash
./scripts/devserver.sh
```

- UI: `http://localhost:8000/ui/`
- API docs: `http://localhost:8000/docs`

The devserver sources `.env` and the app also loads `.env` (unless `PROCSUITE_SKIP_DOTENV=1`).
Keep secrets (e.g., `OPENAI_API_KEY`) out of git; prefer setting them in your shell or an untracked local `.env`.

## Required Env (Enforced at Startup)

The app refuses to start unless:

- `PROCSUITE_PIPELINE_MODE=extraction_first`

In production (`CODER_REQUIRE_PHI_REVIEW=true` or `PROCSUITE_ENV=production`), also require:

- `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
- `REGISTRY_SCHEMA_VERSION=v3`
- `REGISTRY_AUDITOR_SOURCE=raw_ml`

## PHI Workflow

- Keep `POST /api/v1/process` enabled in production.
- When `CODER_REQUIRE_PHI_REVIEW=true`, responses must default to:
  - `review_status=pending_phi_review`
  - `needs_manual_review=true`

Client-side PHI scrubbing is the long-term direction; the server can still scrub when `already_scrubbed=false`.

## Parallel NER (“Split Brain”) Notes

When `REGISTRY_EXTRACTION_ENGINE=parallel_ner`, the extraction-first pipeline runs:

- Path A: Granular NER → registry mapping → deterministic registry→CPT rules
- Path B: registry ML predictor (optional); code must not crash if unavailable or if return types differ
- Deterministic uplift fills common misses (BAL/EBBx/radial EBUS/cryotherapy + pleural drains + chest ultrasound) and attaches evidence spans
- Omission scan emits `SILENT_FAILURE:` warnings for missed high-value procedures

Evidence returned to the UI should be V3-shaped:
`{"source","text","span":[start,end],"confidence"}`

## Context/Negation Guardrails (Extraction Quality)

The deterministic layer includes guardrails to reduce “keyword-only” hallucinations:

- **Stents**: inspection-only phrases (e.g., “stent … in good position”) should *not* trigger stent placement (`31636`).
- **Chest tubes**: discontinue/removal phrases (e.g., “D/c chest tube”) should *not* trigger insertion (`32551`).
- **TBNA**: EBUS-TBNA should *not* populate `tbna_conventional` (prevents double-coding `31629` alongside `31652/31653`).
- **Radial EBUS**: explicit “radial probe …” language should set `radial_ebus.performed` even without concentric/eccentric markers.
- **Menu masking**: `mask_extraction_noise()` strips CPT/menu blocks (e.g., `IP ... CODE MOD DETAILS`) before extraction to prevent “menu reading” hallucinations.

## Granular NER — Stent Label Taxonomy

- `DEV_STENT`: stent mentioned as a device with an interaction (placed/deployed/removed/exchanged/migrated).
- `NEG_STENT`: explicit absence (e.g., “no stent was placed”, “stent not indicated”).
- `CTX_STENT_PRESENT`: stent present/in good position with no intervention evidence.
- Labeling helper: `scripts/label_neg_stent.py` (dry-run by default; use `--write` to persist changes).
- Training allowlist: update `scripts/train_registry_ner.py:ALLOWED_LABEL_TYPES` when adding new label types.

## LLM Self-Correction (Recommended)

- Enable by default with `REGISTRY_SELF_CORRECT_ENABLED=1`. This allows the server to call an external LLM on **scrubbed text**
  as a judge to patch missing registry fields when RAW-ML flags high-confidence omissions.
- For faster responses (no self-correction), set `PROCSUITE_FAST_MODE=1` or `REGISTRY_SELF_CORRECT_ENABLED=0`.

### Debugging Self-Correction

- Self-correction only runs when `REGISTRY_AUDITOR_SOURCE=raw_ml` produces `high_conf_omissions` and the CPT keyword guard passes.
- Keyword gating lives in `modules/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.
- Use the smoke script for visibility into triggers/skips:
  - `python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct`
  - Look for `Audit high-conf omissions:` and `SELF_CORRECT_SKIPPED:` reasons.

## Files You’ll Touch Most Often

- API app wiring + startup env validation: `modules/api/fastapi_app.py`
- Unified process endpoint: `modules/api/routes/unified_process.py`
- Extraction-first pipeline: `modules/registry/application/registry_service.py`
- Parallel pathway orchestrator: `modules/coder/parallel_pathway/orchestrator.py`
- Omission guardrails: `modules/registry/self_correction/keyword_guard.py`
- Clinical postprocessing guardrails: `modules/extraction/postprocessing/clinical_guardrails.py`
- PHI redactor veto rules: `modules/api/static/phi_redactor/protectedVeto.js`

## Tests

- Run full suite: `make test`
- Run targeted: `pytest -q <path>::<test_name>`
