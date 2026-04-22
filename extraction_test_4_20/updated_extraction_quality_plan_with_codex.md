# Updated Extraction Quality Improvement Plan with Codex Instructions

**Branch:** `russellmiller49/Procedure_suite`, branch `extraction_improvements`  
**Date:** 2026-04-20  
**Goal:** Improve the 20-note extraction batch from 65.4 / 100 toward ≥85 / 100 while preserving the repo's precision-first extraction architecture and keeping regressions bisectable.

---

## 0. Repo alignment corrections before implementation

Apply these corrections to the original plan before coding.

1. Use `app/registry/postprocess/__init__.py`, not `app/registry/postprocess/init.py`.
2. Do not assume `tests/quality/test_unified_quality_matrix.py` exists. The currently visible `tests/quality/` files are:
   - `tests/quality/test_reporter_precision_extra_flags.py`
   - `tests/quality/test_reporter_seed_dual_path_matrix.py`
   Add `test_unified_quality_matrix.py` only if the implementation also adds that test harness.
3. Do not assume `extraction_test_4_20/` is checked in. The branch root currently exposes `my_results.txt` and `my_results_batch_4.txt`; either commit the canonical 20-note batch directory or update verification commands to the checked-in result/input paths.
4. Keep the established quality-pass order intact:
   1. masked text prep / source-aware preprocessing
   2. deterministic uplift
   3. narrative-vs-template reconciliation
   4. precision guardrails / negation cleanup
   5. evidence verification
   6. deterministic CPT derivation
   7. omission scan / RAW-ML audit
5. CPT derivation must depend on structured `RegistryRecord` fields, not raw-note parsing inside `app/coder/domain_rules/registry_to_cpt/coding_rules.py`.
6. Every new suppression or recovery must include suppress/preserve fixtures and targeted tests.
7. New trace output should go under `registry.coding_support.quality_pass.signals`, not ad hoc warning strings only.

---

## 1. Implementation strategy

Use three bisect-friendly PR groups instead of one large change.

### PR 1 — Low-risk precision suppressions and outcome cleanup

Purpose: remove common false positives without changing major data models.

Includes:

- transient-hemostasis complication demotion
- topical TXA / epinephrine therapeutic-injection suppression
- chest-tube-removal hallucination guard in IPC placement language
- indication consent-boilerplate scrub
- partial-success outcome precedence cleanup

Target: raise the 20-note batch to ≥75 / 100 with no new high-impact false positives.

### PR 2 — Coding-sensitive extraction suppression

Purpose: fix 31640 overreach from non-tumor airway material while retaining true mechanical work in the registry.

Includes:

- mechanical-debulking non-tumor classification
- schema/serialization update for the new field
- CPT 31640 suppression when non-tumor material is identified
- preservation of diagnostic bronchoscopy / therapeutic aspiration / foreign-body logic as applicable

Target: remove 31640 false positives for granulation, necrotic inflammatory tissue, mycetoma/fungal material, hair, and foreign-body cases without suppressing true tumor coring/excision.

### PR 3 — Deeper logic rewrites and recall recoveries

Purpose: fix association/scoping errors that require mapper/schema/session-level decisions.

Split this PR further if possible:

- PR 3A: EBUS station/action/ROSE scoping and non-station `target_text`
- PR 3B: airway stent removal-plus-new-placement event representation and CPT session logic
- PR 3C: IPC-with-thoracoscopy and endobronchial-biopsy-in-combined-EBUS recovery, placed before CPT derivation or followed by CPT re-derive

Target: final 20-note batch ≥85 / 100 and FAIL count ≤2.

---

## 2. PR 1 detailed plan — low-risk precision suppressions

### 2.1 Transient-hemostasis complication demotion

**Files:**

- `app/registry/postprocess/complications_reconcile.py`

**Implementation:**

Extend the existing routine-hemostasis framework instead of adding a parallel rule. Demote a bleeding complication when all are true:

- note contains explicit no-complication language such as `COMPLICATIONS: None` or `no immediate complications`
- the relevant bleeding/hemostasis sentence has routine hemostasis intervention language, including:
  - suction
  - wedge / bronchoscope wedged
  - cold saline / iced saline
  - endobronchial epinephrine
  - topical TXA / tranexamic acid
  - direct pressure / compression
- the same local scope has resolution language, including:
  - bleeding resolved / ceased / controlled
  - hemostasis achieved / obtained / confirmed
  - no active bleeding
  - no further bleeding
- no high-grade cue is present in the local scope, including:
  - blocker / Arndt / endobronchial blocker
  - transfusion / PRBC / packed RBC
  - embolization
  - surgery
  - protamine
  - massive/brisk/significant/severe hemorrhage
  - hypotension or aborted-for-bleeding language

**Quality signal:**

- `COMPLICATION_DEMOTED_TRANSIENT_HEMOSTASIS`

**Fixtures:**

- suppress: `tests/fixtures/complications/hemostasis_epi_wedge_none.txt`
- suppress: `tests/fixtures/complications/topical_txa_hemostasis_none.txt`
- preserve: `tests/fixtures/complications/moderate_hemorrhage_blocker.txt`
- preserve: `tests/fixtures/complications/transfusion_for_bleeding.txt`

