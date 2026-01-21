import sys
from pathlib import Path

# Set up the repository root directory to import the utility function
def get_repo_root():
    current_path = Path(__file__).resolve()
    for parent in [current_path] + list(current_path.parents):
        if (parent / ".git").exists() or (parent / "scripts").exists():
            return parent
    return current_path.parent

REPO_ROOT = get_repo_root()
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Raises ValueError if the term is not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
    
    if start == -1:
        raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text:\n{text[:100]}...")
        
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2498770_syn_1
# ==========================================
t1 = """Dx: Left pleural nodularity.
Proc: Dx Thoracoscopy.
- Mass lesion on diaphragm.
- Fluid evacuated.
- Chest tube placed.
- No biopsy in note."""
e1 = [
    {"label": "LATERALITY", **get_span(t1, "Left", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodularity", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Mass lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "diaphragm", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "placed", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2498770_syn_2
# ==========================================
t2 = """PROCEDURE: Left-sided diagnostic medical thoracoscopy. The instrument was introduced into the 6th intercostal space. Exploration of the hemithorax revealed a distinct mass lesion situated on the diaphragmatic pleura. The parietal and visceral surfaces were otherwise visualized. Effusion was cleared, and a chest tube was sited. The lung was fully expanded."""
e2 = [
    {"label": "LATERALITY", **get_span(t2, "Left-sided", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "6th intercostal space", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "diaphragmatic pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "visceral", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "visualized", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "Effusion", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "cleared", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "sited", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "lung", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t2, "fully expanded", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2498770_syn_3
# ==========================================
t3 = """Service: 32601 (Diagnostic Thoracoscopy).
Site: [REDACTED]
Findings: Diaphragmatic mass lesion.
Procedure: Visual inspection of all pleural surfaces. Drainage of residual fluid. Chest tube placement. No tissue sampling documented."""
e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "Diagnostic Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "Diaphragmatic", 1)},
    {"label": "OBS_LESION", **get_span(t3, "mass lesion", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Visual inspection", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "pleural surfaces", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Drainage", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "placement", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2498770_syn_4
# ==========================================
t4 = """Left Thoracoscopy
Indication: Nodules on CT.
Findings: Mass on diaphragm.
Steps: Entry 6th ICS -> Looked around -> Drained fluid -> Tube in.
No complications."""
e4 = [
    {"label": "LATERALITY", **get_span(t4, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Nodules", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Mass", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "diaphragm", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "6th ICS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Drained", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "Tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No complications", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2498770_syn_5
# ==========================================
t5 = """timothy scott left side. went in to look at the nodules. saw a big mass on the diaphragm. looked at the rest of the pleura. drained the fluid put the chest tube in. patient did fine."""
e5 = [
    {"label": "LATERALITY", **get_span(t5, "left side", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodules", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "ANAT_PLEURA", **get_span(t5, "diaphragm", 1)},
    {"label": "ANAT_PLEURA", **get_span(t5, "pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "drained", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2498770_syn_6
# ==========================================
t6 = """Medical Thoracoscopy (Pleuroscopy) - Diagnostic. Under moderate sedation, single-port entry at 6th intercostal space, mid-axillary line (Left). Semi-rigid pleuroscope inserted. Findings: Mass lesion on diaphragmatic pleura. Parietal, visceral, and diaphragmatic pleura visualized. All remaining fluid evacuated. Chest tube placed."""
e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Medical Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "mid-axillary line", 1)},
    {"label": "LATERALITY", **get_span(t6, "Left", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "pleuroscope", 1)},
    {"label": "OBS_LESION", **get_span(t6, "Mass lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "diaphragmatic pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "diaphragmatic pleura", 2)},
    {"label": "PROC_ACTION", **get_span(t6, "visualized", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "placed", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2498770_syn_7
# ==========================================
t7 = """[Indication]
Pleural nodularity.
[Anesthesia]
Moderate.
[Description]
Left entry. Findings: Mass lesion on diaphragm. Fluid evacuated. Chest tube to water seal.
[Plan]
Admit. Pull tube when <150mL."""
e7 = [
    {"label": "ANAT_PLEURA", **get_span(t7, "Pleural", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodularity", 1)},
    {"label": "LATERALITY", **get_span(t7, "Left", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Mass lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t7, "diaphragm", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2498770_syn_8
# ==========================================
t8 = """We performed a diagnostic thoracoscopy on the left side for [REDACTED]. The exam revealed a specific mass lesion located on the diaphragmatic pleura. We visualized the remaining pleural surfaces and evacuated the fluid. A chest tube was placed, and the lung was confirmed to be expanded."""
e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "diagnostic thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(t8, "left side", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "diaphragmatic pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "pleural surfaces", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "visualized", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "evacuated", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "placed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "lung", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t8, "expanded", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2498770_syn_9
# ==========================================
t9 = """Procedure: Exploratory Pleuroscopy.
Side: Left.
Discovery: Mass situated on the diaphragmatic surface.
Action: Cleared pleural effusion. Installed chest drain. Lung re-inflation confirmed."""
e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Pleuroscopy", 1)},
    {"label": "LATERALITY", **get_span(t9, "Left", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Mass", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "diaphragmatic surface", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "pleural effusion", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Cleared", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "chest drain", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Lung", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t9, "re-inflation", 1)},
]
BATCH_DATA.append({"id": "2498770_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2498770 (Main)
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Michael Chen
Fellow: Dr. James Liu (PGY-5)

Indication: Pleural nodularity on imaging
Side: Left

PROCEDURE: Medical Thoracoscopy (Pleuroscopy) - Diagnostic
Under moderate sedation with local anesthesia.
Single-port entry at 6th intercostal space, mid-axillary line.
Semi-rigid pleuroscope inserted.

FINDINGS: Mass lesion on diaphragmatic pleura
Parietal, visceral, and diaphragmatic pleura visualized.
All remaining fluid evacuated under direct visualization.
Chest tube placed. No air leak. Lung expanded.

DISPOSITION: Floor admission, chest tube to water seal.
F/U: Path results in 3-5 days. Tube removal when output <150mL/day.

Chen, MD"""
e10 = [
    {"label": "ANAT_PLEURA", **get_span(t10, "Pleural", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodularity", 1)},
    {"label": "LATERALITY", **get_span(t10, "Left", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Medical Thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "6th intercostal space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "mid-axillary line", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Semi-rigid pleuroscope", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Mass lesion", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "diaphragmatic pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "visceral", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "diaphragmatic pleura", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "visualized", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "evacuated", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "Chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "placed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lung", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t10, "expanded", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
]
BATCH_DATA.append({"id": "2498770", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)