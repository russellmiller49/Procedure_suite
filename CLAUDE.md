# Procedure Suite (Claude Guide)

For broader operational repo details and constraints, see `AGENTS.md`.

## What This Service Does

- The server is a **stateless coding engine**: **scrubbed note text in → registry fields + CPT codes out**.
- The primary UI/API entrypoint is `POST /api/v1/process` (`app/api/routes/unified_process.py`).

## How To Run Locally

```bash
./ops/devserver.sh
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

### PDF Extraction Pipeline (Client-Side)

For PDF upload in the dashboard, extraction is browser-local and worker-based:

- Native extraction path: `ui/static/phi_redactor/pdf_local/workers/pdf.worker.js`
  - pdf.js text layer + layout/image region analysis.
  - Computes per-page `nativeTextDensity = charCount / pageArea`.
  - High-density native pages short-circuit OCR (`NATIVE_DENSE_TEXT`).
- OCR path: `ui/static/phi_redactor/pdf_local/workers/ocr.worker.js`
  - Image masking modes (`auto`, `on`, `off`) + crop logic.
  - Header zonal OCR: top 25% header split into strict left/right zones, each OCRed independently, recombined by zone order.
  - Figure overlap suppression/filtering before final text merge.
- OCR clinical hardening (`ui/static/phi_redactor/pdf_local/pdf/ocrPostprocess.js`):
  - `Lidocaine 49%` -> `Lidocaine 4%`
  - `Atropine 9.5 mg` -> `Atropine 0.5 mg`
  - `lyrnphadenopathy` -> `lymphadenopathy`
  - `hytnph` -> `lymph`
  - Lightweight Levenshtein correction for long clinical terms.
- Fusion/arbitration (`ui/static/phi_redactor/pdf_local/pdf/fusion.js`) prefers native text unless OCR adds missing content.

Hard constraints for this path:

- Raw PDF bytes and unredacted extracted text must not leave the browser.
- OCR/model assets are same-origin vendored files.
- Debug logging is metrics-only (no raw clinical text).

## SMART on FHIR (Epic / Oracle Health–Cerner) EHR Launch

Optional, **disabled by default**. Full guide: `docs/SMART_ON_FHIR.md`.

- Launch pages: `/ui/smart/launch.html` (register as the EHR's SMART launch URL) and
  `/ui/smart/callback.html` (OAuth redirect URI). Standalone launch (issuer picker) is
  supported for sandbox testing.
- **Browser-only** OAuth (authorization-code + PKCE S256) and FHIR reads; EHR tokens and
  unredacted note text never reach the server. The server's sole surface is the public
  issuer allowlist at `GET /api/v1/smart/config` (`app/api/routes/smart.py`, settings in
  `config/smart_settings.py`, fail-soft `config_errors`).
- Env: `SMART_ENABLED=1` + `SMART_ISSUERS` (inline JSON) or `SMART_ISSUERS_FILE`
  (see `configs/smart/issuers.example.json`); optional `SMART_DEFAULT_SCOPES`.
  Issuers are exact-`iss` allowlisted (https required; http only on localhost); Cerner
  issuers get `online_access` appended (short-lived tokens → in-session refresh).
- Dashboard: `#smartEhrCard` (index.html) renders only when a SMART session exists
  (`ui/static/phi_redactor/smart/smartPanel.js`). Loading a note resolves the best
  DocumentReference attachment (text → HTML → RTF best-effort → PDF via the local
  `pdf_local` pipeline), inserts it with `note_source_type=ehr_fhir`, then the normal
  detect → redact → submit PHI flow applies unchanged.
- Hard constraints: never send the Bearer token off the issuer origin; SMART pages load
  same-origin assets only; panel DOM is built via `textContent` (no innerHTML with EHR
  data); logging stays metrics/status-only.
- Tests: `tests/api/test_smart_config.py` (endpoint) and
  `ui/source/registry_grid/src/__tests__/smartCore.test.js` (PKCE/scopes/parsing/RTF-HTML
  conversion, Vitest).

## Reporter Module (Builder + Seeding)

- Reporter Builder UI: `http://localhost:8000/ui/reporter_builder.html`
- Reporter Builder enforces client-side PHI sequence before seeding:
  - `Run Detection` -> `Apply Redactions` -> `Seed Bundle`
