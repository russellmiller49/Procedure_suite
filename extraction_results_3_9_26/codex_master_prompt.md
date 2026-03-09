### Master prompt for Codex

```text
You are working in the proc_suite repository. Your goal is to reduce the systematic extraction and coding failures identified in the six structured evaluation batches.

Operating rules:
1. Work in small, reviewable commits.
2. Do not refactor unrelated code.
3. First add focused regression tests for the failing note patterns before changing logic.
4. Prefer fixing routing and canonical normalization before adding new post-hoc overrides.
5. Keep extraction truth separate from coding policy. Represent what happened first; apply bundling/NCCI/coder-review logic afterwards.
6. When ambiguity remains, preserve uncertainty with audit flags instead of hallucinating a procedure or CPT.

Files to inspect first:
- app/registry/extraction/structurer.py
- app/registry/processing/focus.py
- app/registry/heuristics/linear_ebus_station_detail.py
- app/registry/heuristics/navigation_targets.py
- app/registry/processing/navigation_fiducials.py
- app/registry/self_correction/judge.py
- app/registry/self_correction/apply.py
- app/registry/slots/stent.py
- app/registry/slots/blvr.py
- app/registry/slots/therapeutics.py
- app/coder/ebus_rules.py
- app/coder/ncci.py
- app/domain/text/negation.py
- app/coder/adapters/nlp/simple_negation_detector.py
- app/registry/postprocess/template_checkbox_negation.py
- ops/tools/unified_pipeline_batch.py
- ops/tools/run_quality_gates.py
- ml/scripts/shadow_diff_structured_extraction.py

Implementation order:
A. Add regression packs for:
   - EBUS sampled-vs-inspected failures (e.g. batch1 note_001/note_002; batch2 note_001/note_030; batch6 note_008/note_019)
   - percutaneous ablation misrouting (batch5 note_002/note_006/note_012/note_024)
   - BLVR bundling/count errors (batch4 note_001/note_004/note_007/note_018)
   - trach/T-tube/stent action errors (batch3 note_029/note_032/note_034/note_036/note_038; batch6 note_007/note_012)
   - negation/complication errors (batch1 note_004/note_039; batch6 note_009/note_021/note_031)

B. Add an encounter-family router and make downstream modules consume it.
C. Reconcile EBUS/EUS-B node events into a canonical sampled-station representation before coding.
D. Add negation-scoped inspection findings and routine-hemostasis suppression.
E. Split percutaneous ablation from bronchoscopic ablation.
F. Normalize BLVR/PAL cases and suppress same-session 31634 unless explicitly allowed.
G. Add explicit device/trach action enums: assessment_only, placement, revision_or_reposition, removal, exchange, t_tube_insertion.
H. Normalize target-site objects so anatomic targets cannot be overwritten by specimen-count text.
I. Re-run the existing batch/quality tools after each workstream and summarize before/after deltas.

Required outputs:
- updated tests
- minimal code changes
- short changelog of what root cause each change fixes
- before/after regression results
```

### Smaller Codex prompts by workstream

#### Prompt 1 — Fix EBUS sampled-vs-inspected logic

```text
Add regression tests for EBUS notes where station tables/specimen logs show true sampling but node_events are left inspected_only, causing 31652/31653 errors. Implement a canonical node-event reconciliation pass that prioritizes procedural sampling lines over specimen-only text, separates EUS-B from bronchoscopic EBUS, and derives 31652/31653 from unique sampled bronchoscopic stations only.
```

#### Prompt 2 — Fix percutaneous-vs-bronchoscopic ablation routing

```text
Add regression tests for CT-guided/percutaneous microwave, cryo, RFA, and PEF ablation notes that are currently producing bronchoscopic 31641/cryotherapy/thermal-ablation families. Add a pre-normalization encounter router and dedicated percutaneous_ablation schema path so these notes never default into bronchoscopic therapeutic families.
```

#### Prompt 3 — Fix BLVR/PAL valve counts and 31634 bundling

```text
Add regression tests for BLVR and persistent-air-leak valve cases with wrong valve counts, blank target lobe, and unsupported 31634 in same-session valve placement. Normalize valve deployment into a dedicated BLVR/PAL structure, preserve target lobe/segments and Chartis result, and suppress 31634 unless a policy exception is explicitly met.
```

#### Prompt 4 — Fix trach/stent/T-tube action typing

```text
Add regression tests for tracheostomy exchange, PDT, Y-stent, and Montgomery T-tube notes that are currently reduced to bronchoscopy-only or misread as revision. Add explicit action enums and dedicated procedure families for trach exchange/PDT/established-trach bronchoscopy/T-tube insertion. Do not infer stent revision from assessment-only notes.
```

#### Prompt 5 — Fix negation and complication overcalls

```text
Add regression tests for notes that explicitly say no endobronchial lesion/mass/tumor and notes with routine cold saline/suction/wedge hemostasis but no true complication. Add scoped negation to inspection findings and a routine_hemostasis suppression rule so these cases no longer create false lesion/tumor findings or inflated Nashville bleeding grades.
```

## Final recommendation

Do **not** start by adding more isolated overrides. The repo already appears to have many override paths. Start by fixing routing and canonical normalization, then let self-correction and coding consume a cleaner state.
