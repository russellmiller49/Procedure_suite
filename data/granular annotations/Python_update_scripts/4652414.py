import sys
from pathlib import Path

# Set the repository root directory (assuming this script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the add_case utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback if running directly without package context, mainly for testing
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 4652414_syn_1
# ==========================================
t1 = """Indication: Post-PDT Debridement (96h).
Procedure: Bronchoscopy, Debridement.
Findings: Left Mainstem necrosis. 72% obstructed -> 7% post-debridement.
Tools: Rigid Coring, Suction, Forceps.
Specimen: None.
Plan: Surveillance 8 wks."""

e1 = [
    {"label": "CTX_HISTORICAL", **get_span(t1, "Post-PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Debridement", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Debridement", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Left Mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "necrosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "72% obstructed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "7% post-debridement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Rigid Coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 4652414_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Ms. [REDACTED] presented for debridement of the left mainstem bronchus 96 hours post-PDT. Examination revealed extensive necrosis consistent with an excellent therapeutic response. We utilized rigid coring, suction, and forceps to debulk the airway. The luminal obstruction was reduced from 72% to 7%, restoring ventilation to the left lung. No complications occurred."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "debridement", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "left mainstem bronchus", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t2, "post-PDT", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "necrosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "rigid coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "debulk", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "72%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "7%", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "left lung", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "No complications", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 4652414_syn_3
# ==========================================
t3 = """Procedure: 31641 (Debridement).
Site: Left Mainstem Bronchus (LMS).
Tools: Rigid coring, Suction, Forceps.
Indication: Post-PDT cleanup.
Result: 72% -> 7% obstruction.
Note: 96 hour interval appropriate for Temoporfin."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Debridement", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Left Mainstem Bronchus", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "LMS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Rigid coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Forceps", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t3, "Post-PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "cleanup", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t3, "72%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "7% obstruction", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 4652414_syn_4
# ==========================================
t4 = """Procedure: PDT Debridement
Pt: [REDACTED]
1. Intubation.
2. LMS visualization.
3. Debridement with coring/suction/forceps.
4. Airway clear.
5. Extubated.
Plan: F/u 8 weeks."""

e4 = [
    {"label": "CTX_HISTORICAL", **get_span(t4, "PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Debridement", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Intubation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "visualization", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Debridement", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "forceps", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "clear", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Extubated", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 4652414_syn_5
# ==========================================
t5 = """[REDACTED] 4 days after pdt left mainstem clean out used rigid coring and suction and forceps lots of junk in there got it all out airway looks good now 7 percent blocked patient ok"""

e5 = [
    {"label": "CTX_HISTORICAL", **get_span(t5, "pdt", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "left mainstem", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "clean out", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "junk", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "7 percent blocked", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 4652414_syn_6
# ==========================================
t6 = """96 hours following PDT, the left mainstem bronchus was debrided. Necrotic tissue was removed using rigid coring, suction catheter, and forceps. Obstruction was reduced from 72% to 7%. No biopsies were performed. The patient tolerated the procedure well."""

e6 = [
    {"label": "CTX_HISTORICAL", **get_span(t6, "PDT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "left mainstem bronchus", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "debrided", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "Necrotic tissue", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "rigid coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "suction catheter", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "72%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "7%", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsies", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 4652414_syn_7
# ==========================================
t7 = """[Indication]
Post-PDT Debridement (96h), LMS.
[Anesthesia]
General, 8.5 ETT.
[Description]
Necrosis removed from LMS using coring, suction, forceps. Airway patent. No biopsies.
[Plan]
Surveillance 8 weeks."""

e7 = [
    {"label": "CTX_HISTORICAL", **get_span(t7, "Post-PDT", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Debridement", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "LMS", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Necrosis", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "removed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "LMS", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "forceps", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "patent", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsies", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 4652414_syn_8
# ==========================================
t8 = """We performed the clean-up bronchoscopy for [REDACTED] left mainstem bronchus. It had been 4 days since the light treatment. We found a lot of debris and cleared it out using coring, suction, and forceps. The airway opened up beautifully, down to just 7% obstruction. She woke up fine and is breathing much better."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "clean-up", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "left mainstem bronchus", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t8, "light treatment", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "debris", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "suction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "7% obstruction", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t8, "breathing much better", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 4652414_syn_9
# ==========================================
t9 = """PROCEDURES: 1. Bronchoscopy with removal of necrotic tissue.
DETAILS: The LMS was inspected. Necrosis was substantial. Rigid coring and suction were used to clear the airway. Patency was restored. No samples were collected. The patient was awakened."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "removal", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "necrotic tissue", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "LMS", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Necrosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "Rigid coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "suction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "Patency was restored", 1)},
]
BATCH_DATA.append({"id": "4652414_syn_9", "text": t9, "entities": e9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)