**Acceptance criteria:**

- Low-grade transient hemostasis with `Complications: None` does not populate formal complication fields.
- Blocker/transfusion/embolization/surgery/protamine/aborted-for-bleeding cases still populate the appropriate bleeding complication severity.

---

### 2.2 Topical TXA / epinephrine is not therapeutic injection

**Files:**

- `app/registry/deterministic_extractors.py`
- optional defense-in-depth check in CPT rule layer if topical hemostasis can still reach structured registry fields

**Implementation:**

In `extract_therapeutic_injection`:

1. Remove `tranexamic acid`, `txa`, and `epinephrine` from broad medication fallback patterns that infer therapeutic injection from drug mention alone.
2. Add a sentence-level exclusion before returning a positive therapeutic-injection object when:
   - medication is TXA / tranexamic acid / epinephrine, and
   - local context contains topical/hemostasis language such as `topical`, `applied`, `instilled for hemostasis`, `for bleeding`, `for hemostasis`, `to the bleeding site`, or `hemostasis achieved`.
3. Do not suppress true intralesional/intratumoral therapeutic injection of eligible non-hemostatic agents.

**Fixtures:**

- suppress: `tests/fixtures/therapeutic_injection/topical_txa_hemostasis.txt`
- suppress: `tests/fixtures/therapeutic_injection/topical_epinephrine_hemostasis.txt`
- preserve: `tests/fixtures/therapeutic_injection/amphotericin_mycetoma_instill.txt`
- preserve: `tests/fixtures/therapeutic_injection/intratumoral_agent_injection.txt`

**Acceptance criteria:**

- Topical TXA/epi hemostasis does not set `therapeutic_injection.performed=true`.
- Amphotericin or other true therapeutic instillation/injection remains eligible when clinically appropriate.

---

### 2.3 Chest-tube-removal hallucination guard in IPC placement language

**Files:**

- `app/registry/deterministic_extractors.py`

**Implementation:**

In `extract_chest_tube_removal`, reject a removal match when the containing sentence or enclosing procedure block contains IPC-placement mechanics without explicit existing-catheter removal.

Suppress if the local scope contains placement mechanics such as:

- introducer
- tunneler
- dilator
- peel-away sheath
- sheath
- guidewire
- catheter pulled through tunnel
- trocar / obturator, if used in placement context

Also suppress if local scope contains IPC-specific vocabulary and no explicit existing-catheter removal:

- `IPC`
- `PleurX`
- `Aspira`
- `tunneled pleural catheter`
- `indwelling pleural catheter`

Add historical/context negators:

- prior
- previous
- outside facility
- historical
- existing catheter noted but not removed

**Fixtures:**

- suppress: `tests/fixtures/pleural/ipc_placement_pulled_tunneler.txt`
- suppress: `tests/fixtures/pleural/ipc_placement_peelaway_sheath.txt`
- suppress: `tests/fixtures/pleural/prior_chest_tube_history.txt`
- preserve: `tests/fixtures/pleural/post_op_day2_ct_removed.txt`
- preserve: `tests/fixtures/pleural/existing_ipc_removed.txt`

**Acceptance criteria:**

- IPC placement text does not set `chest_tube_removal.performed=true`.
- True chest-tube removal remains detected.
- True IPC removal should route to the IPC structure if that field exists, not generic chest-tube removal unless current schema requires it.

---

### 2.4 Indication consent-boilerplate scrub

**Files:**

- `app/registry/deterministic_extractors.py`

**Implementation:**

Extend `extract_primary_indication` cleanup to remove consent and workflow tails from extracted indications. Add split/scrub phrases such as:

- `consent was obtained`
- `consent obtained`
- `consent reviewed`
- `consent signed`
- `risks and benefits`
- `risk of benefits` / typo-tolerant variants if currently present in real data
- `understood and agreed`
- `time-out was performed`
- `timeout was performed`
- `pre-procedure briefing`
- `explanation in lay terms`

Apply the same scrub to `clinical_context.primary_indication` when populated from the same source span.

**Fixtures:**

- suppress: `tests/fixtures/indication/indication_with_consent_tail.txt`
- suppress: `tests/fixtures/indication/indication_with_timeout_tail.txt`
- preserve: `tests/fixtures/indication/indication_clean.txt`
- preserve: `tests/fixtures/indication/risk_benefit_as_clinical_reasoning.txt`

**Acceptance criteria:**

- Extracted indications keep clinical rationale and remove consent/workflow boilerplate.
- Legitimate clinical risk-benefit reasoning is not truncated.

---

### 2.5 Partial-success outcome precedence

**Files:**

- `app/registry/postprocess/__init__.py`

**Implementation:**

In `enrich_procedure_success_status`, make outcome precedence explicit.

Recommended precedence:

