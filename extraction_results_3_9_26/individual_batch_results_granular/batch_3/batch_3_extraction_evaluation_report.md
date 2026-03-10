# Extraction Quality Report
Evaluated **50 notes** across **1 batch-output file**.
Overall average score: **64.3 / 100**
Status counts: **5 PASS**, **14 WARNING**, **31 FAIL**.
## Cross-file patterns
- Repeated **T-tube / tracheostomy errors**: routine trach exchanges and PDT notes were often coded as standalone bronchoscopy (31615/31622) or lost the primary tracheostomy/trach-change procedure entirely.
- Frequent **Montgomery T-tube under-extraction**: insertion/exchange cases often captured laser+dilation but missed the defining T-tube placement/removal/replacement event, or mislabeled it as stent revision (31638) rather than new placement logic.
- Multiple cases showed **false or overstated complications**, especially bleeding severity inflation (minor/expected ooze → moderate/severe complication) and one false pneumothorax inferred from monitoring language.
- Several EBUS notes had **station/action logic failures**, including hallucinated sampled stations (for example false 3P or 4L) or copied ROSE results, with direct downstream CPT impact (most notably **31652 vs 31653**).
- There was recurrent **airway-clearance confusion**: mucus-plug/clot extraction or T-tube toileting was often missed as therapeutic aspiration, while other cases overcalled 31645 from incidental suctioning.
- Pleural cases often had **bundling / procedure-family collapse**: pleural biopsy and thoracoscopy details were lost, pleurodesis was hallucinated when deferred, or chest-tube/thoracentesis codes were not aligned with the documented guidance and context.

## my_results_batch_3.txt

### note_033 — ❌ FAIL — 12 / 100

**Accuracy (Precision)**
- Hallucination: BLVR/valve placement is entirely unsupported. The note is a routine tracheostomy tube exchange with stomal granulation treated by silver nitrate, not bronchoscopic lung-volume reduction.
- Hallucination: CPT 31615 and 31647 are unsupported by the note.
- Mismatch: established_tracheostomy_route=true is used to derive bronchoscopy coding even though no bronchoscopy is documented.

**Completeness (Recall)**
- Missed procedure: Tracheostomy tube exchange is the primary performed procedure and is not represented.
- Missed procedure: Stomal granulation treatment with silver nitrate is not represented.
- Missed detail: New tube type/size (Bivona 7.0 TTS), guide-catheter exchange technique, and absence of complication are omitted.

**Logic & Coding**
- CPT consistency: 31615 and 31647 are not supported; the note describes tracheostomy tube exchange with local granulation cautery, not bronchoscopy or valve placement.
- Schema / structure: High-severity wrong procedure family with near-total loss of the real procedure.

### note_007 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Right side, drained volume (1,050 mL), and specimen panel could be more granular.

**Logic & Coding**
- CPT consistency: 32555 is consistent with ultrasound-guided thoracentesis.
- Schema / structure: Core pleural extraction is accurate and internally coherent.

### note_038 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The note clearly documents Montgomery T-tube insertion, but no airway-stent/T-tube placement object is present.

**Completeness (Recall)**
- Missed procedure: T-tube insertion is a major performed procedure and is omitted.
- Missed detail: T-tube size (13 × 60 × 30 mm), stoma creation at ring 2–3, and flexible confirmation are not captured as stent details.

**Logic & Coding**
- CPT consistency: 31641 is supported for laser treatment, but the extraction misses the separately documented T-tube placement logic raised in the note (31631-22 / 31899 discussion).
- Schema / structure: Good capture of laser+dilation, but the defining therapeutic device placement is absent.

### note_011 — ❌ FAIL — 52 / 100

**Accuracy (Precision)**
- Hallucination: Station 3P is hallucinated from the specimen label '4L node (3p)'; only stations 4L and 7 were sampled by EBUS.
- Mismatch: Sedation is set to Moderate even though the note documents General anesthesia with LMA/TIVA.
- Mismatch: 31653 is upcoded from the false third station; the note supports 31652 for 2 sampled stations.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: LLL B6 target detail and BAL location are only partially structured.

**Logic & Coding**
- CPT consistency: 31624, 31627, 31628, and +31654 are supported. Linear EBUS should derive 31652, not 31653.
- Schema / structure: Classic nodal-station hallucination causing downstream CPT inflation.

