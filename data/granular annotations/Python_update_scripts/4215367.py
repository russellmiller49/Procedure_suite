import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Case 1: 4215367_syn_1
# ==========================================
t1 = """Dx: Nodule Lingula (LB5).
Proc: Ion Nav Bronch + Bx.
Findings: rEBUS Eccentric.
Action: Locked catheter. TBNA (21G/23G x4). Cryo (1.7mm x6). Brush x2.
ROSE: Adenocarcinoma.
Comp: None."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "(LB5)", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion Nav Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Bx", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x4", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Cryo", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "1.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x2", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_1", "text": t1, "entities": e1})

# ==========================================
# Case 2: 4215367_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: [REDACTED] an 11mm nodule in the Lingula (Inferior segment, LB5). Under general anesthesia, the Ion robotic catheter was navigated to the target with a registration error of 2.5mm. Radial EBUS revealed an eccentric view of the lesion. Following shape-sensing lock, transbronchial needle aspiration (21G/23G), cryobiopsy (1.7mm), and brushing were performed. Rapid On-Site Evaluation (ROSE) was positive for malignant cells consistent with adenocarcinoma."""

e2 = [
    {"label": "MEAS_SIZE", **get_span(t2, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Inferior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Ion robotic catheter", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "23G", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "1.7mm", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "brushing", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_2", "text": t2, "entities": e2})

# ==========================================
# Case 3: 4215367_syn_3
# ==========================================
t3 = """Service: Bronchoscopy with Navigation (+31627), REBUS (+31654), TBNA (31629), Cryo (31628), Brush (31623).
Location: Lingula (LB5).
Indication: 11mm nodule, prior malignancy.
Device: Ion Robotic System.
Verification: Eccentric rEBUS view.
Samples: 4 TBNA, 6 Cryo, 2 Brush.
Pathology: Malignant (Adenocarcinoma)."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "Bronchoscopy with Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "REBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Cryo", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Brush", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LB5", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t3, "prior malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Ion Robotic System", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "Eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "4", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(t3, "6", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Cryo", 2)},
    {"label": "MEAS_COUNT", **get_span(t3, "2", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Brush", 2)},
    {"label": "OBS_ROSE", **get_span(t3, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "Adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_3", "text": t3, "entities": e3})

# ==========================================
# Case 4: 4215367_syn_4
# ==========================================
t4 = """Procedure: Ion Bronchoscopy
Patient: [REDACTED]
Target: Lingula (LB5)

Steps:
1. Navigated to LB5.
2. rEBUS: Eccentric.
3. Locked catheter.
4. TBNA x4, Cryo x6, Brush x2.
5. ROSE: Adenocarcinoma.
6. No bleeding.

Plan: Oncology referral."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Ion Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LB5", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LB5", 2)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x4", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Cryo", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x6", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x2", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No bleeding", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_4", "text": t4, "entities": e4})

# ==========================================
# Case 5: 4215367_syn_5
# ==========================================
t5 = """kevin jackson here for biopsy of that lingula nodule in lb5. used the ion robot navigation went pretty smooth. radial ebus showed it eccentric but good margin. locked the arm and took samples. used both needles 21 and 23 then the cryo probe and a brush. pathologist in the room said it looks like adenocarcinoma. pulled out no bleeding. recovery then home."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lingula", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lb5", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ion robot navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "radial ebus", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "21", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "23", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "cryo probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no bleeding", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_5", "text": t5, "entities": e5})

# ==========================================
# Case 6: 4215367_syn_6
# ==========================================
t6 = """Robotic navigation bronchoscopy (Ion) for 11mm Lingula nodule (LB5). Registration error 2.5mm. Radial EBUS: Eccentric. Catheter locked. Sampling: TBNA (21G/23G, 4 passes), Cryobiopsy (1.7mm, 6 samples), Brush (2 samples). ROSE: Malignant cells, consistent with adenocarcinoma. No complications."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Robotic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Ion", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "11mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "4 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "1.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "6 samples", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "2 samples", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "adenocarcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_6", "text": t6, "entities": e6})

# ==========================================
# Case 7: 4215367_syn_7
# ==========================================
t7 = """[Indication]
11mm nodule Lingula, prior malignancy.
[Anesthesia]
General.
[Description]
Ion nav to Inferior Lingula (LB5). rEBUS: Eccentric. 
- TBNA (21G/23G)
- Cryo (1.7mm)
- Brush
ROSE: Adenocarcinoma.
[Plan]
Outpatient discharge. Oncology."""

e7 = [
    {"label": "MEAS_SIZE", **get_span(t7, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Lingula", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t7, "prior malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Ion nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "23G", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Cryo", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "1.7mm", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "Adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_7", "text": t7, "entities": e7})

# ==========================================
# Case 8: 4215367_syn_8
# ==========================================
t8 = """The patient, [REDACTED], underwent a robotic bronchoscopy to investigate an 11mm nodule in the inferior Lingula. We navigated the Ion catheter to LB5 and confirmed the lesion location with an eccentric radial EBUS signal. We obtained multiple samples using needles, a cryoprobe, and a brush. Unfortunately, the immediate pathology evaluation indicated adenocarcinoma. The procedure was otherwise uncomplicated."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "robotic bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "inferior Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Ion catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "needles", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "cryoprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_8", "text": t8, "entities": e8})

# ==========================================
# Case 9: 4215367_syn_9
# ==========================================
t9 = """Operation: Robotic-assisted airway endoscopy.
Site: Inferior Lingula (LB5).
Guidance: Ion shape-sensing and radial EBUS (Eccentric).
Sampling: The lesion was aspirated (TBNA), frozen (Cryobiopsy), and brushed. ROSE confirmed adenocarcinoma. The airway was inspected and found clear."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Robotic-assisted airway endoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Ion shape-sensing", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "frozen", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Cryobiopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "brushed", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "adenocarcinoma", 1)}
]
BATCH_DATA.append({"id": "4215367_syn_9", "text": t9, "entities": e9})

# ==========================================
# Case 10: 4215367
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Robert Martinez
Fellow: Dr. James Liu (PGY-5)

Indication: Pulmonary nodule in patient with prior malignancy
Target: 11mm nodule in Lingula

PROCEDURE:

After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings:

The endotracheal tube is in good position. The visualized portion of the trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy are normal; there are no endobronchial lesions.

Successful therapeutic aspiration was performed to clean out the Bronchus Intermedius, Right Mainstem, RUL Carina (RC1), Left Carina (LC2) from mucus.

CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target. The navigational plan was reviewed and verified. This was then loaded into robotic bronchoscopy platform.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
VCV\t12\t320\t9\t80\t5\t18

Robotic navigation bronchoscopy was performed with Ion platform. Full registration was used. Registration error: 2.5mm. Ion robotic catheter was used to engage the Inferior Lingula (LB5). Target lesion is approximately 11mm in diameter. Under navigational guidance the Ion robotic catheter was advanced to 1.3cm away from the planned target.

Radial EBUS was performed to confirm lesion location. rEBUS view: Eccentric. Continuous margin noted.

The robotic arm was actively locked to maintain rigidity. Vision probe was unlocked and removed from the working channel, leaving the outer catheter locked in position via shape-sensing technology.

Transbronchial needle aspiration was performed with 21G and 23G Needle through the extended working channel catheter. Total 4 samples were collected. Samples sent for Cytology and Cell block.

Transbronchial cryobiopsy was performed with 1.7mm cryoprobe via the extended working channel catheter. Freeze time of 5 seconds was used. Total 6 samples were collected. Samples sent for Pathology.

Transbronchial brushing was performed with protected cytology brush through the extended working channel catheter. Total 2 samples were collected. Samples sent for Cytology.

ROSE Result: Malignant cells id[REDACTED], consistent with adenocarcinoma

Vision probe was re-inserted to inspect the airway. No significant bleeding observed. The catheter was retracted. Final airway inspection showed no complications.

The patient tolerated the procedure well without immediate complications.

DISPOSITION: Recovery, then discharge if stable. CXR to rule out pneumothorax.
Follow-up: Results conference in 5-7 days.

Martinez, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Pulmonary nodule", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t10, "prior malignancy", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Bronchus Intermedius", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RUL Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RC1", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LC2", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Robotic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion platform", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB5", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "11mm", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion robotic catheter", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Eccentric", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Vision probe", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "4 samples", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial cryobiopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.7mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "cryoprobe", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "5 seconds", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "6 samples", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial brushing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "cytology brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "2 samples", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "adenocarcinoma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Vision probe", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No significant bleeding", 1)}
]
BATCH_DATA.append({"id": "4215367", "text": t10, "entities": e10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)