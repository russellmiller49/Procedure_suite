import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure this script is run from a location where 'scripts.add_training_case' is accessible
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Please ensure the project structure is correct.")
    sys.exit(1)

# List to hold all the case data
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to find (case-sensitive).
        occurrence (int): The occurrence number (1-based).
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Term not found enough times
            
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Case 1: 4735191
# ==========================================

id_1 = "4735191"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (62 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Robert Patel
Fellow: Dr. Jason Park (PGY-6)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Peripheral nodule and bilateral hilar adenopathy

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

PROCEDURE START TIME: 08:15
PROCEDURE END TIME: 09:40
TOTAL PROCEDURE TIME: 85 minutes

EQUIPMENT
- Linear EBUS scope: Fujifilm EB-580S
- EBUS needle: Olympus NA-201SX-4022 (22G Standard FNA)
- Robotic platform: Ion (Intuitive Surgical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 10L: Id[REDACTED] hypoechoic lymph node measuring 13.0mm (short axis) x 14.3mm (long axis). 3 passes performed with 22G needle. ROSE: Malignant - NSCLC NOS.
Station 4L: Id[REDACTED] homogeneous lymph node measuring 15.7mm (short axis) x 23.7mm (long axis). 2 passes performed with 22G needle. ROSE: Adequate lymphocytes.
Station 11L: Id[REDACTED] hypoechoic lymph node measuring 19.4mm (short axis) x 27.5mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - small cell carcinoma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Ion robotic bronchoscopy system was deployed.

Target lesion: RUL anterior (B3)
Lesion characteristics:
- Size: 21.6 mm
- Distance from pleura: 5.8 mm
- CT appearance: Ground-glass
- Bronchus sign: Negative


Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming eccentric view of the lesion.

Tool-in-lesion confirmation: CBCT

Sampling performed:
- Transbronchial forceps biopsies: 8 specimens
- TBNA: 4 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Granuloma

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 10L, 4L, 11L - sent for cytology, cell block, and flow cytometry
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

[REDACTED] Patel
Interventional Pulmonology
Presbyterian Hospital

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_1 = [
    # Clinical Indication
    {"label": "OBS_LESION", **get_span(text_1, "Peripheral nodule", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "hilar", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "adenopathy", 1)},
    
    # Preop Diagnosis
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Mediastinal lymphadenopathy", 1)},
    
    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},

    # Anesthesia
    {"label": "PROC_ACTION", **get_span(text_1, "endotracheal intubation", 1)},
    
    # Timestamps
    {"label": "CTX_TIME", **get_span(text_1, "08:15", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "09:40", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "85 minutes", 1)},
    
    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},
    
    # Procedure Details - Part 1
    {"label": "PROC_METHOD", **get_span(text_1, "linear EBUS", 1)}, # "linear EBUS for mediastinal..."
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    
    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hypoechoic", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.0mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - NSCLC NOS", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.7mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes", 1)},
    
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hypoechoic", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - small cell carcinoma", 1)},
    
    # Part 2
    {"label": "PROC_METHOD", **get_span(text_1, "Ion robotic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B3", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.6 mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "probe", 2)}, # "Radial EBUS probe"
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    
    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "EBUS-TBNA specimens", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "11L", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 4)},
    
    # Complications / EBL / Impression
    {"label": "OBS_FINDING", **get_span(text_1, "bleeding", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "pneumothorax", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "10 mL", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "peripheral nodule", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "pneumothorax", 2)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Execution
# ==========================================

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)