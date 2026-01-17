import sys
from pathlib import Path

# Set up repository root (dynamic calculation)
# Assuming this script is run from a subdirectory or the root of the repo
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import the utility function from the scripts module
# Ensure 'scripts' folder and 'add_training_case.py' exist in REPO_ROOT
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Warning: Could not import 'add_case'. Ensure the script is run in the correct environment.")
    # Mocking add_case for standalone testing if import fails
    def add_case(case_id, text, entities, root):
        print(f"Processing {case_id} (Entities: {len(entities)})")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            # Fallback to prevent crash, though logic should ensure term exists
            return {"start": 0, "end": 0} 
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 4086330_syn_1
# ==========================================
t1 = """Indication: TB pleuritis suspicion.
Proc: Left Thoracoscopy + Biopsy.
- Findings: Inflammatory changes.
- 9 biopsies parietal pleura + diaphragm.
- Fluid evacuated. Chest tube in."""

e1 = [
    {"label": "LATERALITY", **get_span(t1, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "9", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 4086330_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: Left medical thoracoscopy for suspected tuberculous pleuritis. Access via 6th intercostal space. The pleura exhibited inflammatory changes without distinct nodularity. To ensure diagnostic yield, nine biopsies were obtained from the parietal pleura, along with diaphragmatic sampling. Fluid was evacuated and a chest tube inserted."""

e2 = [
    {"label": "LATERALITY", **get_span(t2, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleura", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "nine", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "sampling", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "inserted", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 4086330_syn_3
# ==========================================
t3 = """CPT: 32609 (Biopsy).
Side: Left.
Findings: Inflammatory.
Samples: 9 parietal biopsies.
Note: High biopsy count to r/o TB. No talc."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Biopsy", 1)},
    {"label": "LATERALITY", **get_span(t3, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "Inflammatory", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "9", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "parietal", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsies", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 4086330_syn_4
# ==========================================
t4 = """Left Thoracoscopy w/ Biopsy
Indication: ?TB
Findings: Inflamed pleura.
Action: 9 biopsies taken from parietal wall. Diaphragm sampled. Fluid out. Tube in."""

e4 = [
    {"label": "LATERALITY", **get_span(t4, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Inflamed", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "9", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "parietal wall", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "Diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "sampled", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "Tube", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 4086330_syn_5
# ==========================================
t5 = """donald flores left side. think its TB. went in saw inflammation. took a lot of biopsies 9 of them plus diaphragm just to be sure. put the tube in. no air leak."""

e5 = [
    {"label": "LATERALITY", **get_span(t5, "left", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "inflammation", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "9", 1)},
    {"label": "ANAT_PLEURA", **get_span(t5, "diaphragm", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "tube", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 4086330_syn_6
# ==========================================
t6 = """Medical Thoracoscopy with Pleural Biopsy. Indication: Suspected tuberculous pleuritis. Left side. Findings: Inflammatory changes without nodularity. Multiple biopsies obtained from parietal pleura (9 specimens). Additional biopsies from diaphragmatic pleura. All fluid evacuated. Chest tube placed."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "Pleural", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Biopsy", 1)},
    {"label": "LATERALITY", **get_span(t6, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "Inflammatory changes", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "9", 1)},
    {"label": "SPECIMEN", **get_span(t6, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(t6, "diaphragmatic pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "placed", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 4086330_syn_7
# ==========================================
t7 = """[Indication]
Suspected TB pleuritis.
[Anesthesia]
Moderate.
[Description]
Left side. Inflammatory changes. 9 parietal biopsies taken. Fluid drained. Chest tube in.
[Plan]
Admit. Await path."""

e7 = [
    {"label": "LATERALITY", **get_span(t7, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "9", 1)},
    {"label": "ANAT_PLEURA", **get_span(t7, "parietal", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 4086330_syn_8
# ==========================================
t8 = """We performed a left-sided thoracoscopy on Mr. [REDACTED] to check for TB. The pleura looked inflamed but didn't have nodules. We took nine biopsies from the chest wall and some from the diaphragm to send for analysis. We drained the fluid and left a chest tube in place."""

e8 = [
    {"label": "LATERALITY", **get_span(t8, "left", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "pleura", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "inflamed", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "nine", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "chest wall", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 4086330_syn_9
# ==========================================
t9 = """Procedure: Pleuroscopy with Multiple Biopsies.
Side: Left.
Findings: Pleuritis/inflammation.
Action: Acquired 9 parietal tissue samples. Evacuated fluid. Positioned thoracostomy tube."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Pleuroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Biopsies", 1)},
    {"label": "LATERALITY", **get_span(t9, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Pleuritis", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "inflammation", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "9", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "parietal", 1)},
    {"label": "SPECIMEN", **get_span(t9, "tissue samples", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "thoracostomy tube", 1)},
]
BATCH_DATA.append({"id": "4086330_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 4086330
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams

Indication: Suspected tuberculous pleuritis
Side: Left

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Inflammatory changes without nodularity
Multiple biopsies obtained from parietal pleura (9 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Williams, MD"""

e10 = [
    {"label": "LATERALITY", **get_span(t10, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Pleural", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "pleuroscope", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "inserted", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Inflammatory changes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "9", 1)},
    {"label": "SPECIMEN", **get_span(t10, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(t10, "diaphragmatic pleura", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placed", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 2)},
]
BATCH_DATA.append({"id": "4086330", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)