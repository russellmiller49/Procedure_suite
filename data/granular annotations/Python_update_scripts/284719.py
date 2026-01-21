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
# 2. Helper Functions
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text: {text[:50]}...")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# 3. Data Definitions
# ==========================================

# ------------------------------------------
# Case 1: 284719_syn_1
# ------------------------------------------
t1 = """Indication: Chronic cough, RML narrowing.
Findings: RML orifice thickened, 5mm stenosis.
Action: 4 biopsies taken.
Dx: R/O carcinoid vs inflammation.
Plan: Path review."""
e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 1)},
    {"label": "OBS_FINDING",   **get_span(t1, "narrowing", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 2)},
    {"label": "OBS_FINDING",   **get_span(t1, "thickened", 1)},
    {"label": "MEAS_SIZE",     **get_span(t1, "5mm", 1)},
    {"label": "OBS_FINDING",   **get_span(t1, "stenosis", 1)},
    {"label": "MEAS_COUNT",    **get_span(t1, "4", 1)},
    {"label": "PROC_ACTION",   **get_span(t1, "biopsies", 1)},
    {"label": "OBS_LESION",    **get_span(t1, "carcinoid", 1)},
    {"label": "OBS_FINDING",   **get_span(t1, "inflammation", 1)},
]
BATCH_DATA.append({"id": "284719_syn_1", "text": t1, "entities": e1})

# ------------------------------------------
# Case 2: 284719_syn_2
# ------------------------------------------
t2 = """PROCEDURE: Diagnostic bronchoscopy. The RML orifice demonstrated significant circumferential mucosal thickening and edema, resulting in stenosis to approximately 5mm. No discrete mass was evident. Four biopsy specimens were obtained to differentiate between inflammatory stricture and neoplastic process (e.g., carcinoid)."""
e2 = [
    {"label": "PROC_METHOD",   **get_span(t2, "Diagnostic bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RML", 1)},
    {"label": "OBS_FINDING",   **get_span(t2, "mucosal thickening", 1)},
    {"label": "OBS_FINDING",   **get_span(t2, "edema", 1)},
    {"label": "OBS_FINDING",   **get_span(t2, "stenosis", 1)},
    {"label": "MEAS_SIZE",     **get_span(t2, "5mm", 1)},
    {"label": "OBS_LESION",    **get_span(t2, "mass", 1)},
    {"label": "MEAS_COUNT",    **get_span(t2, "Four", 1)},
    {"label": "PROC_ACTION",   **get_span(t2, "biopsy", 1)},
    {"label": "OBS_FINDING",   **get_span(t2, "inflammatory stricture", 1)},
    {"label": "OBS_LESION",    **get_span(t2, "neoplastic process", 1)},
    {"label": "OBS_LESION",    **get_span(t2, "carcinoid", 1)},
]
BATCH_DATA.append({"id": "284719_syn_2", "text": t2, "entities": e2})

# ------------------------------------------
# Case 3: 284719_syn_3
# ------------------------------------------
t3 = """Billing: 31625 (Biopsy of RML orifice). Medical necessity supported by radiographic finding of bronchial narrowing and symptoms of cough."""
e3 = [
    {"label": "PROC_ACTION",   **get_span(t3, "Biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RML", 1)},
    {"label": "OBS_FINDING",   **get_span(t3, "narrowing", 1)},
]
BATCH_DATA.append({"id": "284719_syn_3", "text": t3, "entities": e3})

