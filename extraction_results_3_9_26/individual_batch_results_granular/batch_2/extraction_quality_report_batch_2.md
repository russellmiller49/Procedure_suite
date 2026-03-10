## Extraction Quality Report
Evaluated **50 notes** from **my_results_batch_2.txt**.
Overall average score: **75.1 / 100**
Status counts: **18 PASS**, **11 WARNING**, **21 FAIL**.
### Cross-file patterns
- The most frequent high-severity failure was **sampled vs inspected_only confusion** in linear EBUS node events, often cascading into missing or wrong 31652/31653 selection.
- A second recurring error was **peripheral TBNA being collapsed into nodal EBUS**, especially in mass-target notes, producing unsupported 31652 instead of defensible 31629.
- Several navigation cases had **partial recall loss**: the biopsy was captured but the parent navigation procedure, a concurrent needle-aspiration event, or both were dropped.
- Therapeutic airway cases showed **procedure-family and CPT dominance problems**, especially laser/electrocautery cases normalized to 31640 when 31641 or a less specific therapeutic representation was more defensible.
- Pleural extraction was mostly strong, but one case added a clearly unrelated **hallucinated therapeutic injection family/code** and another falsely marked future chest-tube removal as already performed.

### note_001 — ❌ FAIL — 52 / 100

**Accuracy (Precision)**
- clinical_context/risk_assessment ASA 3 is not supported by 'MONITORING: Standard ASA'.
- Node events mark stations 7 and 4R as inspected_only even though the note explicitly says TBNA was performed at both stations.
- Because sampled actions are not represented in node_events, no EBUS CPT is derived despite a 2-station EBUS-TBNA.

**Completeness (Recall)**
- Missed procedures: None
- Pass counts (7 x4, 4R x3) and ROSE presence are not fully carried through.

**Logic & Coding**
- CPT consistency: Should derive 31652 for 2 sampled stations (7 and 4R).
- Schema / structure: Internal contradiction between stations_sampled/granular detail and node_events.

### note_002 — ❌ FAIL — 38 / 100

**Accuracy (Precision)**
- Station 11R is falsely treated as sampled; the corrected note text supports 11L and station 7, not 11R.
- EBUS is upcoded to 31653 even though only 2 stations (11L and 7) were sampled.
- Evidence quotes for node events are pulled from the specimen list rather than the procedural sampling sentence.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: Should be 31652, not 31653.
- Schema / structure: High-severity target/laterality hallucination in a simple 2-station EBUS case.

### note_003 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Sedation/anesthesia is not documented in the source note and is appropriately not invented.

**Logic & Coding**
- CPT consistency: 31652 is correct for single-station EBUS-TBNA of 4R.
- Schema / structure: Accurate extraction for a terse single-station note.

### note_004 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- diagnostic_bronchoscopy.inspection_findings implies a mass even though the airway exam says mildly edematous mucosa and no mass.
- General anesthesia is documented in the note but not surfaced in the structured sedation section.

**Completeness (Recall)**
- Missed procedures: None
- TBLB target RB3 is not preserved in the biopsy location fields.
- Node-event evidence quotes for sampled stations are taken from specimen text rather than the procedural sampling sentence.

**Logic & Coding**
- CPT consistency: 31628/31653/+31654 are supported.
- Schema / structure: High-level procedure families are right, but narrative polarity and some grounding details are weak.

### note_005 — ❌ FAIL — 58 / 100

**Accuracy (Precision)**
- Hallucinations: None
- linear_ebus.node_events labels station 4L as inspected_only even though the note documents EBUS-TBNA/FNA with 3 passes and a 22G needle.

**Completeness (Recall)**
- Missed procedures: None
- Moderate sedation is documented but not captured.
- Needle gauge and pass count are only partially reflected.

**Logic & Coding**
- CPT consistency: Should derive 31652 from a single sampled station (4L).
- Schema / structure: Granular station detail says sampled=true while node_events say inspected_only; internal contradiction.

