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
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4366016
# ==========================================
id_1 = "4366016"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (67 years old)
Gender: Male
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Brian O'Connor
Fellow: Dr. Kevin Chang (PGY-6)
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
2. Robotic-assisted bronchoscopy (Ion platform) with peripheral lung biopsy
3. Radial EBUS for peripheral lesion localization
4. Transbronchial lung biopsy

ANESTHESIA
Type: General anesthesia with endotracheal intubation
ASA Class: 3

PROCEDURE START TIME: 10:15
PROCEDURE END TIME: 11:36
TOTAL PROCEDURE TIME: 81 minutes

EQUIPMENT
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: Olympus NA-201SX-4022 (22G Standard FNA)
- Robotic platform: Ion (Intuitive Surgical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 10R: Id[REDACTED] homogeneous lymph node measuring 15.5mm (short axis) x 31.6mm (long axis). 3 passes performed with 22G needle. ROSE: Suspicious for malignancy.
Station 10L: Id[REDACTED] hypoechoic lymph node measuring 21.7mm (short axis) x 14.6mm (long axis). 2 passes performed with 22G needle. ROSE: Adequate lymphocytes.
Station 11R: Id[REDACTED] homogeneous lymph node measuring 20.5mm (short axis) x 29.9mm (long axis). 3 passes performed with 22G needle. ROSE: Malignant - NSCLC NOS.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Ion robotic bronchoscopy system was deployed.

Target lesion: LLL lateral basal (B9)
Lesion characteristics:
- Size: 29.4 mm
- Distance from pleura: 20.2 mm
- CT appearance: Part-solid
- Bronchus sign: Negative


Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming adjacent view of the lesion.

Tool-in-lesion confirmation: Fluoroscopy

Sampling performed:
- Transbronchial forceps biopsies: 6 specimens
- TBNA: 2 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Malignant - squamous cell carcinoma

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 10R, 10L, 11R - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from LLL - sent for surgical pathology
3. Brushings from LLL - sent for cytology
4. BAL from LLL - sent for cultures (bacterial, fungal, AFB)

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

Brian O'Connor
Interventional Pulmonology
Northwestern Memorial Hospital

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_1 = [
    # Clinical Indication
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    
    # Preop Dx
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Lung", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 2)}, # "Lung nodule/mass"
    {"label": "OBS_LESION", **get_span(text_1, "Mediastinal lymphadenopathy", 1)},
    
    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "peripheral lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},
    
    # Anesthesia & Times
    {"label": "PROC_METHOD", **get_span(text_1, "General anesthesia", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "endotracheal intubation", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "10:15", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "11:36", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "81 minutes", 1)},
    
    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Olympus NA-201SX-4022", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G Standard FNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Robotic platform", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},
    
    # Procedure Details - Part 1
    {"label": "PROC_METHOD", **get_span(text_1, "general anesthesia", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "endotracheal intubation", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.5mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.5mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.9mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Procedure Details - Part 2
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Ion robotic bronchoscopy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL lateral basal (B9)", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.4 mm", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "pleura", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.2 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Part-solid", 1)}, # CT appearance
    
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "Fluoroscopy", 1)},
    
    # Sampling
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Transbronchial forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # 1st occurrence in details
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},
    
    # Specimens Collected
    {"label": "SPECIMEN", **get_span(text_1, "EBUS-TBNA specimens", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 2)}, # "Brushings from LLL"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 3)},
    {"label": "SPECIMEN", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 4)},
    
    # Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    
    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)