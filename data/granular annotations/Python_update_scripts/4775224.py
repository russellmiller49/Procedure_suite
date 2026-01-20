import sys
from pathlib import Path

# ==============================================================================
# SETUP: Repo Root & Imports
# ==============================================================================
# Adjust the REPO_ROOT path calculation if this script is placed elsewhere.
# Assuming this runs from a subdirectory like 'data/processed' or similar.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of a specific occurrence of a case-sensitive term.
    Raises ValueError if the term is not found the specified number of times.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
    return {"start": start, "end": start + len(term)}

# ==============================================================================
# CASE: 4775224
# ==============================================================================
id_4775224 = "4775224"
text_4775224 = """Carolyn Thomas, MRN [REDACTED], a 64-year-old male underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Presbyterian Hospital on [REDACTED]. The indication was lung cancer staging - suspected nsclc with mediastinal lymphadenopathy with a 15.4mm ground-glass lesion in the RML lateral (B4), bronchus sign positive, PET SUV max 4.3. The patient was ASA class 2 with smoking history of 47 pack-years (former). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Fujifilm EB-580S bronchoscope with 21-gauge Standard FNA needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 10R (15.1mm, 3 passes, ROSE: Adequate lymphocytes); station 4L (21.5mm, 2 passes, ROSE: Adequate lymphocytes, no malignancy); station 4R (12.6mm, 2 passes, ROSE: Suspicious for malignancy); station 11L (22.8mm, 4 passes, ROSE: Adequate lymphocytes, no malignancy). Rapid on-site evaluation was available for all stations.

The Monarch robotic bronchoscopy system (Auris Health (J&J)) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 2.5mm. The robotic catheter was advanced to the RML lateral (B4) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by radial ebus. Transbronchial forceps biopsies (7 specimens), transbronchial needle aspiration (4 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed atypical cells.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 105 minutes. Attending physician: Brian O'Connor, MD."""

entities_4775224 = [
    # --- Paragraph 1 ---
    # "endobronchial ultrasound" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_4775224, "endobronchial ultrasound", 1)},
    # "transbronchial needle aspiration" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(text_4775224, "transbronchial needle aspiration", 1)},
    # "robotic bronchoscopy" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_4775224, "robotic bronchoscopy", 1)},
    # "biopsy" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(text_4775224, "biopsy", 1)},
    # "mediastinal lymphadenopathy" -> OBS_LESION
    {"label": "OBS_LESION", **get_span(text_4775224, "mediastinal lymphadenopathy", 1)},
    # "15.4mm" -> MEAS_SIZE (Lesion size)
    {"label": "MEAS_SIZE", **get_span(text_4775224, "15.4mm", 1)},
    # "ground-glass lesion" -> OBS_LESION
    {"label": "OBS_LESION", **get_span(text_4775224, "ground-glass lesion", 1)},
    # "RML lateral (B4)" -> ANAT_LUNG_LOC
    {"label": "ANAT_LUNG_LOC", **get_span(text_4775224, "RML lateral (B4)", 1)},

    # --- Paragraph 2 ---
    # "Linear EBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_4775224, "Linear EBUS", 1)},
    # "21-gauge" -> DEV_NEEDLE
    {"label": "DEV_NEEDLE", **get_span(text_4775224, "21-gauge", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_4775224, "station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4775224, "15.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4775224, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4775224, "Adequate lymphocytes", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_4775224, "station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4775224, "21.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4775224, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4775224, "Adequate lymphocytes, no malignancy", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_4775224, "station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4775224, "12.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4775224, "2 passes", 2)}, # Second occurrence of "2 passes"
    {"label": "OBS_ROSE", **get_span(text_4775224, "Suspicious for malignancy", 1)},
    
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_4775224, "station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4775224, "22.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4775224, "4 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4775224, "Adequate lymphocytes, no malignancy", 2)}, # Second occurrence
    
    # --- Paragraph 3 ---
    # "robotic bronchoscopy" -> PROC_METHOD (Found as "robotic bronchoscopy system", using "robotic bronchoscopy" to map to method)
    {"label": "PROC_METHOD", **get_span(text_4775224, "robotic bronchoscopy", 2)},
    # "robotic catheter" -> DEV_INSTRUMENT
    {"label": "DEV_INSTRUMENT", **get_span(text_4775224, "robotic catheter", 1)},
    # "RML lateral (B4)" -> ANAT_LUNG_LOC (Re-navigated)
    {"label": "ANAT_LUNG_LOC", **get_span(text_4775224, "RML lateral (B4)", 2)},
    # "radial EBUS" -> PROC_METHOD
    {"label": "PROC_METHOD", **get_span(text_4775224, "radial EBUS", 1)},
    # "forceps" -> DEV_INSTRUMENT
    {"label": "DEV_INSTRUMENT", **get_span(text_4775224, "forceps", 1)},
    # "biopsies" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(text_4775224, "biopsies", 1)},
    # "7 specimens" -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(text_4775224, "7 specimens", 1)},
    # "transbronchial needle aspiration" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(text_4775224, "transbronchial needle aspiration", 2)},
    # "4 passes" -> MEAS_COUNT
    {"label": "MEAS_COUNT", **get_span(text_4775224, "4 passes", 2)},
    # "brushings" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(text_4775224, "brushings", 1)},
    # "Bronchoalveolar lavage" -> PROC_ACTION
    {"label": "PROC_ACTION", **get_span(text_4775224, "Bronchoalveolar lavage", 1)},
    # "atypical cells" -> OBS_ROSE
    {"label": "OBS_ROSE", **get_span(text_4775224, "atypical cells", 1)},
    
    # --- Paragraph 4 ---
    # "no pneumothorax" -> OUTCOME_COMPLICATION
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4775224, "no pneumothorax", 1)},
    # "cell block" -> SPECIMEN
    {"label": "SPECIMEN", **get_span(text_4775224, "cell block", 1)},
    
    # --- Footer ---
    # "105 minutes" -> CTX_TIME
    {"label": "CTX_TIME", **get_span(text_4775224, "105 minutes", 1)},
]

BATCH_DATA.append({"id": id_4775224, "text": text_4775224, "entities": entities_4775224})

# ==============================================================================
# EXECUTION
# ==============================================================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)