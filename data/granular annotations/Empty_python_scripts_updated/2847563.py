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

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note: 2847563_syn_1
# ==========================================
case_2847563_syn_1_text = """Dx: LMS Carcinoid (40% block).
Anesthesia: GA, 7.5 ETT.
Action: Cryotherapy ablation (Erbe). 5 cycles (20s freeze).
Result: Tumor blanched/devitalized. Lumen stable.
Plan: D/C. Re-scope 6 wks."""
case_2847563_syn_1_entities = [
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_1_text, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_1_text, "Carcinoid", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(case_2847563_syn_1_text, "40% block", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_1_text, "Cryotherapy", 1)},
    {"label": "PROC_ACTION", **get_span(case_2847563_syn_1_text, "ablation", 1)},
    {"label": "MEAS_COUNT", **get_span(case_2847563_syn_1_text, "5 cycles", 1)},
    {"label": "MEAS_TIME", **get_span(case_2847563_syn_1_text, "20s", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_1_text, "blanched", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_1_text, "devitalized", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(case_2847563_syn_1_text, "Lumen stable", 1)},
    {"label": "MEAS_TIME", **get_span(case_2847563_syn_1_text, "6 wks", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_1", "text": case_2847563_syn_1_text, "entities": case_2847563_syn_1_entities})

# ==========================================
# Note: 2847563_syn_2
# ==========================================
case_2847563_syn_2_text = """PROCEDURE NOTE: The patient presented for management of a biopsied LMS carcinoid tumor. Under general anesthesia, the lesion was id[REDACTED] on the posterior wall, causing 40% obstruction. Cryotherapy was selected as the primary modality. Five freeze-thaw cycles were delivered circumferentially to the tumor base using an Erbe probe. Visual confirmation of tissue blanching and early necrosis was obtained. The airway remained patent with no immediate complications."""
case_2847563_syn_2_entities = [
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_2_text, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_2_text, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_2_text, "lesion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_2_text, "posterior wall", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(case_2847563_syn_2_text, "40% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_2_text, "Cryotherapy", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_2_text, "tumor", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(case_2847563_syn_2_text, "Erbe probe", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_2_text, "blanching", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_2_text, "necrosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(case_2847563_syn_2_text, "patent", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_2", "text": case_2847563_syn_2_text, "entities": case_2847563_syn_2_entities})

# ==========================================
# Note: 2847563_syn_3
# ==========================================
case_2847563_syn_3_text = """CPT: 31641 (Tumor destruction, cryotherapy).
Target: Left Mainstem Bronchus.
Pathology: Typical Carcinoid.
Technique: Flexible bronchoscopy with contact cryotherapy.
Dosimetry: 5 cycles, 20s freeze/10s thaw.
Outcome: Successful ablation/devitalization of tumor mass. No biopsy taken (prior dx)."""
case_2847563_syn_3_entities = [
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_3_text, "cryotherapy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_3_text, "Left Mainstem Bronchus", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_3_text, "Typical Carcinoid", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_3_text, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_3_text, "cryotherapy", 2)},
    {"label": "MEAS_COUNT", **get_span(case_2847563_syn_3_text, "5 cycles", 1)},
    {"label": "MEAS_TIME", **get_span(case_2847563_syn_3_text, "20s", 1)},
    {"label": "MEAS_TIME", **get_span(case_2847563_syn_3_text, "10s", 1)},
    {"label": "PROC_ACTION", **get_span(case_2847563_syn_3_text, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_3_text, "tumor", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_3", "text": case_2847563_syn_3_text, "entities": case_2847563_syn_3_entities})

# ==========================================
# Note: 2847563_syn_4
# ==========================================
case_2847563_syn_4_text = """Resident Note
Patient: [REDACTED]
Dx: LMS Carcinoid
Procedure: Cryo ablation
Steps:
1. GA, ETT.
2. Saw tumor in LMS (pink, vascular).
3. Used cryo probe.
4. Froze it 5 times.
5. Tumor turned white (dead).
6. No bleeding.
Plan: Home today, check back in 6 weeks."""
case_2847563_syn_4_entities = [
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_4_text, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_4_text, "Carcinoid", 1)},
    {"label": "PROC_ACTION", **get_span(case_2847563_syn_4_text, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_4_text, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_4_text, "LMS", 2)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_4_text, "pink", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_4_text, "vascular", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(case_2847563_syn_4_text, "No bleeding", 1)},
    {"label": "MEAS_TIME", **get_span(case_2847563_syn_4_text, "6 weeks", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_4", "text": case_2847563_syn_4_text, "entities": case_2847563_syn_4_entities})

# ==========================================
# Note: 2847563_syn_5
# ==========================================
case_2847563_syn_5_text = """Note for Maria C. Miller treating the carcinoid in the left main. General anesthesia. Saw the tumor about 40 percent block. Used the cryo probe on it did 5 freezes. Turned white looks dead. No bleeding really. She can go home today check it again in a month and a half."""
case_2847563_syn_5_entities = [
    {"label": "OBS_LESION", **get_span(case_2847563_syn_5_text, "tumor", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(case_2847563_syn_5_text, "No bleeding", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_5", "text": case_2847563_syn_5_text, "entities": case_2847563_syn_5_entities})

# ==========================================
# Note: 2847563_syn_6
# ==========================================
case_2847563_syn_6_text = """Flexible bronchoscopy with cryotherapy ablation of endobronchial tumor. 63 y/o female with LMS carcinoid tumor. LMS with polypoid tumor arising from posterior wall, 15mm in size, causing approximately 40% obstruction. Cryotherapy performed using Erbe cryoprobe: 5 freeze-thaw cycles applied circumferentially to tumor base. Visible blanching and early necrosis noted. Post-procedure: Tumor appears devitalized. Lumen maintained. No significant bleeding."""
case_2847563_syn_6_entities = [
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_6_text, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_6_text, "cryotherapy", 1)},
    {"label": "PROC_ACTION", **get_span(case_2847563_syn_6_text, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_6_text, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_6_text, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_6_text, "tumor", 2)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_6_text, "LMS", 2)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_6_text, "tumor", 3)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_6_text, "posterior wall", 1)},
    {"label": "MEAS_SIZE", **get_span(case_2847563_syn_6_text, "15mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(case_2847563_syn_6_text, "40% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_6_text, "Cryotherapy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(case_2847563_syn_6_text, "Erbe cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(case_2847563_syn_6_text, "5 freeze-thaw cycles", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_6_text, "tumor", 4)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_6_text, "blanching", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_6_text, "necrosis", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_6_text, "devitalized", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(case_2847563_syn_6_text, "Lumen maintained", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(case_2847563_syn_6_text, "No significant bleeding", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_6", "text": case_2847563_syn_6_text, "entities": case_2847563_syn_6_entities})

# ==========================================
# Note: 2847563_syn_7
# ==========================================
case_2847563_syn_7_text = """[Indication]
LMS Carcinoid tumor (40% obstruction).
[Anesthesia]
General, ETT 7.5.
[Description]
Cryotherapy ablation performed. 5 freeze-thaw cycles to tumor base. Tissue devitalized. No bleeding.
[Plan]
Discharge. Surveillance bronchoscopy 6 weeks."""
case_2847563_syn_7_entities = [
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_7_text, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_7_text, "Carcinoid", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_7_text, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(case_2847563_syn_7_text, "40% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_7_text, "Cryotherapy", 1)},
    {"label": "PROC_ACTION", **get_span(case_2847563_syn_7_text, "ablation", 1)},
    {"label": "MEAS_COUNT", **get_span(case_2847563_syn_7_text, "5 freeze-thaw cycles", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_7_text, "tumor", 2)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_7_text, "devitalized", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(case_2847563_syn_7_text, "No bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_7_text, "bronchoscopy", 1)},
    {"label": "MEAS_TIME", **get_span(case_2847563_syn_7_text, "6 weeks", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_7", "text": case_2847563_syn_7_text, "entities": case_2847563_syn_7_entities})

# ==========================================
# Note: 2847563_syn_8
# ==========================================
case_2847563_syn_8_text = """[REDACTED] A. Taylor came in for treatment of a carcinoid tumor in her left main airway. We used a freezing probe (cryotherapy) to treat the tumor without needing surgery. We applied the freezing cycles five times to the base of the tumor. We could see the tissue turn white, indicating the treatment was effective. She tolerated it well with no bleeding."""
case_2847563_syn_8_entities = [
    {"label": "OBS_LESION", **get_span(case_2847563_syn_8_text, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_8_text, "left main airway", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(case_2847563_syn_8_text, "freezing probe", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_8_text, "cryotherapy", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_8_text, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_8_text, "tumor", 3)},
]
BATCH_DATA.append({"id": "2847563_syn_8", "text": case_2847563_syn_8_text, "entities": case_2847563_syn_8_entities})

# ==========================================
# Note: 2847563_syn_9
# ==========================================
case_2847563_syn_9_text = """PREOPERATIVE DIAGNOSIS: Left mainstem endobronchial carcinoid tumor
PROCEDURE: Flexible bronchoscopy with cryotherapy destruction of endobronchial tumor
NARRATIVE: LMS with polypoid tumor arising from posterior wall. Cryotherapy performed using Erbe cryoprobe: 5 freeze-thaw cycles applied to tumor base. Visible blanching and early necrosis noted. Post-procedure: Tumor appears devitalized."""
case_2847563_syn_9_entities = [
    {"label": "OBS_LESION", **get_span(case_2847563_syn_9_text, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_9_text, "Flexible bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_9_text, "cryotherapy", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_9_text, "tumor", 2)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_9_text, "LMS", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_9_text, "tumor", 3)},
    {"label": "ANAT_AIRWAY", **get_span(case_2847563_syn_9_text, "posterior wall", 1)},
    {"label": "PROC_METHOD", **get_span(case_2847563_syn_9_text, "Cryotherapy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(case_2847563_syn_9_text, "Erbe cryoprobe", 1)},
    {"label": "MEAS_COUNT", **get_span(case_2847563_syn_9_text, "5 freeze-thaw cycles", 1)},
    {"label": "OBS_LESION", **get_span(case_2847563_syn_9_text, "tumor", 4)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_9_text, "blanching", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_9_text, "necrosis", 1)},
    {"label": "OBS_FINDING", **get_span(case_2847563_syn_9_text, "devitalized", 1)},
]
BATCH_DATA.append({"id": "2847563_syn_9", "text": case_2847563_syn_9_text, "entities": case_2847563_syn_9_entities})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)