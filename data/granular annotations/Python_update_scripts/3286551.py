import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

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
    
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 3286551
# ==========================================
id_1 = "3286551"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (55 years old)
Gender: Male
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Steven Park
Fellow: Dr. Jason Park (PGY-6)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
PET-avid lung mass and mediastinal lymphadenopathy

PREOPERATIVE DIAGNOSIS
1. Lung nodule/mass requiring tissue diagnosis
2. Mediastinal lymphadenopathy requiring staging

POSTOPERATIVE DIAGNOSIS
Same as preoperative, pending final pathology

PROCEDURES PERFORMED
1. Linear endobronchial ultrasound with transbronchial needle aspiration (EBUS-TBNA) for mediastinal staging
2. Robotic-assisted bronchoscopy (Monarch platform) with peripheral lung biopsy
3. Radial EBUS for peripheral lesion localization
4. Transbronchial lung biopsy

ANESTHESIA
Type: General anesthesia with endotracheal intubation
ASA Class: 3

PROCEDURE START TIME: 08:15
PROCEDURE END TIME: 09:32
TOTAL PROCEDURE TIME: 77 minutes

EQUIPMENT
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: Cook EchoTip ProCore (22G FNB/ProCore)
- Robotic platform: Monarch (Auris Health (J&J))
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 4L: Id[REDACTED] homogeneous lymph node measuring 18.3mm (short axis) x 28.3mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - NSCLC NOS.
Station 10R: Id[REDACTED] hypoechoic lymph node measuring 14.8mm (short axis) x 23.9mm (long axis). 4 passes performed with 22G needle. ROSE: Suspicious for malignancy.
Station 4R: Id[REDACTED] homogeneous lymph node measuring 20.9mm (short axis) x 20.6mm (long axis). 4 passes performed with 22G needle. ROSE: Malignant - adenocarcinoma.
Station 7: Id[REDACTED] homogeneous lymph node measuring 24.0mm (short axis) x 28.4mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - adenocarcinoma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy system was deployed.

Target lesion: RUL anterior (B3)
Lesion characteristics:
- Size: 30.9 mm
- Distance from pleura: 17.5 mm
- CT appearance: Ground-glass
- Bronchus sign: Negative


Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming adjacent view of the lesion.

Tool-in-lesion confirmation: Fluoroscopy

Sampling performed:
- Transbronchial forceps biopsies: 6 specimens
- TBNA: 4 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Granuloma

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 4L, 10R, 4R, 7 - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from RUL - sent for surgical pathology
3. Brushings from RUL - sent for cytology
4. BAL from RUL - sent for cultures (bacterial, fungal, AFB)

COMPLICATIONS
None. No significant bleeding. No pneumothorax noted on post-procedure imaging.

ESTIMATED BLOOD LOSS
Minimal (<10 mL)

IMPRESSION
1. Successful EBUS-TBNA mediastinal staging with sampling of 4 lymph node stations
2. Successful robotic bronchoscopy with peripheral nodule biopsy
3. ROSE adequate at all sampled sites
4. Await final pathology and molecular testing if indicated

PLAN
1. Monitor in recovery for 2 hours
2. Post-procedure chest X-ray - completed, no pneumothorax
3. Discharge to home if stable with standard post-bronchoscopy precautions
4. Results conference scheduled
5. Final pathology will determine staging and treatment planning

Steven Park
Interventional Pulmonology
Regional Medical Center

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_1 = [
    # Clinical Indication / Pre-op
    {"label": "OBS_LESION", **get_span(text_1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule/mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Mediastinal lymphadenopathy", 1)},

    # Procedures Performed Header
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "peripheral lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},

    # Anesthesia / Time
    {"label": "PROC_ACTION", **get_span(text_1, "endotracheal intubation", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "08:15", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "09:32", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "77 minutes", 1)},

    # Equipment
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS probe", 1)},

    # Part 1: EBUS
    {"label": "PROC_ACTION", **get_span(text_1, "intubation", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "ETT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "ETT", 2)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.3mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "NSCLC NOS", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.9mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 2)},

    # Part 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B3", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.9 mm", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "pleura", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.5 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Ground-glass", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3mm", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "robotic catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS probe", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Fluoroscopy", 1)},
    
    # Peripheral Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},

    # Specimens
    {"label": "ANAT_LN_STATION", **get_span(text_1, "stations 4L, 10R, 4R, 7", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 4)},

    # Complications / Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},

    # Impression / Plan
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "adequate", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "2 hours", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)