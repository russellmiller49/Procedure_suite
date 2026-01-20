import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from a subdirectory like 'scripts/' or 'data_gen/'
# Adjusts to find the root where 'scripts.add_training_case' is located
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 4082755
# ==========================================
text_4082755 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (45 years old)
Gender: Male
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Robert Patel
Fellow: Dr. Priya Sharma (PGY-5)
Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Peripheral lung nodule with suspicious mediastinal nodes

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

PROCEDURE START TIME: 08:30
PROCEDURE END TIME: 10:18
TOTAL PROCEDURE TIME: 108 minutes

EQUIPMENT
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: Olympus NA-201SX-4021 (21G Standard FNA)
- Robotic platform: Ion (Intuitive Surgical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 4L: Id[REDACTED] homogeneous lymph node measuring 21.5mm (short axis) x 32.3mm (long axis). 2 passes performed with 21G needle. ROSE: Malignant - NSCLC NOS.
Station 10L: Id[REDACTED] homogeneous lymph node measuring 21.1mm (short axis) x 12.4mm (long axis). 2 passes performed with 21G needle. ROSE: Malignant - NSCLC NOS.
Station 11L: Id[REDACTED] homogeneous lymph node measuring 8.8mm (short axis) x 15.4mm (long axis). 3 passes performed with 21G needle. ROSE: Malignant - squamous cell carcinoma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Ion robotic bronchoscopy system was deployed.

Target lesion: LUL superior lingula (B4)
Lesion characteristics:
- Size: 24.3 mm
- Distance from pleura: 39.0 mm
- CT appearance: Solid
- Bronchus sign: Negative
- PET SUV max: 12.7

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming eccentric view of the lesion.

Tool-in-lesion confirmation: Augmented fluoroscopy

Sampling performed:
- Transbronchial forceps biopsies: 4 specimens
- TBNA: 2 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Adequate lymphocytes

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 4L, 10L, 11L - sent for cytology, cell block, and flow cytometry
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

Robert Patel
Interventional Pulmonology
Memorial Hospital

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_4082755 = [
    # Indication / Diagnosis
    {"label": "OBS_LESION", **get_span(text_4082755, "Peripheral lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_4082755, "Mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_4082755, "Lung nodule/mass", 1)},

    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_4082755, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_4082755, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_4082755, "EBUS", 1)}, # In (EBUS-TBNA)
    {"label": "PROC_ACTION", **get_span(text_4082755, "TBNA", 1)}, # In (EBUS-TBNA)
    {"label": "PROC_METHOD", **get_span(text_4082755, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4082755, "Ion platform", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4082755, "peripheral lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_4082755, "biopsy", 1)}, # In peripheral lung biopsy
    {"label": "PROC_METHOD", **get_span(text_4082755, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4082755, "Transbronchial lung biopsy", 1)},

    # Anesthesia & Time
    {"label": "CTX_TIME", **get_span(text_4082755, "08:30", 1)},
    {"label": "CTX_TIME", **get_span(text_4082755, "10:18", 1)},
    {"label": "CTX_TIME", **get_span(text_4082755, "108 minutes", 1)},

    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_4082755, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4082755, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4082755, "21G", 1)},
    {"label": "PROC_METHOD", **get_span(text_4082755, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_4082755, "Ion", 2)}, # "Ion (Intuitive..."
    {"label": "DEV_INSTRUMENT", **get_span(text_4082755, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4082755, "20 MHz miniprobe", 1)},

    # Part 1: EBUS
    {"label": "MEAS_SIZE", **get_span(text_4082755, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4082755, "linear EBUS bronchoscope", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_4082755, "Station 4L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "21.5mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "32.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4082755, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4082755, "21G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_4082755, "Malignant - NSCLC NOS", 1)},

    # Station 10L
    {"label": "ANAT_LN_STATION", **get_span(text_4082755, "Station 10L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "21.1mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "12.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4082755, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_4082755, "21G needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_4082755, "Malignant - NSCLC NOS", 2)},

    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(text_4082755, "Station 11L", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "8.8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "15.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4082755, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4082755, "21G needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_4082755, "Malignant - squamous cell carcinoma", 1)},

    # Part 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_4082755, "Ion robotic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4082755, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4082755, "superior lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4082755, "B4", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "24.3 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4082755, "39.0 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_4082755, "Solid", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4082755, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4082755, "Radial EBUS probe", 2)}, # 2nd occurrence in text (1st in Equip)
    {"label": "PROC_METHOD", **get_span(text_4082755, "Augmented fluoroscopy", 1)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_4082755, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4082755, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4082755, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_4082755, "TBNA", 2)}, # 1st was in Procedure List
    {"label": "MEAS_COUNT", **get_span(text_4082755, "2 passes", 3)},
    {"label": "PROC_ACTION", **get_span(text_4082755, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4082755, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_4082755, "Adequate lymphocytes", 1)},

    # Specimens
    {"label": "SPECIMEN", **get_span(text_4082755, "EBUS-TBNA specimens", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4082755, "4L", 2)}, # Inside "stations 4L, 10L..."
    {"label": "ANAT_LN_STATION", **get_span(text_4082755, "10L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_4082755, "11L", 2)},
    {"label": "SPECIMEN", **get_span(text_4082755, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4082755, "LUL", 2)},
    {"label": "SPECIMEN", **get_span(text_4082755, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4082755, "LUL", 3)},
    {"label": "PROC_ACTION", **get_span(text_4082755, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4082755, "LUL", 4)},

    # Complications / Outcomes
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4082755, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4082755, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4082755, "No pneumothorax", 1)},

    # Impression
    {"label": "PROC_METHOD", **get_span(text_4082755, "EBUS-TBNA", 2)}, # 1st in Proc List
    {"label": "PROC_METHOD", **get_span(text_4082755, "robotic bronchoscopy", 1)}, # "Robotic-assisted..." earlier, this is exact match
    {"label": "PROC_ACTION", **get_span(text_4082755, "peripheral nodule biopsy", 1)},
    {"label": "OBS_ROSE", **get_span(text_4082755, "ROSE adequate", 1)},

    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4082755, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": "4082755", "text": text_4082755, "entities": entities_4082755})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)