### note_006 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Pass count x4 is not deeply structured in the concise registry view.
- Sedation documentation is conflicting in the note; choosing General is a reasonable interpretation because an explicit anesthesia line is present.

**Logic & Coding**
- CPT consistency: 31652 is correct for one sampled station.
- Schema / structure: Good extraction despite conflicting sedation text.

### note_007 — ✅ PASS — 93 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Could additionally structure the propofol/anesthesia details and the follow-up destination.

**Logic & Coding**
- CPT consistency: 31652 is correct for 2 sampled stations (4R and 10R).
- Schema / structure: Clean extraction of a straightforward 2-station EBUS note.

### note_008 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Only minor detail loss; the note is otherwise represented correctly.

**Logic & Coding**
- CPT consistency: 31652 is appropriate for single-station station-7 EBUS-TBNA.
- Schema / structure: Good handling of malformed header codes without inventing extra work.

### note_009 — ❌ FAIL — 45 / 100

**Accuracy (Precision)**
- linear_ebus/31652 are not supported by the note; the target is a peripheral RUL mass, not a sampled nodal station.
- The coder suppresses peripheral TBNA even though the note explicitly says TBNA was performed on the RUL mass.

**Completeness (Recall)**
- Missed procedures: None
- No nodal station is actually documented.

**Logic & Coding**
- CPT consistency: 31629 is supportable. 31652 is not.
- Schema / structure: Classic peripheral-TBNA versus nodal-EBUS confusion.

### note_010 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- BAL location is left vague instead of RB6/RLL superior segment.
- The radial view changed from eccentric to concentric, but only the final state is preserved.

**Logic & Coding**
- CPT consistency: 31624/31627/31628/31629/+31654 are coherent with the note.
- Schema / structure: Good separation of navigation, radial EBUS, peripheral TBNA, TBBx, and BAL.

### note_011 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Apicoposterior LUL target detail and biopsy count x5 could be more explicit.

**Logic & Coding**
- CPT consistency: 31627/31628/+31654 are supported.
- Schema / structure: Strong extraction for a simple navigation + rEBUS + TBBx case.

### note_012 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Disposition/follow-up text is partially mangled by the conflicting note wording about extubation versus no ETT.

**Completeness (Recall)**
- Missed procedures: None
- Fluoroscopy is present but not materially integrated into the structured procedure summary.

**Logic & Coding**
- CPT consistency: 31627 and 31628 are supported.
- Schema / structure: Core procedure family is correct; only the conflicting peri-procedural narrative is messy.

### note_013 — ❌ FAIL — 64 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Navigational bronchoscopy is explicitly documented ("Nav bronch") but not extracted.
- Fluoroscopic confirmation/no pneumothorax is not represented.

**Logic & Coding**
- CPT consistency: 31628 is supported, but 31627 is also supported and was missed.
- Schema / structure: The extractor captures the biopsy but drops the navigation procedure that drove it.

### note_014 — ✅ PASS — 92 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Pass count (x3) and corrected lesion depth (2.0 cm, not 20 cm) are not preserved in granular fields.

**Logic & Coding**
- CPT consistency: 31627/31629 are supported.
- Schema / structure: Good handling of noisy units without inventing extra procedures.

### note_015 — ❌ FAIL — 64 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Transbronchial biopsy / forceps biopsy of the LUL target is documented but not extracted.
- Target is only represented generically rather than as LUL.
- Sampling counts (TBNA 3, forceps 4, brush 1) are not fully structured.

**Logic & Coding**
- CPT consistency: 31623/31627/31629 are supported, but 31628 is also supported and missing.
- Schema / structure: Partial recall loss in a multi-tool robotic bronchoscopy case.

### note_016 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Upper-third tracheal location could be more specific in airway outcome fields.

**Logic & Coding**
- CPT consistency: 31630 is supported.
- Schema / structure: Good capture of rigid bronchoscopy with balloon dilation for tracheal stenosis.

