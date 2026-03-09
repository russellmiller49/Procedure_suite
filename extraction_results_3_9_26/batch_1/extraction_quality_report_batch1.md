# Extraction Quality Report

Evaluated **50 notes** from **my_results_batch_1.txt**.

Overall average score: **83.3 / 100**
Status counts: **21 PASS**, **19 WARNING**, **10 FAIL**.

## Cross-file patterns

- Most consequential logic errors were EBUS sampled-versus-inspected_only mistakes, which downcoded 3-station cases to 31652 in notes 001, 002, and 025.
- Several airway cases still need coder review around same-site bundling or family selection for dilation/debulking/stent management (notes 012, 015, 024, 036, 048).
- Complication overcalls remain a real failure mode: routine cold-saline/wedging hemostasis was converted into formal bleeding complications in notes 004 and 039 despite 'Complications: None'.
- Lobe leakage into biopsy logic caused unsupported +31632 add-on coding in notes 013 and 044.
- Navigation/fiducial cases are partly improved, but note 045 still misses 31626 entirely and note 014 stores fiducials only in granular_data rather than a clean performed-procedure object.
- A softer but frequent precision issue is false-positive inspection narrative text implying an endobronchial lesion/mass when the note explicitly says no lesion.

## note_041 — ✅ PASS — 97 / 100
**Note title:** Therapeutic bronchoscopy — balloon dilation

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: The 10 mm then 12 mm balloon sequence and pre-dilation lumen (7–8 mm) are not deeply structured.

**Logic & Coding**
- CPT consistency: 31630 is supported for balloon dilation of tracheal stenosis.
- Schema / structure: Accurate extraction for a simple therapeutic airway dilation case.

## note_031 — ✅ PASS — 97 / 100
**Note title:** Pleural ultrasound + thoracentesis (brief)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: 850 mL volume removed and left laterality are not strongly surfaced in top-level pleural fields.

**Logic & Coding**
- CPT consistency: 32555 is correct for ultrasound-guided thoracentesis.
- Schema / structure: Accurate extraction for a simple pleural drainage note.

## note_049 — ✅ PASS — 97 / 100
**Note title:** Pleural: Diagnostic thoracentesis (ultra short)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Removed volume and left laterality could be more explicit.

**Logic & Coding**
- CPT consistency: 32555 is correct for ultrasound-guided thoracentesis.
- Schema / structure: Accurate extraction for an ultra-short pleural note.

## note_019 — ⚠️ WARNING — 85 / 100
**Note title:** Bronchoscopy + EBUS with elastography mention

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: EBUS node-event evidence quotes are pulled from the specimen list region rather than the procedural sampling lines.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Elastography is captured, but the specific station-level association is not strongly modeled beyond a boolean/use flag.

**Logic & Coding**
- CPT consistency: 31624/31625/31652 are supported. 76982 may be supportable for one elastography target, but it remains a coder-review item.
- Schema / structure: Good overall recall with some evidence-localization and adjunct-coding shakiness.

## note_012 — ⚠️ WARNING — 78 / 100
**Note title:** Airway stent surveillance and clearance

**Accuracy (Precision)**
- Hallucination: CPT 31640 is not supported; the note describes granulation tissue debridement/cryotherapy in an existing stent, not tumor excision.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Cryotherapy application count (2 applications) is not preserved.
- Missed detail: Granulation tissue location at the proximal stent edge is only partially structured.

**Logic & Coding**
- CPT consistency: 31638 and 31645 are supported. 31640 is not supported as documented.
- Schema / structure: Stent management is recognized, but coding mislabels granulation treatment as tumor excision.

## note_002 — ❌ FAIL — 64 / 100
**Note title:** Indication: Hemoptysis and left upper lobe mass on CT in a 58-year-old female.

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: EBUS node_events mark station 7 and 4L as inspected_only despite documented TBNA sampling.
- Mismatch: Downstream CPT logic selects 31652 instead of 31653 even though 11L, 7, and 4L were all sampled.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31623/31624/31625 are supported. EBUS should derive 31653, not 31652.
- Schema / structure: High-level bronchoscopy content is correct, but nodal action logic is materially wrong.

## note_006 — ✅ PASS — 92 / 100
**Note title:** CPT/ICD + HEADINGS TEMPLATE

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Tumor obstruction pre/post patency and balloon sequence are not deeply structured.

