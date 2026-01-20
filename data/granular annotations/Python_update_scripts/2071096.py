import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case
except ImportError:
    print(f"Error: Could not import 'add_case' from {REPO_ROOT}/scripts/add_training_case.py")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            # If the term/occurrence isn't found, return None or raise warning.
            # Returning None allows the list comprehension to filter it out if handled.
            print(f"Warning: Term '{term}' (occurrence {occurrence}) not found.")
            return None
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 2071096
# ==========================================
id_1 = "2071096"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Robert Patel, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Fujifilm EB-580S linear EBUS bronchoscope
   - Needle: 22-gauge Standard FNA (FNB/ProCore)
   - STATIONS SAMPLED: 3 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 10L: 3 passes, short axis 13.0mm
     * Station 4L: 2 passes, short axis 15.7mm
     * Station 11L: 2 passes, short axis 19.4mm


   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Ion Robotic Bronchoscopy System (Intuitive Surgical)
   - Registration method: CT-to-body
   - Registration accuracy: 1.8 mm
   - Navigation to peripheral lesion: RUL anterior (B3)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Eccentric view of 21.6mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RUL lobe
   - Forceps biopsies obtained: 8 specimens
   - Additional TBNA: 4 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: CBCT
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 08:15 - 09:40 (85 minutes)
ANESTHESIA: General anesthesia (ASA 3)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Robert Patel, MD
[REDACTED]"""

entities_1 = [
    # --- Section 1: EBUS-TBNA ---
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "FNA", 1)},
    
    # Stations and Measurements
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.0mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15.7mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)}, # Second occurrence of "2 passes"
    {"label": "MEAS_SIZE", **get_span(text_1, "19.4mm", 1)},
    
    # --- Section 2: Navigation ---
    {"label": "PROC_METHOD", **get_span(text_1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Ion Robotic Bronchoscopy System", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "anterior (B3)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "electromagnetic navigation", 1)},
    
    # --- Section 3: Peripheral EBUS ---
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)}, # In Justification
    {"label": "PROC_METHOD", **get_span(text_1, "radial EBUS", 1)}, # In Equipment (lowercase 'r' check text) -> Text has "radial EBUS miniprobe"
    {"label": "MEAS_SIZE", **get_span(text_1, "21.6mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "lesion", 2)}, # "21.6mm lesion" is 2nd occurrence (1st is "peripheral lesion" in nav section)
    
    # --- Section 4: Biopsy ---
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)}, # Brushings count
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},
    
    # --- Specimens / Outcomes / Time ---
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "08:15", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "85 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)} # Matches COMPLICATIONS: None
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)