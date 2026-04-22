# Extraction Quality Report

Evaluated **20 notes** from **my_results.txt**.

Overall average score: **68.95 / 100**
Status counts: **2 PASS**, **8 WARNING**, **10 FAIL**.

## Cross-file patterns

- Most serious failures were **action-type and target-type errors**: non-nodal targets forced into nodal EBUS logic, completed-vs-aborted confusion, and wrong stent action/location modeling.
- Several notes had **major recall loss** in multi-procedure cases, especially pleural biopsy, tracheostomy/PEG, blocker-based hemoptysis control, fiducial placement, and ICG localization marking.
- **CPT errors followed extraction errors**: unsupported nodal EBUS coding for a hilar cyst aspiration, no-biopsy thoracoscopy coding despite pleural biopsies, completed thoracentesis coding for an aborted no-aspirate attempt, blank coding for a real navigation/radial case, and isolated bronchial stent coding for a tracheobronchial Y-stent.
- Complications were often mishandled in the opposite direction from prior batches: instead of overcalling routine bleeding, this batch more often **omitted real complications**, including tracheal tear, pneumothorax/possible aspiration, tooth loss during rigid intubation, and intraoperative death.

## note_179 — ❌ FAIL — 42 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - linear_ebus is forced into nodal staging even though the target was a 45 mm hilar cyst, not a nodal station.
  - CPT 31652 is not supported; no mediastinal/hilar nodal station was sampled.
- Mismatch: 
  - outcomes.procedure_success_status='Partial success' and aborted_reason overstate the note; the procedure was completed and yielded material for cytology/culture.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Actual EBUS target was a proximal left upper lobe hilar cyst with multiple septations.
  - Samples were sent for both culture and routine cytology.

### 3. Logic and Coding
- CPT Consistency: Diagnostic bronchoscopy is supported. Nodal EBUS code 31652 is not defensible from a cyst aspiration with no sampled station.
- Schema Compliance: This is a non-nodal EBUS target, and the current schema collapses it into a fake station-based EBUS event.

## note_052 — ⚠️ WARNING — 88 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - The top-level elastography_pattern='blue_green' is not stated in the note; the note documents Type 2 patterns.
- Mismatch: 
  - specimens.specimens_collected lists only 11L, but the specimen section documents 11L, 11Rs, and 4R TBNA.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Per-station specimen locations are incomplete.
  - diagnostic_bronchoscopy.inspection_findings does not actually summarize airway inspection findings.

### 3. Logic and Coding
- CPT Consistency: 31653 is supported by 3 sampled stations. Elastography is documented for 3 targets and supports the elastography add-ons within this pipeline's coding framework.
- Schema Compliance: Overall extraction is coherent; the main misses are specimen completeness and an unsupported color-pattern normalization.

## note_131 — ❌ FAIL — 58 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - CPT 32601 (diagnostic thoracoscopy without biopsy) understates the documented pleural biopsies.
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: 
  - Pleural biopsy is omitted despite targeted biopsies of diaphragmatic pleural lesions and additional chest-wall pleural biopsies.
- Missed Details: 
  - Right-sided procedure location is not preserved.
  - Approximately 3000 mL of serous pleural fluid suctioned is not captured.
  - 15.5 Fr PleurX size and biopsy sites are not captured.

### 3. Logic and Coding
- CPT Consistency: 32550 is supported. Thoracoscopic coding should reflect pleural biopsy rather than a no-biopsy diagnostic thoracoscopy code.
- Schema Compliance: Good pleuroscopy + IPC recognition, but major recall loss for the pleural biopsy component.

## note_047 — ⚠️ WARNING — 86 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: 
  - Fiducial marker placement is documented but not represented as its own structured procedure/event.
- Missed Details: 
  - The second RLL target attempt and abort due inability to localize the nodule are not represented.
  - Cryobiopsy count (6 samples) and first-target peripheral sampling counts could be more explicit in structured fields.

### 3. Logic and Coding
- CPT Consistency: 31623/31624/31626/31627/31628/31629/31653/+31654 are supported by the note. Elastography coding is also supported for the sampled EBUS targets documented.
- Schema Compliance: Strong separation of navigation, peripheral sampling, and mediastinal staging, with the main recall loss being fiducial placement and the aborted second target.

## note_043 — ⚠️ WARNING — 87 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: 
  - Loculations are captured as 'Thin' only even though the template marks both thin and thick loculations.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Dnase is omitted; only tPA is captured.
  - Subsequent-day context and left-sided chest tube context are not fully structured.

### 3. Logic and Coding
- CPT Consistency: 76604 and 32562 are supported.
- Schema Compliance: Core fibrinolytic therapy extraction is correct, but agent/detail capture is incomplete.

## note_228 — ✅ PASS — 94 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Kenalog dose and some post-dilation patency percentages could be captured more granularly.

### 3. Logic and Coding
- CPT Consistency: 31638 and 31641 are defensible from left mainstem stent removal plus cryotherapy/debulking of distal granulation tissue.
- Schema Compliance: Good recognition of existing-stent removal, rigid bronchoscopy, dilation, cryotherapy, and therapeutic injection.

