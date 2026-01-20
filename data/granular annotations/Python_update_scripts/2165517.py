import sys
from pathlib import Path

# Set up the repository root directory
# (Assumes this script is running from a subdirectory or needs to find the root)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the python path to import the utility
sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly in a different structure, 
    # assumes the script is in the same directory for testing
    from add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==============================================================================
# CASE: 2165517
# ==============================================================================
id_2165517 = "2165517"
text_2165517 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Andrew Nakamura, MD
Fellow: Kevin Chang
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 61 years
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
Lung nodule evaluation with mediastinal lymphadenopathy workup
Target lesion: 25.0mm solid nodule, LUL anterior (B3)
Bronchus sign: Positive

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Fujifilm EB-580S
- EBUS needle: 21G Standard FNA
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
   - Station 7: 19.5mm, 4 passes
   - Station 11L: 18.1mm, 2 passes
   - Station 10R: 17.1mm, 4 passes
   - Station 4L: 11.5mm, 3 passes
6. ROSE performed - cytopathologist present
7. ROSE results: Granuloma

PART B - ROBOTIC NAVIGATION:
1. Monarch system prepared and registered
2. Registration error: 1.6mm (acceptable)
3. Robotic catheter advanced to LUL anterior (B3)
4. Radial EBUS deployed - Eccentric view obtained
5. Tool-in-lesion confirmed with Fluoroscopy
6. Sampling performed:
   - Forceps biopsies: 4
   - TBNA passes: 3
   - Brushings: 2
7. ROSE performed - Malignant - squamous cell carcinoma
8. BAL obtained from LUL

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 7, 11L, 10R, 4L) → Cytology, cell block
2. TBBx LUL → Surgical pathology
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

Procedure performed under direct supervision of Andrew Nakamura, MD

Kevin Chang, PGY-6
Andrew Nakamura, MD (Attending - present for entire procedure)"""

entities_2165517 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_2165517, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_2165517, "mediastinal lymphadenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2165517, "25.0mm", 1)},
    {"label": "OBS_LESION", **get_span(text_2165517, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2165517, "LUL anterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2165517, "B3", 1)},

    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_2165517, "8.0mm", 1)},
    # ETT is typically standard equipment, included as instrument if needed, 
    # but often ignored if strictly just device. Included here as DEV_INSTRUMENT for completeness.
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "ETT", 1)},

    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Linear EBUS scope", 1)},
    {"label": "PROC_METHOD", **get_span(text_2165517, "EBUS", 2)}, # In "EBUS needle"
    {"label": "DEV_NEEDLE", **get_span(text_2165517, "21G", 1)},
    {"label": "PROC_METHOD", **get_span(text_2165517, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_2165517, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "20 MHz miniprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Cytology brushes", 1)},

    # Procedure Steps - Part A
    {"label": "PROC_METHOD", **get_span(text_2165517, "Linear EBUS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2165517, "airways", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Linear EBUS scope", 2)},
    
    # Stations and Sampling
    {"label": "ANAT_LN_STATION", **get_span(text_2165517, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2165517, "19.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2165517, "4 passes", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_2165517, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2165517, "18.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2165517, "2 passes", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_2165517, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2165517, "17.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2165517, "4 passes", 2)}, # 2nd occurrence of "4 passes"
    
    {"label": "ANAT_LN_STATION", **get_span(text_2165517, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2165517, "11.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2165517, "3 passes", 1)},
    
    {"label": "OBS_ROSE", **get_span(text_2165517, "Granuloma", 1)},

    # Procedure Steps - Part B
    {"label": "PROC_METHOD", **get_span(text_2165517, "ROBOTIC NAVIGATION", 1)}, # Header
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2165517, "LUL anterior", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2165517, "B3", 2)},
    {"label": "PROC_METHOD", **get_span(text_2165517, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_2165517, "Fluoroscopy", 1)},
    
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Forceps", 1)}, # In "Forceps biopsies"
    {"label": "PROC_ACTION", **get_span(text_2165517, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2165517, "4", 3)}, # "4" in list
    
    {"label": "PROC_ACTION", **get_span(text_2165517, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2165517, "3", 3)}, # "3" in list
    
    {"label": "PROC_ACTION", **get_span(text_2165517, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2165517, "2", 4)}, # "2" in list (after "11L: ... 2 passes" etc)
    
    {"label": "OBS_ROSE", **get_span(text_2165517, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_2165517, "squamous cell carcinoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_2165517, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2165517, "LUL", 3)}, # 3rd occur: Indication, Part B step 3, Part B step 8

    # Post Procedure
    {"label": "ANAT_AIRWAY", **get_span(text_2165517, "Airways", 1)}, # "Airways inspected"
    {"label": "DEV_INSTRUMENT", **get_span(text_2165517, "Bronchoscope", 2)},

    # Specimens
    {"label": "PROC_METHOD", **get_span(text_2165517, "EBUS", 5)},
    {"label": "PROC_ACTION", **get_span(text_2165517, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2165517, "11L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2165517, "10R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2165517, "4L", 2)},
    {"label": "SPECIMEN", **get_span(text_2165517, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_2165517, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2165517, "LUL", 4)},
    {"label": "SPECIMEN", **get_span(text_2165517, "Brushings", 2)}, # Listed under SPECIMENS SENT
    {"label": "PROC_ACTION", **get_span(text_2165517, "BAL", 2)}, # Listed under SPECIMENS SENT

    # Complications / Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2165517, "None", 1)}, # In "COMPLICATIONS: None"
    {"label": "MEAS_VOL", **get_span(text_2165517, "<10 mL", 1)},

    # Impression
    {"label": "PROC_METHOD", **get_span(text_2165517, "EBUS", 6)},
    {"label": "PROC_ACTION", **get_span(text_2165517, "TBNA", 3)},
    {"label": "PROC_METHOD", **get_span(text_2165517, "robotic", 1)}, # Fixed count: Only one lowercase 'robotic' in Impression
    {"label": "PROC_ACTION", **get_span(text_2165517, "bronchoscopy", 1)}, # Fixed count: Only one lowercase 'bronchoscopy'
    {"label": "ANAT_LUNG_LOC", **get_span(text_2165517, "peripheral lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_2165517, "biopsy", 1)}, # Fixed count: Only one lowercase 'biopsy' in Impression
]

BATCH_DATA.append({"id": id_2165517, "text": text_2165517, "entities": entities_2165517})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)