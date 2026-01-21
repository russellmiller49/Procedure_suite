import sys
from pathlib import Path

# Set up the repository root path.
# This file lives at: <repo>/data/granular annotations/Python_update_scripts/<id>.py
# so parents[3] is the repo root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError as e:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print(f"ImportError: {e}")
    print(f"Computed REPO_ROOT: {REPO_ROOT}")
    sys.exit(1)

# Helper function to find text spans
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

BATCH_DATA = []

# ==========================================
# Note 1: 419283_syn_1
# ==========================================
t1 = """Indication: RUL mass (PET+).
Findings: RB1 mucosal invasion.
Action: 5 biopsies, 1 brush.
ROSE: Suspicious for malignancy.
Plan: Tumor board."""
e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RB1", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "mucosal invasion", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "1", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Suspicious for malignancy", 1)}
]
BATCH_DATA.append({"id": "419283_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 419283_syn_2
# ==========================================
t2 = """PROCEDURE: Flexible bronchoscopy with rapid on-site evaluation (ROSE). The RUL apical segment revealed extrinsic compression with mucosal irregularities suggestive of invasion. Five biopsy specimens and a protected brush sample were obtained. ROSE preliminary interpretation demonstrated atypical cells consistent with malignancy."""
e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "Flexible bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL apical segment", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "extrinsic compression", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "mucosal irregularities", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "invasion", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "Five", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "protected brush", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "atypical cells consistent with malignancy", 1)}
]
BATCH_DATA.append({"id": "419283_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 419283_syn_3
# ==========================================
t3 = """CPT Coding: 31625 (Biopsy). 31623 (Brushing) is not separately reportable when performed at the same site (RB1) as the biopsy. Service encompasses the diagnostic sampling of the RUL lesion."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Brushing", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RB1", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "lesion", 1)}
]
BATCH_DATA.append({"id": "419283_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 419283_syn_4
# ==========================================
t4 = """Procedure: Bronchoscopy
Pt: L. Anderson
1. Scope to RUL.
2. RB1 looks irregular/invaded.
3. Biopsy x5.
4. Brush x1.
5. ROSE: Positive for cancer cells.
Plan: Oncology referral."""
e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB1", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "irregular", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "invaded", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "5", 2)}, # "x5"
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "1", 2)}, # "x1"
    {"label": "OBS_ROSE", **get_span(t4, "Positive for cancer cells", 1)}
]
BATCH_DATA.append({"id": "419283_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 419283_syn_5
# ==========================================
t5 = """linda anderson rul mass on pet scan went in and saw rb1 looking bad mucosa irregular took 5 biopsies and a brush rose guy said it looks like cancer no bleeding going to tumor board."""
e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rul", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rb1", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "mucosa irregular", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "looks like cancer", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 1)}
]
BATCH_DATA.append({"id": "419283_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 419283_syn_6
# ==========================================
t6 = """Moderate sedation was used. The RUL apical segment (RB1) showed mucosal invasion and extrinsic compression. Five endobronchial biopsies and a brush specimen were obtained. ROSE confirmed atypical cells suspicious for malignancy. The patient was discharged home."""
e6 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL apical segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RB1", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "mucosal invasion", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "extrinsic compression", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Five", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "endobronchial biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "atypical cells suspicious for malignancy", 1)}
]
BATCH_DATA.append({"id": "419283_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 419283_syn_7
# ==========================================
t7 = """[Indication]
RUL mass, PET positive.
[Anesthesia]
Moderate.
[Description]
RB1 mucosal invasion noted. 5 Biopsies + Brush taken. ROSE positive.
[Plan]
Tumor board. Oncology referral."""
e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB1", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "mucosal invasion", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "positive", 2)} # First "positive" is PET, second is ROSE
]
BATCH_DATA.append({"id": "419283_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 419283_syn_8
# ==========================================
t8 = """[REDACTED] for a PET-positive mass in the right upper lobe. We saw irregular tissue invading the airway at RB1. We took five biopsies and a brush sample. The pathologist in the room confirmed suspicious cells immediately. We will discuss her case at the tumor board."""
e8 = [
    {"label": "OBS_LESION", **get_span(t8, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right upper lobe", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "irregular tissue", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "invading", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "RB1", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "five", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "suspicious cells", 1)}
]
BATCH_DATA.append({"id": "419283_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 419283_syn_9
# ==========================================
t9 = """Diagnostic evaluation of RUL mass. Performed endoscopy. Noted luminal invasion at RB1. Sampled tissue via forceps and brush. ROSE indicated malignancy. Referred to oncology."""
e9 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "luminal invasion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RB1", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "malignancy", 1)}
]
BATCH_DATA.append({"id": "419283_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 419283
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Richard Patel

Dx: RUL mass with endobronchial extension seen on PET (SUV 12.4)
Procedure: Bronchoscopy with endobronchial biopsy, brushings

Moderate sedation. Oral bronchoscopy. RUL apical segment (RB1) shows extrinsic compression with mucosal invasion - erythematous, irregular mucosa extending into lumen. 5 endobronchial biopsies obtained. Protected brush specimen from same site. LUL, LLL, RML, RLL all normal. No secretions or blood.

ROSE: Atypical cells, suspicious for malignancy.

D/C home. Path results to be discussed at tumor board. PET staging complete.

R. Patel, MD"""
e10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "endobronchial extension", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "endobronchial biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "brushings", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL apical segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB1", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "extrinsic compression", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "mucosal invasion", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "erythematous", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "irregular mucosa", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "extending into lumen", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "endobronchial biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Protected brush", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "blood", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Atypical cells, suspicious for malignancy", 1)}
]
BATCH_DATA.append({"id": "419283", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)