# Extraction Quality Report

Evaluated **20 notes** from the uploaded batch output file.

Overall average score: **65.4 / 100**
Status counts: **1 PASS**, **9 WARNING**, **10 FAIL**.

## Cross-file patterns

- The most common high-severity failure was EBUS node logic: surveyed or eligible stations were converted into sampled stations, or ROSE results leaked onto unsupported stations.
- Existing-stent and new-stent cases remain fragile. Some notes were flattened into revision when new placement occurred, while other cases lost stent-family coding entirely.
- Granulation tissue, necrotic inflammatory tissue, cavitary fungal material, or airway hair removal were repeatedly mislabeled as tumor excision or as the wrong biopsy family.
- Several pleural cases showed false ancillary events, especially unsupported chest_tube_removal and exaggerated outcome/complication framing.
- Routine bleeding control or transient biopsy-site bleeding continues to be at risk of being promoted into formal complication constructs despite notes that state no immediate complications.

## Per-note evaluations

### note_246 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - procedure.indication and clinical_context.primary_indication are contaminated with consent text rather than just the indication.
  - outcomes.procedure_success_status='Failed' overcalls the result; the note describes full reopening of the LUL and partial reopening of the LLL, which is better characterized as partial success.
- Mismatch: 
  - therapeutic_injection is turned on from topical TXA hemostasis; this is supportive bleeding control rather than a clearly separate primary procedural family.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The note clearly distinguishes complete reopening of the LUL versus only ~70% reopening of the LLL; that sided outcome granularity is only partially preserved.

**Logic & Coding**
- CPT consistency: 31640 is defensible for mechanical tumor excision/debulking. Additional destruction work was performed, but the main coding error is the failed/aborted outcome overcall rather than the primary CPT.
- Schema / structure: Core CAO procedure families are captured, but indication and outcome fields are noisy.

### note_162 — ❌ FAIL — 54 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - linear_ebus.stations_sampled incorrectly includes 10R and 4L as sampled even though the note only says they met sampling criteria.
  - node_events assign malignant or generic 'malig' ROSE results to stations without note support.
- Mismatch: 
  - The actually sampled stations are 11Rs, 7, 4R, 2R, and 11L. The JSON treats surveyed nodes as sampled nodes.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - 11L had 8 additional passes for molecular studies and a dedicated flow cytometry pass, which are not properly preserved.

**Logic & Coding**
- CPT consistency: 31653 remains supported because 3 or more structures were truly sampled, but the station-level extraction is materially inaccurate.
- Schema / structure: Classic surveyed-versus-sampled EBUS failure.

### note_122 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - stations_sampled includes a synthetic 'NONE' station and target labeling is not anatomically clean.
- Mismatch: 
  - procedure_setting.airway_type is set inconsistently with the note's LMA wording in parts of the record.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The JSON does not cleanly preserve that this was a mediastinal mass in the 4R position sampled with 5 biopsies using a 22G Vizishot needle.

**Logic & Coding**
- CPT consistency: A single EBUS-sampled target/structure is present, so 31652 is defensible.
- Schema / structure: Usable extraction overall, but non-station target representation is awkward.

### note_240 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - 31640 is not well supported as tumor excision; the note describes coring/debridement of granulation tissue in stenosis management.
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The note separately documents migrated stent removal, balloon dilation, rigid coring of granulation tissue, and stent replacement with a new 12 x 40 Bonastent; some of that granularity is flattened.

**Logic & Coding**
- CPT consistency: 31638 is consistent with revision/replacement work on the migrated tracheal stent. 31640 is shaky because this is granulation tissue rather than tumor.
- Schema / structure: Good high-level stent-management extraction with a coding overreach on tumor excision.

### note_146 — ❌ FAIL — 42 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: 
  - The note clearly documents silicone Y-stent placement across trachea/carina/both mainstems, but the billing output omits the stent placement family.

**Completeness (Recall)**
- Missed Procedures: 
  - Airway stent placement is a major performed procedure and should drive stent-family CPT logic.
  - Thermal tumor destruction/APC work is incompletely reflected in the final coding output.
- Missed Details: 
  - Stent brand/type/size are important and the note gives them: silicone Y-stent, Novatec 14-10-10 mm, customized limbs.

**Logic & Coding**
- CPT consistency: Endobronchial biopsy and tumor excision/debulking are supported, but stent placement is also clearly supported and should not be omitted.
- Schema / structure: Major recall failure in a complex therapeutic airway case.