- Seed endpoint: `POST /report/seed_from_text`
- Strategy env:
  - `REPORTER_SEED_STRATEGY=registry_extract_fields` (default, production path)
  - `REPORTER_SEED_STRATEGY=llm_findings` (challenger-only masked prompt -> findings -> mapper/guardrails -> templates)
- Strict mode:
  - `REPORTER_SEED_LLM_STRICT=1` (error on findings failure; no fallback)
- LLM findings mode uses existing OpenAI wiring:
  - `LLM_PROVIDER=openai_compat`
  - `OPENAI_MODEL_STRUCTURER=gpt-5-mini`
  - `OPENAI_API_KEY=...`
- Reporter baseline and challenger evals should share the same machine-readable schema, and `--strict` is the intended render-stability mode.

### Robotic Bronchoscopy + EBUS Reporting (2026-10-11)

- **Dictation order drives the report.** `assign_source_sequence()`
  (`app/reporting/normalization/source_sequence.py`) sets `ProcedureInput.sequence` from where each
  step is mentioned, for short peripheral/EBUS prompts and the institutional operative narrative.
  `ReporterEngine._sorted_procedures` is sequence-dominant when ≥2 procedures carry a sequence
  (`uses_source_sequence`); the PROCEDURE header list is reordered to match
  (`pipeline._order_summary_lines`). Clinical constraints per target: navigation first,
  localization (rEBUS/CBCT/tool-in-lesion) before tissue sampling, fiducial after tissue sampling.
  Kill switch: `REPORTER_SOURCE_SEQUENCE=0` (legacy type ranking; the fiducial still sorts after
  sampling, never ahead of navigation).
- **Elastography is per station.** `EBUSStationSample.elastography_pattern` ("Type 1/2/3"); the
  record-level `EBUSTBNA.elastography_pattern` is set only when one pattern applies to every
  station. Parsed from prompts (`_elastography` in `robotic_prompt_fidelity.py`; the class digits
  are blanked so they are never read as pass counts) and from full notes
  (`robotic_ebus_fidelity.py`). Do not put elastography in `echo_features`.
- **Survey-only EBUS** is its own procedure, `ebus_survey` (`EBUSSurvey`, `ebus_survey.j2`), with
  **no `cpt_hints`**: inspected nodes must never derive 31652/31653.
- **Institutional prose blocks** render for short prompts *and* for the operative-report layout
  recognized by `robotic_ebus_fidelity.is_operative_block_note()` (template flag `prose_blocks`).
  Only short prompts switch the shell to `robotic_prompt_shell.j2` (`source_only`). Every
  boilerplate sentence is tied to an explicit field (e.g. the CT interpretation attestation needs
  `CBCTFusion.physician_interpreted`); do not add default assertions to those branches.
- **Full-note reconciliation** (`reconcile_operative_blocks`) takes each cone-beam CT spin (source
  wording, one procedure per spin), tool-in-lesion, the fiducial, ventilation parameters, a
  post-EBUS lavage, and the closing sentence from the source itself.
- **Foreign body removal** is no longer inferred from "aspiration" + "removed"; it needs
  "foreign body" or an aspirated object.
- **Structured seed inputs** (`app/reporting/seed_inputs.py`): enumerated builder dropdowns sent as
  `structured_inputs` on `POST /report/seed_from_text`; catalog at `GET /report/seed_input_spec`
  (derived from the Pydantic model, so options cannot drift). `apply_seed_inputs()` runs on the
  bundle after extraction in **both** the route and `run_reporter_seed_pipeline` (never write the
  selections into the prompt text: a newline disables short-prompt handling). Unspecified = nothing
  written; a specified value overrides extraction and is reported in `seed_input_notes`; nodal
  inputs never create an EBUS-TBNA procedure. No free-text fields (keeps the channel PHI-free).
- **Eval:** `ops/tools/eval_reporter_robotic_minimal.py` now also checks workflow order
  (`check_order`), block/station/elastography rendering (`check_rendered`), and structured-input
  cases (`*-SI-*` rows in `tests/fixtures/reporting/robotic_ebus_minimal_prompts.json`).
- Tests: `tests/reporting/test_robotic_minimal_prompts.py`, `tests/reporting/test_seed_inputs.py`,
  `tests/reporting/test_robotic_ebus_source_fidelity.py`, `tests/api/test_fastapi.py` (seed inputs),
  `tests/api/test_phi_redactor_ui.py` (panel + `phi_redactor`/`phi_redactor_classic` builder files
  must stay byte-identical).

