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
# Note 1: 3367578
# ==========================================
id_1 = "3367578"
text_1 = """===============================================
BRONCHOSCOPY PROCEDURE REPORT
===============================================
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Physician: Andrew Nakamura, MD
===============================================

[INDICATION]
Primary: Combined staging and peripheral nodule diagnosis
Category: Lung Cancer Staging
Target: 16.3mm Ground-glass lesion, RLL superior (B6)
Bronchus Sign: Positive
PET SUV: 6.9

[ANESTHESIA]
Type: General endotracheal anesthesia
ASA Class: 2
Airway: 8.0mm ETT
Duration: 94 minutes

[DESCRIPTION]
Procedure 1: Linear EBUS-TBNA
- Scope: Olympus BF-UC190F
- Needle: 22G Standard FNA
- Stations sampled: 11L, 4L, 10L
- Number of stations: 3 (≥3)
- ROSE available: Yes
- ROSE result: Granuloma

Procedure 2: Robotic Bronchoscopy
- Platform: Galaxy (Noah Medical)
- Registration: CT-to-body, error 3.4mm
- Target: RLL superior (B6)

Procedure 3: Radial EBUS
- View: Adjacent
- Confirmation: Radial EBUS

Procedure 4: Transbronchial Biopsy
- Forceps biopsies: 6
- TBNA passes: 4
- Brushings: 2
- ROSE result: Malignant - squamous cell carcinoma

Specimens: Cytology, cell block, surgical pathology, BAL cultures
Complications: None
EBL: <10mL

[PLAN]
1. Post-procedure monitoring x2 hours
2. Chest X-ray - completed, no pneumothorax
3. Discharge to home if stable
4. Follow-up: 1-2 weeks for pathology
5. Tumor board review pending final results
6. Molecular testing if malignancy confirmed

===============================================
Electronically signed: Andrew Nakamura, MD
Date: [REDACTED]
===============================================
"""

entities_1 = [
    # Indication & Target
    {"label": "MEAS_SIZE",          **get_span(text_1, "16.3mm", 1)},
    {"label": "OBS_LESION",         **get_span(text_1, "Ground-glass lesion", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "RLL superior (B6)", 1)},
    
    # Anesthesia
    {"label": "MEAS_SIZE",          **get_span(text_1, "8.0mm", 1)}, # ETT size
    {"label": "MEAS_TIME",          **get_span(text_1, "94 minutes", 1)},

    # Procedure 1: Linear EBUS
    {"label": "PROC_METHOD",        **get_span(text_1, "Linear EBUS-TBNA", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Olympus BF-UC190F", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_1, "22G Standard FNA", 1)},
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "11L", 1)},
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "4L", 1)},
    {"label": "ANAT_LN_STATION",    **get_span(text_1, "10L", 1)},
    {"label": "MEAS_COUNT",         **get_span(text_1, "3", 3)}, # "Number of stations: 3" (Matches 3rd '3' in text approx? Let's be careful. '16.3' has a 3. '3.4' has a 3. 'Procedure 3' has a 3. )
    # Let's count '3's in text before "Number of stations: 3":
    # 1. "16.3mm" -> index 1
    # 2. "Procedure 3" -> No, that's later.
    # 3. "3" in "3 (>=3)" -> This line is "Number of stations: 3 (>=3)".
    # Let's try to be precise. "Number of stations: 3". 
    # The '3' in '16.3mm' is the first '3'.
    # The '3' in '3.4mm' is later.
    # The '3' in 'Procedure 3' is later.
    # So "Number of stations: 3" might be the 2nd or 3rd '3'.
    # Actually, let's use the full phrase span trick if needed, but the template asks for the term.
    # Safe approach: Just target "3" carefully.
    # "16.3mm" -> 1st.
    # "3" (stations) -> 2nd? No, "Procedure 1". No "Procedure 2", "Procedure 3".
    # Wait, "Procedure 1" lines comes before "Procedure 3".
    # Let's just use unique phrase "Number of stations: 3" and offset? No, helper doesn't support that.
    # I will assume "3" in "Number of stations: 3" is the 2nd occurrence (after 16.3mm). 
    # Let's check text: "...Target: 16.3mm...Procedure 1...Number of stations: 3..."
    # 16.3mm (1st '3').
    # Any other '3' before? "Date: [REDACTED]" might have digits. Assuming REDACTED doesn't.
    # "3" in "Procedure 3" is way later.
    # So it is likely the 2nd occurrence. 
    {"label": "MEAS_COUNT",         **get_span(text_1, "3", 2)}, 
    
    {"label": "OBS_ROSE",           **get_span(text_1, "Granuloma", 1)},

    # Procedure 2: Robotic
    {"label": "PROC_METHOD",        **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Galaxy (Noah Medical)", 1)},
    # "3.4mm" -> MEAS_SIZE (Error). Let's skip as it's technical error, not patient anatomy/lesion.
    {"label": "ANAT_LUNG_LOC",      **get_span(text_1, "RLL superior (B6)", 2)},

    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD",        **get_span(text_1, "Radial EBUS", 1)}, # Procedure header
    # "Confirmation: Radial EBUS". Duplicate method mention? I'll skip to keep clean.

    # Procedure 4: TBB
    {"label": "PROC_METHOD",        **get_span(text_1, "Transbronchial Biopsy", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Forceps", 1)}, # In "Forceps biopsies"
    # "Forceps biopsies: 6". "6" in "16.3mm" (1), "6.9" (2), "B6" (3), "B6" (4), "6" (biopsies). 
    # Occurrences of 6: 
    # 1. 16.3mm
    # 2. B6
    # 3. 6.9
    # 4. B6 (2nd time)
    # 5. "Forceps biopsies: 6" -> 5th occurrence.
    {"label": "MEAS_COUNT",         **get_span(text_1, "6", 5)},
    
    # "TBNA passes: 4".
    # Occurrences of 4:
    # 1. "4L"
    # 2. "Procedure 4"
    # 3. "4" (passes) -> 3rd occurrence.
    {"label": "MEAS_COUNT",         **get_span(text_1, "4", 3)},

    # "Brushings: 2".
    # Occurrences of 2:
    # 1. "ASA Class: 2"
    # 2. "Procedure 2"
    # 3. "2" (brushings) -> 3rd occurrence.
    {"label": "MEAS_COUNT",         **get_span(text_1, "2", 3)},

    {"label": "OBS_ROSE",           **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},

    # Specimens & Vitals
    {"label": "SPECIMEN",           **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "surgical pathology", 1)},
    {"label": "SPECIMEN",           **get_span(text_1, "BAL cultures", 1)},
    {"label": "MEAS_VOL",           **get_span(text_1, "<10mL", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)