### note_144 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - mechanical_debulking method details are not faithful to the note; forceps-type debulking is not clearly described.
- Mismatch: 
  - therapeutic_aspiration content is described too generically; the note specifically says retained blood and secretions at the end of the case.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The note distinguishes left lower lobe snare/coagulation debulking from right lower lobe APC/electrocautery destruction with residual peripheral tumor; this separation is underdeveloped.

**Logic & Coding**
- CPT consistency: Therapeutic aspiration is supported. Tumor debulking/destruction is also supported, but the coding stack is likely incomplete because distinct destruction work is not well represented.
- Schema / structure: Broadly correct extraction with under-specified therapeutic detail.

### note_062 — ⚠️ WARNING — 88 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The note documents separate right mainstem dilation in addition to left mainstem stent exchange; that contralateral dilation detail is not carried very cleanly.
  - Outcome/follow-up text is partially mangled.

**Logic & Coding**
- CPT consistency: BAL, therapeutic aspiration, rigid bronchoscopy, dilation, and stent revision/replacement are all supported. The main concern is detail loss, not core procedure family error.
- Schema / structure: Strong overall extraction for a complicated transplant-airway case.

### note_191 — ⚠️ WARNING — 80 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - ROSE/outcome values are corrupted for some node events.
- Mismatch: 
  - Granular EBUS station detail is incomplete or misassigned relative to the note, which documents stations 7, 4R, and 4L sampled with at least 5 passes each.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - Dual-needle use (22G and 19G) is important and not reflected cleanly.

**Logic & Coding**
- CPT consistency: 31653 is correct because 3 nodal stations were sampled.
- Schema / structure: High-level EBUS extraction is right, but quantitative and station-level detail is unreliable.

### note_242 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - The EBUS portion is embellished with extra sampled/station detail not supported by the note.
  - ROSE positivity from the endobronchial lesion is effectively leaked into the nodal sampling interpretation.
- Mismatch: 
  - The only sampled EBUS node documented is station 7 x4. The JSON's station logic is not coherent.

**Completeness (Recall)**
- Missed Procedures: 
  - Endobronchial forceps biopsy of the RLL superior segment lesion is a key performed procedure and should be explicitly represented.
- Missed Details: 
  - Hemostasis with lidocaine/epinephrine plus cold saline is present but not clearly tied to the lesion biopsy event.

**Logic & Coding**
- CPT consistency: 31652 is supported for single-station EBUS sampling, but 31625-class endobronchial biopsy work is also supported and should not be absent.
- Schema / structure: Combined lesion-biopsy plus staging case is incompletely and inconsistently extracted.

### note_138 — ⚠️ WARNING — 79 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - The non-station target is awkwardly normalized into station-style structures.
- Mismatch: 
  - This is EBUS sampling of a left pulmonary artery mass rather than nodal staging in the usual station schema.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The note documents 3 passes with a 22G needle and nondiagnostic ROSE from the pulmonary artery mass; those details are only partially preserved.

**Logic & Coding**
- CPT consistency: A one-target EBUS-guided sampling construct is defensible, so 31652 is reasonable.
- Schema / structure: Reasonable extraction overall, but the schema struggles with a non-station EBUS target.

### note_195 — ❌ FAIL — 62 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - pleural_procedures.chest_tube_removal is not supported.
  - A formal bleeding-complication construct is overcalled despite the note ending with no immediate complications.
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - Pleural biopsy detail (~5 biopsies) is not well surfaced.

**Logic & Coding**
- CPT consistency: Medical thoracoscopy with pleural biopsies and tunneled IPC placement are supported. The false chest-tube-removal and complication logic reduce reliability.
- Schema / structure: Pleural core is captured, but false ancillary events hurt precision.

### note_247 — ❌ FAIL — 48 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - mechanical_debulking / 31640 are not supported; the note documents multiple forceps biopsies of a mycetoma/cavitary lesion, not tumor excision.
  - Complication severity is overstated from intraprocedural bleeding control despite 'Complications: None'.
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: 
  - A forceps biopsy procedure family should be represented instead of tumor excision.
- Missed Details: 
  - The note gives BAL volumes (60 mL in / 20 mL out) and describes epinephrine + iced saline + wedging for hemostasis.

**Logic & Coding**
- CPT consistency: 31624 is supported. 31640 is not. The biopsy family should be represented as biopsy, not excision/debulking.
- Schema / structure: Procedure-family confusion is the dominant error.

### note_076 — ✅ PASS — 93 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - Aspiration material is described more specifically in the note (clear thick secretions/mucus) than in the structured output.

**Logic & Coding**
- CPT consistency: 31624 and 31645 are both supported.
- Schema / structure: Clean BAL plus therapeutic aspiration extraction.

