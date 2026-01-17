import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

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

# ==========================================
# Note 1: 1917284_syn_1
# ==========================================
id_1 = "1917284_syn_1"
text_1 = """Indication: Migrated LMS stent.
Procedure: Rigid bronchoscopy with Stent Revision (31638).
- Stent found protruding into trachea.
- Granulation tissue debrided.
- Stent grasped and pushed distal into LMS.
- Position confirmed.
Patency restored."""

entities_1 = [
    # Indication: Migrated LMS stent
    {"label": "LMB", **get_span(text_1, "LMS", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 1)},
    
    # Procedure: Rigid bronchoscopy with Stent Revision
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Stent Revision", 1)},
    
    # Stent found protruding into trachea
    {"label": "DEV_STENT", **get_span(text_1, "Stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "trachea", 1)},
    
    # Granulation tissue debrided
    {"label": "OBS_LESION", **get_span(text_1, "Granulation tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "debrided", 1)},
    
    # Stent grasped and pushed distal into LMS
    {"label": "DEV_STENT", **get_span(text_1, "Stent", 2)},
    {"label": "LMB", **get_span(text_1, "LMS", 2)},
    
    # Patency restored
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "Patency restored", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1917284_syn_2
# ==========================================
id_2 = "1917284_syn_2"
text_2 = """OPERATIVE REPORT: Bronchoscopic Revision of Airway Prosthesis.
INDICATION: Dyspnea secondary to proximal migration of Left Mainstem Stent.
PROCEDURE: Rigid bronchoscopy revealed the Ultraflex stent extending into the distal trachea. Using rigid forceps, the prosthesis was mobilized. It was successfully repositioned distally into the left mainstem bronchus. Airway patency was fully restored, and the stent is now seated appropriately."""

entities_2 = [
    # Bronchoscopic Revision of Airway Prosthesis
    {"label": "PROC_ACTION", **get_span(text_2, "Bronchoscopic Revision", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "Airway Prosthesis", 1)},
    
    # Dyspnea secondary to proximal migration of Left Mainstem Stent
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_2, "Dyspnea", 1)},
    {"label": "LMB", **get_span(text_2, "Left Mainstem", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "Stent", 1)},
    
    # Rigid bronchoscopy revealed the Ultraflex stent extending into the distal trachea
    {"label": "PROC_METHOD", **get_span(text_2, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_2, "Ultraflex", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "trachea", 1)},
    
    # Using rigid forceps, the prosthesis was mobilized
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "rigid forceps", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "prosthesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "mobilized", 1)},
    
    # repositioned distally into the left mainstem bronchus
    {"label": "PROC_ACTION", **get_span(text_2, "repositioned", 1)},
    {"label": "LMB", **get_span(text_2, "left mainstem bronchus", 1)},
    
    # Airway patency was fully restored, and the stent...
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "Airway patency was fully restored", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "stent", 2)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1917284_syn_3
# ==========================================
id_3 = "1917284_syn_3"
text_3 = """Code: 31638 (Revision of tracheal/bronchial stent).
Target: Left Mainstem Bronchus.
Action: Repositioning of migrated SEMS.
Note: Includes debridement of granulation tissue facilitating the revision."""

entities_3 = [
    # Revision of tracheal/bronchial stent
    {"label": "PROC_ACTION", **get_span(text_3, "Revision", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "tracheal", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "stent", 1)},
    
    # Target: Left Mainstem Bronchus
    {"label": "LMB", **get_span(text_3, "Left Mainstem Bronchus", 1)},
    
    # Action: Repositioning of migrated SEMS
    {"label": "PROC_ACTION", **get_span(text_3, "Repositioning", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "SEMS", 1)},
    
    # debridement of granulation tissue
    {"label": "PROC_ACTION", **get_span(text_3, "debridement", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "granulation tissue", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1917284_syn_4
# ==========================================
id_4 = "1917284_syn_4"
text_4 = """Procedure: Stent Revision
Steps:
1. Rigid scope inserted.
2. Saw stent sticking out of LMS.
3. Cleaned up tissue.
4. Grabbed stent and pushed it back in.
5. Checked with flex scope, looks open."""

entities_4 = [
    # Stent Revision
    {"label": "DEV_STENT", **get_span(text_4, "Stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Revision", 1)},
    
    # Rigid scope inserted
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    
    # Saw stent sticking out of LMS
    {"label": "DEV_STENT", **get_span(text_4, "stent", 1)},
    {"label": "LMB", **get_span(text_4, "LMS", 1)},
    
    # Cleaned up tissue
    {"label": "OBS_LESION", **get_span(text_4, "tissue", 1)},
    
    # Grabbed stent
    {"label": "DEV_STENT", **get_span(text_4, "stent", 2)},
    
    # Checked with flex scope
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "flex scope", 1)}
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1917284_syn_5
# ==========================================
id_5 = "1917284_syn_5"
text_5 = """frank anderson has a stent in the left lung that moved up. went in with the rigid scope. saw it blocking the trachea a bit. grabbed it with the big forceps and shoved it back down where it belongs. looks good now breathing better."""

entities_5 = [
    # stent in the left lung
    {"label": "DEV_STENT", **get_span(text_5, "stent", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "left lung", 1)},
    
    # went in with the rigid scope
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "rigid scope", 1)},
    
    # blocking the trachea
    {"label": "ANAT_AIRWAY", **get_span(text_5, "trachea", 1)},
    
    # grabbed it with the big forceps
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    
    # breathing better
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_5, "breathing better", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1917284_syn_6
# ==========================================
id_6 = "1917284_syn_6"
text_6 = """Rigid bronchoscopy performed for migrated left mainstem stent. Stent found extending into trachea. Granulation tissue removed. Stent grasped and repositioned distally into proper position within the left mainstem. Airway patent."""

entities_6 = [
    # Rigid bronchoscopy performed for migrated left mainstem stent
    {"label": "PROC_METHOD", **get_span(text_6, "Rigid bronchoscopy", 1)},
    {"label": "LMB", **get_span(text_6, "left mainstem", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "stent", 1)},
    
    # Stent found extending into trachea
    {"label": "DEV_STENT", **get_span(text_6, "Stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "trachea", 1)},
    
    # Granulation tissue removed
    {"label": "OBS_LESION", **get_span(text_6, "Granulation tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "removed", 1)},
    
    # Stent grasped and repositioned distally into... left mainstem
    {"label": "DEV_STENT", **get_span(text_6, "Stent", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "repositioned", 1)},
    {"label": "LMB", **get_span(text_6, "left mainstem", 2)},
    
    # Airway patent
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "Airway patent", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1917284_syn_7
# ==========================================
id_7 = "1917284_syn_7"
text_7 = """[Indication]
Migrated LMS Stent, obstruction.
[Anesthesia]
General/Jet Ventilation.
[Description]
Stent protruding into trachea. Repositioned into LMS using rigid forceps. Granulation tissue treated.
[Plan]
PACU then home."""

entities_7 = [
    # Migrated LMS Stent
    {"label": "LMB", **get_span(text_7, "LMS", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "Stent", 1)},
    
    # obstruction
    {"label": "OBS_FINDING", **get_span(text_7, "obstruction", 1)},
    
    # Stent protruding into trachea
    {"label": "DEV_STENT", **get_span(text_7, "Stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "trachea", 1)},
    
    # Repositioned into LMS using rigid forceps
    {"label": "PROC_ACTION", **get_span(text_7, "Repositioned", 1)},
    {"label": "LMB", **get_span(text_7, "LMS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "rigid forceps", 1)},
    
    # Granulation tissue treated
    {"label": "OBS_LESION", **get_span(text_7, "Granulation tissue", 1)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1917284_syn_8
# ==========================================
id_8 = "1917284_syn_8"
text_8 = """[REDACTED] had slipped out of place and was blocking his windpipe. We put him to sleep and used a metal tube to reach the stent. We carefully grabbed it and moved it back down into the left lung's airway where it is supposed to be. His breathing passage is now wide open again."""

entities_8 = [
    # blocking his windpipe
    {"label": "OBS_FINDING", **get_span(text_8, "blocking", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "windpipe", 1)},
    
    # used a metal tube
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "metal tube", 1)},
    
    # reach the stent
    {"label": "DEV_STENT", **get_span(text_8, "stent", 1)},
    
    # moved it back down into the left lung's airway
    {"label": "PROC_ACTION", **get_span(text_8, "moved", 1)},
    {"label": "LMB", **get_span(text_8, "left lung's airway", 1)},
    
    # breathing passage is now wide open
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "breathing passage is now wide open", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1917284_syn_9
# ==========================================
id_9 = "1917284_syn_9"
text_9 = """Procedure: Readjustment of endobronchial prosthesis.
Issue: Proximal migration.
Action: The prosthesis was manipulated and reseated within the left mainstem bronchus. Patency was re-established."""

entities_9 = [
    # Readjustment of endobronchial prosthesis
    {"label": "PROC_ACTION", **get_span(text_9, "Readjustment", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "endobronchial prosthesis", 1)},
    
    # The prosthesis was manipulated and reseated
    {"label": "DEV_STENT", **get_span(text_9, "prosthesis", 2)},
    {"label": "PROC_ACTION", **get_span(text_9, "reseated", 1)},
    
    # left mainstem bronchus
    {"label": "LMB", **get_span(text_9, "left mainstem bronchus", 1)},
    
    # Patency was re-established
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "Patency was re-established", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)