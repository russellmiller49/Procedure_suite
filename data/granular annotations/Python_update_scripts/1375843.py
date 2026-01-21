import sys
from pathlib import Path

# Set up the repository root path
# This assumes the script is running within the standard folder structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the python path to import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    Returns a dictionary suitable for the 'entities' list.
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

# ==========================================
# Note 1: 1375843
# ==========================================
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (77 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Brian O'Connor
Fellow: Dr. Jessica Martinez (PGY-5)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Mediastinal staging for biopsy-proven lung adenocarcinoma

PREOPERATIVE DIAGNOSIS
1. Lung nodule/mass requiring tissue diagnosis
2. Mediastinal lymphadenopathy requiring staging

POSTOPERATIVE DIAGNOSIS
Same as preoperative, pending final pathology

PROCEDURES PERFORMED
1. Linear endobronchial ultrasound with transbronchial needle aspiration (EBUS-TBNA) for mediastinal staging
2. Robotic-assisted bronchoscopy (Galaxy platform) with peripheral lung biopsy
3. Radial EBUS for peripheral lesion localization
4. Transbronchial lung biopsy

ANESTHESIA
Type: General anesthesia with endotracheal intubation
ASA Class: 3

PROCEDURE START TIME: 07:45
PROCEDURE END TIME: 09:56
TOTAL PROCEDURE TIME: 131 minutes

EQUIPMENT
- Linear EBUS scope: Olympus BF-UC190F
- EBUS needle: Olympus NA-201SX-4022 (22G Standard FNA)
- Robotic platform: Galaxy (Noah Medical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 11R: Id[REDACTED] homogeneous lymph node measuring 24.9mm (short axis) x 17.4mm (long axis). 3 passes performed with 22G needle. ROSE: Malignant - adenocarcinoma.
Station 2L: Id[REDACTED] hypoechoic lymph node measuring 14.7mm (short axis) x 16.9mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - NSCLC NOS.
Station 4R: Id[REDACTED] hypoechoic lymph node measuring 13.0mm (short axis) x 24.5mm (long axis). 3 passes performed with 22G needle. ROSE: Malignant - small cell carcinoma.
Station 11L: Id[REDACTED] hypoechoic lymph node measuring 19.1mm (short axis) x 15.5mm (long axis). 3 passes performed with 22G needle. ROSE: Suspicious for malignancy.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Galaxy robotic bronchoscopy system was deployed.

Target lesion: RUL apical (B1)
Lesion characteristics:
- Size: 22.6 mm
- Distance from pleura: 21.0 mm
- CT appearance: Solid
- Bronchus sign: Negative
- PET SUV max: 9.7

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming concentric view of the lesion.

Tool-in-lesion confirmation: CBCT

Sampling performed:
- Transbronchial forceps biopsies: 4 specimens
- TBNA: 4 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Suspicious for malignancy

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 11R, 2L, 4R, 11L - sent for cytology, cell block, and flow cytometry
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

Brian O'Connor
Interventional Pulmonology
Veterans Affairs Medical Center

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_1 = [
    # Indications / Diagnoses
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule/mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Mediastinal lymphadenopathy", 1)},

    # Procedures Performed Header
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 1)}, # Mapped as part of method/platform
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "peripheral lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},

    # Anesthesia / Times
    {"label": "CTX_TIME", **get_span(text_1, "07:45", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "09:56", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "131 minutes", 1)},

    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)}, # In "Robotic platform"
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},

    # Procedure Details Part 1
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 2)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.9mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - adenocarcinoma", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.1mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Procedure Details Part 2
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy robotic bronchoscopy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL apical (B1)", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.6 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 2)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)}, # In "TBNA: 4 passes"
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 2)},

    # Specimens
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "specimens", 3)}, # EBUS-TBNA specimens
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 2)},
    
    {"label": "SPECIMEN", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    
    {"label": "SPECIMEN", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 4)},

    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}, # Under Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    
    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 3)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 3)}, # In peripheral nodule biopsy
]

BATCH_DATA.append({"id": "1375843", "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)