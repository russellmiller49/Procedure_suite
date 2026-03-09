# Extraction Quality Report

Evaluated **50 notes** from **my_results_batch_6.txt**.

Overall average score: **81.1 / 100**
Status counts: **11 PASS**, **31 WARNING**, **8 FAIL**.

## Cross-file patterns

- Most recurrent precision issue was negation handling: several notes saying no endobronchial lesion/disease were turned into positive inspection findings.
- The next major failure mode was EBUS logic drift, especially dropped sampled stations, inspected_only vs needle_aspiration confusion, and resulting 31652 vs 31653 errors.
- Peripheral target cases still lose granularity: some navigation targets, biopsy locations, and fiducial details were backfilled as Unknown target or garbled non-anatomic text.
- Airway intervention notes showed recurring stent-state confusion (assessment/reposition vs new action) and location errors for stenosis/stent anatomy.
- Coding problems usually cascaded from extraction errors, especially false procedure families (eg, negated brushings/EBBx) and incomplete nodal station capture.

## note_001 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: transbronchial_biopsy location is not populated despite explicit RUL targeting.

**Logic & Coding**
- CPT consistency: 31624/31628/31652 are coherent with BAL + RUL TBBx + 2-station EBUS-TBNA.
- Schema / structure: Good combined parenchymal and mediastinal sampling extraction.

## note_002 — ✅ PASS — 96 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Drainage volume (900 mL) is not preserved.

**Logic & Coding**
- CPT consistency: 32555 is supported for ultrasound-guided thoracentesis.
- Schema / structure: Straightforward pleural extraction with good precision.

## note_003 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Primary indication text is overly long because it absorbs the short narrative sentence.

**Logic & Coding**
- CPT consistency: 31615 and 31645 are consistent with bronchoscopy through a mature tracheostomy with mucus-plug clearance.
- Schema / structure: Accurate simple trach bronchoscopy extraction.

## note_004 — ⚠️ WARNING — 83 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: airway_stent.location is simplified to Right mainstem even though the note describes a stent spanning the distal trachea into the right mainstem.; mechanical_debulking.location includes BI, which is not actually treated as a tumor site in the raw note.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Stent descriptor is only partially captured; brand field is corrupted.

**Logic & Coding**
- CPT consistency: Rigid bronchoscopy with debulking/APC/dilation/stent placement is well supported. Final code selection still needs careful tracheal-versus-bronchial stent family review and same-site 31640/31641 bundling logic.
- Schema / structure: Excellent recall for a complex CAO case, with remaining anatomic/coding nuance errors.

## note_005 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings falsely suggests a lesion statement rather than preserving the explicit "No endobronchial lesion."
- Mismatches: linear_ebus.node_events are left as inspected_only even though the note documents EBUS-TBNA of 11L and 7 with pass counts.

**Completeness (Recall)**
- Missed procedures: Transbronchial forceps biopsy of the peripheral target is documented in the note but not turned on as transbronchial_biopsy.
- Missed details: Station 7 pass count is recorded as 4 in granular detail, but the raw note states 3 passes.

**Logic & Coding**
- CPT consistency: Peripheral sampling codes are mostly supported, but a nodal EBUS code is missed because sampled-vs-inspected logic failed.
- Schema / structure: High-severity EBUS action logic error plus partial recall loss for forceps biopsy.

## note_006 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Could additionally preserve laterality and the initial 320 mL turbid return, but this is minor.

**Logic & Coding**
- CPT consistency: 32557 is consistent with ultrasound-guided 14 Fr pigtail chest tube placement.
- Schema / structure: Strong pleural extraction with correct device and guidance.

## note_007 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: airway_stent_revision.performed=true and CPT 31638 are not supported; the note explicitly says stent revision/repositioning was not required.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: The existing Y-stent is appropriately present as an assessment-only finding, but the JSON redundantly turns on a revision event that never occurred.

**Logic & Coding**
- CPT consistency: 31645 is supported for secretion clearance. Cryotherapy to granulation tissue is documented. 31638 is not supported because no stent revision/repositioning was performed.
- Schema / structure: Classic existing-stent surveillance case partially collapsed into a false revision event.

