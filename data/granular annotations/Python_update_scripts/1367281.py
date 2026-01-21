import sys
from pathlib import Path

# Set up the repository root directory
# This logic assumes the script is run from within the repository structure
# or allows manual definition if needed.
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path(".").resolve()

# Add the scripts directory to the system path to import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search.
        term (str): The term to find.
        occurrence (int): The occurrence number (1-based).
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None # Term not found enough times
            
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1367281_syn_1
# ==========================================
t1 = """Procedure: Flex Bronch, Tracheal Dilation.
- Dx: Post-intubation stenosis (Subglottic).
- Action: CRE Balloon (8-12mm). 3 inflations.
- Result: Patency increased 40% -> 75%.
- Plan: IV Decadron, Obs overnight."""

e1 = [
    {"label": "PROC_ACTION", **get_span(t1, "Bronch", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Tracheal", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Dilation", 1)},
    {"label": "OBS_LESION", **get_span(t1, "stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Subglottic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "CRE Balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "8-12mm", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "40%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "75%", 1)},
    {"label": "MEDICATION", **get_span(t1, "Decadron", 1)},
]
BATCH_DATA.append({"id": "1367281_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1367281_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: The patient presented with symptomatic tracheal stenosis. Flexible bronchoscopy revealed a circumferential cicatricial stenosis 3cm distal to the vocal cords. Balloon dilation was performed using a CRE balloon with serial inflations up to 12mm. Post-intervention, the airway lumen was significantly improved. No immediate restenosis or significant bleeding was observed."""

e2 = [
    {"label": "ANAT_AIRWAY", **get_span(t2, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t2, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Flexible bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t2, "stenosis", 2)},
    {"label": "MEAS_SIZE", **get_span(t2, "3cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "vocal cords", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "12mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "airway lumen", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "significantly improved", 1)},
]
BATCH_DATA.append({"id": "1367281_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1367281_syn_3
# ==========================================
t3 = """CPT: 31630 (Bronchoscopy with dilation). Diagnosis: Tracheal Stenosis (J95.5). Technique: Balloon dilation via flexible scope. Anesthesia: General."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t3, "Stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "dilation", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "flexible scope", 1)},
]
BATCH_DATA.append({"id": "1367281_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1367281_syn_4
# ==========================================
t4 = """Procedure: Bronch w/ Balloon Dilation
1. GA.
2. Scope down. Stenosis seen below cords.
3. Balloon up: 8mm, 10mm, 12mm.
4. Airway looks much better (75% open).
5. No bleeding.
Plan: Admit for airway watch."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Bronch", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Scope", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "cords", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Balloon", 2)},
    {"label": "MEAS_SIZE", **get_span(t4, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "10mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "12mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "75%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "airway", 1)}, # Fixed: Changed occurrence from 2 to 1 (Capital 'Airway' is handled separately)
]
BATCH_DATA.append({"id": "1367281_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1367281_syn_5
# ==========================================
t5 = """bronchoscopy for roberto garcia tracheal stenosis. used the cre balloon to dilate it. went up to 12mm. opened up pretty good from 40 percent to 75 percent. gave some dexamethasone. watching him overnight."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t5, "stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "cre balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "dilate", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "12mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "40 percent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "75 percent", 1)},
    {"label": "MEDICATION", **get_span(t5, "dexamethasone", 1)},
]
BATCH_DATA.append({"id": "1367281_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1367281_syn_6
# ==========================================
t6 = """Flexible bronchoscopy and balloon dilation were performed for post-intubation tracheal stenosis. Findings included circumferential narrowing 3cm below cords. Serial dilations with CRE balloon up to 12mm were performed. Patency improved to 75 percent. No complications occurred. The patient was admitted for monitoring."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Flexible bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t6, "stenosis", 1)},
    {"label": "OBS_LESION", **get_span(t6, "narrowing", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "3cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "cords", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "dilations", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "12mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "75 percent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)},
]
BATCH_DATA.append({"id": "1367281_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1367281_syn_7
# ==========================================
t7 = """[Indication]
Tracheal Stenosis.
[Anesthesia]
General.
[Description]
Flexible bronchoscopy. Balloon dilation (8mm-12mm). Stenosis relieved.
[Plan]
Overnight observation."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Flexible bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "dilation", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "8mm-12mm", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Stenosis", 2)},
]
BATCH_DATA.append({"id": "1367281_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1367281_syn_8
# ==========================================
t8 = """We brought [REDACTED] OR to address his tracheal stenosis. Using a flexible bronchoscope, we id[REDACTED] the narrowed segment and used a balloon catheter to dilate it. We performed three inflations, gradually increasing the size to 12mm. The airway opened up significantly, and he tolerated the procedure well. We'll keep him overnight to ensure no swelling develops."""

e8 = [
    {"label": "ANAT_AIRWAY", **get_span(t8, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t8, "stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "flexible bronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(t8, "narrowed segment", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "balloon catheter", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "dilate", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "three", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "12mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "opened up significantly", 1)},
]
BATCH_DATA.append({"id": "1367281_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1367281_syn_9
# ==========================================
t9 = """Procedure: Endoscopic airway dilation.
Pathology: Cicatricial tracheal stenosis.
Method: Radial expansion via balloon catheter.
Outcome: Restoration of luminal caliber."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Endoscopic", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "airway", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "dilation", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Cicatricial tracheal stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "balloon catheter", 1)},
]
BATCH_DATA.append({"id": "1367281_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1367281
# ==========================================
t10 = """PT: [REDACTED] | 52M | MRN [REDACTED]
DATE: [REDACTED]
PROVIDER: Dr. K. Patel
INDICATION:

Post-intubation tracheal stenosis
Location: [REDACTED]
Baseline stridor with dyspnea on exertion

PROCEDURE: Flexible bronchoscopy + Balloon dilation (CPT 31630)
SEDATION: Propofol/fentanyl (general anesthesia)
FINDINGS:

Vocal cords: normal mobility
Tracheal stenosis at 3cm below glottis
Pre-dilation: ~40% luminal narrowing, circumferential scar tissue
Length: approximately 1.5cm
No active inflammation or granulation

INTERVENTION:

CRE balloon (8mm x 4cm) advanced to stenosis site
Serial dilations performed:

8mm × 60 seconds
10mm × 60 seconds
12mm × 90 seconds (max size)


Total 3 inflations
Post-dilation patency improved to ~75%
Minimal mucosal tearing, no significant bleeding
Topical epinephrine 1:10,000 applied (5mL)

SPECIMENS: None
COMPLICATIONS: None
DISPOSITION:

Extubated in OR, stable
Dexamethasone 10mg IV given
Admit overnight for monitoring
F/u flexible scope in 4 weeks
May need repeat dilation vs stent if restenosis occurs

PLAN:
→ Repeat dilation in 4-6 weeks
→ Consider stent if <3 successful dilations
→ ENT referral for surgical evaluation"""

e10 = [
    {"label": "ANAT_AIRWAY", **get_span(t10, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t10, "stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "dilation", 1)},
    {"label": "MEDICATION", **get_span(t10, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(t10, "fentanyl", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Vocal cords", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t10, "stenosis", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "3cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "glottis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "~40%", 1)},
    {"label": "OBS_LESION", **get_span(t10, "narrowing", 1)},
    {"label": "OBS_LESION", **get_span(t10, "scar tissue", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.5cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "CRE balloon", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "8mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "4cm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "stenosis", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "dilations", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "8mm", 2)},
    {"label": "MEAS_TIME", **get_span(t10, "60 seconds", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "10mm", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "60 seconds", 2)},
    {"label": "MEAS_SIZE", **get_span(t10, "12mm", 1)},
    {"label": "MEAS_TIME", **get_span(t10, "90 seconds", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "~75%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no significant bleeding", 1)},
    {"label": "MEDICATION", **get_span(t10, "epinephrine", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "None", 1)},
    {"label": "MEDICATION", **get_span(t10, "Dexamethasone", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "flexible scope", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "dilation", 2)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 1)},
    {"label": "OBS_LESION", **get_span(t10, "restenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "dilation", 3)},
    {"label": "DEV_STENT", **get_span(t10, "stent", 2)},
]
BATCH_DATA.append({"id": "1367281", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)