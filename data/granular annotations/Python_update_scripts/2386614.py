import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
    
    if start == -1:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 2386614_syn_1
# ==========================================
t1 = """Pre-op: 14mm LUL nodule. 
Anesthesia: GA, 8.0 ETT.
Procedure:
- Monarch robot nav to LB1+2.
- rEBUS: Adjacent view.
- Sampling: 21G TBNA (x6), Forceps (x6), Protected Brush.
- ROSE: No malignancy.
Complications: None.
Plan: Recovery, D/C if stable."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "(x6)", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "(x6)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Protected Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "No malignancy", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2386614_syn_2
# ==========================================
t2 = """OPERATIVE NARRATIVE: The patient was brought to the endoscopy suite for evaluation of a 14mm peripheral pulmonary nodule in the Apicoposterior Segment of the Left Upper Lobe. Following induction of general anesthesia, the Monarch robotic platform was deployed. Electromagnetic navigation was registered with an error of 4.6mm. Upon reaching the target, radial EBUS demonstrated an adjacent acoustic signature. Transbronchial needle aspiration (21G), forceps biopsy, and cytological brushing were performed under continuous visualization. Rapid On-Site Evaluation (ROSE) was negative for malignant neoplasm. Hemostasis was achieved without intervention."""

e2 = [
    {"label": "MEAS_SIZE", **get_span(t2, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "peripheral pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Apicoposterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Left Upper Lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Monarch robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Electromagnetic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "21G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "cytological brushing", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "negative for malignant neoplasm", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2386614_syn_3
# ==========================================
t3 = """Procedure: Bronchoscopy with Computer-Assisted Navigation (31627) and EBUS (31654).
Target: LUL Nodule (14mm).
Technique:
1. Navigated to LB1+2 using electromagnetic guidance.
2. Confirmed target via rEBUS (Adjacent).
3. TBNA: 21G needle, 6 passes (31629).
4. Biopsy: Standard forceps, 6 samples (31628).
5. Brushing: Protected brush (31623).
Outcome: Samples to patho. ROSE negative."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Computer-Assisted Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "electromagnetic guidance", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "6 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "6 samples", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Brushing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Protected brush", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "negative", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2386614_syn_4
# ==========================================
t4 = """Resident Note
Pt: [REDACTED].
Proc: Robotic Bronch LUL.
Steps:
1. Time out. GA induced. ETT 8.0.
2. Monarch scope inserted. Registration 4.6mm error.
3. Navigated to LUL (Apicoposterior).
4. rEBUS confirmed lesion (adjacent).
5. TBNA x6, Bx x6, Brush x1.
6. ROSE: No malignancy.
7. Pt tolerated well.
Plan: CXR, D/C."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Monarch scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "Apicoposterior", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "OBS_LESION", **get_span(t4, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Bx", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x6", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x1", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "No malignancy", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2386614_syn_5
# ==========================================
t5 = """Procedure note for Mr [REDACTED] we did the robotic bronch today for that LUL nodule. General anesthesia tube size 8.0 registration was okay 4.6mm. Went out to the apicoposterior segment found it with rebus adjacent view. Did the needle biopsy 21 gauge then the forceps then the brush. ROSE said no cancer seen. No bleeding really. Extubated fine sent to recovery check a chest xray."""

e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "apicoposterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rebus", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsy", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "21 gauge", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "no cancer seen", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2386614_syn_6
# ==========================================
t6 = """The patient underwent robotic bronchoscopy for a 14mm LUL nodule under general anesthesia with an 8.0 ETT. The Monarch system was navigated to the apicoposterior segment of the LUL. Radial EBUS confirmed the lesion with an adjacent view. Sampling included transbronchial needle aspiration with a 21G needle (6 passes), forceps biopsy (6 specimens), and protected brushings. Continuous visualization was maintained. ROSE result showed no evidence of malignancy. The patient tolerated the procedure without complications."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Monarch system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "apicoposterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LUL", 2)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t6, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "6 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "protected brushings", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "no evidence of malignancy", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2386614_syn_7
# ==========================================
t7 = """[Indication]
Peripheral pulmonary nodule, LUL (14mm).
[Anesthesia]
General, 8.0 ETT.
[Description]
Monarch robotic navigation to LB1+2. rEBUS: Adjacent. Sampling performed: 21G TBNA, Forceps biopsy, Protected Brush. Continuous visualization confirmed tool exit. ROSE: No evidence of malignant neoplasm.
[Plan]
Post-procedure CXR. Discharge if stable."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Peripheral pulmonary nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LUL", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "14mm", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Monarch robotic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LB1+2", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Protected Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "No evidence of malignant neoplasm", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2386614_syn_8
# ==========================================
t8 = """[REDACTED] biopsy of a 14mm nodule in the left upper lobe. We induced general anesthesia and secured the airway. Using the Monarch robotic system, we navigated to the apicoposterior segment. We confirmed the location with radial EBUS, which showed the lesion adjacent to the airway. We then proceeded to sample the area using a 21-gauge needle, followed by standard forceps biopsies and a brush. The on-site pathologist saw no evidence of malignancy in the preliminary review. The procedure was completed without any immediate complications."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "left upper lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Monarch robotic system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "apicoposterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lesion", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "21-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "no evidence of malignancy", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2386614_syn_9
# ==========================================
t9 = """Operation: Robotic-assisted bronchoscopy.
Target: LUL nodule.
Action: The device was steered to the LUL apicoposterior segment. rEBUS verified the target. The lesion was aspirated with a 21G needle, sampled with forceps, and brushed. Visual confirmation of tool deployment was maintained.
Result: ROSE indicated no malignancy. No trauma noted.
Plan: Recovery."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Robotic-assisted", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "apicoposterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rEBUS", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "sampled", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "brushed", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "no malignancy", 1)}
]
BATCH_DATA.append({"id": "2386614_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2386614
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: 7/1/1972
Date: [REDACTED] || Location: [REDACTED]
Attending: CAPT Russell Miller, MD

Indication: Peripheral pulmonary nodule
Target: 14mm nodule in LUL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
VCV\t13\t354\t18\t100\t5\t17

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 4.6mm.

The device was navigated to the LUL. The outer sheath was parked and locked at the ostium of the segmental airway (LB1+2) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Apicoposterior Segment of LUL.

Radial EBUS performed via the working channel. rEBUS view: Adjacent. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 21G aspiration needle under direct endoscopic and fluoroscopic guidance. 6 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 6 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

ROSE Result: No evidence of malignant neoplasm

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Miller, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Peripheral pulmonary nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "OBS_LESION", **get_span(t10, "endobronchial lesions", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Monarch robotic endoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "lobar carinas", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB1+2", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Apicoposterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Lesion", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "6 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Protected cytology brushings", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "No evidence of malignant neoplasm", 1)}
]
BATCH_DATA.append({"id": "2386614", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)