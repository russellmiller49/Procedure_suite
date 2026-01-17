import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Adjust the import path if your project structure is different
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback/Mock for standalone testing if the script isn't in the expected dir
    def add_case(case_id, text, entities, root):
        print(f"Adding case {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
            
    if start == -1:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
        
    end = start + len(term)
    return {"start": start, "end": end}

# ==========================================
# Note 1: 652015_syn_1
# ==========================================
id_1 = "652015_syn_1"
text_1 = """Dx: RML Carcinoid, hemoptysis.
Anesthesia: GA, ETT.
Proc: Washings taken. 5F cath placed past RML tumor. Fluoro confirm.
Tx: 5Gy x 3 weekly.
Plan: Obs 23hr. Next session 1 week."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Carcinoid", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hemoptysis", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Washings", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "cath", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Fluoro", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "23hr", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "1 week", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 652015_syn_2
# ==========================================
id_2 = "652015_syn_2"
text_2 = """PROCEDURE NOTE: [REDACTED] recurrent hemoptysis secondary to a typical carcinoid tumor in the right middle lobe (RML). Under general anesthesia, the airway was inspected, revealing an exophytic lesion obstructing the RML bronchus. A 5-French flexible catheter was advanced 2 cm beyond the tumor margin. Positioning was authenticated via fluoroscopy. The patient was prepared for the first of three weekly HDR brachytherapy fractions (5.0 Gy)."""

entities_2 = [
    {"label": "OBS_FINDING", **get_span(text_2, "hemoptysis", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "typical carcinoid tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right middle lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RML", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "exophytic lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RML", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchus", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "5-French", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "flexible catheter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "2 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(text_2, "fluoroscopy", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 652015_syn_3
# ==========================================
id_3 = "652015_syn_3"
text_3 = """Primary Code: 31643 (Catheter placement).
Secondary Code: 31622 (Washings - Bundled/Not billed separately if NCCI applies).
Location: RML Bronchus.
Device: 5F Flexible Catheter.
Imaging: Fluoroscopy verification.
Indication: Recurrent carcinoid with hemoptysis."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Catheter placement", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Washings", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RML", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Bronchus", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Flexible Catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Fluoroscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "carcinoid", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "hemoptysis", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 652015_syn_4
# ==========================================
id_4 = "652015_syn_4"
text_4 = """Procedure: Bronchoscopy w/ Brachy Cath
Pt: T. Anderson
Steps:
1. GA/ETT.
2. Scope to RML.
3. Washings for cytology.
4. Place 5F catheter.
5. Verify with fluoro.
6. Secure device.
Plan: RadOnc 5Gy."""

entities_4 = [
    {"label": "DEV_CATHETER", **get_span(text_4, "Brachy Cath", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RML", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Washings", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "fluoro", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 652015_syn_5
# ==========================================
id_5 = "652015_syn_5"
text_5 = """dr nguyen note for thomas anderson he has that carcinoid in the rml bleeding again so we are doing brachytherapy anesthesia was ga scope went down washed the area first then put the 5f catheter in checked it with the x ray machine looks fine taped it up hes going for his first treatment today"""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "carcinoid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rml", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "washed", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5, "5f", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "catheter", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 652015_syn_6
# ==========================================
id_6 = "652015_syn_6"
text_6 = """A 77-year-old male with recurrent RML carcinoid tumor underwent bronchoscopy for brachytherapy catheter placement. General anesthesia was used. The airway inspection revealed a 1.2 cm tumor. A 5F flexible catheter was inserted past the lesion. Fluoroscopy confirmed correct placement. The patient will receive 5.0 Gy today as part of a 3-fraction course."""

entities_6 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RML", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "carcinoid tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "brachytherapy catheter placement", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "brachytherapy catheter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.2 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "flexible catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Fluoroscopy", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 652015_syn_7
# ==========================================
id_7 = "652015_syn_7"
text_7 = """[Indication]
Recurrent RML carcinoid, hemoptysis.
[Anesthesia]
General, ETT.
[Description]
RML tumor visualized. Bronchial washings obtained. 5F catheter placed distal to tumor. Position confirmed with fluoroscopy. Treatment length 3.2 cm.
[Plan]
Weekly sessions x3. Monitor for bleeding."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RML", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "carcinoid", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RML", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Bronchial washings", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(text_7, "fluoroscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "3.2 cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "bleeding", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 652015_syn_8
# ==========================================
id_8 = "652015_syn_8"
text_8 = """We performed a bronchoscopy on [REDACTED] his recurring carcinoid tumor in the right middle lobe. After putting him under general anesthesia, we inspected the airway and took some washings. We then placed a 5F catheter through the scope, guiding it past the tumor. We double-checked the position with fluoroscopy. He's set to get 5 Gy of radiation today."""

entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "carcinoid tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right middle lobe", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "washings", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_8, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(text_8, "fluoroscopy", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 652015_syn_9
# ==========================================
id_9 = "652015_syn_9"
text_9 = """Reason: Recurring carcinoid of RML.
Action: Endoscopy with positioning of radiation catheter.
Findings: Exophytic mass in RML. 5F tube deployed. Site validated by fluoroscopy. Washings collected. Patient routed to Oncology for 5 Gy dose."""

entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "carcinoid", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RML", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "radiation catheter", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Exophytic mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RML", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_9, "5F", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "tube", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Washings", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)