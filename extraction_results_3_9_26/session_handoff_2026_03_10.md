# Session Handoff - March 10, 2026

This handoff is the authoritative working summary for the `extraction_improvements` branch. It preserves the March 10, 2026 desktop-session baseline and now also records the later March 11-13 follow-on work completed after that session.

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

## Post-March 10 Follow-On Updates (March 11, 2026)

### Completed - Percutaneous Ablation

This slice is now complete at the requested evidence level for the anchored extraction family.

Committed change:

- `a56173c3 Guard percutaneous cryoablation from bronchoscopic cryotherapy routing`

What changed:

- Explicit CT-guided / percutaneous / non-bronchoscopic cryoablation no longer leaks into bronchoscopic `cryotherapy`.
- Unsupported bronchoscopic CPT `31641` no longer derives from that percutaneous language.
- The fix was kept conservative:
  - it prevents false bronchoscopic routing / CPT leakage
  - it does **not** yet assert a positive structured percutaneous-ablation extraction
  - it does **not** add broader percutaneous CPT derivation

Primary files touched:

- `app/registry/deterministic_extractors.py`
- `app/registry/self_correction/keyword_guard.py`
- `tests/registry/test_fixpack_percutaneous_ablation_regressions.py`

Measured percutaneous anchor-note subset:

- `batch_5/note_002`: improved
  - before: `cryotherapy.performed=True`, `cpt_codes=['31641']`
  - after: no bronchoscopic ablation family, `cpt_codes=[]`
- `batch_5/note_006`: same / protected
- `batch_5/note_012`: same / protected
- `batch_5/note_024`: same / protected

Percutaneous validation completed:

- new real-note regression:
  - `tests/registry/test_fixpack_percutaneous_ablation_regressions.py`
- adjacent focused protections:
  - `tests/registry/test_codex_plan_first_pass_march2026.py`
  - `tests/registry/test_keyword_guard_overrides.py -k 'ablation or cryo'`

Percutaneous closure status:

- Closed only for:
  - the committed anchored fix
  - the measured four-note subset above
- Still unverified:
  - broader March-family impact
  - downstream/UI/export behavior

### Completed - BLVR / PAL Valve

This slice is now complete at the requested anchored implementation level and committed on branch.

Committed changes:

- `b68b2a64 Normalize BLVR PAL valve counts and bundling`
- `4c647f88 Relax BLVR parenthetical count unit expectations`

What changed:

- BLVR/PAL notes now better preserve:
  - explicit valve totals
  - target-lobe normalization
  - same-session Chartis / localization bundling when integral to same-session valve placement
- Same-session `31634` is suppressed only in the measured same-lobe / integral-localization scenarios supported by the selected anchors.

Primary files touched:

- `app/extraction/postprocessing/clinical_guardrails.py`
- `app/registry/deterministic_extractors.py`
- `tests/registry/test_codex_plan_third_pass_march2026.py`
- `tests/registry/test_fixpack_blvr_pal_regressions.py`

Measured BLVR/PAL anchor-note outcomes:

- `batch_4/note_004`: improved
  - before: `target_lobe=None`, no valve count, `cpt_codes=['31634', '31647']`
  - after: `target_lobe='LUL'`, `number_of_valves=4`, `cpt_codes=['31647']`
- `batch_4/note_007`: improved
  - before: `target_lobe='Lingula'`, no valve count
  - after: `target_lobe='LUL'`, `number_of_valves=4`, preserved treated segments
- `batch_4/note_018`: improved
  - before: `target_lobe='RLL'`, valve count missing
  - after: `target_lobe='RLL'`, `number_of_valves=2`, `cpt_codes=['31647']`

BLVR/PAL validation completed:

- new real-note regression:
  - `tests/registry/test_fixpack_blvr_pal_regressions.py`
- adjacent focused validations:
  - `tests/registry/test_codex_plan_third_pass_march2026.py`
  - `tests/registry/test_registry_to_cpt_blvr_chartis_sedation.py`
  - `tests/registry/test_extraction_quality_fixpack_batch4_march2026.py`

Important caveat:

- The pre-fix live probe evidence for BLVR/PAL used the TF-IDF fallback path while the current workspace used the ONNX-backed path.
- Those probes are supportive note-level evidence, not a clean apples-to-apples batch measurement.

BLVR/PAL closure status:

- Closed only for:
  - the committed anchored implementation slice
  - the focused validations above
- Still unverified:
  - broader March-family impact
  - downstream/UI/export behavior
  - broader batch-level shadow measurement

### Completed - Negation / Complication Gating

This slice is now committed on branch and closed at the requested anchored evidence level.

Committed change:

- `9596d1db updates`

What changed:

- routine hemostasis / `no significant bleeding` language no longer becomes a bleeding complication
- masked-text lesion snippets no longer reintroduce false endobronchial lesion findings when the raw note negates endobronchial disease

Primary files touched:

- `app/extraction/postprocessing/clinical_guardrails.py`
- `app/registry/postprocess/complications_reconcile.py`
- `app/registry/application/registry_service.py`
- `tests/registry/test_fixpack_negation_complication_regressions.py`

Measured anchor-note outcomes:

- `batch_1/note_004`: improved
  - false bleeding complication / Nashville 2 cleared
- `batch_1/note_039`: improved
  - false bleeding complication / Nashville 2 cleared
- `batch_6/note_009`: improved
  - corrected evidence shows the reliable pre-fix baseline under the exact regression path was `diagnostic_bronchoscopy=None`
  - committed state restores `diagnostic_bronchoscopy.performed=True` with no lesion/mass/tumor carryover

Important note on `batch_6/note_009`:

- An earlier review report incorrectly described the pre-fix baseline as `inspection_findings='lesion'`.
- The clean rerun using the exact single-note regression path showed the reliable pre-fix baseline was actually missing `diagnostic_bronchoscopy` entirely.
- Treat the corrected interpretation above as authoritative.

Focused validation completed:

- `tests/registry/test_fixpack_negation_complication_regressions.py`
- `tests/registry/test_codex_plan_first_pass_march2026.py`
- `tests/registry/test_codex_plan_second_pass_march2026.py`
- `tests/registry/test_extraction_quality_fixpack_march2026.py -k 'endobronchial or bleeding or hemostasis'`

Important caveat:

- The pre-fix `batch_6/note_009` anchor run used the TF-IDF fallback path while the committed-state run used the ONNX-backed path.
- That note should be treated as supportive anchored evidence, not a clean backend A/B measurement.

Negation/complication closure status:

- Closed only for:
  - the committed anchored note-level slice
  - the focused validations above
- Still unverified:
  - broader March-family impact
  - downstream/UI/export behavior

### Completed - Target Location Normalization

This cluster now has two committed, measured sub-slices and one broader measurement-only follow-up.

Committed target-location sub-slices:

- `6576c818 Normalize fiducial target location text`
- `06e7ec31 Clean navigation target pollution from note text`
- `50ebf29d Tighten`

#### Sub-slice 1 - Fiducial target-location normalization

What changed:

- Fiducial/navigation notes now recognize narrow procedural phrases such as:
  - `target in LLL posterior basal segment`
  - `target in the apicoposterior LUL was reached`
- This prevents those notes from falling back to `Unknown target` when a true target is explicitly documented.

Primary files touched:

- `app/registry/processing/navigation_fiducials.py`
- `tests/registry/test_navigation_fiducials.py`
- `tests/registry/test_fixpack_target_location_regressions.py`

Measured anchor-note outcomes:

- `batch_1/note_014`: improved
  - before: `target_location_text='Unknown target'`, `target_lobe=None`
  - after: `target_location_text='LLL posterior basal segment'`, `target_lobe='LLL'`
- `batch_6/note_030`: improved
  - before: `target_location_text='Unknown target'`, `target_lobe=None`
  - after: `target_location_text='apicoposterior LUL'`, `target_lobe='LUL'`

Focused validation completed:

- `tests/registry/test_fixpack_target_location_regressions.py`
- `tests/registry/test_navigation_fiducials.py`

Important caveat:

- The pre-fix live probe used the TF-IDF fallback path while the committed-state probe used the ONNX-backed path.
- Those probe outputs are supportive anchored evidence, not a clean apples-to-apples batch measurement.