1. Strong global abort/failure language wins when the overall intended procedure was stopped.
2. Subcomponent abort does not make the whole case failed if another intended therapeutic/diagnostic goal was completed.
3. Completed-but-limited cases become `Partial success` when the narrative contains:
   - `limited by adhesions`
   - `despite adhesions`
   - `completed the intended/planned procedure`
   - `partial reopen` / `partially reopened`
   - `70% open`, `80% reopened`, or similar percent-reopened language
   - `procedure completed` plus residual stenosis/partial result language
4. Template-level completion must not override a narrative global abort for bleeding, instability, inability to access target, or unsafe anatomy.

**Fixtures:**

- preserve aborted: `tests/fixtures/outcomes/aborted_for_bleeding.txt`
- preserve aborted: `tests/fixtures/outcomes/ipc_aborted_after_thoracoscopy.txt`
- preserve partial success: `tests/fixtures/outcomes/adhesions_partial_success.txt`
- preserve partial success: `tests/fixtures/outcomes/lul_full_lll_70pct.txt`
- preserve mixed outcome: `tests/fixtures/outcomes/biopsy_aborted_bronchoscopy_completed.txt`

**Acceptance criteria:**

- Mixed and partially successful cases are not mislabeled `Failed/Aborted`.
- True global aborted cases remain `Failed/Aborted`.

---

## 3. PR 2 detailed plan — 31640 non-tumor mechanical-debulking guard

### 3.1 Mechanical-debulking non-tumor flag

**Files:**

- `app/registry/deterministic_extractors.py`
- `app/registry/processing/cao_interventions_detail.py`
- `app/registry/schema/granular_models.py` or the relevant current registry model file
- serialization/adapters if the new field is otherwise dropped

**Implementation:**

Add a structured field rather than using only free-text evidence. Preferred naming:

- `mechanical_debulking.cpt31640_eligible: bool | None`, or
- `mechanical_debulking.material_type: Literal["tumor", "granulation", "necrotic_inflammatory", "fungal_material", "hair", "foreign_body", "mucus", "other_non_tumor", "unknown"]`

If minimizing schema change, use:

- `mechanical_debulking.non_tumor: bool | None`

Recommended classification:

- Set `mechanical_debulking.performed=true` when there is actual mechanical action on obstructing material.
- Set `cpt31640_eligible=true` only when there is an explicit tumor anchor in local scope:
  - tumor / tumour
  - neoplasm
  - malignancy / malignant
  - endobronchial tumor
  - endobronchial lesion/mass when clearly treated as tumor
- Set non-tumor / `cpt31640_eligible=false` for:
  - granulation tissue
  - necrotic inflammatory tissue
  - fungal ball / fungal material / mycetoma
  - hair
  - foreign body
  - mucus plug / secretions, if action is aspiration/clearance rather than tumor excision

**Quality signal:**

- `MECH_DEBULK_NON_TUMOR_SUPPRESSED_31640`

**Fixtures:**

- suppress: `tests/fixtures/cao_interventions/granulation_forceps_debulk.txt`
- suppress: `tests/fixtures/cao_interventions/mycetoma_coring.txt`
- suppress: `tests/fixtures/cao_interventions/endobronchial_hair.txt`
- suppress: `tests/fixtures/cao_interventions/necrotic_inflammatory_obstruction.txt`
- suppress: `tests/fixtures/cao_interventions/foreign_body_forceps_removal.txt`
- preserve: `tests/fixtures/cao_interventions/endobronchial_tumor_rigid_coring.txt`
- preserve: `tests/fixtures/cao_interventions/malignant_obstruction_mechanical_debulking.txt`

**Acceptance criteria:**

- Non-tumor mechanical work remains represented in the registry.
- 31640 is suppressed when material is explicitly non-tumor.
- True tumor excision/coring still derives 31640.

---

### 3.2 CPT derivation update for 31640

**Files:**

- `app/coder/domain_rules/registry_to_cpt/coding_rules.py`

**Implementation:**

Update deterministic CPT derivation so 31640 requires structured evidence of tumor-eligible mechanical debulking.

Rules:

1. If `mechanical_debulking.performed=true` and `cpt31640_eligible=true`, allow 31640.
2. If `mechanical_debulking.non_tumor=true` or `cpt31640_eligible=false`, suppress 31640 and emit `MECH_DEBULK_NON_TUMOR_SUPPRESSED_31640`.
3. Do not parse raw note text inside CPT rules. Use only structured registry fields.
4. Preserve other applicable codes based on existing structured fields, such as diagnostic bronchoscopy, therapeutic aspiration, foreign-body logic, or infection/fungal treatment logic if represented elsewhere.

**Coder tests:**

Add or update tests under `tests/coder/` for:

- non-tumor mechanical debridement → no 31640
- tumor mechanical coring → 31640
- non-tumor material plus BAL/aspiration → applicable non-31640 code retained
- tumor debulking plus EBUS/biopsy → existing bundling/modifier behavior unchanged

---

## 4. PR 3A detailed plan — EBUS station scoping, ROSE scoping, and non-station targets

### 4.1 Tighten station/action binding upstream

**Files:**

- `app/registry/ner_mapping/station_extractor.py`
- `app/registry/ner_mapping/entity_to_registry.py`
- `app/registry/postprocess/__init__.py`
- `proc_schemas/shared/ebus_events.py`