### note_017 — ⚠️ WARNING — 86 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Primary indication remains right mainstem obstruction even though the corrected therapeutic target is the left mainstem lesion.
- diagnostic_bronchoscopy.inspection_findings is noisy/unhelpful.

**Completeness (Recall)**
- Missed procedures: None
- Explicit location laterality and APC settings (40W) are not carried into therapeutic fields.

**Logic & Coding**
- CPT consistency: 31641 is supported.
- Schema / structure: The core thermal-ablation family is right, but laterality normalization is shaky.

### note_018 — ❌ FAIL — 66 / 100

**Accuracy (Precision)**
- mechanical_debulking.method="Forceps debulking" is unsupported; the note says cryo-debulking, not forceps debulking.
- The case is over-normalized into a mechanical-excision family from sparse cryotherapy-style wording.

**Completeness (Recall)**
- Missed procedures: None
- Location LLL is captured, but the actual cryo modality is not.

**Logic & Coding**
- CPT consistency: Therapeutic tumor debulking is supported, but the specific 31640 mechanical-excision inference is not firmly grounded from this note alone.
- Schema / structure: Procedure-family specificity is too confident for an ultra-short cryo-debulking note.

### note_019 — ⚠️ WARNING — 76 / 100

**Accuracy (Precision)**
- Bleeding severity is overstated as a Nashville grade-2 / moderate bleeding complication; the note says minimal bleeding controlled with cold saline.
- Billing selects 31640 even though the note clearly documents laser ablation plus mechanical coring; 31641 is the more defensible dominant code for same-site destruction work.

**Completeness (Recall)**
- Missed procedures: None
- Specimen/biopsy detail is present in the note but not surfaced as a separate structured sampling event.

**Logic & Coding**
- CPT consistency: 31645 is arguable for copious purulent secretion clearance. The therapeutic tumor work is better represented by 31641 than 31640.
- Schema / structure: Major therapeutic events are recognized, but complication grading and CPT dominance logic are off.

### note_020 — ✅ PASS — 93 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Dilation duration (60 seconds) is not preserved.

**Logic & Coding**
- CPT consistency: 31630 is supported.
- Schema / structure: Good extraction of flexible balloon dilation for LMS stenosis.

### note_021 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- airway_stent.stent_type is labeled as uncovered, but the note explicitly says fully covered self-expanding metallic stent.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- General anesthesia with paralysis is the corrected procedural anesthesia context and could be better emphasized.

**Logic & Coding**
- CPT consistency: 31631 is supported for tracheal stent placement.
- Schema / structure: Core stent-placement family is right, but covered-versus-uncovered device detail is wrong.

### note_022 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Granulation-tissue target detail after stent removal could be more explicit.

**Logic & Coding**
- CPT consistency: 31638 is supported for airway stent removal; the APC adjunct is reasonably captured as therapeutic ablation.
- Schema / structure: Good separation of rigid bronchoscopy, stent removal, and APC treatment.

### note_023 — ⚠️ WARNING — 82 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Stent surveillance/assessment is not represented as a distinct event.
- Corrected laterality/type of the stent are not preserved.

**Logic & Coding**
- CPT consistency: 31645 is supportable for mucus-plug clearance. No separate stent-management CPT is clearly supported from the note.
- Schema / structure: Usable extraction, but it flattens the stent-check context into aspiration alone.

### note_024 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Drained volume (1.2 L) and yellow fluid appearance are not structured.

**Logic & Coding**
- CPT consistency: 32555 is correct for US-guided thoracentesis.
- Schema / structure: Clean pleural extraction.

### note_025 — ❌ FAIL — 42 / 100

