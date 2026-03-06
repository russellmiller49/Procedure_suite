# Extraction Quality Report

Evaluated **30 notes** across **2 batch-output files**.

Overall average score: **73.8 / 100**
Status counts: **6 PASS**, **11 WARNING**, **13 FAIL**.

## Cross-file patterns

- Most serious failures were **action-type errors**, especially **sampled vs inspected_only** for EBUS node events.
- The next most common issue was **procedure family confusion**, especially **BAL vs washings** and **endobronchial biopsy vs transbronchial biopsy**.
- Several notes **overcalled complications**, usually converting minor intraprocedural bleeding/oozing or hemostatic maneuvers into formal complications despite `Complications: None` in the note.
- Billing errors usually followed extraction errors: wrong node action counts caused **31652 vs 31653** mistakes; false procedure families generated false CPTs such as **31625**, **31636**, or unsupported elastography add-ons.

## my_results.txt

### note_002 — ❌ FAIL — 62 / 100

**Accuracy (Precision)**
- Hallucination: Complications block overcalls moderate bleeding despite Complications: None in the note.
- Mismatch: EBUS node_events mark station 7 and 4L as inspected_only even though both were sampled via TBNA.
- Mismatch: Because only one node event is treated as sampled, billing is downcoded to 31652 instead of 31653.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Station 7 pass count is missing from granular detail.

**Logic & Coding**
- CPT consistency: 31623/31624/31625 are supported. EBUS should derive 31653, not 31652, because 11L, 7, and 4L were all sampled.
- Schema / structure: This is a classic sampled-vs-inspected logic failure.

### note_009 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies endobronchial tumor despite the note stating no endobronchial tumor.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Granular EBUS detail misses the 5 passes at station 7.

**Logic & Coding**
- CPT consistency: 31653 is correct for sampling 4R, 7, and 10R.
- Schema / structure: Core staging logic is good; false-positive lesion text is the main precision issue.

### note_010 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Counts (TBNA x3, forceps x6, brushing x1) are not deeply structured, but the performed procedures and target are correct.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31629/+31654 are coherent with the note.
- Schema / structure: Good separation of navigation, radial EBUS, TBNA, TBBx, brushings, and BAL.

### note_011 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucination: Inspection findings falsely imply an endobronchial lesion; note explicitly says no endobronchial lesion.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Bronchial washings from RLL are not represented as a separate specimen/procedure concept.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31645 is supported.
- Schema / structure: Therapeutic aspiration is correct, but washings are omitted.

### note_012 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucination: CPT 31640 (tumor excision) is not supported; the note describes granulation tissue debridement, not tumor excision.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Cryotherapy application count (2 applications) is not preserved.

**Logic & Coding**
- CPT consistency: 31638 is supported for stent repositioning/revision. 31645 is arguable from stent lumen toileting/suctioning. 31640 is not supported as documented.
- Schema / structure: Procedure families are mostly correct, but coding logic treats granulation tissue as tumor.

### note_018 — ❌ FAIL — 72 / 100

**Accuracy (Precision)**
- Hallucination: endobronchial_biopsy.performed=true and CPT 31625 are not supported; the note documents forceps biopsies of a peripheral RML target, i.e., transbronchial biopsy, not endobronchial biopsy.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Brush count, TBNA count, and forceps biopsy count are not preserved in structured fields.

**Logic & Coding**
- CPT consistency: 31623/31627/31628/31629/+31654 are supported. 31625 is not. 77012 is a gray-zone billing inference from CBCT mention rather than a clearly documented procedural code.
- Schema / structure: Major procedure family mostly correct, but biopsy type classification is wrong.

### note_019 — ⚠️ WARNING — 77 / 100

**Accuracy (Precision)**
- Hallucination: Inspection findings imply an endobronchial lesion despite the note stating no endobronchial lesion.
- Hallucination: Extra elastography add-on coding (76983) is not clearly supported; only a single target/station is described as having elastography findings.
- Mismatch: Pass counts are misassigned/incomplete in granular EBUS detail (station 7 should have 6 passes; station 11R should have 4).

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31624/31625/31652 are supported. 76982 may be supportable for one elastography target; +76983 is not clearly supported.
- Schema / structure: Good overall recall, but imaging adjunct coding and pass quantitation are shaky.

### note_021 — ❌ FAIL — 72 / 100

**Accuracy (Precision)**
- Hallucination: foreign_body_removal.performed=true is not supported; this is airway stent removal, not foreign body removal.
- Hallucination: Complications block creates a mild bleeding complication even though the note says Complications: None and only mentions minor oozing resolved with suction.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Residual stenosis caliber (~11–12 mm) and post-removal patency are not preserved in structured airway outcome fields.

**Logic & Coding**
- CPT consistency: 31638 is consistent with stent removal/revision-style work on an existing stent.
- Schema / structure: Stent removal is recognized, but an unrelated foreign-body family is spuriously turned on.

### note_022 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings says 'endobronchial tumor' even though the note says airway inspection normal and no endobronchial tumor.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Granular station detail omits station 7 pass metadata.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations.
- Schema / structure: Major extraction is correct; narrative polarity error remains.