**Implementation:**

Do not rely only on postprocess cleanup. Bad station/action associations should be prevented in the extractor and mapper when possible.

Station sampling should require one of:

1. Station token and strong sampling action within ≤80 characters, or
2. Single-station sentence where the only station token is clearly governed by the sampling action, or
3. A clause-level station list explicitly attached to a sampling verb.

Strong sampling actions include:

- sampled
- biopsied
- TBNA
- FNA
- needle aspiration
- passes made
- aspirates obtained
- specimen obtained

Survey/inspection-only language should produce inspected-only / surveyed events, not `stations_sampled`:

- visualized
- surveyed
- inspected
- measured only
- seen
- identified
- no biopsy performed
- not sampled
- not amenable to sampling

### 4.2 Replace broad postprocess short-circuit

**Files:**

- `app/registry/postprocess/__init__.py`

**Implementation:**

In `sanitize_ebus_events`, replace the current broad short-circuit that keeps an event whenever `evidence_quote` contains any strong sampling language.

New rule:

- Keep station sampled only when the station token and strong sampling phrase are station-adjacent within ≤80 characters, or when the sentence has exactly one station token and a clear sampling action.
- Otherwise demote to inspected-only or remove from `stations_sampled` while preserving evidence in node events if appropriate.

**Quality signal:**

- `EBUS_STATION_DEMOTED_SURVEYED_ONLY`

### 4.3 Scope ROSE to the correct station or lesion

**Files:**

- `app/registry/ner_mapping/station_extractor.py`
- `app/registry/postprocess/__init__.py`

**Implementation:**

Add a clause-aware ROSE scoping helper.

Rules:

1. Bind `ROSE`, `on-site cytology`, `rapid onsite`, `adequate for diagnosis`, or `preliminary cytology` to the nearest preceding station/target in the same clause.
2. Treat punctuation boundaries as hard scope limits when appropriate:
   - semicolon
   - period
   - line break
   - station label boundary
   - lesion/airway target boundary
3. Do not propagate a lesion ROSE result to nodal stations.
4. Do not propagate one station's ROSE result to all stations in the sentence unless the text explicitly states that multiple stations had the same ROSE result.

**Quality signal:**

- `AUTO_SCOPED_ROSE_TO_STATION`

### 4.4 Preserve non-station EBUS targets using `target_text`

**Files:**

- `proc_schemas/shared/ebus_events.py`
- `app/registry/ner_mapping/entity_to_registry.py`
- `app/registry/postprocess/__init__.py`
- CPT distinct-target logic if it consumes EBUS targets

**Implementation:**

Use existing `NodeInteraction.target_text` rather than forcing non-station targets into station shape.

Targets to preserve as `target_text` include:

- mediastinal mass
- pulmonary artery mass / PA mass
- transvascular target accessed through pulmonary artery
- station-5-like text only when the note clearly describes a non-nodal/transvascular target rather than true nodal station 5

Important nuance:

- Station 5 is a real nodal station. Do not globally demote `station 5` to non-station. Only route away from station shape when the evidence specifically indicates PA/transvascular/non-nodal target behavior.

Also update hollow-EBUS culling logic:

- If there is no valid nodal sampled station but there is a valid non-station `target_text` sampled under EBUS, do not cull EBUS as hollow.

**Fixtures:**

- `tests/fixtures/ebus/surveyed_4L_sampled_4R.txt`
- `tests/fixtures/ebus/rose_bleed_4R_not_7.txt`
- `tests/fixtures/ebus/station5_transvascular.txt`
- `tests/fixtures/ebus/pa_mass_non_station.txt`
- `tests/fixtures/ebus/mediastinal_mass_non_station.txt`
- `tests/fixtures/ebus/single_station_sampled_preserve.txt`
- `tests/fixtures/ebus/multiple_stations_all_explicitly_sampled.txt`

**Acceptance criteria:**

- Surveyed-only stations are not in `linear_ebus.stations_sampled`.
- Sampled stations remain sampled.
- ROSE binds to the correct station or lesion only.
- Non-station targets land in `target_text`, not station fields.
- EBUS is not culled when non-station target sampling is the valid EBUS action.

---

## 5. PR 3B detailed plan — airway stent removal-plus-new-placement split

### 5.1 Define event representation before coding

**Files:**

- `app/registry/ner_mapping/procedure_extractor.py`
- `app/registry/schema/granular_models.py`
- possible registry schema/adapters if an event list is added
- `app/coder/domain_rules/registry_to_cpt/coding_rules.py`

**Implementation decision required:**

The current single stent action model can flatten compound language such as removal plus new placement into `Revision/Repositioning`. Before changing CPT rules, decide how the registry will represent multiple same-session stent events.

Preferred representation:

```python
airway_stent.events: list[AirwayStentProcedure]
```

Each event should preserve:

- action: `Placement`, `Removal`, `Revision/Repositioning`, `Inspection only`
- old/new status if present
- stent identity / brand / type
- size if present
- location
- evidence span
- whether action was performed vs historical/device-status-only

Maintain a derived legacy aggregate field for backward compatibility if existing UI/tests require it.

