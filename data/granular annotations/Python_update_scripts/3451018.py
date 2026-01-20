import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the scripts directory
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

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
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 3451018
# ==========================================
t1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Lisa Thompson, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Pentax EB-1990i linear EBUS bronchoscope
   - Needle: 21-gauge Standard FNA (Acquire)
   - STATIONS SAMPLED: 3 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 10R: 3 passes, short axis 11.9mm
     * Station 4R: 2 passes, short axis 21.4mm
     * Station 7: 4 passes, short axis 16.1mm


   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Galaxy Robotic Bronchoscopy System (Noah Medical)
   - Registration method: CT-to-body
   - Registration accuracy: 2.4 mm
   - Navigation to peripheral lesion: RLL posterior basal (B10)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Concentric view of 23.3mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RLL lobe
   - Forceps biopsies obtained: 6 specimens
   - Additional TBNA: 3 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: CBCT
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 08:00 - 10:05 (125 minutes)
ANESTHESIA: General anesthesia (ASA 2)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Lisa Thompson, MD
[REDACTED]"""

e1 = [
    # Section 1: EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(t1, "ENDOBRONCHIAL ULTRASOUND-GUIDED", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Pentax EB-1990i linear EBUS bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21-gauge", 1)},
    
    # Stations
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 10R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "11.9mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 4R", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "21.4mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(t1, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "16.1mm", 1)},

    # Section 2: Navigation
    {"label": "PROC_METHOD", **get_span(t1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Galaxy Robotic Bronchoscopy System", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL posterior basal (B10)", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Computer-assisted electromagnetic navigation", 1)},
    {"label": "OBS_LESION", **get_span(t1, "peripheral lung lesion", 1)},

    # Section 3: Peripheral EBUS
    {"label": "PROC_METHOD", **get_span(t1, "ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "20 MHz radial EBUS miniprobe", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Concentric view", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "23.3mm", 1)},
    {"label": "OBS_LESION", **get_span(t1, "lesion", 4)}, # "23.3mm lesion"
    {"label": "PROC_METHOD", **get_span(t1, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t1, "peripheral pulmonary lesion", 1)},

    # Section 4: Biopsy
    {"label": "PROC_ACTION", **get_span(t1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)}, # "Additional TBNA"
    {"label": "MEAS_COUNT", **get_span(t1, "3 passes", 2)}, # "Additional TBNA: 3 passes"
    {"label": "PROC_ACTION", **get_span(t1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "2 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CBCT", 1)},

    # Specimens & Outcomes
    {"label": "SPECIMEN", **get_span(t1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(t1, "flow cytometry", 1)},
    {"label": "SPECIMEN", **get_span(t1, "Cytology", 2)}, # Brushings: Cytology
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "SPECIMEN", **get_span(t1, "cultures", 1)},
    
    # Timing & Complications
    {"label": "CTX_TIME", **get_span(t1, "08:00", 1)},
    {"label": "CTX_TIME", **get_span(t1, "10:05", 1)},
    {"label": "CTX_TIME", **get_span(t1, "125 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)}
]

BATCH_DATA.append({"id": "3451018", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)