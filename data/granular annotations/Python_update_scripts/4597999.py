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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload (Batch)
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case: 4597999
# ------------------------------------------
id_4597999 = "4597999"
text_4597999 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (76 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Rachel Goldman
Fellow: Dr. Jason Park (PGY-6)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Right upper lobe mass with ipsilateral mediastinal nodes

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
PROCEDURE END TIME: 09:38
TOTAL PROCEDURE TIME: 113 minutes

EQUIPMENT
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: Olympus NA-201SX-4021 (21G Standard FNA)
- Robotic platform: Galaxy (Noah Medical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 4L: Id[REDACTED] homogeneous lymph node measuring 24.4mm (short axis) x 26.8mm (long axis). 2 passes performed with 21G needle. ROSE: Adequate lymphocytes, no malignancy.
Station 7: Id[REDACTED] homogeneous lymph node measuring 20.3mm (short axis) x 30.7mm (long axis). 3 passes performed with 21G needle. ROSE: Adequate lymphocytes, no malignancy.
Station 10R: Id[REDACTED] homogeneous lymph node measuring 20.4mm (short axis) x 33.1mm (long axis). 4 passes performed with 21G needle. ROSE: Atypical cells.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Galaxy robotic bronchoscopy system was deployed.

Target lesion: LUL inferior lingula (B5)
Lesion characteristics:
- Size: 20.2 mm
- Distance from pleura: 35.1 mm
- CT appearance: Solid
- Bronchus sign: Positive
- PET SUV max: 16.9

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming concentric view of the lesion.

Tool-in-lesion confirmation: Radial EBUS

Sampling performed:
- Transbronchial forceps biopsies: 7 specimens
- TBNA: 4 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Malignant - small cell carcinoma

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 4L, 7, 10R - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from LUL - sent for surgical pathology
3. Brushings from LUL - sent for cytology
4. BAL from LUL - sent for cultures (bacterial, fungal, AFB)

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

Rachel Goldman
Interventional Pulmonology
Community Hospital

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_4597999 = [
    # Clinical Indication
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_4597999, "mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "mediastinal", 1)},

    # Preoperative Diagnosis
    {"label": "OBS_LESION", **get_span(text_4597999, "Lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_4597999, "mass", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "Mediastinal", 1)},
    {"label": "OBS_FINDING", **get_span(text_4597999, "lymphadenopathy", 1)},

    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_4597999, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "peripheral lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "Transbronchial lung biopsy", 1)},

    # Time
    {"label": "CTX_TIME", **get_span(text_4597999, "07:45", 1)},
    {"label": "CTX_TIME", **get_span(text_4597999, "09:38", 1)},
    {"label": "CTX_TIME", **get_span(text_4597999, "113 minutes", 1)},

    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_4597999, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4597999, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4597999, "21G", 1)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "Galaxy", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4597999, "Radial EBUS probe", 1)},

    # Part 1
    {"label": "PROC_METHOD", **get_span(text_4597999, "LINEAR EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4597999, "linear EBUS bronchoscope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "mediastinal lymph node", 1)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "Station 4L", 1)},
    {"label": "OBS_FINDING", **get_span(text_4597999, "homogeneous", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "lymph node", 2)},
    {"label": "MEAS_SIZE", **get_span(text_4597999, "24.4mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4597999, "26.8mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4597999, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4597999, "21G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_4597999, "Adequate lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(text_4597999, "no malignancy", 1)},

    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "Station 7", 1)},
    {"label": "OBS_FINDING", **get_span(text_4597999, "homogeneous", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "lymph node", 3)},
    {"label": "MEAS_SIZE", **get_span(text_4597999, "20.3mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4597999, "30.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4597999, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4597999, "21G needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_4597999, "Adequate lymphocytes", 2)},
    {"label": "OBS_ROSE", **get_span(text_4597999, "no malignancy", 2)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "Station 10R", 1)},
    {"label": "OBS_FINDING", **get_span(text_4597999, "homogeneous", 3)},
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "lymph node", 4)},
    {"label": "MEAS_SIZE", **get_span(text_4597999, "20.4mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4597999, "33.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4597999, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4597999, "21G needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_4597999, "Atypical cells", 1)},

    # Part 2
    {"label": "PROC_METHOD", **get_span(text_4597999, "ROBOTIC BRONCHOSCOPY", 1)},
    {"label": "OBS_LESION", **get_span(text_4597999, "PERIPHERAL LESION", 1)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "Galaxy robotic bronchoscopy system", 1)},
    {"label": "OBS_LESION", **get_span(text_4597999, "Target lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "inferior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "B5", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4597999, "20.2 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_4597999, "Solid", 1)},
    {"label": "OBS_FINDING", **get_span(text_4597999, "Bronchus sign", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4597999, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4597999, "Radial EBUS probe", 2)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "Radial EBUS", 3)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_4597999, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4597999, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_4597999, "4 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4597999, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_4597999, "Malignant - small cell carcinoma", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_4597999, "EBUS-TBNA specimens", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4597999, "stations 4L, 7, 10R", 1)},
    {"label": "SPECIMEN", **get_span(text_4597999, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "LUL", 2)},
    {"label": "SPECIMEN", **get_span(text_4597999, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "LUL", 3)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "LUL", 4)},

    # Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4597999, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4597999, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4597999, "No pneumothorax", 1)},

    # Impression
    {"label": "PROC_METHOD", **get_span(text_4597999, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_4597999, "robotic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4597999, "peripheral", 3)},
    {"label": "OBS_LESION", **get_span(text_4597999, "nodule", 2)},
    {"label": "PROC_ACTION", **get_span(text_4597999, "biopsy", 3)},
    {"label": "OBS_ROSE", **get_span(text_4597999, "ROSE adequate", 1)},
    
    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4597999, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_4597999, "text": text_4597999, "entities": entities_4597999})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)