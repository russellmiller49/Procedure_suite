import json

# The content of the script to be generated
script_content = """import sys
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
# Case 1: 3786812
# ==========================================
id_1 = "3786812"
text_1 = \"\"\"Linda Rivera, MRN [REDACTED], a 50-year-old male underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Memorial Hospital on [REDACTED]. The indication was right upper lobe mass with ipsilateral mediastinal nodes with a 31.9mm ground-glass lesion in the LLL anteromedial basal (B7+8), bronchus sign negative, PET SUV max 13.4. The patient was ASA class 3 with smoking history of 57 pack-years (current). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Pentax EB-1990i bronchoscope with 22-gauge Acquire needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 11L (21.6mm, 4 passes, ROSE: Suspicious for malignancy); station 2L (14.5mm, 4 passes, ROSE: Suspicious for malignancy); station 7 (21.8mm, 3 passes, ROSE: Adequate lymphocytes); station 11R (15.0mm, 3 passes, ROSE: Malignant - small cell carcinoma); station 10R (21.4mm, 4 passes, ROSE: Adequate lymphocytes, no malignancy). Rapid on-site evaluation was available for all stations.

The Ion robotic bronchoscopy system (Intuitive Surgical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 3.2mm. The robotic catheter was advanced to the LLL anteromedial basal (B7+8) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by fluoroscopy. Transbronchial forceps biopsies (6 specimens), transbronchial needle aspiration (3 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed suspicious for malignancy.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 119 minutes. Attending physician: Maria Santos, MD.\"\"\"

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "LATERALITY", **get_span(text_1, "ipsilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL anteromedial basal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B7+8", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Acquire", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "small cell carcinoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "no malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CT-to-body registration", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3.2mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL anteromedial basal", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B7+8", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "Tool-in-lesion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "suspicious for malignancy", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Specimens", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "119 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
"""

with open("add_case_3786812.py", "w") as f:
    f.write(script_content)

print("Script 'add_case_3786812.py' generated successfully.")