# ------------------------------------------
# Case 4: 284719_syn_4
# ------------------------------------------
t4 = """Resident Note
Pt: M. Garcia
1. Scope to RML.
2. Narrowing seen (5mm), red/swollen.
3. Biopsied x4.
4. No bleeding.
5. Patient stable."""
e4 = [
    {"label": "PROC_METHOD",          **get_span(t4, "Scope", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(t4, "RML", 1)},
    {"label": "OBS_FINDING",          **get_span(t4, "Narrowing", 1)},
    {"label": "MEAS_SIZE",            **get_span(t4, "5mm", 1)},
    {"label": "OBS_FINDING",          **get_span(t4, "red", 1)},
    {"label": "OBS_FINDING",          **get_span(t4, "swollen", 1)},
    {"label": "PROC_ACTION",          **get_span(t4, "Biopsied", 1)},
    {"label": "MEAS_COUNT",           **get_span(t4, "4", 1)}, # Corrected: '4' in 'x4' is the 1st occurrence in t4.
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No bleeding", 1)},
]
BATCH_DATA.append({"id": "284719_syn_4", "text": t4, "entities": e4})

# ------------------------------------------
# Case 5: 284719_syn_5
# ------------------------------------------
t5 = """maria garcia cough rml narrowing on ct went in and rml opening is tight red swollen took 4 biopsies to see what it is maybe carcinoid or just inflammation bleeding was scant patient went home."""
e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rml", 1)},
    {"label": "OBS_FINDING",   **get_span(t5, "narrowing", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rml", 2)},
    {"label": "OBS_FINDING",   **get_span(t5, "tight", 1)},
    {"label": "OBS_FINDING",   **get_span(t5, "red", 1)},
    {"label": "OBS_FINDING",   **get_span(t5, "swollen", 1)},
    {"label": "MEAS_COUNT",    **get_span(t5, "4", 1)},
    {"label": "PROC_ACTION",   **get_span(t5, "biopsies", 1)},
    {"label": "OBS_LESION",    **get_span(t5, "carcinoid", 1)},
    {"label": "OBS_FINDING",   **get_span(t5, "inflammation", 1)},
]
BATCH_DATA.append({"id": "284719_syn_5", "text": t5, "entities": e5})

# ------------------------------------------
# Case 6: 284719_syn_6
# ------------------------------------------
t6 = """Moderate sedation was utilized. The RML orifice showed circumferential thickening and narrowing to 5mm. Four biopsies were obtained from the erythematous mucosa. The appearance was concerning for carcinoid or inflammatory stricture. No complications occurred."""
e6 = [
    {"label": "ANAT_LUNG_LOC",        **get_span(t6, "RML", 1)},
    {"label": "OBS_FINDING",          **get_span(t6, "thickening", 1)},
    {"label": "OBS_FINDING",          **get_span(t6, "narrowing", 1)},
    {"label": "MEAS_SIZE",            **get_span(t6, "5mm", 1)},
    {"label": "MEAS_COUNT",           **get_span(t6, "Four", 1)},
    {"label": "PROC_ACTION",          **get_span(t6, "biopsies", 1)},
    {"label": "OBS_FINDING",          **get_span(t6, "erythematous", 1)},
    {"label": "OBS_LESION",           **get_span(t6, "carcinoid", 1)},
    {"label": "OBS_FINDING",          **get_span(t6, "inflammatory stricture", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)},
]
BATCH_DATA.append({"id": "284719_syn_6", "text": t6, "entities": e6})

# ------------------------------------------
# Case 7: 284719_syn_7
# ------------------------------------------
t7 = """[Indication]
Chronic cough, RML stenosis.
[Anesthesia]
Moderate.
[Description]
RML orifice narrowed/thickened. 4 Biopsies taken. No complications.
[Plan]
Pathology follow-up."""
e7 = [
    {"label": "ANAT_LUNG_LOC",        **get_span(t7, "RML", 1)},
    {"label": "OBS_FINDING",          **get_span(t7, "stenosis", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(t7, "RML", 2)},
    {"label": "OBS_FINDING",          **get_span(t7, "narrowed", 1)},
    {"label": "OBS_FINDING",          **get_span(t7, "thickened", 1)},
    {"label": "MEAS_COUNT",           **get_span(t7, "4", 1)},
    {"label": "PROC_ACTION",          **get_span(t7, "Biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "No complications", 1)},
]
BATCH_DATA.append({"id": "284719_syn_7", "text": t7, "entities": e7})

# ------------------------------------------
# Case 8: 284719_syn_8
# ------------------------------------------
t8 = """[REDACTED] for a cough and narrowing of her airway seen on CT. We found the opening to the right middle lobe was swollen and narrowed. We took four biopsies to figure out if it's inflammation or a tumor. There was barely any bleeding, and she went home safely."""
e8 = [
    {"label": "OBS_FINDING",   **get_span(t8, "narrowing", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right middle lobe", 1)},
    {"label": "OBS_FINDING",   **get_span(t8, "swollen", 1)},
    {"label": "OBS_FINDING",   **get_span(t8, "narrowed", 1)},
    {"label": "MEAS_COUNT",    **get_span(t8, "four", 1)},
    {"label": "PROC_ACTION",   **get_span(t8, "biopsies", 1)},
    {"label": "OBS_FINDING",   **get_span(t8, "inflammation", 1)},
    {"label": "OBS_LESION",    **get_span(t8, "tumor", 1)},
]
BATCH_DATA.append({"id": "284719_syn_8", "text": t8, "entities": e8})

# ------------------------------------------
# Case 9: 284719_syn_9
# ------------------------------------------
t9 = """Investigation of bronchial stenosis. Visualized RML narrowing with mucosal edema. Sampled 4 sites circumferentially. Minimal hemorrhage. Monitoring for pathology."""
e9 = [
    {"label": "OBS_FINDING", **get_span(t9, "stenosis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RML", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "narrowing", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "mucosal edema", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Sampled", 1)},
    {"label": "MEAS_COUNT",  **get_span(t9, "4", 1)},
]
BATCH_DATA.append({"id": "284719_syn_9", "text": t9, "entities": e9})

# ------------------------------------------
# Case 10: 284719 (Original)
# ------------------------------------------
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Thomas Green, Fellow: Dr. Amy Zhao (PGY-5)

Dx: Chronic cough, CT shows RML bronchial narrowing with thickening
Procedure: Bronchoscopy with endobronchial biopsy

Moderate sedation. Flexible bronchoscopy. RML orifice shows circumferential mucosal thickening with narrowing to ~5mm. No exophytic mass. Mucosa appears edematous and erythematous. 4 biopsies obtained circumferentially. Appearance concerning for possible carcinoid or inflammatory stricture. Airways otherwise unremarkable. No complications.

D/C with return precautions. Path f/u next week.

T. Green, MD / A. Zhao, MD"""
e10 = [
    {"label": "ANAT_LUNG_LOC",        **get_span(t10, "RML", 1)},
    {"label": "OBS_FINDING",          **get_span(t10, "narrowing", 1)},
    {"label": "OBS_FINDING",          **get_span(t10, "thickening", 1)},
    {"label": "PROC_METHOD",          **get_span(t10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION",          **get_span(t10, "biopsy", 1)},
    {"label": "PROC_METHOD",          **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC",        **get_span(t10, "RML", 2)},
    {"label": "OBS_FINDING",          **get_span(t10, "circumferential mucosal thickening", 1)},
    {"label": "OBS_FINDING",          **get_span(t10, "narrowing", 2)},
    {"label": "MEAS_SIZE",            **get_span(t10, "5mm", 1)},
    {"label": "OBS_LESION",           **get_span(t10, "mass", 1)},
    {"label": "OBS_FINDING",          **get_span(t10, "edematous", 1)},
    {"label": "OBS_FINDING",          **get_span(t10, "erythematous", 1)},
    {"label": "MEAS_COUNT",           **get_span(t10, "4", 1)},
    {"label": "PROC_ACTION",          **get_span(t10, "biopsies", 1)},
    {"label": "OBS_LESION",           **get_span(t10, "carcinoid", 1)},
    {"label": "OBS_FINDING",          **get_span(t10, "inflammatory stricture", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No complications", 1)},
]
BATCH_DATA.append({"id": "284719", "text": t10, "entities": e10})

# ==========================================
# 4. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)