### note_013 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucination: Therapeutic aspiration/31645 is not clearly required by the note; secretion clearance may be incidental toileting during a navigational case.
- Mismatch: Complication severity is overstated as moderate bleeding when the note describes mild post-cryobiopsy hemorrhage controlled endoscopically.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Sedation/general anesthesia details are not surfaced in the registry section.

**Logic & Coding**
- CPT consistency: 31623, 31624, 31627, 31628, and +31654 are supported. 31645 is gray-zone and overcalled here.
- Schema / structure: Peripheral sampling is largely correct, but aspiration and bleeding severity are too aggressive.

### note_029 — ❌ FAIL — 35 / 100

**Accuracy (Precision)**
- Hallucination: established_tracheostomy_route=true and CPT 31615 are unsupported; this note is percutaneous tracheostomy placement, not bronchoscopy through an established trach.
- Mismatch: The note documents percutaneous tracheostomy, but deterministic coding suppresses 31600 and substitutes bronchoscopic codes.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Modified Griggs/GWDF technique, ultrasound co-guidance, and extended-length Portex/Shiley selection are not surfaced cleanly.

**Logic & Coding**
- CPT consistency: 31600 is the supported primary procedure. 31615/31622 are not defensible from the note as selected.
- Schema / structure: Procedure presence is partly right, but coding logic is inverted by false established-trach reasoning.

### note_017 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Hallucination: The registry treats this as BLVR, but the note is valve placement for postoperative bronchopleural fistula/persistent air leak, not lung-volume reduction.
- Hallucination: number_of_valves=9 is unsupported; the note documents 3 valves.
- Mismatch: Sedation is set to General though the note explicitly clarifies Moderate sedation.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Individual segmental valve placements (RUL B1, B3, B2) are not represented.

**Logic & Coding**
- CPT consistency: 31647 is compatible with documented valve placement, but the extraction misclassifies the indication/procedure family and inflates valve count.
- Schema / structure: Core device placement is recognized, but the wrong therapeutic family is applied.

### note_024 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Bleeding is promoted to a moderate complication although the note describes mild diffuse mucosal hemorrhage controlled with cold saline.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: RUL B2 target granularity and biopsy count (x4) are not deeply structured.

**Logic & Coding**
- CPT consistency: 31624 and 31628 are supported.
- Schema / structure: Good bronchoscopy/BAL/TBBX capture with only complication-severity inflation.

### note_009 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucination: Station 7 is labeled malignant by ROSE in the JSON, but the note says station 7 ROSE showed atypical cells.
- Hallucination: Station 10R is mislabeled as forceps_biopsy; the note documents TBNA x2.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Minor hemorrhage is coded more aggressively than documented.

**Logic & Coding**
- CPT consistency: 31623, 31625, and 31653 are supported by the raw note.
- Schema / structure: Procedure families are correct, but nodal event action/outcome logic is wrong.

### note_014 — ❌ FAIL — 74 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The note's main therapeutic work is mucus plug extraction and lavage, but therapeutic aspiration is not represented.

**Completeness (Recall)**
- Missed procedure: Therapeutic aspiration / mucus plug extraction from the RLL bronchus intermedius-RLL junction is missed.
- Missed detail: BAL site and mucus-cast extraction passes are not structured.

**Logic & Coding**
- CPT consistency: 31624 is supported, but the note also supports therapeutic airway clearance work beyond BAL.
- Schema / structure: Under-calls the therapeutic component of the bronchoscopy.

### note_022 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucination: inspection_findings lose negation and read as if there were an endobronchial abnormality, though the note says none.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Bilateral BAL sites (RLL and LLL) could be carried more explicitly.

**Logic & Coding**
- CPT consistency: 31624 is supported.
- Schema / structure: Usable extraction with only minor narrative polarity noise.

### note_031 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Separate diagnostic bronchoscopy coding is likely overcalled in a PDT note where bronchoscopy is guidance rather than a standalone diagnostic service.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Ultrasound co-guidance and corrected ring 2–3 entry planning are not surfaced.

**Logic & Coding**
- CPT consistency: 31600 is supported. Separate 31622 is not clearly defensible from this documentation.
- Schema / structure: Percutaneous tracheostomy is captured, but coding remains too bronchoscopy-centric.

