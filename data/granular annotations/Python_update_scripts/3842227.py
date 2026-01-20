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
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of a term in the text based on its occurrence.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions (Batch)
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 3842227
# ------------------------------------------
id_1 = "3842227"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Michael Rodriguez, MD
Fellow: N/A
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 49 years
Sex: Female
ASA Class: 4

PRE-PROCEDURE:
1. Patient id[REDACTED] confirmed with two id[REDACTED]
2. Informed consent verified on chart
3. NPO status confirmed (>8 hours)
4. Anticoagulation status reviewed - not on anticoagulation
5. Allergies reviewed - NKDA
6. Time-out performed with all team members

INDICATION:
Right upper lobe mass with ipsilateral mediastinal nodes
Target lesion: 28.6mm ground-glass nodule, RLL lateral basal (B9)
Bronchus sign: Negative

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Olympus BF-UC260F-OL8
- EBUS needle: 21G Standard FNA
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
   - Station 10R: 17.1mm, 2 passes
   - Station 11R: 8.4mm, 2 passes
   - Station 11L: 22.2mm, 4 passes
   - Station 2R: 21.9mm, 4 passes
6. ROSE performed - cytopathologist present
7. ROSE results: Atypical cells

PART B - ROBOTIC NAVIGATION:
1. Ion system prepared and registered
2. Registration error: 2.6mm (acceptable)
3. Robotic catheter advanced to RLL lateral basal (B9)
4. Radial EBUS deployed - Adjacent view obtained
5. Tool-in-lesion confirmed with Augmented fluoroscopy
6. Sampling performed:
   - Forceps biopsies: 5
   - TBNA passes: 4
   - Brushings: 2
7. ROSE performed - Malignant - adenocarcinoma
8. BAL obtained from RLL

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 10R, 11R, 11L, 2R, 4L) → Cytology, cell block
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

Procedure performed under direct supervision of Michael Rodriguez, MD

Fellow, PGY-None
Michael Rodriguez, MD (Attending - present for entire procedure)"""

entities_1 = [
    # Indication / Lesion
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.6mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 1)},
    
    # Equipment
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},

    # Part A - EBUS
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)}, # Second occurrence of "2 passes"
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)}, # Second occurrence of "4 passes"
    
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # Part B - Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 2)}, # Second occurrence
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 2)}, # Second occurrence
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)}, # Second occurrence
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 4)}, # Context "Forceps biopsies: 5"
    
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA passes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 9)}, # Context "TBNA passes: 4"
    
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 15)}, # Context "Brushings: 2"
    
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)}, # Context "BAL obtained from RLL"

    # Specimens Sent
    {"label": "SPECIMEN", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)}, # Context "TBBx RLL"
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL", 2)},

    # Complications / Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}, # Context: "COMPLICATIONS: None"
    
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)