**Logic & Coding**
- CPT consistency: 31640 and 31645 are defensible under the local bundling logic that suppresses separate 31641/31630 at the same site.
- Schema / structure: Good capture of rigid bronchoscopy, debulking, adjunct APC, dilation, and airway clearance.

## note_028 — ✅ PASS — 92 / 100
**Note title:** PROCEDURE NOTE — Peripheral bronchoscopy (robotic)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Bronchus sign and minor bleeding-control details are not deeply structured.

**Logic & Coding**
- CPT consistency: 31627/31628/31629/+31654 are coherent with the note.
- Schema / structure: Good core extraction for a straightforward robotic peripheral case.

## note_047 — ✅ PASS — 95 / 100
**Note title:** Therapeutic bronchoscopy — clot extraction

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Minor oozing treated with cold saline could be represented as routine hemostatic maneuver, but it is appropriately not escalated to a complication.

**Logic & Coding**
- CPT consistency: 31645 is supported for clot extraction/airway clearance.
- Schema / structure: Accurate therapeutic aspiration extraction.

## note_001 — ❌ FAIL — 60 / 100
**Note title:** PRE-PROCEDURE DIAGNOSIS: Mediastinal adenopathy; pulmonary nodule (R91.1, R59.0)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: EBUS node_events mark station 7 and 11L as inspected_only even though both were sampled via TBNA.
- Mismatch: Because only one node_event is treated as sampled, nodal coding is downcoded to 31652 instead of 31653.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: The note’s explicit 'No endobronchial lesion' is flattened into secretions-only inspection findings.

**Logic & Coding**
- CPT consistency: 31624 is supported. EBUS should derive 31653, not 31652, because 4R, 7, and 11L were all sampled.
- Schema / structure: Classic sampled-versus-inspected_only logic failure.

## note_017 — ✅ PASS — 95 / 100
**Note title:** Pleural procedure: Small-bore chest tube placement

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Left laterality and immediate cloudy drainage could be surfaced more explicitly.

**Logic & Coding**
- CPT consistency: 32557 is correct for ultrasound-guided 14 Fr pigtail placement.
- Schema / structure: Pleural drainage extraction is accurate.

## note_023 — ⚠️ WARNING — 86 / 100
**Note title:** Navigational bronchoscopy — mixed sampling strategy

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.airway_abnormalities includes an endobronchial-lesion concept that is not supported by the note.
- Mismatch: BAL location is malformed ('LUL with').

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: TBNA and forceps-biopsy counts are not deeply structured.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/31629/+31654 are supported.
- Schema / structure: Good core navigation case extraction with modest precision loss in airway narrative/location text.

## note_004 — ❌ FAIL — 66 / 100
**Note title:** PROCEDURE NOTE (COMPLEX)

**Accuracy (Precision)**
- Hallucination: Complications are overstated as moderate bleeding despite 'Complications: None' and only routine wedge/cold-saline hemostasis in the note.
- Hallucination: An endobronchial_biopsy object appears even though the note documents peripheral forceps biopsy and cryobiopsy, not endobronchial biopsy.
- Mismatch: Peripheral sampling detail is internally scrambled: TBNA/forceps/cryobiopsy locations and counts are misassigned.
- Mismatch: Cryobiopsy and forceps biopsy sample counts are inverted in structured fields.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: RLL superior-segment target granularity is poorly preserved.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/31629/31652/+31654 are supported, but the complication layer is not.
- Schema / structure: Major quantitative and complication-layer errors reduce trustworthiness.

## note_011 — ✅ PASS — 94 / 100
**Note title:** THERAPEUTIC BRONCHOSCOPY

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Washings are represented without much specimen-detail granularity.

**Logic & Coding**
- CPT consistency: 31645 is supported; washings are documented and represented separately.
- Schema / structure: Good extraction for therapeutic aspiration with associated washings.

## note_043 — ✅ PASS — 95 / 100
**Note title:** Pleuroscopy with biopsy ± talc pleurodesis (narrative)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Right laterality, 900 mL aspirated fluid, and pleural-studding findings could be more explicit.

**Logic & Coding**
- CPT consistency: 32650 is consistent with medical pleuroscopy with talc pleurodesis; chest tube placement is bundled into the thoracoscopic work.
- Schema / structure: Good separation of thoracoscopy, pleurodesis, and adjunct chest-tube placement.

