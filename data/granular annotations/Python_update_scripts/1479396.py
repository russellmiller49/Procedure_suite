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
# 3. Data Definitions
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 1494096
# ------------------------------------------
id_1 = "1494096"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: David Kim, MD
Fellow: Marcus Williams
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 49 years
Sex: Male
ASA Class: 4

PRE-PROCEDURE:
1. Patient id[REDACTED] confirmed with two id[REDACTED]
2. Informed consent verified on chart
3. NPO status confirmed (>8 hours)
4. Anticoagulation status reviewed - not on anticoagulation
5. Allergies reviewed - NKDA
6. Time-out performed with all team members

INDICATION:
PET-avid lung mass and mediastinal lymphadenopathy
Target lesion: 20.0mm solid nodule, RML medial (B5)
Bronchus sign: Negative

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Olympus BF-UC190F
- EBUS needle: 22G Acquire
- Robotic platform: Ion (Intuitive Surgical)
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
   - Station 2L: 13.8mm, 4 passes
   - Station 4R: 23.9mm, 3 passes
   - Station 11R: 19.6mm, 3 passes
   - Station 11L: 17.4mm, 2 passes
6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - small cell carcinoma

PART B - ROBOTIC NAVIGATION:
1. Ion system prepared and registered
2. Registration error: 2.5mm (acceptable)
3. Robotic catheter advanced to RML medial (B5)
4. Radial EBUS deployed - Adjacent view obtained
5. Tool-in-lesion confirmed with Augmented fluoroscopy
6. Sampling performed:
   - Forceps biopsies: 7
   - TBNA passes: 2
   - Brushings: 2
7. ROSE performed - Malignant - NSCLC NOS
8. BAL obtained from RML

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 2L, 4R, 11R, 11L) → Cytology, cell block
2. TBBx RML → Surgical pathology
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

Procedure performed under direct supervision of David Kim, MD

Marcus Williams, PGY-6
David Kim, MD (Attending - present for entire procedure)"""

entities_1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.0mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "solid nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 1)},
    
    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)}, # ETT size
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    
    # Equipment
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC190F", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G Acquire", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},
    
    # Procedure Part A
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "airways", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    
    # Procedure Part B
    {"label": "PROC_METHOD", **get_span(text_1, "Ion system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.5mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML medial (B5)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 1)}, # Forceps count
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)}, # Corrected: 1st occurrence in text (Part B)
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 3)}, # "BAL obtained from RML"
    
    # Post Procedure / Specimens / Impression
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airways", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 4)}, # "TBBx RML"
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)}, # Corrected: 2nd occurrence in text (Specimens)
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)}, # Specimens section
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}, # "COMPLICATIONS: None"
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 2)}, # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No immediate complications", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)