### note_036 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Montgomery T-tube insertion is documented, but no airway-stent/T-tube placement object is present.

**Completeness (Recall)**
- Missed procedure: T-tube insertion is omitted.
- Missed detail: Balloon size, T-tube device details, and stoma-sidearm configuration are not captured.

**Logic & Coding**
- CPT consistency: 31641 is supported for Nd:YAG treatment, but the defining T-tube placement component is not reflected.
- Schema / structure: Same pattern as other T-tube insertions: device placement is lost.

### note_010 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucination: airway_stent.action_type='revision' is unsupported; the note documents new Y-stent placement.
- Mismatch: Stent brand/type details are wrong (Dumon Y-stent vs generic 'ENT').
- Mismatch: CPT 31638 is selected instead of placement logic for new tracheal stent placement.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Y-stent limb diameters/lengths and >90% post-stent patency are not preserved.

**Logic & Coding**
- CPT consistency: 31631 and 31641 are the defensible codes from the note. 31638 is not.
- Schema / structure: Core therapeutic intent is right, but stent action-type and coding are materially wrong.

### note_016 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Fibrinolytic plan is future care, not same-day treatment, and is appropriately not turned on.

**Logic & Coding**
- CPT consistency: 32557 is consistent with ultrasound-guided 14 Fr chest tube placement.
- Schema / structure: Accurate pleural drainage extraction.

### note_035 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucination: airway_stent.action_type='revision' and CPT 31638 are unsupported for this note; it documents new Montgomery T-tube insertion.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: T-tube sizing and tracheomalacia-bridge rationale are incompletely represented.

**Logic & Coding**
- CPT consistency: 31641 is supported for laser. The T-tube/device placement is captured only partially and is coded as revision rather than insertion.
- Schema / structure: Better than the other T-tube insertions because a stent object exists, but the action logic is still wrong.

### note_045 — ❌ FAIL — 62 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The note documents re-expansion pulmonary edema, but no complication structure is surfaced.
- Mismatch: CPT is downcoded to 32554 even though the note documents ultrasound guidance.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Drained volume (1,650 mL), left-sided location, and O2-responsive REPE management are not structured.

**Logic & Coding**
- CPT consistency: 32555 is supported by the note. 32554 is not.
- Schema / structure: Procedure presence is correct, but the major complication is missed.

### note_042 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Chest-tube coding is not cleanly aligned with the note's emergent tube thoracostomy language (the note itself points toward 32551-style work, not 32556).

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: General anesthesia is not surfaced in sedation.

**Logic & Coding**
- CPT consistency: 31623, 31624, 31627, 31628, and +31654 are supported. The emergent pneumothorax management/chest-tube code selection is the weak point.
- Schema / structure: Good core peripheral bronchoscopy extraction with appropriate recognition of the true complication.

### note_002 — ⚠️ WARNING — 88 / 100

**Accuracy (Precision)**
- Hallucination: inspection_findings lose negation and imply an endobronchial mass despite the note stating no discrete endobronchial mass.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: RLL B7/B8 localization is not preserved.

**Logic & Coding**
- CPT consistency: 31624 is defensible because BAL was collected from the RLL.
- Schema / structure: Core extraction is good with only a negation/polarity error.

### note_041 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucination: Station 10R is marked malignant in the JSON, but the note only gives malignant ROSE for station 4R; 10R was hemorrhagic/contaminated.
- Hallucination: 31641 is not a clean fit for hemorrhage-control bronchoscopy in this note.
- Mismatch: Sedation is collapsed to General even though the note clearly documents a moderate-sedation start with emergent conversion to GA.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Fogarty balloon tamponade is clinically important but not represented as a distinct hemostatic maneuver.

**Logic & Coding**
- CPT consistency: 31500 and 31652 are supported. The therapeutic hemorrhage-control coding selected via 31641 is not well supported by the documentation.
- Schema / structure: Major complication handling is recognized, but nodal outcome and CPT logic are wrong.

### note_003 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucination: A pneumothorax complication is created from 'post-procedure CXR ordered / monitor for PTX' language even though the note states no intraoperative complication.
- Hallucination: Locations for brushings/biopsy are malformed and lifted from narrative fragments.
- Mismatch: Radial EBUS view is labeled Adjacent even though the note says concentric ring.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: LUL target segment (LB1+2) is not cleanly structured.

