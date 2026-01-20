import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
# Adjust parents based on where this script is saved.
# If saved in: data/granular_annotations/Python_update_scripts/
# Then parents[3] is the Repo Root.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

# ==========================================
# 2. Data Definition
# ==========================================

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3729485_syn_1
# ==========================================
t1 = """Procedure: EBUS-TBNA
Target: Mediastinal/Hilar Nodes
Results:
- Stn 7: 31mm (Pos Lymphoma)
- Stn 4R: 22mm (Pos Lymphoma)
- Stn 10R: 17mm (Pos Lymphoma)
- Stn 11R: 19mm (Pos Lymphoma)
Disposition: Outpatient. Ref to Oncology."""

e1 = [
    {"label": "PROC_METHOD",     **get_span(t1, "EBUS", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "Hilar", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "Stn 7", 1)},
    {"label": "MEAS_SIZE",       **get_span(t1, "31mm", 1)},
    {"label": "OBS_ROSE",        **get_span(t1, "Lymphoma", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "Stn 4R", 1)},
    {"label": "MEAS_SIZE",       **get_span(t1, "22mm", 1)},
    {"label": "OBS_ROSE",        **get_span(t1, "Lymphoma", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "Stn 10R", 1)},
    {"label": "MEAS_SIZE",       **get_span(t1, "17mm", 1)},
    {"label": "OBS_ROSE",        **get_span(t1, "Lymphoma", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t1, "Stn 11R", 1)},
    {"label": "MEAS_SIZE",       **get_span(t1, "19mm", 1)},
    {"label": "OBS_ROSE",        **get_span(t1, "Lymphoma", 4)},
]
BATCH_DATA.append({"id": "3729485_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 3729485_syn_2
# ==========================================
t2 = """PROCEDURE INDICATION: Staging of mediastinal lymphadenopathy in a patient with history of follicular lymphoma.
TECHNIQUE: Endobronchial ultrasound-guided transbronchial needle aspiration.
FINDINGS: The subcarinal (7), right paratracheal (4R), right hilar (10R), and right interlobar (11R) lymph nodes were visualized and noted to be abnormal. TBNA was performed at each station. 
PATHOLOGY: Immediate cytologic evaluation was diagnostic for lymphoma at all sites sampled. Tissue was submitted for flow cytometric analysis."""

e2 = [
    {"label": "PROC_METHOD",     **get_span(t2, "Endobronchial ultrasound", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "transbronchial needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "subcarinal", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "7", 1)},
    {"label": "LATERALITY",      **get_span(t2, "right", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "4R", 1)},
    {"label": "LATERALITY",      **get_span(t2, "right", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "hilar", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "10R", 1)},
    {"label": "LATERALITY",      **get_span(t2, "right", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t2, "11R", 1)},
    {"label": "PROC_ACTION",     **get_span(t2, "TBNA", 1)},
    {"label": "OBS_ROSE",        **get_span(t2, "lymphoma", 2)}, # 1st is history
    {"label": "SPECIMEN",        **get_span(t2, "Tissue", 1)},
]
BATCH_DATA.append({"id": "3729485_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 3729485_syn_3
# ==========================================
t3 = """Code Selection: 31653
Rationale: EBUS sampling performed on >2 distinct nodal stations.
- Station 7 sampled (4 passes)
- Station 4R sampled (3 passes)
- Station 10R sampled (2 passes)
- Station 11R sampled (2 passes)
All samples adequate and diagnostic."""

e3 = [
    {"label": "PROC_METHOD",     **get_span(t3, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 7", 1)},
    {"label": "MEAS_COUNT",      **get_span(t3, "4 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 4R", 1)},
    {"label": "MEAS_COUNT",      **get_span(t3, "3 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 10R", 1)},
    {"label": "MEAS_COUNT",      **get_span(t3, "2 passes", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t3, "Station 11R", 1)},
    {"label": "MEAS_COUNT",      **get_span(t3, "2 passes", 2)},
]
BATCH_DATA.append({"id": "3729485_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 3729485_syn_4
# ==========================================
t4 = """Procedure Note
Pt: [REDACTED]
Staff: Dr. Singh

- EBUS scope inserted.
- Systematic exam of mediastinum.
- Sampled 7, 4R, 10R, 11R.
- ROSE: Lymphoma.
- Complications: None.
- Plan: Oncology referral."""

e4 = [
    {"label": "PROC_METHOD",     **get_span(t4, "EBUS", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t4, "11R", 1)},
    {"label": "OBS_ROSE",        **get_span(t4, "Lymphoma", 1)},
]
BATCH_DATA.append({"id": "3729485_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 3729485_syn_5
# ==========================================
t5 = """note for mr [REDACTED] procedure ebus tbna date [REDACTED]. dr singh performing. indication lymphoma. we saw big nodes at 7 and 4r and smaller ones at 10r 11r. stuck them all with the needle. [REDACTED] said positive for lymphoma. sent for flow. patient did great no bleeding. discharge home."""

e5 = [
    {"label": "PROC_METHOD",     **get_span(t5, "ebus", 1)},
    {"label": "PROC_ACTION",     **get_span(t5, "tbna", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "4r", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "10r", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t5, "11r", 1)},
    {"label": "DEV_NEEDLE",      **get_span(t5, "needle", 1)},
    {"label": "OBS_ROSE",        **get_span(t5, "lymphoma", 2)}, # 1st is indication
]
BATCH_DATA.append({"id": "3729485_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 3729485_syn_6
# ==========================================
t6 = """Under MAC anesthesia, an EBUS-TBNA was performed on [REDACTED]. The indication was staging for follicular lymphoma. We visualized and sampled lymph nodes at stations 7, 4R, 10R, and 11R. All stations yielded positive results for lymphoma on rapid on-site evaluation. Samples were processed for flow cytometry. There were no complications."""

e6 = [
    {"label": "PROC_METHOD",     **get_span(t6, "EBUS", 1)},
    {"label": "PROC_ACTION",     **get_span(t6, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t6, "11R", 1)},
    {"label": "OBS_ROSE",        **get_span(t6, "lymphoma", 2)}, # 1st is history
]
BATCH_DATA.append({"id": "3729485_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 3729485_syn_7
# ==========================================
t7 = """[Indication]
Lymphoma staging.
[Anesthesia]
MAC.
[Description]
EBUS-TBNA of stations 7, 4R, 10R, 11R. All nodes abnormal sonographically. Cytology positive for lymphoma.
[Plan]
Flow cytometry pending. Oncology consult."""

e7 = [
    {"label": "PROC_METHOD",     **get_span(t7, "EBUS", 1)},
    {"label": "PROC_ACTION",     **get_span(t7, "TBNA", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t7, "11R", 1)},
    {"label": "OBS_ROSE",        **get_span(t7, "lymphoma", 1)}, # Lowercase, only 1 occ
]
BATCH_DATA.append({"id": "3729485_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 3729485_syn_8
# ==========================================
t8 = """[REDACTED] EBUS procedure today. We were looking to stage his lymphoma given new findings on his CT scan. We found several abnormal lymph nodes in the chest, specifically under the trachea and on the right side. We took needle samples from four different areas. The preliminary check in the room showed lymphoma cells in all the samples. We sent everything off for detailed testing."""

e8 = [
    {"label": "PROC_METHOD",     **get_span(t8, "EBUS", 1)},
    {"label": "LATERALITY",      **get_span(t8, "right side", 1)},
    {"label": "DEV_NEEDLE",      **get_span(t8, "needle", 1)},
    {"label": "OBS_ROSE",        **get_span(t8, "lymphoma", 2)}, # 1st is staging
]
BATCH_DATA.append({"id": "3729485_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 3729485_syn_9
# ==========================================
t9 = """Procedure: Endosonographic needle aspiration.
Findings: Lymphadenopathy id[REDACTED] at stations 7, 4R, 10R, 11R.
Intervention: Targets were sampled via transbronchial aspiration.
Analysis: Immediate cytology revealed lymphoma. Tissue forwarded for flow cytometry."""

e9 = [
    {"label": "PROC_METHOD",     **get_span(t9, "Endosonographic", 1)},
    {"label": "PROC_ACTION",     **get_span(t9, "needle aspiration", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "7", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "10R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t9, "11R", 1)},
    {"label": "PROC_ACTION",     **get_span(t9, "transbronchial aspiration", 1)},
    {"label": "OBS_ROSE",        **get_span(t9, "lymphoma", 1)},
    {"label": "SPECIMEN",        **get_span(t9, "Tissue", 1)},
]
BATCH_DATA.append({"id": "3729485_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 3729485
# ==========================================
t10 = """PATIENT: [REDACTED] RECORD: 3729485 SERVICE DATE: [REDACTED]
PROCEDURE: EBUS-TBNA
DOCTOR: Singh, Raj MD
REASON: Lymphoma staging - known follicular lymphoma, new mediastinal nodes on CT
SEDATION: MAC anesthesia (Dr. Johnson)
WHAT WE DID: Put ultrasound bronchoscope in through mouth. Looked at lymph nodes in chest with ultrasound. Used needle to get samples from lymph nodes.
NODES WE FOUND:
•	Node under windpipe branches (station 7): 31mm, looks abnormal
•	Node on right (station 4R): 22mm, looks abnormal
•	Node at right lung root (station 10R): 17mm
•	Node inside right lung (station 11R): 19mm
SAMPLES TAKEN: Station 7: Did 4 needle sticks
•	Doctor looking at slides right away says: SEE LYMPHOMA CELLS
Station 4R: Did 3 sticks
•	Lymphoma cells seen
Station 10R: Did 2 sticks
•	Lymphoma present
Station 11R: Did 2 sticks
•	Also shows lymphoma
All samples sent for special testing (flow cytometry)
NO PROBLEMS during procedure
WHAT IT MEANS: Lymphoma has spread to multiple lymph nodes in chest
NEXT STEPS:
•	Cancer doctor will see patient
•	More treatment planning needed
•	Full testing results in few days
Dr. Raj Singh [REDACTED]
________________________________________

╔═══════════════════════════════════════╗ ║ INTERVENTIONAL PULMONOLOGY REPORT ║ ╚═══════════════════════════════════════╝"""

e10 = [
    {"label": "PROC_METHOD",     **get_span(t10, "EBUS", 1)},
    {"label": "PROC_ACTION",     **get_span(t10, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT",  **get_span(t10, "ultrasound bronchoscope", 1)},
    {"label": "PROC_METHOD",     **get_span(t10, "ultrasound", 2)}, # 1st is in 'ultrasound bronchoscope'
    {"label": "DEV_NEEDLE",      **get_span(t10, "needle", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 7", 1)},
    {"label": "MEAS_SIZE",       **get_span(t10, "31mm", 1)},
    {"label": "LATERALITY",      **get_span(t10, "right", 1)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 4R", 1)},
    {"label": "MEAS_SIZE",       **get_span(t10, "22mm", 1)},
    {"label": "LATERALITY",      **get_span(t10, "right", 2)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 10R", 1)},
    {"label": "MEAS_SIZE",       **get_span(t10, "17mm", 1)},
    {"label": "LATERALITY",      **get_span(t10, "right", 3)},
    {"label": "ANAT_LN_STATION", **get_span(t10, "station 11R", 1)},
    {"label": "MEAS_SIZE",       **get_span(t10, "19mm", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 7", 1)},
    {"label": "MEAS_COUNT",      **get_span(t10, "4 needle sticks", 1)},
    {"label": "OBS_ROSE",        **get_span(t10, "LYMPHOMA", 1)},
    
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 4R", 1)},
    {"label": "MEAS_COUNT",      **get_span(t10, "3 sticks", 1)},
    {"label": "OBS_ROSE",        **get_span(t10, "Lymphoma", 2)}, # 1st is Reason
    
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 10R", 1)},
    {"label": "MEAS_COUNT",      **get_span(t10, "2 sticks", 1)},
    {"label": "OBS_ROSE",        **get_span(t10, "Lymphoma", 3)},
    
    {"label": "ANAT_LN_STATION", **get_span(t10, "Station 11R", 1)},
    {"label": "MEAS_COUNT",      **get_span(t10, "2 sticks", 2)},
    {"label": "OBS_ROSE",        **get_span(t10, "lymphoma", 2)}, # 1st is follicular
]
BATCH_DATA.append({"id": "3729485", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)