## note_008 — ❌ FAIL — 57 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: linear_ebus.stations_sampled omits station 7 even though the node table and specimen log document 11R, 4R, and 7.; As a result, billing is downcoded to 31652 instead of 31653.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Granular station detail captures only one station despite a full 3-station EBUS table in the note.

**Logic & Coding**
- CPT consistency: This should support 31653, not 31652, because three nodal stations were sampled.
- Schema / structure: Classic EBUS station-count loss.

## note_009 — ❌ FAIL — 50 / 100

**Accuracy (Precision)**
- Hallucinations: brushings.performed=true and CPT 31623 are not supported; the note explicitly says cytology brushings were not obtained.; endobronchial_biopsy.performed=true and CPT 31625 are not supported; the note explicitly says endobronchial biopsies were not obtained.; diagnostic_bronchoscopy.inspection_findings implies a lesion despite the note stating no focal endobronchial lesion.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: Only 31624 is supported. 31623 and 31625 are unsupported by the raw note.
- Schema / structure: Negation failure creates two false procedure families and false CPTs.

## note_010 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: granular_data.navigation_targets and peripheral/transbronchial target location fields are backfilled with garbled non-anatomic text rather than the LUL target.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Peripheral sampling counts are only partially structured despite explicit TBNA/forceps/TBBx/cryobiopsy counts.; Minor bleeding is encoded with Nashville grade 2 / "Bleeding - Moderate," which feels stronger than the note's "Minor endobronchial bleeding resolved during the note."

**Logic & Coding**
- CPT consistency: 31624/31627/31628/31629/31653/+31654 are coherent with the documented combined peripheral diagnostic and 3-station EBUS staging case. 77012 remains a gray-zone imaging add-on inference from CBCT use.
- Schema / structure: Excellent recall for a complex combined case, but target granularity and bleeding severity are noisy.

## note_011 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings says "tumor" even though the note describes benign-appearing scar stenosis and explicitly says no active infection or tumor.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Pre- and post-dilation lumen caliber are not fully separated into structured outcome fields.

**Logic & Coding**
- CPT consistency: 31641 is defensible for electrocautery relief of bronchial stenosis; dilation is also documented but typically bundled when performed at the same site.
- Schema / structure: Therapeutic family is correct, but narrative polarity incorrectly invents tumor.

## note_012 — ⚠️ WARNING — 77 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31622 is not separately supported in addition to 31615 for bronchoscopy through trach.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: The tracheostomy tube exchange itself is a major documented action but is not represented in the current schema output.
- Missed details: New tube tip position (~2.5 cm above carina) is not preserved as an explicit outcome field.

**Logic & Coding**
- CPT consistency: 31615 is supported for bronchoscopy through trach. The exchange procedure is documented but not represented; separate 31622 is not the right substitute.
- Schema / structure: Good bronchoscopy extraction, but the distinct trach-exchange action is lost.

## note_013 — ⚠️ WARNING — 89 / 100

**Accuracy (Precision)**
- Hallucinations: pleurodesis.indication is set to recurrent benign effusion, which is not supported; the note describes recurrent effusion with pleural nodularity/studding and pleural biopsies, not a benign effusion context.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Pleural biopsy quantity/sites are not richly structured.

**Logic & Coding**
- CPT consistency: 32650 is consistent with medical pleuroscopy plus talc poudrage/pleurodesis. Separate pleural biopsy coding is generally bundled here.
- Schema / structure: Good pleural extraction with a mild indication-label error.

## note_014 — ⚠️ WARNING — 89 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: number_of_valves is recorded as 3 although the note documents four valves deployed to the LUL.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Negative collateral ventilation assessment could be carried more explicitly.

**Logic & Coding**
- CPT consistency: 31647 is consistent with initial lobe valve placement.
- Schema / structure: High-quality BLVR extraction with a small quantity miss.

## note_015 — ⚠️ WARNING — 89 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Final laterality (left) is not surfaced in the structured pleural procedure despite the note explicitly correcting an earlier right-sided documentation error.

