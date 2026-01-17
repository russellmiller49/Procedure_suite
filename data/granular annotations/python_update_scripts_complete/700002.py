import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Data Definition
# ==========================================
NOTE_ID = "golden_700002"

# Source note text embedded as an escaped JSON string for safety.
RAW_TEXT = "Name: [REDACTED]\nMRN: [REDACTED]\nDOB: [REDACTED] (59 years)\nDate of Service: [REDACTED]\nLocation: Bronchoscopy/Procedural Suite\n\nProcedure: Robotic navigational bronchoscopy with radial EBUS confirmation and transbronchial biopsies of peripheral RUL nodule.\nOperating Physician: Michael Thompson, MD (Interventional Pulmonology)\nAssistant: Brian Wu, MD (Pulmonary Fellow)\nRT: Sarah Long, RRT\nRN: Casey Nguyen, RN\n\nIndication:\n59-year-old female with 8 mm posterior segment right upper lobe nodule, intensely PET-avid, bronchus sign positive on CT, no clear mediastinal adenopathy. Referred for minimally invasive diagnostic biopsy.\n\nAnesthesia/Airway:\nGeneral anesthesia with LMA provided by Anesthesia team. Patient in supine position. Standard ASA monitors in place.\n\nProcedure Description:\nFollowing time-out, the robotic bronchoscopy platform was docked (Monarch system). Pre-procedure CT was loaded and registration performed using automatic airway mapping with final registration error < 2 mm.\n\nUsing the navigation interface, the robotic scope was advanced to the posterior segment of the RUL following the virtual pathway. The working channel was aligned to the target; divergence from the target center was < 3 mm.\n\nRadial EBUS:\nA radial EBUS probe with guide sheath was advanced through the working channel. A concentric, solid lesion was visualized corresponding to the CT target. The guide sheath was left in place at the point of maximal signal.\n\nSampling:\nThrough the guide sheath, the following samples were obtained:\n\u2022 Transbronchial forceps biopsies: 6 passes from the RUL posterior segment nodule.\n\u2022 Transbronchial needle aspiration: 3 passes with a 21G needle targeting the same lesion.\n\u2022 Cytology brushings: 2 passes from the nodule.\n\nAll samples were sent for histology, cytology, microbiology, and molecular profiling including PD-L1. No significant bleeding occurred; minor oozing resolved with wedging and suction.\n\nComplications:\nNo hypoxia, arrhythmia, or pneumothorax was observed. Fluoroscopy was used intermittently to confirm tool position. Estimated blood loss < 5 mL.\n\nDisposition/Plan:\nPatient [REDACTED] and transported to PACU in stable condition. Post-procedure CXR to evaluate for pneumothorax was ordered. Follow-up visit in IP clinic in 1\u20132 weeks to discuss results and management options.\n\nImpression:\nSuccessful robotic navigational bronchoscopy with radial EBUS confirmation and transbronchial sampling of an 8 mm RUL posterior segment nodule. Final pathology pending."


def get_span(text: str, term: str, occurrence: int = 1) -> dict:
    """Return a span dict for the Nth occurrence of `term` in `text`."""
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}


entities = [
    # Target / anatomy
    {"label": "MEAS_SIZE", **get_span(RAW_TEXT, "8 mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(RAW_TEXT, "right upper lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(RAW_TEXT, "posterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(RAW_TEXT, "RUL", 1)},

    # Guidance / methods
    {"label": "PROC_METHOD", **get_span(RAW_TEXT, "Robotic", 1)},
    {"label": "PROC_METHOD", **get_span(RAW_TEXT, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(RAW_TEXT, "Fluoroscopy", 1)},

    # Platform / device-ish nouns
    {"label": "DEV_INSTRUMENT", **get_span(RAW_TEXT, "Monarch system", 1)},
    {"label": "MEAS_SIZE", **get_span(RAW_TEXT, "registration error < 2 mm", 1)},

    # Actions / sampling modalities
    {"label": "PROC_ACTION", **get_span(RAW_TEXT, "Transbronchial forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(RAW_TEXT, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(RAW_TEXT, "6 passes", 1)},

    {"label": "PROC_ACTION", **get_span(RAW_TEXT, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(RAW_TEXT, "21G", 1)},
    {"label": "MEAS_COUNT", **get_span(RAW_TEXT, "3 passes", 1)},

    {"label": "PROC_ACTION", **get_span(RAW_TEXT, "Cytology brushings", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(RAW_TEXT, "brush", 1)},
    {"label": "MEAS_COUNT", **get_span(RAW_TEXT, "2 passes", 1)},

    # Outcome / complications (explicit negatives)
    {"label": "OUTCOME_COMPLICATION", **get_span(RAW_TEXT, "No hypoxia, arrhythmia, or pneumothorax", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(RAW_TEXT, "Estimated blood loss < 5 mL", 1)},
]

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    add_case(NOTE_ID, RAW_TEXT, entities, REPO_ROOT)
