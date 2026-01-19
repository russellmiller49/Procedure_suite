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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 3992265_syn_1
# ==========================================
text_0 = """Proc: Rt Diagnostic Thoracoscopy.
Findings: Thickened parietal pleura, nodules.
Actions:
- Visual inspection.
- Fluid evacuated.
- Chest tube placed.
Status: Lung expanded. No leak."""
entities_0 = [
    {"label": "LATERALITY", **get_span(text_0, "Rt", 1)},
    {"label": "PROC_METHOD", **get_span(text_0, "Diagnostic Thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_0, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_0, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_0, "nodules", 1)},
    {"label": "SPECIMEN", **get_span(text_0, "Fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_0, "Chest tube", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_0, "Lung", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_1", "text": text_0, "entities": entities_0})

# ==========================================
# Note 2: 3992265_syn_2
# ==========================================
text_1 = """PROCEDURE NOTE: Right-sided diagnostic medical thoracoscopy was performed. Inspection revealed significant thickening of the parietal pleura studded with nodularity. The visceral and diaphragmatic surfaces were visualized. Fluid was completely evacuated under direct vision. A thoracostomy tube was placed to water seal. The lung was observed to re-expand."""
entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "Right-sided", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "medical thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "thickening", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodularity", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "diaphragmatic", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "thoracostomy tube", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lung", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_2", "text": text_1, "entities": entities_1})

# ==========================================
# Note 3: 3992265_syn_3
# ==========================================
text_2 = """Billing: 32601 (Diagnostic Thoracoscopy).
Rationale: Right pleural space inspected. Thickened pleura/nodules noted. Fluid drained. No biopsies performed or coded (included in diag if minor, but here focusing on diagnostic code). No pleurodesis. Chest tube placed."""
entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Diagnostic Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_2, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleura", 2)},
    {"label": "OBS_LESION", **get_span(text_2, "nodules", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "Fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "Chest tube", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_3", "text": text_2, "entities": entities_2})

# ==========================================
# Note 4: 3992265_syn_4
# ==========================================
text_3 = """Resident Note: Right Diagnostic Pleuroscopy
Steps:
1. Sedation.
2. Single port 6th ICS.
3. Exam: Thickened pleura with nodules.
4. Drainage: All fluid removed.
5. Closure: Chest tube placed.
Plan: Path review (if fluid sent)."""
entities_3 = [
    {"label": "LATERALITY", **get_span(text_3, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Diagnostic Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "6th ICS", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodules", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Chest tube", 1)},
    {"label": "SPECIMEN", **get_span(text_3, "fluid", 2)}
]
BATCH_DATA.append({"id": "3992265_syn_4", "text": text_3, "entities": entities_3})

# ==========================================
# Note 5: 3992265_syn_5
# ==========================================
text_4 = """diagnostic scope on the right side saw some thickened pleura and nodules didn't do biopsies just drained the fluid and put the tube in lung came up fine no air leak sending to floor"""
entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "diagnostic scope", 1)},
    {"label": "LATERALITY", **get_span(text_4, "right side", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "tube", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "lung", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_5", "text": text_4, "entities": entities_4})

# ==========================================
# Note 6: 3992265_syn_6
# ==========================================
text_5 = """A right diagnostic medical thoracoscopy was performed. The parietal pleura appeared thickened with multiple nodules. The visceral and diaphragmatic pleura were also visualized. Remaining pleural fluid was evacuated. A chest tube was inserted, and the lung expanded well. No air leak was noted."""
entities_5 = [
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "parietal pleura", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "thickened", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "pleura", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "pleura", 3)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lung", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_6", "text": text_5, "entities": entities_5})

# ==========================================
# Note 7: 3992265_syn_7
# ==========================================
text_6 = """[Indication] Pleural nodularity.
[Anesthesia] Moderate.
[Description] Right diagnostic thoracoscopy. Findings: Thickened parietal pleura with nodules. Interventions: Fluid evacuation. Chest tube placement.
[Plan] Monitor drainage."""
entities_6 = [
    {"label": "ANAT_PLEURA", **get_span(text_6, "Pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodularity", 1)},
    {"label": "LATERALITY", **get_span(text_6, "Right", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "Fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Chest tube", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_7", "text": text_6, "entities": entities_6})

# ==========================================
# Note 8: 3992265_syn_8
# ==========================================
text_7 = """[REDACTED] a right diagnostic medical thoracoscopy. Upon inspection, we noted thickened parietal pleura with nodules. We visualized the visceral and diaphragmatic surfaces as well. We evacuated all remaining fluid under direct visualization and placed a chest tube. The lung expanded appropriately."""
entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "right", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "medical thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "diaphragmatic", 1)},
    {"label": "SPECIMEN", **get_span(text_7, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "chest tube", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "lung", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_8", "text": text_7, "entities": entities_7})

# ==========================================
# Note 9: 3992265_syn_9
# ==========================================
text_8 = """Right diagnostic pleuroscopy executed. Observed thickened parietal membrane with nodules. Effusion drained. Catheter deployed. Lung re-expansion confirmed."""
entities_8 = [
    {"label": "LATERALITY", **get_span(text_8, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "diagnostic pleuroscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal membrane", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "Effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "Catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "Lung", 1)}
]
BATCH_DATA.append({"id": "3992265_syn_9", "text": text_8, "entities": entities_8})

# ==========================================
# Note 10: 3992265
# ==========================================
text_9 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. James Rodriguez

Indication: Pleural nodularity on imaging
Side: Right

PROCEDURE: Medical Thoracoscopy (Pleuroscopy) - Diagnostic
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted.

FINDINGS: Thickened parietal pleura with nodules
Parietal, visceral, and diaphragmatic pleura visualized.
All remaining fluid evacuated under direct visualization.
Chest tube placed. No air leak. Lung expanded.

DISPOSITION: Floor admission, chest tube to water seal.
F/U: Path results in 3-5 days. Tube removal when output <150mL/day.

Rodriguez, MD"""
entities_9 = [
    {"label": "ANAT_PLEURA", **get_span(text_9, "Pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodularity", 1)},
    {"label": "LATERALITY", **get_span(text_9, "Right", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Medical Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Semi-rigid pleuroscope", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "pleura", 2)},
    {"label": "SPECIMEN", **get_span(text_9, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Chest tube", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Lung", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "chest tube", 1)}
]
BATCH_DATA.append({"id": "3992265", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)