## Ancillary Documents & Longitudinal Outcomes (Case Aggregation)

The registry houses more than the procedure note. Ancillary documents append to a case
(`POST` via `app/api/routes/registry_append.py`, stored in `registry_appended_documents`)
and `CaseAggregator` (`app/registry/application/case_aggregator.py`) merges them into the
canonical case snapshot (`registry_case_records`), deterministic-first with optional LLM fallback:

- **Imaging** (`event_type=imaging`): CT + PET-CT (targets, sizes, SUV, response) and — new 2026-07 —
  **CXR/US** (`app/registry/aggregation/imaging/extract_cxr.py`): pneumothorax presence/side/trend,
  effusion presence/side/trend, device position, `subtype=post_procedure`. Free-text
  `source_modality` is canonicalized by `normalize_modality()` (e.g. "portable chest x-ray" → `cxr`).
  Snapshots land in `imaging_summary.baseline/followups`.
- **Pathology** (`event_type=pathology`): final diagnosis, staging, biomarkers (PD-L1), micro;
  per-station results are checked against `stations_sampled` (QA flags
  `path_station_not_in_stations_sampled` / `sampled_station_missing_from_path`).
  Per-specimen yield (`app/registry/aggregation/pathology/specimen_yield.py`) parses specimen
  blocks into `pathology_results.specimen_results[]` — sampling modality (tbna / brushing /
  washing / bal / transbronchial_biopsy / endobronchial_biopsy / cryobiopsy / pleural_biopsy…),
  station, and result category — so the registry can answer "which modality made the diagnosis".
- **Clinical follow-up** (`event_type=clinical_update|treatment_update|complication`):
  admission/ICU/deceased/disease status plus — new 2026-07 — `ed_visit`, `readmission`, and
  structured `complication_types` (pneumothorax, bleeding, infection, respiratory_failure,
  effusion_recurrence, stent_migration_or_obstruction, drain_malfunction). Updates land in
  `clinical_course.updates` (+ distilled `current_state`).
- **Longitudinal rollup** (new 2026-07): after event patching, `derive_longitudinal_outcomes()`
  (`app/registry/aggregation/outcomes_rollup.py`) computes `registry.longitudinal_outcomes`:
  day-30 complication/readmission/ED-visit/mortality flags, survival status,
  last-known-status day offset, `diagnostic_yield` (Malignant / Benign-specific / Nondiagnostic /
  Pending — classified from `pathology_results.final_diagnosis`, falling back to the best
  per-specimen result), and `reintervention_within_30d` (procedure/procedure_addendum events
  at day 1–30). Manual-override locks on `/longitudinal_outcomes` are honored; the block is
  omitted until any longitudinal signal exists.
- **LLM fallbacks** mirror per event type (pathology / imaging / clinical): CXR/US events fall
  back to `CxrFindingsLLM` only when deterministic extraction produced no structured findings
  (`llm_cxr_fallback` / `llm_cxr_failed` QA flags).
- **Dashboard**: the workflow UI's Flattened Tables render "Longitudinal Outcomes (Case Rollup)"
  and "Pathology Specimen Yield" (when present), plus pneumothorax/effusion/device rows in the
  Imaging Summary and ED-visit/readmission/complication-type rows in Clinical Follow-up
  (`ui/static/phi_redactor/app.js:buildFlattenedTables`).
- Schema notes: sections are declared in `data/knowledge/IP_Registry.json` +
  `proc_schemas/registry/ip_v3.py` + mirrored in `app/registry/schema/v2_dynamic.py`
  (attach hand-written models via `CUSTOM_FIELD_TYPES`). All changes are additive.
- Tests: `tests/registry/test_longitudinal_extension.py`, `tests/registry/test_case_aggregator_*.py`.

## Robotic/EBUS Registry: Claude Extractor (2026-10-28)

The robotic_ebus_v1 0.2.0 contract (`packages/ip_registry_contracts`, dictionary
`data/knowledge/robotic_ebus_v1/launch_dictionary.json`) is the same one the Epic app
(`ip-registry-clinical`) vendors. The packages stay local-only: no LLM/network/app imports
(`packages/tests/test_registry_package_imports.py`). Cloud extraction lives in `app/`.