**Accuracy (Precision)**
- therapeutic_injection.performed=true with CPT 31573 is unsupported; the note describes intrapleural fibrinolytic instillation via the pigtail, not a separate airway injection procedure.
- pleural_procedures.chest_tube_removal.performed=true is unsupported; the note contains only a future plan to remove the tube when output decreases.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Drainage volume (500 cc), turbid fluid appearance, and 1-hour clamp time are not preserved.

**Logic & Coding**
- CPT consistency: 32557 and 32561 are supported. 31573 is not.
- Schema / structure: Correct pleural families are present, but they are contaminated by unrelated hallucinated procedure families.

### note_026 — ❌ FAIL — 55 / 100

**Accuracy (Precision)**
- Stations 7 and 4R are marked inspected_only in node_events even though the note says TBNA was performed at both stations.
- No EBUS CPT is derived despite a documented 2-station EBUS-TBNA.

**Completeness (Recall)**
- Missed procedures: None
- Moderate sedation and pass counts are incompletely surfaced.

**Logic & Coding**
- CPT consistency: Should derive 31652 for stations 7 and 4R.
- Schema / structure: Same sampled-versus-inspected failure pattern as note_001.

### note_027 — ❌ FAIL — 38 / 100

**Accuracy (Precision)**
- Station 4R is falsely treated as sampled; the corrected note supports 4L and station 7 only.
- EBUS is upcoded to 31653 even though only 2 stations were sampled.
- Evidence quotes are anchored to specimen text instead of the procedural sampling sentence.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: Should be 31652, not 31653.
- Schema / structure: High-severity corrected-laterality hallucination in a simple EBUS case.

### note_028 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Only minor detail loss in a terse single-station EBUS note.

**Logic & Coding**
- CPT consistency: 31652 is correct for single-station 11L sampling.
- Schema / structure: Accurate extraction for an ultra-short EBUS note.

### note_029 — ⚠️ WARNING — 78 / 100

**Accuracy (Precision)**
- Hallucinations: None
- linear_ebus.stations_sampled incorrectly includes 11R even though only station 7 was sampled; 4R and 11R were inspected only.
- transbronchial_biopsy location/sample fields are malformed (e.g., location tied to "Needle aspiration x 3").

**Completeness (Recall)**
- Missed procedures: None
- RUL apical-segment target detail and the exact counts (TBNA 3, forceps 5, washings 1) are not cleanly preserved.

**Logic & Coding**
- CPT consistency: 31627/31628/31629/31652 are supported.
- Schema / structure: High-level recall is good, but station and target granularity are noisy.

### note_030 — ❌ FAIL — 48 / 100

**Accuracy (Precision)**
- Node events mark 4R and 4L as inspected_only even though the note says all three stations (4R, 4L, 7) were sampled.
- Station 7 is omitted from structured EBUS detail.
- No CPT is derived despite an explicit 3-station EBUS-TBNA and even a procedure header naming 31653.

**Completeness (Recall)**
- Missed procedures: None
- Moderate sedation is documented but not captured.

**Logic & Coding**
- CPT consistency: Should derive 31653 for 3 sampled stations.
- Schema / structure: Major sampled-versus-inspected logic failure with substantial undercoding.

### note_031 — ⚠️ WARNING — 89 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Pass counts (11R x4, 10R x3) are not fully structured.
- Sedation choice is based on conflicting note text; General with LMA is a reasonable read, but the conflict remains in the source note.

**Logic & Coding**
- CPT consistency: 31652 is correct for 2 sampled stations.
- Schema / structure: Core EBUS extraction is correct despite conflicting anesthesia text.

### note_032 — ✅ PASS — 93 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Could additionally preserve that airway inspection showed no endobronchial lesions.

**Logic & Coding**
- CPT consistency: 31652 is correct for stations 7 and 10L.
- Schema / structure: Good extraction of a simple 2-station EBUS note.

### note_033 — ❌ FAIL — 50 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Station 7 is omitted even though the note says 4R, 4L, and 7 were all sampled.
- 31652 is selected instead of 31653 despite 3 sampled stations.

