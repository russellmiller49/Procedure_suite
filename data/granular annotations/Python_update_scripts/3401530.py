import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo or similar structure)
# Adjust this logic as needed for your specific environment.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Mocking the utility import for standalone generation. 
# In a real environment, ensure scripts.add_training_case is accessible.
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback/Placeholder if the module isn't strictly available in this generation context
    def add_case(case_id, text, entities, root):
        print(f"Would add case {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    case_sensitive=True (Python find is case sensitive).
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 3401530
# ==========================================
id_1 = "3401530"
text_1 = """INTERVENTIONAL PULMONOLOGY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (82 years old)
Gender: Female
Date of Service: [REDACTED]
Location: [REDACTED]

CARE TEAM
Attending Physician: Dr. Lisa Thompson
Fellow: Dr. Kevin Chang (PGY-6)
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
2. Robotic-assisted bronchoscopy (Galaxy platform) with peripheral lung biopsy
3. Radial EBUS for peripheral lesion localization
4. Transbronchial lung biopsy

ANESTHESIA
Type: General anesthesia with endotracheal intubation
ASA Class: 2

PROCEDURE START TIME: 08:00
PROCEDURE END TIME: 10:05
TOTAL PROCEDURE TIME: 125 minutes

EQUIPMENT
- Linear EBUS scope: Pentax EB-1990i
- EBUS needle: Olympus NA-201SX-4021 (21G Standard FNA)
- Robotic platform: Galaxy (Noah Medical)
- Radial EBUS probe: 20 MHz miniprobe

PROCEDURE DETAILS

PART 1: LINEAR EBUS FOR MEDIASTINAL STAGING

The patient was brought to the procedure suite and placed in supine position. After induction of general anesthesia and endotracheal intubation with an 8.0 mm ETT, the linear EBUS bronchoscope was advanced through the ETT.

Systematic mediastinal lymph node sampling was performed at the following stations:

Station 10R: Id[REDACTED] homogeneous lymph node measuring 11.9mm (short axis) x 22.1mm (long axis). 3 passes performed with 21G needle. ROSE: Malignant - squamous cell carcinoma.
Station 4R: Id[REDACTED] homogeneous lymph node measuring 21.4mm (short axis) x 27.6mm (long axis). 2 passes performed with 21G needle. ROSE: Suspicious for malignancy.
Station 7: Id[REDACTED] hypoechoic lymph node measuring 16.1mm (short axis) x 28.6mm (long axis). 4 passes performed with 21G needle. ROSE: Granuloma.

PART 2: ROBOTIC BRONCHOSCOPY FOR PERIPHERAL LESION

Following completion of mediastinal staging, the Galaxy robotic bronchoscopy system was deployed.

Target lesion: RLL posterior basal (B10)
Lesion characteristics:
- Size: 23.3 mm
- Distance from pleura: 12.3 mm
- CT appearance: Solid
- Bronchus sign: Negative
- PET SUV max: 2.8

Navigation was performed successfully with registration error < 3mm. The robotic catheter was advanced to the target location. Radial EBUS probe was deployed confirming concentric view of the lesion.

Tool-in-lesion confirmation: CBCT

Sampling performed:
- Transbronchial forceps biopsies: 6 specimens
- TBNA: 3 passes
- Brushings: 2 specimens

ROSE result from peripheral lesion: Adequate lymphocytes, no malignancy

SPECIMENS COLLECTED
1. EBUS-TBNA specimens from stations 10R, 4R, 7 - sent for cytology, cell block, and flow cytometry
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

Lisa Thompson
Interventional Pulmonology
Community Hospital

CPT CODES: 31653, 31627, 31654, 31628
"""

entities_1 = [
    # Indication / Diagnosis
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "mediastinal lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Lung nodule/mass", 1)},
    
    # Procedures Performed
    {"label": "PROC_METHOD", **get_span(text_1, "Linear endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial needle aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic-assisted bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy platform", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral lung biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial lung biopsy", 1)},
    
    # Anesthesia / Time
    {"label": "PROC_ACTION", **get_span(text_1, "endotracheal intubation", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "08:00", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "10:05", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "125 minutes", 1)},
    
    # Equipment
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Linear EBUS scope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Pentax EB-1990i", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "Olympus NA-201SX-4021", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G Standard FNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic platform", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 2)}, # In equipment list
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "20 MHz miniprobe", 1)},
    
    # Part 1
    {"label": "PROC_METHOD", **get_span(text_1, "LINEAR EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "endotracheal intubation", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0 mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "11.9mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.1mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G needle", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Malignant - squamous cell carcinoma", 1)},
    
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.4mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G needle", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
    
    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.1mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.6mm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G needle", 3)},
    {"label": "OBS_ROSE", **get_span(text_1, "Granuloma", 1)},
    
    # Part 2
    {"label": "PROC_METHOD", **get_span(text_1, "ROBOTIC BRONCHOSCOPY", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy robotic bronchoscopy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL posterior basal (B10)", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "23.3 mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12.3 mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Solid", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bronchus sign", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "< 3mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "robotic catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Radial EBUS probe", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    
    # Sampling
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial forceps biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Adequate lymphocytes, no malignancy", 1)},
    
    # Specimens / Outcome / Plan
    {"label": "SPECIMEN", **get_span(text_1, "EBUS-TBNA specimens", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "10R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 2)}, # In 'stations 10R, 4R, 7'
    {"label": "SPECIMEN", **get_span(text_1, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)}, # In 'from RLL'
    {"label": "SPECIMEN", **get_span(text_1, "Brushings", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 3)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 4)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No pneumothorax noted", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "<10 mL", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS-TBNA", 2)},
    {"label": "PROC_METHOD", **get_span(text_1, "robotic bronchoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "peripheral nodule biopsy", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "2 hours", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)