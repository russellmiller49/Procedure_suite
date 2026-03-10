# Session Handoff - March 10, 2026

This handoff is the authoritative working summary for the `extraction_improvements` branch as of the March 10, 2026 desktop session. It includes the earlier March-plan work plus everything completed and validated later in the same day.

Start the next session by reading, in order:
- `extraction_results_3_9_26/codex_master_prompt.md`
- `extraction_results_3_9_26/pipeline_improvement_plan.md`
- this handoff file

## Branch Baseline And Hygiene

- Hygiene baseline commit from this session:
  - `e6772e8c Clean extraction artifact diff`
- That cleanup removed generated March artifact payloads from the branch/PR surface, restored tracked runtime outputs to repo state, and intentionally retained only the planning docs under `extraction_results_3_9_26/`.
- After that cleanup:
  - `main...HEAD` became materially smaller and code-focused
  - `git diff --check main...HEAD` was clean
- Intentionally retained planning docs:
  - `extraction_results_3_9_26/codex_master_prompt.md`
  - `extraction_results_3_9_26/pipeline_improvement_plan.md`
  - `extraction_results_3_9_26/session_handoff_2026_03_10.md`
- Known local-only dirt still present in the working tree and should not be blindly reverted:
  - `.venv_pdf/*`
  - `data/knowledge/ip_coding_billing_v2_9.json`
  - `.claude/settings.local.json`
  - the tracked/untracked docs filename churn around `"Diamond" Improvement Plan 1_18_26.txt`

## What Was Implemented On This Branch

Known completed March 2026 extraction-hardening clusters on this branch:

- First pass:
  - Linear EBUS station reconciliation excludes EUS-B-only content before bronchoscopic station counting / CPT derivation.
  - CT-guided or percutaneous lung ablation language no longer leaks into bronchoscopic `peripheral_ablation` / CPT `31641`.
  - Routine biopsy-site oozing with standard hemostasis, including phrases like `no active bleeding`, no longer becomes a bleeding complication.

- Second pass:
  - Negated airway sampling language such as `brushings ... not obtained` and `endobronchial biopsies ... not obtained` clears false `brushings` and `endobronchial_biopsy`.
  - Negated lesion phrases like `without focal endobronchial lesion` and `without endobronchial abnormality` are stripped from diagnostic inspection findings while preserving true findings like erythema.

- Third pass:
  - BLVR normalization handles phrases such as `valve deployment x4` and `treated with four valves`.
  - Generic negative collateral ventilation language maps to structured negative Chartis / CV status.
  - Target-lobe normalization prefers `LUL` over stale `Lingula` carry-through when the note supports upper-lobe treatment.

- Fourth pass:
  - Routine trach exchange notes no longer promote `established_tracheostomy_route` or CPT `31615` incorrectly.
  - False BLVR extraction from trach-exchange note language is suppressed.
  - Montgomery T-tube insertion routes to airway stent placement, while exchange notes initially retained revision semantics.

- Fifth pass and same-day follow-up work before the semantic airway-device slice:
  - Blue Rhino PDT notes route to percutaneous tracheostomy, while mature trach exchanges stay on established-trach logic.
  - T-tube surveillance / sidearm bronchoscopy notes no longer become airway stent removal or revision.
  - Confirmation-only mature trach bronchoscopy no longer promotes false diagnostic bronchoscopy / established-trach route.
  - T-tube hygiene / sidearm maintenance language no longer promotes `brushings`.
  - Standby laser on Montgomery T-tube exchange no longer triggers `thermal_ablation` / `31641`.
  - History-only stenosis on T-tube maintenance bronchoscopy no longer becomes a diagnostic finding.
  - Compact EBUS lines like `7 x3 passes` are accepted as station `7`, while specimen-pass leakage like `passes 1-5` remains suppressed.
  - Navigation target extraction handles prose such as `computer-assisted navigational bronchoscopy to LUL peripheral target`, dedupes repeated target mentions, canonicalizes to lobe labels like `LUL`, and avoids using generic `target lesion` specimen text as a target location.
  - BAL location trimming works together with target-site cleanup so BAL/specimen language does not bleed into navigation fields.

