import sys
from pathlib import Path

# Set up the repository root (assuming standard directory structure)
# If this script is in 'scripts/', the root is one level up.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 653325_syn_1
# ==========================================
t1 = """Dx: Metastatic RCC to LUL.
Anesthesia: Mod Sed.
Proc: 6F afterloading cath placed. Fluoro verified.
Plan: Final 5Gy session. Cath removed post-tx. F/U 4wks."""

e1 = [
    {"label": "OBS_LESION",      **get_span(t1, "Metastatic RCC", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t1, "LUL", 1)},
    # "afterloading cath" is an airway tool, mapped to INSTRUMENT to avoid pleural schema mapping
    {"label": "DEV_INSTRUMENT",  **get_span(t1, "afterloading cath", 1)},
    {"label": "PROC_METHOD",     **get_span(t1, "Fluoro", 1)}
]
BATCH_DATA.append({"id": "653325_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 653325_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: [REDACTED] his final fraction of endobronchial brachytherapy for a metastatic renal cell carcinoma lesion in the LUL. Under moderate sedation, the 2.2 cm tumor was id[REDACTED]. A 6-French afterloading catheter was positioned 2 cm distal to the lesion. Verification was accomplished via fluoroscopy. The patient proceeded to Radiation Oncology for the terminal 5.0 Gy dose."""

e2 = [
    {"label": "OBS_LESION",      **get_span(t2, "metastatic renal cell carcinoma", 1)},
    {"label": "OBS_LESION",      **get_span(t2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t2, "LUL", 1)},
    {"label": "MEAS_SIZE",       **get_span(t2, "2.2 cm", 1)}, # Tumor size
    {"label": "OBS_LESION",      **get_span(t2, "tumor", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t2, "afterloading catheter", 1)},
    {"label": "OBS_LESION",      **get_span(t2, "lesion", 2)},
    {"label": "PROC_METHOD",     **get_span(t2, "fluoroscopy", 1)}
]
BATCH_DATA.append({"id": "653325_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 653325_syn_3
# ==========================================
t3 = """Code: 31643.
Indication: LUL Endobronchial Metastasis.
Hardware: 6F Afterloading Catheter.
Imaging: Fluoroscopy verification included.
Treatment: Session 3 of 3 (Final).
Status: Outpatient."""

e3 = [
    {"label": "ANAT_LUNG_LOC",   **get_span(t3, "LUL", 1)},
    {"label": "OBS_LESION",      **get_span(t3, "Metastasis", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t3, "Afterloading Catheter", 1)},
    {"label": "PROC_METHOD",     **get_span(t3, "Fluoroscopy", 1)}
]
BATCH_DATA.append({"id": "653325_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 653325_syn_4
# ==========================================
t4 = """Procedure: Brachy Cath Placement (Final)
Pt: J. Garcia
Steps:
1. Sedation.
2. Scope LUL.
3. 6F cath placed.
4. Fluoro confirm.
5. Secure.
Plan: Final tx today."""

e4 = [
    {"label": "DEV_INSTRUMENT",  **get_span(t4, "Brachy Cath", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t4, "LUL", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t4, "cath", 1)}, # "6F cath placed"
    {"label": "PROC_METHOD",     **get_span(t4, "Fluoro", 1)}
]
BATCH_DATA.append({"id": "653325_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 653325_syn_5
# ==========================================
t5 = """dr nguyen note for joseph garcia he has that kidney cancer met in his lung lul doing the last brachy session today sedation was fine put the 6f catheter in checked it on the screen looks good taped it sending him for radiation then we pull the catheter"""

e5 = [
    {"label": "OBS_LESION",      **get_span(t5, "kidney cancer met", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t5, "lul", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t5, "catheter", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t5, "catheter", 2)}
]
BATCH_DATA.append({"id": "653325_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 653325_syn_6
# ==========================================
t6 = """Flexible bronchoscopy performed for placement of brachytherapy catheter in a 76-year-old male with LUL metastatic RCC. Moderate sedation. 6F afterloading catheter placed across the tumor. Fluoroscopic confirmation obtained. This represents the final of 3 planned sessions."""

e6 = [
    # "brachytherapy catheter" is a valid instrument span
    {"label": "DEV_INSTRUMENT",  **get_span(t6, "brachytherapy catheter", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t6, "LUL", 1)},
    {"label": "OBS_LESION",      **get_span(t6, "metastatic RCC", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t6, "afterloading catheter", 1)},
    {"label": "OBS_LESION",      **get_span(t6, "tumor", 1)},
    {"label": "PROC_METHOD",     **get_span(t6, "Fluoroscopic", 1)}
]
BATCH_DATA.append({"id": "653325_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 653325_syn_7
# ==========================================
t7 = """[Indication]
Metastatic RCC, LUL obstruction.
[Anesthesia]
Moderate sedation.
[Description]
LUL tumor id[REDACTED]. 6F catheter placed. Fluoroscopic verification. Treatment length 4.2 cm.
[Plan]
Final 5.0 Gy fraction. Remove cath. Clinic f/u."""

e7 = [
    {"label": "OBS_LESION",      **get_span(t7, "Metastatic RCC", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t7, "LUL", 1)},
    {"label": "OBS_LESION",      **get_span(t7, "obstruction", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t7, "LUL", 2)},
    {"label": "OBS_LESION",      **get_span(t7, "tumor", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t7, "catheter", 1)},
    {"label": "PROC_METHOD",     **get_span(t7, "Fluoroscopic", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t7, "cath", 1)}
]
BATCH_DATA.append({"id": "653325_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 653325_syn_8
# ==========================================
t8 = """We did the final catheter placement for [REDACTED] today. Using moderate sedation, we guided the scope to the LUL and threaded the 6F catheter past the tumor. Fluoroscopy showed it was in a good spot. He's off to get his last dose of radiation, and then the catheter comes out."""

e8 = [
    {"label": "DEV_INSTRUMENT",  **get_span(t8, "catheter", 1)},
    {"label": "ANAT_LUNG_LOC",   **get_span(t8, "LUL", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t8, "catheter", 2)},
    {"label": "OBS_LESION",      **get_span(t8, "tumor", 1)},
    {"label": "PROC_METHOD",     **get_span(t8, "Fluoroscopy", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t8, "catheter", 3)}
]
BATCH_DATA.append({"id": "653325_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 653325_syn_9
# ==========================================
t9 = """Diagnosis: LUL renal cell metastasis.
Procedure: Bronchoscopy with implantation of radiation tube.
Findings: 6F device inserted past the obstruction. Fluoroscopy utilized for validation. Final 5 Gy dose to be administered. Follow-up in one month."""

e9 = [
    {"label": "ANAT_LUNG_LOC",   **get_span(t9, "LUL", 1)},
    {"label": "OBS_LESION",      **get_span(t9, "renal cell metastasis", 1)},
    # "radiation tube" captures the function well under DEV_INSTRUMENT
    {"label": "DEV_INSTRUMENT",  **get_span(t9, "radiation tube", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t9, "device", 1)},
    {"label": "OBS_LESION",      **get_span(t9, "obstruction", 1)},
    {"label": "PROC_METHOD",     **get_span(t9, "Fluoroscopy", 1)}
]
BATCH_DATA.append({"id": "653325_syn_9", "text": t9, "entities": e9})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)