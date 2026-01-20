import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 5230703
# ==========================================
id_1 = "5230703"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (48 years old)
Gender: Male
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Lisa Thompson
Fellow: Dr. Jason Park (PGY-6)
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

PROCEDURE START TIME: 09:30
PROCEDURE END TIME: 10:49
TOTAL PROCEDURE TIME: 79 minutes

EQUIPMENT
- Linear EBUS scope: Olympus BF-UC260F-OL8
- EBUS needle: Cook EchoTip ProCore (22G FNB/ProCore)
- Robotic platform: Monarch (Auris Health (J&J))
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 2R: Id[REDACTED] hypoechoic lymph node measuring 15.3mm (short axis) x 24.4mm (long axis). 3 passes performed with 22G needle. ROSE: Adequate lymphocytes.
Station 11R: Id[REDACTED] hypoechoic lymph node measuring 23.0mm (short axis) x 31.5mm (long axis). 3 passes performed with 22G needle. ROSE: Adequate lymphocytes, no malignancy.
Station 4R: Id[REDACTED] hypoechoic lymph node measuring 15.0mm (short axis) x 25.3mm (long axis). 3 passes performed with 22G needle. ROSE: Malignant - NSCLC NOS.
Station 7: Id[REDACTED] hypoechoic lymph node measuring 13.7mm (short axis) x 16.2mm (long axis). 2 passes performed with 22G needle. ROSE: Adequate lymphocytes.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy system was deployed.

Target lesion: RML lateral (B4)
Lesion characteristics:
- Size: 30.4 mm
- Distance from pleura: 18.5 mm
- CT appearance: Solid
- Bronchus sign: Negative
- PET SUV max: 13.0

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming adjacent view of the lesion.

Tool-in-lesion confirmation: Radial EBUS

Sampling performed:
- Transbronchial forceps biopsies: 4 specimens
- TBNA: 2 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Suspicious for malignancy

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 2R, 11R, 4R, 7 - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from RML - sent for surgical pathology
3. Brushings from RML - sent for cytology
4. BAL from RML - sent for cultures (bacterial, fungal, AFB)

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

Lisa Thompson
Interventional Pulmonology
Baptist Medical Center

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_1 = [
    # Clinical Indications / Diagnoses
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Mediastinal lymphadenopathy", 1)},

    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch platform", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},

    # Timestamps
    {"label": "CTX_TIME", **get_span(text_1, "09:30", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "10:49", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "79 minutes", 1)},

    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 2)},
    
    # Measurements and Stations - Part 1
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "hypoechoic lymph node", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.3mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "24.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},

    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "hypoechoic lymph node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},

    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "hypoechoic lymph node", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "25.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},

    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "hypoechoic lymph node", 4)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 2)},

    # Part 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch robotic bronchoscopy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML lateral (B4)", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "30.4 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.5 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Solid", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bronchus sign", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "< 3mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Specimens Collected
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 4)},

    # Complications / Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Successful EBUS-TBNA", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Successful robotic bronchoscopy", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "ROSE adequate", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)