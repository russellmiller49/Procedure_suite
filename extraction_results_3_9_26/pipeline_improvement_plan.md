# Pipeline improvement plan for structured extraction

## Reviewed inputs

- [gitingest.md](sandbox:/mnt/data/gitingest.md)
- [gitingest_details.md](sandbox:/mnt/data/gitingest_details.md)
- [BATCH_extractions.txt](sandbox:/mnt/data/BATCH_extractions.txt)
- [batch1 eval](sandbox:/mnt/data/extraction_quality_structured_batch1.json)
- [batch2 eval](sandbox:/mnt/data/extraction_quality_structured_batch_2.json)
- [batch3 eval](sandbox:/mnt/data/batch_3_extraction_evaluation_structured.json)
- [batch4 eval](sandbox:/mnt/data/batch_4_extraction_quality_structured.json)
- [batch5 eval](sandbox:/mnt/data/batch5_extraction_evaluation_structured.json)
- [batch6 eval](sandbox:/mnt/data/extraction_evaluation_batch6_structured.json)

## Executive summary

- I reviewed 300 note-level evaluations across 6 batches. The mean score across all notes is **73.8**, with **75 PASS**, **104 WARNING**, and **121 FAIL**.
- The failures are not random. They cluster into a few recurring families: encounter-family routing errors, EBUS sampled-vs-inspected reconciliation, BLVR bundling/counting, trach/stent/T-tube action typing, negation/complication logic, and target/location normalization.
- The most important architectural change is to move from "many local heuristics plus late overrides" to **family-aware routing -> canonical normalized state -> coding policy**. Several failing notes already show audit warnings that indicate the pipeline tried to self-correct, but coding still used inconsistent intermediate state.

## Batch-level performance

|   batch |   avg_score |   pass |   warning |   fail |
|--------:|------------:|-------:|----------:|-------:|
|       1 |        83.3 |     21 |        19 |     10 |
|       2 |        75.1 |     18 |        11 |     21 |
|       3 |        64.3 |      5 |        14 |     31 |
|       4 |        75.6 |     13 |        17 |     20 |
|       5 |        63.5 |      7 |        12 |     31 |
|       6 |        81.1 |     11 |        31 |      8 |

Interpretation:
- **Batch 3** and **Batch 5** are the low points. Batch 3 is dominated by trach/PDT/T-tube/stent-family confusion. Batch 5 is dominated by CT-guided or percutaneous ablation notes that are being forced into bronchoscopic ablation/cryotherapy/31641-style buckets.
- **Batch 4** is largely a BLVR/persistent-air-leak batch: valve counts, target lobe capture, and unsupported 31634 add-ons recur.
- **Batch 6** shows that the core pipeline can recover to a better baseline (81.1 average, only 8 FAIL), but it still carries many warnings because negation, station counts, quantity capture, and coding-policy precision remain weak.

## Rule-based grouping of evaluator comments (approximate prevalence)

These counts come from keyword grouping of evaluator comments, so treat them as directional rather than exact truth labels.

| category                                                  |   note_count |   avg_score |   pass |   warning |   fail | batches     |
|:----------------------------------------------------------|-------------:|------------:|-------:|----------:|-------:|:------------|
| Sedation/anesthesia handling                              |           48 |        71.1 |     10 |        18 |     20 | 1,2,3,4,5   |
| Percutaneous ablation misrouted into bronchoscopic family |           46 |        59.9 |      5 |        10 |     31 | 3,5,6       |
| Target/location normalization                             |           44 |        79.1 |     15 |        15 |     14 | 1,2,3,4,6   |
| Negation/polarity in inspection findings                  |           39 |        76.5 |      2 |        27 |     10 | 1,2,3,4,5,6 |
| EBUS station/action logic                                 |           37 |        76   |      8 |        16 |     13 | 1,2,3,4,6   |
| Complication severity overcall or miss                    |           31 |        67.3 |      5 |         9 |     17 | 1,2,3,4,5,6 |
| Stent or T-tube action-type/location                      |           31 |        72.3 |      6 |        13 |     12 | 1,2,3,4,6   |
| BLVR / valve count / 31634 bundling                       |           22 |        68.1 |      1 |         8 |     13 | 3,4,5,6     |
| Bundling / NCCI policy                                    |           13 |        73.5 |      0 |         8 |      5 | 1,5,6       |
| Trach exchange / PDT family confusion                     |            8 |        47.5 |      0 |         2 |      6 | 3,4,6       |
| Evidence anchored to specimen text                        |            6 |        67.2 |      1 |         2 |      3 | 1,2         |

## What the data says the architecture is doing wrong