### 5.2 Split old-stent removal plus new-stent placement

**Files:**

- `app/registry/ner_mapping/procedure_extractor.py`
- `app/registry/schema/granular_models.py`

**Implementation:**

When a session contains both removal verbs and new-placement verbs, split into two events if the local text references a distinct new stent identity.

Removal cues:

- removed
- extracted
- explanted
- taken out
- prior stent removed

Placement cues:

- new stent placed
- deployed
- inserted
- positioned
- Aero / silicone / Y-stent / covered metal stent plus placement verb
- brand/size after placement verb

Do not split true revision-only cases:

- repositioned
- adjusted
- revised
- migrated stent repositioned
- no new stent identity

### 5.3 CPT session logic for stents

**Files:**

- `app/coder/domain_rules/registry_to_cpt/coding_rules.py`

**Implementation:**

Rules:

1. If same session has `Removal` plus `Placement`, derive the placement family and suppress standalone removal line unless existing bundling rules explicitly require otherwise.
2. Placement family should be based on structured location:
   - tracheal stent placement → 31631
   - bronchial stent placement → 31636
   - additional major bronchus → 31637 if supported by structured event count/location
3. Y-stent / carinal / tracheobronchial stent should not fall through as a simple bronchial-only stent solely because the text lacks the word `trachea`.
4. True revision/repositioning without a new placement verb remains revision/removal-family behavior per existing rules.
5. Do not add raw text parsing to CPT rules; CPT rules consume structured stent event fields.

**Fixtures:**

- `tests/fixtures/stent/remove_old_place_new_y_silicone.txt`
- `tests/fixtures/stent/aero_tracheobronchial_new.txt`
- `tests/fixtures/stent/true_revision_reposition.txt`
- `tests/fixtures/stent/inspection_only_stent_in_good_position.txt`

**Acceptance criteria:**

- Old-stent removal plus new Y-stent placement is not flattened to revision-only.
- New Aero stent placement is preserved as placement.
- True revision remains revision.
- Inspection-only remains not performed for placement.
- CPT family resolves correctly and does not emit an inappropriate standalone 31638 when placement is present.

---

## 6. PR 3C detailed plan — IPC and endobronchial biopsy recoveries

### 6.1 IPC recovery when thoracoscopy is present

**Files:**

- `app/registry/deterministic_extractors.py`
- `app/registry/postprocess/__init__.py`

**Implementation:**

Add a deterministic uplift or pre-CPT recovery step, not a post-CPT-only omission fix.

When `medical_thoracoscopy.performed=true` and raw text contains IPC vocabulary, re-run or call the existing IPC extractor and merge only if the result has true placement evidence.

IPC vocabulary:

- tunneled pleural catheter
- indwelling pleural catheter
- IPC
- PleurX
- Aspira

Require placement/action cues:

- placed
- inserted
- tunneled
- catheter advanced
- peel-away sheath used for catheter placement
- connected/drained after new catheter insertion

Suppress historical/pre-existing cases:

- existing IPC noted
- prior IPC
- catheter left in place
- no catheter placed
- removed previously

**Quality signal:**

- `IPC_RECOVERED_WITH_THORACOSCOPY`

**Fixture:**

- `tests/fixtures/pleural/thoracoscopy_plus_ipc.txt`
- preserve negative: `tests/fixtures/pleural/thoracoscopy_existing_ipc_only.txt`

**Acceptance criteria:**

- Thoracoscopy plus new IPC placement sets IPC placement.
- Thoracoscopy plus historical/pre-existing IPC does not create new IPC placement.
- CPT derivation sees the recovered IPC field.

---

### 6.2 Endobronchial biopsy recovery in combined EBUS plus lesion notes

**Files:**

- `app/registry/postprocess/__init__.py`, but place logic before CPT derivation if possible
- extraction uplift helper if one exists for `endobronchial_biopsy`
- CPT derivation only if structured field is already set before CPT

**Implementation:**

When `linear_ebus.performed=true` and the note contains forceps-biopsy language bound to a lung/airway lesion distinct from a nodal station, set or preserve `endobronchial_biopsy.performed=true`.

Biopsy action cues:

- forceps biopsy
- endobronchial biopsy
- biopsy forceps
- biopsies obtained
- sampled with forceps

Distinct lung/airway lesion anchors:

- RLL / RUL / LLL / LUL
- lingula
- superior segment
- lobar / segmental airway
- endobronchial lesion
- airway lesion
- mass in bronchus / endobronchial mass

Suppress nodal-only cases:

- station 7 TBNA
- 4R FNA
- EBUS needle aspirates only
- lymph-node station biopsy without forceps/lung-lesion anchor

**Quality signal:**

- `ENDOBRONCHIAL_BIOPSY_RECOVERED_COMBINED_CASE`

**Fixture:**

- `tests/fixtures/combined/ebus_plus_rll_forceps_biopsy.txt`
- preserve negative: `tests/fixtures/combined/ebus_only_no_endobronchial_biopsy.txt`

**Acceptance criteria:**

