import sys
from pathlib import Path

# Set the repository root directory (assuming this script runs inside the 'scripts' or similar subfolder)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports from specific modules
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2880089_syn_1
# ==========================================
t1 = """Target: 17mm nodule Lingula (LB5).
Tech: Ion, rEBUS (Concentric), CBCT.
Action: TBNA (21G/23G x3). BAL (80cc).
ROSE: Suspicious for malignancy.
Disp: Outpatient."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "17mm", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x3", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "80cc", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Suspicious for malignancy", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2880089_syn_2
# ==========================================
t2 = """PROCEDURE: [REDACTED] to the suite for biopsy of a 17mm Lingular nodule (LB5). The Ion robotic system was employed. Navigation was verified with a concentric radial EBUS view and Cone Beam CT. Transbronchial needle aspiration was performed with 21G and 23G needles. A bronchoalveolar lavage was also performed. ROSE was suspicious for malignancy."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "17mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Lingular", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Ion robotic system", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "23G", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "suspicious for malignancy", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2880089_syn_3
# ==========================================
t3 = """Billing Codes: 31629 (TBNA), 31624 (BAL), +31627 (Nav), +31654 (rEBUS).
Location: Lingula (LB5).
Tools: Ion, Cios Spin (CBCT).
Note: No brush or cryo performed. Indication suspected malignancy."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "BAL", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Cios Spin", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "CBCT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "cryo", 1)},
    {"label": "OBS_LESION", **get_span(t3, "suspected malignancy", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2880089_syn_4
# ==========================================
t4 = """Resident Note
Pt: [REDACTED]
Staff: Dr. Kim

1. Ion nav to Lingula LB5.
2. rEBUS: Concentric.
3. CBCT: Confirmed.
4. Bx: TBNA (21/23G), BAL.
5. ROSE: Suspicious.
6. Stable."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Ion nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Bx", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "21/23G", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Suspicious", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2880089_syn_5
# ==========================================
t5 = """amy campbell procedure note. 17mm nodule in the lingula lb5. used ion robot. radial ebus concentric. cone beam ct looked good. did 3 needle passes and a bal. pathologist says suspicious for cancer. no bleeding."""

e5 = [
    {"label": "MEAS_SIZE", **get_span(t5, "17mm", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lb5", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ion robot", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "radial ebus", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "cone beam ct", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "3", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "bal", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "suspicious for cancer", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no bleeding", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2880089_syn_6
# ==========================================
t6 = """Robotic navigation bronchoscopy (Ion) for 17mm Lingula nodule (LB5). Registration error 2.0mm. Radial EBUS: Concentric. Cone Beam CT: Confirmed. Sampling: TBNA (21G/23G, 3 passes) and BAL. ROSE: Suspicious for malignancy. No complications."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Robotic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Ion", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "17mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "3 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "Suspicious for malignancy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2880089_syn_7
# ==========================================
t7 = """[Indication]
Suspected malignancy, 17mm Lingula.
[Anesthesia]
General.
[Description]
Ion nav to Inferior Lingula (LB5). rEBUS: Concentric. CBCT: Confirmed. 
- TBNA
- BAL
ROSE: Suspicious.
[Plan]
Outpatient discharge."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Suspected malignancy", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "17mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Ion nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "CBCT", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "Suspicious", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2880089_syn_8
# ==========================================
t8 = """[REDACTED] a robotic bronchoscopy for a 17mm nodule in the inferior Lingula. We navigated to LB5 using the Ion system, confirming position with concentric radial EBUS and Cone Beam CT. We performed needle aspiration and a lavage. The on-site pathologist reported cells suspicious for malignancy."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "robotic bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "17mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Ion system", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Cone Beam CT", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "suspicious for malignancy", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2880089_syn_9
# ==========================================
t9 = """Operation: Robotic-assisted bronchoscopy.
Focus: Inferior Lingula (LB5).
Checks: rEBUS (Concentric) and CBCT.
Intervention: The lesion was sampled via needle aspiration and lavage. ROSE indicated suspicion of malignancy."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Robotic-assisted bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "CBCT", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "sampled", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "suspicion of malignancy", 1)}
]
BATCH_DATA.append({"id": "2880089_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2880089 (Original)
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Rachel Kim
Fellow: Dr. James Liu (PGY-5)

Indication: Suspected lung malignancy
Target: 17mm nodule in Lingula

PROCEDURE:

After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings:

The endotracheal tube is in good position. The visualized portion of the trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy are normal; there are no endobronchial lesions.

Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), RML Carina (RC2), Right Mainstem, Left Mainstem, LUL Lingula Carina (LC1) from mucus.

CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target. The navigational plan was reviewed and verified. This was then loaded into robotic bronchoscopy platform.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t12\t346\t13\t100\t8\t22

Robotic navigation bronchoscopy was performed with Ion platform. Partial registration was used. Registration error: 2.0mm. Ion robotic catheter was used to engage the Inferior Lingula (LB5). Target lesion is approximately 17mm in diameter. Under navigational guidance the Ion robotic catheter was advanced to 1.7cm away from the planned target.

Radial EBUS was performed to confirm lesion location. rEBUS view: Concentric. Continuous margin noted.

Needle was advanced into the lesion. Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation. Cios Spin system was used for evaluation of nodule location. Low dose spin was performed to acquire CT imaging. This was passed on to Ion platform system for reconstruction and nodule location. The 3D images were interpreted on an independent workstation (Ion). I personally interpreted the cone beam CT and 3-D reconstruction.

Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location. Vision probe removed for biopsy; catheter position maintained via shape-sensing lock. Repeat imaging confirmed tool-in-lesion.

Transbronchial needle aspiration was performed with 21G and 23G Needle through the extended working channel catheter. Total 3 samples were collected. Samples sent for Cytology and Cell block.

Bronchoalveolar lavage was performed at Inferior Lingula (LB5). Instilled 80cc of NS, suction returned with 37cc of NS. Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

ROSE Result: Atypical cells present, suspicious for malignancy

Vision probe was re-inserted to inspect the airway. No significant bleeding observed. The catheter was retracted. Final airway inspection showed no complications.

The patient tolerated the procedure well without immediate complications.

DISPOSITION: Recovery, then discharge if stable. CXR to rule out pneumothorax.
Follow-up: Results conference in 5-7 days.

Kim, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Suspected lung malignancy", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "17mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)}, # "Trachea" (Capitalized) appears only once in the text (cleaning section). 
    # {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)}, # Removed: Not found in text.
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)}, 
    {"label": "ANAT_AIRWAY", **get_span(t10, "RML Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RC2", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Right Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Left Mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LUL Lingula Carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "LC1", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Robotic navigation bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Ion platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Inferior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB5", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "17mm", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Cone Beam CT", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Cios Spin system", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "23G", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3 samples", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Inferior Lingula", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB5", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "80cc", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "37cc", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Atypical cells present, suspicious for malignancy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no complications", 1)}
]
BATCH_DATA.append({"id": "2880089", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")