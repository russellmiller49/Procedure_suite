import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 2590875
# ==========================================
id_1 = "2590875"
text_1 = """PROCEDURE NOTE - CODING DOCUMENTATION

Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]
Date of Service: [REDACTED]
Performing Physician: Michael Rodriguez, MD
Facility: [REDACTED]

PROCEDURES PERFORMED WITH CPT CODE JUSTIFICATION:

1. ENDOBRONCHIAL ULTRASOUND-GUIDED TRANSBRONCHIAL NEEDLE ASPIRATION (CPT 31653)
   - Equipment: Olympus BF-UC260F-OL8 linear EBUS bronchoscope
   - Needle: 21-gauge Standard FNA (Standard FNA)
   - STATIONS SAMPLED: 5 DISTINCT MEDIASTINAL/HILAR LYMPH NODE STATIONS
     * Station 10R: 2 passes, short axis 17.1mm
     * Station 11R: 2 passes, short axis 8.4mm
     * Station 11L: 4 passes, short axis 22.2mm
     * Station 2R: 4 passes, short axis 21.9mm
     * Station 4L: 4 passes, short axis 18.5mm
   - ROSE performed at each station: YES
   - Code justification: ≥3 mediastinal/hilar lymph node stations sampled under real-time ultrasound guidance

2. COMPUTER-ASSISTED IMAGE-GUIDED NAVIGATION (CPT +31627)
   - Platform: Ion Robotic Bronchoscopy System (Intuitive Surgical)
   - Registration method: CT-to-body
   - Registration accuracy: 2.6 mm
   - Navigation to peripheral lesion: RLL lateral basal (B9)
   - Code justification: Computer-assisted electromagnetic navigation used to guide bronchoscope to peripheral lung lesion beyond direct visualization

3. ENDOBRONCHIAL ULTRASOUND FOR PERIPHERAL LESION (CPT +31654)
   - Equipment: 20 MHz radial EBUS miniprobe
   - Probe visualization: Adjacent view of 28.6mm lesion
   - Used to confirm catheter position relative to peripheral target
   - Code justification: Radial EBUS performed to localize peripheral pulmonary lesion during bronchoscopic intervention

4. TRANSBRONCHIAL LUNG BIOPSY, SINGLE LOBE (CPT 31628)
   - Location: RLL lobe
   - Forceps biopsies obtained: 5 specimens
   - Additional TBNA: 4 passes
   - Brushings: 2 specimens
   - Tool-in-lesion confirmed via: Augmented fluoroscopy
   - Code justification: Multiple transbronchial biopsies obtained from single lobe for tissue diagnosis

SPECIMEN DOCUMENTATION:
- EBUS-TBNA specimens: Cytology, cell block, flow cytometry
- Transbronchial biopsies: Surgical pathology, molecular testing
- Brushings: Cytology
- BAL: Bacterial, fungal, AFB cultures

PROCEDURE TIME: 09:30 - 11:02 (92 minutes)
ANESTHESIA: General anesthesia (ASA 4)
COMPLICATIONS: None

CPT CODES SUBMITTED: 31653, 31627, 31654, 31628
TOTAL FACILITY RVU: 18.41
ESTIMATED FACILITY PAYMENT: $595

Attestation: I personally performed all documented procedures. Documentation supports medical necessity and code selection.

Michael Rodriguez, MD
[REDACTED]"""

entities_1 = [
    # --- Procedure 1: EBUS-TBNA ---
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL NEEDLE ASPIRATION", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "linear EBUS bronchoscope", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21-gauge", 1)},
    
    # Stations and Metrics
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 10R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "17.1mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.4mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 11L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "22.2mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 2R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "21.9mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(text_1, "Station 4L", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "18.5mm", 1)},
    
    # --- Procedure 2: Navigation ---
    {"label": "PROC_METHOD", **get_span(text_1, "Ion Robotic Bronchoscopy System", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.6 mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lateral basal (B9)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Computer-assisted electromagnetic navigation", 1)},
    
    # --- Procedure 3: Radial EBUS ---
    {"label": "PROC_METHOD", **get_span(text_1, "ENDOBRONCHIAL ULTRASOUND", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "radial EBUS miniprobe", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "28.6mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Radial EBUS", 1)},
    
    # --- Procedure 4: TBB ---
    {"label": "PROC_ACTION", **get_span(text_1, "TRANSBRONCHIAL LUNG BIOPSY", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)}, # Context: "Forceps biopsies"
    {"label": "MEAS_COUNT", **get_span(text_1, "5 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 2)}, # Context: "Additional TBNA"
    {"label": "MEAS_COUNT", **get_span(text_1, "4 passes", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "2 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Augmented fluoroscopy", 1)},
    
    # --- Specimens & Metadata ---
    {"label": "PROC_ACTION", **get_span(text_1, "EBUS-TBNA", 1)}, # In Specimen section
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "cell block", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "flow cytometry", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Transbronchial biopsies", 1)}, # In Specimen section
    {"label": "SPECIMEN", **get_span(text_1, "Surgical pathology", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "molecular testing", 1)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "Brushings", 2)}, # In Specimen section
    {"label": "SPECIMEN", **get_span(text_1, "Cytology", 2)},
    
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Bacterial", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "fungal", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "AFB cultures", 1)},
    
    {"label": "CTX_TIME", **get_span(text_1, "09:30 - 11:02", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "92 minutes", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)