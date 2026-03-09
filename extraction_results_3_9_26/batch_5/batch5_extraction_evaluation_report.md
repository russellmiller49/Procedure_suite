# Extraction Quality Report

Evaluated **50 notes** across **1 batch-output file** (`my_results_batch_5.txt`).

Overall average score: **63.5 / 100**
Status counts: **7 PASS**, **12 WARNING**, **31 FAIL**.

## Cross-file patterns

- All **21 CT-guided percutaneous ablation notes** failed. In 16, the pipeline forced the case into a bronchoscopic `peripheral_ablation` or `cryotherapy` family with **31641**; in the remaining 5 percutaneous **PEF** notes, the primary ablation procedure was missed entirely.
- All **7 bronchoscopic PEF cases** failed. Five dropped the therapeutic ablation event altogether, and two recast **PEF** as **thermal ablation / 31641**, including extraction from the note's own 'non-thermal' wording.
- The provided NCCI table marks **31628 + 31629** as a bundled pair (modifier indicator 0). That exact unsupported pair appears in **11 notes**, so several otherwise reasonable sampling extractions still yield a non-defensible final CPT stack.
- Peripheral **cryoablation** is repeatedly routed through the `cryotherapy` family rather than a clean peripheral-ablation concept. That wrong-family logic appears in **11 notes** and is a recurring source of bad 31641 derivation.
- Lower-severity but frequent issues include unsupported **SPiN** platform hallucinations, false endobronchial inspection findings despite normal airway surveys, and repeated omission of documented anesthesia/sedation context.

### note_001 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - navigation_platform='SPiN' is not supported; the note says robotic navigation but never names a platform.
- Mismatch: 
  - peripheral_tbna.targets_sampled and granular_data.navigation_targets are polluted with specimen-count strings ('TBNA x4 passes', 'TBBx x6 fragments') instead of true anatomic targets.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - Could preserve the exact RUL posterior segment target in a cleaner target object rather than duplicating 'RUL' and specimen-count text.

**Logic & Coding**
- CPT consistency: 31627, 31628, 31629, and +31654 are procedurally supported, but 31628/31629 form an NCCI bundled pair in the provided table, so the final CPT stack is not defensible as-is. 31641 and 77012 remain gray-zone inferences from peripheral ablation and CBCT mention.
- Schema / structure: Core procedure families are correct, but target granularity is malformed.

### note_002 — ❌ FAIL — 38 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true and 31641 are not supported; the note documents CT-guided percutaneous cryoablation, not bronchoscopic cryotherapy/tumor destruction.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The true CT-guided percutaneous ablation family is not represented.
- Missed details: 
  - Post-procedure CT guidance context is present in the note but no guidance-specific evidence or code is surfaced.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this purely CT-guided percutaneous case.
- Schema / structure: Primary procedure is forced into the wrong bronchoscopic family.

### note_003 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - thermal_ablation/31641 are not supported; the note explicitly documents pulsed electric field ablation and even describes it as non-thermal.
  - navigation_platform='SPiN' is not supported; no platform is named.
  - diagnostic_bronchoscopy.inspection_findings turns a normal airway survey into a 'lesion confirmed' narrative.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is left blank.

**Logic & Coding**
- CPT consistency: 31624, 31627, 31628, 31629, and +31654 are supported by the note. 31641 is not. Also, 31628/31629 appear together despite the provided NCCI pair marking them bundled with modifier indicator 0.
- Schema / structure: The primary therapeutic event is misclassified: bronchoscopic PEF is recast as thermal ablation.

### note_004 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: 
  - Sedation is internally conflicted in the note (moderate sedation vs later GA with LMA); the JSON chooses Moderate without carrying the ambiguity.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - LMA airway detail is not surfaced.
  - TBNA/TBBx exact counts are not preserved.

**Logic & Coding**
- CPT consistency: 31627, 31628, 31629, and +31654 are procedurally supported. 31628/31629 together remain NCCI-inconsistent in the provided table. 31641 is still a gray-zone peripheral-ablation inference.
- Schema / structure: Overall extraction is clinically coherent despite the sedation ambiguity.

### note_005 — ❌ FAIL — 54 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - linear_ebus.performed=true is not supported; the note only mentions Doppler on linear EBUS from a segmental takeoff to exclude an adjacent vessel, not a formal linear EBUS staging procedure.
  - balloon_occlusion.performed=true and CPT 31634 are not supported; the balloon language is hemostasis readiness during cryobiopsy, not a stand-alone Chartis/balloon occlusion assessment.
