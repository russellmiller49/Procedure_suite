# Extraction Quality Report
Evaluated **50 notes** across **1 batch-output file**.
Overall average score: **70.2 / 100**  
Status counts: **10 PASS**, **21 WARNING**, **19 FAIL**.
Previous same-batch run average: **60.0 / 100**  
Change vs prior run: **+10.2** points; FAIL count improved from **30** to **19**.
## Cross-file patterns
- The rerun materially improved **rare-procedure recognition** in several places: **whole lung lavage** (notes 021-023), **transthoracic core biopsy** (note 024), **therapeutic aspiration for mucus plug** (note 029), and **bronchial thermoplasty** (note 035) are much closer to note truth.
- The most persistent residual failures are still **rare airway adjuncts** that collapse to null or generic bronchoscopy: **EWS spigot placement** (031), **brachytherapy catheter placement** (043), **cryospray ablation** (034), **TEF methylene-blue evaluation** (038), **vocal-cord motion assessment** (045), and **transtracheal oxygen catheter exchange** (046).
- **BLVR logic** remains the dominant warning pattern: wrong valve counts, lobe-vs-segment confusion, missing target lobe, and several unsupported **31634** derivations despite same-session valve placement. Local coding rules in the uploaded billing support explicitly state not to report **31634** with **31647/+31651** in the same session.
- **Coding precision** still needs work in a few high-impact areas: wrong Y-stent family selection (033), mutually inconsistent thermoplasty dual billing (036), gray-zone duplicate EUS-B coding (040), unsupported BAL in a foreign-body case (028), and the wrong thoracoscopy family for pleural biopsies (049).
- There is also a recurring tendency to **turn routine bleeding control into formal complications** (most clearly 042), which is not defensible when the note ends with **Complications: none**.
## Biggest changes from the prior run
- Improved to PASS/WARNING: **note_035**, **note_024**, **note_029**, **note_021**, **note_023**, **note_022**, **note_016**, **note_040**, **note_015**, **note_014**, **note_012**.
- Regressions worth attention: **note_042** now overcalls a complication while still missing the main debulking procedure; **note_004** overcounts valves; **note_007** now mislabels the target as lingula instead of the LUL session.
## my_results_batch_4.txt
### note_001 — ⚠️ WARNING — 80 / 100
*Change vs prior batch-4 evaluation: -2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucination: 31634 is not separately supported; local coding rules suppress Chartis/balloon occlusion when valves are placed in the same session/lobe.
- Mismatch: BLVR target lobe is not preserved even though the note clearly states LUL.
- Mismatch: Collateral ventilation is left 'Chartis indeterminate' instead of absent/no collateral ventilation.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve the treated LUL segments (apicoposterior, anterior, lingular) and mild diffuse bronchitis.

**Logic & Coding**
- CPT consistency: 31647 is supported. Separate 31634 should be suppressed in this same-session BLVR/Chartis case.
- Schema / structure: Correct family, but lobe-level detail and Chartis interpretation drift.

### note_002 — ⚠️ WARNING — 82 / 100
*Change vs prior batch-4 evaluation: -2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: number_of_valves=2 is unsupported; the note documents 3 RUL valves.
- Mismatch: Collateral ventilation is labeled indeterminate rather than the documented no/minimal-CV pattern.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve apical, posterior, and anterior segment deployment.

**Logic & Coding**
- CPT consistency: 31647 is consistent with single-lobe RUL valve placement. Suppressing 31634 is appropriate.
- Schema / structure: Main BLVR family is correct with residual quantitative cleanup needed.

### note_003 — ⚠️ WARNING — 78 / 100
*Change vs prior batch-4 evaluation: +2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucination: 31634 is not separately supported once valves are placed in the same session.
- Mismatch: Target lobe LLL is not preserved.
- Mismatch: Collateral ventilation is left indeterminate instead of the documented minimal/no-CV interpretation.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve LLL segmental deployment more explicitly.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should be suppressed in this BLVR-with-Chartis case.
- Schema / structure: Recognizes BLVR, but the lobe target and Chartis result are under-resolved.

