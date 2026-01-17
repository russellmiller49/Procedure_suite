import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
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
            raise ValueError(f"Term '{term}' not found {occurrence} times in text: {text[:50]}...")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 204263_syn_1
# ==========================================
id_1 = "204263_syn_1"
text_1 = """Dx: RLL NSCLC, atelectasis.
Anesthesia: GA, ETT.
Proc: 5F poly cath placed past obstruction. Fluoro verified.
Plan: 7.5Gy x 2 (Final). Extubate/Obs."""
entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "NSCLC", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "atelectasis", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "5F poly cath", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Fluoro", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_1, "7.5Gy", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 204263_syn_2
# ==========================================
id_2 = "204263_syn_2"
text_2 = """OPERATIVE SUMMARY: [REDACTED], presenting with recurrent NSCLC and RLL collapse, underwent the final session of palliative brachytherapy. Under general anesthesia, the near-complete obstruction of the RLL bronchus was visualized. A 5-French polyethylene catheter was navigated distally. Fluoroscopy confirmed the tip position relative to the 4.8 cm treatment length. The patient was transported for the final 7.5 Gy fraction."""
entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "NSCLC", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "collapse", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "brachytherapy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "near-complete obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchus", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "5-French", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "5-French polyethylene catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Fluoroscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "4.8 cm", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_2, "7.5 Gy", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 204263_syn_3
# ==========================================
id_3 = "204263_syn_3"
text_3 = """Code: 31643.
Indication: RLL Atelectasis/Tumor.
Device: 5F Polyethylene Catheter.
Mode: General Anesthesia (due to compromised airway).
Imaging: Fluoroscopy.
Tx: Session 2 of 2 (Final)."""
entities_3 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "Atelectasis", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Tumor", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "5F Polyethylene Catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Fluoroscopy", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 204263_syn_4
# ==========================================
id_4 = "204263_syn_4"
text_4 = """Procedure: Brachy Cath (Final)
Pt: M. Smith
Steps:
1. GA/ETT.
2. Scope RLL (95% blocked).
3. 5F cath placed.
4. Fluoro check.
5. Secure.
Plan: Final 7.5Gy tx."""
entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_4, "95% blocked", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "5F cath", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Fluoro", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_4, "7.5Gy", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 204263_syn_5
# ==========================================
id_5 = "204263_syn_5"
text_5 = """maria smith note for final brachy session rll tumor causing collapse she was under ga scope went down saw the blockage put the 5f catheter past it checked on fluoro taped it up sending her for radiation then catheter out"""
entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "brachy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "collapse", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "blockage", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5, "5f", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "5f catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "fluoro", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 204263_syn_6
# ==========================================
id_6 = "204263_syn_6"
text_6 = """Flexible bronchoscopy for placement of brachytherapy catheter in an 81-year-old female with RLL obstruction. General anesthesia. 5F polyethylene catheter placed. Fluoroscopic verification. Patient transported for final 7.5 Gy treatment."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Flexible bronchoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "brachytherapy catheter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "obstruction", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "5F polyethylene catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Fluoroscopic", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_6, "7.5 Gy", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 204263_syn_7
# ==========================================
id_7 = "204263_syn_7"
text_7 = """[Indication]
RLL NSCLC, lobar collapse.
[Anesthesia]
General, ETT.
[Description]
RLL obstruction visualized. 5F catheter inserted. Position verified with fluoroscopy. Treatment length 4.8 cm.
[Plan]
Final 7.5 Gy fraction. Monitor post-extubation."""
entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "NSCLC", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "lobar collapse", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 2)},
    {"label": "OBS_FINDING", **get_span(text_7, "obstruction", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "5F catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "fluoroscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "4.8 cm", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_7, "7.5 Gy", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 204263_syn_8
# ==========================================
id_8 = "204263_syn_8"
text_8 = """[REDACTED] for her last brachytherapy treatment for that RLL tumor. Because of the lung collapse, we used general anesthesia. We got the 5F catheter past the blockage in the RLL bronchus and checked it with fluoroscopy. She's going for her 7.5 Gy dose now, and we'll take the catheter out afterwards."""
entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "brachytherapy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "lung collapse", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_8, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "5F catheter", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "blockage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RLL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "bronchus", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "fluoroscopy", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_8, "7.5 Gy", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 204263_syn_9
# ==========================================
id_9 = "204263_syn_9"
text_9 = """Diagnosis: RLL neoplasm with atelectasis.
Intervention: Bronchoscopy with insertion of radioelement conduit.
Findings: 5F tube deployed past the occlusion. Location authenticated via imaging. Final 7.5 Gy dose scheduled. Monitoring planned."""
entities_9 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "neoplasm", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "atelectasis", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "radioelement conduit", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_9, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "5F tube", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "occlusion", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_9, "7.5 Gy", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)