- **Sparse facts, not a nullable record.** Claude structured outputs cap a request at 24 optional
  and 16 union-typed parameters, so `ClinicalRevision` cannot be the output schema. Claude returns
  rows + typed facts (`app/llm_extraction/facts_schema.py`); the schema is generated from the
  contract (`app/registry_workbench/extraction/contract_spec.py`): all properties required, no unions.
- **Prompt from the dictionary** (`extraction/prompt.py`): definitions, values, units, applicability
  and the extraction-relevant QA rules; every dictionary QA rule is prompted or explicitly excluded
  (tested). Deterministic text so the 1-hour prompt cache holds; the note goes in the user turn.
- **Deterministic assembly** (`extraction/assembler.py`): every value needs an anchored verbatim
  quote (`app/llm_extraction/anchoring.py`, no fuzzy matches); planned/historical/uncertain facts
  become unresolved mentions; validator trips become `conflict_status=unresolved` (approval blocked);
  link errors are fixed deterministically, then at most one stateless repair call.
- **Provider** `ClaudeRegistryProvider` (`extraction/claude_provider.py`) implements the engine's
  `ExtractionProvider` and returns the same proposal shape as `LocalDeterministicProvider`.
  Non-procedure documents still go to the local engine.
- **Egress gate** (`app/common/llm_egress.py`): callers declare text provenance with
  `egress_context(...)`; only `synthetic` passes unless `PROCSUITE_LLM_EGRESS_APPROVED` +
  `PROCSUITE_LLM_EGRESS_PROVIDERS` are set. Client: `app/common/anthropic_client.py` (streams,
  never sends temperature/top_p/top_k, refusal fallbacks online, cache/batch-aware cost).
- Env: `ANTHROPIC_API_KEY`, `PROCSUITE_ANTHROPIC_MODEL` (default `claude-opus-5-5`),
  `PROCSUITE_ANTHROPIC_EFFORT` (default `medium`), `PROCSUITE_ANTHROPIC_FALLBACKS=default|off`.
- **Eval:** `python ops/tools/eval_registry_llm.py --splits validation --arms deterministic
  claude:opus:medium --output /tmp/registry_llm.json` (`--mode batch` for half price, `--dry-run`
  offline, `--gold` for the 8 reviewed docs; those are exposed, engineering regression only).
- **Workbench (non-EMR registry, synthetic only):** `app/registry_workbench/` (own SQLite file
  `registry_workbench.db`, tables `wb_*`; append-only revisions, optimistic concurrency, evidence
  spans re-verified on save, approval only with empty `approval_errors`). API at
  `/api/v1/workbench` (`routes.py`); review UI `ui/source/registry_workbench` (React 19, built into
  `ui/static/registry_workbench`, served at `/workbench`). Seed with
  `make workbench-seed`, run with `python ops/tools/run_registry_workbench.py` (port 8010; the full
  app also mounts it when `PROCSUITE_WORKBENCH_ENABLED=1`, never when `PROCSUITE_ENV=production` or
  `CODER_REQUIRE_PHI_REVIEW=true`). Blinded drafts hide model proposals; only blinded reviews are
  `qualification_eligible` in the gold export. The UI renders against
  `src/__fixtures__/profile.json`, which a pytest keeps equal to the live profile.
- **Truth-first corpus** (`ops/tools/robotic_ebus_truth/`): `scenarios.py` samples a case as
  statement units (each sets contract fields and renders one sentence; nine named traps such as
  surveyed-not-sampled, TIL claimed from radial EBUS, planned-only EBUS, history-only stations);
  `gold.py` builds the gold `ClinicalRevision` only from stated units (must validate with no
  approval errors); `template_writer.py` renders five styles with exact spans; `claude_writer.py`
  writes notes with verbatim quotes per fact plus an independent verifier call (needs a key);
  `verify.py` checks every gold value is readable in its quote. `build_split.py` writes
  `data/ml_training/robotic_ebus_v1/corpus_truth_<date>/` (family-level 60/20/20 split, gold as
  values + `{field_path: [start, end, assertion]}` evidence, test gold in `sealed/` with its hash in
  the manifest). Generation is deterministic from `--seed`; corpora are immutable.
