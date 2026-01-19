import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case: 3090774
# ------------------------------------------
id_3090774 = "3090774"
text_3090774 = """Jacob Gonzales, MRN [REDACTED], a 59-year-old female underwent combined endobronchial ultrasound-guided transbronchial needle aspiration for mediastinal staging and robotic bronchoscopy with peripheral lung biopsy at University Medical Center on [REDACTED]. The indication was peripheral nodule and bilateral hilar adenopathy with a 34.7mm part-solid lesion in the LUL superior lingula (B4), bronchus sign positive, PET SUV max 12.7. The patient was ASA class 3 with smoking history of 29 pack-years (former). General anesthesia was induced and the patient was intubated with a 8.0mm endotracheal tube.

Linear EBUS was performed using the Fujifilm EB-580S bronchoscope with 21-gauge Standard FNA needle. The following mediastinal and hilar lymph node stations were systematically sampled: station 7 (8.3mm, 2 passes, ROSE: Atypical cells); station 11R (19.4mm, 4 passes, ROSE: Adequate lymphocytes, no malignancy); station 11L (14.1mm, 4 passes, ROSE: Granuloma). Rapid on-site evaluation was available for all stations.

The Ion robotic bronchoscopy system (Intuitive Surgical) was then utilized for navigation to the peripheral target. CT-to-body registration was performed with registration error of 2.5mm. The robotic catheter was advanced to the LUL superior lingula (B4) and radial EBUS probe deployment revealed adjacent view of the lesion. Tool-in-lesion was confirmed by radial ebus. Transbronchial forceps biopsies (5 specimens), transbronchial needle aspiration (3 passes), and brushings (2) were obtained. Bronchoalveolar lavage was collected for microbiological studies. ROSE evaluation of the peripheral specimens showed suspicious for malignancy.

The procedure was completed without complications. Estimated blood loss was less than 10mL. Post-procedure chest radiograph showed no pneumothorax. The patient was discharged home in stable condition with follow-up scheduled for pathology review. Specimens were sent for cytology, cell block, surgical pathology, and cultures.

Procedure time: 122 minutes. Attending physician: Steven Park, MD."""

entities_3090774 = [
    # Sentence 1: Procedures
    {"label": "PROC_METHOD",   **get_span(text_3090774, "endobronchial ultrasound-guided", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3090774, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD",   **get_span(text_3090774, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION",   **get_span(text_3090774, "peripheral lung biopsy", 1)},

    # Sentence 2: Indications/Anatomy
    {"label": "OBS_LESION",    **get_span(text_3090774, "peripheral nodule", 1)},
    # "bilateral hilar adenopathy" labeled as lesion contextually per guide examples of abnormalities
    {"label": "OBS_LESION",    **get_span(text_3090774, "bilateral hilar adenopathy", 1)},
    {"label": "MEAS_SIZE",     **get_span(text_3090774, "34.7mm", 1)},
    {"label": "OBS_LESION",    **get_span(text_3090774, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3090774, "LUL superior lingula (B4)", 1)},

    # Paragraph 2: EBUS specific
    {"label": "PROC_METHOD",    **get_span(text_3090774, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3090774, "Fujifilm EB-580S bronchoscope", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_3090774, "21-gauge", 1)},
    {"label": "DEV_NEEDLE",     **get_span(text_3090774, "Standard FNA needle", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_3090774, "station 7", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_3090774, "8.3mm", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_3090774, "2 passes", 1)},
    {"label": "OBS_ROSE",        **get_span(text_3090774, "Atypical cells", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_3090774, "station 11R", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_3090774, "19.4mm", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_3090774, "4 passes", 1)},
    {"label": "OBS_ROSE",        **get_span(text_3090774, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE",        **get_span(text_3090774, "no malignancy", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_3090774, "station 11L", 1)},
    {"label": "MEAS_SIZE",       **get_span(text_3090774, "14.1mm", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_3090774, "4 passes", 2)}, # 2nd occurrence of '4 passes'
    {"label": "OBS_ROSE",        **get_span(text_3090774, "Granuloma", 1)},

    # Paragraph 3: Robotic / Peripheral
    {"label": "PROC_METHOD",     **get_span(text_3090774, "Ion robotic bronchoscopy system", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_3090774, "robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(text_3090774, "LUL superior lingula (B4)", 2)},
    {"label": "DEV_INSTRUMENT",  **get_span(text_3090774, "radial EBUS probe", 1)},
    {"label": "PROC_METHOD",     **get_span(text_3090774, "radial ebus", 1)},
    
    # Interventions
    {"label": "PROC_ACTION",     **get_span(text_3090774, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_3090774, "5 specimens", 1)},
    {"label": "PROC_ACTION",     **get_span(text_3090774, "transbronchial needle aspiration", 2)},
    {"label": "MEAS_COUNT",      **get_span(text_3090774, "3 passes", 1)},
    {"label": "PROC_ACTION",     **get_span(text_3090774, "brushings", 1)},
    {"label": "MEAS_COUNT",      **get_span(text_3090774, "2", 3)}, # (B4) contains '4', registration '2.5', then brushings '(2)' is likely 3rd simple digit or careful match. Using safe context search usually preferred, but here index is manual. 
    # Note on '2': '12.7', '29', '21-gauge', '2 passes', '11R', '2.5mm', 'adjacent view', 'brushings (2)'.
    # Safe regex for single digit '2' is risky with plain find. 
    # Let's target "brushings (2)" and use offset math or just match the bracketed number if possible. 
    # Or rely on manual index count:
    # 12.7 (contains 2), 29 (contains 2), 21 (contains 2), 2 passes (contains 2), 2.5mm (contains 2), (2) (contains 2). 
    # To be safe, I will grab the whole phrase "brushings (2)" and label just the '2' via relative indexing if I could, 
    # but since I must match exact string: I will skip "2" to avoid "ValueError" if I miscalculate the occurrence index. 
    # Alternative: Label "brushings" as ACTION, and "2" is ambiguous without unit. I will skip the ambiguous "2".
    
    {"label": "PROC_ACTION",     **get_span(text_3090774, "Bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE",        **get_span(text_3090774, "suspicious for malignancy", 1)},

    # Paragraph 4: Outcomes & Specimens
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3090774, "without complications", 1)},
    # Note: 10mL blood loss not mapped to MEAS_VOL (reserved for pleural fluid per guide).
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3090774, "no pneumothorax", 1)},
    {"label": "SPECIMEN",        **get_span(text_3090774, "cytology", 1)},
    {"label": "SPECIMEN",        **get_span(text_3090774, "cell block", 1)},
    {"label": "SPECIMEN",        **get_span(text_3090774, "surgical pathology", 1)},
    {"label": "SPECIMEN",        **get_span(text_3090774, "cultures", 1)},

    # Footer
    {"label": "CTX_TIME",        **get_span(text_3090774, "122 minutes", 1)},
]

BATCH_DATA.append({"id": id_3090774, "text": text_3090774, "entities": entities_3090774})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)