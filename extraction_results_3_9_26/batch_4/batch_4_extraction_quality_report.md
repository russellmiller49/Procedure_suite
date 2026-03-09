# Extraction Quality Report

Evaluated **50 notes** from **my_results_batch_4.txt**.

Overall average score: **75.6 / 100**
Status counts: **13 PASS**, **17 WARNING**, **20 FAIL**.

## Batch patterns

- The most common high-severity problem was **BLVR/PAL coding logic**, especially unsupported dual-coding of **31634 + 31647** when balloon occlusion/Chartis work was bundled into same-session valve placement.
- The next major issue was **recall loss for performed procedures**, especially rare/non-core workflows such as tracheostomy exchange, brachytherapy catheter placement, Watanabe spigot placement, TEF dye evaluation, vocal-cord assessment, and transtracheal oxygen catheter exchange.
- Several BLVR notes also had **quantitative drift** in `number_of_valves` and/or loss of explicit target lobe.
- A recurring precision issue was **false lesion/mass/tumor narrative** inside `diagnostic_bronchoscopy.inspection_findings` even when the note explicitly said no lesion or no mass.
- Secondary coding failures included **tumor-family overcalls** (e.g., 31640 for granulation or non-tumor obstructing material) and **dropped radial EBUS / forceps-biopsy detail** in peripheral sampling cases.

## Compact summary