- **Full-contract scorer** (`app/registry_workbench/scoring.py`): rows aligned by natural keys
  (lobe/station/tool/label; Hungarian on collisions), per-field TP/false-fill/miss, FK accuracy,
  Wilson lower bounds; defaults and `not_documented` count as no value. Use it via
  `eval_registry_llm.py --truth-corpus <dir> --splits train validation`. Baseline:
  `reports/robotic_ebus_truth_deterministic_baseline.json`.
- **One-use qualification:** `ops/tools/robotic_ebus_truth/qualify_truth.py --corpus <dir> --provider
  claude:opus:medium` verifies hashes, reserves `independent_qualification_use.json` before any
  inference, then gates Core-tier fields at P≥0.98/R≥0.95 (sufficient support), FK accuracy, and
  contract validity. Never open `sealed/` any other way.
- **Physician anchor set:** `anchor_set.py` picks blinded-review notes (half third-party corpus,
  half truth-first validation; never test) and seeds them into the workbench under split `anchor`;
  selection in `data/knowledge/robotic_ebus_v1/anchor_set_20261109.json`.
- Tests: `tests/registry_workbench/`, `packages/tests/`, `make workbench-ui-test`.

## Robotic/EBUS Demo Page (2026-11-25)

A focused public demo for robotic bronchoscopy + linear EBUS, separate from the dashboard and
from the workbench. Release 1 serves **stored, reviewed results for bundled synthetic samples
only**: no provider call, no API key.

- **API** `app/registry_demo/` (`settings`, `store`, `service`, `routes`), registered at
  `/api/v1/demo/robotic-ebus` only when `PROCSUITE_ROBOTIC_EBUS_DEMO=1`. `GET /config`,
  `GET /samples/{id}`, `POST /extract`. It never imports the workbench database modules; the
  field profile lives in `app/registry_workbench/profile.py`.
- **Exact match only.** `POST /extract` returns a result only when the submitted text is
  byte-for-byte (after line-ending normalisation) a reviewed redacted sample
  (`store.text_key`). No fuzzy matching; anything else is 403 `reviewed_samples_only`
  (409 `result_not_generated` for a reviewed text with no stored result).
- **Data** in `data/knowledge/robotic_ebus_v1/demo/`: `samples.json`
  (`ops/tools/build_robotic_ebus_demo_samples.py`: two hand-written notes plus six from the
  truth-first generator with seeds outside every eval corpus, each with gold),
  `redactions.json` (the text the real browser redactor produces, recorded with
  `ops/tools/import_robotic_ebus_demo_redactions.py`, which re-applies the spans and checks
  both hashes), `results.json` (`ops/tools/warm_robotic_ebus_demo_cache.py --llm claude`;
  it also prints the per-sample review checks). `--llm gold` is a development stand-in and
  refuses to write the shipped file.
- **Suggested codes** `app/registry_workbench/contract_coding.py`: contract proposal -> minimal
  `RegistryRecord` -> the existing `derive_all_codes_with_meta` + `derive_units_for_codes` +
  `build_coding_support_payload`. Every contributing fact keeps its quote; unresolved or
  unattributed sampling never drives a code and becomes a review flag. Out-of-family codes
  (fiducial 31626, imaging, EUS-B, sedation) are listed as not assessed.
- **Page** `ui/source/registry_workbench/src/demo/` (second Vite config `vite.demo.config.ts`,
  `npm run build:demo` / `make demo-ui-build`), built with fixed file names into
  `ui/static/phi_redactor/registry_demo/`. It drives the existing redactor worker by URL.
  `ScanGate` (`phiRedaction.ts`) enables Extract only after a *completed* scan is applied to
  the current text: the worker posts `done` with partial detections after a cancel, so
  cancelled or outdated scans are discarded. Redaction writes only `[REDACTED]`.
- **Field states** (`fields.ts`): value, explicit negative, stated-missing, unresolved
  conflict, and **"Not extracted"** for a blank. A blank is never shown as "No" or as "not
  documented", because the extractor stays silent when the note is silent.
- **Routing** `PROCSUITE_UI_HOME=robotic_ebus_demo` serves the page at `/ui/`;
  `/ui/dashboard.html` always serves the dashboard, and pages that link to the dashboard name
  it. `/ui/registry_demo/` is the staging URL. Local: `make demo-serve` (port 8020).