**Logic & Coding**
- CPT consistency: 31623, 31624, 31627, 31628, and +31654 are supported.
- Schema / structure: High-level procedure recall is good, but false complication derivation is a material error.

### note_008 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucination: Bleeding is promoted to a moderate formal complication even though the note describes expected grade I laceration and bleeding controlled with cold saline.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Pre/post lumen caliber and serial dilation details are only partly structured.

**Logic & Coding**
- CPT consistency: 31641 is defensible for laser relief of stenosis. Separate dilation coding is not clearly required from the same-site documentation.
- Schema / structure: Reasonable airway-therapy extraction with complication inflation.

### note_021 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Pass attribution across 10L vs 4L is not completely clean given the note's own inconsistent follow-up-pass wording.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Individual pass counts for 4R, 7, and 10R are not carried into node_events.

**Logic & Coding**
- CPT consistency: 31624 and 31653 are supported by the raw note.
- Schema / structure: Overall high recall and correct station count, but quantitative node detail is incomplete.

### note_015 — ❌ FAIL — 62 / 100

**Accuracy (Precision)**
- Hallucination: Station 11L is treated as sampled even though the note says it was not visualized.
- Hallucination: peripheral_tbna is unsupported; the peripheral phase documents TBBX, brushings, and BAL, not peripheral TBNA.
- Mismatch: EUS-B adrenal passes/gauge are wrong (note: 19G, 3 passes; JSON: 21G and 14 passes).

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Station 2R/4R/4L/7 pass counts are not preserved accurately.

**Logic & Coding**
- CPT consistency: 31653, 31623, 31624, 31627, 31628, and +31654 are broadly supported. The transesophageal adrenal sampling is real, but the extracted EUS-B granular details and code choice are unreliable.
- Schema / structure: Good broad recall, but several target-relationship fields are hallucinated or corrupted.

### note_004 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucination: 31645 is not clearly supported; secretion suctioning is incidental in a major tumor-debulking case.
- Mismatch: airway_dilation location is wrong (RMB stenotic tumor site, not RUL).
- Mismatch: Coding selects 31640 but misses the same-site APC/electrocautery destruction logic where 31641 is the stronger code.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Pre/post patency (70% obstruction to ~80% patency) is not preserved as outcome data.

**Logic & Coding**
- CPT consistency: 31641 best matches the documented therapeutic work. 31640 may be arguable mechanically, but same-site destruction work makes the selected 31640/31645 stack weak.
- Schema / structure: Therapeutic families are broadly recognized, but coding logic does not match the documented intervention mix.

### note_050 — ❌ FAIL — 40 / 100

**Accuracy (Precision)**
- Hallucination: airway_stent.performed=true and CPT 31638 are unsupported; the note explicitly says covered stent was evaluated and deferred.
- Hallucination: Bleeding is hallucinated as severe/Nashville 4 even though the note describes mild biopsy-site ooze controlled with cold saline.
- Mismatch: Sedation is set to Moderate though the patient remained on baseline ICU propofol/fentanyl and no additional procedural sedation was given.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: BAL volumes from both lobes and bilateral TBBX lobe accounting are only partly structured.

**Logic & Coding**
- CPT consistency: 31624, 31628, and +31632 are supported. 31638 is not.
- Schema / structure: Major false-positive stent management and false severe complication make this a clear fail.

### note_001 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: inspection_findings are slightly malformed because diagnosis text bleeds into the inspection narrative.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: ROSE details could be more explicit per station.

**Logic & Coding**
- CPT consistency: 31653 is correct for sampling 4R, 7, and 11R.
- Schema / structure: Strong EBUS extraction with only minor text-noise contamination.

### note_012 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: procedures_performed is empty even though the note clearly documents flexible bronchoscopy through the tracheostomy.

**Completeness (Recall)**
- Missed procedure: Granulation tissue treatment with silver nitrate is omitted.
- Missed detail: Trach position details (tip 3 cm above carina) and negative bleeding source are not reflected in structured bronchoscopy fields.

**Logic & Coding**
- CPT consistency: 31615 is supported by the note.
- Schema / structure: Coding is better than the registry body; the bronchoscopy itself should have been surfaced in performed procedures.