## March 10 Addendum - Airway Device Action

This cluster was taken through both a precision pass and a follow-on semantic pass during this session.

Completed airway-device work:

- Added a minimal non-CPT-driving structured field:
  - `procedures_performed.airway_device_action`
- Added explicit structured handling for:
  - mature trach exchange
  - Montgomery T-tube exchange
- Updated the schema/knowledge surfaces to include that field:
  - `app/registry/schema/granular_models.py`
  - `app/registry/schema/v2_dynamic.py`
  - `app/registry/schema_granular.py`
  - `data/knowledge/IP_Registry.json`
- Updated deterministic extraction / routing so that:
  - trach tube exchange is captured as `airway_device_action`
  - Montgomery T-tube exchange is captured as `airway_device_action`
  - Montgomery T-tube exchange no longer misroutes to `airway_stent`
  - RegistryService generic bronchoscopy backfill no longer treats `airway_device_action` as a reason to invent diagnostic bronchoscopy

Primary files touched for this cluster:

- `app/extraction/postprocessing/clinical_guardrails.py`
- `app/registry/application/registry_service.py`
- `app/registry/deterministic_extractors.py`
- `app/registry/schema/granular_models.py`
- `app/registry/schema/v2_dynamic.py`
- `app/registry/schema_granular.py`
- `app/registry/self_correction/keyword_guard.py`
- `data/knowledge/IP_Registry.json`
- `tests/registry/test_fixpack_device_action_regressions.py`
- `tests/registry/test_codex_plan_fourth_pass_march2026.py`
- `tests/registry/test_codex_plan_fifth_pass_march2026.py`

Measured airway-device anchor-note outcomes:

- `batch_3/note_032`: improved / semantically resolved at the anchor-note level
  - now yields `airway_device_action` for trach tube exchange
  - no `diagnostic_bronchoscopy`
  - no `established_tracheostomy_route`
  - no CPTs

- `batch_3/note_039`: improved / semantically resolved for device routing
  - now yields `airway_device_action` for Montgomery T-tube exchange
  - no `airway_stent`
  - no `31638`
  - no `31641`
  - `diagnostic_bronchoscopy` still remains, which is consistent with the explicit rigid/flexible bronchoscopy narrative

- `batch_6/note_012`: preserved / same as the protect-against-regression note
  - still keeps `31615` + `31622`
  - now also includes additive `airway_device_action`

Airway-device validation completed in this session:

- Focused airway-device regression ring passed:
  - `tests/registry/test_fixpack_device_action_regressions.py`
  - `tests/registry/test_tracheostomy_route.py`
  - `tests/registry/test_registry_to_cpt_airway_stent_assessment_only.py`
  - `tests/registry/test_codex_plan_first_pass_march2026.py`
  - `tests/registry/test_codex_plan_second_pass_march2026.py`
  - `tests/registry/test_codex_plan_third_pass_march2026.py`
  - `tests/registry/test_codex_plan_fourth_pass_march2026.py`
  - `tests/registry/test_codex_plan_fifth_pass_march2026.py`

- Additional downstream validation completed:
  - extraction/evidence serialization checks
  - generic procedure enumeration checks in the UI code
  - one anchored reporter/render path check on `batch_3/note_032`:
    - `RegistryService.extract_fields()`
    - `build_procedure_bundle_from_extraction()`
    - `_verify_bundle()`
    - `_render_bundle_markdown()`
  - This passed and showed no immediate break in that checked reporter/render path.

Airway-device closure status:

- Closed only for:
  - the anchored extraction slice
  - extraction/evidence serialization checks
  - generic procedure enumeration checks
  - one anchored reporter/render path
- Still unverified:
  - broader March batch impact
  - broader consumer/UI semantic support beyond the checked paths above

## March 10 Addendum - EBUS Station Logic

This cluster was taken through a narrow real-note fix and then measured again through the normal extraction path.

Anchor-note status entering this slice:

- `batch_1/note_009` was already the protect-against-regression note and was functioning correctly.
- `batch_2/note_033` was the real failing anchor:
  - deterministic extraction saw stations `4R / 4L / 7`
  - full postprocess / `RegistryService.extract_fields()` dropped station `7`
  - full output ended at `4R / 4L`
  - CPT under-derived to `31652`

