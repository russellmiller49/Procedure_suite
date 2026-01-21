import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Expected location:
# data/granular_annotations/python_scripts/Granular_note_700005.py
# parents[3] => repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Note Text (Authoritative)
# ==========================================
NOTE_ID = "golden_700005"

RAW_TEXT = """
PROCEDURE: Bedside diagnostic and therapeutic left thoracentesis without imaging guidance.

INDICATION:
82-year-old female with chronic systolic heart failure and progressive dyspnea with a large left pleural effusion.

PROCEDURE DESCRIPTION:
The patient was seated upright. The left posterior hemithorax was prepped and draped in sterile fashion.
Percussion and auscultation identified dullness consistent with pleural effusion.

Local anesthesia with 1% lidocaine was administered at the left posterior 8th intercostal space.
Using landmark technique, an 18G catheter was inserted with immediate return of straw-colored fluid.

Approximately 60 mL was aspirated for diagnostic studies.
An additional 900 mL was drained slowly for therapeutic relief.

COMPLICATIONS:
None.

DISPOSITION:
Patient tolerated the procedure well and was discharged home.
"""

# ==========================================
# 3. Span Helper
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {
        "text": term,
        "start": start,
        "end": start + len(term),
    }

# ==========================================
# 4. Entity Annotations (Evidence-only)
# ==========================================
entities = [
    # Anatomy
    {"label": "ANAT_PLEURA", **get_span(RAW_TEXT, "left pleural effusion")},
    {"label": "ANAT_LUNG_LOC", **get_span(RAW_TEXT, "left posterior hemithorax")},
    {"label": "ANAT_INTERCOSTAL_SPACE", **get_span(RAW_TEXT, "8th intercostal space")},

    # Procedure
    {"label": "PROC_NAME", **get_span(RAW_TEXT, "thoracentesis")},
    {"label": "PROC_METHOD", **get_span(RAW_TEXT, "landmark technique")},

    # Devices / tools
    {"label": "DEV_NEEDLE", **get_span(RAW_TEXT, "18G catheter")},

    # Fluids / findings
    {"label": "OBS_FLUID_COLOR", **get_span(RAW_TEXT, "straw-colored fluid")},

    # Volumes
    {"label": "MEAS_VOLUME", **get_span(RAW_TEXT, "60 mL")},
    {"label": "MEAS_VOLUME", **get_span(RAW_TEXT, "900 mL")},

    # Outcomes
    {"label": "OBS_NO_COMPLICATION", **get_span(RAW_TEXT, "None")},
    {"label": "DISPOSITION", **get_span(RAW_TEXT, "discharged home")},
]

# ==========================================
# 5. Execution
# ==========================================
if __name__ == "__main__":
    add_case(
        note_id=NOTE_ID,
        raw_text=RAW_TEXT,
        entities=entities,
        repo_root=REPO_ROOT,
    )
