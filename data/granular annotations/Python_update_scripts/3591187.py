import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 3591187_syn_1
# ==========================================
t1 = """Indication: Recurrent effusion.
Proc: Left Diagnostic Thoracoscopy.
- Nodules found (malignant appearance).
- Fluid drained.
- Chest tube placed.
- No biopsy recorded in this note."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "effusion", 1)},
    {"label": "LATERALITY", **get_span(t1, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Nodules", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "malignant appearance", 1)},
    {"label": "SPECIMEN", **get_span(t1, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsy", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 3591187_syn_2
# ==========================================
t2 = """OPERATIVE NOTE: The patient underwent a diagnostic medical thoracoscopy on the left side for recurrent effusion of unknown etiology. The pleural space was entered via the 6th intercostal space. Visualization revealed multiple pleural nodules with a malignant macroscopic appearance. The remaining pleural fluid was evacuated. A chest tube was positioned, confirming lung re-expansion and absence of air leak."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(t2, "left", 1)},
    {"label": "OBS_LESION", **get_span(t2, "effusion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural", 2)},
    {"label": "OBS_LESION", **get_span(t2, "nodules", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "malignant macroscopic appearance", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural", 3)},
    {"label": "SPECIMEN", **get_span(t2, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t2, "lung re-expansion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "absence of air leak", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 3591187_syn_3
# ==========================================
t3 = """Code: 32601 (Diagnostic Thoracoscopy).
Side: Left.
Findings: Multiple malignant-appearing nodules.
Work: Visualization of parietal/visceral/diaphragmatic pleura. Evacuation of fluid. Placement of tube. (Note: Biopsy 32609 not documented in this specific text, coding strictly to documentation)."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(t3, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "malignant-appearing", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "diaphragmatic pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Evacuation", 1)},
    {"label": "SPECIMEN", **get_span(t3, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "tube", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Biopsy", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 3591187_syn_4
# ==========================================
t4 = """Procedure: Left Pleuroscopy (Diagnostic)
Pt: [REDACTED], 54F
1. Port 6th ICS.
2. Saw multiple nodules (look bad).
3. Drained fluid.
4. Chest tube placed.
Plan: Admit, wait for path/cytology."""

e4 = [
    {"label": "LATERALITY", **get_span(t4, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "6th ICS", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Drained", 1)},
    {"label": "SPECIMEN", **get_span(t4, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 3591187_syn_5
# ==========================================
t5 = """[REDACTED] left side scope. looking for why the effusion keeps coming back. went in saw a bunch of nodules they look malignant. drained the fluid put a tube in. no air leak. sending to floor."""

e5 = [
    {"label": "LATERALITY", **get_span(t5, "left", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "scope", 1)},
    {"label": "OBS_LESION", **get_span(t5, "effusion", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodules", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "malignant", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "drained", 1)},
    {"label": "SPECIMEN", **get_span(t5, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no air leak", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 3591187_syn_6
# ==========================================
t6 = """Medical Thoracoscopy (Pleuroscopy) - Diagnostic. Single-port entry at 6th intercostal space, mid-axillary line on the Left. Findings: Multiple pleural nodules - malignant appearing. Parietal, visceral, and diaphragmatic pleura visualized. All remaining fluid evacuated. Chest tube placed. No air leak. Lung expanded."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "6th intercostal space", 1)},
    {"label": "LATERALITY", **get_span(t6, "Left", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodules", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "malignant appearing", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "diaphragmatic pleura", 1)},
    {"label": "SPECIMEN", **get_span(t6, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "Chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No air leak", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t6, "Lung expanded", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 3591187_syn_7
# ==========================================
t7 = """[Indication]
Recurrent pleural effusion, unknown etiology.
[Anesthesia]
Moderate.
[Description]
Left side. Multiple malignant-appearing nodules visualized. Fluid evacuated. Chest tube placed.
[Plan]
Admit. Tube to water seal."""

e7 = [
    {"label": "ANAT_PLEURA", **get_span(t7, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(t7, "effusion", 1)},
    {"label": "LATERALITY", **get_span(t7, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "malignant-appearing", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodules", 1)},
    {"label": "SPECIMEN", **get_span(t7, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "Chest tube", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "Tube", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 3591187_syn_8
# ==========================================
t8 = """[REDACTED] a diagnostic thoracoscopy on the left side to investigate her recurrent effusion. Upon inspection, we id[REDACTED] multiple nodules that appeared malignant. We ensured all fluid was removed and placed a chest tube. The lung expanded fully, and there was no evidence of an air leak."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(t8, "left", 1)},
    {"label": "OBS_LESION", **get_span(t8, "effusion", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodules", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "malignant", 1)},
    {"label": "SPECIMEN", **get_span(t8, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "removed", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t8, "lung expanded fully", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "no evidence of an air leak", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 3591187_syn_9
# ==========================================
t9 = """Procedure: Diagnostic Pleuroscopy.
Side: Left.
Visualization: Numerous nodules with malignant features.
Task: Evacuated pleural fluid. Inserted intercostal drain. Verified lung inflation."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Pleuroscopy", 1)},
    {"label": "LATERALITY", **get_span(t9, "Left", 1)},
    {"label": "OBS_LESION", **get_span(t9, "nodules", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "malignant features", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Evacuated", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "pleural", 1)},
    {"label": "SPECIMEN", **get_span(t9, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "intercostal drain", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t9, "lung inflation", 1)},
]
BATCH_DATA.append({"id": "3591187_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 3591187
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Mark Taylor

Indication: Recurrent pleural effusion of unknown etiology
Side: Left

PROCEDURE: Medical Thoracoscopy (Pleuroscopy) - Diagnostic
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted.

FINDINGS: Multiple pleural nodules - malignant appearing
Parietal, visceral, and diaphragmatic pleura visualized.
All remaining fluid evacuated under direct visualization.
Chest tube placed. No air leak. Lung expanded.

DISPOSITION: Floor admission, chest tube to water seal.
F/U: Path results in 3-5 days. Tube removal when output <150mL/day.

Taylor, MD"""

e10 = [
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(t10, "effusion", 1)},
    {"label": "LATERALITY", **get_span(t10, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "6th intercostal space", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "pleuroscope", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural", 2)},
    {"label": "OBS_LESION", **get_span(t10, "nodules", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "malignant appearing", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "diaphragmatic pleura", 1)},
    {"label": "SPECIMEN", **get_span(t10, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No air leak", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t10, "Lung expanded", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
]
BATCH_DATA.append({"id": "3591187", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)