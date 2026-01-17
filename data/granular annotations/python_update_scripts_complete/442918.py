import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

# Define the helper function for span extraction
def get_span(text, term, occurrence=1):
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
    return {"start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 442918_syn_1
# ==========================================
text_1 = """Indication: Migrated L main stent.
Proc: Stent Revision.
Findings: Stent proximal migration.
Action: Grasped w/ forceps, pushed distal. Balloon dilated 12mm.
Result: Stent re-centered. Good position.
Plan: Admit."""

entities_1 = [
    {"label": "ANAT_AIRWAY",       **get_span(text_1, "L main", 1)},
    {"label": "DEV_STENT",         **get_span(text_1, "stent", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "Stent Revision", 1)},
    {"label": "OBS_FINDING",       **get_span(text_1, "Stent proximal migration", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "forceps", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION",       **get_span(text_1, "dilated", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_1, "12mm", 1)},
    {"label": "OBS_FINDING",       **get_span(text_1, "Stent re-centered", 1)},
    {"label": "OBS_FINDING",       **get_span(text_1, "Good position", 1)},
]
BATCH_DATA.append({"id": "442918_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 442918_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: [REDACTED] symptomatic migration of a left mainstem bronchial stent. Under general anesthesia, bronchoscopy revealed the covered metal stent protruding into the distal trachea. The stent was manipulated distally using alligator forceps and repositioned into the appropriate anatomic location. Balloon dilation was performed to ensure apposition to the bronchial wall. The airway is now patent."""

entities_2 = [
    {"label": "OBS_FINDING",       **get_span(text_2, "migration", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_2, "left mainstem", 1)},
    {"label": "DEV_STENT",         **get_span(text_2, "stent", 1)},
    {"label": "PROC_METHOD",       **get_span(text_2, "bronchoscopy", 1)},
    {"label": "DEV_STENT_MATERIAL",**get_span(text_2, "covered metal", 1)},
    {"label": "DEV_STENT",         **get_span(text_2, "stent", 2)},
    {"label": "ANAT_AIRWAY",       **get_span(text_2, "trachea", 1)},
    {"label": "DEV_STENT",         **get_span(text_2, "stent", 3)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_2, "alligator forceps", 1)},
    {"label": "PROC_ACTION",       **get_span(text_2, "repositioned", 1)},
    {"label": "PROC_ACTION",       **get_span(text_2, "Balloon dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "patent", 1)},
]
BATCH_DATA.append({"id": "442918_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 442918_syn_3
# ==========================================
text_3 = """CPT Code: 31638 (Revision of tracheobronchial stent).
Detail: Existing stent was manipulated and repositioned (not removed/replaced). Balloon dilation (bundled) used to seat the stent. Fluoroscopy confirmed position. Meets criteria for revision."""

entities_3 = [
    {"label": "PROC_ACTION",       **get_span(text_3, "Revision", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_3, "tracheobronchial", 1)},
    {"label": "DEV_STENT",         **get_span(text_3, "stent", 1)},
    {"label": "DEV_STENT",         **get_span(text_3, "stent", 2)},
    {"label": "PROC_ACTION",       **get_span(text_3, "repositioned", 1)},
    {"label": "PROC_ACTION",       **get_span(text_3, "Balloon dilation", 1)},
    {"label": "DEV_STENT",         **get_span(text_3, "stent", 3)},
    {"label": "PROC_METHOD",       **get_span(text_3, "Fluoroscopy", 1)},
]
BATCH_DATA.append({"id": "442918_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 442918_syn_4
# ==========================================
text_4 = """Procedure: Stent Revision
Patient: [REDACTED]
1. ETT 8.0.
2. Scope inserted.
3. Stent migrated proximal.
4. Used forceps/snare to push it back.
5. Ballooned it (12mm).
6. Looks good now.
7. No bleeding."""

entities_4 = [
    {"label": "PROC_ACTION",       **get_span(text_4, "Stent Revision", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_4, "Scope", 1)},
    {"label": "DEV_STENT",         **get_span(text_4, "Stent", 1)},
    {"label": "OBS_FINDING",       **get_span(text_4, "migrated proximal", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_4, "forceps", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_4, "snare", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_4, "12mm", 1)},
]
BATCH_DATA.append({"id": "442918_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 442918_syn_5
# ==========================================
text_5 = """[REDACTED] his stent moved up into the trachea causing coughing. went in with the scope grabbed the edge of the stent and pushed it back down into the left main where it belongs. dilated it with a balloon so it sticks better. looks fine now no tumor growth just migration."""

entities_5 = [
    {"label": "DEV_STENT",         **get_span(text_5, "stent", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_5, "trachea", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_5, "scope", 1)},
    {"label": "DEV_STENT",         **get_span(text_5, "stent", 2)},
    {"label": "ANAT_AIRWAY",       **get_span(text_5, "left main", 1)},
    {"label": "PROC_ACTION",       **get_span(text_5, "dilated", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_5, "balloon", 1)},
    {"label": "OBS_LESION",        **get_span(text_5, "tumor", 1)},
    {"label": "OBS_FINDING",       **get_span(text_5, "migration", 1)},
]
BATCH_DATA.append({"id": "442918_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 442918_syn_6
# ==========================================
text_6 = """Flexible bronchoscopy performed for stent migration. The previously placed left mainstem stent was found to have migrated proximally. Using grasping instruments the stent was repositioned distally into the correct location. Balloon dilation was performed within the stent. Final inspection showed adequate patency and position. Patient tolerated well."""

entities_6 = [
    {"label": "PROC_METHOD",       **get_span(text_6, "Flexible bronchoscopy", 1)},
    {"label": "OBS_FINDING",       **get_span(text_6, "stent migration", 1)},
    {"label": "CTX_HISTORICAL",    **get_span(text_6, "previously", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_6, "left mainstem", 1)},
    {"label": "DEV_STENT",         **get_span(text_6, "stent", 2)},
    {"label": "OBS_FINDING",       **get_span(text_6, "migrated proximally", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_6, "grasping instruments", 1)},
    {"label": "DEV_STENT",         **get_span(text_6, "stent", 3)},
    {"label": "PROC_ACTION",       **get_span(text_6, "repositioned", 1)},
    {"label": "PROC_ACTION",       **get_span(text_6, "Balloon dilation", 1)},
    {"label": "DEV_STENT",         **get_span(text_6, "stent", 4)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "patency", 1)},
]
BATCH_DATA.append({"id": "442918_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 442918_syn_7
# ==========================================
text_7 = """[Indication]
Stent migration LMSB.
[Anesthesia]
General.
[Description]
Visualization: Stent proximal. Action: Repositioned distal using forceps. Balloon dilation 10-12mm. Position corrected.
[Plan]
Extubate. Obs."""

entities_7 = [
    {"label": "OBS_FINDING",       **get_span(text_7, "Stent migration", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_7, "LMSB", 1)},
    {"label": "DEV_STENT",         **get_span(text_7, "Stent", 1)},
    {"label": "PROC_ACTION",       **get_span(text_7, "Repositioned", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_7, "forceps", 1)},
    {"label": "PROC_ACTION",       **get_span(text_7, "Balloon dilation", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_7, "10-12mm", 1)},
]
BATCH_DATA.append({"id": "442918_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 442918_syn_8
# ==========================================
text_8 = """We took [REDACTED] OR to fix his lung stent. It had slipped up into his windpipe. We put him to sleep and used a scope to carefully push the stent back down into the left lung airway where it belongs. We used a balloon to widen it so it stays put. He is breathing better now."""

entities_8 = [
    {"label": "DEV_STENT",         **get_span(text_8, "stent", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_8, "windpipe", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_8, "scope", 1)},
    {"label": "DEV_STENT",         **get_span(text_8, "stent", 2)},
    {"label": "ANAT_AIRWAY",       **get_span(text_8, "left lung", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_8, "balloon", 1)},
    {"label": "OUTCOME_SYMPTOMS",  **get_span(text_8, "breathing better", 1)},
]
BATCH_DATA.append({"id": "442918_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 442918_syn_9
# ==========================================
text_9 = """Procedure: Repositioning of bronchial prosthesis.
Indication: Displacement of airway device.
Method: The device was mobilized and translocated to the target site using endoscopic tools. Radial expansion was applied to secure the device. 
Result: Restoration of airway architecture."""

entities_9 = [
    {"label": "PROC_ACTION",       **get_span(text_9, "Repositioning", 1)},
    {"label": "DEV_STENT",         **get_span(text_9, "bronchial prosthesis", 1)},
    {"label": "OBS_FINDING",       **get_span(text_9, "Displacement", 1)},
    {"label": "PROC_ACTION",       **get_span(text_9, "mobilized", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_9, "endoscopic tools", 1)},
]
BATCH_DATA.append({"id": "442918_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 442918 (Original)
# ==========================================
text_10 = """PATIENT: [REDACTED], 63-year-old Male
MRN: [REDACTED]
DATE OF PROCEDURE: [REDACTED]
PROCEDURE: Flexible bronchoscopy with bronchial stent revision (CPT 31638)
INDICATION: Symptomatic migration of left mainstem covered metal stent placed 4 months ago for malignant obstruction from non–small cell lung cancer.
ATTENDING PHYSICIAN: Dr. Priya Mehta
ASSISTANT: Dr. Alan Rivera (IP fellow)
ANESTHESIA: General anesthesia with endotracheal intubation
AIRWAY: 8.0 ETT

PROCEDURE DESCRIPTION:
After induction of general anesthesia, flexible bronchoscope was introduced through the ETT. A 12 x 40 mm covered metal stent was visualized in the left mainstem bronchus with proximal migration and approximately 30–40% overhang into the distal trachea.

Using alligator forceps and a snare, the stent was carefully mobilized distally and re-centered in the left mainstem bronchus under direct visualization. No new stent was placed. Balloon dilation (10–12 mm) was performed within the existing stent to improve apposition to the airway wall.

No tumor debulking, mechanical destruction, laser or APC was performed; the intervention was limited to revision/repositioning of the pre-existing stent and balloon dilation inside the stent.

FINDINGS:
- Malignant-appearing narrowing at distal left mainstem with prior stent in place
- Proximal stent migration successfully corrected with revision maneuvers

SPECIMENS: None
COMPLICATIONS: None; mild mucosal oozing controlled with cold saline.
DISPOSITION: Extubated in the OR, monitored in PACU then admitted to telemetry overnight."""

entities_10 = [
    {"label": "PROC_METHOD",       **get_span(text_10, "Flexible bronchoscopy", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "bronchial stent", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "revision", 1)},
    {"label": "OBS_FINDING",       **get_span(text_10, "migration", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "left mainstem", 1)},
    {"label": "DEV_STENT_MATERIAL",**get_span(text_10, "covered metal", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 2)},
    {"label": "OBS_LESION",        **get_span(text_10, "malignant obstruction", 1)},
    {"label": "OBS_LESION",        **get_span(text_10, "non–small cell lung cancer", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "flexible bronchoscope", 1)},
    {"label": "DEV_STENT_SIZE",    **get_span(text_10, "12 x 40 mm", 1)},
    {"label": "DEV_STENT_MATERIAL",**get_span(text_10, "covered metal", 2)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 3)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "left mainstem bronchus", 1)},
    {"label": "OBS_FINDING",       **get_span(text_10, "proximal migration", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "trachea", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "alligator forceps", 1)},
    {"label": "DEV_INSTRUMENT",    **get_span(text_10, "snare", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 4)},
    {"label": "PROC_ACTION",       **get_span(text_10, "mobilized", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "left mainstem bronchus", 2)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 5)},
    {"label": "PROC_ACTION",       **get_span(text_10, "Balloon dilation", 1)},
    {"label": "MEAS_SIZE",         **get_span(text_10, "10–12 mm", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 6)},
    {"label": "OBS_LESION",        **get_span(text_10, "tumor", 1)},
    {"label": "PROC_METHOD",       **get_span(text_10, "laser", 1)},
    {"label": "PROC_METHOD",       **get_span(text_10, "APC", 1)},
    {"label": "PROC_ACTION",       **get_span(text_10, "repositioning", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 7)},
    {"label": "PROC_ACTION",       **get_span(text_10, "balloon dilation", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 8)},
    {"label": "OBS_LESION",        **get_span(text_10, "Malignant-appearing narrowing", 1)},
    {"label": "ANAT_AIRWAY",       **get_span(text_10, "left mainstem", 2)},
    {"label": "CTX_HISTORICAL",    **get_span(text_10, "prior", 1)},
    {"label": "DEV_STENT",         **get_span(text_10, "stent", 9)},
    {"label": "OBS_FINDING",       **get_span(text_10, "Proximal stent migration", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "None", 2)},
    {"label": "OBS_FINDING",       **get_span(text_10, "mild mucosal oozing", 1)},
]
BATCH_DATA.append({"id": "442918", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)