Root cause fixed in this session:

- The problem was the fallback/cull seam inside `app/registry/postprocess/__init__.py`:
  - `populate_ebus_node_events_fallback()` could discard a correct aggregate `linear_ebus.stations_sampled` list and replace it with a bogus non-station fallback target.
  - A later cull step could then drop bare-digit station `7` because the strict station regex did not accept the trailing bare `7` in explicit plural station-list text such as `stations 4R, 4L, and 7`.

Implemented fix:

- `populate_ebus_node_events_fallback()` now trusts an already-correct aggregate `stations_sampled` list when the note has explicit global sampling language such as:
  - `TBNA of all three stations performed`
  - `3 passes each`
- That fallback now seeds sampled `node_events` from the trusted station list instead of replacing them with a non-station target.
- The later station-presence cull now preserves digit-only station `7` when it appears in an explicit plural station-list context.

Primary files touched for this cluster:

- `app/registry/postprocess/__init__.py`
- `tests/registry/test_codex_plan_fourth_pass_march2026.py`

EBUS real-note regressions added/updated:

- `tests/registry/test_codex_plan_fourth_pass_march2026.py`
  - helper now scopes:
    - `PROCSUITE_PIPELINE_MODE=extraction_first`
    - `REGISTRY_EXTRACTION_ENGINE=parallel_ner`
    - `REGISTRY_AUDITOR_SOURCE=disabled`
    - `REGISTRY_SELF_CORRECT_ENABLED=0`
  - This scoping was added only to keep these focused regressions local/deterministic and should stay local unless separately justified.
  - real-note regressions now include:
    - `batch_1/note_009` protect case
    - `batch_2/note_033` undercount / CPT case

EBUS validation completed in this session:

- Targeted subset passed:
  - `tests/registry/test_codex_plan_fourth_pass_march2026.py -k 'minimal_heading_ebus_pass_list_keeps_three_sampled_stations or all_three_station_ebus_tbna_keeps_station_7_and_31653 or compact_ebus_pass_list_derives_three_sampled_stations or keeps_eus_b_separate'`
  - `tests/registry/test_ebus_postprocess_fallback.py tests/registry/test_extraction_quality_fixpack_march2026.py -k 'ebus'`

- Focused EBUS/March ring passed:
  - `tests/registry/test_codex_plan_first_pass_march2026.py`
  - `tests/registry/test_codex_plan_fourth_pass_march2026.py`
  - `tests/registry/test_ebus_postprocess_fallback.py`
  - `tests/registry/test_ebus_site_block_reconcile.py`
  - `tests/registry/test_extraction_quality_fixpack_march2026.py`

- Normal extraction path measurement through `RegistryService.extract_fields()` also completed with the ambient env left unset:
  - `PROCSUITE_PIPELINE_MODE=None`
  - `REGISTRY_EXTRACTION_ENGINE=None`
  - `REGISTRY_AUDITOR_SOURCE=None`
  - `REGISTRY_SELF_CORRECT_ENABLED=None`

Measured EBUS anchor-note outcomes:

- `batch_1/note_009`: same / preserved
  - `stations_sampled=['10R', '4R', '7']`
  - node events preserve passes `5 / 5 / 3`
  - `cpt_codes=['31653']`

- `batch_2/note_033`: improved
  - `stations_sampled=['4L', '4R', '7']`
  - three sampled node events, each with `passes=3`
  - `cpt_codes=['31653']`
  - this fixes the prior full-path state of `['4L', '4R']` plus `31652`
  - one warning was observed but nonblocking:
    - `SELF_CORRECT_SKIPPED: 31620: Path not allowed: /procedures_performed/diagnostic_bronchoscopy/procedure_type`

EBUS closure status:

- Closed only for the measured anchor-note slice through the normal extraction path.
- Still unverified:
  - broader March batch impact
  - broader consumer/UI validation
  - non-default runtime configurations

## Files Currently Touched On Branch

Core code files now known to be part of the March-plan work on this branch:

- `app/extraction/postprocessing/clinical_guardrails.py`
- `app/registry/application/registry_service.py`
- `app/registry/deterministic_extractors.py`
- `app/registry/evidence/verifier.py`
- `app/registry/heuristics/navigation_targets.py`
- `app/registry/legacy/adapters/airway.py`
- `app/registry/postprocess/__init__.py`
- `app/registry/postprocess/complications_reconcile.py`
- `app/registry/processing/navigation_targets.py`
- `app/registry/schema/granular_logic.py`
- `app/registry/schema/granular_models.py`
- `app/registry/schema/v2_dynamic.py`
- `app/registry/schema_granular.py`
- `app/registry/self_correction/keyword_guard.py`
- `data/knowledge/IP_Registry.json`

Regression / plan tests currently in play:

- `tests/registry/test_codex_plan_first_pass_march2026.py`
- `tests/registry/test_codex_plan_second_pass_march2026.py`
- `tests/registry/test_codex_plan_third_pass_march2026.py`
- `tests/registry/test_codex_plan_fourth_pass_march2026.py`
- `tests/registry/test_codex_plan_fifth_pass_march2026.py`
- `tests/registry/test_fixpack_device_action_regressions.py`

## Validation Completed

Earlier in this branch triage, the focused March regression ring passed and `make test` was rerun.

Focused March regression coverage already known green:

- `tests/registry/test_codex_plan_first_pass_march2026.py`
- `tests/registry/test_codex_plan_second_pass_march2026.py`
- `tests/registry/test_codex_plan_third_pass_march2026.py`
- `tests/registry/test_codex_plan_fourth_pass_march2026.py`
- `tests/registry/test_codex_plan_fifth_pass_march2026.py`
- `tests/registry/test_fixpack_device_action_regressions.py`

Full repo validation from the earlier branch-triage step still had 15 failures concentrated in:

- `tests/common/test_path_redaction.py` x2
- `tests/quality/test_reporter_precision_extra_flags.py`
- `tests/registry/test_derive_procedures_from_granular_consistency.py`
- `tests/registry/test_external_notes_2_18_26_regressions.py`
- `tests/registry/test_navigation_targets_inline_target.py` x2
- `tests/registry/test_note_002_regression.py`
- `tests/reporter/test_golden_examples.py`
- `tests/reporting/test_pipeline_parity.py` x3
- `tests/reporting/test_render_parity_normalization.py` x3

Important scope note:

- `make test` was not rerun again after the later airway-device and EBUS anchor-note work, so the current repo-wide failure picture beyond the focused validations above remains unrefreshed.

## March 9 Batch / Shadow-Diff Summary

The most recent broader March six-batch rerun still remains the March 9 comparison captured before today's later airway-device semantic pass and later EBUS anchor-note pass.

Current known broader rerun artifacts from that earlier measurement:

- New batch outputs: `/tmp/procsuite_march9_postpass/batch_1_current.txt` through `/tmp/procsuite_march9_postpass/batch_6_current.txt`
- Pairwise eval artifact: `/tmp/procsuite_march9_postpass/eval_all_batches_20260309_postpass.json`
- Previous local comparison artifact: `/tmp/procsuite_march9_rerun/eval_all_batches_20260309_current.json`

Known broader comparison signal from that March 9 rerun:

- Before that pass: `PASS 44 / WARNING 190 / FAIL 66`
- After that pass: `PASS 47 / WARNING 187 / FAIL 66`
- Delta: `+3 PASS / -3 WARNING / 0 FAIL`
- Pairwise result versus the external March 9 baseline:
  - `300` total notes
  - `69 improved / 206 same / 25 regressed`

Important limitation:

- No broader March rerun or shadow diff was performed after today's airway-device semantic work or today's EBUS station fix.
- So broader batch impact from today's two completed slices remains unverified.

## Known Note-Level Changes After Today

Anchor notes now explicitly measured and updated this session:

- `batch_3/note_032`: improved and semantically resolved for mature trach exchange
- `batch_3/note_039`: improved and semantically resolved for Montgomery T-tube exchange routing
- `batch_3/note_046`: cleaner after airway-device precision work
- `batch_6/note_012`: preserved as the trach-exchange non-regression guard
- `batch_1/note_009`: preserved and measured good for EBUS
- `batch_2/note_033`: improved / fixed for EBUS station counting and CPT derivation