- Mismatch: 
  - The note documents TBNA x4 and transbronchial cryobiopsy x3, but the JSON also creates a standard transbronchial_biopsy object with sample count 4, blurring cryobiopsy vs conventional TBBx.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - Cryobiopsy counts and the 1.1 mm probe are captured, but the biopsy-family logic remains internally messy.

**Logic & Coding**
- CPT consistency: 31627, 31629, and +31654 are supported. 31634 is not. 31628 may be arguable only if cryobiopsy is intentionally mapped to TBLB, but the current schema does not state that cleanly. 31641 is routed through the wrong family and remains gray-zone for peripheral ablation.
- Schema / structure: Multiple adjunct phrases are over-interpreted into extra procedure families.

### note_006 — ❌ FAIL — 42 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note is CT-guided microwave ablation, not bronchoscopic destruction.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The true CT-guided percutaneous ablation family is not represented.
- Missed details: 
  - Small apical pneumothorax documented in the note is not surfaced in outcomes/complications.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family plus missed complication detail.

### note_007 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - diagnostic_bronchoscopy.inspection_findings says 'endobronchial abnormality' even though the note says no endobronchial abnormality.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.
  - Exact TBBx x6 and brushing x1 counts are not deeply structured.

**Logic & Coding**
- CPT consistency: 31623, 31627, 31628, and +31654 are supported. 31641 is still a gray-zone inference for peripheral RFA ablation.
- Schema / structure: Core procedure families are correct; the main precision issue is the false airway finding.

### note_008 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - thermal_ablation/31641 are not supported; the note documents pulsed electric field ablation, not thermal destruction.
  - diagnostic_bronchoscopy.inspection_findings reduces a normal airway survey to a vague 'lesion' finding.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.
  - TBNA/TBBx counts are only partially preserved.

**Logic & Coding**
- CPT consistency: 31627, 31628, 31629, and +31654 are supported. 31641 is not. As extracted, 31628/31629 are also NCCI-inconsistent when billed together.
- Schema / structure: Primary ablation modality is misclassified.

### note_009 — ❌ FAIL — 46 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note documents percutaneous RFA under CT.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided percutaneous ablation family is not represented.
- Missed details: 
  - CT guidance is explicit in the note but not carried into the coded output.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong bronchoscopic family assigned to a percutaneous ablation.

### note_010 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - diagnostic_bronchoscopy.inspection_findings ('lesion with robotic platform') is not supported; the note describes no endobronchial lesion and no specimens were collected.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported by the performed navigation/radial workflow. 31641 and 77012 remain gray-zone inferences for peripheral microwave ablation plus CBCT.
- Schema / structure: Core no-specimen ablation workflow is captured correctly.

### note_011 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true is not cleanly supported; the note documents peripheral cryoablation of a pulmonary nodule, not an endobronchial cryotherapy procedure.
  - diagnostic_bronchoscopy.inspection_findings says 'lesion' despite a normal airway survey.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - TBNA/TBBx counts are not deeply structured beyond the procedure flags.

**Logic & Coding**
- CPT consistency: 31627, 31628, 31629, and +31654 are supported procedurally, but 31628/31629 are an NCCI bundled pair in the provided table. 31641 is currently derived from cryotherapy rather than the peripheral-ablation concept, which is the wrong family.
- Schema / structure: Core capture is good, but cryoablation is routed through the cryotherapy family.

### note_012 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - CT-guided percutaneous PEF ablation is missed entirely; no primary procedure is extracted.
- Missed details: 
  - Small perilesional hemorrhage in the operative summary is not surfaced as an outcome detail.

**Logic & Coding**
- CPT consistency: No defensible ablation CPT is produced because the primary procedure is omitted.
- Schema / structure: Major recall failure: the note's only real procedure is absent.

### note_013 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.
  - TBBx x5 and brush x1 counts are not deeply structured.

**Logic & Coding**
- CPT consistency: 31623, 31627, 31628, and +31654 are supported. 31641 is still a gray-zone peripheral-ablation inference, but the extraction itself is otherwise coherent.
- Schema / structure: Good separation of brushing, transbronchial biopsy, navigation, radial EBUS, and ablation.

