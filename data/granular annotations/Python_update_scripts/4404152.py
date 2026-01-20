import sys
from pathlib import Path

# Set up the repository root (assuming script is run from inside the repo structure)
# If this script is at <repo>/scripts/processing/add_case_4404152.py,
# REPO_ROOT is three levels up. Adjust based on actual depth.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term in the text.
    Returns a dictionary with 'start' and 'end' keys, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Term not found
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 4404152
# ==========================================
id_1 = "4404152"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Robert Patel, MD
Fellow: Jason Park
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 63 years
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
Peripheral nodule and bilateral hilar adenopathy
Target lesion: 21.6mm ground-glass nodule, RUL anterior (B3)
Bronchus sign: Negative

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Fujifilm EB-580S
- EBUS needle: 22G Standard FNA
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
   - Station 10L: 13.0mm, 3 passes
   - Station 4L: 15.7mm, 2 passes
   - Station 11L: 19.4mm, 2 passes

6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - NSCLC NOS

PART B - ROBOTIC NAVIGATION:
1. Ion system prepared and registered
2. Registration error: 1.8mm (acceptable)
3. Robotic catheter advanced to RUL anterior (B3)
4. Radial EBUS deployed - Eccentric view obtained
5. Tool-in-lesion confirmed with CBCT
6. Sampling performed:
   - Forceps biopsies: 8
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
1. EBUS-TBNA (stations 10L, 4L, 11L) → Cytology, cell block
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

Procedure performed under direct supervision of Robert Patel, MD

[REDACTED], PGY-6
Robert Patel, MD (Attending - present for entire procedure)"""

entities_1 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "Peripheral nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "bilateral hilar adenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.6mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 1)},
    
    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    
    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fujifilm EB-580S", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},
    
    # Part A
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "airways", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "endobronchial lesions", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "NSCLC NOS", 1)},
    
    # Part B
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "Eccentric view", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Forceps biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    
    # Post Procedure
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Airways", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "active bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
    
    # Specimens
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "Surgical pathology", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Cultures", 1)},
    
    # Outcomes / Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No immediate complications", 1)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)