import sys
from pathlib import Path
from scripts.add_training_case import add_case

REPO_ROOT = Path(__file__).resolve().parent.parent

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times.")
    return {"start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 4534382
# ==========================================
id_1 = "4534382"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient [REDACTED]: [REDACTED]
MRN: [REDACTED]
Date: [REDACTED]
Attending: Katherine Lee, MD
Fellow: N/A
Location: [REDACTED]

PATIENT [REDACTED]:
Age: 74 years
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
Left lower lobe nodule and subcarinal adenopathy
Target lesion: 29.8mm ground-glass nodule, LUL anterior (B3)
Bronchus sign: Negative

ANESTHESIA:
Type: General anesthesia
Airway: 8.0mm ETT, oral
Induction: Standard IV induction by anesthesia team

EQUIPMENT USED:
- Linear EBUS scope: Pentax EB-1990i
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
   - Station 10R: 8.4mm, 4 passes
   - Station 10L: 13.7mm, 3 passes
   - Station 2L: 11.1mm, 3 passes

6. ROSE performed - cytopathologist present
7. ROSE results: Malignant - NSCLC NOS

PART B - ROBOTIC NAVIGATION:
1. Ion system prepared and registered
2. Registration error: 1.8mm (acceptable)
3. Robotic catheter advanced to LUL anterior (B3)
4. Radial EBUS deployed - Adjacent view obtained
5. Tool-in-lesion confirmed with CBCT
6. Sampling performed:
   - Forceps biopsies: 8
   - TBNA passes: 2
   - Brushings: 2
7. ROSE performed - Malignant - adenocarcinoma
8. BAL obtained from LUL

POST-PROCEDURE:
1. Airways inspected - no active bleeding
2. Bronchoscope removed
3. Patient extubated without difficulty
4. Post-procedure CXR ordered - no pneumothorax
5. Patient to recovery area

SPECIMENS SENT:
1. EBUS-TBNA (stations 10R, 10L, 2L) → Cytology, cell block
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

Procedure performed under direct supervision of Katherine Lee, MD

Fellow, PGY-None
Katherine Lee, MD (Attending - present for entire procedure)"""

entities_1 = [
    # Indication
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "subcarinal", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "adenopathy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.8mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "ground-glass nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior (B3)", 1)},

    # Anesthesia
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},

    # Equipment
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)}, # "Linear EBUS scope"
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cytology brushes", 1)},

    # Procedure Steps - Part A
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "airways", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "no endobronchial lesions", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 2)}, # "Linear EBUS scope exchanged"
    
    # Stations
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},

    # ROSE
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "NSCLC NOS", 1)},

    # Procedure Steps - Part B
    {"label": "PROC_METHOD", **get_span(text_1, "Ion system", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.8mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Robotic catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior (B3)", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Forceps biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)}, # Adjusted to 1 (Part B)
    
    # ROSE 2
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 1)},
    
    # BAL
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 3)},

    # Post-Procedure
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no active bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Bronchoscope", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},

    # Specimens
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 2)}, # Inside "stations 10R"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)}, # Adjusted to 2 (Specimens)
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 2)},

    # Complications / Impression
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No immediate complications", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)