## note_165 — ❌ FAIL — 60 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: 
  - No CPTs are derived even though navigation and radial EBUS are clearly documented.

### 2. Completeness (Recall)
- Missed Procedures: 
  - ICG dye injection / localization marking adjacent to the RUL nodule is not represented as its own event.
- Missed Details: 
  - 0.75 mL isocyanate green volume is omitted.
  - Right upper lobe pleural-adjacent target context is omitted.

### 3. Logic and Coding
- CPT Consistency: The note supports navigational bronchoscopy and radial EBUS. It does not support peripheral TBNA because no aspirate/sample was actually obtained; the coded 31629 line in the note header is not backed by the narrative.
- Schema Compliance: The extractor appropriately avoids hallucinating TBNA, but it misses the actual localization/injection work and drops the supported navigation/radial coding.

## note_189 — ❌ FAIL — 52 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - chest_tube/performed=true and CPT 32551 are not supported; the note explicitly says they chose observation and would place a chest tube only if the pneumothorax expanded or symptoms developed.
- Mismatch: 
  - station 7 is marked inspected_only even though the note says station 11L, 7, 11Rs, and 10R were sampled by EBUS-TBNA.

### 2. Completeness (Recall)
- Missed Procedures: 
  - Peripheral TBNA of the pulmonary nodule is described ('peripheral needle') but not represented as its own sampling event.
- Missed Details: 
  - Complications are not surfaced despite explicit post-procedure emesis/possible aspiration and a small apical pneumothorax.

### 3. Logic and Coding
- CPT Consistency: Brushings, transbronchial biopsy, radial EBUS, and 31653 are supported. 32551 is not supported.
- Schema Compliance: High-severity post-procedure logic error: false chest tube placement plus incomplete EBUS station capture.

## note_259 — ❌ FAIL — 34 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - airway_stent.performed=true is not supported; stent placement was considered but never performed before the patient arrested.
- Mismatch: 
  - Only one chest tube event/code is surfaced even though the note documents both a left and a right chest tube placed intraoperatively.

### 2. Completeness (Recall)
- Missed Procedures: 
  - Bilateral chest tube placement is incompletely captured.
  - Forceps biopsy work is not represented.
- Missed Details: 
  - Intraoperative PEA/asystolic arrest and death are not modeled as major outcomes/complications.
  - Hemostatic measures (TXA, epinephrine, cold saline) are omitted.

### 3. Logic and Coding
- CPT Consistency: The note supports rigid bronchoscopy with thermal ablation/mechanical debulking and bilateral rescue chest tube placement. A stent code is not supported because no stent was placed.
- Schema Compliance: Severe failure in a high-acuity case: false stent placement, incomplete rescue procedures, and omission of intraoperative death.

## note_042 — ❌ FAIL — 54 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: 
  - Percutaneous tracheostomy is a major performed procedure and is omitted.
  - PEG insertion is also documented but omitted.
- Missed Details: 
  - BAL location (RB4/RB5) and broad aspiration locations could be more explicit.
  - The registry follow-up text points to tracheostomy/PEG, underscoring the omitted procedures.

### 3. Logic and Coding
- CPT Consistency: 31624 and 31645 are supported, but the extraction materially undercalls the combined procedure note by omitting tracheostomy and PEG components.
- Schema Compliance: Core bronchoscopic work is present, but recall is materially incomplete for the overall case.

## note_110 — ❌ FAIL — 46 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - thoracentesis.performed=true and CPT 32555 are overcalled as completed work even though no fluid was aspirated and the procedure was aborted.
- Mismatch: 
  - The registry simultaneously marks the thoracentesis as performed while outcomes correctly say the procedure was aborted.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - The failed left 1st intercostal space mid-clavicular attempt and no-fluid result are not preserved in the procedural object.

### 3. Logic and Coding
- CPT Consistency: 76604 is supported. A completed thoracentesis code is not defensible from an aborted, no-aspirate attempt without stronger attempted-procedure handling.
- Schema Compliance: Classic attempted-versus-completed failure.

## note_148 — ✅ PASS — 94 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Purulent secretions in the superior segment of the left lower lobe could be captured more explicitly.

### 3. Logic and Coding
- CPT Consistency: Bronchoscopy through an established tracheostomy route with BAL is consistent with the note.
- Schema Compliance: Good capture of tracheostomy route and BAL.

## note_023 — ⚠️ WARNING — 74 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: 
  - Bronchial blocker exchange/repositioning for hemoptysis control is not represented.
- Missed Details: 
  - The blocker moved from the RLL to the distal bronchus intermedius with 3 mL of air for occlusion, which is clinically important context.
  - Hemoptysis-control context is reduced to aspiration alone.

### 3. Logic and Coding
- CPT Consistency: 31645 is supported. The note header's 31622 is not clearly supported by the narrative because no washing specimen is described.
- Schema Compliance: The aspiration event is real, but the principal blocker-based hemorrhage-control workflow is omitted.

