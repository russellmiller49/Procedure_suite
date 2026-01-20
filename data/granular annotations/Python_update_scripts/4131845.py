import sys
from pathlib import Path

# Set up the repository root path (assuming script is running from within the repo)
# Adjust the number of .parent calls based on your actual directory structure
try:
    REPO_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    # Fallback for interactive environments
    REPO_ROOT = Path('.').resolve()

# Add the scripts directory to sys.path to import the utility
sys.path.append(str(REPO_ROOT))

# Import the add_case utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Warning: Could not import 'add_case'. Ensure the script is placed correctly relative to 'scripts/'.")
    def add_case(case_id, text, entities, root):
        print(f"Mock processing {case_id}...")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Case: 4131845
# ==========================================
id_1 = "4131845"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Amanda Foster, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Olympus BF-UC190F linear EBUS bronchoscope
   - Needle: 22-gauge FNB/ProCore (FNB/ProCore)
   - STATIONS SAMPLED: 3 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 4L: 3 passes, short axis 9.1mm
     * Station 2R: 3 passes, short axis 14.9mm
     * Station 2L: 2 passes, short axis 13.2mm


   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Ion Robotic Bronchoscopy System (Intuitive Surgical)
   - Registration method: CT-to-body
   - Registration accuracy: 1.8 mm
   - Navigation to peripheral lesion: RLL superior (B6)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Adjacent view of 27.1mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RLL lobe
   - Forceps biopsies obtained: 5 specimens
   - Additional TBNA: 2 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Augmented fluoroscopy
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 09:15 - 11:03 (108 minutes)
ANESTHESIA: General anesthesia (ASA 3)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Amanda Foster, MD
[REDACTED]"""

entities_1 = [
    # Procedure 1: EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    
    # Stations
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "9.1mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.9mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.2mm", 1)},

    # Procedure 2: Navigation
    {"label": "PROC_METHOD", **get_span(text_1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Robotic Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "peripheral lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL superior", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "B6", 1)}, # Segmental bronchus
    {"label": "PROC_METHOD", **get_span(text_1, "electromagnetic navigation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "bronchoscope", 2)},
    
    # Procedure 3: Peripheral EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "PERIPHERAL LESION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "27.1mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 4)}, # "Adjacent view of 27.1mm lesion"
    
    # Procedure 4: Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # "Additional TBNA"
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "transbronchial biopsies", 1)},

    # Specimens & Context
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "09:15", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "11:03", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "108 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)