| Note | Score | Status | Key issue |
|---|---:|---|---|
| note_040 | 58 | FAIL | linear_ebus.performed=true and CPT 31652 are not supported by this note. The procedure ... |
| note_026 | 82 | WARNING | Dynamic assessment/forced expiratory maneuver and CPAP titration response are central t... |
| note_044 | 55 | FAIL | diagnostic_bronchoscopy.airway_abnormalities=['Secretions'] is not supported; the note ... |
| note_018 | 86 | WARNING | number_of_valves=1, but the note documents two valves placed within the RLL target due ... |
| note_013 | 92 | PASS | Sample counts (TBNA x4, forceps x4, brush x1) and fluoroscopy use are only partially pr... |
| note_004 | 46 | FAIL | CPT 31634 is not separately supported with same-session valve placement; the note docum... |
| note_036 | 90 | PASS | Per-area activation counts (LUL 38, lingula 12) are not preserved as structured quantit... |
| note_030 | 76 | WARNING | inspection_findings implies a lesion even though the note says no discrete lesion was v... |
| note_043 | 40 | FAIL | Bronchoscopy is explicitly performed. |
| note_048 | 92 | PASS | Topical mitomycin C is not represented as an adjunct treatment detail. |
| note_023 | 90 | PASS | The note says bilateral staged with today's lavage on the right; laterality is not pres... |
| note_009 | 80 | WARNING | inspection_findings implies a lesion despite the airway survey explicitly saying 'No le... |
| note_001 | 62 | FAIL | CPT 31634 is not separately supported with same-session BLVR valve placement. |
| note_050 | 94 | PASS | Dose fields are unspecified in the source note and appropriately not hallucinated. |
| note_028 | 93 | PASS | Basket retrieval technique and exact RLL basal target are not deeply structured. |
| note_024 | 84 | WARNING | The registry uses pleural_biopsy as the procedure family, while the note is more specif... |
| note_025 | 86 | WARNING | As in note_024, this is modeled as pleural_biopsy even though the note describes an ult... |
| note_031 | 58 | FAIL | Endobronchial Watanabe spigot placement is the key therapeutic intervention and is not ... |
| note_033 | 72 | FAIL | The stent is a distal tracheal/carina silicone Y-stent, yet billing is assigned to 3163... |
| note_019 | 60 | FAIL | CPT 31634 is not separately supported with same-session valve placement for persistent ... |
| note_006 | 78 | WARNING | inspection_findings implies a mass even though the note says 'no mass'. |
| note_015 | 62 | FAIL | sedation.type is effectively treated as moderate-sedation evidence even though the note... |
| note_007 | 76 | WARNING | inspection_findings implies a lesion even though the note says 'no lesion'. |
| note_008 | 68 | FAIL | CPT 31634 is not separately supported with same-session valve placement. |
| note_037 | 84 | WARNING | Selective intubation/endobronchial tamponade with blocker positioning is not modeled as... |
| note_002 | 82 | WARNING | number_of_valves=2, but the note documents 3 RUL valves. |
| note_042 | 68 | FAIL | CPT 31640 (tumor excision) is a poor fit for removal of necrotic/fungal obstructing mat... |
| note_021 | 95 | PASS | No major issues. |
| note_047 | 78 | WARNING | CPT 31640 is not strongly supported; the note describes granulation debulking after ste... |
| note_039 | 88 | WARNING | Pass metadata is preserved for 4R but not clearly carried through for station 7. |
| note_029 | 94 | PASS | No major issues. |
| note_027 | 91 | PASS | Kenalog intralesional injection is not modeled as an adjunct treatment detail. |
| note_012 | 66 | FAIL | diagnostic_bronchoscopy.inspection_findings is pulled from the plan language ('hemoptys... |
| note_020 | 91 | PASS | No major issues. |
| note_022 | 84 | WARNING | diagnostic_bronchoscopy.inspection_findings suggests endobronchial obstruction even tho... |
| note_005 | 64 | FAIL | CPT 31634 is not separately supported with same-session BLVR valve placement. |
| note_034 | 82 | WARNING | Treatment locations (supraglottic and tracheal lesions) are not captured with anatomic ... |
| note_041 | 85 | WARNING | Cryoprobe en-bloc extraction versus suction/forceps fragments is not preserved in struc... |
| note_003 | 68 | FAIL | CPT 31634 is not separately supported with same-session BLVR valve placement. |
| note_032 | 92 | PASS | Granulation-specific detail and final airway caliber are not quantified. |
| note_017 | 64 | FAIL | CPT 31634 is not separately supported with same-session endobronchial valve placement f... |
| note_011 | 70 | FAIL | Radial EBUS/radial ultrasound confirmation is documented and not represented. |
| note_035 | 94 | PASS | Bronchospasm treated with bronchodilator is not surfaced as a transient intraprocedural... |
| note_046 | 58 | FAIL | Transtracheal oxygen catheter exchange is explicitly performed and is not represented. |
| note_010 | 93 | PASS | Brush and TBBx counts are not deeply structured, but the core procedures and station 7 ... |
| note_016 | 84 | WARNING | inspection_findings implies a lesion even though the note says 'no lesion'. |
| note_014 | 72 | FAIL | CPT 31634 is not supported. The balloon use in the note is for segmental hemostasis dur... |
| note_049 | 78 | WARNING | Pleural drain placement is documented in the note, but pleural_procedures.chest_tube is... |
| note_038 | 35 | FAIL | Bronchoscopy is explicitly performed. |
| note_045 | 40 | FAIL | Bronchoscopic/laryngoscopic vocal-cord motion assessment is explicitly performed. |

## note_040 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: linear_ebus.performed=true and CPT 31652 are not supported by this note. The procedure is explicitly EUS-B via the esophagus, not bronchoscopic linear EBUS.
- Mismatch: The pipeline double-counts the same staging work under both eus_b and linear_ebus.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Per-station pass counts (3 passes each at 7 and 4L) are not preserved in a station-specific EUS-B structure.

**Logic & Coding**
- CPT consistency: 43238 is the only defensible code surfaced here. 31652 is not supported from the raw note.
- Schema / structure: Major procedure-family confusion: EUS-B was forced into a bronchoscopic EBUS bucket.

## note_026 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Dynamic assessment/forced expiratory maneuver and CPAP titration response are central to the note but are largely absent from structured output.; Severity and distribution of collapse (>80% in distal trachea and bilateral main bronchi) are not preserved.

**Logic & Coding**
- CPT consistency: A diagnostic bronchoscopy code is a reasonable fallback. There is no separate defensible CPT in the note for CPAP titration itself.
- Schema / structure: Usable high-level extraction, but the clinically important tracheobronchomalacia dynamics are under-modeled.

## note_044 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.airway_abnormalities=['Secretions'] is not supported; the note says the trachea was clear.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Tracheostomy tube exchange is explicitly performed and is not represented as a procedure.
- Missed details: Mild granulation at the stoma and bronchoscopic confirmation of position are not surfaced cleanly.

**Logic & Coding**
- CPT consistency: 31615 is supported for bronchoscopy through an established tracheostomy. 31622 is not supported by the note. The exchange itself is omitted from coding logic.
- Schema / structure: Important recall failure: a tracheostomy exchange note was reduced to bronchoscopy only.

## note_018 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: number_of_valves=1, but the note documents two valves placed within the RLL target due to residual bubbling after the first valve.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Target granularity is reduced from RLL superior segment plus adjacent segment to the lobe only.

**Logic & Coding**
- CPT consistency: 31647 is supported. A separate 31634 should remain suppressed because the balloon occlusion work is integral to same-session valve placement in the treated lobe.
- Schema / structure: Core PAL valve workflow is captured correctly; the main issue is undercounting the deployed valves.

## note_013 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Sample counts (TBNA x4, forceps x4, brush x1) and fluoroscopy use are only partially preserved.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31629/+31654 are coherent with the note.
- Schema / structure: Good separation of navigation, radial EBUS, peripheral TBNA, TBBx, brushings, and BAL.

## note_004 — ❌ FAIL — 46 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not separately supported with same-session valve placement; the note documents Chartis assessment bundled into BLVR insertion.; diagnostic_bronchoscopy.inspection_findings implies tumor despite the note saying 'No tumor'.
- Mismatch: number_of_valves=6, but the note documents total 4 valves.; blvr.target_lobe is missing even though LUL is explicit.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: The no-collateral-ventilation Chartis result is diluted into generic coding evidence.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should not be separately billed in this same-session BLVR case.
- Schema / structure: High-severity BLVR logic failure with wrong valve count and unsupported dual-coding.

## note_036 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Per-area activation counts (LUL 38, lingula 12) are not preserved as structured quantitative detail.

**Logic & Coding**
- CPT consistency: 31660 is reasonable for this thermoplasty session as documented.
- Schema / structure: Solid extraction; only quantitative detail depth is limited.

## note_030 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Hallucinations: inspection_findings implies a lesion even though the note says no discrete lesion was visualized because of clot burden.
- Mismatch: sedation.type='Moderate' conflicts with the note's narrative that the procedure was actually performed under GA due to ongoing bleeding.

**Completeness (Recall)**
- Missed procedures: Endobronchial blocker placement/isolation is a major performed action but is not represented as its own therapeutic event.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31645 is supported for airway clearance/clot aspiration. The blocker placement itself is not captured in current coding logic.
- Schema / structure: Core hemoptysis management is only partially represented; blocker therapy is omitted.

## note_043 — ❌ FAIL — 40 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Bronchoscopy is explicitly performed.; Endobronchial brachytherapy catheter placement is explicitly performed.
- Missed details: Left main bronchus endobronchial tumor and handoff to radiation oncology are not represented.

**Logic & Coding**
- CPT consistency: No standard CPT may be derivable for the adjunct catheter placement from this note, but leaving the registry essentially empty is not defensible.
- Schema / structure: Near-total recall failure.

## note_048 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Topical mitomycin C is not represented as an adjunct treatment detail.

**Logic & Coding**
- CPT consistency: 31630 is supported for rigid bronchoscopy with balloon dilation of tracheal stenosis.
- Schema / structure: Good extraction of the core therapeutic procedure.

## note_023 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: The note says bilateral staged with today's lavage on the right; laterality is not preserved.

**Logic & Coding**
- CPT consistency: 32997 is supported.
- Schema / structure: Good WLL extraction with minor detail loss.

## note_009 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: inspection_findings implies a lesion despite the airway survey explicitly saying 'No lesion'.
- Mismatch: number_of_valves=3, but the tab log says 4 placed.; collateral_ventilation_assessment='Chartis indeterminate' understates a clearly negative/no-CV result.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. Suppressing 31634 is appropriate in this same-session BLVR case.
- Schema / structure: Core BLVR extraction is usable, but quantitative and narrative precision are off.

## note_001 — ❌ FAIL — 62 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not separately supported with same-session BLVR valve placement.
- Mismatch: blvr.target_lobe is missing even though the note repeatedly specifies LUL.; collateral_ventilation_assessment='Chartis indeterminate' does not reflect the documented absence of collateral ventilation.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Secretions were captured, but the targeted segment distribution and immediate airflow reduction are not well preserved.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should not be separately billed here.
- Schema / structure: Same recurrent BLVR bundling error plus loss of explicit target lobe.

## note_050 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Dose fields are unspecified in the source note and appropriately not hallucinated.

**Logic & Coding**
- CPT consistency: 32561 is supported for first-day intrapleural fibrinolytic instillation.
- Schema / structure: Clean extraction.

## note_028 — ✅ PASS — 93 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Basket retrieval technique and exact RLL basal target are not deeply structured.

**Logic & Coding**
- CPT consistency: 31635 is supported for foreign body removal. BAL was correctly not forced on from an optional header mention.
- Schema / structure: Good precision and recall.

## note_024 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The registry uses pleural_biopsy as the procedure family, while the note is more specifically a transthoracic core needle biopsy of a pleural-based lung/chest-wall-abutting lesion.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Real-time ultrasound vessel-avoidance detail is not preserved.

**Logic & Coding**
- CPT consistency: 32408 is supported. A separate 76942 should not be added when imaging guidance is included in 32408.
- Schema / structure: Coding is right, but the procedural family is only approximately mapped.

## note_025 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: As in note_024, this is modeled as pleural_biopsy even though the note describes an ultrasound-guided transthoracic core biopsy of a pleural-based nodule.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Immediate bedside ultrasound check for pneumothorax is not preserved.

**Logic & Coding**
- CPT consistency: 32408 is supported.
- Schema / structure: Acceptable coding with an only-partial procedure-family fit.

## note_031 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Endobronchial Watanabe spigot placement is the key therapeutic intervention and is not represented.
- Missed details: RUL anterior segment localization and secure-fit placement are lost.

**Logic & Coding**
- CPT consistency: 31634 is defensible for stand-alone balloon occlusion localization. 31622 is only a fallback diagnostic component. The actual spigot placement work is missing from the extraction.
- Schema / structure: Major recall loss in a device-placement case.

## note_033 — ❌ FAIL — 72 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The stent is a distal tracheal/carina silicone Y-stent, yet billing is assigned to 31636 (bronchial stent) rather than the tracheal stent family.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Detailed Y-stent sizing is only partially preserved.

**Logic & Coding**
- CPT consistency: Mechanical debulking is supported. The stent work is supported, but 31631 is more defensible than 31636 given the tracheal/carina Y-stent description.
- Schema / structure: Good procedural recall, but materially wrong stent-family coding.

## note_019 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not separately supported with same-session valve placement for persistent air leak.
- Mismatch: blvr.number_of_valves=3, but the note documents 2 valves.; The target is RUL, but target lobe is not structured.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should be suppressed in this PAL valve case.
- Schema / structure: Another BLVR/PAL bundling failure with wrong valve count.

## note_006 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: inspection_findings implies a mass even though the note says 'no mass'.
- Mismatch: number_of_valves=1, but the note documents 3 valves to the RUL.; collateral_ventilation_assessment='Chartis indeterminate' does not match the explicit 'no CV' pattern.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. Suppressing 31634 is appropriate.
- Schema / structure: Core BLVR case is recognized, but quantitative accuracy is weak.

## note_015 — ❌ FAIL — 62 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: sedation.type is effectively treated as moderate-sedation evidence even though the note says GA and explicitly frames the midazolam line as a nursing typo, not administered sedation.

**Completeness (Recall)**
- Missed procedures: Transbronchial biopsy/forceps biopsy is documented ('forceps x5') but not represented.
- Missed details: BAL volumes (50 mL in / 18 mL out) are not preserved.

**Logic & Coding**
- CPT consistency: 31624/31627/31629/+31654 are supported. 31628 is also supported and is missing.
- Schema / structure: Important recall miss in a peripheral sampling case.

## note_007 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Hallucinations: inspection_findings implies a lesion even though the note says 'no lesion'.
- Mismatch: blvr.target_lobe='Lingula' is too narrow; the note documents a LUL treatment with valves in apicoposterior, anterior, and lingular segments.; number_of_valves=3, but the note documents 4 total valves.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. Suppressing 31634 is appropriate.
- Schema / structure: Usable BLVR extraction, but target and valve count are wrong.

## note_008 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not separately supported with same-session valve placement.
- Mismatch: The note resolves the laterality ambiguity in favor of RUL, but blvr.target_lobe is left blank.; collateral_ventilation_assessment should reflect a negative/no-CV Chartis result.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should not be separately reported.
- Schema / structure: The note explicitly clarifies laterality, but the extraction does not carry that forward.

## note_037 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Selective intubation/endobronchial tamponade with blocker positioning is not modeled as a distinct therapeutic action.
- Missed details: Topical vasoconstrictor use and RUL isolation are not preserved in structured fields.

**Logic & Coding**
- CPT consistency: 31645 is supported for clot extraction/therapeutic aspiration. The tamponade/blocker component is not represented.
- Schema / structure: Reasonable airway-clearance capture with incomplete modeling of hemorrhage-control maneuvers.

## note_002 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: number_of_valves=2, but the note documents 3 RUL valves.; collateral_ventilation_assessment='Chartis indeterminate' softens a clearly negative/no-CV result.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. Suppressing 31634 is appropriate in this same-session BLVR case.
- Schema / structure: Good overall extraction with valve-count drift.

## note_042 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31640 (tumor excision) is a poor fit for removal of necrotic/fungal obstructing material; the note does not describe tumor excision.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Forceps-plus-suction removal technique is not clearly separated from the BAL event.

**Logic & Coding**
- CPT consistency: 31624 is supported. The debulking/removal work is real, but 31640 is not well supported by the note as written.
- Schema / structure: Procedure family is partly right, but the coding logic over-reads the obstructing material as tumor.

## note_021 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 32997 is supported.
- Schema / structure: Excellent WLL extraction.

## note_047 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31640 is not strongly supported; the note describes granulation debulking after stent removal, not tumor excision.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Mucus plugging as part of the indication is not represented in the structured therapeutic detail.

**Logic & Coding**
- CPT consistency: 31638 is defensible for stent removal/revision-style work on an existing airway stent. 31640 is questionable.
- Schema / structure: Good stent-removal recognition, but granulation is treated too much like tumor.

## note_039 — ⚠️ WARNING — 88 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Pass metadata is preserved for 4R but not clearly carried through for station 7.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: The second elastography target and its mixed pattern could be structured more explicitly.

**Logic & Coding**
- CPT consistency: 31652 and 76982 are supported for 2-station EBUS-TBNA with elastography of one initial target.
- Schema / structure: Overall good extraction with minor granularity issues.

## note_029 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31645 is supported.
- Schema / structure: Clean therapeutic aspiration extraction.

## note_027 — ✅ PASS — 91 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Kenalog intralesional injection is not modeled as an adjunct treatment detail.

**Logic & Coding**
- CPT consistency: 31630 is supported for rigid bronchoscopy with balloon dilation of subglottic stenosis.
- Schema / structure: Good core extraction.

## note_012 — ❌ FAIL — 66 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings is pulled from the plan language ('hemoptysis, fever, worsening dyspnea') rather than the procedure findings.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Transbronchial biopsy/TBBx is explicitly performed (x5) and not represented.
- Missed details: Radial view evolution (eccentric to near-concentric) and complete station pass detail are only partly preserved.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31652/+31654 are supported. 31628 is also supported and is missing.
- Schema / structure: Major recall miss in a combined peripheral-plus-EBUS case.

## note_020 — ✅ PASS — 91 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. Suppressing 31634 is appropriate because leak localization is integral to same-session valve placement.
- Schema / structure: Good concise extraction.

## note_022 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings suggests endobronchial obstruction even though the note says there was no endobronchial obstruction.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Planned short-term ICU ventilatory support and recruitment maneuvers are not preserved.

**Logic & Coding**
- CPT consistency: 32997 is supported.
- Schema / structure: WLL extraction is strong overall, with a polarity error in the bronchoscopic survey narrative.

## note_005 — ❌ FAIL — 64 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not separately supported with same-session BLVR valve placement.; diagnostic_bronchoscopy.inspection_findings is pulled from plan text ('hemoptysis/fever/chest pain') rather than procedural findings.
- Mismatch: blvr.target_lobe is missing despite explicit RLL targeting.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Final valve repositioning and tracheobronchomalacia are incompletely structured.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should be suppressed in this same-session BLVR case.
- Schema / structure: Another BLVR case with unsupported dual-coding and poor finding-text sourcing.

## note_034 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Treatment locations (supraglottic and tracheal lesions) are not captured with anatomic specificity.

**Logic & Coding**
- CPT consistency: 31641 is a reasonable match for bronchoscopic destruction/ablation as documented.
- Schema / structure: Core cryotherapy/ablation extraction is acceptable.

## note_041 — ⚠️ WARNING — 85 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Cryoprobe en-bloc extraction versus suction/forceps fragments is not preserved in structured detail.; Right main bronchus and RLL locations are not represented.

**Logic & Coding**
- CPT consistency: 31645 is defensible for airway cast clearance/therapeutic aspiration.
- Schema / structure: Good high-level capture with limited procedural granularity.

## note_003 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not separately supported with same-session BLVR valve placement.
- Mismatch: blvr.target_lobe is missing even though the note explicitly says LLL target.; collateral_ventilation_assessment='Chartis indeterminate' undercalls a note that supports minimal/absent collateral ventilation.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should be suppressed.
- Schema / structure: Same BLVR bundling failure pattern.

## note_032 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Granulation-specific detail and final airway caliber are not quantified.

**Logic & Coding**
- CPT consistency: 31641 is supported for laser relief of stenosis; separate 31630 can remain bundled for same-site dilation.
- Schema / structure: Good extraction.

## note_017 — ❌ FAIL — 64 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not separately supported with same-session endobronchial valve placement for air-leak control.
- Mismatch: number_of_valves=2, but the note documents 3 valves to LUL segmental bronchi.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should be suppressed.
- Schema / structure: Recurring PAL/BLVR bundling and valve-count error.

## note_011 — ❌ FAIL — 70 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Radial EBUS/radial ultrasound confirmation is documented and not represented.; Forceps transbronchial biopsy is documented and not clearly represented as its own sampling family.
- Missed details: Cryobiopsy and forceps counts are not both preserved.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628 are supported. +31654 is also supported by the note and is missing.
- Schema / structure: Important recall loss for radial EBUS and full peripheral sampling stack.

## note_035 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Bronchospasm treated with bronchodilator is not surfaced as a transient intraprocedural event, which is appropriate given Complications: none.

**Logic & Coding**
- CPT consistency: 31660 is supported.
- Schema / structure: Strong thermoplasty extraction.

## note_046 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Transtracheal oxygen catheter exchange is explicitly performed and is not represented.
- Missed details: Established tract exchange and mucous-plugging exclusion are not preserved.

**Logic & Coding**
- CPT consistency: Diagnostic bronchoscopy alone does not capture the main procedural work in this note.
- Schema / structure: Recall failure in a rare but clearly documented exchange procedure.

## note_010 — ✅ PASS — 93 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Brush and TBBx counts are not deeply structured, but the core procedures and station 7 EBUS-TBNA are correct.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31652/+31654 are supported.
- Schema / structure: Good combined peripheral-plus-staging extraction.

## note_016 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: inspection_findings implies a lesion even though the note says 'no lesion'.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Chest-tube bubbling response and segmental target details are not deeply structured.

**Logic & Coding**
- CPT consistency: 31647 is supported. Suppressing 31634 is appropriate for same-session PAL valve placement.
- Schema / structure: Core extraction is good with a narrative polarity error.

## note_014 — ❌ FAIL — 72 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31634 is not supported. The balloon use in the note is for segmental hemostasis during cryobiopsy, not stand-alone Chartis/air-leak assessment.
- Mismatch: Only the RUL target is surfaced under peripheral_tbna; the second peripheral target/workflow (RLL cryobiopsy) is incompletely expressed in target-level structure.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Per-target sample counts and target-specific radial findings are only partially preserved.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31629/31653/+31654 are supported. 31634 is not.
- Schema / structure: Broad recall is good, but the hemostatic balloon maneuver is mis-coded as a separate balloon-occlusion service.

## note_049 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Pleural drain placement is documented in the note, but pleural_procedures.chest_tube is cleared to false.

**Completeness (Recall)**
- Missed procedures: Pleural drain placement is omitted as a performed procedure.
- Missed details: Biopsy count (x6) is not preserved.

**Logic & Coding**
- CPT consistency: 32604 and 76604 are supported. Separate drain coding may be bundled depending approach, but the drain placement should still be represented procedurally.
- Schema / structure: Thoracoscopy is captured, but associated drain placement is dropped from the registry.

## note_038 — ❌ FAIL — 35 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Bronchoscopy is explicitly performed.; Methylene blue evaluation for tracheoesophageal fistula is explicitly performed.
- Missed details: Mid-tracheal posterior wall fistula identification and coordinated GI esophageal instillation are not represented.

**Logic & Coding**
- CPT consistency: Even if no specific intervention code is derived, an empty registry is not supportable.
- Schema / structure: Near-total omission of a clearly performed bronchoscopy evaluation.

## note_045 — ❌ FAIL — 40 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: Bronchoscopic/laryngoscopic vocal-cord motion assessment is explicitly performed.
- Missed details: Paradoxical inspiratory adduction and absence of significant subglottic stenosis are not represented.

**Logic & Coding**
- CPT consistency: Coding is gray, but the performed evaluation itself should still be present in the registry.
- Schema / structure: Another near-empty extraction despite a real performed airway evaluation.