### note_004 — ❌ FAIL — 65 / 100
*Change vs prior batch-4 evaluation: -7 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: 31634 is not separately supported in the same LUL valve-placement session.
- Mismatch: number_of_valves=6 is unsupported; the note documents total 4 valves.
- Mismatch: Target lobe LUL is not preserved.
- Mismatch: diagnostic_bronchoscopy.inspection_findings implies tumor despite the note stating no tumor.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve apicoposterior, anterior, and lingular deployment plus the mixed GA/LMA documentation context.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 should be suppressed.
- Schema / structure: Correct family is found, but valve count and target anatomy are materially wrong.

### note_005 — ❌ FAIL — 68 / 100
*Change vs prior batch-4 evaluation: -2 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: 31634 is not separately supported with same-session RLL valve placement.
- Mismatch: inspection_findings is polluted by plan text ('hemoptysis/fever/chest pain') rather than bronchoscopic findings.
- Mismatch: Target lobe RLL is not preserved in the BLVR record.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve tracheobronchomalacia, mucous plugging, and one-valve repositioning.

**Logic & Coding**
- CPT consistency: 31647 is supported for RLL valve placement. Separate 31634 is not.
- Schema / structure: BLVR family is recognized, but narrative sanitation and target preservation remain weak.

### note_006 — ⚠️ WARNING — 78 / 100
*Change vs prior batch-4 evaluation: -2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucination: inspection_findings retains a false-positive 'mass' despite 'no mass' in the note.
- Mismatch: number_of_valves=1 is unsupported; the note documents 3 RUL valves.
- Mismatch: Collateral ventilation is labeled indeterminate instead of the documented 'no CV' pattern.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. Suppressing 31634 is appropriate here.
- Schema / structure: Core BLVR family is right, but count/CV precision is off.

### note_007 — ❌ FAIL — 68 / 100
*Change vs prior batch-4 evaluation: -6 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: target_lobe='Lingula' is wrong; this is an LUL BLVR case with lingular segment treatment, not a lingula-only session.
- Mismatch: number_of_valves=3 is unsupported; the note documents 4 valves.
- Mismatch: inspection_findings implies a lesion even though the note says no lesion.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported for the LUL session. Separate 31634 is appropriately suppressed.
- Schema / structure: BLVR family is recognized, but lobe-vs-segment logic is materially wrong.

### note_008 — ⚠️ WARNING — 78 / 100
*Change vs prior batch-4 evaluation: -2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucination: 31634 is not separately supported in the same-session BLVR case.
- Mismatch: The clarified RUL target is not preserved even though the note explicitly resolves the LUL flowsheet artifact.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve that the nursing reference to 'LUL valves' is a documentation artifact.

**Logic & Coding**
- CPT consistency: 31647 is supported for RUL valve placement. 31634 should be suppressed.
- Schema / structure: Main therapy is captured, but laterality-resolution logic is incomplete.

### note_009 — ⚠️ WARNING — 84 / 100
*Change vs prior batch-4 evaluation: +3 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: number_of_valves=3 is unsupported; the tab log says 4 placed.
- Mismatch: Collateral ventilation is labeled indeterminate instead of 'LUL no CV'.
- Mismatch: inspection_findings implies a lesion despite airway survey 'No lesion'.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: 31647 is supported. Omitting 31634 is appropriate.
- Schema / structure: Good BLVR family capture with residual count/CV cleanup.