#### Sub-slice 2 - Navigation target pollution cleanup (`batch_3/note_003`)

What changed:

- `navigation_targets.py` no longer promotes planning/table/impression prose into `navigation_targets` for the original pollution anchor.
- The parser now prefers narrow intra-procedural target confirmation text and avoids treating mid-sentence pseudo-headers as real target lines.

Primary files touched:

- `app/registry/processing/navigation_targets.py`
- `tests/registry/test_navigation_targets_engage_fallback_sampling.py`
- `tests/registry/test_fixpack_target_location_pollution_regressions.py`

Measured anchor-note outcome:

- `batch_3/note_003`: improved
  - before: 2 polluted targets from planning/impression prose
  - after: 1 clean target
  - final structured target: `LUL apical-posterior segment (LB1+2)` / `target_lobe='LUL'`

Focused validation completed:

- `tests/registry/test_fixpack_target_location_pollution_regressions.py`
- `tests/registry/test_navigation_targets_engage_fallback_sampling.py`
- `tests/registry/test_navigation_targets_numbered_targets.py`

#### Sub-slice 3 - Navigation target header/planning cleanup (`batch_4/note_011`, `batch_4/note_015`, `batch_6/note_005`)

What changed:

- `navigation_targets.py` now handles:
  - target-table first-column rows such as `LLL nodule`
  - short lobe-first target phrases such as `LLL nodule` / `PET-avid LLL nodule`
- This prevents the later heuristic fallback from promoting non-procedural header/planning prose into `navigation_targets`.

Primary files touched:

- `app/registry/processing/navigation_targets.py`
- `tests/registry/test_navigation_targets_engage_fallback_sampling.py`
- `tests/registry/test_fixpack_target_location_header_planning_regressions.py`

Measured anchor-note outcomes:

- `batch_4/note_011`: improved
  - before: demographic/header prose populated the target field
  - after: `target_location_text='LLL nodule'`, `target_lobe='LLL'`
- `batch_4/note_015`: improved
  - before: note-header prose populated the target field
  - after: `target_location_text='LLL nodule'`, `target_lobe='LLL'`
- `batch_6/note_005`: improved
  - before: planning prose populated the target field
  - after: `target_location_text='PET-avid LLL nodule'`, `target_lobe='LLL'`
- `batch_3/note_003`: preserved as a compatibility check

Focused validation completed:

- `tests/registry/test_fixpack_target_location_header_planning_regressions.py`
- `tests/registry/test_navigation_targets_engage_fallback_sampling.py`
- `tests/registry/test_navigation_targets_numbered_targets.py`

Broader measurement-only pollution-family follow-up:

- A later comparison pass re-checked:
  - `batch_3/note_003`
  - `batch_2/note_011`
  - `batch_2/note_036`
  - `batch_1/note_023`
  - `batch_5/note_031`
  - `batch_4/note_011`
  - `batch_4/note_015`
  - `batch_6/note_005`
- Result:
  - the original `batch_3/note_003` anchor improved
  - the later three-note header/planning cleanup was justified by still-live same-family pollution on:
    - `batch_4/note_011`
    - `batch_4/note_015`
    - `batch_6/note_005`

Target-location closure status:

- Closed only for:
  - the committed fiducial target-location sub-slice
  - the committed `batch_3/note_003` pollution sub-slice
  - the committed header/planning pollution sub-slice for:
    - `batch_4/note_011`
    - `batch_4/note_015`
    - `batch_6/note_005`
- Still unverified:
  - broader `target_location_normalization` family closure
  - downstream/UI/export behavior

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
- `tests/registry/test_fixpack_percutaneous_ablation_regressions.py`
- `tests/registry/test_fixpack_blvr_pal_regressions.py`
- `tests/registry/test_fixpack_negation_complication_regressions.py`
- `tests/registry/test_fixpack_target_location_regressions.py`
- `tests/registry/test_fixpack_target_location_pollution_regressions.py`
- `tests/registry/test_fixpack_target_location_header_planning_regressions.py`
- `tests/registry/test_navigation_fiducials.py`
- `tests/registry/test_navigation_targets_engage_fallback_sampling.py`
- `tests/registry/test_navigation_targets_numbered_targets.py`

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

