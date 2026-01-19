import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
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
# Note 1: 2721803_syn_1
# ==========================================
t1 = """Indication: Esophageal ca, tracheal invasion.
Findings: 86% RMS obstruction.
Procedure:
- Rigid bronch, jet vent.
- Dilation.
- Novatech Silicone Dumon (20x30mm) placed in RMS.
Result: 21% residual.
Plan: Admit."""

e1 = [
    {"label": "OBS_LESION",                 **get_span(t1, "Esophageal ca", 1)},
    {"label": "OBS_LESION",                 **get_span(t1, "tracheal invasion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t1, "86% RMS obstruction", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t1, "RMS", 1)},
    {"label": "PROC_METHOD",                **get_span(t1, "Rigid bronch", 1)},
    {"label": "PROC_METHOD",                **get_span(t1, "jet vent", 1)},
    {"label": "PROC_ACTION",                **get_span(t1, "Dilation", 1)},
    {"label": "DEV_STENT",                  **get_span(t1, "Novatech Silicone Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t1, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t1, "20x30mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t1, "RMS", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t1, "21% residual", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 2721803_syn_2
# ==========================================
t2 = """HISTORY: [REDACTED], with a history of esophageal carcinoma and tracheal invasion, presented with 86% stenosis of the right mainstem (RMS).
PROCEDURE: General anesthesia with jet ventilation was established. Rigid bronchoscopy visualized the stenosis. Following mechanical dilation, a 20x30mm Novatech Silicone Dumon stent was deployed. The stent maintained airway patency against the extrinsic compression, resulting in a residual obstruction of 21%.
OUTCOME: Satisfactory stent placement."""

e2 = [
    {"label": "OBS_LESION",                 **get_span(t2, "esophageal carcinoma", 1)},
    {"label": "OBS_LESION",                 **get_span(t2, "tracheal invasion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t2, "86% stenosis of the right mainstem (RMS)", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "right mainstem", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t2, "RMS", 1)},
    {"label": "PROC_METHOD",                **get_span(t2, "jet ventilation", 1)},
    {"label": "PROC_METHOD",                **get_span(t2, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION",                 **get_span(t2, "stenosis", 2)},
    {"label": "PROC_ACTION",                **get_span(t2, "mechanical dilation", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t2, "20x30mm", 1)},
    {"label": "DEV_STENT",                  **get_span(t2, "Novatech Silicone Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t2, "Silicone", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t2, "residual obstruction of 21%", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 2721803_syn_3
# ==========================================
t3 = """Procedure: Bronchoscopy with Stent (31636).
Device: Novatech Silicone Dumon (20x30mm).
Location: Right Mainstem Bronchus.
Indication: Extrinsic compression from Esophageal Cancer (86%).
Technique: Rigid bronchoscopy, balloon dilation, stent deployment.
Outcome: Patent airway (21% residual)."""

e3 = [
    {"label": "PROC_ACTION",                **get_span(t3, "Bronchoscopy", 1)},
    {"label": "DEV_STENT",                  **get_span(t3, "Novatech Silicone Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t3, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t3, "20x30mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t3, "Right Mainstem Bronchus", 1)},
    {"label": "OBS_LESION",                 **get_span(t3, "Esophageal Cancer", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t3, "86%", 1)},
    {"label": "PROC_METHOD",                **get_span(t3, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t3, "balloon dilation", 1)},
    {"label": "PROC_ACTION",                **get_span(t3, "stent deployment", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t3, "21% residual", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 2721803_syn_4
# ==========================================
t4 = """Procedure: RMS Stent Placement
Patient: [REDACTED]teps:
1. GA/Jet ventilation.
2. Rigid scope inserted.
3. RMS stenosis (86%) dilated.
4. Dumon stent 20x30mm placed.
5. Confirmed position.
Complications: None.
Plan: Admit."""

e4 = [
    {"label": "ANAT_AIRWAY",                **get_span(t4, "RMS", 1)},
    {"label": "PROC_ACTION",                **get_span(t4, "Stent Placement", 1)},
    {"label": "PROC_METHOD",                **get_span(t4, "Jet ventilation", 1)},
    {"label": "DEV_INSTRUMENT",             **get_span(t4, "Rigid scope", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t4, "RMS", 2)},
    {"label": "OBS_LESION",                 **get_span(t4, "stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t4, "86%", 1)},
    {"label": "PROC_ACTION",                **get_span(t4, "dilated", 1)},
    {"label": "DEV_STENT",                  **get_span(t4, "Dumon stent", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t4, "20x30mm", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 2721803_syn_5
# ==========================================
t5 = """Lisa Rivera here for RMS stent she has esophageal cancer pushing in. Blocked 86 percent. We did the rigid bronch with jet vent dilated it open then put in a silicone dumon stent 20 by 30. Opened up to about 21 percent blocked. No bleeding. She goes to the floor."""

e5 = [
    {"label": "ANAT_AIRWAY",                **get_span(t5, "RMS", 1)},
    {"label": "DEV_STENT",                  **get_span(t5, "stent", 1)},
    {"label": "OBS_LESION",                 **get_span(t5, "esophageal cancer", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t5, "Blocked 86 percent", 1)},
    {"label": "PROC_METHOD",                **get_span(t5, "rigid bronch", 1)},
    {"label": "PROC_METHOD",                **get_span(t5, "jet vent", 1)},
    {"label": "PROC_ACTION",                **get_span(t5, "dilated", 1)},
    {"label": "DEV_STENT",                  **get_span(t5, "silicone dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t5, "silicone", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t5, "20 by 30", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t5, "21 percent blocked", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 2721803_syn_6
# ==========================================
t6 = """Indication: Esophageal cancer with tracheal invasion, ~86% Right mainstem obstruction. Under general anesthesia with jet ventilation, rigid bronchoscopy was performed. Sequential balloon dilation of RMS stenosis performed. Airway measured and Novatech Silicone - Dumon stent (20x30mm) deployed in Right mainstem. Stent position confirmed with good expansion and patency. Post-procedure obstruction was ~21%. No complications. EBL minimal."""

e6 = [
    {"label": "OBS_LESION",                 **get_span(t6, "Esophageal cancer", 1)},
    {"label": "OBS_LESION",                 **get_span(t6, "tracheal invasion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t6, "~86% Right mainstem obstruction", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t6, "Right mainstem", 1)},
    {"label": "PROC_METHOD",                **get_span(t6, "jet ventilation", 1)},
    {"label": "PROC_METHOD",                **get_span(t6, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t6, "balloon dilation", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t6, "RMS", 1)},
    {"label": "OBS_LESION",                 **get_span(t6, "stenosis", 1)},
    {"label": "DEV_STENT",                  **get_span(t6, "Novatech Silicone - Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t6, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t6, "20x30mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t6, "Right mainstem", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t6, "obstruction was ~21%", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 2721803_syn_7
# ==========================================
t7 = """[Indication]
Esophageal cancer, 86% RMS obstruction.
[Anesthesia]
General, Jet Ventilation.
[Description]
RMS dilated. Novatech Dumon stent (20x30mm) deployed. Residual obstruction 21%.
[Plan]
Admit. Follow up 4-6 weeks."""

e7 = [
    {"label": "OBS_LESION",                 **get_span(t7, "Esophageal cancer", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t7, "86% RMS obstruction", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t7, "RMS", 1)},
    {"label": "PROC_METHOD",                **get_span(t7, "Jet Ventilation", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t7, "RMS", 2)},
    {"label": "PROC_ACTION",                **get_span(t7, "dilated", 1)},
    {"label": "DEV_STENT",                  **get_span(t7, "Novatech Dumon stent", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t7, "20x30mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t7, "Residual obstruction 21%", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 2721803_syn_8
# ==========================================
t8 = """[REDACTED] a stent for her right mainstem bronchus, which was being compressed by her esophageal cancer. Under general anesthesia, we dilated the 86% stenosis and deployed a 20x30mm Novatech Silicone Dumon stent. The stent held the airway open well, leaving a residual narrowing of about 21%. She did well and was admitted for observation."""

e8 = [
    {"label": "DEV_STENT",                  **get_span(t8, "stent", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t8, "right mainstem bronchus", 1)},
    {"label": "OBS_LESION",                 **get_span(t8, "esophageal cancer", 1)},
    {"label": "PROC_ACTION",                **get_span(t8, "dilated", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t8, "86% stenosis", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t8, "20x30mm", 1)},
    {"label": "DEV_STENT",                  **get_span(t8, "Novatech Silicone Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t8, "Silicone", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t8, "residual narrowing of about 21%", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 2721803_syn_9
# ==========================================
t9 = """Indication: Esophageal cancer with tracheal incursion.
Pre-procedure occlusion: ~86% Right mainstem.
PROCEDURE: Under general anesthesia with jet ventilation, rigid bronchoscopy was conducted. Sequential balloon expansion of RMS narrowing was done. The airway was sized and a Novatech Silicone - Dumon stent (20x30mm) was installed in the Right mainstem. Stent location was verified with good expansion and flow.
Post-procedure occlusion: ~21%.
No adverse events."""

e9 = [
    {"label": "OBS_LESION",                 **get_span(t9, "Esophageal cancer", 1)},
    {"label": "OBS_LESION",                 **get_span(t9, "tracheal incursion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t9, "occlusion: ~86% Right mainstem", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t9, "Right mainstem", 1)},
    {"label": "PROC_METHOD",                **get_span(t9, "jet ventilation", 1)},
    {"label": "PROC_METHOD",                **get_span(t9, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t9, "balloon expansion", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t9, "RMS", 1)},
    {"label": "OBS_LESION",                 **get_span(t9, "narrowing", 1)},
    {"label": "DEV_STENT",                  **get_span(t9, "Novatech Silicone - Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t9, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t9, "20x30mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t9, "Right mainstem", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t9, "occlusion: ~21%", 1)},
]
BATCH_DATA.append({"id": "2721803_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 2721803
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: LCDR John Park, MD
Fellow: LT Michelle Torres, MD (PGY-5)

Indication: Esophageal cancer with tracheal invasion
Pre-procedure obstruction: ~86% Right mainstem

PROCEDURE:
Under general anesthesia with jet ventilation, rigid bronchoscopy performed.
Sequential balloon dilation of RMS stenosis performed.
Airway measured and Novatech Silicone - Dumon stent (20x30mm) deployed in Right mainstem.
Stent position confirmed with good expansion and patency.
Post-procedure obstruction: ~21%
No complications. EBL minimal.

DISPOSITION: Recovery then floor admission for overnight observation.
F/U: Clinic in 4-6 weeks with repeat bronchoscopy.

Park, MD"""

e10 = [
    {"label": "OBS_LESION",                 **get_span(t10, "Esophageal cancer", 1)},
    {"label": "OBS_LESION",                 **get_span(t10, "tracheal invasion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE",   **get_span(t10, "obstruction: ~86% Right mainstem", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "Right mainstem", 1)},
    {"label": "PROC_METHOD",                **get_span(t10, "jet ventilation", 1)},
    {"label": "PROC_METHOD",                **get_span(t10, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",                **get_span(t10, "balloon dilation", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "RMS", 1)},
    {"label": "OBS_LESION",                 **get_span(t10, "stenosis", 1)},
    {"label": "DEV_STENT",                  **get_span(t10, "Novatech Silicone - Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL",         **get_span(t10, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE",             **get_span(t10, "20x30mm", 1)},
    {"label": "ANAT_AIRWAY",                **get_span(t10, "Right mainstem", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST",  **get_span(t10, "obstruction: ~21%", 1)},
    {"label": "OUTCOME_COMPLICATION",       **get_span(t10, "No complications", 1)},
]
BATCH_DATA.append({"id": "2721803", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)