- Distinct endobronchial forceps biopsy is preserved in combined EBUS cases.
- 31625 is retained alongside EBUS when existing distinct-target logic requires it, including modifier behavior if already implemented.
- Nodal-only EBUS cases do not hallucinate endobronchial biopsy.

---

## 7. Test and verification plan

### 7.1 Required unit-level tests

Add targeted tests in the closest existing test area:

- `tests/registry/` for extraction and postprocess behavior
- `tests/coder/` for registry-to-CPT behavior
- `tests/quality/` only if the quality-matrix harness is actually added or exists

Required test categories:

1. suppress/preserve fixtures for every new rule
2. schema serialization for every new field/event list
3. CPT derivation tests for 31640, 31625, 31631, 31636, 31637, 31638, 31652, 31653, 32557 as relevant
4. signal emission tests for all new quality signals
5. negative controls that prevent broad recall rules from reintroducing false positives

### 7.2 Suggested command set

Run after each PR:

```bash
pytest -q tests/registry -k "ebus or stent or chest_tube or ipc or therapeutic_injection or mechanical_debulking or complications or indication or outcomes"
pytest -q tests/coder -k "cpt or 31640 or 31625 or 31631 or 31636 or 31637 or 31638 or 31652 or 31653 or 32557"
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr
python ml/scripts/eval_golden.py --input tests/fixtures/unified_quality_corpus.json --output /tmp/unified_quality_extraction.json
pytest -q tests/quality/test_reporter_precision_extra_flags.py
pytest -q tests/quality/test_reporter_seed_dual_path_matrix.py
```

Only run this if the file is added:

```bash
pytest -q tests/quality/test_unified_quality_matrix.py
```

Nightly/broader regression check after all PRs:

```bash
python ops/tools/run_quality_gates.py --tier nightly --output-dir /tmp/procsuite_quality_nightly
```

### 7.3 Batch-level gates

Use the exact same 20-note batch that produced the 65.4 / 100 baseline.

If `extraction_test_4_20/` is not checked in, add it or document the checked-in equivalent. Current visible candidates are root-level `my_results.txt` and `my_results_batch_4.txt`, but implementation should verify which file is canonical.

Gate targets:

- after PR 1: score ≥75 / 100
- after PR 2: all non-tumor 31640 false positives removed
- after PR 3: score ≥85 / 100 and FAIL count ≤2

### 7.4 Class-specific gates

Use these in addition to total score:

1. zero chest-tube-removal hallucinations from IPC placement sentences
2. zero therapeutic-injection positives from topical TXA/epi hemostasis
3. zero 31640 codes when mechanical material is classified non-tumor
4. no surveyed-only EBUS station appears in `stations_sampled`
5. ROSE result does not leak across station/lesion boundaries
6. valid non-station EBUS targets appear in `target_text`, not fake station fields
7. old-stent removal plus new-stent placement does not collapse to revision-only
8. true global aborted cases remain failed/aborted
9. completed-but-limited therapeutic cases become partial success
10. thoracoscopy plus true IPC placement preserves IPC placement
11. combined EBUS plus distinct endobronchial forceps biopsy preserves 31625 where appropriate

---

## 8. Codex instructions

Use the following instructions for Codex. They are intentionally explicit so the agent does not broaden scope or mix unrelated changes.

### 8.1 General Codex system instructions for all PRs

```text
You are working in the Procedure_suite repo on branch extraction_improvements.

Before editing, read:
- AGENTS.md
- CLAUDE.md
- app/registry/postprocess/__init__.py
- app/registry/postprocess/complications_reconcile.py
- app/registry/deterministic_extractors.py
- app/coder/domain_rules/registry_to_cpt/coding_rules.py
- the closest existing tests under tests/registry, tests/coder, and tests/quality

Do not change the extraction-first quality-pass order:
1. masked text prep / source-aware preprocessing
2. deterministic uplift
3. narrative-vs-template reconciliation
4. precision guardrails / negation cleanup
5. evidence verification
6. deterministic CPT derivation
7. omission scan / RAW-ML audit

Do not add raw-note parsing inside registry-to-CPT rules. CPT rules must consume structured RegistryRecord fields only.

Do not mix broad recall heuristics with suppressions unless the task explicitly says to. Keep each PR bisectable.

For every new rule:
- add suppress and preserve fixtures
- add pytest assertions that load those fixtures or otherwise validate the behavior
- add quality_pass signal emission when the plan names a signal
- add schema/serialization tests if a new field or event representation is added
- keep legacy warnings compatible if existing tests expect them

Prefer extending existing helpers and guardrails over adding duplicate parallel logic.

After changes, run the targeted tests listed in this plan. If a test cannot be run because a file is absent, state that explicitly in the final summary.

Final response must include:
- files changed
- behavior changed
- tests added
- tests run with pass/fail status
- any follow-up risk or intentionally deferred change
```

---

### 8.2 Codex prompt for PR 1 — low-risk suppressions and outcomes

