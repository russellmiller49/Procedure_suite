import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
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

# ==========================================
# 3. Data Definitions (Batch)
# ==========================================
BATCH_DATA = []

# --- Note 1: 4193717_syn_1 ---
id_1 = "4193717_syn_1"
text_1 = """Indication: Mesothelioma suspicion.
Proc: Dx Thoracoscopy (Right).
- Diffuse nodularity seen.
- Fluid removed.
- No biopsy mentioned in this specific note text (Diagnostic code only).
- Chest tube in.
Plan: Admit."""
entities_1 = [
    {"label": "OBS_LESION",       **get_span(text_1, "Mesothelioma", 1)},
    {"label": "PROC_ACTION",      **get_span(text_1, "Thoracoscopy", 1)},
    {"label": "LATERALITY",       **get_span(text_1, "Right", 1)},
    {"label": "OBS_FINDING",      **get_span(text_1, "nodularity", 1)},
    {"label": "OBS_FINDING",      **get_span(text_1, "Fluid", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# --- Note 2: 4193717_syn_2 ---
id_2 = "4193717_syn_2"
text_2 = """OPERATIVE REPORT: The patient presented for diagnostic evaluation of the right pleural space due to suspected mesothelioma. Following access at the 6th intercostal space, the pleuroscope was introduced. The inspection demonstrated diffuse pleural nodularity involving the parietal, visceral, and diaphragmatic surfaces. The pleural effusion was completely evacuated under direct visualization. A thoracostomy tube was placed. The lung expanded appropriately without air leak."""
entities_2 = [
    {"label": "LATERALITY",       **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_2, "pleural space", 1)},
    {"label": "OBS_LESION",       **get_span(text_2, "mesothelioma", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_2, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_2, "pleuroscope", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_2, "pleural", 1)},
    {"label": "OBS_FINDING",      **get_span(text_2, "nodularity", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_2, "parietal", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_2, "visceral", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_2, "diaphragmatic", 1)},
    {"label": "OBS_FINDING",      **get_span(text_2, "pleural effusion", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_2, "thoracostomy tube", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_2, "lung expanded", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "without air leak", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# --- Note 3: 4193717_syn_3 ---
id_3 = "4193717_syn_3"
text_3 = """Billing Code: 32601 (Thoracoscopy, diagnostic).
Location: [REDACTED]
Details: Visualization of parietal, visceral, and diaphragmatic pleura. Findings included diffuse pleural nodularity. Complete fluid evacuation performed. No biopsies recorded in this specific encounter note (Pathology pending from fluid/prior)."""
entities_3 = [
    {"label": "PROC_ACTION",      **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_3, "parietal", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_3, "visceral", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_3, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_3, "pleura", 1)},
    {"label": "OBS_FINDING",      **get_span(text_3, "pleural nodularity", 1)},
    {"label": "OBS_FINDING",      **get_span(text_3, "fluid", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# --- Note 4: 4193717_syn_4 ---
id_4 = "4193717_syn_4"
text_4 = """Resident Note: Right Medical Thoracoscopy (Diagnostic)
Indication: R/O Mesothelioma
1. Prep/Drape.
2. Entry 6th ICS mid-axillary.
3. Findings: Diffuse nodules.
4. Suctioned fluid.
5. Placed chest tube.
No complications. Lung up."""
entities_4 = [
    {"label": "LATERALITY",       **get_span(text_4, "Right", 1)},
    {"label": "PROC_ACTION",      **get_span(text_4, "Medical Thoracoscopy", 1)},
    {"label": "OBS_LESION",       **get_span(text_4, "Mesothelioma", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_4, "6th ICS", 1)},
    {"label": "OBS_LESION",       **get_span(text_4, "nodules", 1)},
    {"label": "OBS_FINDING",      **get_span(text_4, "fluid", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_4, "chest tube", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_4, "Lung up", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No complications", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# --- Note 5: 4193717_syn_5 ---
id_5 = "4193717_syn_5"
text_5 = """procedure on mr [REDACTED] right side thoracoscopy just diagnostic today. saw a lot of nodules diffuse all over the pleura. sucked out the rest of the fluid. put the tube in 6th intercostal space. lung came up fine no air leak. plan to keep him on the floor until drainage slows down."""
entities_5 = [
    {"label": "LATERALITY",       **get_span(text_5, "right", 1)},
    {"label": "PROC_ACTION",      **get_span(text_5, "thoracoscopy", 1)},
    {"label": "OBS_LESION",       **get_span(text_5, "nodules", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_5, "pleura", 1)},
    {"label": "OBS_FINDING",      **get_span(text_5, "fluid", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_5, "tube", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_5, "6th intercostal space", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_5, "lung came up", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "no air leak", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# --- Note 6: 4193717_syn_6 ---
id_6 = "4193717_syn_6"
text_6 = """Medical Thoracoscopy (Pleuroscopy) - Diagnostic. Under moderate sedation with local anesthesia, entry was achieved at the 6th intercostal space, mid-axillary line. The semi-rigid pleuroscope was inserted. Findings included diffuse pleural nodularity. Parietal, visceral, and diaphragmatic pleura were visualized. All remaining fluid was evacuated under direct visualization. A chest tube was placed. There was no air leak and the lung expanded."""
entities_6 = [
    {"label": "PROC_ACTION",      **get_span(text_6, "Medical Thoracoscopy", 1)},
    {"label": "PROC_METHOD",      **get_span(text_6, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_6, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_6, "semi-rigid pleuroscope", 1)},
    {"label": "OBS_FINDING",      **get_span(text_6, "pleural nodularity", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_6, "Parietal", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_6, "visceral", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_6, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_6, "pleura", 1)},
    {"label": "OBS_FINDING",      **get_span(text_6, "fluid", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_6, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no air leak", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_6, "lung expanded", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# --- Note 7: 4193717_syn_7 ---
id_7 = "4193717_syn_7"
text_7 = """[Indication]
Suspected mesothelioma.
[Anesthesia]
Moderate sedation.
[Description]
Right side accessed (6th ICS). Visualized diffuse pleural nodularity across parietal/visceral surfaces. Fluid evacuated. Chest tube placed.
[Plan]
Floor admission. Path f/u."""
entities_7 = [
    {"label": "OBS_LESION",       **get_span(text_7, "mesothelioma", 1)},
    {"label": "LATERALITY",       **get_span(text_7, "Right", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_7, "6th ICS", 1)},
    {"label": "OBS_FINDING",      **get_span(text_7, "pleural nodularity", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_7, "parietal", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_7, "visceral", 1)},
    {"label": "OBS_FINDING",      **get_span(text_7, "Fluid", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# --- Note 8: 4193717_syn_8 ---
id_8 = "4193717_syn_8"
text_8 = """We performed a diagnostic thoracoscopy on the right side to investigate suspected mesothelioma. Upon inspection via the sixth intercostal space, we noted diffuse nodularity throughout the pleural cavity. We ensured all remaining fluid was suctioned out under direct vision. The procedure was concluded by placing a chest tube; the lung was fully expanded with no evidence of an air leak."""
entities_8 = [
    {"label": "PROC_ACTION",      **get_span(text_8, "thoracoscopy", 1)},
    {"label": "LATERALITY",       **get_span(text_8, "right", 1)},
    {"label": "OBS_LESION",       **get_span(text_8, "mesothelioma", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_8, "sixth intercostal space", 1)},
    {"label": "OBS_FINDING",      **get_span(text_8, "nodularity", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_8, "pleural cavity", 1)},
    {"label": "OBS_FINDING",      **get_span(text_8, "fluid", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_8, "chest tube", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_8, "lung was fully expanded", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "no evidence of an air leak", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# --- Note 9: 4193717_syn_9 ---
id_9 = "4193717_syn_9"
text_9 = """Procedure: Diagnostic Pleuroscopy.
Side: Right.
Observations: Widespread pleural nodularity.
Execution: Visualized parietal, visceral, and diaphragmatic surfaces. Extracted remaining effusion. Inserted thoracostomy drain. Confirmed lung re-expansion."""
entities_9 = [
    {"label": "PROC_ACTION",      **get_span(text_9, "Pleuroscopy", 1)},
    {"label": "LATERALITY",       **get_span(text_9, "Right", 1)},
    {"label": "OBS_FINDING",      **get_span(text_9, "pleural nodularity", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_9, "parietal", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_9, "visceral", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_9, "diaphragmatic", 1)},
    {"label": "OBS_FINDING",      **get_span(text_9, "effusion", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_9, "thoracostomy drain", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_9, "lung re-expansion", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# --- Note 10: 4193717 (Main) ---
id_10 = "4193717"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Robert Martinez

Indication: Suspected mesothelioma
Side: Right

PROCEDURE: Medical Thoracoscopy (Pleuroscopy) - Diagnostic
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted.

FINDINGS: Diffuse pleural nodularity
Parietal, visceral, and diaphragmatic pleura visualized.
All remaining fluid evacuated under direct visualization.
Chest tube placed. No air leak. Lung expanded.

DISPOSITION: Floor admission, chest tube to water seal.
F/U: Path results in 3-5 days. Tube removal when output <150mL/day.

Martinez, MD"""
entities_10 = [
    {"label": "OBS_LESION",       **get_span(text_10, "mesothelioma", 1)},
    {"label": "LATERALITY",       **get_span(text_10, "Right", 1)},
    {"label": "PROC_ACTION",      **get_span(text_10, "Medical Thoracoscopy", 1)},
    {"label": "PROC_METHOD",      **get_span(text_10, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_10, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_10, "Semi-rigid pleuroscope", 1)},
    {"label": "OBS_FINDING",      **get_span(text_10, "pleural nodularity", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_10, "Parietal", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_10, "visceral", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_10, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA",      **get_span(text_10, "pleura", 1)},
    {"label": "OBS_FINDING",      **get_span(text_10, "fluid", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_10, "Chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No air leak", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(text_10, "Lung expanded", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)