- Tests: `tests/registry_workbench/test_contract_coding.py`, `test_demo_api.py`,
  `tests/api/test_registry_demo_ui.py`, `ui/source/registry_workbench/src/demo/demo.test.ts`.

## Recent Updates (2026-07-04)

- **Location integrity:** intervention locations (mechanical_debulking/cryotherapy/thermal_ablation) are now sentence-scoped around action verbs; normal-anatomy ("trachea was normal") and scope-navigation sentences no longer contribute sites; prose double-spaces no longer count as table rows (`_is_multicell_table_line`).
- **PR1 completion:** consent scrub covers "consent was obtained"/"explanation in lay terms"; percent-reopened/partial-opening language yields `Partial success` (negation-aware); chest-tube-removal has an IPC-placement-mechanics veto; lidocaine-with-epinephrine and hemostasis-context instillations are not therapeutic injection.
- **EBUS:** `reconcile_ebus_node_event_consistency` enforces inspected-only nodes carry no ROSE and granular `sampled` flags match `stations_sampled`; ROSE sentence capture fixed (`[^.\\n]` typo truncated "identified" to "ide"); 31652/31653 count "stations or structures" — non-station targets count only when no station was identified, deduped against peripheral-TBNA targets (no 31629+31652 double-bill, no alias upcoding).
- **Stents:** placement/removal classification is subject-aware (scope removal ≠ stent removal; scope-as-instrument removal still counts); bullet-style "Deployed under direct vision" lines detect placement (Y-stent → 31631); first-time SEMS deployment no longer misreads as revision.
- **Endobronchial biopsy:** menu/mod-22 text can't force 31625; forceps biopsies with the lesion in the previous sentence are recovered; transbronchial/guide-sheath forceps biopsies are excluded.
- **Pleural:** thoracoscopy with pleural biopsies derives **32609** (32604 is pericardial and was wrong); biopsy enrichment re-runs after the thoracoscopy backstop; IPC "catheter ... with tunneling" phrasing verifies; pleural-needle "aspiration of air/fluid to verify placement" is not 31645 (airway anchors override).
- **Header hierarchy:** the ≤3-code header-authoritative shortcut applies only when there is no substantive narrative (narrative supersedes header codes).
- **Complications:** bleeding-context window fallback requires control-language + unnegated bleeding (blocker-for-blood-soiling = grade 3 without fabricating grade 4 from tumor-board/pre-op mentions); event notes are sentence-scoped, not paragraph heads.
- **Reporter:** tracheostomy route requires stoma language (`via/through ... tracheostom-`, not "through the trachea"); CHEST ULTRASOUND FINDINGS renders only when an ultrasound exam is documented; quality-gate "removed"/"required" adverse cues exclude routine fluid-removal and "no further intervention was required" idioms only; pleural fluid appearance and intercostal-space ordinals render correctly. Reporter seed eval: cpt_jaccard/F1 1.0, zero blockers/contradictions/extra flags.
- Stale tests updated to current policy: fungal debulking ≠ 31640, pleural biopsy = 32609, non-station EBUS structures derive 31652 (see tests with "Policy update" comments).

## Recent Updates (2026-03-09)

- Quality gates were hardened: `eval_golden.py` now exercises the real extraction-first runtime, gate artifacts are path-sanitized, and failing gates still write summaries.
- Extraction-first postprocessing now runs as an ordered quality-pass flow with structured internal `quality_signals`; legacy warnings remain for compatibility.
- Precision suppressions now reduce false positives from header/menu leakage, unchecked template items, inspection-only stents, EBUS/peripheral TBNA contamination, tool-without-action, pleural placement/removal inversion, BAL vs WLL, BLVR exchange/removal, and cryo vs forceps confusion.
- Reporter seed paths share a contract and eval schema, strict-render fallback diagnostics are available, and reporter extra-flag precision improved for chest ultrasound, diagnostic bronchoscopy, BAL, peripheral TBNA, and transbronchial biopsy.

## Quality System

- Effective extraction quality-pass order:
  1. masked text prep / source-aware preprocessing
  2. deterministic uplift
  3. narrative-vs-template reconciliation
  4. precision guardrails / negation cleanup
  5. evidence verification
  6. deterministic CPT derivation
  7. omission scan / RAW-ML audit