### note_014 — ❌ FAIL — 44 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; this is percutaneous microwave ablation under CT guidance.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided/percutaneous ablation family is not represented.
- Missed details: 
  - Small tract hemorrhage documented in the note is omitted from outcomes/complications.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Primary procedure family is wrong and the only documented complication detail is missed.

### note_015 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: 
  - radial_ebus.probe_position='Not visualized' conflicts with the note, which explicitly says the lesion was concentric on radial EBUS.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - The missing +31654 logic is notable because radial EBUS localization is clearly documented alongside peripheral sampling.
  - Airway survey detail ('mild anthracosis; no endobronchial lesion') is not carried through cleanly.

**Logic & Coding**
- CPT consistency: 31624, 31627, 31628, and 31629 are supported. +31654 should also be considered. 31628/31629 together are NCCI-inconsistent in the provided pair file. 31641 remains a gray-zone peripheral-ablation inference.
- Schema / structure: High recall overall, but radial EBUS specifics are wrong and coding is incomplete.

### note_016 — ❌ FAIL — 44 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true and 31641 are not supported; the note is CT-guided cryoablation, not bronchoscopic cryotherapy.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided percutaneous ablation family is not represented.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong bronchoscopic family assigned to a percutaneous cryoablation note.

### note_017 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - diagnostic_bronchoscopy.inspection_findings='lesion' is not supported; the note says airway survey without lesion.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The primary bronchoscopic PEF ablation is not extracted at all.
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 77012 alone is not a defensible final output for this case. The note supports navigation/radial localization and a bronchoscopic PEF ablation, not just guidance.
- Schema / structure: Major recall failure: the therapeutic event is missing.

### note_018 — ❌ FAIL — 46 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note documents CT-guided RFA ablation.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided percutaneous ablation family is not represented.
- Missed details: 
  - Mild perilesional hemorrhage in the tab summary is not surfaced.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong bronchoscopic family plus incomplete outcome capture.

### note_019 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true is not cleanly supported; the note documents peripheral cryoablation rather than an endobronchial cryotherapy service.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented only as 'GA' in the note and sedation is left blank.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported by the navigation/radial workflow. 31641 is being sourced from cryotherapy rather than the peripheral-ablation concept and remains a gray-zone coding inference.
- Schema / structure: Core no-sampling cryoablation workflow is captured, but the family used to justify 31641 is wrong.

### note_020 — ❌ FAIL — 50 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note is CT-guided microwave ablation.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The true percutaneous/CT-guided ablation family is not represented.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family.

### note_021 — ❌ FAIL — 44 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - A formal moderate bleeding complication is overcalled even though the note says Complications: None and describes only mild biopsy bleeding controlled endoscopically.
  - diagnostic_bronchoscopy.inspection_findings turns a non-endobronchial peripheral lesion into an airway lesion narrative.
- Mismatch: 
  - radial_ebus.probe_position='Adjacent' is not what the note says; the documented view is eccentric with adjacent atelectasis.

**Completeness (Recall)**
- Missed procedures: 
  - The primary bronchoscopic PEF ablation is not represented.
- Missed details: 
  - TBBx x5 is not carried with full count granularity.

**Logic & Coding**
- CPT consistency: 31627, 31628, and +31654 are supported. The therapeutic PEF portion is missing, and 77012 is only an inference from CBCT mention.
- Schema / structure: This is a combined recall and complication-logic failure.

### note_022 — ❌ FAIL — 44 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true and 31641 are not supported; the note documents CT-guided cryoablation.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided percutaneous ablation family is not represented.
- Missed details: 
  - Sedation/anesthesia is not captured at all.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong bronchoscopic family with incomplete peri-procedure context.

### note_023 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - navigation_platform='SPiN' is not supported; the note never names a platform.
  - diagnostic_bronchoscopy.inspection_findings='lesion' is not supported by the normal airway survey.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported. 31641 and 77012 remain gray-zone/inferred from peripheral RFA ablation plus CBCT.
- Schema / structure: Core extraction is usable, but there are avoidable unsupported details.

### note_024 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - CT-guided PEF ablation is missed entirely.
- Missed details: None

**Logic & Coding**
- CPT consistency: No defensible ablation CPT is produced because the primary procedure is omitted.
- Schema / structure: Pure recall failure on the only performed procedure.

