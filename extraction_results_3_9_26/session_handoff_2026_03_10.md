# Session Handoff - March 10, 2026

This note is a reconstruction from the current branch state plus session notes. Some of the earlier branch work was done externally with a custom GPT before this desktop session, so use this as the working handoff rather than a perfect commit-by-commit history.

Start the next session by reading:
- `extraction_results_3_9_26/codex_master_prompt.md`
- `extraction_results_3_9_26/pipeline_improvement_plan.md`
- this handoff file

## What Was Implemented So Far

Known completed clusters on this branch:

- First pass:
  - Linear EBUS station reconciliation now excludes EUS-B-only content before bronchoscopic station counting / CPT derivation.
  - CT-guided or percutaneous lung ablation language no longer leaks into bronchoscopic `peripheral_ablation` / CPT `31641`.
  - Routine biopsy-site oozing with standard hemostasis, including phrases like `no active bleeding`, no longer becomes a bleeding complication.

- Second pass:
  - Negated airway sampling language such as `brushings ... not obtained` and `endobronchial biopsies ... not obtained` now clears false `brushings` and `endobronchial_biopsy`.
  - Negated lesion phrases like `without focal endobronchial lesion` and `without endobronchial abnormality` are stripped from diagnostic inspection findings while preserving true findings like erythema.

- Third pass:
  - BLVR normalization now handles phrases such as `valve deployment x4` and `treated with four valves`.
  - Generic negative collateral ventilation language maps to structured negative Chartis / CV status.
  - Target-lobe normalization prefers `LUL` over stale `Lingula` carry-through when the note supports upper-lobe treatment.

- Fourth pass:
  - Routine trach exchange notes no longer promote `established_tracheostomy_route` or CPT `31615` incorrectly.
  - False BLVR extraction from trach-exchange note language is suppressed.
  - Montgomery T-tube insertion routes to airway stent placement, while exchange notes retain revision semantics.

- Fifth pass and latest follow-up work:
  - Blue Rhino PDT notes route to percutaneous tracheostomy, while mature trach exchanges stay on established-trach logic.
  - T-tube surveillance / sidearm bronchoscopy notes no longer become airway stent removal or revision, and diagnostic bronchoscopy `31622` survives even when masking blanks the `PROCEDURE:` line.
  - Same-session new Y-stent deployment / removal / redeployment stays on placement when appropriate; true preexisting-stent revision contexts keep revision semantics.
  - Compact EBUS lines like `7 x3 passes` are accepted as station `7`, while specimen-pass leakage like `passes 1-5` remains suppressed.
  - Navigation target extraction now handles prose such as `computer-assisted navigational bronchoscopy to LUL peripheral target`, dedupes repeated target mentions, canonicalizes to lobe labels like `LUL`, and avoids using generic `target lesion` specimen text as a target location.
  - BAL location trimming now works together with the target-site cleanup so BAL/specimen language does not bleed into navigation fields.

## Files Currently Touched On Branch

Core code files known to be part of the March-plan work:

- `app/extraction/postprocessing/clinical_guardrails.py`
- `app/registry/deterministic_extractors.py`
- `app/registry/evidence/verifier.py`
- `app/registry/heuristics/navigation_targets.py`
- `app/registry/legacy/adapters/airway.py`
- `app/registry/postprocess/__init__.py`
- `app/registry/postprocess/complications_reconcile.py`
- `app/registry/processing/navigation_targets.py`
- `app/registry/schema/granular_logic.py`

Regression / plan tests currently present:

- `tests/registry/test_codex_plan_first_pass_march2026.py`
- `tests/registry/test_codex_plan_second_pass_march2026.py`
- `tests/registry/test_codex_plan_third_pass_march2026.py`
- `tests/registry/test_codex_plan_fourth_pass_march2026.py`
- `tests/registry/test_codex_plan_fifth_pass_march2026.py`
- `tests/registry/test_fixpack_device_action_regressions.py`

Working-tree notes:

- The March artifact folder was reorganized from old top-level `extraction_results_3_9_26/batch_*` paths into `extraction_results_3_9_26/individual_batch_results_granular/batch_*`.
- There are also unrelated dirty local files in the working tree such as `.venv_pdf/*`, `phi_demo.db`, `data/coding_traces.jsonl`, and `data/knowledge/ip_coding_billing_v2_9.json`. Be careful not to blindly revert unrelated changes.

## Validation Completed

Focused regression ring passed after the latest fixes. This included:

- `tests/registry/test_codex_plan_first_pass_march2026.py`
- `tests/registry/test_codex_plan_second_pass_march2026.py`
- `tests/registry/test_codex_plan_third_pass_march2026.py`
- `tests/registry/test_codex_plan_fourth_pass_march2026.py`
- `tests/registry/test_codex_plan_fifth_pass_march2026.py`
- `tests/registry/test_fixpack_device_action_regressions.py`
- `tests/registry/test_airway_stent_vascular_plug_revision.py`
- `tests/registry/test_clinical_guardrails_stent_inspection.py`
- `tests/registry/test_complications_reconcile_precision.py`
- `tests/registry/test_ebus_config_station_count.py`
- `tests/registry/test_ebus_deterministic.py`
- `tests/registry/test_ebus_postprocess_enrichment.py`
- `tests/registry/test_ebus_postprocess_fallback.py`
- `tests/registry/test_ebus_site_block_reconcile.py`
- `tests/registry/test_ebus_specimen_override.py`
- `tests/registry/test_fixpack_trach_stent_elastography_normalization.py`
- `tests/registry/test_linear_ebus_stations_detail.py`
- `tests/registry/test_registry_extraction_ebus.py`
- `tests/registry/test_registry_to_cpt_airway_stent_assessment_only.py`
- `tests/registry/test_registry_to_cpt_blvr_chartis_sedation.py`
- `tests/registry/test_sedation_blvr.py`
- `tests/registry/test_tracheostomy_route.py`
- `tests/registry/test_regression_pack_updates_march_2026.py`
- `tests/coding/test_ebus_rules.py`
- `tests/coder/test_coding_rules_phase7.py`

Full repo validation was also run with `make test`. It still fails, currently with 15 failures concentrated in:

- `tests/common/test_path_redaction.py` x2
- `tests/quality/test_reporter_precision_extra_flags.py`
- `tests/registry/test_derive_procedures_from_granular_consistency.py`
- `tests/registry/test_external_notes_2_18_26_regressions.py`
- `tests/registry/test_navigation_targets_inline_target.py` x2
- `tests/registry/test_note_002_regression.py`
- `tests/reporter/test_golden_examples.py`
- `tests/reporting/test_pipeline_parity.py` x3
- `tests/reporting/test_render_parity_normalization.py` x3

Two focused regressions that were previously failing are now green:

- `tests/registry/test_fixpack_trach_stent_elastography_normalization.py::test_trach_change_note_does_not_derive_31600`
- `tests/registry/test_regression_pack_updates_march_2026.py::test_stent_action_classifier_gates_preexisting_context_and_exchange`

## March 9 Batch / Shadow-Diff Summary

The full March 9 six-batch extraction set was rerun and compared with pairwise shadow diffing.

Current rerun artifacts:

- New batch outputs: `/tmp/procsuite_march9_postpass/batch_1_current.txt` through `/tmp/procsuite_march9_postpass/batch_6_current.txt`
- Pairwise eval artifact: `/tmp/procsuite_march9_postpass/eval_all_batches_20260309_postpass.json`
- Previous local comparison artifact: `/tmp/procsuite_march9_rerun/eval_all_batches_20260309_current.json`

Clean before/after signal using the previous local rerun versus the latest rerun:

- Before this pass: `PASS 44 / WARNING 190 / FAIL 66`
- After this pass: `PASS 47 / WARNING 187 / FAIL 66`
- Delta: `+3 PASS / -3 WARNING / 0 FAIL`

Latest pairwise result versus the external March 9 baseline:

- `300` total notes
- `69 improved / 206 same / 25 regressed`
- New status counts: `PASS 47 / WARNING 187 / FAIL 66`

Remaining cluster counts after the latest rerun:

- `airway_device_action: 72`
- `percutaneous_ablation: 53`
- `ebus_station_logic: 39`
- `other: 35`
- `pleural_family: 15`
- `blvr: 13`
- `trach_device_routing: 11`
- `aspiration_clearance: 10`
- `negation_complication: 2`
- `target_normalization: 1`

Useful cluster movement versus the prior local rerun:

- Improved:
  - `trach_device_routing 14 -> 11`
  - `ebus_station_logic 41 -> 39`
  - `other 40 -> 35`
  - `blvr 16 -> 13`
  - `pleural_family 16 -> 15`
  - `percutaneous_ablation 54 -> 53`

- Worsened:
  - `airway_device_action 62 -> 72`
  - `negation_complication 1 -> 2`

## Known Note-Level Changes

Status-improved notes:

- `batch_3/note_029`: `FAIL -> WARNING` after PDT routing improved and `31600` / `31622` were captured more cleanly
- `batch_3/note_030`: `FAIL -> WARNING` after the established-trach misroute was corrected
- `batch_1/note_001`: `FAIL -> WARNING`
- `batch_1/note_032`: `FAIL -> WARNING`

Qualitative but still-warning improvements:

- `batch_6/note_010`
- `batch_6/note_030`
- `batch_6/note_046`

Regressions introduced or still concerning:

- `batch_1/note_009`: `WARNING -> FAIL`
- `batch_1/note_044`: `WARNING -> FAIL`
- `batch_3/note_032`: still `FAIL`
- `batch_3/note_039`: still `FAIL`
- `batch_3/note_046`: still `FAIL`, though cleaner than before

## Recommended Next Slice

Top 3 unresolved error clusters:

- `airway_device_action` (`72`)
- `percutaneous_ablation` (`53`)
- `ebus_station_logic` (`39`)

Recommended next PR-sized chunk:

- Isolate `airway_device_action` only.
- Work from the remaining trach / T-tube / surveillance-only airway-device notes as the fixture set.
- Keep the coding logic conservative:
  - prefer explicit procedural actions over inferred ones
  - do not promote procedures from inventory / device-surveillance language alone
  - do not derive CPT from pre-reconciled state
  - keep unsupported add-on suppression intact unless the note clearly supports it

Good next March-note fixtures for the next pass:

- `batch_3/note_032`
- `batch_3/note_039`
- `batch_3/note_046`
- `batch_6/note_012`

After `airway_device_action`, the next chunk should be `ebus_station_logic`, using problem notes like:

- `batch_1/note_009`
- `batch_2/note_033`

## Repro Commands Used

- Focused validation:
  - `pytest -q tests/registry/test_codex_plan_{first,second,third,fourth,fifth}_pass_march2026.py ... tests/coding/test_ebus_rules.py tests/coder/test_coding_rules_phase7.py`

- Full suite:
  - `make test`

- Batch rerun / pairwise comparison:
  - March rerun outputs were written under `/tmp/procsuite_march9_postpass/`
  - The inherited comparison script expects `/tmp/procsuite_march9_rerun/batch_*_current.txt`, so the latest outputs were temporarily copied there before running:
  - `/tmp/procsuite_march9_rerun/eval_pairwise_march9.py --output /tmp/procsuite_march9_postpass/eval_all_batches_20260309_postpass.json`

## Suggested Fresh-Session Prompt

Use something close to this on the next machine:

`Read extraction_results_3_9_26/codex_master_prompt.md, extraction_results_3_9_26/pipeline_improvement_plan.md, and extraction_results_3_9_26/session_handoff_2026_03_10.md. Then continue with the next highest-yield unresolved cluster, prioritizing airway_device_action batch-error reduction over heuristic expansion. Work test-first from the known March notes, rerun targeted tests after each patch, and rerun the batch shadow-diff before moving on.`