- The canonical structured quality trace is `registry.coding_support.quality_pass.signals`.
- Prefer structured quality signals over new ad hoc warnings.
- CPT-driving performed flags need both an allowed evidence source/context and an action + target pattern.
- Do not infer procedures from tool mention, status language, or header/menu content alone.
- Representative source buckets: narrative procedure, findings, impression, template checkbox, menu/code block, history/plan, device-status-only, header/metadata.

## When Touching Reporter Code

- Preserve seed-path comparability; do not fork downstream reporter behavior by seed path.
- Preserve strict-render diagnostics and fallback reason bucketing.
- Keep debug-only metadata out of normal API responses.
- Prefer minimal reporter logic/template changes tied to suppress/preserve fixtures when fixing precision regressions.

## When Touching Extraction Code

- Prefer suppress/preserve fixtures for new precision rules.
- Use evidence-aware suppressions before adding broader heuristics.
- Narrative evidence outranks template/menu/header content.
- Do not mix recall expansion with suppression work unless you can justify it.

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
- Labeling helper: `ml/scripts/label_neg_stent.py` (dry-run by default; use `--write` to persist changes).
- Training allowlist: update `ml/scripts/train_registry_ner.py:ALLOWED_LABEL_TYPES` when adding new label types.

## LLM Self-Correction (Recommended)

- Enable by default with `REGISTRY_SELF_CORRECT_ENABLED=1`. This allows the server to call an external LLM on **scrubbed text**
  as a judge to patch missing registry fields when RAW-ML flags high-confidence omissions.
- For faster responses (no self-correction), set `PROCSUITE_FAST_MODE=1` or `REGISTRY_SELF_CORRECT_ENABLED=0`.

### Debugging Self-Correction

- Self-correction only runs when `REGISTRY_AUDITOR_SOURCE=raw_ml` produces `high_conf_omissions` and the CPT keyword guard passes.
- Keyword gating lives in `app/registry/self_correction/keyword_guard.py:CPT_KEYWORDS`.
- Use the smoke script for visibility into triggers/skips:
  - `python ops/tools/registry_pipeline_smoke.py --note <note.txt> --self-correct`
  - Look for `Audit high-conf omissions:` and `SELF_CORRECT_SKIPPED:` reasons.

## UMLS (Distilled IP-UMLS Map + Deterministic Linker)

The default UMLS integration is a **distilled deterministic linker** backed by a small IP-focused concept map (no spaCy/scispaCy model loading required). A scispaCy backend remains optional.

- **Build tool:** `python ops/tools/build_ip_umls_map.py` → writes `data/knowledge/ip_umls_map.json` (~7 MB, ~19K concepts).
- **Runtime store:** `app/umls/ip_umls_store.py` (local/S3 resolution + file-locked atomic cache).
- **Public API:** `proc_nlp/umls_linker.py` (default backend: `distilled`; keep `umls_link()` stable; use `umls_link_terms()` for term-based linking).
- **Env vars (source resolution: local → S3 → repo fallback):**
  - `UMLS_ENABLE_LINKER` (alias: `ENABLE_UMLS_LINKER`) — enable/disable integration
  - `UMLS_LINKER_BACKEND=distilled|scispacy` (default: `distilled`)
  - `UMLS_IP_UMLS_MAP_LOCAL_PATH` (alias: `IP_UMLS_MAP_PATH`) — explicit local override
  - `UMLS_IP_UMLS_MAP_S3_URI=s3://procedure-suite-models/ip_umls_map.json` — production source of truth
  - `UMLS_IP_UMLS_MAP_CACHE_PATH=/tmp/procsuite/ip_umls_map.json` — S3 cache destination
  - `UMLS_FORCE_REFRESH=true` — redownload on boot even if cache exists

## Files You'll Touch Most Often

- API app wiring + startup env validation: `app/api/fastapi_app.py`
- Unified process endpoint: `app/api/routes/unified_process.py`
- Extraction-first pipeline: `app/registry/application/registry_service.py`
- Parallel pathway orchestrator: `app/coder/parallel_pathway/orchestrator.py`
- Omission guardrails: `app/registry/self_correction/keyword_guard.py`
- Clinical postprocessing guardrails: `app/extraction/postprocessing/clinical_guardrails.py`
- PHI redactor veto rules: `ui/static/phi_redactor/protectedVeto.js`
- UMLS distilled store + cache: `app/umls/ip_umls_store.py`
- UMLS linker wrapper: `proc_nlp/umls_linker.py`
- UMLS map builder: `ops/tools/build_ip_umls_map.py`

