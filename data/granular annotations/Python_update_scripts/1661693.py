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
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case 1: 1661693_syn_1
# ------------------------------------------
text_1 = """Proc: Lt Thoracoscopy w/ Biopsy.
Findings: Inflammatory changes.
Actions:
- 12 biopsies parietal pleura.
- Diaphragmatic biopsies.
- Fluid evacuated.
- Tube placed.
- No talc.
Status: No leak."""

entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "Lt", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 2)},
    {"label": "SPECIMEN", **get_span(text_1, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No leak", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_1", "text": text_1, "entities": entities_1})

# ------------------------------------------
# Case 2: 1661693_syn_2
# ------------------------------------------
text_2 = """OPERATIVE REPORT: Left medical thoracoscopy was performed for suspected malignancy. Inflammatory changes were noted without distinct nodularity. Twelve biopsies were harvested from the parietal pleura, with additional diaphragmatic sampling. Fluid was evacuated. No pleurodesis was performed. A chest tube was placed."""

entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "medical thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignancy", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "sampling", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "placed", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_2", "text": text_2, "entities": entities_2})

# ------------------------------------------
# Case 3: 1661693_syn_3
# ------------------------------------------
text_3 = """Code: 32609 (Biopsy).
Site: [REDACTED]
Tech: 12 parietal biopsies obtained. Diaphragm sampled. No talc used. Chest tube inserted."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "parietal", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "Diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "sampled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "inserted", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_3", "text": text_3, "entities": entities_3})

# ------------------------------------------
# Case 4: 1661693_syn_4
# ------------------------------------------
text_4 = """Procedure: Left Thoracoscopy
Steps:
1. Sedation.
2. Scope inserted left 6th ICS.
3. Findings: Inflammation.
4. Biopsies: 12 parietal + diaphragm.
5. Fluid drained.
6. Chest tube placed.
Plan: Path review."""

entities_4 = [
    {"label": "LATERALITY", **get_span(text_4, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Thoracoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "inserted", 1)},
    {"label": "LATERALITY", **get_span(text_4, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "6th ICS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Inflammation", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "diaphragm", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "placed", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_4", "text": text_4, "entities": entities_4})

# ------------------------------------------
# Case 5: 1661693_syn_5
# ------------------------------------------
text_5 = """left thoracoscopy for william inflammation seen no nodules took 12 biopsies from the wall and some from diaphragm drained fluid chest tube in no talc"""

entities_5 = [
    {"label": "LATERALITY", **get_span(text_5, "left", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "inflammation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "wall", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drained", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_5", "text": text_5, "entities": entities_5})

# ------------------------------------------
# Case 6: 1661693_syn_6
# ------------------------------------------
text_6 = """Left medical thoracoscopy was performed. Inflammatory changes were noted without nodularity. Twelve biopsies were obtained from the parietal pleura, along with diaphragmatic biopsies. Fluid was evacuated and a chest tube was placed."""

entities_6 = [
    {"label": "LATERALITY", **get_span(text_6, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "medical thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 2)},
    {"label": "SPECIMEN", **get_span(text_6, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "placed", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_6", "text": text_6, "entities": entities_6})

# ------------------------------------------
# Case 7: 1661693_syn_7
# ------------------------------------------
text_7 = """[Indication] Biopsy-negative malignancy.
[Anesthesia] Moderate.
[Description] Left thoracoscopy. Inflammatory changes. 12 parietal biopsies. Diaphragmatic biopsies. Fluid drained. Chest tube placed.
[Plan] Path results."""

entities_7 = [
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "malignancy", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "parietal", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "Diaphragmatic", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 2)},
    {"label": "SPECIMEN", **get_span(text_7, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "placed", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_7", "text": text_7, "entities": entities_7})

# ------------------------------------------
# Case 8: 1661693_syn_8
# ------------------------------------------
text_8 = """We performed a left medical thoracoscopy on [REDACTED]. The pleura showed inflammatory changes. We collected twelve biopsies from the parietal pleura and additional samples from the diaphragm. We evacuated the fluid and placed a chest tube. No pleurodesis was done."""

entities_8 = [
    {"label": "LATERALITY", **get_span(text_8, "left", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleura", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "inflammatory changes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal pleura", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "evacuated", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "placed", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_8", "text": text_8, "entities": entities_8})

# ------------------------------------------
# Case 9: 1661693_syn_9
# ------------------------------------------
text_9 = """Left pleuroscopy performed. Inflammatory alterations observed. Twelve tissue samples harvested from parietal pleura; diaphragm also sampled. Effusion drained. Catheter deployed."""

entities_9 = [
    {"label": "LATERALITY", **get_span(text_9, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "pleuroscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Inflammatory alterations", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "Twelve", 1)},
    {"label": "SPECIMEN", **get_span(text_9, "tissue samples", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampled", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "deployed", 1)},
]
BATCH_DATA.append({"id": "1661693_syn_9", "text": text_9, "entities": entities_9})

# ------------------------------------------
# Case 10: 1661693
# ------------------------------------------
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: 7/22/1967
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams
Fellow: Dr. Kevin Patel (PGY-5)

Indication: Biopsy-negative suspected malignancy
Side: Left

PROCEDURE: Medical Thoracoscopy with Pleural Biopsy
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted. Pleural space inspected.

FINDINGS: Inflammatory changes without nodularity
Multiple biopsies obtained from parietal pleura (12 specimens).
Additional biopsies from diaphragmatic pleura.
Specimens sent for histopathology and immunohistochemistry.
All fluid evacuated. Chest tube placed.
Hemostasis confirmed. No air leak.

DISPOSITION: Floor admission. Chest tube to suction.
F/U: Path results in 5-7 days. Oncology consultation if malignant.

Williams, MD"""

entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "Biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "malignancy", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Biopsy", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "pleuroscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "inserted", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Inflammatory changes", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "12", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "diaphragmatic pleura", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Specimens", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "placed", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 2)},
]
BATCH_DATA.append({"id": "1661693", "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")