**Logic & Coding**
- CPT consistency: 32557 is consistent with ultrasound-guided 12 Fr pigtail chest tube placement.
- Schema / structure: Good extraction overall with a laterality detail omission.

## note_016 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: BAL/brushing/endobronchial/TBBx locations could be more explicitly separated within the structured specimen representation.

**Logic & Coding**
- CPT consistency: 31623/31624/31625/31628 are well supported by the note.
- Schema / structure: Good multi-sampling extraction.

## note_017 — ⚠️ WARNING — 85 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Transient desaturation during dilation is not modeled.

**Logic & Coding**
- CPT consistency: The note clearly supports rigid bronchoscopy with balloon dilation and cryotherapy for stenosis. 31641 is arguable for relief of stenosis by cryotherapy; 31630 is also explicitly suggested by the note header and remains a coding gray zone.
- Schema / structure: Core procedure capture is good; coding hierarchy remains somewhat debatable.

## note_018 — ⚠️ WARNING — 87 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings is corrupted by negation and reads as if tumor or foreign body were identified even though the note says no tumor or foreign body.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31645 is supported for therapeutic aspiration of mucus plugging.
- Schema / structure: Straightforward therapeutic aspiration case with a negation-handling narrative error.

## note_019 — ❌ FAIL — 54 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: linear_ebus.stations_sampled omits station 7 even though the note clearly documents EBUS-TBNA at 4R, 7, and 11R.; linear_ebus.node_events use forceps_biopsy action for nodal sampling, which is not what the note describes.

**Completeness (Recall)**
- Missed procedures: Transbronchial forceps biopsy of the RML target is documented in the note but not turned on as transbronchial_biopsy.
- Missed details: Pass counts for all three nodal stations are incompletely preserved.

**Logic & Coding**
- CPT consistency: 31627/31629/+31654 are supported. EBUS should derive 31653, not 31652, because 3 nodal stations were sampled. A TBBx code is also supported by the raw note.
- Schema / structure: High-severity combined peripheral+EBUS logic failure.

## note_020 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Pleuritic discomfort during instillation is not represented, but this is minor.

**Logic & Coding**
- CPT consistency: 32561 is supported for combined intrapleural alteplase/DNase instillation through an existing catheter.
- Schema / structure: Accurate fibrinolytic extraction.

## note_021 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings says endobronchial abnormality even though the note says the airways were otherwise without endobronchial abnormality.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: BAL location is carried as a long free-text phrase rather than normalized cleanly to LLL.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/31629/+31654 are consistent with the documented robotic peripheral sampling case.
- Schema / structure: Core procedure families are correct; main precision issue is false inspection narrative polarity.

## note_022 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion despite the note saying extrinsic compression without endobronchial lesion.; eus_b.passes=7 is unsupported; the note says station 8 via EUS-B x3 passes.
- Mismatches: linear_ebus.stations_sampled incorrectly includes station 8, which belongs to the separate EUS-B sampling step rather than bronchoscopic EBUS.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31653 is supported for the 3 bronchoscopically sampled stations (11L, 7, 4L), and 43238 is supportable for the separate EUS-B-guided station 8 sample.
- Schema / structure: Main procedures are identified, but the relationship between EBUS and EUS-B targets is blurred.

## note_023 — ⚠️ WARNING — 89 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: airway_stent.location is set to Trachea even though the intended device is the previously placed right mainstem silicone stent; the tracheal prolapse is described, but the final corrected location is right mainstem.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Existing stent material conflict (silicone vs one later covered-metallic phrase) is appropriately not over-normalized, but could be explained more explicitly.

**Logic & Coding**
- CPT consistency: 31638 and 31645 are consistent with stent repositioning/revision and secretion clearance.
- Schema / structure: Strong extraction with only a location nuance.

## note_024 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Instilled/returned lavage volumes and transient desaturation/hypothermia are not represented in structured fields.

**Logic & Coding**
- CPT consistency: 32997 is consistent with whole-lung lavage.
- Schema / structure: Correctly captures whole-lung lavage and avoids BAL confusion.