### note_048 — ❌ FAIL — 65 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The note's primary therapeutic action is mucus-cast extraction, but only BAL is represented.

**Completeness (Recall)**
- Missed procedure: Therapeutic aspiration / mucus plug extraction is missed.
- Missed detail: LUL target and forceps-extraction passes are not preserved.

**Logic & Coding**
- CPT consistency: The note supports therapeutic aspiration/airway clearance work in addition to any lavage. A BAL-only coding stack is incomplete.
- Schema / structure: Under-calls the reason for bronchoscopy in an airway-clearance case.

### note_026 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Separate bronchoscopy coding (31622) is not clearly defensible in a PDT note.
- Mismatch: Sedation is labeled Moderate despite propofol/fentanyl/rocuronium procedural anesthesia.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Device/tube position confirmation details are not richly structured.

**Logic & Coding**
- CPT consistency: 31600 is supported; separate 31622 is questionable.
- Schema / structure: Good procedural recall with residual coding inflation.

### note_032 — ❌ FAIL — 48 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The note is primarily a mature-tract tracheostomy tube exchange, but the registry surfaces only bronchoscopy coding.

**Completeness (Recall)**
- Missed procedure: Tracheostomy tube exchange is omitted as the main performed procedure.
- Missed detail: New tube size/type (Shiley 6.0 cuffless) and safe-over-guide exchange technique are not represented.

**Logic & Coding**
- CPT consistency: 31615 may be supportable for bronchoscopic confirmation through the mature trach, but the primary tube-exchange work is missing and 31622 is not supported separately.
- Schema / structure: Bronchoscopic confirmation is captured, but the actual exchange procedure is lost.

### note_034 — ❌ FAIL — 35 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Only bronchoscopy is surfaced, despite a difficult immature-tract trach reinsertion/exchange being the main intervention.

**Completeness (Recall)**
- Missed procedure: Tracheostomy tube reinsertion/exchange in an immature tract is omitted.
- Missed procedure: Backup emergent orotracheal intubation documented in the note is not represented.
- Missed detail: Stepwise smaller-to-larger trach exchange (5.0 then 7.0 over Aintree) is omitted.

**Logic & Coding**
- CPT consistency: A tracheostomy-tube-change/reinsertion code is more aligned with the note than a standalone 31622-only result.
- Schema / structure: Major recall failure in a difficult airway rescue/exchange case.

### note_049 — ❌ FAIL — 70 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: BAL volume is corrupted (3 mL from epinephrine instillation rather than BAL volume).

**Completeness (Recall)**
- Missed procedure: Therapeutic clot extraction/airway clearance is not represented as a procedure family.
- Missed detail: Active RUL B2 hemorrhage localization and cold-saline hemostasis are incompletely structured.

**Logic & Coding**
- CPT consistency: BAL is supported, but the note also documents therapeutic clot extraction and hemorrhage control that are not reflected in the coding stack.
- Schema / structure: Good localization of hemorrhage, but procedure recall is incomplete.

### note_040 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Montgomery T-tube insertion is documented, but no airway-stent/T-tube placement object is present.

**Completeness (Recall)**
- Missed procedure: T-tube insertion is omitted.
- Missed detail: Device size (11 × 60 × 25), stoma creation, and sidearm/carina relationship are not represented.

**Logic & Coding**
- CPT consistency: 31641 is supported for laser. The defining T-tube placement piece is missing from extraction/coding.
- Schema / structure: Same major omission pattern as the other T-tube insertion notes.

### note_039 — ❌ FAIL — 28 / 100

**Accuracy (Precision)**
- Hallucination: thermal_ablation/31641 are unsupported; the note describes routine T-tube exchange with cold-forceps trimming of small stomal granulation, not thermal ablation.
- Mismatch: airway_stent is left false even though this is removal of an old T-tube and insertion of a new T-tube.

**Completeness (Recall)**
- Missed procedure: T-tube removal and replacement are both omitted.
- Missed detail: New tube size, identical repositioning, and flexible confirmation via sidearm are not represented.

**Logic & Coding**
- CPT consistency: A T-tube exchange/removal-replacement construct is supported; 31641 is not.
- Schema / structure: Near-total failure on the actual device-management work.

### note_043 — ❌ FAIL — 66 / 100

