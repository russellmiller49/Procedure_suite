import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case'. Ensure you are running from the correct repository structure.")
    sys.exit(1)

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
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1595295
# ==========================================
id_1 = "1595295"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (68 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Steven Park
Fellow: Dr. Jason Park (PGY-6)
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
2. Robotic-assisted bronchoscopy (Galaxy platform) with peripheral lung biopsy
3. Radial EBUS for peripheral lesion localization
4. Transbronchial lung biopsy

ANESTHESIA
Type: General anesthesia with endotracheal intubation
ASA Class: 4

PROCEDURE START TIME: 08:30
PROCEDURE END TIME: 10:10
TOTAL PROCEDURE TIME: 100 minutes

EQUIPMENT
- Linear EBUS scope: Fujifilm EB-580S
- EBUS needle: Boston Scientific Acquire (22G Acquire)
- Robotic platform: Galaxy (Noah Medical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 11R: Id[REDACTED] homogeneous lymph node measuring 22.0mm (short axis) x 13.6mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - small cell carcinoma.
Station 4R: Id[REDACTED] hypoechoic lymph node measuring 13.7mm (short axis) x 29.3mm (long axis). 4 passes performed with 22G needle. ROSE: Atypical cells.
Station 11L: Id[REDACTED] homogeneous lymph node measuring 18.9mm (short axis) x 31.0mm (long axis). 3 passes performed with 22G needle. ROSE: Malignant - small cell carcinoma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Galaxy robotic bronchoscopy system was deployed.

Target lesion: RLL superior (B6)
Lesion characteristics:
- Size: 27.5 mm
- Distance from pleura: 9.7 mm
- CT appearance: Ground-glass
- Bronchus sign: Negative
- PET SUV max: 16.3

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming eccentric view of the lesion.

Tool-in-lesion confirmation: CBCT

Sampling performed:
- Transbronchial forceps biopsies: 4 specimens
- TBNA: 3 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Adequate lymphocytes, no malignancy

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 11R, 4R, 11L - sent for cytology, cell block, and flow cytometry
2. Transbronchial biopsies from RLL - sent for surgical pathology
3. Brushings from RLL - sent for cytology
4. BAL from RLL - sent for cultures (bacterial, fungal, AFB)

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

Steven Park
Interventional Pulmonology
Baptist Medical Center

CPT CODES: 31653, 31627, 31654, 31628
"""
entities_1 = [
    # Indications/Diagnoses
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lymphadenopathy", 1)},

    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "peripheral lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},
    
    # Time
    {"label": "CTX_TIME", **get_span(text_1, "08:30", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "10:10", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "100 minutes", 1)},

    # Equipment
    {"label": "PROC_METHOD", **get_span(text_1, "Linear EBUS", 1)}, # In "Linear EBUS scope"
    {"label": "DEV_NEEDLE", **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS bronchoscope", 1)},

    # Station 11R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},

    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "29.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical cells", 1)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.9mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.0mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 2)},

    # Part 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)}, # In "robotic bronchoscopy system"
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B6", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.5 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Ground-glass", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bronchus sign", 1)},
    
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 2)},
    
    # Sampling
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},

    # Specimens
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 4)}, # In "EBUS-TBNA specimens"
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 3)}, # In "EBUS-TBNA specimens"
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},

    # Complications
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},

    # Impression
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 5)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 4)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 3)}, # In "nodule biopsy"
    {"label": "OBS_ROSE", **get_span(text_1, "ROSE adequate", 1)},

    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)