## note_015 — ⚠️ WARNING — 86 / 100
**Note title:** THERAPEUTIC BRONCHOSCOPY — COMBINED

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Electrocautery radial incision count (3) and stenosis length (~1.5 cm) are not preserved.

**Logic & Coding**
- CPT consistency: 31641 is supported. The note also documents balloon dilation, but the pipeline drops 31630 under a same-site bundling rule; that deserves coder review rather than outright rejection.
- Schema / structure: Thermal treatment and dilation are both extracted; the question is coding completeness, not family confusion.

## note_045 — ❌ FAIL — 52 / 100
**Note title:** Peripheral bronchoscopy — fiducial placement only (short)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Navigation target is stored as 'Unknown target' despite explicit LLL lesion targeting.

**Completeness (Recall)**
- Missed procedure: Fiducial marker placement is not surfaced in billing even though the note clearly documents fiducial placement x4 and granular_data marks fiducials placed.
- Missed detail: Fiducial count (x4) and lesion location are not preserved in a clinician-friendly procedure object.

**Logic & Coding**
- CPT consistency: 31626 is supported by the note and appears to be missing from the selected CPT output.
- Schema / structure: This fiducial-only navigation case is undercoded and under-modeled.

## note_048 — ⚠️ WARNING — 88 / 100
**Note title:** Airway stent repositioning + balloon dilation

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Granulation tissue debridement and in-stent balloon sequence are not richly structured.

**Logic & Coding**
- CPT consistency: 31638 is consistent with stent revision/repositioning; separate dilation coding is not clearly required in this context.
- Schema / structure: Core stent-revision extraction is correct with only partial therapeutic-detail recall.

## note_033 — ✅ PASS — 95 / 100
**Note title:** Bronchoscopy with endobronchial biopsy + BAL

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Biopsy count, brushing count, and BAL location could be made more explicit.

**Logic & Coding**
- CPT consistency: 31623/31624/31625 are all supported.
- Schema / structure: Good extraction for endobronchial biopsy + brushing + BAL.

## note_039 — ❌ FAIL — 72 / 100
**Note title:** Peripheral bronchoscopy — cryobiopsy included

**Accuracy (Precision)**
- Hallucination: Complications are overstated as moderate bleeding/Nashville grade 2 even though the note says 'Complications: None' and specifically says cryobiopsy was retrieved without significant bleeding.
- Mismatch: BAL location is malformed ('RLL (').

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Cryobiopsy probe size (1.1 mm) and BAL volumes (150 mL in / 62 mL out) are not well surfaced in top-level fields.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/+31654 are consistent with the note.
- Schema / structure: Complication extraction is the main failure.

## note_005 — ⚠️ WARNING — 90 / 100
**Note title:** Flexible bronchoscopy with therapeutic aspiration and BAL

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: bronchial_wash.location is wrong; the note says additional washings were obtained from the LLL basilar segments, not the RML.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31624 and 31645 are supported. Separate washings are also supported conceptually.
- Schema / structure: Core aspiration + BAL + washings families are correct; one location field is wrong.

## note_024 — ⚠️ WARNING — 82 / 100
**Note title:** THERAPEUTIC BRONCHOSCOPY — OBSTRUCTION

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Diagnostic bronchoscopy narrative underemphasizes the malignant LMS obstruction and overfocuses on secretions.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Pre/post patency (~70% restored) and left mainstem target detail could be more explicit.

**Logic & Coding**
- CPT consistency: 31640 and 31645 are supported. Balloon dilation is also documented, but 31630 is dropped by the local same-site bundling rule and should be coder-reviewed.
- Schema / structure: High-level therapeutic families are correct; coding completeness is the open issue.

## note_044 — ❌ FAIL — 58 / 100
**Note title:** Bronchoscopy with transbronchial biopsy (ICD/CPT style lines)

**Accuracy (Precision)**
- Hallucination: +31632 is not supported; the note documents transbronchial biopsies only in the RLL.
- Mismatch: transbronchial_biopsy.locations incorrectly include RML because BAL location leaked into biopsy-lobe logic.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Biopsy count (6) and fluoroscopic guidance are not cleanly preserved.

**Logic & Coding**
- CPT consistency: 31624 and 31628 are supported. +31632 is not.
- Schema / structure: A lobe-attribution error cascades into unsupported add-on coding.