**Accuracy (Precision)**
- Hallucination: The complication is converted into severe bleeding/Nashville 4, but the documented complication is posterior tracheal wall laceration with only minimal ooze.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Bronchoscopic guidance and the actual laceration complication type are not represented explicitly.

**Logic & Coding**
- CPT consistency: 31600 is supported. The omitted/incorrect issue is complication modeling, not the primary procedure.
- Schema / structure: Primary PDT extraction is acceptable, but the complication family is wrong.

### note_030 — ❌ FAIL — 38 / 100

**Accuracy (Precision)**
- Hallucination: intubation/31500 is unsupported; the patient was already intubated and the note describes ETT withdrawal, not a separate emergency intubation.
- Hallucination: 31615 is unsupported; this is not bronchoscopy through an established tracheostomy route.
- Mismatch: Percutaneous tracheostomy is present, but coding is dominated by extra bronchoscopic codes.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Post-trach bronchoscopy confirmation is present but does not justify the selected standalone bronchoscopic code stack.

**Logic & Coding**
- CPT consistency: 31600 is the supported primary procedure. 31500, 31615, and separate 31622 are not supported as selected.
- Schema / structure: High-severity CPT inflation around an otherwise straightforward PDT.

### note_025 — ❌ FAIL — 42 / 100

**Accuracy (Precision)**
- Hallucination: airway_stent is coded as revision/31638, but the note documents new covered SEMS placement across a TEF.
- Hallucination: 31640 is not the right code concept for APC treatment of granulation tissue around a fistula.
- Mismatch: mechanical_debulking/therapeutic_aspiration are over-emphasized relative to the dominant stent-placement work.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Covered SEMS brand/diameter/length and pre/post patency/coverage metrics are not faithfully structured.

**Logic & Coding**
- CPT consistency: 31631 and 31641 are supported. The selected 31638/31640/31645 stack is not.
- Schema / structure: Major stent-action and CPT-family errors in a complex TEF case.

### note_018 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucination: Station 4L is falsely treated as sampled even though the note says 4L was not identified.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Needle gauge and full per-station ROSE detail are not structured.

**Logic & Coding**
- CPT consistency: 31653 is still defensible because 4R, 7, and 11L were sampled. The problem is the unsupported extra station, not the final nodal count.
- Schema / structure: A wrong station is a serious precision error even though the headline code remains correct.

### note_019 — ❌ FAIL — 45 / 100

**Accuracy (Precision)**
- Hallucination: pleurodesis.performed=true and CPT 32650 are unsupported; the note explicitly says pleurodesis was deferred pending pathology.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Pleural biopsy is a core performed procedure and is not represented.
- Missed detail: Six parietal/diaphragmatic biopsies and ~600 mL drainage are omitted from structured fields.

**Logic & Coding**
- CPT consistency: The note supports medical thoracoscopy/pleuroscopy with pleural biopsies. 32650 for pleurodesis is not supported.
- Schema / structure: Misses the main diagnostic tissue-acquisition event and hallucinates pleurodesis.

### note_020 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucination: 31640 is not well supported; the note describes minimal granulation trimming rather than tumor excision.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Stent removal/re-use/repositioning sequence could be represented more explicitly.

**Logic & Coding**
- CPT consistency: 31638 is defensible for stent revision/repositioning. 31645 is arguable from mucus clearance. 31640 is the weak code.
- Schema / structure: Good overall recognition of stent management with some coding excess.

### note_028 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Sedation remains labeled Moderate despite propofol infusion plus paralytic and the note's explicit documentation conflict.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Minor platelet-related ooze and intraoperative platelet transfusion are not richly modeled.

**Logic & Coding**
- CPT consistency: 31600 is supported. Separate 31622 remains questionable.
- Schema / structure: Procedural recall is good, but coding and anesthesia normalization are imperfect.

### note_006 — ❌ FAIL — 30 / 100

**Accuracy (Precision)**
- Hallucination: CPT 31573 is entirely unsupported.
- Hallucination: Thoracentesis is over-selected as a standalone code in a thoracoscopy/biopsy/pleurodesis session.
- Mismatch: The note documents pleural biopsies x6, but pleural_biopsy is missing.
- Mismatch: The procedure is collapsed into 32650 even though the note separately documents medical thoracoscopy, pleural biopsy, talc pleurodesis, and chest tube placement.

