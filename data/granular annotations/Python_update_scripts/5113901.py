import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 5113901
# ==========================================
t1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (54 years old)
Gender: Male
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. David Kim
Fellow: Dr. Marcus Williams (PGY-6)
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
2. Robotic-assisted bronchoscopy (Ion platform) with peripheral lung biopsy
3. Radial EBUS for peripheral lesion localization
4. Transbronchial lung biopsy

ANESTHESIA
Type: General anesthesia with endotracheal intubation
ASA Class: 4

PROCEDURE START TIME: 10:45
PROCEDURE END TIME: 12:12
TOTAL PROCEDURE TIME: 87 minutes

EQUIPMENT
- Linear EBUS scope: Olympus BF-UC190F
- EBUS needle: Boston Scientific Acquire (22G Acquire)
- Robotic platform: Ion (Intuitive Surgical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 2L: Id[REDACTED] homogeneous lymph node measuring 13.8mm (short axis) x 21.0mm (long axis). 4 passes performed with 22G needle. ROSE: Malignant - small cell carcinoma.
Station 4R: Id[REDACTED] hypoechoic lymph node measuring 23.9mm (short axis) x 31.2mm (long axis). 3 passes performed with 22G needle. ROSE: Malignant - adenocarcinoma.
Station 11R: Id[REDACTED] hypoechoic lymph node measuring 19.6mm (short axis) x 30.0mm (long axis). 3 passes performed with 22G needle. ROSE: Atypical cells.
Station 11L: Id[REDACTED] hypoechoic lymph node measuring 17.4mm (short axis) x 22.1mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - adenocarcinoma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Ion robotic bronchoscopy system was deployed.

Target lesion: RML medial (B5)
Lesion characteristics:
- Size: 20.0 mm
- Distance from pleura: 15.9 mm
- CT appearance: Solid
- Bronchus sign: Negative
- PET SUV max: 6.5

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming adjacent view of the lesion.

Tool-in-lesion confirmation: Augmented fluoroscopy

Sampling performed:
- Transbronchial forceps biopsies: 7 specimens
- TBNA: 2 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Malignant - NSCLC NOS

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 2L, 4R, 11R, 11L - sent for cytology, cell block, and flow cytometry
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

David Kim
Interventional Pulmonology
Regional Medical Center

CPT CODES: 31653, 31627, 31654, 31628
"""

e1 = [
    # Indications and Diagnoses
    {"label": "OBS_LESION", **get_span(t1, "lung mass", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Lung nodule/mass", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Mediastinal lymphadenopathy", 1)},
    
    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(t1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS-TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion platform", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "peripheral lesion localization", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 1)}, # in "peripheral lesion localization"
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial lung biopsy", 1)},

    # Anesthesia / Time / Equipment
    {"label": "MEDICATION", **get_span(t1, "General anesthesia", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "intubation", 1)}, # endotracheal intubation
    {"label": "CTX_TIME", **get_span(t1, "10:45", 1)},
    {"label": "CTX_TIME", **get_span(t1, "12:12", 1)},
    {"label": "CTX_TIME", **get_span(t1, "87 minutes", 1)},
    
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Olympus BF-UC190F", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22G", 1)}, # In "22G Acquire"
    {"label": "PROC_METHOD", **get_span(t1, "Ion", 2)}, # under equipment
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "20 MHz miniprobe", 1)},

    # Part 1: EBUS
    {"label": "PROC_METHOD", **get_span(t1, "LINEAR EBUS", 1)},
    {"label": "MEDICATION", **get_span(t1, "general anesthesia", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "intubation", 2)},
    {"label": "MEAS_SIZE", **get_span(t1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "linear EBUS bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "lymph node sampling", 1)},
    
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 2L", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "homogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "13.8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "21.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - small cell carcinoma", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 4R", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "hypoechoic", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "23.9mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "31.2mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22G", 3)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - adenocarcinoma", 1)},
    
    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 11R", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "hypoechoic", 2)},
    {"label": "MEAS_SIZE", **get_span(t1, "19.6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "30.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22G", 4)},
    {"label": "OBS_ROSE", **get_span(t1, "Atypical cells", 1)},
    
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 11L", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "hypoechoic", 3)},
    {"label": "MEAS_SIZE", **get_span(t1, "17.4mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "22.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22G", 5)},
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - adenocarcinoma", 2)},

    # Part 2: Robotic
    {"label": "PROC_METHOD", **get_span(t1, "ROBOTIC BRONCHOSCOPY", 1)},
    {"label": "OBS_LESION", **get_span(t1, "PERIPHERAL LESION", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Ion robotic bronchoscopy system", 1)},
    
    # Target
    {"label": "OBS_LESION", **get_span(t1, "Target lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML medial (B5)", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "20.0 mm", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "pleura", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "15.9 mm", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Solid", 1)},
    
    # Navigation / Sampling
    {"label": "PROC_METHOD", **get_span(t1, "Navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "< 3mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Radial EBUS probe", 2)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 5)}, # adjacent view of the lesion
    {"label": "PROC_METHOD", **get_span(t1, "Augmented fluoroscopy", 1)},
    
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)}, # In "Sampling performed"
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 specimens", 1)},
    
    {"label": "OBS_ROSE", **get_span(t1, "Malignant - NSCLC NOS", 1)},

    # Specimens
    {"label": "PROC_METHOD", **get_span(t1, "EBUS-TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "2L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "11L", 2)},
    {"label": "SPECIMEN", **get_span(t1, "cytology", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(t1, "flow cytometry", 1)},
    
    {"label": "PROC_ACTION", **get_span(t1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 2)},
    {"label": "SPECIMEN", **get_span(t1, "surgical pathology", 1)},
    
    {"label": "PROC_ACTION", **get_span(t1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 3)},
    {"label": "SPECIMEN", **get_span(t1, "cytology", 2)},
    
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 4)},
    {"label": "SPECIMEN", **get_span(t1, "cultures", 1)},

    # Complications / EBL
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No pneumothorax", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "<10 mL", 1)},
    
    # Impression / Plan
    {"label": "PROC_METHOD", **get_span(t1, "EBUS-TBNA", 3)},
    {"label": "PROC_METHOD", **get_span(t1, "robotic bronchoscopy", 2)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsy", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "ROSE adequate", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "no pneumothorax", 1)}
]

BATCH_DATA.append({"id": "5113901", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)