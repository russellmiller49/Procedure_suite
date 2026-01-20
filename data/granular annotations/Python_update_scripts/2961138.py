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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2961138
# ==========================================
id_1 = "2961138"
text_1 = """Brian Cruz, MRN [REDACTED], a 80-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Memorial Hospital on [REDACTED]. The indication was combined staging and peripheral nodule diagnosis with a 16.3mm part-solid lesion in the RUL anterior (B3), bronchus sign positive, PET SUV max 12.4. The patient was ASA class 4 with smoking history of 27 pack-years (former). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Olympus BF-UC180F bronchoscope with 21-gauge Standard FNA needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 2L (19.0mm, 2 passes, ROSE: Malignant - adenocarcinoma); station 10L (22.7mm, 4 passes, ROSE: Malignant - adenocarcinoma); station 7 (16.8mm, 4 passes, ROSE: Adequate lymphocytes, no malignancy). Rapid on-site evaluation was available for all stations.

The Monarch robotic bronchoscopy system (Auris Health (J&J)) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 3.0mm. The robotic catheter was advanced to the RUL anterior (B3) and radial EBUS probe deployment revealed eccentric view of the lesion. Tool-in-lesion was confirmed by augmented fluoroscopy. Transbronchial forceps biopsies (6 specimens), transbronchial needle aspiration (2 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed malignant - adenocarcinoma.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 75 minutes. Attending physician: Maria Santos, MD."""

entities_1 = [
    # --- Paragraph 1 ---
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.3mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B3", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign positive", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},

    # --- Paragraph 2 ---
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    
    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 2)},
    
    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},

    # --- Paragraph 3 ---
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic bronchoscopy system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B3", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "eccentric view", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "malignant", 1)}, # lowercase

    # --- Paragraph 4 & Footer ---
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "75 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)