## note_025 — ✅ PASS — 97 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Volume removed (1250 mL) could be preserved.

**Logic & Coding**
- CPT consistency: 32555 is supported for ultrasound-guided thoracentesis.
- Schema / structure: Clean extraction despite redaction noise.

## note_026 — ⚠️ WARNING — 88 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings is polluted by negated text ("No mass, foreign body, or significant stenosis").
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: BAL location could be normalized more specifically to the posterior segment of the RUL.

**Logic & Coding**
- CPT consistency: 31623 and 31624 are supported.
- Schema / structure: Procedure families are correct; inspection narrative precision is the main issue.

## note_027 — ⚠️ WARNING — 87 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: number_of_valves is recorded as 3 even though the note says four valves were deployed.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Collateral ventilation assessment result (negative) is only implicit rather than richly structured.

**Logic & Coding**
- CPT consistency: 31647 is appropriate for single-lobe valve placement.
- Schema / structure: BLVR extraction is good overall with a minor quantity error.

## note_028 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: The note documents both mechanical debulking and APC of the same tumor site; the coding summary does not clearly explain same-site bundling logic.

**Logic & Coding**
- CPT consistency: Mechanical tumor debulking is clearly supported. Because APC destruction was also performed at the same site, 31640 versus 31641 requires careful same-site bundling logic; the selected stack is not clearly justified from the note alone. 31645 for clot/debris clearance is arguable but could represent work integral to tumor debulking.
- Schema / structure: Therapeutic airway family is correct, but coding rationale is under-explained for same-site debulking/APC work.

## note_029 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Initial drainage volume (1000 mL serous) is not structured.

**Logic & Coding**
- CPT consistency: 32550 is consistent with tunneled pleural catheter placement.
- Schema / structure: Strong IPC extraction with correct side and tunneled status.

## note_030 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings implies endobronchial disease even though the note states "No endobronchial disease."
- Mismatches: navigation_targets.target_location_text and peripheral_tbna.targets_sampled are left as Unknown target despite explicit apicoposterior LUL targeting.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Sampling counts (TBNA x3, forceps biopsy x5) are not preserved in structured fields.; Fiducial placement is captured only in granular navigation detail, not a more specific target/location field.

**Logic & Coding**
- CPT consistency: 31626/31627/31628/31629/+31654 are consistent with the documented guided peripheral sampling and fiducial placement.
- Schema / structure: High-level extraction is good; remaining errors are target specificity and false narrative polarity.

## note_031 — ⚠️ WARNING — 79 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion despite the note stating no endobronchial lesion.; Extra elastography add-on 76983 is not clearly supported; the note describes selective elastography use with station 4R prioritized, not multiple separately billable elastography targets.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Per-station pass counts are not fully preserved in granular detail.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations. One elastography code may be arguable; +76983 is not clearly defended by the note.
- Schema / structure: Main EBUS extraction is correct; adjunct elastography coding is overextended.

## note_032 — ⚠️ WARNING — 88 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: The RLL treated target is not richly structured, and exact lesion size is appropriately left blank because the note says it is not documented.

**Logic & Coding**
- CPT consistency: Navigational peripheral ablation is supported; 31641/77012 remain coding-policy gray zones rather than pure note truth.
- Schema / structure: Therapeutic extraction is reasonable and appropriately avoids inventing the missing lesion size.

## note_033 — ❌ FAIL — 40 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion despite the note saying no central endobronchial lesion.
- Mismatches: The note documents pulsed electric field ablation of a peripheral lesion, but the JSON never turns on peripheral_ablation and the CPT output collapses to 77012 only.

**Completeness (Recall)**
- Missed procedures: Peripheral ablation / bronchoscopic treatment of the known peripheral adenocarcinoma is completely missed.
- Missed details: Trace apical pneumothorax is captured, but the treated lesion/lobe is not surfaced as a therapeutic target event.

**Logic & Coding**
- CPT consistency: Ablation work is the key procedure here; 77012 alone is not an adequate coding summary.
- Schema / structure: High-severity therapeutic omission.