### 1) Encounter-family routing is failing before extraction normalization

- CT-guided/percutaneous ablation notes are repeatedly routed into bronchoscopic families, usually ending in unsupported 31641/cryotherapy/thermal-ablation interpretations.
- EUS-B staging can bleed into linear EBUS, causing double counting or wrong station ownership.
- Trach exchange/PDT notes can be reduced to bronchoscopy-only or even valve/stent-like families, which means the primary procedure is lost before coding begins.

### 2) Existing self-correction exists, but it is ordered too late or writes to the wrong layer

- The extraction outputs already show warnings such as `EBUS_SPECIMEN_OVERRIDE`, `EBUS_NARRATIVE_RECONCILE`, `AUTO_EBUS_NEEDLE_GAUGE`, `AUTO_CORRECTED`, and `HARD_OVERRIDE` in cases that still fail final evaluation.
- That pattern implies the pipeline already has patch logic, but **coding is still being derived from stale or partially reconciled state**.

### 3) Extraction truth and coding policy are not cleanly separated

- A recurring problem is that the extractor suppresses or invents procedure families to make coding work. That is backwards.
- The extractor should first represent what happened. The coder should then apply same-site bundling, NCCI rules, and uncertainty flags.

### 4) Negation and routine-hemostasis handling are weak

- Many notes explicitly say **no endobronchial lesion/mass/tumor**, but the inspection narrative becomes positive anyway.
- Routine cold saline, suction, wedge positioning, or transient oozing are often escalated into formal complications or Nashville bleeding grades.

### 5) Source priority is inconsistent

- Procedure tables and intervention bullets are frequently overridden by specimen-log text, header text, or plan text.
- That is why station sampling, target location, BAL location, and biopsy lobe can become malformed or drift into the wrong family.

## Highest-priority workstreams

### P0 — Build an encounter router and canonical normalized state

**Goal:** stop family confusion before downstream heuristics or coding.

**Implement:**
- Add a lightweight pre-normalization router that classifies notes into one or more **encounter families** with confidence: `bronchoscopic_airway`, `peripheral_navigation`, `linear_ebus`, `eus_b`, `blvr_pal_valve`, `pleural`, `trach_exchange_or_pdt`, `airway_stent_or_t_tube`, `whole_lung_lavage`, `percutaneous_ablation`.
- Enforce family exclusivity or explicit coexistence rules. Examples:
  - `percutaneous_ablation` cannot silently derive bronchoscopic `31641`/cryotherapy families.
  - `eus_b` stations cannot be counted inside bronchoscopic `linear_ebus` station totals.
  - `existing_stent_assessment_only` must not auto-create `revision`.
- Persist the router output in the registry payload so downstream code can audit and respect it.

**Likely repo touchpoints (from the repo manifest):**
- `app/registry/extraction/structurer.py`
- `app/registry/processing/focus.py`
- `app/agents/run_pipeline.py`
- `app/registry/schema_filter.py`

### P0 — EBUS/EUS-B reconciliation before coding

**Goal:** fix sampled-vs-inspected station logic and 31652 vs 31653 derivation.

**Implement:**
- Define canonical `node_event.action` values: `visualized_only`, `sampled_tbna`, `sampled_fna`, `sampled_other`.
- Compute `stations_sampled` from canonical node events only after reconciliation.
- Reconcile sources in this priority order: **procedure table / intervention bullets -> narrative sampling sentence -> specimen log -> generic findings**.
- Keep `eus_b` stations in a separate structure and exclude them from bronchoscopic EBUS CPT derivation.
- Derive 31652/31653 from the **unique sampled bronchoscopic stations** after de-duplication.

**Likely repo touchpoints:**
- `app/registry/heuristics/linear_ebus_station_detail.py`
- `app/coder/ebus_rules.py`
- `app/registry/slots/ebus.py`
- `app/registry/ner_mapping/entity_to_registry.py`
- `tests/registry/test_linear_ebus_stations_detail.py`
- `tests/registry/test_eus_b_sampling_regressions.py`

### P0 — Negation and complication gating

**Goal:** reduce false positive airway findings and complication inflation.

**Implement:**
- Add scoped negation to inspection findings for lesion/mass/tumor/foreign body language.
- Add a `routine_hemostasis` concept that captures cold saline, suction, wedge positioning, iced saline, and brief oozing without escalating to a complication unless severity thresholds are met.
- Only assign Nashville grades when there is explicit severity, persistent bleeding, transfusion/escalation, blocker/tamponade, or other material consequence.
- If the note explicitly says `Complications: None`, require a higher threshold before creating a structured complication.