- `make test` was not rerun again after the later airway-device, EBUS, percutaneous, BLVR/PAL, negation/complication, or target-location follow-on work, so the current repo-wide failure picture beyond the focused validations remains unrefreshed.

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

- No broader March rerun or shadow diff was performed after the later airway-device semantic work, EBUS station fix, committed percutaneous slice, or committed BLVR/PAL slice.
- So broader batch impact from all of those later completed slices remains unverified.

## Known Note-Level Changes After Today

Anchor notes now explicitly measured and updated this session:

- `batch_3/note_032`: improved and semantically resolved for mature trach exchange
- `batch_3/note_039`: improved and semantically resolved for Montgomery T-tube exchange routing
- `batch_3/note_046`: cleaner after airway-device precision work
- `batch_6/note_012`: preserved as the trach-exchange non-regression guard
- `batch_1/note_009`: preserved and measured good for EBUS
- `batch_2/note_033`: improved / fixed for EBUS station counting and CPT derivation
- `batch_5/note_002`: improved for percutaneous cryoablation leakage
- `batch_5/note_006`: same / protected in the measured percutaneous subset
- `batch_5/note_012`: same / protected in the measured percutaneous subset
- `batch_5/note_024`: same / protected in the measured percutaneous subset
- `batch_4/note_004`: improved for BLVR target-lobe / valve-count / same-session `31634`
- `batch_4/note_007`: improved for BLVR `LUL` normalization and valve count
- `batch_4/note_018`: improved for PAL valve count
- `batch_1/note_004`: improved for false bleeding complication removal
- `batch_1/note_039`: improved for false bleeding complication removal
- `batch_6/note_009`: improved, with corrected evidence showing restored diagnostic bronchoscopy and no lesion carryover
- `batch_1/note_014`: improved for fiducial target-location extraction
- `batch_6/note_030`: improved for fiducial target-location extraction
- `batch_3/note_003`: improved for navigation target planning/impression pollution
- `batch_4/note_011`: improved for navigation target header pollution
- `batch_4/note_015`: improved for navigation target header pollution
- `batch_6/note_005`: improved for navigation target planning pollution

Notes that should no longer be described as the next open anchors from this session:

- `batch_1/note_009`
- `batch_3/note_032`
- `batch_3/note_039`
- `batch_5/note_002`
- `batch_4/note_004`
- `batch_4/note_007`
- `batch_4/note_018`
- `batch_1/note_014`
- `batch_6/note_030`
- `batch_3/note_003`
- `batch_4/note_011`
- `batch_4/note_015`
- `batch_6/note_005`

## What Still Needs Completed

Still unverified / still deferred:

- Broader March batch impact for the later completed slices:
  - `airway_device_action`
  - `ebus_station_logic`
  - `percutaneous_ablation`
  - `blvr_pal_valve`
  - requires a new March rerun / shadow diff if quantified improvement is needed

- Broader consumer/UI validation
  - airway-device only has:
    - extraction/evidence serialization checks
    - generic procedure enumeration checks
    - one anchored reporter/render path check
  - EBUS has no broader consumer/UI validation from today's work
  - percutaneous only has the measured four-note anchored subset
  - BLVR/PAL only has the anchored implementation slice plus focused validations

- Full repo validation refresh
  - the branch-triage `make test` failure list above is still the latest repo-wide snapshot
  - no later full-suite rerun was done after the airway-device semantic slice, EBUS fix, percutaneous slice, BLVR/PAL slice, or local negation/complication work

- Broader quantified impact still remains unmeasured for the later committed slices:
  - `negation_complication_gating`
  - committed `target_location_normalization` sub-slices
  - requires a broader March rerun / shadow diff if quantified family or batch impact is needed

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

Current best next move:

- pause `target_location_normalization` here and re-rank the next unresolved extraction cluster rather than continuing to broaden navigation work

After that, two reasonable choices remain:

- If quantified impact is needed before more feature work:
  - run a broader March rerun / shadow diff
  - optionally refresh `make test` after that to separate true new regressions from already-known repo-wide failures

- If another PR-sized extraction slice is preferred before the broader rerun:
  - select the next unresolved cluster from the plan/handoff context now that:
    - `negation_complication_gating` is committed
    - the current measured `target_location_normalization` sub-slices are committed

Updated cluster status from this session:

- `airway_device_action`: closed only for the anchored slice and limited downstream checks described above
- `ebus_station_logic`: closed only for the measured anchor-note slice through the normal extraction path
- `percutaneous_ablation`: closed only for the committed anchored fix plus the measured four-note subset
- `blvr_pal_valve`: closed only for the committed anchored implementation slice plus focused validations
- `negation_complication_gating`: closed only for the committed anchored note-level slice plus focused validations
- `target_location_normalization`: partially closed only for the committed measured sub-slices described above; broader family closure remains unverified

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

- Focused percutaneous validations:
  - targeted `pytest` runs on:
    - `tests/registry/test_fixpack_percutaneous_ablation_regressions.py`
    - `tests/registry/test_codex_plan_first_pass_march2026.py`
    - `tests/registry/test_keyword_guard_overrides.py -k 'ablation or cryo'`
  - focused four-note comparison on:
    - `batch_5/note_002`
    - `batch_5/note_006`
    - `batch_5/note_012`
    - `batch_5/note_024`

- Focused BLVR/PAL validations:
  - targeted `pytest` runs on:
    - `tests/registry/test_fixpack_blvr_pal_regressions.py`
    - `tests/registry/test_codex_plan_third_pass_march2026.py`
    - `tests/registry/test_registry_to_cpt_blvr_chartis_sedation.py`
    - `tests/registry/test_extraction_quality_fixpack_batch4_march2026.py`
  - targeted extraction measurement on:
    - `batch_4/note_004`
    - `batch_4/note_007`
    - `batch_4/note_018`

- Focused local negation/complication validations:
  - targeted `pytest` runs on:
    - `tests/registry/test_fixpack_negation_complication_regressions.py`
    - `tests/registry/test_codex_plan_first_pass_march2026.py`
    - `tests/registry/test_codex_plan_second_pass_march2026.py`
    - `tests/registry/test_extraction_quality_fixpack_march2026.py -k 'endobronchial or bleeding or hemostasis'`
  - targeted extraction / regression-path measurement on:
    - `batch_1/note_004`
    - `batch_1/note_039`
    - `batch_6/note_009`

- Focused target-location validations:
  - targeted `pytest` runs on:
    - `tests/registry/test_fixpack_target_location_regressions.py`
    - `tests/registry/test_navigation_fiducials.py`
    - `tests/registry/test_fixpack_target_location_pollution_regressions.py`
    - `tests/registry/test_fixpack_target_location_header_planning_regressions.py`
    - `tests/registry/test_navigation_targets_engage_fallback_sampling.py`
    - `tests/registry/test_navigation_targets_numbered_targets.py`
  - targeted extraction measurement on:
    - `batch_1/note_014`
    - `batch_6/note_030`
    - `batch_3/note_003`
    - `batch_4/note_011`
    - `batch_4/note_015`
    - `batch_6/note_005`
  - broader measurement-only pollution-family subset re-check on:
    - `batch_2/note_011`
    - `batch_2/note_036`
    - `batch_1/note_023`
    - `batch_5/note_031`

## Suggested Fresh-Session Prompt

Use something close to this on the next machine:

`Read extraction_results_3_9_26/codex_master_prompt.md, extraction_results_3_9_26/pipeline_improvement_plan.md, and extraction_results_3_9_26/session_handoff_2026_03_10.md. Use the handoff as the authoritative working summary. Treat airway_device_action, ebus_station_logic, percutaneous_ablation, blvr_pal_valve, and negation_complication_gating as closed only for their explicitly measured slices. Treat target_location_normalization as partially closed only for the committed measured sub-slices in this handoff, with broader family closure still unverified. If quantified impact is needed, rerun the broader March shadow diff first; otherwise re-rank the next unresolved extraction cluster instead of broadening navigation work further.`
