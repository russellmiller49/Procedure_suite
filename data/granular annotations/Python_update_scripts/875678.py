import sys
from pathlib import Path

# Set up the repository root (assumes this script is running two levels deep or similar)
# Adjust specific path logic as needed for your pipeline environment
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function from the pipeline
# Ensure your environment has this module available
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback/Mock for standalone testing if script is run outside the pipeline
    def add_case(case_id, text, entities, repo_root):
        print(f"Processed {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    Strict case-sensitivity is applied.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            # Safety return to avoid runtime unpacking errors
            # In a production pipeline, this should likely raise a specific error
            print(f"WARNING: Term '{term}' not found (occurrence {occurrence})")
            return {"start": 0, "end": 0}
            
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 875678_syn_1
# ==========================================
id_1 = "875678_syn_1"
text_1 = """Dx: Tracheal Adenoid Cystic Ca.
Anesthesia: Mod Sed.
Proc: 5F flex cath placed past tumor. Fluoro verified.
Plan: 6Gy x 4. Weekly."""

entities_1 = [
    {"label": "ANAT_AIRWAY",      **get_span(text_1, "Tracheal", 1)},
    {"label": "OBS_LESION",       **get_span(text_1, "Adenoid Cystic Ca", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_1, "5F flex cath", 1)},
    {"label": "OBS_LESION",       **get_span(text_1, "tumor", 1)},
    {"label": "PROC_METHOD",      **get_span(text_1, "Fluoro", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 875678_syn_2
# ==========================================
id_2 = "875678_syn_2"
text_2 = """CLINICAL REPORT: [REDACTED], a 72-year-old male with adenoid cystic carcinoma of the mid-trachea, underwent bronchoscopic catheter placement. The exophytic tumor caused 45% obstruction. A 5-French flexible catheter was advanced distally to cover the 3.6 cm treatment length. Fluoroscopic verification was documented. The patient was transferred for the first of four weekly HDR fractions."""

entities_2 = [
    {"label": "OBS_LESION",               **get_span(text_2, "adenoid cystic carcinoma", 1)},
    {"label": "ANAT_AIRWAY",              **get_span(text_2, "mid-trachea", 1)},
    {"label": "PROC_METHOD",              **get_span(text_2, "bronchoscopic", 1)},
    {"label": "OBS_LESION",               **get_span(text_2, "exophytic tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "45% obstruction", 1)},
    {"label": "DEV_CATHETER",             **get_span(text_2, "5-French flexible catheter", 1)},
    {"label": "MEAS_SIZE",                **get_span(text_2, "3.6 cm", 1)},
    {"label": "PROC_METHOD",              **get_span(text_2, "Fluoroscopic", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 875678_syn_3
# ==========================================
id_3 = "875678_syn_3"
text_3 = """Code: 31643.
Site: Mid-trachea.
Device: 5F Flexible Catheter.
Imaging: Fluoroscopy utilized.
Treatment: 6.0 Gy (Session 1).
Indication: Local control of ACC."""

entities_3 = [
    {"label": "ANAT_AIRWAY",      **get_span(text_3, "Mid-trachea", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_3, "5F Flexible Catheter", 1)},
    {"label": "PROC_METHOD",      **get_span(text_3, "Fluoroscopy", 1)},
    {"label": "OBS_LESION",       **get_span(text_3, "ACC", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 875678_syn_4
# ==========================================
id_4 = "875678_syn_4"
text_4 = """Procedure: Brachy Cath #1
Pt: T. Williams
Steps:
1. Mod sed.
2. Scope trachea.
3. 5F cath placed.
4. Fluoro check.
5. Secure.
Plan: RadOnc 6Gy."""

entities_4 = [
    {"label": "DEV_CATHETER",     **get_span(text_4, "Brachy Cath", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_4, "Scope", 1)},
    {"label": "ANAT_AIRWAY",      **get_span(text_4, "trachea", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_4, "5F cath", 1)},
    {"label": "PROC_METHOD",      **get_span(text_4, "Fluoro", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 875678_syn_5
# ==========================================
id_5 = "875678_syn_5"
text_5 = """mr [REDACTED] has that trachea tumor acc we did the cath placement today moderate sedation scope went in saw the tumor mid trachea put the 5f catheter past it checked with fluoro taped it up hes going for radiation now"""

entities_5 = [
    {"label": "ANAT_AIRWAY",      **get_span(text_5, "trachea", 1)},
    {"label": "OBS_LESION",       **get_span(text_5, "tumor", 1)},
    {"label": "OBS_LESION",       **get_span(text_5, "acc", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_5, "cath", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_5, "scope", 1)},
    {"label": "OBS_LESION",       **get_span(text_5, "tumor", 2)},
    {"label": "ANAT_AIRWAY",      **get_span(text_5, "mid trachea", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_5, "5f catheter", 1)},
    {"label": "PROC_METHOD",      **get_span(text_5, "fluoro", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 875678_syn_6
# ==========================================
id_6 = "875678_syn_6"
text_6 = """Bronchoscopy performed for placement of brachytherapy catheter in a 72-year-old male with tracheal ACC. Moderate sedation. 5F catheter placed. Fluoroscopic confirmation. Patient sent for radiation therapy session 1 of 4."""

entities_6 = [
    {"label": "PROC_METHOD",      **get_span(text_6, "Bronchoscopy", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_6, "brachytherapy catheter", 1)},
    {"label": "ANAT_AIRWAY",      **get_span(text_6, "tracheal", 1)},
    {"label": "OBS_LESION",       **get_span(text_6, "ACC", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_6, "5F catheter", 1)},
    {"label": "PROC_METHOD",      **get_span(text_6, "Fluoroscopic", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 875678_syn_7
# ==========================================
id_7 = "875678_syn_7"
text_7 = """[Indication]
Tracheal ACC, dyspnea.
[Anesthesia]
Moderate sedation.
[Description]
Mid-trachea tumor visualized. 5F catheter inserted. Position verified with fluoroscopy. Treatment length 3.6 cm.
[Plan]
6.0 Gy fraction 1. Weekly f/u."""

entities_7 = [
    {"label": "ANAT_AIRWAY",      **get_span(text_7, "Tracheal", 1)},
    {"label": "OBS_LESION",       **get_span(text_7, "ACC", 1)},
    {"label": "OBS_FINDING",      **get_span(text_7, "dyspnea", 1)},
    {"label": "ANAT_AIRWAY",      **get_span(text_7, "Mid-trachea", 1)},
    {"label": "OBS_LESION",       **get_span(text_7, "tumor", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_7, "5F catheter", 1)},
    {"label": "PROC_METHOD",      **get_span(text_7, "fluoroscopy", 1)},
    {"label": "MEAS_SIZE",        **get_span(text_7, "3.6 cm", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 875678_syn_8
# ==========================================
id_8 = "875678_syn_8"
text_8 = """[REDACTED] brachytherapy for his tracheal tumor. We used moderate sedation. The scope showed the tumor in the middle of the windpipe. We slid the 5F catheter past it and checked the position on the screen. It looked good, so we secured it. He's heading to radiation for his first dose."""

entities_8 = [
    {"label": "ANAT_AIRWAY",      **get_span(text_8, "tracheal", 1)},
    {"label": "OBS_LESION",       **get_span(text_8, "tumor", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(text_8, "scope", 1)},
    {"label": "OBS_LESION",       **get_span(text_8, "tumor", 2)},
    {"label": "ANAT_AIRWAY",      **get_span(text_8, "windpipe", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_8, "5F catheter", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 875678_syn_9
# ==========================================
id_9 = "875678_syn_9"
text_9 = """Diagnosis: Tracheal Adenoid Cystic Carcinoma.
Intervention: Endoscopy with insertion of radiation tube.
Findings: 5F device deployed past the mass. Positioning confirmed by fluoroscopy. 6 Gy dosage planned. Return in one week."""

entities_9 = [
    {"label": "ANAT_AIRWAY",      **get_span(text_9, "Tracheal", 1)},
    {"label": "OBS_LESION",       **get_span(text_9, "Adenoid Cystic Carcinoma", 1)},
    {"label": "PROC_METHOD",      **get_span(text_9, "Endoscopy", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_9, "radiation tube", 1)},
    {"label": "DEV_CATHETER",     **get_span(text_9, "5F device", 1)},
    {"label": "OBS_LESION",       **get_span(text_9, "mass", 1)},
    {"label": "PROC_METHOD",      **get_span(text_9, "fluoroscopy", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)