```text
Implement PR 1 from updated_extraction_quality_plan_with_codex.md.

Scope only:
1. transient-hemostasis complication demotion
2. topical TXA / epinephrine suppression in therapeutic injection extraction
3. chest-tube-removal guard for IPC placement mechanics and historical/prior mentions
4. indication consent-boilerplate scrub
5. partial-success outcome precedence cleanup

Files expected:
- app/registry/postprocess/complications_reconcile.py
- app/registry/deterministic_extractors.py
- app/registry/postprocess/__init__.py
- tests/fixtures/... as needed
- tests/registry/... as needed

Do not modify EBUS, stent event modeling, 31640 logic, IPC recovery, or endobronchial-biopsy recovery in this PR.

Signals to add/verify:
- COMPLICATION_DEMOTED_TRANSIENT_HEMOSTASIS

Acceptance checks:
- topical TXA/epi hemostasis does not set therapeutic_injection.performed
- IPC placement mechanics do not set chest_tube_removal.performed
- true chest-tube removal remains positive
- consent/workflow text is removed from indication without truncating clinical risk-benefit reasoning
- partial-success cases are not overcalled as Failed/Aborted
- true global aborted cases remain Failed/Aborted

Run:
pytest -q tests/registry -k "chest_tube or therapeutic_injection or complications or indication or outcomes"
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr
```

---

### 8.3 Codex prompt for PR 2 — non-tumor mechanical debulking and 31640 suppression

```text
Implement PR 2 from updated_extraction_quality_plan_with_codex.md.

Scope only:
- add structured non-tumor or cpt31640_eligible classification for mechanical debulking
- classify granulation, necrotic inflammatory tissue, mycetoma/fungal material, hair, and foreign body as non-tumor material
- suppress CPT 31640 when structured classification says non-tumor
- preserve true tumor mechanical coring/excision as 31640-eligible

Files expected:
- app/registry/deterministic_extractors.py
- app/registry/processing/cao_interventions_detail.py
- relevant registry schema/model file, likely app/registry/schema/granular_models.py
- serialization/adapters if needed so the new field is not dropped
- app/coder/domain_rules/registry_to_cpt/coding_rules.py
- tests/fixtures/cao_interventions/...
- tests/registry/...
- tests/coder/...

Do not add raw text parsing to coding_rules.py. Use structured registry fields only.

Signal to add/verify:
- MECH_DEBULK_NON_TUMOR_SUPPRESSED_31640

Acceptance checks:
- mechanical_debulking.performed can remain true for non-tumor mechanical work
- 31640 is not derived for non-tumor material
- 31640 remains derived for true endobronchial tumor debulking/coring
- schema serialization preserves the new field

Run:
pytest -q tests/registry -k "mechanical_debulking or cao"
pytest -q tests/coder -k "31640 or cpt"
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr
```

---

### 8.4 Codex prompt for PR 3A — EBUS station/ROSE/non-station scoping

```text
Implement PR 3A from updated_extraction_quality_plan_with_codex.md.

Scope only:
- EBUS station/action binding
- surveyed-only vs sampled station correction
- ROSE scoping to nearest station/target in the same clause
- non-station EBUS target preservation using NodeInteraction.target_text
- prevent hollow-EBUS culling when valid non-station target sampling exists

Files expected:
- app/registry/ner_mapping/station_extractor.py
- app/registry/ner_mapping/entity_to_registry.py
- app/registry/postprocess/__init__.py
- proc_schemas/shared/ebus_events.py only if needed for serialization compatibility
- tests/fixtures/ebus/...
- tests/registry/...
- tests/coder/... if CPT distinct-target behavior changes

Do not modify stent logic or 31640 logic in this PR.

Signals to add/verify:
- EBUS_STATION_DEMOTED_SURVEYED_ONLY
- AUTO_SCOPED_ROSE_TO_STATION

Acceptance checks:
- surveyed stations are not in linear_ebus.stations_sampled
- sampled stations remain sampled
- ROSE does not leak across station/lesion boundaries
- mediastinal mass and PA mass targets land in target_text, not fake station fields
- station 5 is preserved as a nodal station unless evidence specifically describes transvascular/non-nodal target behavior
- EBUS is not culled when non-station target_text is valid sampled EBUS evidence

Run:
pytest -q tests/registry -k "ebus or rose or station"
pytest -q tests/coder -k "31652 or 31653 or ebus"
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr
```

---

### 8.5 Codex prompt for PR 3B — airway stent event split and CPT session logic

```text
Implement PR 3B from updated_extraction_quality_plan_with_codex.md.

Scope only:
- represent same-session stent removal plus distinct new stent placement without flattening to revision-only
- preserve true revision/repositioning behavior
- update CPT session logic so same-session Removal + Placement emits placement family and suppresses inappropriate standalone removal/revision line per existing bundling behavior

Before editing coding rules, decide and implement a structured event representation that can store multiple stent events. Prefer airway_stent.events: list[AirwayStentProcedure] with legacy aggregate compatibility if needed.

Files expected:
- app/registry/ner_mapping/procedure_extractor.py
- app/registry/schema/granular_models.py
- serialization/adapters if the event list would otherwise be dropped
- app/coder/domain_rules/registry_to_cpt/coding_rules.py
- tests/fixtures/stent/...
- tests/registry/...
- tests/coder/...

Do not implement EBUS changes, IPC recovery, or endobronchial-biopsy recovery in this PR.

Acceptance checks:
- remove old + place new Y-stent produces separate removal and placement events or equivalent structured representation
- new Aero stent placement is placement, not revision-only
- true revision/reposition remains revision
- inspection-only stent in good position remains not placement
- CPT chooses correct placement family: 31631 / 31636 / 31637 as applicable
- standalone 31638 is not emitted when placement is the primary same-session event unless existing rules explicitly require it

Run:
pytest -q tests/registry -k "stent"
pytest -q tests/coder -k "31631 or 31636 or 31637 or 31638 or stent"
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr
```

