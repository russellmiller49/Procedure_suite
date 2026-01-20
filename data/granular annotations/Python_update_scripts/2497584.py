import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
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
# Note 1: 2497584
# ==========================================
id_1 = "2497584"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (56 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Brian O'Connor
Fellow: Dr. Marcus Williams (PGY-6)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Lung nodule evaluation with mediastinal lymphadenopathy workup

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
ASA Class: 2

PROCEDURE START TIME: 07:15
PROCEDURE END TIME: 08:33
TOTAL PROCEDURE TIME: 78 minutes

EQUIPMENT
- Linear EBUS scope: Olympus BF-UC180F
- EBUS needle: Boston Scientific Acquire (22G Acquire)
- Robotic platform: Monarch (Auris Health (J&J))
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 10R: Id[REDACTED] homogeneous lymph node measuring 16.6mm (short axis) x 13.8mm (long axis). 4 passes performed with 22G needle. ROSE: Malignant - NSCLC NOS.
Station 4R: Id[REDACTED] hypoechoic lymph node measuring 13.5mm (short axis) x 29.3mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - small cell carcinoma.
Station 2L: Id[REDACTED] homogeneous lymph node measuring 11.0mm (short axis) x 19.3mm (long axis). 4 passes performed with 22G needle. ROSE: Adequate lymphocytes, no malignancy.
Station 2R: Id[REDACTED] hypoechoic lymph node measuring 21.8mm (short axis) x 17.2mm (long axis). 4 passes performed with 22G needle. ROSE: Adequate lymphocytes, no malignancy.
Station 4L: Id[REDACTED] hypoechoic lymph node measuring 22.9mm (short axis) x 29.8mm (long axis). 3 passes performed with 22G needle. ROSE: Atypical cells.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy system was deployed.

Target lesion: LUL inferior lingula (B5)
Lesion characteristics:
- Size: 31.2 mm
- Distance from pleura: 32.2 mm
- CT appearance: Solid
- Bronchus sign: Positive
- PET SUV max: 5.0

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming concentric view of the lesion.

Tool-in-lesion confirmation: CBCT

Sampling performed:
- Transbronchial forceps biopsies: 6 specimens
- TBNA: 2 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Malignant - squamous cell carcinoma

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 10R, 4R, 2L, 2R, 4L - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from LUL - sent for surgical pathology
3. Brushings from LUL - sent for cytology
4. BAL from LUL - sent for cultures (bacterial, fungal, AFB)

COMPLICATIONS
None. No significant bleeding. No pneumothorax noted on post-procedure imaging.

ESTIMATED BLOOD LOSS
Minimal (<10 mL)

IMPRESSION
1. Successful EBUS-TBNA mediastinal staging with sampling of 5 lymph node stations
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
Cleveland Clinic

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_1 = [
    # Indications
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 2)},

    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},

    # Times
    {"label": "CTX_TIME", **get_span(text_1, "07:15", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "08:33", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "78 minutes", 1)},

    # Equipment
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    
    # Procedure Details - Part 1
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},

    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.5mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},

    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},

    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 2)},

    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.9mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 6)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # Procedure Details - Part 2
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "inferior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B5", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.2 mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},

    # Specimens
    {"label": "ANAT_LN_STATION", **get_span(text_1, "stations 10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 4)},

    # Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10 mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)