### note_010 — ✅ PASS — 94 / 100
*Change vs prior batch-4 evaluation: +1 points (PASS → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Counts and target detail could be richer (RUL posterior segment, TBBx x6, brush x2), but the performed families are correct.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31652/+31654 are coherent with the note.
- Schema / structure: Good separation of navigation, radial EBUS, TBBx, brushings, BAL, and nodal EBUS-TBNA.

### note_011 — ⚠️ WARNING — 84 / 100
*Change vs prior batch-4 evaluation: +2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Radial ultrasound is documented, but +31654 is not derived.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve cryobiopsy x3, forceps x4, brush x2, and BAL return 20 mL.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628 are supported. +31654 is also defensible from the documented radial ultrasound confirmation.
- Schema / structure: Peripheral sampling family is mostly right, but radial-EBUS detail is undercalled.

### note_012 — ⚠️ WARNING — 75 / 100
*Change vs prior batch-4 evaluation: +7 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: diagnostic_bronchoscopy.inspection_findings is polluted by plan symptoms ('hemoptysis, fever, worsening dyspnea').

**Completeness (Recall)**
- Missed procedure: Transbronchial biopsy/TBBx x5 is not represented, so 31628-level lung biopsy work is undercalled.
- Missed detail: Could preserve 3 passes for both 4L and 7 more cleanly in granular detail.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31652/+31654 are supported, but 31628 should also be present.
- Schema / structure: Good navigation/EBUS separation, but peripheral biopsy recall is incomplete.

### note_013 — ✅ PASS — 92 / 100
*Change vs prior batch-4 evaluation: +2 points (PASS → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Counts and richer target detail (TBNA x4, forceps x4, brush x1) could be structured more deeply.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31629/+31654 are coherent with the note.
- Schema / structure: Strong separation of peripheral TBNA, TBBx, brushings, BAL, navigation, and radial EBUS.

### note_014 — ⚠️ WARNING — 74 / 100
*Change vs prior batch-4 evaluation: +10 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucination: 31634 is not supported; the balloon occlusion here is hemostatic after cryobiopsy, not a stand-alone Chartis/air-leak assessment.
- Mismatch: Second-target/multi-lobe peripheral sampling detail is partially collapsed.
- Mismatch: EBUS evidence is partly anchored to specimen text rather than the procedural sampling sentences.

**Completeness (Recall)**
- Missed procedure: Additional-lobe transbronchial biopsy logic is underdeveloped for a true multi-target, multi-lobe case.
- Missed detail: Could preserve RLL cryobiopsy counts and the hemostatic balloon use more cleanly.

**Logic & Coding**
- CPT consistency: 31623/31624/31627/31628/31629/31653/+31654 are broadly supported. 31634 is not.
- Schema / structure: Major families are captured, but multi-target logic remains only partially preserved.

### note_015 — ⚠️ WARNING — 78 / 100
*Change vs prior batch-4 evaluation: +12 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Forceps transbronchial biopsy x5 is missed, so 31628-level lung biopsy work is undercalled.
- Missed detail: Could preserve BAL volumes (50 mL in / 18 mL out).

**Logic & Coding**
- CPT consistency: 31624/31627/31629/+31654 are supported, but 31628 is also supported and should not be omitted.
- Schema / structure: Short-note robotic recognition improved, but peripheral forceps biopsy recall is still incomplete.

### note_016 — ⚠️ WARNING — 86 / 100
*Change vs prior batch-4 evaluation: +26 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: inspection_findings implies a lesion even though the note says no lesion was seen.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve moderate-sedation meds and the improvement from continuous to intermittent bubbling.

**Logic & Coding**
- CPT consistency: 31647 is defensible for valve placement. Suppressing 31634 is reasonable in this same-session PAL valve workflow.
- Schema / structure: Main PAL valve-family capture is good; residual narrative cleanup remains.

### note_017 — ⚠️ WARNING — 80 / 100
*Change vs prior batch-4 evaluation: +1 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: number_of_valves=2 is unsupported; the note documents 3 valves.
- Mismatch: The pre-existing chest tube still leaks into postprocessing even though no chest-tube procedure occurred this session.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve LUL segment localization more explicitly.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 is arguable in this PAL localization context.
- Schema / structure: Good PAL valve-family recognition with residual quantitative cleanup.

### note_018 — ⚠️ WARNING — 78 / 100
*Change vs prior batch-4 evaluation: +0 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: number_of_valves=1 is unsupported; the note documents two valves.
- Mismatch: The target anatomy (RLL superior segment with adjacent segment valve) is not preserved.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Moderate sedation is the more defensible interpretation and is handled reasonably; anatomy remains the larger gap.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 is arguable in this PAL localization workflow.
- Schema / structure: Good main-family capture, but valve-count/anatomy detail is incomplete.

### note_019 — ⚠️ WARNING — 76 / 100
*Change vs prior batch-4 evaluation: +0 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: number_of_valves=3 is unsupported; the valve list documents 2.
- Mismatch: The target lobe/segment (RUL, especially anterior and apical segments) is not carried through cleanly.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: General anesthesia is present in the note but not surfaced in sedation.

**Logic & Coding**
- CPT consistency: 31647 is supported. 31634 is arguable in this PAL localization setting.
- Schema / structure: Recognizes the PAL valve workflow, but quantitative and anatomic detail drift remains.

### note_020 — ❌ FAIL — 50 / 100
*Change vs prior batch-4 evaluation: -2 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: 31622 is left as the bronchoscopic code even though the note explicitly says two valves were deployed.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Endobronchial valve placement for air leak control is missed entirely.
- Missed detail: Could preserve LUL localization and significant bubbling reduction.

**Logic & Coding**
- CPT consistency: 31634 may be supportable for localization, but 31647-level valve placement work is also documented and cannot be omitted.
- Schema / structure: This remains a major recall failure in a short PAL note.

### note_021 — ✅ PASS — 94 / 100
*Change vs prior batch-4 evaluation: +64 points (FAIL → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Double-lumen tube placement and sequential lavage-cycle detail are not structured, but the core procedure is correct.

**Logic & Coding**
- CPT consistency: 32997 is the defensible unilateral whole-lung lavage code family here.
- Schema / structure: Correctly distinguishes whole-lung lavage from BAL.

### note_022 — ⚠️ WARNING — 88 / 100
*Change vs prior batch-4 evaluation: +56 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: diagnostic_bronchoscopy.inspection_findings implies obstruction even though the note says no endobronchial obstruction.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve intubated ICU transport and the PAP-specific lavage workflow in more detail.

**Logic & Coding**
- CPT consistency: 32997 is the defensible primary procedure family. BAL is appropriately cleared.
- Schema / structure: Major improvement: whole-lung lavage is now correctly recognized.

### note_023 — ⚠️ WARNING — 86 / 100
*Change vs prior batch-4 evaluation: +58 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve that today's staged lavage was the right lung and carry through the aliquot/effluent sequence.

**Logic & Coding**
- CPT consistency: 32997 fits the documented unilateral total lung lavage session.
- Schema / structure: Now correctly separates whole-lung lavage from BAL, with only detail loss remaining.

### note_024 — ⚠️ WARNING — 84 / 100
*Change vs prior batch-4 evaluation: +74 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: The procedure is bucketed as pleural_biopsy even though the note describes an ultrasound-guided transthoracic core needle biopsy of a pleural-based lung/chest-wall lesion.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve local-only anesthesia and manual-pressure hemostasis more explicitly.

**Logic & Coding**
- CPT consistency: 32408 is the defensible code family here; standalone 76942 add-on logic is not needed when guidance is included.
- Schema / structure: Main family recognition is fixed, but the structural bucket is still not ideal.

### note_025 — ❌ FAIL — 18 / 100
*Change vs prior batch-4 evaluation: +0 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: US-guided transthoracic core biopsy is missed entirely.
- Missed detail: Could preserve the left lateral chest-wall target, three cores, and local-only anesthesia.

**Logic & Coding**
- CPT consistency: This note supports a percutaneous transthoracic biopsy family, not a null extraction.
- Schema / structure: Major recall failure.

### note_026 — ❌ FAIL — 28 / 100
*Change vs prior batch-4 evaluation: +4 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Dynamic bronchoscopy with forced-expiratory assessment and CPAP titration is missed entirely.
- Missed detail: Severe distal tracheal and bilateral main-bronchial collapse (>80%) and improvement with CPAP are central findings that are not structured.

**Logic & Coding**
- CPT consistency: 31622-level diagnostic bronchoscopy is the closest family, but the dynamic/CPAP study is not really represented.
- Schema / structure: This remains a major miss of the actual procedure intent.

### note_027 — ✅ PASS — 92 / 100
*Change vs prior batch-4 evaluation: +2 points (PASS → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Intralesional Kenalog injection is not structurally represented, but the core rigid bronchoscopy plus balloon dilation workflow is correct.

**Logic & Coding**
- CPT consistency: 31630 is consistent with balloon dilation of subglottic stenosis.
- Schema / structure: Core stenosis-management extraction is strong.

### note_028 — ❌ FAIL — 64 / 100
*Change vs prior batch-4 evaluation: -4 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: BAL/31624 is not supported; the note lists BAL as optional, but the performed technique documents foreign-body retrieval without lavage.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve RLL basal-segment location and basket retrieval more explicitly.

**Logic & Coding**
- CPT consistency: 31635 is supported for foreign-body removal. 31624 is not.
- Schema / structure: Main procedure family is right, but the extra BAL creates a material precision error.

### note_029 — ✅ PASS — 92 / 100
*Change vs prior batch-4 evaluation: +70 points (FAIL → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Forceps assistance and moderate-sedation detail are not richly structured, but the therapeutic aspiration event is correctly captured.

**Logic & Coding**
- CPT consistency: 31645 is strongly supported by the note.
- Schema / structure: Major improvement: the prior null extraction is fixed.

### note_030 — ⚠️ WARNING — 78 / 100
*Change vs prior batch-4 evaluation: +0 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucination: sedation.type='Moderate' is wrong; the procedure was performed under GA despite the stale header.
- Mismatch: inspection_findings implies lesion visualization even though the note says no discrete lesion was visualized because of clot burden.

**Completeness (Recall)**
- Missed procedure: Endobronchial blocker placement for hemorrhage isolation is not represented as a distinct therapeutic event.
- Missed detail: Could preserve left lower lobe source localization.

**Logic & Coding**
- CPT consistency: 31645 is supported for airway clearance/clot aspiration. The blocker placement has no clean standard code here but is still a real missed intervention.
- Schema / structure: Partial capture of a more complex hemoptysis-control workflow.

### note_031 — ❌ FAIL — 45 / 100
*Change vs prior batch-4 evaluation: -1 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: Only diagnostic bronchoscopy + balloon occlusion are represented, but the note clearly documents endobronchial Watanabe spigot placement.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Endobronchial Watanabe spigot placement for PAL is missed entirely.
- Missed detail: Could preserve RUL anterior-segment localization and secure device fit.

**Logic & Coding**
- CPT consistency: 31634 may reflect localization work, but the definitive spigot-placement intervention is not represented. Coding remains incomplete/gray-zone.
- Schema / structure: The therapeutic action is missed, leaving only the localization setup.

### note_032 — ✅ PASS — 92 / 100
*Change vs prior batch-4 evaluation: +0 points (PASS → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Balloon dilation is bundled into the same-site 31641 treatment logic; minimal oozing is appropriately not turned into a complication.

**Logic & Coding**
- CPT consistency: 31641 is consistent with laser treatment/relief of stenosis in this same-site workflow.
- Schema / structure: Strong core capture of therapeutic airway ablation.

### note_033 — ❌ FAIL — 64 / 100
*Change vs prior batch-4 evaluation: +2 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: 31636 is the wrong stent family; this is a silicone Y-stent spanning distal trachea/carina, so tracheal/Y-stent logic is more appropriate than initial bronchial-stent logic.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve explicit Y-stent sizing (tracheal 16 mm; right 12 mm; left 12 mm).

**Logic & Coding**
- CPT consistency: Stent placement plus mechanical debulking are supported. The problem is the stent-code family/location logic, not the presence of the interventions.
- Schema / structure: Recognizes the CAO workflow, but the stent family is materially wrong.

### note_034 — ❌ FAIL — 22 / 100
*Change vs prior batch-4 evaluation: +0 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Cryospray airway ablation is missed entirely.
- Missed detail: Could preserve the supraglottic/tracheal lesion sites and short-burst application pattern.

**Logic & Coding**
- CPT consistency: A therapeutic airway-ablation family is supported by the note. A null extraction is not.
- Schema / structure: Major recall failure on a rare airway intervention.

### note_035 — ✅ PASS — 93 / 100
*Change vs prior batch-4 evaluation: +75 points (FAIL → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Mild bronchospasm treated with bronchodilator is not deeply structured, but the thermoplasty session itself is correctly captured.

**Logic & Coding**
- CPT consistency: 31660 is consistent with single-lobe bronchial thermoplasty to the RLL.
- Schema / structure: Major improvement: the prior null extraction is fixed.

### note_036 — ❌ FAIL — 62 / 100
*Change vs prior batch-4 evaluation: +40 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: Simultaneous billing of 31660 and 31661 is internally inconsistent; only one thermoplasty family code should survive for a single session.
- Mismatch: The LUL/Lingula treatment geography is not resolved cleanly enough to justify both one-lobe and two-or-more-lobe codes at once.

**Completeness (Recall)**
- Missed procedures: None
- Missed details: None

**Logic & Coding**
- CPT consistency: Bronchial thermoplasty is definitely supported, but dual family billing is not.
- Schema / structure: Procedure recognition improved, but the coding logic remains materially wrong.

### note_037 — ❌ FAIL — 55 / 100
*Change vs prior batch-4 evaluation: +11 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Selective intubation/endobronchial tamponade with blocker placement is missed entirely as a therapeutic event.
- Missed detail: Could preserve the RUL bleeding source and topical vasoconstrictor use.

**Logic & Coding**
- CPT consistency: 31645 is supported for clot extraction/airway clearance, but the key tamponade maneuver is omitted.
- Schema / structure: Partial capture of a much more complex massive-hemoptysis intervention.

### note_038 — ❌ FAIL — 30 / 100
*Change vs prior batch-4 evaluation: +0 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Bronchoscopic methylene-blue evaluation for tracheoesophageal fistula is missed entirely.
- Missed detail: Could preserve mid-tracheal posterior-wall fistula localization and GI-coordinated esophageal dye instillation.

**Logic & Coding**
- CPT consistency: At minimum this is a diagnostic bronchoscopy/fistula-evaluation workflow; a null extraction is inadequate.
- Schema / structure: Rare diagnostic procedure still missed.

### note_039 — ✅ PASS — 92 / 100
*Change vs prior batch-4 evaluation: +2 points (PASS → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Pass count for station 7 is not explicitly preserved.
- Missed detail: General anesthesia is documented but not surfaced in sedation.

**Logic & Coding**
- CPT consistency: 31652 and 76982 are supportable from the documented two-station EBUS-TBNA with elastography mapping.
- Schema / structure: Good linear-EBUS plus elastography separation.

### note_040 — ⚠️ WARNING — 72 / 100
*Change vs prior batch-4 evaluation: +14 points (FAIL → WARNING).*
**Accuracy (Precision)**
- Hallucination: Simultaneous 31652 and 43238 coding for the same EUS-B sampling episode may be duplicative/gray-zone rather than cleanly cumulative.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve that both sampled stations had 3 passes each inside node_events, not only in the separate eus_b block.

**Logic & Coding**
- CPT consistency: The note supports a two-station EUS-B/convex-ultrasound sampling workflow, but the dual-code output still needs manual review.
- Schema / structure: Much better than the prior run, but not yet fully clean on coding logic.

### note_041 — ⚠️ WARNING — 82 / 100
*Change vs prior batch-4 evaluation: -2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: Large cast extraction with cryoprobe/forceps is collapsed into generic therapeutic aspiration, which understates the extraction technique.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve R main bronchus cast removal and RLL fragment clearance more explicitly.

**Logic & Coding**
- CPT consistency: 31645 is defensible for major cast/airway clearance, though the structural detail is light.
- Schema / structure: Reasonable family capture with technique under-resolution.

### note_042 — ❌ FAIL — 42 / 100
*Change vs prior batch-4 evaluation: -8 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: Complications/bleeding grade 1 are unsupported; the note says complications none and only minimal mucosal bleeding was controlled routinely.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Debulking/removal of obstructing fungal material is not represented as the main therapeutic action.
- Missed detail: Could preserve RUL bronchus target and endobronchial debris specimen handling.

**Logic & Coding**
- CPT consistency: 31624 is supported for BAL, but this note also documents 31641-type therapeutic airway work that is omitted.
- Schema / structure: This case worsened: the therapeutic intervention is still missed and routine bleeding is overcalled as a complication.

### note_043 — ❌ FAIL — 28 / 100
*Change vs prior batch-4 evaluation: +0 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Bronchoscopic brachytherapy-catheter placement is missed entirely.
- Missed detail: Could preserve left main bronchus target lesion and radiation-oncology handoff.

**Logic & Coding**
- CPT consistency: No obvious standard CPT conclusion is required to score this case; a null procedural extraction still misses the documented intervention.
- Schema / structure: Rare adjunctive airway procedure remains unrecognized.

### note_044 — ❌ FAIL — 55 / 100
*Change vs prior batch-4 evaluation: +7 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: 31622 is not cleanly supported in addition to 31615 for bronchoscopy through an established tracheostomy.
- Hallucination: airway_abnormalities='Secretions' is unsupported; the note says the trachea was clear with mild granulation at the stoma.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Tracheostomy tube exchange is missed as a distinct performed procedure.
- Missed details: None

**Logic & Coding**
- CPT consistency: 31615 is supported. The trach change itself is real procedural work even if a separate CPT conclusion is gray-zone here.
- Schema / structure: Partial capture of the bronchoscopic route, but the exchange component is omitted.

### note_045 — ❌ FAIL — 42 / 100
*Change vs prior batch-4 evaluation: +0 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Limited laryngeal/airway inspection with vocal-cord motion assessment is missed entirely.
- Missed detail: Could preserve paradoxical inspiratory adduction and the absence of significant subglottic stenosis.

**Logic & Coding**
- CPT consistency: The exact CPT is not the main issue here; the note still documents a real endoscopic airway-evaluation procedure that should not be blank.
- Schema / structure: This remains a null extraction for a performed diagnostic airway evaluation.

### note_046 — ❌ FAIL — 38 / 100
*Change vs prior batch-4 evaluation: +0 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: Pressure at the stoma is carried as an outcomes complication intervention even though the note states 'complications none' and describes routine mild bleeding control.
- Mismatch: None

**Completeness (Recall)**
- Missed procedure: Bronchoscopy-assisted transtracheal oxygen catheter exchange is missed entirely as the main intervention.
- Missed details: None

**Logic & Coding**
- CPT consistency: A standalone diagnostic bronchoscopy code does not capture the documented catheter-exchange procedure.
- Schema / structure: Rare airway-device management workflow remains undercalled.

### note_047 — ⚠️ WARNING — 80 / 100
*Change vs prior batch-4 evaluation: +2 points (WARNING → WARNING).*
**Accuracy (Precision)**
- Hallucination: stent_brand='ENT' is unsupported and appears to be a substring artifact from the word 'stent'.
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve mucus-plugging context more explicitly.

**Logic & Coding**
- CPT consistency: 31638 and 31640 are supportable for stent revision/removal plus granulation debulking.
- Schema / structure: Core rigid bronchoscopy/stent-removal workflow is captured with a minor string hallucination.

### note_048 — ✅ PASS — 92 / 100
*Change vs prior batch-4 evaluation: +2 points (PASS → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Topical mitomycin C adjunct is not structurally represented, but the core dilation case is correct.

**Logic & Coding**
- CPT consistency: 31630 is consistent with tracheal stenosis balloon dilation.
- Schema / structure: Strong core extraction in an ultra-short note.

### note_049 — ❌ FAIL — 58 / 100
*Change vs prior batch-4 evaluation: +2 points (FAIL → FAIL).*
**Accuracy (Precision)**
- Hallucination: 32604 is the wrong thoracoscopy code family; local coding rules point medical thoracoscopy/pleuroscopy with pleural biopsies toward the 32650 family.
- Mismatch: Pleural drain placement from the procedure list is not carried as a performed action.

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Could preserve biopsy count (x6) and diffuse pleural nodularity/thickening.

**Logic & Coding**
- CPT consistency: Thoracoscopy with pleural biopsies is supported, as is chest ultrasound localization. The drain placement is adjunctive/bundled; the main error is the thoracoscopy code selection.
- Schema / structure: Pleural procedural family is recognized, but the code-family choice and drain recall are off.

### note_050 — ✅ PASS — 94 / 100
*Change vs prior batch-4 evaluation: +0 points (PASS → PASS).*
**Accuracy (Precision)**
- Hallucinations: None
- Mismatch: None

**Completeness (Recall)**
- Missed procedures: None
- Missed detail: Exact tPA/DNase doses are variably documented and are appropriately not hallucinated.

**Logic & Coding**
- CPT consistency: 32561 is consistent with first-session intrapleural fibrinolytic instillation via existing chest tube.
- Schema / structure: Clean pleural-procedure extraction.