## note_009 — ⚠️ WARNING — 86 / 100
**Note title:** Bronchoscopy + EBUS staging (minimal headings)

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies endobronchial tumor even though the note says bronchoscopy showed no endobronchial tumor.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Node size measurements (4R 12 mm, 7 15 mm) are not preserved.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (4R, 7, 10R).
- Schema / structure: Core staging logic is correct; inspection narrative polarity is the main precision issue.

## note_007 — ✅ PASS — 93 / 100
**Note title:** OP NOTE — Airway stent

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Straight silicone stent sizing and exact subglottic distance could be more explicit in structured fields.

**Logic & Coding**
- CPT consistency: 31631 is consistent with tracheal stent placement; balloon dilation is bundled into the stent service.
- Schema / structure: Good core extraction for stenosis dilation plus stent placement.

## note_025 — ❌ FAIL — 58 / 100
**Note title:** Navigational bronchoscopy + EBUS staging combined (Template E style, no explicit codes)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: EBUS node_events mark stations 7 and 11R as inspected_only even though all 3 stations were sampled.
- Mismatch: Because of that logic error, nodal coding is downcoded to 31652 instead of 31653.

**Completeness (Recall)**
- Missed procedure: Transbronchial biopsy / forceps biopsy of the RUL target is missed.
- Missed detail: Combined peripheral-target and mediastinal-target relationships are only partially preserved.

**Logic & Coding**
- CPT consistency: 31627/31629/+31654 are supported. EBUS should derive 31653, and the peripheral forceps biopsies support 31628 as well.
- Schema / structure: Combined peripheral+mediastinal case is not cleanly separated; this is a material logic and recall failure.

## note_021 — ✅ PASS — 94 / 100
**Note title:** Airway stent removal

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Residual post-removal stenosis caliber (~11–12 mm) and good distal patency are not preserved in airway outcome fields.

**Logic & Coding**
- CPT consistency: 31638 is consistent with stent removal/revision-style work on an existing stent.
- Schema / structure: Core stent-removal extraction is accurate.

## note_040 — ⚠️ WARNING — 82 / 100
**Note title:** Very short dictated note (codes omitted)

**Accuracy (Precision)**
- Hallucination: therapeutic_aspiration is an overcall from short-note suctioning of secretions in a combined BAL + EBUS case.
- Mismatch: Node_events omit the documented x4 pass counts for both station 7 and 4R.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31624 and 31652 are consistent with BAL plus 2-station EBUS sampling.
- Schema / structure: Overall extraction is usable; aspiration flag is too aggressive and pass counts are dropped.

## note_038 — ✅ PASS — 94 / 100
**Note title:** Bronchoscopy + EBUS with station list (headings format, no codes)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Enlarged-station descriptors are not preserved.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (4R, 7, 10R).
- Schema / structure: Accurate extraction for a concise EBUS staging note.

## note_020 — ❌ FAIL — 20 / 100
**Note title:** THERAPEUTIC BRONCHOSCOPY — ULTRA CONCISE (still non-edge-case)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Therapeutic aspiration / clot extraction is completely missed.
- Missed procedure: Diagnostic bronchoscopy is completely missed.
- Missed detail: General anesthesia and airway-patency outcome are also absent because the registry is effectively empty.

**Logic & Coding**
- CPT consistency: 31645 is clearly supported by the note.
- Schema / structure: Severe recall failure: the registry is essentially blank despite an explicit therapeutic bronchoscopy.

## note_008 — ✅ PASS — 96 / 100
**Note title:** Indication: Pleural effusion, diagnostic and therapeutic drainage.

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Volume removed and right laterality could be surfaced more explicitly.

**Logic & Coding**
- CPT consistency: 32555 is correct for ultrasound-guided thoracentesis.
- Schema / structure: Simple pleural case extracted accurately.

## note_042 — ✅ PASS — 93 / 100
**Note title:** Airway stent removal + BAL

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: BAL location is malformed ('right lower lobe (').
- Mismatch: Stent-brand detail is degraded ('S').

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Post-removal airway patency and mild mucosal irritation are not richly structured.

**Logic & Coding**
- CPT consistency: 31624 and 31638 are supported.
- Schema / structure: Core stent-removal + BAL extraction is correct with only minor text-normalization issues.

## note_046 — ✅ PASS — 92 / 100
**Note title:** EBUS-TBNA + endobronchial biopsies (sarcoid evaluation)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: BAL location and some evidence anchoring lean more on specimen text than on the procedural lines.

