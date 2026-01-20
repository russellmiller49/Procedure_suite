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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Definitions (Batch)
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Note 1: 4376848_syn_1
# ------------------------------------------
id_1 = "4376848_syn_1"
text_1 = """Indication: BI stenosis post-intubation.
Procedure: Balloon dilation (31630).
- 8.0 ETT.
- BI stenosis 55%.
- CRE balloon: 6, 8, 10mm x 60s.
- Post: 26% residual.
- Minimal ooze.
Plan: Admit overnight. Decadron 10mg."""

entities_1 = [
    {"label": "ANAT_AIRWAY", **get_span(text_1, "BI", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "stenosis", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_1, "post-intubation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "ETT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "BI", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "55%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "6", 2)}, # "6" in "31630" is first, "6" in "6," is second
    {"label": "MEAS_SIZE", **get_span(text_1, "8", 2)}, # "8" in "8.0" is first
    {"label": "MEAS_SIZE", **get_span(text_1, "10mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "60s", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "26% residual", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Minimal ooze", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Decadron", 1)}
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ------------------------------------------
# Note 2: 4376848_syn_2
# ------------------------------------------
id_2 = "4376848_syn_2"
text_2 = """PROCEDURE REPORT: Therapeutic bronchoscopy for bronchus intermedius stenosis.
CLINICAL CONTEXT: 73-year-old female with history of prolonged intubation.
FINDINGS: Circumferential stenosis of the bronchus intermedius, 2 cm distal to the carina, with 55% luminal narrowing.
INTERVENTION: Serial balloon dilation utilizing a CRE catheter was performed to a maximum diameter of 10mm. Each inflation was maintained for 60 seconds.
RESULT: Immediate improvement in airway caliber to 74% patency. Minimal mucosal oozing observed."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "stenosis", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Circumferential stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchus intermedius", 2)},
    {"label": "MEAS_SIZE", **get_span(text_2, "2 cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "carina", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "55% luminal narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "CRE catheter", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "10mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_2, "60 seconds", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "74% patency", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Minimal mucosal oozing", 1)}
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ------------------------------------------
# Note 3: 4376848_syn_3
# ------------------------------------------
id_3 = "4376848_syn_3"
text_3 = """Service: Bronchoscopy with dilation (31630).
Site: Bronchus Intermedius.
Tool: CRE Balloon.
Process: Stenosis visualized (55%). Dilation performed at 6mm, 8mm, 10mm. Airway patency improved to 74%. Medical necessity: Symptomatic stenosis."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Bronchus Intermedius", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "CRE Balloon", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "Stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "55%", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "improved to 74%", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "stenosis", 1)}
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ------------------------------------------
# Note 4: 4376848_syn_4
# ------------------------------------------
id_4 = "4376848_syn_4"
text_4 = """Resident Note
Patient: [REDACTED]
Procedure: Balloon Dilation
Staff: Dr. S. Kim
Steps:
1. GA, ETT 8.0.
2. Scope to BI.
3. Stenosis found.
4. CRE balloon dilation x 2 cycles.
5. Good result.
Plan: Admit overnight."""

entities_4 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "ETT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "8.0", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "BI", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "dilation", 1)}, # Case sensitive: Dilation vs dilation
    {"label": "MEAS_COUNT", **get_span(text_4, "2", 2)} # "2" in step index vs count
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ------------------------------------------
# Note 5: 4376848_syn_5
# ------------------------------------------
id_5 = "4376848_syn_5"
text_5 = """jessica lopez 73 female post intubation stenosis in the bi. took her to or general anesthesia. saw the narrowing about halfway closed. used the cre balloon did 6 8 and 10 mm. held it for a minute each time. looks way better now. tiny bit of bleeding stopped on its own. admit for obs."""

entities_5 = [
    {"label": "CTX_HISTORICAL", **get_span(text_5, "post intubation", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "bi", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "narrowing", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "halfway closed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "cre balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "6", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "10 mm", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "minute", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "tiny bit of bleeding", 1)}
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ------------------------------------------
# Note 6: 4376848_syn_6
# ------------------------------------------
id_6 = "4376848_syn_6"
text_6 = """This 73-year-old female underwent bronchoscopy for post-intubation bronchus intermedius stenosis. Under general anesthesia, the stenosis was id[REDACTED] with 55% narrowing. A CRE balloon was used for dilation at 6mm, 8mm, and 10mm. The airway patency improved to 74%. Minimal mucosal oozing was noted. The patient was admitted for overnight observation."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoscopy", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_6, "post-intubation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "stenosis", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "55% narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "6mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "improved to 74%", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Minimal mucosal oozing", 1)}
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ------------------------------------------
# Note 7: 4376848_syn_7
# ------------------------------------------
id_7 = "4376848_syn_7"
text_7 = """[Indication]
Post-intubation bronchus intermedius stenosis.
[Anesthesia]
General, 8.0 ETT.
[Description]
BI stenosis (55%) id[REDACTED]. CRE balloon dilation performed (6-10mm). Patency improved to 74%.
[Plan]
Admit overnight. Repeat in 4 weeks."""

entities_7 = [
    {"label": "CTX_HISTORICAL", **get_span(text_7, "Post-intubation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "stenosis", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "8.0", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "ETT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "BI", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "55%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "6-10mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "Patency improved to 74%", 1)}
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ------------------------------------------
# Note 8: 4376848_syn_8
# ------------------------------------------
id_8 = "4376848_syn_8"
text_8 = """[REDACTED] for dilation of her bronchus intermedius stenosis. Under general anesthesia, we advanced the scope and found the narrowing. We used a CRE balloon to dilate the area, carefully increasing the size to 10mm. The airway opened up nicely. There was a tiny amount of oozing which stopped quickly. We admitted her for routine monitoring."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "narrowing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "CRE balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dilate", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "10mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "oozing", 1)}
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ------------------------------------------
# Note 9: 4376848_syn_9
# ------------------------------------------
id_9 = "4376848_syn_9"
text_9 = """INDICATION: Bronchus intermedius constriction.
PROCEDURE: Bronchoscopy with balloon stretching.
FINDINGS: We found a circumferential narrowing in the BI. We utilized a CRE balloon to widen the lumen. We cycled through 6, 8, and 10mm sizes. The passage caliber improved. Minor bleeding was seen. She will be hospitalized overnight."""

entities_9 = [
    {"label": "ANAT_AIRWAY", **get_span(text_9, "Bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "constriction", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "stretching", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "narrowing", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "BI", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "6", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "8", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "10mm", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "bleeding", 1)}
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)