### note_025 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Hallucination: Inspection findings falsely imply an endobronchial lesion although the note says no endobronchial lesion.
- Mismatch: linear_ebus.stations_sampled omits station 7 even though 4R, 7, and 11R were all sampled.
- Mismatch: node_events mark station 7 and 11R as inspected_only despite documented TBNA sampling.

**Completeness (Recall)**
- Missed procedure: Transbronchial biopsy/forceps biopsies of the RUL target are missed.
- Missed detail: Granular EBUS detail captures only 4R and 11R, omitting station 7.

**Logic & Coding**
- CPT consistency: 31627/31629/+31654 are supported. EBUS should derive 31653, not 31652, because 3 nodal stations were sampled.
- Schema / structure: Combined peripheral+mediastinal case is not cleanly separated; major recall and logic issues.

### note_026 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Hallucination: Inspection findings falsely imply an endobronchial lesion/mass despite the note stating no endobronchial lesion.
- Mismatch: Granular pass counts are swapped/incomplete: station 7 should have 6 passes and 11L should have 3, but the detail table assigns 6 to 11L and omits 7 pass count.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (7, 4L, 11L).
- Schema / structure: High-level EBUS extraction is right, but quantitative details are unreliable.

### note_027 — ⚠️ WARNING — 88 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Bronchial washings are documented but not represented.
- Missed detail: RLL lateral basal BAL location and washings could be more explicit in structured fields.

**Logic & Coding**
- CPT consistency: 31624 and 31645 are supported; washings are absent from extraction but do not invalidate the main coding stack.
- Schema / structure: Good core extraction with partial recall loss for washings.

### note_028 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucination: endobronchial_biopsy/31625 are not supported; the note documents peripheral forceps biopsies.
- Hallucination: Complications block overcalls moderate bleeding, though the note describes mild bleeding controlled with wedge positioning and cold saline and says Complications: None.
- Mismatch: clinical_context.bronchus_sign='Not assessed' conflicts with the note, which explicitly says the nodule had a bronchus sign.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Target segment is posterior basal LLL, but target granularity is only partially preserved.

**Logic & Coding**
- CPT consistency: 31627/31628/31629/+31654 are consistent. 31625 is not supported.
- Schema / structure: Biopsy family and complication severity are both wrong.

### note_035 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucination: BAL/performed=true and CPT 31624 are not supported; note describes therapeutic aspiration with saline lavage plus washings, not bronchoalveolar lavage.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Bronchial washings / bronchial wash specimen not represented.
- Missed detail: Moderate sedation present in note but not surfaced in the concise registry section used for key procedure interpretation.

**Logic & Coding**
- CPT consistency: 31645 is supported. 31624 is not supported by the note.
- Schema / structure: Core therapeutic aspiration event is present, but registry confuses lavage language with BAL.

### note_036 — ❌ FAIL — 48 / 100

**Accuracy (Precision)**
- Hallucination: airway_stent.action_type='placement' and CPT 31636 are not supported; this was surveillance/toileting of an existing tracheal stent, not new placement.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Mechanical debridement of granulation tissue is described in the note but not extracted as its own therapeutic event.
- Missed detail: Existing stent type/location are only partially represented; suction/toileting is flattened into secretions without a clear toileting event.

**Logic & Coding**
- CPT consistency: 31641 is defensible for APC treatment of granulation/stenosis. 31636 is not supported.
- Schema / structure: Existing-stent management is collapsed into a false placement event.

### note_037 — ✅ PASS — 96 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could additionally capture laterality and immediate cloudy drainage, but this is minor.

**Logic & Coding**
- CPT consistency: 32557 and 32561 are consistent with US-guided 14 Fr pigtail placement plus first-day intrapleural fibrinolytic instillation.
- Schema / structure: Good separation of chest tube placement and fibrinolytic therapy.

### note_038 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion even though the note explicitly says no endobronchial lesion.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Granular station detail omits station 7 pass count (6 passes) despite 3 sampled stations being present.

**Logic & Coding**
- CPT consistency: 31653 is consistent with 3 sampled stations (4R, 7, 10R).
- Schema / structure: Node actions are separated correctly, but inspection narrative polarity is wrong.

### note_039 — ❌ FAIL — 74 / 100

**Accuracy (Precision)**
- Hallucination: Complications block overcalls moderate bleeding/Nashville grade 2, while the note says no complications and specifically says cryobiopsy was retrieved without significant bleeding.
- Mismatch: BAL location is malformed ('RLL (').

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Cryobiopsy probe size (1.1 mm) and BAL volumes (150 mL in / 62 mL out) are incompletely captured in the top-level structured fields.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/+31654 are consistent with BAL + navigation + transbronchial cryobiopsy + radial EBUS.
- Schema / structure: Complication extraction is the main failure.

### note_040 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucination: therapeutic_aspiration.performed=true is an overcall from incidental suctioning of thick secretions in a combined BAL + EBUS case.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could capture that both station 7 and 4R had 4 passes.

**Logic & Coding**
- CPT consistency: 31624 and 31652 are consistent with BAL plus 2-station EBUS sampling.
- Schema / structure: Overall extraction is usable; therapeutic aspiration flag is too aggressive.

