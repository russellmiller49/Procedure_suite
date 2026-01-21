import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 217055_syn_1
# ==========================================
t1 = """Indication: Lung mass + LN.\nProc: EBUS TBNA 4R -> ROSE pos. Nav Bronch RUL mass -> Biopsy.\nDx: Adeno."""
e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Lung mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "LN", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "pos", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Nav Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "Biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Adeno", 1)},
]
BATCH_DATA.append({"id": "217055_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 217055_syn_2
# ==========================================
t2 = """EBUS-TBNA performed at Station 4R. ROSE positive for malignancy. Electromagnetic navigation utilized to reach RUL lesion. Target biopsied. Diagnosis: Adenocarcinoma."""
e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "Station 4R", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "positive for malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Electromagnetic navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsied", 1)},
    {"label": "OBS_LESION", **get_span(t2, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "217055_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 217055_syn_3
# ==========================================
t3 = """Codes: 31629 (Needle asp), 31627 (Nav), 31620 (EBUS). \nTarget 1: 4R (ROSE+).\nTarget 2: ENB -> RUL mass. \nDx: Adenocarcinoma."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Needle asp", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "4R", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "+", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "ENB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "217055_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 217055_syn_4
# ==========================================
t4 = """Dr. Liu EBUS Case:\n1. 4R node -> ROSE malignant.\n2. Navigated to RUL mass.\n3. Biopsy confirmed Adeno."""
e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "node", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "malignant", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Adeno", 1)},
]
BATCH_DATA.append({"id": "217055_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 217055_syn_5
# ==========================================
t5 = """liu ebus 4r 2 passes rose positive. navigated to right upper lobe nodule biopsy done. adeno."""
e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "ebus", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "4r", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "positive", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t5, "adeno", 1)},
]
BATCH_DATA.append({"id": "217055_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 217055_syn_6
# ==========================================
t6 = """Endobronchial ultrasound guided transbronchial needle aspiration of Station 4R performed. ROSE assessment showed malignancy. Electromagnetic navigation bronchoscopy used to localize RUL mass. Transbronchial biopsy performed. Final path: Adenocarcinoma."""
e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "Station 4R", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Electromagnetic navigation bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Transbronchial biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "217055_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 217055_syn_7
# ==========================================
t7 = """[Indication]
Lymphadenopathy + RUL Mass.
[Anesthesia]
General.
[Procedures]
1. EBUS-TBNA 4R (ROSE pos).
2. Nav Bronch RUL (Biopsy).
[Dx]
Adenocarcinoma."""
e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "Lymphadenopathy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Mass", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4R", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "pos", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Nav Bronch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 2)},
    {"label": "PROC_ACTION", **get_span(t7, "Biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "217055_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 217055_syn_8
# ==========================================
t8 = """Procedure Note: We used the ultrasound scope to look at the lymph node (4R). Put a needle in and took a sample. The cells looked bad (cancer). Then we navigated to the right upper lobe mass with the biopsy tool. Biopsied it. Confirmed cancer."""
e8 = [
    {"label": "DEV_INSTRUMENT", **get_span(t8, "ultrasound scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "lymph node", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "4R", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "Put a needle in", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "took a sample", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "bad", 1)},
    {"label": "OBS_LESION", **get_span(t8, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "biopsy tool", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "Biopsied", 1)},
    {"label": "OBS_LESION", **get_span(t8, "cancer", 2)},
]
BATCH_DATA.append({"id": "217055_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 217055_syn_9
# ==========================================
t9 = """Technique: EBUS-TBNA and ENB-Guided Biopsy.
Target 1: Station 4R. Result: Malignant (ROSE).
Target 2: RUL Mass. Action: TBBx.
Pathology: Adenocarcinoma."""
e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "ENB", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "Station 4R", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "Malignant", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "TBBx", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Adenocarcinoma", 1)},
]
BATCH_DATA.append({"id": "217055_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 217055
# ==========================================
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
DATE: [REDACTED]
PHYSICIAN: Dr. James Liu, MD

**INDICATION:**
Patient with history of smoking found to have RUL nodule on CT. PET scan showed uptake in RUL nodule and Station 4R lymph node. Plan for EBUS and Navigation for staging and diagnosis.

**PROCEDURE:**
1.  **EBUS-TBNA:**
    * Station 4R (Right Lower Paratracheal): Identified heterogeneous node.
    * Needle: 22ga Olympus ViziShot.
    * Passes: 3 passes obtained.
    * ROSE: Positive for malignancy (Adenocarcinoma).
    * Staging: N2 disease confirmed.

2.  **Electromagnetic Navigation (ENB):**
    * System: Veran SpinView.
    * Target: RUL posterior segment mass.
    * Navigation successful to target.
    * Tools: Cytology brush and biopsy forceps.
    * Samples: 5 biopsies taken.
    * Diagnosis: Confirmed Adenocarcinoma.

**FINDINGS:**
* Normal vocal cord function.
* Trachea and main carina patent.
* Secretions: Minimal.

**PLAN:**
* Oncology referral for Stage IIIA NSCLC.
* Discharge home."""
e10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "lymph node", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "EBUS", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "Right Lower Paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "node", 2)},
    {"label": "DEV_NEEDLE", **get_span(t10, "Needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22ga", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Positive for malignancy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Adenocarcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Electromagnetic Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "ENB", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Veran SpinView", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL posterior segment", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Cytology brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "biopsy forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 biopsies", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Adenocarcinoma", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Secretions", 1)},
]
BATCH_DATA.append({"id": "217055", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)