### note_200 — ❌ FAIL — 52 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - sedation.type='Local Only' is not supported; the note says medications were per anesthesia record.
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: 
  - Tunneled pleural catheter / IPC placement is clearly documented but missing from the retained pleural procedures.
- Missed Details: 
  - The note documents ~1600 cc serosanguinous fluid removed and ~12 pleural biopsies from abnormal parietal pleura.

**Logic & Coding**
- CPT consistency: Medical thoracoscopy is supported, but IPC insertion is also supported and should not be dropped.
- Schema / structure: Major pleural recall failure.

### note_202 — ❌ FAIL — 38 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - Stent work is treated as revision-style work rather than new tracheobronchial stent placement.
  - therapeutic_aspiration is spuriously turned on from pleural/airway fluid handling that does not support bronchoscopic therapeutic aspiration coding.
  - pleural_procedures.chest_tube_removal is not supported.
- Mismatch: 
  - The note describes a new Aero tracheobronchial stent in the bronchus intermedius/right-sided airway, not the extracted stent action/location construct.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The IPC placement and airway stent placement are both real major interventions, but the structured relationship between them is muddled.

**Logic & Coding**
- CPT consistency: The billing logic is materially unreliable because the airway stent family is misclassified and the pleural component contains false ancillary events.
- Schema / structure: High-severity airway-stent logic failure in a mixed bronchoscopy-plus-pleural case.

### note_184 — ❌ FAIL — 57 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - 11L is effectively treated as sampled despite the note explicitly explaining why it was not sampled.
  - Pass and outcome detail are overgeneralized across targets.
- Mismatch: 
  - The truly sampled structures are 4R, 4L, and the transvascular station-5 target. The JSON's node-event logic does not preserve that accurately.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The note's transvascular station-5 biopsy route through the pulmonary artery is a major nuance and should be preserved explicitly.

**Logic & Coding**
- CPT consistency: A 3-structure EBUS sampling construct is plausible, but the station-level logic is inaccurate enough to merit failure.
- Schema / structure: Another sampled-versus-not-sampled EBUS logic error, with transvascular complexity layered on top.

### note_226 — ❌ FAIL — 40 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - 31573 is not supported as a defensible CPT conclusion from this note.
  - 31640 tumor excision is not supported; the note describes cryo/forceps debulking of necrotic or inflammatory obstructive tissue/granulation rather than tumor excision.
- Mismatch: 
  - Indication and medication fields are noisy/malformed in the extraction.

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - The note explicitly documents Kenalog 80 mg submucosal injection with a 21G needle and balloon dilation of the LLL orifice/subsegments.

**Logic & Coding**
- CPT consistency: Airway dilation and cryo/forceps obstruction management are supported. 31573 and 31640 are not well supported as coded here.
- Schema / structure: Inflammatory/necrotic obstruction is miscast as tumor excision and formal injection coding.

### note_029 — ⚠️ WARNING — 88 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - pleural_procedures.chest_tube_removal is not supported.
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - Only minor follow-up/disposition text loss.

**Logic & Coding**
- CPT consistency: 76604 and 32557 are supported.
- Schema / structure: Good pleural extraction apart from a false removal event.

### note_245 — ⚠️ WARNING — 75 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - pleural_procedures.chest_tube_removal is not supported.
  - The outcome is overstated toward partial success/aborted logic even though the case completed; the note only says full inspection was limited by fused lung/adhesions.
- Mismatch: None

**Completeness (Recall)**
- Missed Procedures: None
- Missed Details: 
  - Biopsy targets included both parietal pleura and adherent non-ventilated fused lung, which deserves more explicit capture.

**Logic & Coding**
- CPT consistency: Medical thoracoscopy with biopsy and tunneled IPC placement are supported.
- Schema / structure: Core pleural extraction is decent, but false removal and outcome framing reduce confidence.

### note_009 — ❌ FAIL — 34 / 100

**Accuracy (Precision)**
- Hallucinations: 
  - endobronchial_biopsy / 31625 are not supported by the operative narrative.
  - 31640 tumor excision is not supported; the note describes hair/granulation removal and airway cleanup, not tumor excision.
- Mismatch: 
  - The case includes migrated stent management and endobronchial hair/granulation removal, but the extracted procedure families do not model that faithfully.

**Completeness (Recall)**
- Missed Procedures: 
  - Existing-stent removal/management is insufficiently represented.
- Missed Details: 
  - The note's unusual-work narrative centers on significant airway management and endobronchial hair removal.

**Logic & Coding**
- CPT consistency: BAL and therapeutic aspiration are supported. 31625 and 31640 are not supported as documented.
- Schema / structure: Severe family-classification error in a complex airway-clearance/stent-management case.
