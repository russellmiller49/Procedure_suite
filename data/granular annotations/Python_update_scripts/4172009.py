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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definition
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 4172009
# ------------------------------------------
id_1 = "4172009"
text_1 = """Ruth Cooper, MRN [REDACTED], a 62-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Presbyterian Hospital on [REDACTED]. The indication was peripheral nodule and bilateral hilar adenopathy with a 21.6mm ground-glass lesion in the RUL anterior (B3), bronchus sign negative. The patient was ASA class 3 with smoking history of 41 pack-years (former). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Fujifilm EB-580S bronchoscope with 22-gauge Standard FNA needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 10L (13.0mm, 3 passes, ROSE: Malignant - NSCLC NOS); station 4L (15.7mm, 2 passes, ROSE: Adequate lymphocytes); station 11L (19.4mm, 2 passes, ROSE: Malignant - small cell carcinoma). Rapid on-site evaluation was available for all stations.

The Ion robotic bronchoscopy system (Intuitive Surgical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 1.8mm. The robotic catheter was advanced to the RUL anterior (B3) and radial EBUS probe deployment revealed eccentric view of the lesion. Tool-in-lesion was confirmed by cbct. Transbronchial forceps biopsies (8 specimens), transbronchial needle aspiration (4 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed granuloma.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 85 minutes. Attending physician: Robert Patel, MD."""

entities_1 = [
    # Procedure & Methods
    {"label": "PROC_METHOD",       **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "Ion robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD",       **get_span(text_1, "radial EBUS", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "PROC_ACTION",       **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # Indications & Lesions
    {"label": "OBS_LESION",        **get_span(text_1, "peripheral nodule", 1)},
    {"label": "OBS_LESION",        **get_span(text_1, "bilateral hilar adenopathy", 1)},
    {"label": "OBS_LESION",        **get_span(text_1, "ground-glass lesion", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "21.6mm", 1)},
    
    # Anatomy
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "station 10L", 1)},
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "station 4L", 1)},
    {"label": "ANAT_LN_STATION",   **get_span(text_1, "station 11L", 1)},
    {"label": "ANAT_LUNG_LOC",     **get_span(text_1, "RUL anterior (B3)", 2)},

    # Devices
    {"label": "MEAS_SIZE",         **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "endotracheal tube", 1)}, # Often mapped to ANAT_AIRWAY if generic, but size implies device
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "Fujifilm EB-580S bronchoscope", 1)},
    {"label": "DEV_NEEDLE",        **get_span(text_1, "22-gauge", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "robotic catheter", 1)},

    # Measurements (Sizes & Counts)
    {"label": "MEAS_SIZE",         **get_span(text_1, "13.0mm", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "15.7mm", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "19.4mm", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "2 passes", 2)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "1.8mm", 1)}, # Registration error, fits generic size measure
    {"label": "MEAS_COUNT",        **get_span(text_1, "8 specimens", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_COUNT",        **get_span(text_1, "(2)", 1)}, # brushings (2)

    # Observations (ROSE)
    {"label": "OBS_ROSE",          **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    {"label": "OBS_ROSE",          **get_span(text_1, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE",          **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    {"label": "OBS_ROSE",          **get_span(text_1, "granuloma", 1)},

    # Outcomes & Context
    {"label": "CTX_HISTORICAL",    **get_span(text_1, "former", 1)}, # smoking history modifier
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    {"label": "SPECIMEN",          **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN",          **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",          **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN",          **get_span(text_1, "cultures", 1)},
    {"label": "CTX_TIME",          **get_span(text_1, "85 minutes", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)