## note_008 — ❌ FAIL — 68 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - CPT 31612 is not supported; the note does not document percutaneous transtracheal aspiration/injection.
- Mismatch: 
  - airway_stent_revision location is misassigned to the left mainstem even though the stent was tracheal and revised proximally within the trachea.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Bona 14 x 60 mm stent size and the trans-tracheal securing suture are not preserved.
  - Balloon dilation sizes (12/13.5/15) are not preserved.

### 3. Logic and Coding
- CPT Consistency: 31631, 31638, and 31645 are supported. 31612 is not.
- Schema Compliance: Strong procedural recall, but a material CPT hallucination and wrong stent-revision location keep this out of PASS.

## note_094 — ⚠️ WARNING — 82 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - mechanical_debulking location is too narrow/imprecise; the note describes excision/debridement at RC2, bronchus intermedius, and LC1, not simply 'RUL'.
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - BAL volumes (60 mL in / 25 mL out) are not fully surfaced.
  - Site-by-site patency changes and stent details could be more granular.

### 3. Logic and Coding
- CPT Consistency: 31624, 31646, and 31641 are supported.
- Schema Compliance: Good capture of transplant-airway surveillance with aspiration, cryotherapy, and BAL, with mainly location/detail imprecision.

## note_056 — ❌ FAIL — 64 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: 
  - The registry does not surface the explicit complication of posterior distal tracheal injury / full-thickness tear.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Posterior membrane defect measurements are omitted.
  - Final tubular tracheal stent size (16 x 45 mm) is omitted.
  - This was inspection-only EBUS with no biopsy, and that nuance is only partially preserved.

### 3. Logic and Coding
- CPT Consistency: 31624, 31645, and 31631 are supported. The note does not support a nodal sampling CPT because no EBUS biopsy was performed.
- Schema Compliance: The major miss is failure to structure a clearly documented complication in a high-stakes rescue-stent case.

## note_201 — ⚠️ WARNING — 78 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - The coding stack selects 31640 only even though the note explicitly documents APC/cryotherapy destruction work that strongly supports 31641.
- Mismatch: 
  - outcomes.procedure_success_status='Partial success' with an aborted_reason is a slightly awkward fit; the procedure completed, albeit with residual disease.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Residual 60% obstruction at the end of the case is not preserved.
  - Hemostatic epinephrine/iced saline details are not surfaced.

### 3. Logic and Coding
- CPT Consistency: Rigid bronchoscopy with APC plus cryotherapy/debulking is supported. 31641 is the stronger therapeutic code; 31640 alone is questionable under the pipeline's own bundling logic.
- Schema Compliance: Therapeutic modalities are recognized, but CPT selection is shaky.

## note_019 — ⚠️ WARNING — 86 / 100

### 1. Accuracy (Precision)
- Hallucinations: None
- Mismatch: None

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Only a shallow chest-ultrasound summary is captured despite bilateral findings.
  - Dnase is omitted.
  - The 400 cc bloody output after dwell is omitted.

### 3. Logic and Coding
- CPT Consistency: 76604 and 32561 are supported.
- Schema Compliance: Good core first-day fibrinolytic extraction with incomplete ultrasound and agent detail.

## note_229 — ❌ FAIL — 60 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - airway_stent location is collapsed to the left mainstem even though the procedure was placement of a silicone tracheobronchial Y-stent spanning the trachea and both mainstems.
  - CPT 31636 alone under-represents the tracheal/Y-stent work.
- Mismatch: 
  - mechanical_debulking location is wrong; debulking was tracheal/carina/proximal bilateral mainstem work, not an RUL procedure.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - Customized stent dimensions and limb lengths are omitted.
  - Loss of two teeth during rigid intubation is omitted as a procedural complication/event.

### 3. Logic and Coding
- CPT Consistency: 31641 is supported for APC/cryotherapy tumor debulking. Stent coding should reflect tracheal Y-stent logic rather than an isolated bronchial stent placement code.
- Schema Compliance: Major location/coding compression in a complex central-airway stent case.

## note_083 — ⚠️ WARNING — 72 / 100

### 1. Accuracy (Precision)
- Hallucinations: 
  - Radial EBUS / CPT 31654 is not clearly supported; the note uses radial EBUS to identify vasculature/airways in complex stenotic anatomy rather than for a peripheral lesion intervention.
- Mismatch: 
  - airway_stent removal location is mislabeled; the removed device was an LMSB stent, not an LLL stent.

### 2. Completeness (Recall)
- Missed Procedures: None
- Missed Details: 
  - BAL volumes (40 mL in / 15 mL out) are incompletely surfaced.
  - No-new-stent decision and complex anatomy are not well structured.

### 3. Logic and Coding
- CPT Consistency: 31645, 31624, 31638, and 31641 are supported. 31625 is supported by the explicit 'LMSB EBBx' specimen. 31654 is doubtful.
- Schema Compliance: Complex airway-stent management is mostly captured, but device location and radial-EBUS logic are off.
