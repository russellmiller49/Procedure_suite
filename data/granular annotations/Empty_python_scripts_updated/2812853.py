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
# Note 1: 2812853
# ==========================================
t1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Steven Park, MD
Fellow: Jason Park
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 60 years
Sex: Male
ASA Class: 3

PRE-PROCEDURE:
1. Patient id[REDACTED] confirmed with two id[REDACTED]
2. Informed consent verified on chart
3. NPO status confirmed (>8 hours)
4. Anticoagulation status reviewed - not on anticoagulation
5. Allergies reviewed - NKDA
6. Time-out performed with all team members

INDICATION:
PET-avid lung mass and mediastinal lymphadenopathy
Target lesion: 30.9mm ground-glass nodule, RUL anterior (B3)
Bronchus sign: Negative

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: 22G FNB/ProCore
- Robotic platform: Monarch (Auris Health (J&J))
- Radial EBUS: 20 MHz miniprobe
- Biopsy forceps: Standard
- Cytology brushes: Standard

PROCEDURE STEPS:

PART A - LINEAR EBUS FOR STAGING:
1. Bronchoscope inserted through ETT
2. Standard airway inspection performed - airways patent, no endobronchial lesions
3. Linear EBUS scope exchanged
4. Systematic lymph node survey performed
5. Following stations id[REDACTED] and sampled:
   - Station 4L: 18.3mm, 2 passes
   - Station 10R: 14.8mm, 4 passes
   - Station 4R: 20.9mm, 4 passes
   - Station 7: 24.0mm, 2 passes
6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - NSCLC NOS

PART B - ROBOTIC NAVIGATION:
1. Monarch system prepared and registered
2. Registration error: 2.0mm (acceptable)
3. Robotic catheter advanced to RUL anterior (B3)
4. Radial EBUS deployed - Adjacent view obtained
5. Tool-in-lesion confirmed with Fluoroscopy
6. Sampling performed:
   - Forceps biopsies: 6
   - TBNA passes: 4
   - Brushings: 2
7. ROSE performed - Granuloma
8. BAL obtained from RUL

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 4L, 10R, 4R, 7) → Cytology, cell block
2. TBBx RUL → Surgical pathology
3. Brushings → Cytology
4. BAL → Cultures (bacterial, fungal, AFB)

COMPLICATIONS: None
ESTIMATED BLOOD LOSS: <10 mL

IMPRESSION:
1. Completed EBUS-TBNA mediastinal staging
2. Completed robotic bronchoscopy with peripheral lung biopsy
3. No immediate complications

PLAN:
1. Monitor in recovery x 2 hours
2. Discharge home if stable
3. Follow-up in clinic for pathology results
4. Results to be discussed at tumor board

Procedure performed under direct supervision of [REDACTED], MD

[REDACTED], PGY-6
Steven Park, MD (Attending - present for entire procedure)"""

e1 = [
    # Indication
    {"label": "OBS_LESION",         **get_span(t1, "lung mass", 1)},
    {"label": "OBS_FINDING",        **get_span(t1, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE",          **get_span(t1, "30.9mm", 1)},
    {"label": "OBS_LESION",         **get_span(t1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "anterior (B3)", 1)},
    
    # Equipment
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Pentax EB-1990i", 1)},
    {"label": "DEV_NEEDLE",         **get_span(t1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE",         **get_span(t1, "22G", 1)},
    {"label": "DEV_NEEDLE",         **get_span(t1, "FNB/ProCore", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Robotic platform", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "20 MHz miniprobe", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Cytology brushes", 1)},

    # Procedure Part A (Linear EBUS)
    {"label": "PROC_METHOD",        **get_span(t1, "Linear EBUS", 2)}, # Header 'PART A - LINEAR EBUS'
    {"label": "ANAT_LN_STATION",    **get_span(t1, "Station 4L", 1)},
    {"label": "MEAS_SIZE",          **get_span(t1, "18.3mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "2", 1)}, # 2 passes (4L)
    {"label": "ANAT_LN_STATION",    **get_span(t1, "Station 10R", 1)},
    {"label": "MEAS_SIZE",          **get_span(t1, "14.8mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "4", 1)}, # 4 passes (10R)
    {"label": "ANAT_LN_STATION",    **get_span(t1, "Station 4R", 1)},
    {"label": "MEAS_SIZE",          **get_span(t1, "20.9mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "4", 2)}, # 4 passes (4R)
    {"label": "ANAT_LN_STATION",    **get_span(t1, "Station 7", 1)},
    {"label": "MEAS_SIZE",          **get_span(t1, "24.0mm", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "2", 2)}, # 2 passes (7)
    {"label": "OBS_ROSE",           **get_span(t1, "ROSE", 1)},
    {"label": "OBS_FINDING",        **get_span(t1, "Malignant", 1)},
    {"label": "OBS_FINDING",        **get_span(t1, "NSCLC NOS", 1)},

    # Procedure Part B (Robotic)
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Monarch", 1)},
    {"label": "MEAS_SIZE",          **get_span(t1, "2.0mm", 1)}, # Registration error
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "anterior (B3)", 2)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "Radial EBUS", 2)},
    {"label": "PROC_METHOD",        **get_span(t1, "Forceps biopsies", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "6", 1)},
    {"label": "PROC_METHOD",        **get_span(t1, "TBNA passes", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "4", 3)}, # TBNA passes: 4
    {"label": "PROC_METHOD",        **get_span(t1, "Brushings", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "2", 3)}, # Brushings: 2
    {"label": "OBS_ROSE",           **get_span(t1, "ROSE", 2)},
    {"label": "OBS_FINDING",        **get_span(t1, "Granuloma", 1)},
    {"label": "PROC_METHOD",        **get_span(t1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "RUL", 3)},

    # Specimens
    {"label": "PROC_METHOD",        **get_span(t1, "EBUS-TBNA", 1)}, # In 'Specimens Sent'
    {"label": "ANAT_LN_STATION",    **get_span(t1, "4L", 2)},
    {"label": "ANAT_LN_STATION",    **get_span(t1, "10R", 2)},
    {"label": "ANAT_LN_STATION",    **get_span(t1, "4R", 2)},
    {"label": "ANAT_LN_STATION",    **get_span(t1, "7", 2)}, # "Station 7" -> find "7" inside
    {"label": "SPECIMEN",           **get_span(t1, "cell block", 1)},
    {"label": "PROC_METHOD",        **get_span(t1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "RUL", 4)},
    {"label": "SPECIMEN",           **get_span(t1, "Brushings", 2)},
    {"label": "SPECIMEN",           **get_span(t1, "BAL", 2)},
    
    # Other
    {"label": "MEAS_VOL",           **get_span(t1, "10 mL", 1)},
]

BATCH_DATA.append({"id": "2812853", "text": t1, "entities": e1})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)