**Likely repo touchpoints:**
- `app/domain/text/negation.py`
- `app/coder/adapters/nlp/simple_negation_detector.py`
- `app/registry/postprocess/template_checkbox_negation.py`
- `app/registry_cleaning/clinical_qc.py`

### P1 — BLVR / PAL valve normalization and bundling

**Goal:** fix valve count, target-lobe capture, and unsupported 31634 add-ons.

**Implement:**
- Normalize BLVR/PAL cases into a dedicated structure with: `indication`, `target_lobe`, `target_segments`, `chartis_result`, `number_of_valves`, `deployed_valves[]`, and `same_session_localization=true/false`.
- Suppress separate 31634 when localization/occlusion is integral to same-session 31647, unless you have an explicit policy exception with evidence.
- Distinguish emphysema BLVR from persistent-air-leak valve placement, but keep the shared device logic.

**Likely repo touchpoints:**
- `app/registry/slots/blvr.py`
- `app/registry/slots/therapeutics.py`
- `app/coder/ncci.py`
- `app/domain/coding_rules/evidence_context.py`

### P1 — Stent, T-tube, and trach action taxonomy

**Goal:** stop collapsing device notes into the wrong action type.

**Implement:**
- Add explicit action enums: `assessment_only`, `placement`, `revision_or_reposition`, `removal`, `exchange`, `toileting`, `granulation_treatment`, `t_tube_insertion`.
- Separate `existing_device_seen` from `device_manipulated`.
- Add dedicated procedure objects for `tracheostomy_exchange`, `percutaneous_tracheostomy`, and `bronchoscopy_through_established_trach` rather than forcing all trach notes into bronchoscopy coding.

**Likely repo touchpoints:**
- `app/registry/slots/stent.py`
- `app/registry/slots/therapeutics.py`
- `app/registry/deterministic/anatomy.py`
- `app/registry/schema.py` / `app/registry/schema_granular.py`

### P1 — Target/location normalization and missing key procedures

**Goal:** stop lobe leakage, garbled targets, and missed secondary procedures.

**Implement:**
- Build a canonical `target_site` object with `organ`, `side`, `lobe`, `segment`, `source_span_type`, `source_priority`, and `confidence`.
- Prevent specimen counts and non-anatomic phrases from entering target fields.
- Add or harden explicit procedure families for:
  - `transbronchial_biopsy` / forceps biopsy
  - `fiducial_placement`
  - `endobronchial_blocker_or_isolation`
  - `watanabe_spigot_placement`
  - `brachytherapy_catheter_placement`
  - `bronchoscopic_peripheral_ablation`
  - `percutaneous_ablation`

**Likely repo touchpoints:**
- `app/registry/heuristics/navigation_targets.py`
- `app/registry/processing/navigation_fiducials.py`
- `app/registry/slots/tblb.py`
- `app/registry/slots/therapeutics.py`
- `app/registry/extraction/structurer.py`

### P2 — Sedation/anesthesia confidence handling

**Goal:** stop arbitrary picks when templates conflict.

**Implement:**
- Store `sedation_type`, `anesthesia_support`, `airway_support`, and `source_conflict=true/false` separately.
- If there is conflicting template text, preserve ambiguity rather than overwriting with a single hard label.
- Keep procedural sedation coding derivation downstream and gated on explicit provider/time requirements.

## Delivery sequence I would use

1. Lock current failures into regression tests.
2. Implement encounter router and family exclusivity.
3. Fix EBUS/EUS-B reconciliation and code derivation.
4. Add negation + routine-hemostasis gating.
5. Fix percutaneous-vs-bronchoscopic ablation routing.
6. Fix BLVR counts and 31634 bundling.
7. Fix trach/stent/T-tube action taxonomy.
8. Fix target normalization and missing device procedures.
9. Clean up sedation ambiguity handling.

## Acceptance criteria for the first hardening pass

- No CT-guided/percutaneous case emits bronchoscopic 31641/cryotherapy/thermal-ablation families by default.
- No same-session BLVR/PAL valve case emits 31634 unless there is an explicit exception path.
- Existing-stent surveillance notes do not emit revision/reposition unless the note documents manipulation.
- All EBUS regression notes derive sampled station counts from canonical node events, not specimen-only text.
- Notes that say `no endobronchial lesion/mass/tumor` do not produce positive lesion/tumor inspection findings.
- Routine cold saline / wedge / suction hemostasis with `Complications: None` does not auto-grade bleeding.
- Target/location fields never contain specimen-count text or `Unknown target` when the lobe/segment is explicit in the note.

## Codex instructions

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
