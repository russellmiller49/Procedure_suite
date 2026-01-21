import sys
from pathlib import Path

# Set up the repository root dynamically
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Term not found enough times
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1028374_syn_1
# ==========================================
t1 = """Indication: Staging RUL CA.
Procedure:
- 31653: EBUS 3 stations (4R, 7, 4L).
- 31629: TBNA RUL mass (First lobe).
- 31633: TBNA LUL nodule (Add'l lobe).
Results: N2 disease confirmed."""

e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "CA", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "EBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 2)}, # "3" in "3 stations"
    {"label": "ANAT_LN_STATION", **get_span(t1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "4L", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "N2 disease confirmed", 1)}
]
BATCH_DATA.append({"id": "1028374_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1028374_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: EBUS-TBNA and Conventional TBNA.
The mediastinum was staged utilizing EBUS, sampling stations 4R, 7, and 4L. Attention was then turned to parenchymal targets. Using a conventional TBNA needle, the RUL mass was sampled (Initial Lobe, 31629). Subsequently, the separate LUL nodule was id[REDACTED] and sampled (Additional Lobe, 31633). ROSE confirmed malignancy."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "mediastinum", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "4L", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "sampled", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "sampled", 2)},
    {"label": "OBS_ROSE", **get_span(t2, "malignancy", 1)}
]
BATCH_DATA.append({"id": "1028374_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1028374_syn_3
# ==========================================
t3 = """Code Selection:
- 31653 (EBUS-TBNA 3+ stations).
- 31629 (Transtracheal/bronchial needle aspiration, initial lobe/structure - RUL Mass).
- 31633 (TBNA, each additional lobe - LUL Nodule).
Rationale: Separate parenchymal lesions in distinct lobes sampled via needle aspiration."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "3", 2)}, # Matches "3" in "3+"
    {"label": "PROC_ACTION", **get_span(t3, "Transtracheal/bronchial needle aspiration", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Mass", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Nodule", 1)},
    {"label": "OBS_LESION", **get_span(t3, "lesions", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "needle aspiration", 2)}
]
BATCH_DATA.append({"id": "1028374_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1028374_syn_4
# ==========================================
t4 = """Procedure: EBUS + TBNA
1. EBUS done first (3 stations).
2. Switched to conventional needle.
3. Poked RUL mass (First lobe).
4. Poked LUL nodule (Second lobe).
Diagnosis: Adeno CA."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "EBUS", 2)},
    {"label": "MEAS_COUNT", **get_span(t4, "3", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodule", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Adeno CA", 1)}
]
BATCH_DATA.append({"id": "1028374_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1028374_syn_5
# ==========================================
t5 = """doing staging for linda chang she has rul cancer but also a lul nodule. did the ebus first got the lymph nodes. then used the needle on the rul mass. then went to the left side and needled the lul nodule too. positive for cancer."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rul", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lul", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ebus", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "lymph nodes", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rul", 2)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "LATERALITY", **get_span(t5, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lul", 2)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 2)},
    {"label": "OBS_FINDING", **get_span(t5, "positive for cancer", 1)}
]
BATCH_DATA.append({"id": "1028374_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1028374_syn_6
# ==========================================
t6 = """Bronchoscopy with EBUS and conventional TBNA performed. EBUS sampling of stations 4R, 7, and 4L completed. Conventional transbronchial needle aspiration performed on RUL mass (initial lobe). Conventional TBNA then performed on LUL nodule (additional lobe)."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "EBUS", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4L", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)}
]
BATCH_DATA.append({"id": "1028374_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1028374_syn_7
# ==========================================
t7 = """[Indication]
RUL Adeno, Staging.
[Anesthesia]
General.
[Description]
EBUS: 4R, 7, 4L sampled.
TBNA: RUL mass sampled (31629).
TBNA: LUL nodule sampled (31633).
[Plan]
Oncology referral."""

e7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Adeno", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4L", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 2)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)}
]
BATCH_DATA.append({"id": "1028374_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1028374_syn_8
# ==========================================
t8 = """We performed a procedure to stage [REDACTED]. First, we used an ultrasound scope to check the lymph nodes in the center of her chest. Then, we used a needle to take samples directly from the main tumor in her right lung. We also saw a spot on her left lung and used the needle to sample that one as well to see if the cancer had spread there."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "ultrasound scope", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t8, "lymph nodes", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right lung", 1)},
    {"label": "OBS_LESION", **get_span(t8, "spot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "left lung", 1)},
    {"label": "OBS_LESION", **get_span(t8, "cancer", 1)}
]
BATCH_DATA.append({"id": "1028374_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1028374_syn_9
# ==========================================
t9 = """Procedure: Endobronchial ultrasound and multi-lobar needle aspiration.
Action: Lymph nodes sampled via EBUS. RUL mass aspirated (primary parenchymal target). LUL nodule aspirated (secondary parenchymal target)."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "Lymph nodes", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "EBUS", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t9, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 2)}
]
BATCH_DATA.append({"id": "1028374_syn_9", "text": t9, "entities": e9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)