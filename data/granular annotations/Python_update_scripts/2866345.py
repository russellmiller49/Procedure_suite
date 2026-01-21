import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from a subdirectory or the root of the repo
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

# -----------------------------------------------------------------------------
# Helper Function for Span Extraction
# -----------------------------------------------------------------------------
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start, "end": start + len(term)}

# -----------------------------------------------------------------------------
# Data Payload (Batch Processing)
# -----------------------------------------------------------------------------
BATCH_DATA = []

# ==========================================
# Case 1: 2866345
# ==========================================
id_1 = "2866345"
text_1 = """BRONCHOSCOPY REPORT

Patient: [REDACTED]
MRN: [REDACTED]
Date of Birth: [REDACTED]
Date of Procedure: [REDACTED]
Location: [REDACTED]

Attending: Dr. Erin McCarthy, MD
Fellow: Dr. Alex Rivera, MD (PGY-7)
RN: Jennifer Adams
RT: Marcus Thompson

INDICATION: 39-year-old African American male with bilateral hilar lymphadenopathy and scattered bilateral upper lobe perilymphatic nodules on CT chest. Clinical presentation consistent with pulmonary sarcoidosis. Bronchoscopy for tissue diagnosis.

PREOPERATIVE DIAGNOSIS: Suspected pulmonary sarcoidosis, Stage II

POSTOPERATIVE DIAGNOSIS: Same (pending pathology)

PROCEDURE:
1. Flexible bronchoscopy
2. Bronchoalveolar lavage
3. Fluoroscopic-guided transbronchial lung biopsy, right upper lobe

SEDATION: Moderate sedation (Versed 3mg, Fentanyl 75mcg) with topical lidocaine

PROCEDURE NOTE:
Patient [REDACTED] and bronchoscope introduced via oral route. Airway examination revealed normal vocal cords, patent trachea, and normal-appearing carina. All visible airways were free of endobronchial abnormalities. Mucosa appeared normal throughout.

BAL was performed in the right middle lobe using 150mL sterile saline (3 x 50mL). Approximately 75mL of slightly turbid fluid was recovered and sent for cell count, differential, CD4/CD8 ratio, cultures, and cytology.

For transbronchial biopsies, the bronchoscope was advanced into the right upper lobe. Using biplanar fluoroscopy (AP and lateral views), the biopsy forceps (standard cup forceps) were advanced into the RUL anterior segment (RB3) and positioned approximately 2cm from the pleural surface. 8 biopsies were obtained from the right upper lobe, targeting areas of perilymphatic nodularity.

Each specimen was placed in formalin and examined visually - multiple fragments appeared adequate in size. Minimal bleeding occurred, controlled with wedge technique. Repeat fluoroscopy at end of procedure showed no pneumothorax.

FLUOROSCOPY DATA:
- Total fluoro time: 1.8 min
- DAP: 24 mGy·cm²

SPECIMENS:
1. BAL - Cell count/diff, CD4/CD8 ratio, bacterial/fungal/AFB cultures, PCP DFA, cytology
2. TBLB RUL x 8 - Surgical pathology with request for special stains (GMS, AFB)

COMPLICATIONS: None

ESTIMATED BLOOD LOSS: <5mL

POST-PROCEDURE: Patient recovered well. CXR 2 hours post-procedure showed no pneumothorax. Patient discharged home in stable condition.

IMPRESSION: Airways grossly normal. TBLB and BAL obtained for suspected sarcoidosis workup. Await pathology for non-caseating granulomas and BAL lymphocytosis/elevated CD4:CD8 ratio to confirm diagnosis.

FOLLOW-UP: Return to sarcoidosis clinic in 2 weeks for results.

Erin McCarthy, MD
Alex Rivera, MD"""

entities_1 = [
    # Indication
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "lymphadenopathy", 1)},
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    
    # Procedure Header
    {"label": "PROC_ACTION", **get_span(text_1, "Flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoalveolar lavage", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Fluoroscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial lung biopsy", 1)},
    {"label": "LATERALITY", **get_span(text_1, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "upper lobe", 2)},

    # Sedation
    {"label": "MEDICATION", **get_span(text_1, "Versed", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Fentanyl", 1)},
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},

    # Procedure Note - Airway & BAL
    {"label": "ANAT_AIRWAY", **get_span(text_1, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "carina", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)}, # "BAL was performed"
    {"label": "LATERALITY", **get_span(text_1, "right", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "middle lobe", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "150mL", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # "3 x 50mL"
    {"label": "MEAS_VOL", **get_span(text_1, "50mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "75mL", 1)},

    # Procedure Note - Biopsy
    {"label": "LATERALITY", **get_span(text_1, "right", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "upper lobe", 3)},
    {"label": "PROC_METHOD", **get_span(text_1, "fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "biopsy forceps", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RB3", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 2)}, # "8 biopsies were obtained"
    {"label": "LATERALITY", **get_span(text_1, "right", 4)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "upper lobe", 4)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 1)}, # "showed no pneumothorax"

    # Fluoro Data
    {"label": "MEAS_TIME", **get_span(text_1, "1.8 min", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "BAL", 2)}, # "SPECIMENS: 1. BAL"
    {"label": "SPECIMEN", **get_span(text_1, "TBLB", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},

    # Blood Loss & Post-Procedure
    {"label": "MEAS_VOL", **get_span(text_1, "5mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 2)}, # "CXR... showed no pneumothorax"
    
    # Impression
    {"label": "SPECIMEN", **get_span(text_1, "TBLB", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL", 3)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# -----------------------------------------------------------------------------
# Execution Loop
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)