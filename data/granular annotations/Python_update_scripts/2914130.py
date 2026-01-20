import sys
from pathlib import Path
from scripts.add_training_case import add_case

REPO_ROOT = Path(__file__).resolve().parent.parent

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2914130
# ==========================================
t1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (77 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Maria Santos
Fellow: Dr. Kevin Chang (PGY-6)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Combined staging and peripheral nodule diagnosis

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
ASA Class: 4

PROCEDURE START TIME: 07:30
PROCEDURE END TIME: 08:45
TOTAL PROCEDURE TIME: 75 minutes

EQUIPMENT
- Linear EBUS scope: Olympus BF-UC180F
- EBUS needle: Olympus NA-201SX-4021 (21G Standard FNA)
- Robotic platform: Monarch (Auris Health (J&J))
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 2L: Id[REDACTED] homogeneous lymph node measuring 19.0mm (short axis) x 23.5mm (long axis). 2 passes performed with 21G needle. ROSE: Malignant - adenocarcinoma.
Station 10L: Id[REDACTED] hypoechoic lymph node measuring 22.7mm (short axis) x 13.9mm (long axis). 4 passes performed with 21G needle. ROSE: Malignant - adenocarcinoma.
Station 7: Id[REDACTED] hypoechoic lymph node measuring 16.8mm (short axis) x 24.0mm (long axis). 4 passes performed with 21G needle. ROSE: Adequate lymphocytes, no malignancy.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy system was deployed.

Target lesion: RUL anterior (B3)
Lesion characteristics:
- Size: 16.3 mm
- Distance from pleura: 9.6 mm
- CT appearance: Part-solid
- Bronchus sign: Positive
- PET SUV max: 12.4

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming eccentric view of the lesion.

Tool-in-lesion confirmation: Augmented fluoroscopy

Sampling performed:
- Transbronchial forceps biopsies: 6 specimens
- TBNA: 2 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Malignant - adenocarcinoma

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 2L, 10L, 7 - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from RUL - sent for surgical pathology
3. Brushings from RUL - sent for cytology
4. BAL from RUL - sent for cultures (bacterial, fungal, AFB)

COMPLICATIONS
None. No significant bleeding. No pneumothorax noted on post-procedure imaging.

ESTIMATED BLOOD LOSS
Minimal (<10 mL)

IMPRESSION
1. Successful EBUS-TBNA mediastinal staging with sampling of 3 lymph node stations
2. Successful robotic bronchoscopy with peripheral nodule biopsy
3. ROSE adequate at all sampled sites
4. Await final pathology and molecular testing if indicated

PLAN
1. Monitor in recovery for 2 hours
2. Post-procedure chest X-ray - completed, no pneumothorax
3. Discharge to home if stable with standard post-bronchoscopy precautions
4. Results conference scheduled
5. Final pathology will determine staging and treatment planning

Maria Santos
Interventional Pulmonology
Memorial Hospital

CPT CODES: 31653, 31627, 31654, 31628
"""

e1 = [
    # Clinical Indication / Preop Diagnosis
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 2)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lymphadenopathy", 1)},

    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(t1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Monarch", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsy", 1)}, # peripheral lung biopsy
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial lung biopsy", 1)},

    # Anesthesia / Time
    {"label": "CTX_TIME", **get_span(t1, "07:30", 1)},
    {"label": "CTX_TIME", **get_span(t1, "08:45", 1)},
    {"label": "CTX_TIME", **get_span(t1, "75 minutes", 1)},

    # Equipment
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Monarch", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Radial EBUS probe", 1)},

    # Procedure Details - Part 1
    {"label": "PROC_METHOD", **get_span(t1, "linear EBUS", 1)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 2L", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "19.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "23.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - adenocarcinoma", 1)},

    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "22.7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "13.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 3)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - adenocarcinoma", 2)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "16.8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "24.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 4)},
    {"label": "OBS_ROSE", **get_span(t1, "Adequate lymphocytes, no malignancy", 1)},

    # Procedure Details - Part 2
    {"label": "PROC_METHOD", **get_span(t1, "Monarch", 3)},
    {"label": "PROC_METHOD", **get_span(t1, "robotic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "B3", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "16.3 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Radial EBUS probe", 2)},
    {"label": "PROC_METHOD", **get_span(t1, "Augmented fluoroscopy", 1)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - adenocarcinoma", 3)},

    # Specimens Collected
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 4)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "2L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "10L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 2)},
    {"label": "SPECIMEN", **get_span(t1, "cell block", 1)},
    
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 2)},
    
    {"label": "PROC_ACTION", **get_span(t1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 3)},
    
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 4)},

    # Complications / Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No pneumothorax", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "10 mL", 1)},

    # Impression
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 5)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 4)},
    {"label": "PROC_METHOD", **get_span(t1, "robotic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsy", 2)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 3)},
    
    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": "2914130", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)