### note_047 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucination: Complications block says bleeding occurred (Nashville grade 2 / moderate) even though the note says Complications: None and only mentions minor oozing controlled with cold saline.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31645 is supported for clot extraction / airway clearance.
- Schema / structure: Complication severity is materially overstated.

## my_results_2.txt

### note_001 — ❌ FAIL — 56 / 100

**Accuracy (Precision)**
- Hallucination: clinical_context.asa_class=3 is not supported by 'MONITORING: Standard ASA'.
- Hallucination: Node events mark every station as inspected_only, including 7 and 4R, even though those two were actually sampled.
- Mismatch: Because sampled actions are not represented, the case fails to derive CPT 31652 even though 7 and 4R were sampled.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: ROSE is only partially represented and pass counts (7 x4, 4R x3) are not fully carried through.

**Logic & Coding**
- CPT consistency: Should derive 31652 for two sampled stations (7 and 4R).
- Schema / structure: Internal inconsistency between stations_sampled/granular detail and node_events.

### note_002 — ❌ FAIL — 38 / 100

**Accuracy (Precision)**
- Hallucination: Station 11R is falsely treated as sampled; the note corrects itself to 11L sampled, with station 7 also sampled.
- Mismatch: CPT is upcoded to 31653 even though only 2 stations (11L and 7) were sampled, so the correct nodal EBUS code would be 31652.
- Mismatch: Evidence quotes for node events are taken from the specimen list rather than the actual procedural sampling sentences.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Follow-up/outcome text is mangled ('Patient <PERSON> well').

**Logic & Coding**
- CPT consistency: Should be 31652, not 31653.
- Schema / structure: This is a high-severity laterality/target hallucination.

### note_003 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Sedation is undocumented in the note and appropriately left blank.

**Logic & Coding**
- CPT consistency: 31652 is correct for single-station EBUS-TBNA of 4R.
- Schema / structure: Accurate extraction for an ultra-short note.

### note_004 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies a mass even though the airway exam only reported mildly edematous mucosa and no mass.
- Mismatch: Sedation/anesthesia is missing despite explicit General anesthesia in the note.
- Mismatch: Granular pass counts are partly wrong/incomplete: station 7 should have 4 passes and 11R should have 3, but the detail table omits 7 passes and assigns 4 to 11R.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: TBLB location RB3 is not preserved.

**Logic & Coding**
- CPT consistency: 31628/31653/+31654 are supported.
- Schema / structure: High-level procedure families are right; quantitative granularity is off.

### note_005 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: linear_ebus.node_events labels station 4L as inspected_only even though the note clearly documents EBUS-TBNA/FNA with 3 passes and a 22g needle.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Moderate sedation is not captured.
- Missed detail: Derived CPT 31652 is missing despite one sampled nodal station.

**Logic & Coding**
- CPT consistency: Should derive 31652 from a single sampled station (4L).
- Schema / structure: Granular station detail says sampled=true while node_events say inspected_only; internal contradiction.

### note_006 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Pass count (x4) is not preserved in granular detail.
- Missed detail: Sedation documentation is conflicting in the note; choosing General is a reasonable interpretation because an explicit anesthesia line is present.

**Logic & Coding**
- CPT consistency: 31652 is correct for one sampled station.
- Schema / structure: Good extraction despite conflicting sedation text.

### note_007 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Sedation/agent details are not structured despite propofol being mentioned; however, the noisy dose correction was not hallucinated into the registry, which is appropriate.

**Logic & Coding**
- CPT consistency: 31652 is correct for two sampled stations (4R and 10R).
- Schema / structure: Good handling of noisy text.

### note_008 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy may be inferred more strongly than documented; the text explicitly says Linear EBUS inserted and does not separately describe a flexible airway survey.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Pass count (4) is not propagated into granular detail.

**Logic & Coding**
- CPT consistency: 31652 is correct for a single sampled station 7.
- Schema / structure: Otherwise coherent single-station EBUS extraction.

### note_009 — ❌ FAIL — 30 / 100

**Accuracy (Precision)**
- Hallucination: linear_ebus with CPT 31652 is not supported as a nodal staging event; the note describes TBNA of a mass, not a nodal station sample.
- Mismatch: The note is internally laterality-conflicted ('left upper lobe mass' vs 'RUL mass'), but the JSON resolves this into an invalid EBUS nodal construct rather than preserving ambiguity on a peripheral target.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Should preserve the target as an ambiguous peripheral lung mass TBNA rather than a station-based EBUS node event.

**Logic & Coding**
- CPT consistency: 31652 is not supported by the documented text.
- Schema / structure: Peripheral target and nodal EBUS schemas are conflated.

### note_010 — ✅ PASS — 91 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: BAL location is overly vague ('the segment') instead of RLL superior segment / RB6.
- Mismatch: Radial EBUS is simplified to concentric, whereas the note says eccentric then adjusted to concentric.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Counts for TBNA x3 and TBBx x4 are not deeply structured.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/31629/+31654 are coherent with the documented robotic peripheral bronchoscopy.
- Schema / structure: Strong overall extraction.
