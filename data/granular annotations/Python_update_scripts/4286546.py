import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 4286546
# ==========================================

text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Eric Johnson, MD
Fellow: Priya Sharma
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 49 years
Sex: Female
ASA Class: 2

PRE-PROCEDURE:
1. Patient id[REDACTED] confirmed with two id[REDACTED]
2. Informed consent verified on chart
3. NPO status confirmed (>8 hours)
4. Anticoagulation status reviewed - not on anticoagulation
5. Allergies reviewed - NKDA
6. Time-out performed with all team members

INDICATION:
Peripheral lung nodule with suspicious mediastinal nodes
Target lesion: 19.4mm solid nodule, RUL anterior (B3)
Bronchus sign: Positive

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Olympus BF-UC180F
- EBUS needle: 19G FNB/ProCore
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
   - Station 10R: 21.2mm, 2 passes
   - Station 2L: 8.8mm, 2 passes
   - Station 11L: 13.8mm, 3 passes

6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - adenocarcinoma

PART B - ROBOTIC NAVIGATION:
1. Monarch system prepared and registered
2. Registration error: 1.5mm (acceptable)
3. Robotic catheter advanced to RUL anterior (B3)
4. Radial EBUS deployed - Concentric view obtained
5. Tool-in-lesion confirmed with Augmented fluoroscopy
6. Sampling performed:
   - Forceps biopsies: 6
   - TBNA passes: 3
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
1. EBUS-TBNA (stations 10R, 2L, 11L) → Cytology, cell block
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

Procedure performed under direct supervision of Eric Johnson, MD

Priya Sharma, PGY-5
Eric Johnson, MD (Attending - present for entire procedure)"""

entities_1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    
    # Anesthesia/Airway
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    
    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Olympus BF-UC180F", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},
    
    # Procedure - Part A
    {"label": "PROC_METHOD", **get_span(text_1, "LINEAR EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "airways", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 1)},
    
    # Procedure - Part B
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 2)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    # Using specific context for "2" to avoid mismatch with "20 MHz", "21.2mm" etc.
    {"label": "MEAS_COUNT", "start": text_1.find("Brushings: 2") + 11, "end": text_1.find("Brushings: 2") + 12}, 
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    
    # Post Procedure / Specimens
    # Changed "Airways" occurrence from 2 to 1 (only one Capitalized "Airways" exists)
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airways", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    
    # Impression
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 2)},
]

BATCH_DATA.append({"id": "4286546", "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)