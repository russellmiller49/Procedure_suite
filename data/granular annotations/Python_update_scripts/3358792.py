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
    Finds the start and end indices of a term in the text based on its occurrence.
    Raises ValueError if the term is not found the specified number of times.
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
# Case 1: 3358792
# ------------------------------------------
id_1 = "3358792"
text_1 = """**PATIENT INFORMATION:**
- Name: DeShawn Williams
- MRN: [REDACTED]
- DOB: [REDACTED]
- Date of Procedure: [REDACTED]
- Procedure Time: 11:20-12:05

**INSTITUTION:[REDACTED]

**ATTENDING PHYSICIAN:** Dr. Emily Morrison, MD (Pulmonary/Critical Care)  
**FELLOW:** Dr. Jason Park, MD (PGY-6)

**INDICATION:**
60-year-old male with newly diagnosed left upper lobe mass and moderate left-sided pleural effusion. Thoracentesis for diagnostic workup and staging.

**PRE-PROCEDURE:**
- Informed consent obtained, risks/benefits discussed including pneumothorax, bleeding, infection, re-expansion pulmonary edema
- Timeout performed with entire team
- Bedside ultrasound: Left pleural effusion, maximum depth 5.2 cm, small amount of septations noted
- Vital signs: BP 138/84, HR 82, SpO2 96% on RA

**PROCEDURE DETAILS:**
- Patient positioned sitting, leaning forward on bedside table
- Left posterior chest, 9th intercostal space, posterior axillary line
- Skin prepped with chlorhexidine, sterile drape applied
- Local anesthesia: 12 mL 1% lidocaine administered
- Ultrasound-guided insertion of 18-gauge catheter-over-needle system
- Septations noted on ultrasound but fluid pocket adequate for safe drainage
- Initial fluid: bloody appearance
- Total volume removed: 650 mL
- Drainage ceased as fluid became more viscous
- Post-procedure ultrasound: residual fluid present, no pneumothorax

**SPECIMENS SENT:**
- Pleural fluid analysis (cell count, protein, LDH, glucose, pH)
- Pleural fluid cytology (2 specimens)
- Pleural fluid cultures (aerobic, anaerobic, AFB, fungal)
- Pleural fluid flow cytometry
- Pleural fluid tumor markers (CEA, CA 19-9)

**IMMEDIATE RESULTS:**
- Appearance: Bloody (frank blood)
- Likely exudative effusion based on clinical context

**POST-PROCEDURE:**
- Procedure tolerated adequately
- Patient developed transient chest pain (5/10) which resolved with position change
- Chest X-ray ordered (PA and lateral when patient able)
- Vital signs: BP 142/88, HR 84, SpO2 96% on RA

**COMPLICATIONS:** None

**ASSESSMENT:** Diagnostic thoracentesis of left hemorrhagic pleural effusion in patient with lung mass. Hemorrhagic effusion concerning for malignant pleural disease. Septations noted which may require further intervention if fluid reaccumulates.

**PLAN:**
- Await cytology results
- Review CT chest
- Multidisciplinary tumor board discussion
- May require pleuroscopy for diagnosis and pleurodesis if cytology non-diagnostic
- Consider oncology consultation"""

entities_1 = [
    # Indication
    {"label": "LATERALITY", **get_span(text_1, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "LATERALITY", **get_span(text_1, "left", 2)},  # left-sided
    {"label": "OBS_FINDING", **get_span(text_1, "pleural effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Thoracentesis", 1)},

    # Pre-Procedure
    {"label": "PROC_METHOD", **get_span(text_1, "ultrasound", 1)}, # Bedside ultrasound
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)}, # Capitalized Left in Pre-Procedure
    {"label": "OBS_FINDING", **get_span(text_1, "pleural effusion", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "5.2 cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "septations", 1)},

    # Procedure Details
    {"label": "LATERALITY", **get_span(text_1, "Left", 2)}, # Left posterior chest
    {"label": "ANAT_PLEURA", **get_span(text_1, "posterior chest", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "9th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "posterior axillary line", 1)},
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ultrasound", 1)}, # Ultrasound-guided
    {"label": "DEV_NEEDLE", **get_span(text_1, "18-gauge", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Septations", 1)}, # Capitalized Septations
    {"label": "OBS_FINDING", **get_span(text_1, "bloody", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "650 mL", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "ultrasound", 2)}, # Post-procedure ultrasound
    {"label": "OBS_FINDING", **get_span(text_1, "residual fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "pneumothorax", 2)}, # no pneumothorax

    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "Pleural fluid", 1)},

    # Immediate Results
    {"label": "OBS_FINDING", **get_span(text_1, "Bloody", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "exudative", 1)},

    # Post-Procedure
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_1, "chest pain", 1)},

    # Assessment
    {"label": "PROC_ACTION", **get_span(text_1, "thoracentesis", 1)}, # Lowercase in assessment
    {"label": "LATERALITY", **get_span(text_1, "left", 3)},
    {"label": "OBS_FINDING", **get_span(text_1, "hemorrhagic", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "pleural effusion", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "Septations", 2)},

    # Plan
    {"label": "PROC_ACTION", **get_span(text_1, "pleuroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "pleurodesis", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)