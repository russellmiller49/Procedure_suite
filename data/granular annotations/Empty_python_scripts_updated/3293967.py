import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts module
# Usage: add_case(case_id, text, entities, repo_root)
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure you are running this script from the correct location within the repository.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact string to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' indices, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Occurrence not found
            
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3293967
# ==========================================
id_1 = "3293967"
text_1 = """Jack Brooks, MRN [REDACTED], a 54-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at Regional Medical Center on [REDACTED]. The indication was peripheral lung nodule with suspicious mediastinal nodes with a 19.4mm solid lesion in the RUL anterior (B3), bronchus sign positive, PET SUV max 6.7. The patient was ASA class 2 with smoking history of 54 pack-years (former). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Olympus BF-UC180F bronchoscope with 19-gauge FNB/ProCore needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 10R (21.2mm, 2 passes, ROSE: Malignant - adenocarcinoma); station 2L (8.8mm, 2 passes, ROSE: Atypical cells); station 11L (13.8mm, 3 passes, ROSE: Adequate lymphocytes, no malignancy). Rapid on-site evaluation was available for all stations.

The Monarch robotic bronchoscopy system (Auris Health (J&J)) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 1.5mm. The robotic catheter was advanced to the RUL anterior (B3) and radial EBUS probe deployment revealed concentric view of the lesion. Tool-in-lesion was confirmed by augmented fluoroscopy. Transbronchial forceps biopsies (6 specimens), transbronchial needle aspiration (3 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed granuloma.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 131 minutes. Attending physician: Eric Johnson, MD."""

entities_1 = [
    # Procedure Methods
    {"label": "PROC_METHOD", **get_span(text_1, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic bronchoscopy system", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "augmented fluoroscopy", 1)},

    # Procedure Actions
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "CT-to-body registration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)}, # Inside "forceps biopsies"
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},

    # Anatomy
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal nodes", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 2L", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "station 11L", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},

    # Devices / Instruments
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "endotracheal tube", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC180F bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "FNB/ProCore needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},

    # Measurements (Size, Count, Time)
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 5)}, # In "brushings (2)"
    {"label": "CTX_TIME", **get_span(text_1, "131 minutes", 1)},
    
    # Observations (Lesions, Findings, ROSE)
    {"label": "OBS_LESION", **get_span(text_1, "peripheral lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchus sign positive", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "peripheral target", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric view", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 3)}, # "view of the lesion"
    {"label": "OBS_ROSE", **get_span(text_1, "granuloma", 1)},

    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cultures", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        # Filter out any entities that failed to match (None) to prevent runtime errors
        valid_entities = [e for e in case["entities"] if "start" in e and e["start"] is not None]
        
        # Report missed entities for debugging
        if len(valid_entities) < len(case["entities"]):
            print(f"Warning: {len(case['entities']) - len(valid_entities)} entities failed to match in case {case['id']}.")
        
        add_case(case["id"], case["text"], valid_entities, REPO_ROOT)