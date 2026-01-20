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
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 4351438
# ------------------------------------------
id_1 = "4351438"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Brian O'Connor, MD
Fellow: Jessica Martinez
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 77 years
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
Mediastinal staging for biopsy-proven lung adenocarcinoma
Target lesion: 22.6mm solid nodule, RUL apical (B1)
Bronchus sign: Negative

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Olympus BF-UC190F
- EBUS needle: 22G Standard FNA
- Robotic platform: Galaxy (Noah Medical)
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
   - Station 11R: 24.9mm, 3 passes
   - Station 2L: 14.7mm, 2 passes
   - Station 4R: 13.0mm, 3 passes
   - Station 11L: 19.1mm, 3 passes
6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - adenocarcinoma

PART B - ROBOTIC NAVIGATION:
1. Galaxy system prepared and registered
2. Registration error: 1.8mm (acceptable)
3. Robotic catheter advanced to RUL apical (B1)
4. Radial EBUS deployed - Concentric view obtained
5. Tool-in-lesion confirmed with CBCT
6. Sampling performed:
   - Forceps biopsies: 4
   - TBNA passes: 4
   - Brushings: 2
7. ROSE performed - Suspicious for malignancy
8. BAL obtained from RUL

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 11R, 2L, 4R, 11L) → Cytology, cell block
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

Procedure performed under direct supervision of Brian O'Connor, MD

Jessica Martinez, PGY-5
Brian O'Connor, MD (Attending - present for entire procedure)"""

entities_1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "adenocarcinoma", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.6mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL apical", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B1", 1)},

    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},

    # Equipment Used
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},

    # Part A
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "airway inspection", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "no endobronchial lesions", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "lymph node survey", 1)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},

    # ROSE
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},

    # Part B
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL apical", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B1", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)}, 
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 3)}, 
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2", 3)}, 
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 4)}, 

    # Post Procedure
    {"label": "OBS_FINDING", **get_span(text_1, "no active bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "TBBx", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL", 2)},

    # Complications / Impression
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}, # Corrected occurrence: "None" appears only once.
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "lung biopsy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No immediate complications", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        try:
            add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
            print(f"Successfully added case: {case['id']}")
        except Exception as e:
            print(f"Failed to add case {case['id']}: {e}")