import sys
from pathlib import Path

# Calculate the repository root dynamically
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            # Raise error immediately if the term is not found to prevent data corruption
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text: {text[:50]}...")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 436795_syn_1
# ==========================================
t1 = """Dx: Distal Trachea SCC.
Anesthesia: Mod Sed.
Proc: 5F cath placed past 2.0cm tumor. Fluoro verified.
Plan: 6Gy x 4. D/C home after tx."""

e1 = [
    {"label": "ANAT_AIRWAY", **get_span(t1, "Distal Trachea", 1)},
    {"label": "OBS_LESION",   **get_span(t1, "tumor", 1)},
    {"label": "MEAS_SIZE",    **get_span(t1, "2.0cm", 1)},
    {"label": "PROC_METHOD",  **get_span(t1, "Fluoro", 1)}
]

BATCH_DATA.append({"id": "436795_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 436795_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: [REDACTED], a 65-year-old male with squamous cell carcinoma of the distal trachea, underwent flexible bronchoscopy. The lesion presented with 55% obstruction. A 5-French flexible catheter was successfully navigated past the distal margin of the tumor. Fluoroscopic imaging confirmed the catheter position relative to the 4.0 cm treatment length. The patient was transported for HDR brachytherapy delivery."""

e2 = [
    {"label": "ANAT_AIRWAY",              **get_span(t2, "distal trachea", 1)},
    {"label": "OBS_LESION",               **get_span(t2, "lesion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "55% obstruction", 1)},
    {"label": "OBS_LESION",               **get_span(t2, "tumor", 1)},
    {"label": "PROC_METHOD",              **get_span(t2, "Fluoroscopic", 1)},
    {"label": "MEAS_SIZE",                **get_span(t2, "4.0 cm", 1)}
]

BATCH_DATA.append({"id": "436795_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 436795_syn_3
# ==========================================
t3 = """Procedure: 31643 (Catheter placement for radioelement).
Site: Distal Trachea.
Technique: 5F flexible catheter inserted via working channel.
Validation: Fluoroscopic guidance (5 min).
Dose Plan: 6.0 Gy x 4 fractions.
Note: Outpatient setting."""

e3 = [
    {"label": "ANAT_AIRWAY",  **get_span(t3, "Distal Trachea", 1)},
    {"label": "PROC_METHOD",  **get_span(t3, "Fluoroscopic", 1)},
    {"label": "MEAS_TIME",    **get_span(t3, "5 min", 1)}
]

BATCH_DATA.append({"id": "436795_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 436795_syn_4
# ==========================================
t4 = """Resident Note
Pt: R. Johnson
Staff: Dr. Patel
Steps:
1. Mod sed start.
2. Scope to distal trachea.
3. Tumor ID'd.
4. 5F cath placed.
5. Fluoro check.
6. Secure.
Plan: Session 1/4 today."""

e4 = [
    {"label": "ANAT_AIRWAY", **get_span(t4, "distal trachea", 1)},
    {"label": "OBS_LESION",  **get_span(t4, "Tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Fluoro", 1)}
]

BATCH_DATA.append({"id": "436795_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 436795_syn_5
# ==========================================
t5 = """note for mr [REDACTED] distal trachea tumor causing wheezing we did the brachy cath placement moderate sedation was used scope went in saw the tumor put the 5f catheter past it fluoro confirmed it was in the right spot taped it to his nose sending him for 6gy radiation"""

e5 = [
    {"label": "ANAT_AIRWAY", **get_span(t5, "distal trachea", 1)},
    {"label": "OBS_LESION",  **get_span(t5, "tumor", 1)},
    {"label": "OBS_LESION",  **get_span(t5, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(t5, "fluoro", 1)}
]

BATCH_DATA.append({"id": "436795_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 436795_syn_6
# ==========================================
t6 = """Bronchoscopy for brachytherapy catheter placement in a 65-year-old male with distal tracheal SCC. Moderate sedation used. The 2.0 cm tumor was visualized. A 5F flexible catheter was advanced distally. Position confirmed via fluoroscopy. The patient tolerated the procedure well and was sent for radiation therapy."""

e6 = [
    {"label": "ANAT_AIRWAY", **get_span(t6, "distal tracheal", 1)},
    {"label": "MEAS_SIZE",   **get_span(t6, "2.0 cm", 1)},
    {"label": "OBS_LESION",  **get_span(t6, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "fluoroscopy", 1)}
]

BATCH_DATA.append({"id": "436795_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 436795_syn_7
# ==========================================
t7 = """[Indication]
Distal trachea SCC, dyspnea.
[Anesthesia]
Moderate sedation.
[Description]
Tracheal tumor visualized. 5F catheter inserted 2 cm distal to lesion. Fluoroscopy used to verify position. Catheter secured.
[Plan]
6.0 Gy fraction 1. Weekly f/u."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "Distal trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "Tracheal", 1)},
    {"label": "OBS_LESION",  **get_span(t7, "tumor", 1)},
    {"label": "MEAS_SIZE",   **get_span(t7, "2 cm", 1)},
    {"label": "OBS_LESION",  **get_span(t7, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Fluoroscopy", 1)}
]

BATCH_DATA.append({"id": "436795_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 436795_syn_8
# ==========================================
t8 = """[REDACTED] for his first brachytherapy session for a tracheal tumor. We kept him comfortable with moderate sedation. The scope showed the tumor in the lower windpipe. We slid a 5F catheter down past the blockage and used the fluoroscope to make sure it was sitting right. We taped it securely so he could go get his radiation treatment."""

e8 = [
    {"label": "ANAT_AIRWAY", **get_span(t8, "tracheal", 1)},
    {"label": "OBS_LESION",  **get_span(t8, "tumor", 1)},
    {"label": "OBS_LESION",  **get_span(t8, "tumor", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "lower windpipe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "fluoroscope", 1)}
]

BATCH_DATA.append({"id": "436795_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 436795_syn_9
# ==========================================
t9 = """Dx: Tracheal carcinoma.
Proc: Scope with installation of brachytherapy line.
Details: 5F tube inserted past the 2 cm mass. Positioning confirmed by fluoroscopy. 6 Gy dosage planned. Patient discharged post-treatment."""

e9 = [
    {"label": "ANAT_AIRWAY", **get_span(t9, "Tracheal", 1)},
    {"label": "MEAS_SIZE",   **get_span(t9, "2 cm", 1)},
    {"label": "OBS_LESION",  **get_span(t9, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "fluoroscopy", 1)}
]

BATCH_DATA.append({"id": "436795_syn_9", "text": t9, "entities": e9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")