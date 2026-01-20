import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Case 1: 5183641
# ==========================================
id_1 = "5183641"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Eric Johnson, MD
Fellow: N/A
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 47 years
Sex: Female
ASA Class: 3

PRE-PROCEDURE:
1. Patient id[REDACTED] confirmed with two id[REDACTED]
2. Informed consent verified on chart
3. NPO status confirmed (>8 hours)
4. Anticoagulation status reviewed - not on anticoagulation
5. Allergies reviewed - NKDA
6. Time-out performed with all team members

INDICATION:
Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy
Target lesion: 19.5mm solid nodule, RLL posterior basal (B10)
Bronchus sign: Positive

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Fujifilm EB-580S
- EBUS needle: 19G FNB/ProCore
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
   - Station 10R: 11.4mm, 3 passes
   - Station 7: 8.1mm, 3 passes
   - Station 2R: 13.6mm, 2 passes
   - Station 4R: 22.2mm, 3 passes
6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - adenocarcinoma

PART B - ROBOTIC NAVIGATION:
1. Ion system prepared and registered
2. Registration error: 3.2mm (acceptable)
3. Robotic catheter advanced to RLL posterior basal (B10)
4. Radial EBUS deployed - Adjacent view obtained
5. Tool-in-lesion confirmed with Fluoroscopy
6. Sampling performed:
   - Forceps biopsies: 7
   - TBNA passes: 3
   - Brushings: 2
7. ROSE performed - Malignant - NSCLC NOS
8. BAL obtained from RLL

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 10R, 7, 2R, 4R) → Cytology, cell block
2. TBBx RLL → Surgical pathology
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

Fellow, PGY-None
Eric Johnson, MD (Attending - present for entire procedure)"""

entities_1 = [
    # Indication
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.5mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL posterior basal (B10)", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bronchus sign", 1)},

    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},

    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "miniprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},

    # Part A
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 2)}, # "Linear EBUS FOR STAGING"
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "airways", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "endobronchial lesions", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "lymph node survey", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "ROSE", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},

    # Part B
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 2)}, # "ROBOTIC NAVIGATION"
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3.2mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL posterior basal (B10)", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7", 2)}, # "Forceps biopsies: 7"
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 6)}, # "TBNA passes: 3"
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 4)}, # "Brushings: 2"
    {"label": "PROC_ACTION", **get_span(text_1, "ROSE", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)}, # "from RLL"

    # Post-Proc
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airways", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no active bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 4)}, # "Station 7" -> "7"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL", 2)},

    # Complications/Loss
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10 mL", 1)},

    # Impression
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "mediastinal", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)