---

### 8.6 Codex prompt for PR 3C — IPC and endobronchial biopsy recovery

```text
Implement PR 3C from updated_extraction_quality_plan_with_codex.md.

Scope only:
1. recover true IPC placement when medical thoracoscopy is also present
2. recover true endobronchial forceps biopsy in combined EBUS plus distinct lung/airway lesion notes

Important ordering requirement:
The recovered structured fields must exist before deterministic CPT derivation, or the code must explicitly re-run deterministic CPT derivation after recovery. Prefer pre-CPT deterministic uplift/recovery.

Files expected:
- app/registry/deterministic_extractors.py
- app/registry/postprocess/__init__.py
- tests/fixtures/pleural/...
- tests/fixtures/combined/...
- tests/registry/...
- tests/coder/... for 31625 and IPC/pleural CPT behavior if affected

Signals to add/verify:
- IPC_RECOVERED_WITH_THORACOSCOPY
- ENDOBRONCHIAL_BIOPSY_RECOVERED_COMBINED_CASE

Acceptance checks:
- thoracoscopy plus true new IPC placement sets IPC placement
- thoracoscopy plus historical/pre-existing IPC only does not set new IPC placement
- EBUS plus distinct RLL/RUL/LLL/LUL/segmental/endobronchial forceps biopsy sets endobronchial_biopsy.performed
- nodal-only EBUS does not hallucinate endobronchial biopsy
- 31625 is retained when the endobronchial biopsy is distinct and current modifier logic requires it

Run:
pytest -q tests/registry -k "ipc or thoracoscopy or endobronchial_biopsy or ebus"
pytest -q tests/coder -k "31625 or 32557 or ipc or pleural"
python ops/tools/run_quality_gates.py --tier pr --output-dir /tmp/procsuite_quality_pr
```

---

## 9. Reviewer checklist after Codex implementation

Use this checklist before merging each PR.

### PR 1 checklist

- [ ] No `app/registry/postprocess/init.py` references remain.
- [ ] Topical TXA/epi cases are suppressed for therapeutic injection.
- [ ] True therapeutic injections still extract.
- [ ] IPC placement mechanics do not create chest-tube-removal positives.
- [ ] True chest-tube removals still extract.
- [ ] Indication scrub preserves clinical rationale.
- [ ] Partial success and global aborted outcomes follow precedence.
- [ ] `COMPLICATION_DEMOTED_TRANSIENT_HEMOSTASIS` fires only in appropriate cases.

### PR 2 checklist

- [ ] New mechanical-debulking field survives schema validation and serialization.
- [ ] 31640 depends on structured tumor eligibility.
- [ ] No raw note parsing was added to CPT derivation.
- [ ] Non-tumor material suppresses 31640.
- [ ] True tumor debulking preserves 31640.
- [ ] `MECH_DEBULK_NON_TUMOR_SUPPRESSED_31640` fires appropriately.

### PR 3A checklist

- [ ] Station sampling requires station-adjacent action evidence.
- [ ] Surveyed-only stations are demoted/removed from `stations_sampled`.
- [ ] ROSE is clause-scoped.
- [ ] Non-station targets use `target_text`.
- [ ] Station 5 nodal cases are not accidentally demoted.
- [ ] Hollow-EBUS culling preserves non-station sampled targets.

### PR 3B checklist

- [ ] Multiple same-session stent events can be represented.
- [ ] Removal plus new placement is not flattened to revision-only.
- [ ] True revision remains revision.
- [ ] Y-stent/tracheobronchial placement maps to the intended CPT family.
- [ ] No inappropriate standalone 31638 when placement is present.

### PR 3C checklist

- [ ] IPC recovery happens before CPT derivation or CPT is explicitly re-derived.
- [ ] Historical/pre-existing IPC mentions are suppressed.
- [ ] Distinct endobronchial biopsy in combined EBUS cases is recovered.
- [ ] Nodal-only EBUS does not trigger endobronchial biopsy.
- [ ] 31625 is retained when structured biopsy evidence supports it.

---

## 10. Final acceptance target

After all PRs merge:

1. Re-run the exact 20-note batch that produced the 65.4 / 100 baseline.
2. Confirm score ≥85 / 100 and FAIL count ≤2.
3. Confirm class-specific gates all pass.
4. Run PR-tier quality gates.
5. Run nightly quality gates before release or broader rollout.
6. Inspect machine-readable JSON gate artifacts, not just pytest pass/fail output.
