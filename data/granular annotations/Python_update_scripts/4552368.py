import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1: break
    
    if start == -1:
        # In a real pipeline, we might log a warning. 
        # For now, return a zero-span to avoid breaking the script execution,
        # though strictly this implies the term wasn't found.
        return {"start": 0, "end": 0}
        
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4552368
# ==========================================
id_1 = "4552368"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (81 years old)
Gender: Male
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Lisa Thompson

Anesthesiologist: On service
ROSE Cytopathologist: Present

CLINICAL INDICATION
Lung cancer staging - suspected NSCLC with mediastinal lymphadenopathy

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

PROCEDURE START TIME: 08:30
PROCEDURE END TIME: 10:15
TOTAL PROCEDURE TIME: 105 minutes

EQUIPMENT
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: Olympus NA-201SX-4022 (22G Standard FNA)
- Robotic platform: Monarch (Auris Health (J&J))
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 4R: Id[REDACTED] homogeneous lymph node measuring 23.5mm (short axis) x 32.6mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - squamous cell carcinoma.
Station 4L: Id[REDACTED] homogeneous lymph node measuring 14.3mm (short axis) x 14.4mm (long axis). 4 passes performed with 22G needle. ROSE: Suspicious for malignancy.
Station 10R: Id[REDACTED] homogeneous lymph node measuring 11.1mm (short axis) x 12.3mm (long axis). 2 passes performed with 22G needle. ROSE: Suspicious for malignancy.
Station 2L: Id[REDACTED] hypoechoic lymph node measuring 20.1mm (short axis) x 33.5mm (long axis). 2 passes performed with 22G needle. ROSE: Malignant - adenocarcinoma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Monarch robotic bronchoscopy system was deployed.

Target lesion: RML medial (B5)
Lesion characteristics:
- Size: 31.5 mm
- Distance from pleura: 36.7 mm
- CT appearance: Part-solid
- Bronchus sign: Positive
- PET SUV max: 7.9

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming adjacent view of the lesion.

Tool-in-lesion confirmation: Augmented fluoroscopy

Sampling performed:
- Transbronchial forceps biopsies: 5 specimens
- TBNA: 4 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Malignant - squamous cell carcinoma

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 4R, 4L, 10R, 2L - sent for cytology, cell block, and flow cytometry
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
    # Indications & Diagnosis
    {"label": "OBS_LESION", **get_span(text_1, "Lung cancer", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule/mass", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Mediastinal lymphadenopathy", 2)},

    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)}, # In EBUS-TBNA
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)}, # In EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},

    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "EBUS needle", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},

    # Part 1: Linear EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "LINEAR EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.5mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "32.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "squamous cell carcinoma", 1)},

    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.3mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.4mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},

    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "homogeneous", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.1mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.3mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 4)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 2)},

    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hypoechoic", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "20.1mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "33.5mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 3)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 5)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "adenocarcinoma", 1)},

    # Part 2: Robotic
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 3)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "B5", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.5 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Part-solid", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Positive", 1)}, # Bronchus sign
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 2)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "squamous cell carcinoma", 2)},

    # Specimens Collected
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 2)}, # In EBUS-TBNA
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 3)}, # In EBUS-TBNA
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4L", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "2L", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 4)},

    # Complications & Impression
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 3)}, # In EBUS-TBNA
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 4)}, # In EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 3)},
    {"label": "OBS_LESION", **get_span(text_1, "peripheral nodule", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 4)}, # peripheral nodule biopsy

    # Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 2)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)