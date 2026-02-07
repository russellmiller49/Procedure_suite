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

Startup validation enforces these invariants (see `app/api/fastapi_app.py`):

- `PROCSUITE_PIPELINE_MODE=extraction_first` (required; service fails to start otherwise)
- In production (`CODER_REQUIRE_PHI_REVIEW=true` or `PROCSUITE_ENV=production`), also require:
  - `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
  - `REGISTRY_SCHEMA_VERSION=v3`
  - `REGISTRY_AUDITOR_SOURCE=raw_ml`

`.env` is loaded automatically unless `PROCSUITE_SKIP_DOTENV=1`. Shell env vars take precedence.
Keep secrets (e.g., `OPENAI_API_KEY`) out of git; prefer shell env vars or an untracked local `.env`.

## Primary API Surface

- **Authoritative endpoint:** `POST /api/v1/process` (`app/api/routes/unified_process.py`)
  - If `CODER_REQUIRE_PHI_REVIEW=true`, keep the endpoint enabled but return:
    - `review_status=pending_phi_review`
    - `needs_manual_review=true`
- **Legacy endpoints** are gated (feature flags):
  - `PROCSUITE_ALLOW_LEGACY_ENDPOINTS` controls ID-based extraction endpoints (expected to be locked out in prod).
  - `PROCSUITE_ALLOW_REQUEST_MODE_OVERRIDE` controls request-mode overrides.

## UI (PHI Redactor / Clinical Dashboard)

- Served by `./scripts/devserver.sh` at `/ui/` (static files live in `ui/static/phi_redactor/`).
- Workflow explainer page: `/ui/workflow.html` (links from the top bar).
- **New Note**: clears the editor + all prior tables/JSON output to avoid confusion during long-running submits.
- **Flattened Tables (Editable)** (collapsed by default): provides an edit-friendly view of key tables; some fields use dropdowns.
  - When any flattened table value is edited, the UI generates a second payload under **Edited JSON (Training)** with:
    - `edited_for_training=true`, `edited_at`, `edited_source=ui_flattened_tables`, and `edited_tables[]`.
- **Export JSON** downloads the raw server response; **Export Tables** downloads the flattened tables as an Excel-readable `.xls` (HTML).
- Clinical tables are **registry-driven** (e.g., `registry.*.performed`) and should not hide true clinical events due to billing bundling/suppression
  (non-performed rows/cards may render dimmed when details exist).

## Recent Updates (2026-01-25)

- **Schema refactor:** shared EBUS node-event types now live in `proc_schemas/shared/ebus_events.py` and are re-exported via `app/registry/schema/ebus_events.py`.
- **Granular split:** models moved to `app/registry/schema/granular_models.py` and logic to `app/registry/schema/granular_logic.py`; `app/registry/schema_granular.py` is a compat shim.
- **V2 dynamic builder:** moved to `app/registry/schema/v2_dynamic.py`; `app/registry/schema.py` is now a thin entrypoint preserving the `__path__` hack.
- **V3 extraction schema:** renamed to `app/registry/schema/ip_v3_extraction.py` with a compatibility re-export at `app/registry/schema/ip_v3.py`; the rich registry entry schema remains at `proc_schemas/registry/ip_v3.py`.
- **V3→V2 adapter:** now in `app/registry/schema/adapters/v3_to_v2.py` with a compat shim at `app/registry/adapters/v3_to_v2.py`.
- **Refactor notes/tests:** see `NOTES_SCHEMA_REFACTOR.md` and `tests/registry/test_schema_refactor_smoke.py`.

## Recent Updates (2026-01-24)

- **BLVR CPT derivation:** valve placement now maps to `31647` (initial lobe) + `31651` (each additional lobe), and valve removal maps to `31648` (initial lobe) + `31649` (each additional lobe).
- **Chartis bundling:** `31634` is derived only when Chartis is documented; suppressed when Chartis is in the same lobe as valve placement, and flagged for modifier documentation when distinct lobes are present.
- **Moderate sedation threshold:** `99152`/`99153` are derived only when `sedation.type="Moderate"`, `anesthesia_provider="Proceduralist"`, and intraservice minutes ≥10 (computed from start/end if needed).
- **Coding support + traceability:** extraction-first now populates `registry.coding_support` (rules applied + QA flags) and enriches `registry.billing.cpt_codes[]` with `description`, `derived_from`, and evidence spans.
- **Providers normalization:** added `providers_team[]` (auto-derived from legacy `providers` when missing).
- **Registry schema:** added `pathology_results.pdl1_tps_text` to preserve values like `"<1%"` or `">50%"`.
- **KB hygiene (Phase 0–2):** added `docs/KNOWLEDGE_INVENTORY.md`, `docs/KNOWLEDGE_RELEASE_CHECKLIST.md`, and `make validate-knowledge-release` for safer knowledge/schema updates.
- **KB version gating:** loaders now enforce KB filename semantic version ↔ internal `"version"` (override: `PSUITE_KNOWLEDGE_ALLOW_VERSION_MISMATCH=1`).
- **Single source of truth:** runtime code metadata/RVUs come from `master_code_index`, and synonym phrase lists are centralized in KB `synonyms`.

## Recent Updates (2026-02-05)

- **Hierarchy of truth (conflict resolution):**
  - **Narrative supersedes header codes**: do not treat `PROCEDURE:` CPT lists as “performed” when `PROCEDURE IN DETAIL:` contradicts (e.g., header says “trach change” but narrative describes ETT intubation → do not extract tracheostomy creation).
  - **Narrative supersedes summary**: complications mentioned in narrative override templated “COMPLICATIONS: None” (see `app/registry/postprocess/complications_reconcile.py`).
  - **Evidence supersedes checkbox heuristics**: unchecked template items must *not* force a procedure to `performed=false` when explicit active-voice narrative evidence supports `true` (see `app/registry/postprocess/template_checkbox_negation.py`).
- **Anti-hallucination: tools ≠ intent**: mentions of tools (snare/forceps/basket/cryoprobe) do not imply debulking/ablation; require action-on-tissue language (tightened CAO modality parsing in `app/registry/processing/cao_interventions_detail.py`).
- **Puncture ≠ stoma**: tracheal puncture (CPT `31612`) is *not* percutaneous tracheostomy creation; extraction and CPT derivation distinguish puncture-only from trach creation.
- **Intraprocedural adjustment bundling**:
  - BLVR valve remove/replace in the same session is an adjustment, not foreign body removal; do not derive `31635` for valve exchanges.
  - BLVR now tracks segment tokens (e.g., `RB10`) and counts **final deployed valves** only (removed/replaced devices are not counted).
- **Distinct targets for unbundling**: suppress `31629` when EBUS-TBNA is present unless `peripheral_tbna.targets_sampled` clearly indicates a non-station, anatomically distinct target.

## Extraction‑First Pipeline Notes

Key path: `app/registry/application/registry_service.py:_extract_fields_extraction_first()`

- `REGISTRY_EXTRACTION_ENGINE=parallel_ner` runs:
  - Path A: Granular NER → registry mapping → deterministic registry→CPT rules
  - Path B: registry ML predictor (if available); falls back safely when unavailable
- **Deterministic uplift:** in `parallel_ner`, common missed flags are filled from deterministic extractors
  (BAL/EBBx/radial EBUS/cryotherapy + navigational bronchoscopy backstops + pleural chest tube/pigtail + IPC/tunneled pleural catheter + chest ultrasound) and evidence spans are attached.
- **Context/negation guardrails (extraction quality):**
  - **Stents**: inspection-only phrases (e.g., “stent … in good position”) should *not* trigger stent placement (`31636`).
  - **Chest tubes**: discontinue/removal phrases (e.g., “D/c chest tube”) should *not* trigger insertion (`32551`).
  - **TBNA**: EBUS-TBNA should *not* populate `tbna_conventional`. Use `peripheral_tbna` for lung/lesion TBNA; when peripheral TBNA co-occurs with EBUS (`31652/31653`), keep `31629` with Modifier `59` (distinct site).
  - **Tools ≠ intent**: do not infer `31641`/`31640` from tools alone (snare/cryoprobe/forceps); require therapeutic intent + tissue action language.
  - **Puncture ≠ stoma**: tracheal puncture language should not set percutaneous trach performed.
  - **Header vs narrative**: procedure header CPT/menu content is not source-of-truth when contradicted by the narrative.
  - **Radial EBUS**: explicit “radial probe …” language should set `radial_ebus.performed` even without concentric/eccentric markers.
  - **Menu masking**: `mask_extraction_noise()` strips CPT/menu blocks (e.g., `IP ... CODE MOD DETAILS`) before extraction to prevent “menu reading” hallucinations.
- **Omission scan:** `app/registry/self_correction/keyword_guard.py:scan_for_omissions()` emits
  `SILENT_FAILURE:` warnings for high-value missed procedures; these should surface to the UI via `/api/v1/process`.
- **LLM self-correction:** enable with `REGISTRY_SELF_CORRECT_ENABLED=1` (recommended). For faster responses, set
  `PROCSUITE_FAST_MODE=1` or `REGISTRY_SELF_CORRECT_ENABLED=0`.
  - Self-correction only triggers when the RAW-ML auditor emits `high_conf_omissions`, and it is gated by a CPT keyword guard.
  - If you see `SELF_CORRECT_SKIPPED: <CPT>: keyword guard failed (...)`, update `app/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.

## Evidence Contract (UI Highlighting)

The UI expects V3 evidence items shaped like:
`{"source": "...", "text": "...", "span": [start, end], "confidence": 0.0-1.0}`

See `app/api/adapters/response_adapter.py:build_v3_evidence_payload()`.

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
