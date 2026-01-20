import sys
from pathlib import Path

# Set up the repository root path
# Assumes this script is run from within the repository structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the system path to allow importing the utility function
sys.path.append(str(REPO_ROOT))

# Import the utility function to add the case
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure the script is located in the correct directory structure relative to 'scripts/'.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The specific occurrence to find (1-based index).
    
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in the provided text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 2530243
# ==========================================
id_1 = "2530243"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Steven Park, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Fujifilm EB-580S linear EBUS bronchoscope
   - Needle: 21-gauge Standard FNA (Standard FNA)
   - STATIONS SAMPLED: 3 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 7: 2 passes, short axis 8.3mm
     * Station 11R: 4 passes, short axis 19.4mm
     * Station 11L: 4 passes, short axis 14.1mm


   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Ion Robotic Bronchoscopy System (Intuitive Surgical)
   - Registration method: CT-to-body
   - Registration accuracy: 2.5 mm
   - Navigation to peripheral lesion: LUL superior lingula (B4)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Adjacent view of 34.7mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: LUL lobe
   - Forceps biopsies obtained: 5 specimens
   - Additional TBNA: 3 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Radial EBUS
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 07:00 - 09:02 (122 minutes)
ANESTHESIA: General anesthesia (ASA 3)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

[REDACTED], MD
[REDACTED]"""

entities_1 = [
    # Procedure 1: EBUS-TBNA
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND-GUIDED", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fujifilm EB-580S linear EBUS bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.3mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4mm", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "14.1mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "real-time ultrasound guidance", 1)},

    # Procedure 2: Navigation
    {"label": "PROC_METHOD", **get_span(text_1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion Robotic Bronchoscopy System", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL superior lingula (B4)", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 1)}, # Context: peripheral lesion
    {"label": "PROC_METHOD", **get_span(text_1, "Computer-assisted electromagnetic navigation", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)}, # Context: peripheral lung lesion

    # Procedure 3: Radial EBUS
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 2)}, # Header for 3
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "radial EBUS miniprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "34.7mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 3)}, # Context: 34.7mm lesion
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 4)}, # Context: pulmonary lesion

    # Procedure 4: Biopsy
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # First TBNA was in title, strictly matching "TBNA" here
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 2)},

    # Specimens & Other
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "07:00 - 09:02", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "122 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)