**Completeness (Recall)**
- Missed procedures: None
- Pass counts (3 each) are not fully represented for all stations.

**Logic & Coding**
- CPT consistency: Should be 31653, not 31652.
- Schema / structure: Undercoding cascades directly from incomplete EBUS station extraction.

### note_034 — ❌ FAIL — 45 / 100

**Accuracy (Precision)**
- linear_ebus/31652 are not supported by the note; the target is a peripheral LUL mass, not a nodal EBUS station.
- Peripheral TBNA is suppressed even though the note explicitly documents TBNA on the LUL mass.

**Completeness (Recall)**
- Missed procedures: None
- No nodal station is actually documented.

**Logic & Coding**
- CPT consistency: 31629 is supportable. 31652 is not.
- Schema / structure: Another peripheral-TBNA versus nodal-EBUS confusion.

### note_035 — ❌ FAIL — 70 / 100

**Accuracy (Precision)**
- diagnostic_bronchoscopy.inspection_findings implies a lesion rather than reflecting the documented navigational/peripheral target workflow.
- Navigational bronchoscopy is explicit in the note and header but is not extracted, so 31627 is missing.

**Completeness (Recall)**
- Navigational bronchoscopy.
- RML lateral-segment target detail could be more explicit.

**Logic & Coding**
- CPT consistency: 31628/31629/+31654 are supported, but 31627 is also supported and missing.
- Schema / structure: The peripheral sampling work is captured, but the parent navigation procedure is dropped.

### note_036 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Radial probe position is simplified to concentric even though the note says eccentric then adjusted to concentric.

**Completeness (Recall)**
- Peripheral TBNA / needle aspiration x2 is not extracted.
- Posterior basal LLL target detail is only partially preserved.

**Logic & Coding**
- CPT consistency: 31627/31628/+31654 are supported, and 31629 is also supported from the documented needle aspiration passes.
- Schema / structure: Combined navigation + rEBUS + TBBx case loses the concurrent TBNA event.

### note_037 — ⚠️ WARNING — 87 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Sedation is left as local only even though the note contains conflicting robotic/LMA language that suggests deeper anesthesia support.
- Disposition text is partially mangled by the conflicting source wording.

**Completeness (Recall)**
- Missed procedures: None
- Biopsy count x5 and RUL anterior-segment target could be more explicit.

**Logic & Coding**
- CPT consistency: 31627 and 31628 are supported.
- Schema / structure: Core navigation + TBBx extraction is sound; only the conflicting anesthesia narrative is messy.

### note_038 — ❌ FAIL — 68 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Navigational bronchoscopy ("Nav bronch") is documented but not extracted.
- Apicoposterior LUL target and biopsy count x5 are only partially preserved.

**Logic & Coding**
- CPT consistency: 31628 and +31654 are supported, and 31627 is also supported and missing.
- Schema / structure: Ultra-short note still clearly supports navigation, which the extractor drops.

### note_039 — ❌ FAIL — 64 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Transbronchial biopsy / forceps biopsy x4 is documented but not extracted.
- Corrected lesion depth (1.5 cm, not 15 cm) is not preserved.

**Logic & Coding**
- CPT consistency: 31627/31629 are supported, and 31628 is also supported and missing.
- Schema / structure: Partial recall loss in a combined nav + TBNA + forceps-biopsy case.

### note_040 — ❌ FAIL — 72 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Peripheral TBNA is documented (needle x2, blood only) but not extracted.
- RLL target detail and per-tool counts are incompletely preserved.

**Logic & Coding**
- CPT consistency: 31623/31627/31628/+31654 are supported, and 31629 is also supportable because needle aspiration was performed even though the result was blood only.
- Schema / structure: Another multi-tool navigation case with incomplete recall.

### note_041 — ✅ PASS — 91 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Subglottic location and 2-minute dilation duration could be structured more explicitly.