### note_025 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported by the note's navigation/radial workflow. 31641 and 77012 are still gray-zone peripheral-ablation/CBCT inferences.
- Schema / structure: Good capture of a no-sampling bronchoscopic microwave ablation case.

### note_026 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - navigation_platform='SPiN' is not supported; the note does not name a platform.
  - cryotherapy.performed=true is not cleanly supported; the note documents peripheral cryoablation rather than endobronchial cryotherapy.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported. 31641 is routed through the cryotherapy family and remains a gray-zone coding inference for peripheral cryoablation. 77012 is inferred from CBCT mention.
- Schema / structure: Core capture is good, but the ablation family used for coding is wrong.

### note_027 — ❌ FAIL — 50 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note is CT-guided microwave ablation.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided percutaneous ablation family is not represented.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family.

### note_028 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - Bronchoscopic PEF ablation is omitted even though it is one of the named performed procedures.
- Missed details: 
  - General anesthesia is documented but sedation is omitted.
  - TBNA x2 and TBBx x4 counts are not deeply structured.

**Logic & Coding**
- CPT consistency: 31627, 31628, 31629, and +31654 are supported. The therapeutic PEF portion is missing. Also, 31628/31629 are an NCCI bundled pair in the provided table.
- Schema / structure: High recall for sampling, but the primary ablation event is missing.

### note_029 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.
  - TBBx x5 and brushing x1 counts are not deeply structured.

**Logic & Coding**
- CPT consistency: 31623, 31627, 31628, and +31654 are supported. 31641 remains a gray-zone peripheral-ablation inference.
- Schema / structure: Good overall separation of biopsy, brushing, navigation, radial EBUS, and ablation.

### note_030 — ❌ FAIL — 42 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true and 31641 are not supported; the note is CT-guided cryoablation.
- Mismatch: 
  - sedation.type='General' overreads a conflicting template line; the note's actual procedural sedation description is moderate sedation.

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided percutaneous ablation family is not represented.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong bronchoscopic family plus sedation overread.

### note_031 — ❌ FAIL — 66 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - A formal moderate bleeding complication (Nashville grade 2) is not supported; the note says Complications: None and describes only mild biopsy bleeding controlled with suction and iced saline.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31627, 31628, 31629, and +31654 are supported procedurally. 31628/31629 are nonetheless NCCI-inconsistent as a final stack. 31641 and 77012 remain gray-zone/inferred.
- Schema / structure: Core extraction is good, but complication logic is materially overstated.

### note_032 — ❌ FAIL — 52 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - CT-guided PEF ablation is missed entirely.
- Missed details: 
  - Moderate sedation is not captured.
  - Small perilesional hemorrhage in the note is not surfaced.

**Logic & Coding**
- CPT consistency: No defensible ablation CPT is produced because the primary procedure is omitted.
- Schema / structure: Major recall failure.

### note_033 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported by the navigation/radial workflow. 31641 and 77012 are gray-zone inferences for peripheral microwave ablation plus CBCT.
- Schema / structure: Good capture of an ablation-only bronchoscopic case.

### note_034 — ❌ FAIL — 48 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note documents CT-guided RFA.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided/percutaneous ablation family is not represented.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family.

### note_035 — ❌ FAIL — 40 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note is CT-guided microwave ablation, not bronchoscopic ablation.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided/percutaneous ablation family is not represented.
- Missed details: 
  - Small pneumothorax documented in the note is not surfaced in outcomes/complications.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong bronchoscopic family plus missed complication detail.

### note_036 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - diagnostic_bronchoscopy.inspection_findings='lesion (32998—??)' is not supported; the note says no endobronchial lesion.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported. 31641 and 77012 remain gray-zone inferences for peripheral microwave ablation plus CBCT.
- Schema / structure: Core extraction is otherwise appropriate.

### note_037 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true is not cleanly supported; the note documents peripheral cryoablation, not an endobronchial cryotherapy service.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented only as 'GA' and sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported. 31641 is sourced from cryotherapy rather than the peripheral-ablation concept and is therefore justified from the wrong family.
- Schema / structure: Good overall capture, but cryoablation is routed through the cryotherapy family.