**Logic & Coding**
- CPT consistency: 31624/31625/31653 are supported.
- Schema / structure: Good extraction for a 3-station sarcoid EBUS case with endobronchial biopsies and BAL.

## note_013 — ❌ FAIL — 58 / 100
**Note title:** Procedure note: Bronchoscopy, BAL, transbronchial biopsy

**Accuracy (Precision)**
- Hallucination: +31632 is not supported; the note documents transbronchial biopsies only in the right lower lobe, not an additional lobe.
- Mismatch: transbronchial_biopsy.locations incorrectly include RML because BAL location leaked into biopsy lobe logic.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Biopsy count (6) and fluoroscopic guidance are not preserved cleanly.

**Logic & Coding**
- CPT consistency: 31624 and 31628 are supported. +31632 is not.
- Schema / structure: Lobe attribution error cascades into unsupported add-on coding.

## note_027 — ✅ PASS — 91 / 100
**Note title:** Narrative op note — minimal headings

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: RLL lateral-basal BAL location and washings could be more explicit in top-level fields.

**Logic & Coding**
- CPT consistency: 31624 and 31645 are supported; additional washings are also represented.
- Schema / structure: Good extraction for aspiration + BAL + washings in a narrative note.

## note_022 — ⚠️ WARNING — 88 / 100
**Note title:** Bronchoscopy + EBUS-TBNA (ICD/CPT lines present)

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies a mass even though the note says airway inspection was normal with no endobronchial tumor.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (4R, 7, 11L).
- Schema / structure: High-level EBUS staging is right; only the inspection narrative polarity is wrong.

## note_034 — ⚠️ WARNING — 84 / 100
**Note title:** Peripheral bronchoscopy (cone-beam confirmation) + BAL

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies a lesion as an airway finding, which is not actually described endobronchially in the note.
- Mismatch: 77012 is a coder-inference from cone-beam CT confirmation and should be manually reviewed.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: BAL volume/location detail is not preserved cleanly.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31629/+31654 are supported. 77012 should be manually reviewed.
- Schema / structure: Major procedure families are correct; imaging-code aggressiveness is the main issue.

## note_010 — ✅ PASS — 93 / 100
**Note title:** NAVIGATIONAL BRONCHOSCOPY — SHORT DICTATION

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: BAL location and tool counts could be more explicit in structured fields.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31629/+31654 are coherent with the note.
- Schema / structure: Good separation of navigation, radial EBUS, TBNA, forceps biopsy, brushing, and BAL.

## note_016 — ✅ PASS — 94 / 100
**Note title:** EBUS procedure (checklist style)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Checklist-style airway survey and station enlargement descriptors are minimally structured.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (4R, 7, 10L).
- Schema / structure: Accurate extraction for a concise EBUS checklist note.

## note_035 — ✅ PASS — 94 / 100
**Note title:** THERAPEUTIC BRONCHOSCOPY — mucus plugging

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Washings are represented but with limited specimen-detail granularity.

**Logic & Coding**
- CPT consistency: 31645 is supported; the note does not support BAL, and the current extraction appropriately avoids 31624.
- Schema / structure: Therapeutic aspiration vs washings is handled correctly.

## note_018 — ⚠️ WARNING — 86 / 100
**Note title:** Peripheral bronchoscopy (cone-beam CT assisted)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: 77012 is a gray-zone billing inference from cone-beam CT confirmation rather than a clearly documented procedural code.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Bronchus-sign positivity and lesion-confirmation imaging details could be better structured.

**Logic & Coding**
- CPT consistency: 31623/31627/31628/31629/+31654 are supported. 77012 should be manually reviewed.
- Schema / structure: Major procedure families are correct; only imaging-code aggressiveness remains.

## note_026 — ⚠️ WARNING — 80 / 100
**Note title:** PRE-PROCEDURE DIAGNOSIS: Mediastinal lymphadenopathy; lung mass (R59.0, R91.8)

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies a mass even though the note says no endobronchial lesion.
- Mismatch: Station 11L pass count is wrong in node_events (recorded as 6 instead of 3).

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Enlarged/borderline/visualized station descriptors are not preserved.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (7, 4L, 11L).
- Schema / structure: High-level EBUS extraction is right, but quantitative detail is unreliable.