**Completeness (Recall)**
- Missed procedure: Pleural biopsy is omitted as a performed procedure.
- Missed detail: Talc dose, pleural fluid chemistry specimen, and loculation breakdown are incompletely surfaced.

**Logic & Coding**
- CPT consistency: The note supports medical thoracoscopy with pleural biopsies, talc pleurodesis, and chest tube placement. 31573 is not supported, and the billing stack is materially unreliable.
- Schema / structure: Major pleural-procedure under-modeling with nonsensical coding.

### note_047 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Sedation is labeled Moderate even though no additional procedural sedation was given beyond baseline ICU infusions.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Serial BAL aliquot progression and bilateral site detail could be more explicit.

**Logic & Coding**
- CPT consistency: 31624 is supported for serial BAL confirming DAH.
- Schema / structure: Good extraction of a BAL-only ICU bronchoscopy.

### note_005 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucination: airway_abnormalities include extrinsic compression despite the note stating no extrinsic compression.
- Mismatch: BAL volume_instilled_ml is corrupted to 2 mL from topical lidocaine instead of the documented 60 mL BAL.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: RLL B10 target detail and biopsy pass count are only coarsely represented.

**Logic & Coding**
- CPT consistency: 31624 and 31625 are supported.
- Schema / structure: Strong core extraction with a quantitative BAL-field error and a negation miss.

### note_023 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucination: Severe bleeding/Nashville 3 is unsupported; the note describes minimal self-limited post-biopsy bleeding and mild hemoptysis that resolved before discharge.
- Mismatch: inspection_findings are populated with post-procedure hemoptysis rather than airway findings.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: RML B5 target detail and cryobiopsy cycle details are only partly structured.

**Logic & Coding**
- CPT consistency: 31623, 31624, 31627, 31628, and +31654 are supported.
- Schema / structure: Core peripheral bronchoscopy extraction is good, but complication severity is materially overstated.

### note_027 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Separate 31622 coding is not clearly supported beyond bronchoscopic guidance of the PDT.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Extended-length Shiley XLT selection and confirmation detail are not surfaced.

**Logic & Coding**
- CPT consistency: 31600 is supported. 31622 is questionable as separately reportable guidance.
- Schema / structure: Good bedside PDT extraction with mild coding inflation.

### note_037 — ❌ FAIL — 60 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Montgomery T-tube placement is documented but no airway-stent/T-tube procedure is represented.

**Completeness (Recall)**
- Missed procedure: T-tube insertion is omitted.
- Missed detail: Device size (14 × 80 × 35) and carina/vocal-cord relationships are not structured.

**Logic & Coding**
- CPT consistency: 31641 is supported for laser; the T-tube insertion itself is not reflected in the extraction.
- Schema / structure: Another T-tube insertion with missing device-placement logic.

### note_044 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The stent event is flattened into 'revision' even though the note describes migrated-stent extraction, balloon dilation, and new stent placement.

**Completeness (Recall)**
- Missed procedure: Airway dilation is not represented.
- Missed detail: PEA arrest/ROSC complication and new tracheal stent dimensions are not deeply structured.

**Logic & Coding**
- CPT consistency: 31638 is partly defensible for stent revision-style work, but the full removal-plus-new-placement sequence is not cleanly resolved.
- Schema / structure: Usable core extraction, but relationship modeling of removal/replacement is incomplete.

### note_046 — ❌ FAIL — 18 / 100

**Accuracy (Precision)**
- Hallucination: intubation is unsupported; the note explicitly says no intubation required.
- Hallucination: BAL and brushings are unsupported; the note documents warm-saline lavage and mucus culture only.
- Hallucination: mechanical_debulking/31640 are unsupported; this is mucus/cast clearance from a T-tube, not tumor excision.
- Mismatch: The note's main therapeutic work is bronchoscopic toileting of a T-tube through the sidearm.

**Completeness (Recall)**
- Missed procedure: Therapeutic aspiration / mucus-impaction clearance is omitted.
- Missed detail: T-tube patency restoration, saline-lavage aliquots, and intact tube integrity are not represented.

**Logic & Coding**
- CPT consistency: The note supports airway toileting/therapeutic aspiration rather than the selected 31500/31623/31624/31640 stack.
- Schema / structure: Near-total procedure-family collapse.