### note_038 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - diagnostic_bronchoscopy.inspection_findings='lesion' is not supported; the note describes a normal airway exam.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The primary bronchoscopic PEF ablation is not extracted.
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 77012 alone is not a defensible final stack. The note supports navigation/radial localization plus bronchoscopic PEF ablation.
- Schema / structure: Major recall failure on the therapeutic event.

### note_039 — ❌ FAIL — 48 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note documents CT-guided RFA.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided/percutaneous ablation family is not represented.
- Missed details: 
  - Moderate sedation is not captured.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family.

### note_040 — ❌ FAIL — 42 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true and 31641 are not supported; this is CT-guided percutaneous cryoablation, not bronchoscopic cryotherapy.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The true percutaneous ablation family is not represented.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family.

### note_041 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.
  - TBNA x2 and TBBx x5 counts are not deeply structured.

**Logic & Coding**
- CPT consistency: 31627, 31628, and 31629 are procedurally supported, but 31628/31629 form an NCCI bundled pair in the provided table. 31641 remains a gray-zone peripheral-ablation inference.
- Schema / structure: Strong core extraction with a CPT stack that needs bundling review.

### note_042 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - CT-guided PEF ablation is missed entirely.
- Missed details: None

**Logic & Coding**
- CPT consistency: No defensible ablation CPT is produced because the primary procedure is omitted.
- Schema / structure: Primary procedure missing.

### note_043 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported. 31641 and 77012 remain gray-zone inferences for peripheral RFA ablation plus CBCT.
- Schema / structure: Good capture of a no-specimen RFA ablation case.

### note_044 — ❌ FAIL — 56 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - Bronchoscopic PEF ablation is not extracted.
- Missed details: 
  - General anesthesia is documented but sedation is omitted.
  - diagnostic_bronchoscopy is not explicitly surfaced even though bronchoscopic access is implicit.

**Logic & Coding**
- CPT consistency: 77012 alone is not defensible as the final output; the therapeutic PEF event is missing.
- Schema / structure: Major recall failure on the primary therapeutic procedure.

### note_045 — ❌ FAIL — 62 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - balloon_occlusion.performed=true and CPT 31634 are not supported; the note describes brief balloon occlusion for hemostasis during biopsy bleeding, not a stand-alone Chartis/balloon occlusion assessment.
  - navigation_platform='SPiN' is not supported; the note never names a platform.
  - diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion although the note says there was no endobronchial lesion.
- Mismatch: 
  - radial_ebus.probe_position='Adjacent' is not the documented view; the note says eccentric lesion with catheter manipulation to improve engagement.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - ETT airway detail is not captured.

**Logic & Coding**
- CPT consistency: 31627, 31628, 31629, and +31654 are supported procedurally. 31634 is not. 31628/31629 are also NCCI-inconsistent as a final pair. 31641 and 77012 remain gray-zone peripheral-ablation/CBCT inferences.
- Schema / structure: A hemostatic adjunct is misread as a distinct balloon-occlusion procedure.

### note_046 — ❌ FAIL — 48 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - peripheral_ablation.performed=true and 31641 are not supported; the note is CT-guided microwave ablation.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided/percutaneous ablation family is not represented.
- Missed details: 
  - Moderate sedation is not captured.

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family.

### note_047 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented only as 'GA' and sedation is omitted.

**Logic & Coding**
- CPT consistency: 31624 and 31627 are clearly supported. +31654, 31641, and 77012 remain policy-dependent/gray-zone inferences for radial localization, peripheral cryoablation, and CBCT.
- Schema / structure: Strong overall capture of BAL plus no-sampling cryoablation workflow.

### note_048 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - CT-guided PEF ablation is missed entirely.
- Missed details: None

**Logic & Coding**
- CPT consistency: No defensible ablation CPT is produced because the primary procedure is omitted.
- Schema / structure: Primary procedure missing.

### note_049 — ❌ FAIL — 42 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - cryotherapy.performed=true and 31641 are not supported; the note is CT-guided cryoablation.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: 
  - The CT-guided/percutaneous ablation family is not represented.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31641 is not supported for this percutaneous case.
- Schema / structure: Wrong procedure family.

### note_050 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: 
  - General anesthesia is documented but sedation is omitted.

**Logic & Coding**
- CPT consistency: 31627 and +31654 are supported. 31641 and 77012 remain gray-zone/inferred for peripheral RFA ablation plus CBCT.
- Schema / structure: Good capture of a straightforward no-specimen RFA ablation case.
