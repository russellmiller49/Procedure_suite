import sys
from pathlib import Path

# Set up the repository root path (assuming script is running within the repo structure)
# If running standalone, this can be adjusted to the absolute path of the 'scripts' directory.
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the repository root to sys.path to allow importing from scripts
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'.")
    print("Ensure the script is run from the correct directory structure.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The occurrence number (1-based).
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 4369574_syn_1
# ==========================================
t1 = """Indication: Post-TB bronchial stenosis L main.
Procedure: Balloon dilation (31630).
- MAC, LMA.
- L mainstem stenosis 59%.
- CRE balloon: 7, 8, 10mm x 90s.
- Post: 34% residual.
- Minimal ooze.
Plan: D/C same day. Decadron 10mg."""

e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "bronchial stenosis", 1)},
    {"label": "LATERALITY", **get_span(t1, "L", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "main", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "dilation", 1)},
    {"label": "LATERALITY", **get_span(t1, "L", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "59%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "7", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "10mm", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "90s", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "34% residual", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Minimal ooze", 1)},
    {"label": "MEDICATION", **get_span(t1, "Decadron", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_1", "text": t1, "entities": e1})


# ==========================================
# Note 2: 4369574_syn_2
# ==========================================
t2 = """PROCEDURE: Bronchoscopic dilation of inflammatory bronchial stenosis.
ETIOLOGY: Sequelae of pulmonary tuberculosis.
FINDINGS: Eccentric stenosis of the left mainstem bronchus, 3 cm distal to the carina, narrowing the lumen by approximately 59%.
INTERVENTION: Using a CRE balloon catheter, serial dilations were performed at 7mm, 8mm, and 10mm. Each inflation was sustained for 90 seconds to disrupt fibrous tissue.
OUTCOME: Improved luminal patency with 34% residual narrowing. Procedure well tolerated."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "dilation", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "stenosis", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "stenosis", 2)},
    {"label": "LATERALITY", **get_span(t2, "left", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "mainstem bronchus", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "3 cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "carina", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "59%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "CRE balloon catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "dilations", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "10mm", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "90 seconds", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "34% residual narrowing", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_2", "text": t2, "entities": e2})


# ==========================================
# Note 3: 4369574_syn_3
# ==========================================
t3 = """Code: 31630.
Diagnosis: Post-tuberculous stenosis of bronchus.
Procedure: Flexible bronchoscopy. Localization of L mainstem stenosis. Dilation with CRE balloon (7-10mm). Documented improvement in airway caliber. Medical necessity established by symptoms."""

e3 = [
    {"label": "OBS_FINDING", **get_span(t3, "stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "bronchus", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Flexible bronchoscopy", 1)},
    {"label": "LATERALITY", **get_span(t3, "L", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "stenosis", 2)},
    {"label": "PROC_ACTION", **get_span(t3, "Dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "7-10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "improvement in airway caliber", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_3", "text": t3, "entities": e3})


# ==========================================
# Note 4: 4369574_syn_4
# ==========================================
t4 = """Resident Note
Patient: [REDACTED]
Procedure: Balloon Dilation
Staff: Dr. D. Anderson
Steps:
1. MAC, LMA.
2. Scope to L main.
3. Stenosis id[REDACTED].
4. CRE balloon dilation x 3.
5. Good result.
Plan: Discharge today."""

e4 = [
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Dilation", 1)},
    {"label": "LATERALITY", **get_span(t4, "L", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "main", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "dilation", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_4", "text": t4, "entities": e4})


# ==========================================
# Note 5: 4369574_syn_5
# ==========================================
t5 = """kevin torres had tb years ago now his left main bronchus is closing up. did a bronch with mac. saw the narrowing about 60 percent. used the cre balloon 7 8 10 mm held for 90 seconds. opened up decent maybe 35 percent left. little bleeding. discharge him today with steroids."""

e5 = [
    {"label": "LATERALITY", **get_span(t5, "left", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "main bronchus", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "closing up", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "bronch", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "narrowing", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "60 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "cre balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "7", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "10 mm", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "90 seconds", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "35 percent left", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "bleeding", 1)},
    {"label": "MEDICATION", **get_span(t5, "steroids", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_5", "text": t5, "entities": e5})


# ==========================================
# Note 6: 4369574_syn_6
# ==========================================
t6 = """This 55-year-old male with a history of TB underwent bronchoscopy for left mainstem bronchial stenosis. Under MAC anesthesia, the stenosis was id[REDACTED] with 59% narrowing. A CRE balloon was used for dilation at 7mm, 8mm, and 10mm. The airway patency improved to 66%. Minimal mucosal oozing was noted. The patient was discharged the same day."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "bronchoscopy", 1)},
    {"label": "LATERALITY", **get_span(t6, "left", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "mainstem bronchial", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "stenosis", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "59% narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "7mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "patency improved to 66%", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "Minimal mucosal oozing", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_6", "text": t6, "entities": e6})


# ==========================================
# Note 7: 4369574_syn_7
# ==========================================
t7 = """[Indication]
Post-tuberculous bronchial stenosis.
[Anesthesia]
MAC, LMA.
[Description]
L mainstem stenosis (59%) id[REDACTED]. CRE balloon dilation performed (7-10mm). Patency improved to 66%.
[Plan]
Discharge same day. Repeat in 6 weeks."""

e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "bronchial stenosis", 1)},
    {"label": "LATERALITY", **get_span(t7, "L", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "59%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "7-10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "Patency improved to 66%", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_7", "text": t7, "entities": e7})


# ==========================================
# Note 8: 4369574_syn_8
# ==========================================
t8 = """[REDACTED] dilation of his post-TB bronchial stenosis. We used MAC anesthesia. The scope revealed a significant narrowing in the left mainstem bronchus. We utilized a CRE balloon to dilate the airway, holding the inflations for 90 seconds to ensure a good result. The airway caliber improved significantly. He tolerated the procedure well and was discharged home."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "dilation", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "bronchial stenosis", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "narrowing", 1)},
    {"label": "LATERALITY", **get_span(t8, "left", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "mainstem bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "dilate", 1)},
    {"label": "MEAS_TIME", **get_span(t8, "90 seconds", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "airway caliber improved significantly", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_8", "text": t8, "entities": e8})


# ==========================================
# Note 9: 4369574_syn_9
# ==========================================
t9 = """INDICATION: Post-TB airway constriction.
ACTION: Bronchoscopy with balloon widening.
FINDINGS: We found an eccentric narrowing in the left main bronchus. We used a CRE balloon to expand the lumen. We inflated to 7, 8, and 10mm. The passage opened up well. Minor oozing occurred. He is going home today."""

e9 = [
    {"label": "OBS_FINDING", **get_span(t9, "airway constriction", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "widening", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "narrowing", 1)},
    {"label": "LATERALITY", **get_span(t9, "left", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "main bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "expand", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "7", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "passage opened up well", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Minor oozing", 1)},
]
BATCH_DATA.append({"id": "4369574_syn_9", "text": t9, "entities": e9})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")