## note_034 — ✅ PASS — 91 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Transient bronchospasm is omitted from complication detail.

**Logic & Coding**
- CPT consistency: 31624 and 31645 are both supported by therapeutic clearance followed by diagnostic BAL.
- Schema / structure: Correct BAL-versus-therapeutic-aspiration separation.

## note_035 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31640 (tumor excision) is not well supported; the note describes benign tracheal granulation tissue debridement with cryotherapy, not tumor excision.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Tracheal narrowing severity (~60%) and improvement after intervention are not carried into explicit outcome fields.

**Logic & Coding**
- CPT consistency: 31615 is supportable because bronchoscopy was performed through an established tracheostomy stoma. 31640 is questionable; destruction/debulking language is present, but not tumor excision.
- Schema / structure: Performed procedures are mostly captured, but coding overcalls tumor excision.

## note_036 — ⚠️ WARNING — 79 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Drainage volume (780 mL) is not preserved.; Standalone chest ultrasound may be overinterpreted for separate 76604 billing if it only served as thoracentesis guidance.

**Logic & Coding**
- CPT consistency: 32555 is supported. Separate 76604 is a documentation/coding gray zone rather than clearly supported from this short note.
- Schema / structure: Procedure extraction is good; billing may over-separate the ultrasound.

## note_037 — ⚠️ WARNING — 81 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion/mass despite the note stating no visible endobronchial lesion.; peripheral_tbna.performed=true is spuriously turned on in an EBUS-only case.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Pass counts are stated in the note but not fully preserved in granular station detail.

**Logic & Coding**
- CPT consistency: 31653 is correct for 3 sampled stations (10R, 7, 4R).
- Schema / structure: EBUS staging logic is correct at the top level, but an unrelated peripheral TBNA family was falsely activated.

## note_038 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: cryotherapy.performed=true is not separately supported; the note documents cryoablation of a peripheral lesion, not bronchoscopic cryotherapy/debulking.; diagnostic_bronchoscopy.inspection_findings implies endobronchial bleeding despite the note stating no significant endobronchial bleeding.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: Navigational peripheral ablation is supported. 31641/77012 remain payer-policy gray-zone conclusions rather than note-derived certainty.
- Schema / structure: Main therapeutic family is captured, but a separate cryotherapy family is spuriously turned on.

## note_039 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: Therapeutic aspiration / secretion-clearance work is documented but not represented as its own procedure family.; Existing stent assessment is implicit in the note but not surfaced as a stent-management event.
- Missed details: None

**Logic & Coding**
- CPT consistency: APC treatment of granulation tissue is supported. 31645 may also be defensible because retained secretions were a major treated problem.
- Schema / structure: Core thermal treatment is captured, but retained-secretion/stent-management context is incompletely represented.

## note_040 — ✅ PASS — 93 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Instilled/returned whole-lung lavage volumes are not surfaced in structured fields.; Transient hypotension is omitted from complication detail despite being documented.

**Logic & Coding**
- CPT consistency: 32997 is consistent with whole-lung lavage for pulmonary alveolar proteinosis.
- Schema / structure: Correctly distinguishes whole-lung lavage from BAL.

## note_041 — ❌ FAIL — 66 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: Ultrasound guidance is documented in the note, but pleural_procedures.thoracentesis lacks guidance and billing is downcoded to 32554 instead of 32555.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Volume removed (1350 mL) is not preserved.

**Logic & Coding**
- CPT consistency: This should support 32555, not 32554, because the note explicitly describes US-guided thoracentesis.
- Schema / structure: Core procedure family is right, but imaging-guidance extraction failed and cascaded into wrong CPT.

## note_042 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Pass counts for station 11L and 7 are not preserved in node_events.; The biopsy-related bleeding is represented, but severity may be somewhat strong relative to the note's "minimal bleeding" wording.

**Logic & Coding**
- CPT consistency: 31625 and 31652 are supported by the raw note.
- Schema / structure: Good combined endobronchial biopsy plus 2-station EBUS extraction.