## Tests

- Run full suite: `make test`
- Run targeted: `pytest -q <path>::<test_name>`

### Preferred Validation Commands

```bash
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr
python ops/tools/run_quality_gates.py --tier nightly --output-dir /tmp/procsuite_quality_nightly
python ops/tools/summarize_reporter_seed_fallbacks.py --left-report <left.json> --right-report <right.json> --output <summary.json>
python ml/scripts/eval_golden.py --input tests/fixtures/unified_quality_corpus.json --output /tmp/unified_quality_extraction.json
python ops/tools/eval_reporter_prompt_baseline.py --input tests/fixtures/reporter_seed_eval_samples.json --output /tmp/reporter_seed_registry.json --strict
python ops/tools/eval_reporter_prompt_llm_findings.py --input tests/fixtures/reporter_seed_eval_samples.json --output /tmp/reporter_seed_llm.json --strict
python ops/tools/eval_reporter_robotic_minimal.py --output /tmp/reporter_robotic_minimal.json --artifacts-dir /tmp/reporter_robotic_minimal
pytest -q tests/quality/test_unified_quality_matrix.py
pytest -q tests/quality/test_reporter_seed_dual_path_matrix.py
pytest -q tests/reporting/test_strict_render_validation.py
pytest -q tests/quality/test_reporter_precision_extra_flags.py
```

## Golden Extraction Data Generator

Generates high-quality NER training data and golden registry records from procedure notes using a 2-pass LLM pipeline (annotator + judge).

- **Script:** `ops/tools/generate_golden_extraction_data.py`
- **Prompts:** `configs/prompts/golden_extraction_annotator_v1.txt`, `golden_extraction_judge_v1.txt`, `golden_extraction_notegen_v1.txt`
- **Output:** `data/ml_training/golden_extraction/v1/` (accepted NER spans, golden registry records, metrics)

### Input modes
- `--input-dir PATH` or `--input-jsonl PATH`: annotate existing notes
- `--generate-notes COUNT`: generate synthetic notes first via LLM, then annotate

### Pipeline per note
1. Mask CPT/menu noise (`mask_extraction_noise()`)
2. Annotator LLM (temp=0.0) → entities with preceding/following context + registry dict
3. Deterministic offset resolution (context-anchored, longest-first, overlap-aware)
4. Deterministic checks (label taxonomy, `RegistryRecord.model_validate()`, cross-consistency, negation scan, tools-to-intent)
5. If registry validation fails → skip Judge, go to repair loop
6. Judge LLM (temp=0.0) → scores + per-entity verdicts + verdict
7. Repair loop (max 2 attempts) if verdict = "revise"
8. Accept/reject split with quality gates

### Quality gates
- Entity resolution rate >= 80%, judge entity/registry accuracy >= 0.85, anti-hallucination >= 0.90, no critical hallucinations
- Run-level abort if accept rate < 40% after first 20 notes

### Key design decisions
- **No LLM char offsets**: annotator returns entity text + `preceding_context` + `following_context`; offsets resolved deterministically via substring search
- **Longest-first resolution**: entities sorted by text length descending to prevent shorter strings from stealing overlapping ranges
- **RegistryRecord as hard gate**: production Pydantic model validates registry before Judge LLM runs
- **Anti-mode-collapse** (note generation): randomized formatting quirks, demographics, temperature 0.7–1.0

### Reused code
- `app/common/llm.py:LLMService`, `app/registry/processing/masking.py`, `app/registry/schema/v2_dynamic.py:RegistryRecord`, `app/ner/entity_types.py:ENTITY_CATEGORIES`, `ml/scripts/add_training_case.py:add_case()`

## Reporter Tooling

- Random reporter prompt sampling:
  - `python ops/tools/run_reporter_random_seeds.py --count 20 --output reporter_tests.txt --include-metadata-json`
- Findings strategy evaluation:
  - `PROCSUITE_ALLOW_ONLINE=1 LLM_PROVIDER=openai_compat OPENAI_MODEL_STRUCTURER=gpt-5-mini python ops/tools/eval_reporter_prompt_llm_findings.py`
