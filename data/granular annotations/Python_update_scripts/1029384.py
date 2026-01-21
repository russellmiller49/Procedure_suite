import sys
from pathlib import Path

# Set up REPO_ROOT dynamically based on script location
# Assuming this script is located in a subdirectory of the repo (e.g., /scripts/batches/)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 1029384_syn_1
# ==========================================
text_1 = """Indication: RUL SCC obstruction (80%). Palliative.
Anesthesia: GA, Rigid.
Action: Cryotherapy (Erbe). 7 cycles (30s each) to RUL/BI tumor.
Result: Necrosis/Debridement. RUL 50% open, BI 80% open.
Complications: Mod bleeding (controlled).
Plan: Repeat 1 week. Rad Onc consult."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "SCC", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "obstruction (80%)", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cryotherapy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Erbe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7 cycles", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "30s", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "BI", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Necrosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Debridement", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RUL", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "50% open", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "BI", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "80% open", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "bleeding (controlled)", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1029384_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: The patient presented with advanced squamous cell carcinoma causing critical RUL obstruction. Under general anesthesia via rigid bronchoscopy, a large exophytic tumor was visualized occluding 80% of the RUL and extending into the bronchus intermedius. Cryotherapeutic ablation was executed using an Erbe flexible probe. Multiple freeze-thaw cycles were applied to the tumor surface. Necrotic tissue was mechanically debrided. Hemostasis was achieved following moderate hemorrhage. Luminal patency was significantly improved."""

entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "squamous cell carcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "exophytic tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "occluding 80%", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RUL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchus intermedius", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Cryotherapeutic ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Erbe flexible probe", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
    {"label": "OBS_FINDING", **get_span(text_2, "Necrotic tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "debrided", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "hemorrhage", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "Luminal patency was significantly improved", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1029384_syn_3
# ==========================================
text_3 = """CPT: 31641 (Tumor destruction via cryotherapy).
Method: Rigid bronchoscopy with cryo-ablation.
Target: RUL and Bronchus Intermedius.
Details:
- Tumor debulking performed.
- 7 freeze-thaw cycles utilized.
- Mechanical debridement of necrotic tissue.
- Hemostasis managed (EBL 75ml).
Outcome: Relief of obstruction (RUL 80%->50% block)."""

entities_3 = [
    {"label": "OBS_LESION", **get_span(text_3, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "cryotherapy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "cryo-ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Bronchus Intermedius", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "debulking", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "7", 2)},  # '31641' contains '1', so '7' is safe
    {"label": "PROC_ACTION", **get_span(text_3, "Mechanical debridement", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "necrotic tissue", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3, "Hemostasis managed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "Relief of obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RUL", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "80%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "50% block", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1029384_syn_4
# ==========================================
text_4 = """Resident Note
Patient: [REDACTED] Reyes
Dx: RUL SCC tumor
Procedure: Cryo debulking
Steps:
1. GA, Rigid scope.
2. Big tumor in RUL/BI.
3. Used cryo probe to freeze it (7 cycles).
4. Pulled out dead tissue.
5. Bleeding controlled with cold saline.
6. Airway looks better.
Plan: Do it again next week."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "SCC tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Cryo debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "tumor", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RUL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "BI", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "cryo probe", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "7 cycles", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "dead tissue", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "Bleeding controlled", 1)},
    {"label": "MEDICATION", **get_span(text_4, "cold saline", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "Airway looks better", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1029384_syn_5
# ==========================================
text_5 = """Procedure for Manuel O. Morales palliative debulking for the cancer. Rigid bronchoscopy general anesthesia. Big tumor blocking the right upper lobe. Used the cryo probe froze it a bunch of times about 30 seconds each. Pulled out the dead pieces. Some bleeding about 75cc but stopped it with epinephrine. Got the airway open a bit more. Will bring him back next week for more."""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "debulking", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "cancer", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "right upper lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "cryo probe", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "30 seconds", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "bleeding", 1)},
    {"label": "MEDICATION", **get_span(text_5, "epinephrine", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "airway open a bit more", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1029384_syn_6
# ==========================================
text_6 = """Rigid bronchoscopy with cryotherapy ablation. 66 y/o male with advanced squamous cell lung cancer. Progressive dyspnea with near-complete RUL obstruction. Large exophytic tumor at RUL orifice causing 80% obstruction with extension into bronchus intermedius. Cryotherapy performed using Erbe Erbokryo CA unit with flexible cryoprobe. Multiple freeze-thaw cycles applied to tumor surface. Significant tumor necrosis achieved. Necrotic tissue debrided with rigid suction. Post-procedure patency improved to approximately 50% at RUL, BI now 80% patent."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "cryotherapy ablation", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "squamous cell lung cancer", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "exophytic tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL orifice", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "80% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "bronchus intermedius", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Cryotherapy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Erbe Erbokryo CA unit", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "flexible cryoprobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "tumor necrosis", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Necrotic tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "debrided", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "rigid suction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "patency improved to approximately 50%", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RUL", 3)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "BI", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "80% patent", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1029384_syn_7
# ==========================================
text_7 = """[Indication]
Malignant airway obstruction (SCC), RUL (80%).
[Anesthesia]
General, Rigid Bronchoscopy.
[Description]
Cryotherapy ablation performed (7 cycles, 30s). Necrotic tissue debrided. RUL patency improved to 50%, BI to 80%. Moderate bleeding controlled.
[Plan]
Repeat bronchoscopy 1 week. Rad Onc consult."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Malignant airway obstruction", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "SCC", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "80%", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Cryotherapy ablation", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "7 cycles", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "30s", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Necrotic tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "debrided", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RUL", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "patency improved to 50%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "BI", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "80%", 2)}, # 1st 80% was RUL pre.
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "bleeding controlled", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1029384_syn_8
# ==========================================
text_8 = """We performed a palliative procedure on [REDACTED] E. Chavez to clear the tumor blocking his right lung. Using a rigid bronchoscope, we applied freezing therapy (cryotherapy) to the tumor mass in the right upper lobe. This killed the surface tissue which we then removed. We managed to open the airway significantly, though some blockage remains. There was some bleeding which we controlled during the case."""

entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "rigid bronchoscope", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "freezing therapy", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "cryotherapy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor mass", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right upper lobe", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "open the airway significantly", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "bleeding", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1029384_syn_9
# ==========================================
text_9 = """PRE-OP DX: Endobronchial squamous cell carcinoma, RUL with 80% obstruction
PROCEDURE: Rigid bronchoscopy with cryotherapy destruction
DETAILS: Large exophytic tumor at RUL orifice. Cryotherapy performed using Erbe unit. Multiple freeze-thaw cycles applied. Significant tumor necrosis achieved. Necrotic tissue extracted with rigid suction. Post-procedure patency improved. Moderate hemorrhage controlled."""

entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "Endobronchial squamous cell carcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_9, "80% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "cryotherapy destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "exophytic tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RUL orifice", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Cryotherapy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Erbe unit", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "tumor necrosis", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Necrotic tissue", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "rigid suction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "patency improved", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "hemorrhage controlled", 1)}
]
BATCH_DATA.append({"id": "1029384_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)