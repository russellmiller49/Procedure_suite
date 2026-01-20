import sys
from pathlib import Path

# Set up the repository root assuming this script is in a subdirectory (e.g., /scripts/processed/)
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'. check your directory structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in the provided text.")
    
    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ==========================================
# Note 1: 5220444
# ==========================================
t_5220444 = r"""PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Andrew Nakamura, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Fujifilm EB-580S linear EBUS bronchoscope
   - Needle: 21-gauge Standard FNA (Standard FNA)
   - STATIONS SAMPLED: 4 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 7: 4 passes, short axis 19.5mm
     * Station 11L: 2 passes, short axis 18.1mm
     * Station 10R: 4 passes, short axis 17.1mm
     * Station 4L: 3 passes, short axis 11.5mm

   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Monarch Robotic Bronchoscopy System (Auris Health (J&J))
   - Registration method: CT-to-body
   - Registration accuracy: 1.6 mm
   - Navigation to peripheral lesion: LUL anterior (B3)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Eccentric view of 25.0mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: LUL lobe
   - Forceps biopsies obtained: 4 specimens
   - Additional TBNA: 3 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Fluoroscopy
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 07:30 - 09:33 (123 minutes)
ANESTHESIA: General anesthesia (ASA 3)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Andrew Nakamura, MD
[REDACTED]"""

e_5220444 = [
    # --- Procedure 1: EBUS-TBNA ---
    {"label": "PROC_METHOD", **get_span(t_5220444, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(t_5220444, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "PROC_METHOD", **get_span(t_5220444, "EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t_5220444, "21-gauge", 1)},
    
    # Station 7
    {"label": "ANAT_LN_STATION", **get_span(t_5220444, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(t_5220444, "4 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t_5220444, "19.5mm", 1)},
    
    # Station 11L
    {"label": "ANAT_LN_STATION", **get_span(t_5220444, "Station 11L", 1)},
    {"label": "MEAS_COUNT", **get_span(t_5220444, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t_5220444, "18.1mm", 1)},
    
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(t_5220444, "Station 10R", 1)},
    {"label": "MEAS_COUNT", **get_span(t_5220444, "4 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(t_5220444, "17.1mm", 1)},
    
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(t_5220444, "Station 4L", 1)},
    {"label": "MEAS_COUNT", **get_span(t_5220444, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(t_5220444, "11.5mm", 1)},

    # --- Procedure 2: Navigation ---
    {"label": "PROC_METHOD", **get_span(t_5220444, "Robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_5220444, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_5220444, "B3", 1)},

    # --- Procedure 3: Radial EBUS ---
    {"label": "PROC_METHOD", **get_span(t_5220444, "ENDOBRONCHIAL ULTRASOUND", 2)},
    {"label": "PROC_METHOD", **get_span(t_5220444, "radial EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(t_5220444, "25.0mm", 1)},

    # --- Procedure 4: Biopsy ---
    {"label": "PROC_ACTION", **get_span(t_5220444, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t_5220444, "LUL", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t_5220444, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t_5220444, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t_5220444, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t_5220444, "3 passes", 2)}, # Additional TBNA
    {"label": "MEAS_COUNT", **get_span(t_5220444, "2 specimens", 1)}, # Brushings count
    {"label": "PROC_METHOD", **get_span(t_5220444, "Fluoroscopy", 1)},

    # --- Timestamps ---
    {"label": "CTX_TIME", **get_span(t_5220444, "07:30", 1)},
    {"label": "CTX_TIME", **get_span(t_5220444, "09:33", 1)},
    {"label": "CTX_TIME", **get_span(t_5220444, "123 minutes", 1)},
]

BATCH_DATA.append({"id": "5220444", "text": t_5220444, "entities": e_5220444})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)