## note_043 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: CPT 31622 is not separately supported; the note is a bronchoscopy through an established tracheostomy and is already represented by 31615.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Tube-tip position 2 cm above carina and absence of false passage could be preserved more explicitly as airway outcome detail.

**Logic & Coding**
- CPT consistency: 31615 is supported. Separate diagnostic bronchoscopy coding is bundled/not separately defensible here.
- Schema / structure: Procedure extraction is fine; coding stacks an unnecessary diagnostic bronchoscopy.

## note_044 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: granular_data assigns atypical-cell ROSE to station 4R, but the note says atypical cells came from station 7.
- Mismatches: linear_ebus.node_events is empty despite two clearly sampled stations.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31652 is correct for two sampled stations (7 and 4R).
- Schema / structure: Top-level EBUS extraction is acceptable, but granular event detail is incomplete and partly misassigned.

## note_045 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings implies an endobronchial lesion despite the note saying no visible endobronchial lesion.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Peripheral sampling counts are not deeply structured.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/31629/+31654 are consistent with the note.
- Schema / structure: Good peripheral sampling extraction with a false-positive inspection narrative.

## note_046 — ❌ FAIL — 56 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings says endobronchial tumor even though the note says no central endobronchial tumor.; Bleeding is overstated as severe / Nashville grade 3 despite the note describing minor bleeding after cryobiopsy resolved with tamponade and suction.
- Mismatches: linear_ebus.stations_sampled collapses to 4R only even though the note documents sampling of both 4R and 7.; linear_ebus.node_events misclassifies nodal aspiration as forceps_biopsy and drops station 7 from the structured event log.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Peripheral target locations remain Unknown target despite explicit RUL targeting.; Three fiducials were deployed, but fiducial quantity is not preserved.

**Logic & Coding**
- CPT consistency: 31626/31627/31628/31629/+31654 are supported. 31652 is correct for two sampled nodal stations, but the nodal event detail itself is internally wrong.
- Schema / structure: Major logic problems in EBUS event typing plus a clear complication severity overcall.

## note_047 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: pleural_procedures.chest_tube.action="Repositioning" is not supported; the note says the existing catheter remained intrapleural and patent after flush, not repositioned.
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 32561 is supported for intrapleural tPA/DNase therapy. Separate 76604 may be reasonable because pleural ultrasound was a named procedure and yielded a distinct loculation assessment, but it remains documentation-sensitive.
- Schema / structure: Good fibrinolytic extraction, but the existing-tube state is overstated as a repositioning action.

## note_048 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatches: None

**Completeness (Recall)**
- Missed procedures: None
- Missed details: The note documents a tiny trace pneumothorax, but complications are left empty.

**Logic & Coding**
- CPT consistency: Peripheral ablation is supported. The use of 31641 and 77012 for bronchoscopic peripheral ablation remains a payer/policy gray zone, but the extraction itself does identify navigational bronchoscopy and RFA.
- Schema / structure: Therapeutic extraction is good; complication recall is partial.

## note_049 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: airway_dilation.location and airway_stent.location are set to RUL, but the note repeatedly localizes the stenosis and stent to the bronchus intermedius.; diagnostic_bronchoscopy.airway_abnormalities includes Secretions without note support.
- Mismatches: airway_dilation.target_anatomy="Stent expansion" is unsupported; dilation treated the bronchus intermedius stenosis.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: Bronchus intermedius target anatomy is not preserved in structured location fields.

**Logic & Coding**
- CPT consistency: 31636 is supported for covered bronchial stent placement; dilation is documented but commonly bundled into the stent service at the same site.
- Schema / structure: Core procedure family is correct, but location logic is materially wrong.

## note_050 — ⚠️ WARNING — 83 / 100

**Accuracy (Precision)**
- Hallucinations: diagnostic_bronchoscopy.inspection_findings is mangled by a negated sentence and reads as if an endobronchial biopsy was performed.
- Mismatches: BAL location is malformed ("the LLL with") rather than cleanly normalized to LLL.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31624 is supported for LLL BAL.
- Schema / structure: Simple case extracted reasonably well, but negation handling corrupts the inspection narrative.