Notes that should no longer be described as the next open anchors from this session:

- `batch_1/note_009`
- `batch_3/note_032`
- `batch_3/note_039`

## What Still Needs Completed

Still unverified / still deferred:

- Broader March batch impact for today's completed airway-device and EBUS slices
  - requires a new March rerun / shadow diff if quantified improvement is needed

- Broader consumer/UI validation
  - airway-device only has:
    - extraction/evidence serialization checks
    - generic procedure enumeration checks
    - one anchored reporter/render path check
  - EBUS has no broader consumer/UI validation from today's work

- Full repo validation refresh
  - the branch-triage `make test` failure list above is still the latest repo-wide snapshot
  - no later full-suite rerun was done after the airway-device semantic slice or EBUS fix

- Existing deferred in-scope failures from the earlier full-suite triage still remain separate work:
  - `tests/quality/test_reporter_precision_extra_flags.py`
  - `tests/registry/test_derive_procedures_from_granular_consistency.py`
  - `tests/registry/test_external_notes_2_18_26_regressions.py`
  - `tests/registry/test_navigation_targets_inline_target.py`
  - `tests/registry/test_note_002_regression.py`
  - related reporter/render parity failures

- Observed-but-nonblocking warning noise:
  - omission-scan / generic `laser` warning noise around the Montgomery T-tube note
  - the `SELF_CORRECT_SKIPPED` warning observed on `batch_2/note_033`
  - neither changed the final anchored outputs in this session

## Recommended Next Step

Two reasonable next moves, depending on what is needed next:

- If quantified impact is needed before more feature work:
  - run a broader March rerun / shadow diff first
  - optionally refresh `make test` after that to separate true new regressions from already-known repo-wide failures

- If continuing with another PR-sized implementation slice without doing the broader rerun first:
  - move to `percutaneous_ablation` only
  - keep it note-anchored and test-first, the same way airway-device and EBUS were handled

Updated cluster status from this session:

- `airway_device_action`: closed only for the anchored slice and limited downstream checks described above
- `ebus_station_logic`: closed only for the measured anchor-note slice through the normal extraction path
- `percutaneous_ablation`: likely the next highest-yield unresolved implementation chunk if broader measurement is deferred

## Repro Commands Used During This Session

- Branch hygiene / diff checks:
  - `git status --short`
  - `git diff --name-status main...HEAD`
  - `git diff --stat main...HEAD`
  - `git diff --check main...HEAD`

- Focused airway-device validations:
  - targeted `pytest` runs on:
    - `tests/registry/test_fixpack_device_action_regressions.py`
    - `tests/registry/test_tracheostomy_route.py`
    - `tests/registry/test_registry_to_cpt_airway_stent_assessment_only.py`
    - `tests/registry/test_codex_plan_{first,second,third,fourth,fifth}_pass_march2026.py`
  - targeted extraction / serialization / reporter probes on the anchor notes

- Focused EBUS validations:
  - targeted `pytest` runs on:
    - `tests/registry/test_codex_plan_fourth_pass_march2026.py`
    - `tests/registry/test_ebus_postprocess_fallback.py`
    - `tests/registry/test_ebus_site_block_reconcile.py`
    - `tests/registry/test_extraction_quality_fixpack_march2026.py`
    - `tests/registry/test_codex_plan_first_pass_march2026.py`
  - targeted `RegistryService.extract_fields()` measurement on:
    - `batch_1/note_009`
    - `batch_2/note_033`

## Suggested Fresh-Session Prompt

Use something close to this on the next machine:

`Read extraction_results_3_9_26/codex_master_prompt.md, extraction_results_3_9_26/pipeline_improvement_plan.md, and extraction_results_3_9_26/session_handoff_2026_03_10.md. Use the handoff as the authoritative working summary. Treat airway_device_action as closed only for the anchored extraction slice plus limited compatibility checks, and treat ebus_station_logic as closed only for the measured anchor-note slice. If quantified impact is needed, rerun the broader March shadow diff first; otherwise continue with the next PR-sized cluster, likely percutaneous_ablation only, staying test-first and note-anchored.`