## note_029 — ⚠️ WARNING — 84 / 100
**Note title:** THERAPEUTIC BRONCHOSCOPY — AIRWAY OBSTRUCTION

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Inspection narrative is malformed and does not cleanly capture the right mainstem endoluminal tumor/80% obstruction.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Pre/post obstruction severity and APC-as-adjunct context are not well structured.

**Logic & Coding**
- CPT consistency: 31640 is supported. APC appears adjunctive at the same site, so a separate 31641 is not clearly required.
- Schema / structure: Therapeutic-family extraction is acceptable, but descriptive fidelity is weak.

## note_030 — ⚠️ WARNING — 87 / 100
**Note title:** Airway stent placement — silicone Y stent

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Y-stent device detail is incomplete: 15 x 12 x 12 mm is reduced to incomplete sizing, and the bilateral mainstem limbs are not represented explicitly.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Carinal/distal-tracheal target anatomy and post-placement improvement could be richer.

**Logic & Coding**
- CPT consistency: 31631 is defensible for tracheal Y-stent placement.
- Schema / structure: Core stent-placement extraction is correct; device granularity is incomplete.

## note_036 — ⚠️ WARNING — 78 / 100
**Note title:** Airway stent surveillance + granulation management

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Mechanical debridement of granulation tissue is described but not represented as its own therapeutic event.
- Missed detail: Existing tracheal stent details and toileting/secretions management are only partially preserved.

**Logic & Coding**
- CPT consistency: 31641 is reasonable for APC treatment of granulation tissue; no false new-stent code is generated in the current output.
- Schema / structure: Improved from the classic false-placement error, but recall remains incomplete.

## note_032 — ⚠️ WARNING — 88 / 100
**Note title:** Bronchoscopy + EBUS (dictated paragraph)

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Station 7 pass count is missing from one node_event despite explicit documentation of 5 passes.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Doppler use is not surfaced.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (4R, 7, 11R).
- Schema / structure: High-level EBUS extraction is correct; one quantitative detail is dropped.

## note_050 — ❌ FAIL — 68 / 100
**Note title:** Navigational bronchoscopy + staging in one session (Template A-ish)

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings is not a faithful restatement of the note and implies lesion-focused inspection language that was not actually documented endobronchially.
- Mismatch: EBUS node-event evidence quotes are drawn from the specimen list rather than the procedural sampling lines.

**Completeness (Recall)**
- Missed procedure: Transbronchial forceps biopsy of the RUL lesion is documented ('forceps biopsies x8') but not represented, and 31628 is missing.
- Missed detail: Peripheral-target biopsy count (x8) is not preserved.

**Logic & Coding**
- CPT consistency: 31627/31629/31653/+31654 are supported. 31628 is also supported and missing.
- Schema / structure: Combined peripheral-target plus mediastinal-staging case has material recall loss.

## note_037 — ✅ PASS — 96 / 100
**Note title:** Pleural procedure: 14 Fr pigtail + intrapleural fibrinolytic instillation

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Drainage character and clamp duration are minor details not fully modeled.

**Logic & Coding**
- CPT consistency: 32557 and 32561 are consistent with pigtail placement plus first-day intrapleural fibrinolytic instillation.
- Schema / structure: Good separation of chest tube placement and fibrinolytic therapy.

## note_003 — ⚠️ WARNING — 88 / 100
**Note title:** PRE: Abnormal chest imaging; mediastinal staging needed

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion/tumor even though the note says airway exam was without endobronchial lesion.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Node size descriptors are not preserved.

**Logic & Coding**
- CPT consistency: 31653 is consistent with 3 sampled stations (4R, 7, 11R).
- Schema / structure: Core EBUS staging extraction is correct; airway narrative polarity is wrong.

## note_014 — ⚠️ WARNING — 84 / 100
**Note title:** Robotic navigational bronchoscopy + fiducial placement

**Accuracy (Precision)**
- Hallucination: diagnostic_bronchoscopy.inspection_findings is nonspecific/nonsensical and not grounded in a real airway finding from the note.
- Mismatch: Peripheral target/fiducial granularity is degraded to 'Unknown target' in structured data.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Fiducial count (x3) and LLL posterior-basal target location are not cleanly preserved in a first-class procedure object.

**Logic & Coding**
- CPT consistency: 31626/31627/31628/31629/+31654 are coherent with the note.
- Schema / structure: Core recall is good, but fiducial placement lives in granular_data rather than a clearly modeled performed procedure.
