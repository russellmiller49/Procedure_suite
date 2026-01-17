import sys
from pathlib import Path

# Set the root directory (assuming this script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback to appending path if module not found immediately
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Term not found enough times
    
    if start != -1:
        return {"start": start, "end": start + len(term)}
    return None

# ==========================================
# Note 1: 345012_syn_1
# ==========================================
text_1 = """Indication: Mediastinal adenopathy.
Proc: VATS biopsy.
- 3 ports.
- Biopsied 4R (x8) and 7 (x6).
- 24Fr chest tube."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsied", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "8", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
]
BATCH_DATA.append({"id": "345012_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 345012_syn_2
# ==========================================
text_2 = """OPERATIVE NOTE: Video-assisted thoracoscopic biopsy of mediastinal lymph nodes.
INDICATION: Extensive mediastinal adenopathy, previous non-diagnostic biopsy.
PROCEDURE: A three-port VATS approach was used. Large confluent nodes were id[REDACTED] in the paratracheal and subcarinal regions. Generous biopsies were taken from stations 4R and 7 for extensive pathological workup including flow cytometry. A 24Fr chest tube was placed."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Video-assisted thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 2)},
    {"label": "PROC_METHOD", **get_span(text_2, "VATS", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodes", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "subcarinal", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
]
BATCH_DATA.append({"id": "345012_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 345012_syn_3
# ==========================================
text_3 = """CPT 32606: VATS biopsy of mediastinal lymph nodes.
Nodes: 4R and 7.
Specimens: 14 total biopsies.
Work: 3-port access, dissection, biopsy, chest tube.
Indication: Lymphadenopathy."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "14", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 2)},
    {"label": "DEV_CATHETER", **get_span(text_3, "chest tube", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Lymphadenopathy", 1)},
]
BATCH_DATA.append({"id": "345012_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 345012_syn_4
# ==========================================
text_4 = """Procedure: VATS Biopsy
1. GA / ETT.
2. 3 ports.
3. Biopsied 4R and 7.
4. Sent fresh for lymphoma workup.
5. 24Fr chest tube."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "chest tube", 1)},
]
BATCH_DATA.append({"id": "345012_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 345012_syn_5
# ==========================================
text_5 = """[REDACTED] for mediastinal biopsy vats 3 ports huge nodes 4r and 7 took tons of biopsies sent for flow and molecular tube in 24fr no issues."""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "vats", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4r", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "tube", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5, "24fr", 1)},
]
BATCH_DATA.append({"id": "345012_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 345012_syn_6
# ==========================================
text_6 = """Thoracoscopy with mediastinal biopsy. General anesthesia induced. Right thoracoscopy via three-port technique. Large confluent nodal mass in the right paratracheal region. Subcarinal adenopathy. Station 4R 8 large biopsies. Station 7 6 biopsies. Specimens sent fresh to pathology. 24Fr chest tube placed."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodal mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Subcarinal", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "adenopathy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Station 4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "8", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
]
BATCH_DATA.append({"id": "345012_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 345012_syn_7
# ==========================================
text_7 = """[Indication]
Mediastinal adenopathy.
[Anesthesia]
General, ETT.
[Description]
3-port VATS. Biopsies of 4R and 7. 24Fr tube.
[Plan]
Admit."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "adenopathy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsies", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "tube", 1)},
]
BATCH_DATA.append({"id": "345012_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 345012_syn_8
# ==========================================
text_8 = """[REDACTED] lymph nodes in her chest that needed a diagnosis. We did a 3-port VATS procedure under general anesthesia. We found large lymph node masses and took many samples to make sure the lab has enough for all the tests, including for lymphoma. We left a chest tube in to drain the chest."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "VATS", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lymph node masses", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "345012_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 345012_syn_9
# ==========================================
text_9 = """Diagnosis: Mediastinal lymph node enlargement.
Action: Thoracoscopic tissue acquisition.
Details: Nodal stations 4R and 7 sampled. Drain inserted."""

entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "lymph node enlargement", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "tissue acquisition", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Drain", 1)},
]
BATCH_DATA.append({"id": "345012_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 345012
# ==========================================
text_10 = """THORACOSCOPY NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
Date: [REDACTED]
Location: [REDACTED]

Physician: Dr. Mark Stevens, MD - Interventional Pulmonology
Fellow: Dr. Rachel Kim, MD - PGY-6

Procedure: Thoracoscopy with mediastinal biopsy

Indication: 47F with new diagnosis of cervical lymphadenopathy, now with CT showing extensive mediastinal adenopathy. Core biopsy of cervical node non-diagnostic. Need mediastinal tissue for diagnosis.

Anesthesia: General (ETT)

Description:
General anesthesia induced. Patient in left lateral decubitus. Right thoracoscopy via three-port technique:
- Camera port 7th ICS mid-axillary
- Working ports 5th and 9th ICS

Findings:
- Large confluent nodal mass in the right paratracheal region
- Subcarinal adenopathy
- No pleural effusion or nodules

Biopsies:
- Station 4R: 8 large biopsies with excellent tissue cores
- Station 7: 6 biopsies
Specimens sent fresh to pathology for touch preps and permanent sections. Additional tissue for flow cytometry and molecular studies.

24Fr chest tube placed. Full lung expansion confirmed.

No complications. Patient extubated and to PACU.

M. Stevens, MD / R. Kim, MD"""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lymphadenopathy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsy", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodal mass", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "paratracheal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Subcarinal", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "adenopathy", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 4R", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "8", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "tissue cores", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "Station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
]
BATCH_DATA.append({"id": "345012", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)