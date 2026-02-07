# Procedure Suite (Claude Guide)

## What This Service Does

- The server is a **stateless coding engine**: **scrubbed note text in → registry fields + CPT codes out**.
- The primary UI/API entrypoint is `POST /api/v1/process` (`app/api/routes/unified_process.py`).

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

## UI (Clinical Dashboard / PHI Redactor)

The devserver mounts the PHI redactor UI as the main UI:

- UI: `http://localhost:8000/ui/` (static files: `ui/static/phi_redactor/`)
- Workflow tab: `http://localhost:8000/ui/workflow.html`

Notable workflow features:

- **New Note** clears the editor and all prior outputs (tables + JSON) between cases.
- **Flattened Tables (Editable)** is collapsed by default; edits generate a second payload under **Edited JSON (Training)**:
  - `edited_for_training=true`, `edited_at`, `edited_source=ui_flattened_tables`, and `edited_tables[]`.
- **Export JSON** downloads the raw server response; **Export Tables** downloads the flattened tables as an Excel-readable `.xls` (HTML).
- Clinical tables should reflect **clinical reality** from `registry` (performed/details) even when a related CPT code is bundled/suppressed.

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
- **TBNA**: EBUS-TBNA should *not* populate `tbna_conventional`. Use `peripheral_tbna` for lung/lesion TBNA; when peripheral TBNA co-occurs with EBUS (`31652/31653`), keep `31629` with Modifier `59` (distinct site).
- **Tools ≠ intent**: do not infer `31641`/`31640` from tools alone (snare/cryoprobe/forceps); require therapeutic intent + tissue action language.
- **Puncture ≠ stoma**: tracheal puncture language should not set percutaneous trach performed.
- **Header vs narrative**: procedure header CPT/menu content is not source-of-truth when contradicted by the narrative.
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
- Keyword gating lives in `app/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.
- Use the smoke script for visibility into triggers/skips:
  - `python scripts/registry_pipeline_smoke.py --note <note.txt> --self-correct`
  - Look for `Audit high-conf omissions:` and `SELF_CORRECT_SKIPPED:` reasons.

## Files You’ll Touch Most Often

- API app wiring + startup env validation: `app/api/fastapi_app.py`
- Unified process endpoint: `app/api/routes/unified_process.py`
- Extraction-first pipeline: `app/registry/application/registry_service.py`
- Parallel pathway orchestrator: `app/coder/parallel_pathway/orchestrator.py`
- Omission guardrails: `app/registry/self_correction/keyword_guard.py`
- Clinical postprocessing guardrails: `app/extraction/postprocessing/clinical_guardrails.py`
- PHI redactor veto rules: `ui/static/phi_redactor/protectedVeto.js`

## Tests

- Run full suite: `make test`
- Run targeted: `pytest -q <path>::<test_name>`
