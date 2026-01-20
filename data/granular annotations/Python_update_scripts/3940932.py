import sys
from pathlib import Path

# Dynamic REPO_ROOT calculation to locate the utility script
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = 0
    for i in range(occurrence):
        pos = text.find(term, start)
        if pos == -1:
            return None
        # If this is the requested occurrence, return the span
        if i == occurrence - 1:
            return {"start": pos, "end": pos + len(term)}
        # Otherwise, move past this occurrence
        start = pos + 1
    return None

# ==========================================
# Note 1: 3940932
# ==========================================
id_1 = "3940932"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Brian O'Connor, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Olympus BF-UC180F linear EBUS bronchoscope
   - Needle: 22-gauge Acquire (FNB/ProCore)
   - STATIONS SAMPLED: 5 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 10R: 4 passes, short axis 16.6mm
     * Station 4R: 2 passes, short axis 13.5mm
     * Station 2L: 4 passes, short axis 11.0mm
     * Station 2R: 4 passes, short axis 21.8mm
     * Station 4L: 3 passes, short axis 22.9mm
   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Monarch Robotic Bronchoscopy System (Auris Health (J&J))
   - Registration method: CT-to-body
   - Registration accuracy: 2.2 mm
   - Navigation to peripheral lesion: LUL inferior lingula (B5)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Concentric view of 31.2mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: LUL lobe
   - Forceps biopsies obtained: 6 specimens
   - Additional TBNA: 2 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: CBCT
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 07:15 - 08:33 (78 minutes)
ANESTHESIA: General anesthesia (ASA 2)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Brian O'Connor, MD
[REDACTED]"""

entities_1 = [
    # --- Procedure 1: EBUS-TBNA ---
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND-GUIDED", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22-gauge", 1)},
    # Station 10R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "16.6mm", 1)},
    # Station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "13.5mm", 1)},
    # Station 2L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)}, # 2nd occurrence of "4 passes"
    {"label": "MEAS_SIZE", **get_span(text_1, "11.0mm", 1)},
    # Station 2R
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)}, # 3rd occurrence of "4 passes"
    {"label": "MEAS_SIZE", **get_span(text_1, "21.8mm", 1)},
    # Station 4L
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.9mm", 1)},
    # General Actions
    {"label": "PROC_ACTION", **get_span(text_1, "ROSE", 1)},

    # --- Procedure 2: Navigation ---
    {"label": "PROC_METHOD", **get_span(text_1, "COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch Robotic Bronchoscopy System", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL inferior lingula (B5)", 1)},

    # --- Procedure 3: Radial EBUS ---
    # Note: "ENDOBRONCHIAL ULTRASOUND" in header 3 is the 2nd occurrence of the phrase
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "radial EBUS miniprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "31.2mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)}, # Capitalized in justification

    # --- Procedure 4: Biopsy ---
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)}, # "Forceps biopsies obtained"
    {"label": "MEAS_COUNT", **get_span(text_1, "6 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)}, # "Additional TBNA"
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)}, # 2nd occurrence of "2 passes"
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "CBCT", 1)},

    # --- Specimens & Metadata ---
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 2)}, # In Brushings line
    {"label": "CTX_TIME", **get_span(text_1, "07:15 - 08:33", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "78 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)