**Logic & Coding**
- CPT consistency: 31630 is supported.
- Schema / structure: Good extraction of rigid bronchoscopy with balloon dilation.

### note_042 — ❌ FAIL — 66 / 100

**Accuracy (Precision)**
- The case is normalized into thermal ablation/31641 even though the note says an electrocautery snare transected the tumor base, which is more consistent with excision/debulking language than pure destruction.
- Corrected laterality is right lower lobe, but the indication remains left lower lobe.

**Completeness (Recall)**
- Missed procedures: None
- The endobronchial tumor biopsy specimen is not surfaced as a structured supporting detail.

**Logic & Coding**
- CPT consistency: 31641 is shaky here; 31640 is more defensible from the excision/transection wording.
- Schema / structure: Procedure-family choice is too aggressive toward ablation in a snare-transection note.

### note_043 — ❌ FAIL — 30 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Rigid bronchoscopy.
- Therapeutic aspiration / airway-clearance of a large mucus plug.
- Right-mainstem location and cryo-extraction technique are not represented at all.

**Logic & Coding**
- CPT consistency: 31645 is supportable, with rigid bronchoscopy context documented.
- Schema / structure: Near-complete miss of a short but clear therapeutic airway note.

### note_044 — ❌ FAIL — 70 / 100

**Accuracy (Precision)**
- mechanical_debulking/31640 are overcalled as the primary coding conclusion; the note clearly centers on Nd:YAG laser ablation.
- The coder outputs 31640 even though 31641 is the better fit for same-site laser destruction work.

**Completeness (Recall)**
- Missed procedures: None
- Left-mainstem location, pre/post obstruction percentages, and jet-ventilation context could be more explicit.

**Logic & Coding**
- CPT consistency: 31641 is the more defensible primary code. 31640 is not well supported as the dominant CPT from this note.
- Schema / structure: Therapeutic family is partly right, but CPT dominance logic is wrong.

### note_045 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Dilation duration (120 seconds) is not preserved.

**Logic & Coding**
- CPT consistency: 31630 is supported.
- Schema / structure: Good extraction of flexible bronchoscopy with tracheal balloon dilation.

### note_046 — ⚠️ WARNING — 84 / 100

**Accuracy (Precision)**
- stent_brand="way" is unsupported and appears to be a parsing artifact.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- General anesthesia with rigid bronchoscopy is the corrected procedural context and could be emphasized more cleanly.

**Logic & Coding**
- CPT consistency: 31636 is supported for bronchial stent placement in the right mainstem.
- Schema / structure: Core stent-placement extraction is good, but device-normalization has a clear artifact.

### note_047 — ✅ PASS — 90 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Granulation-tissue burden and exact post-removal patency are not preserved in outcome fields.

**Logic & Coding**
- CPT consistency: 31638 is supported for airway stent removal.
- Schema / structure: Reasonable extraction; unlike the common false-bleeding pattern, this note does document moderate bleeding controlled with cold saline.

### note_048 — ⚠️ WARNING — 72 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Diagnostic bronchoscopy / stent assessment event is not extracted.
- Corrected laterality (left mainstem), stent type, and absence of tissue ingrowth are not represented.

**Logic & Coding**
- CPT consistency: No specific stent-intervention CPT is supported, but the bronchoscopic stent-surveillance finding is missed.
- Schema / structure: Recall loss in an ultra-short surveillance note.

### note_049 — ✅ PASS — 95 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Volume (800 cc), fluid appearance (serosanguinous), and laboratory plan are not fully structured.

**Logic & Coding**
- CPT consistency: 32555 is correct for US-guided thoracentesis.
- Schema / structure: Clean pleural extraction.

### note_050 — ✅ PASS — 94 / 100

**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Septations, drained volume (600 cc), and purulent fluid character are not fully preserved.

**Logic & Coding**
- CPT consistency: 32557 is supported for US-guided small-bore pleural drain placement.
- Schema / structure: Good extraction of chest tube placement for empyema.

