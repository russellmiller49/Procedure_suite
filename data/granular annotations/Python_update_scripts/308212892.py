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

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 308212892_syn_1
# ==========================================
text_1 = """Indication: Extrinsic compression L mainstem (Esophageal CA).
Proc: Bronchoscopy + Stent.
Findings: L mainstem 90% obstructed.
Action: Dilated. Aero stent (12x40mm) placed. Balloon dilated post-deployment.
Result: Airway patent (80%).
Plan: Nebs, humidified O2."""

entities_1 = [
    {"label": "OBS_FINDING", **get_span(text_1, "Extrinsic compression", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "L mainstem", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Esophageal CA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "L mainstem", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "90% obstructed", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Dilated", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "Aero stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_1, "12x40mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilated", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "Airway patent (80%)", 1)},
    {"label": "MEDICATION", **get_span(text_1, "humidified O2", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 308212892_syn_2
# ==========================================
text_2 = """OPERATIVE SUMMARY: Ms. [REDACTED] presented with critical left mainstem bronchus stenosis secondary to extrinsic esophageal carcinoma. Rigid bronchoscopy was utilized to secure the airway. A 12x40mm Aero tracheobronchial stent was deployed across the stenosis under fluoroscopic guidance. Subsequent balloon dilation resulted in significant restoration of airway patency."""

entities_2 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "critical left mainstem bronchus stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "left mainstem bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "esophageal carcinoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_2, "12x40mm", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "Aero tracheobronchial stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "deployed", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "fluoroscopic guidance", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "significant restoration of airway patency", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 308212892_syn_3
# ==========================================
text_3 = """Billing: 31636 (Bronchoscopy with placement of bronchial stent, initial bronchus). Site: Left Mainstem Bronchus. Device: Aero Stent. Fluoroscopy used for positioning. Dilation bundled."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "placement of bronchial stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Left Mainstem Bronchus", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "Aero Stent", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Dilation", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 308212892_syn_4
# ==========================================
text_4 = """Procedure: Rigid Bronch + Stent
Patient: [REDACTED]
1. General Anesthesia.
2. Rigid scope inserted.
3. L mainstem tight (90%).
4. Guidewire passed.
5. Deployed 12x40mm Aero stent.
6. Ballooned it open.
7. Airway looks much better."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "inserted", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "L mainstem", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_4, "tight (90%)", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Guidewire", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "passed", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Deployed", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_4, "12x40mm", 1)},
    {"label": "DEV_STENT", **get_span(text_4, "Aero stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Ballooned", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "Airway looks much better", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 308212892_syn_5
# ==========================================
text_5 = """tena hughes esophageal cancer pushing on the airway left side strictly closed off almost completely. we went in with the rigid scope couldn't ventilate well so intubated. put a wire down marked it with paper clips on the chest. slid the aero stent in 12 by 40. ballooned it open. looks way better now like 80 percent open."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "esophageal cancer", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "strictly closed off almost completely", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "intubated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "wire", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "aero stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_5, "12 by 40", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "ballooned", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "looks way better now like 80 percent open", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 308212892_syn_6
# ==========================================
text_6 = """Rigid and flexible bronchoscopy performed for high grade left mainstem obstruction. The lesion was bypassed and defined fluoroscopically. An Aero 12x40mm stent was deployed in the left mainstem bronchus covering the area of extrinsic compression. The stent was dilated with a balloon to optimize patency. Final inspection showed marked improvement in airway caliber."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Rigid and flexible bronchoscopy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "high grade left mainstem obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "left mainstem", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "bypassed", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "fluoroscopically", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "Aero", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_6, "12x40mm", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "left mainstem bronchus", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "extrinsic compression", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "balloon", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "marked improvement in airway caliber", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 308212892_syn_7
# ==========================================
text_7 = """[Indication]
Extrinsic compression LMSB.
[Anesthesia]
General.
[Description]
Rigid bronchoscopy. High grade stenosis LMSB. 12x40mm Aero stent deployed. Balloon dilated. Patency improved to 80%.
[Plan]
Humidified O2. Saline nebs."""

entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "Extrinsic compression", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "LMSB", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid bronchoscopy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "High grade stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "LMSB", 2)},
    {"label": "DEV_STENT_SIZE", **get_span(text_7, "12x40mm", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "Aero stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "deployed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dilated", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "Patency improved to 80%", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Humidified O2", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Saline nebs", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 308212892_syn_8
# ==========================================
text_8 = """[REDACTED] a stent placed in her left main airway today. The tumor from her esophagus was crushing the airway closed. We used a rigid tube to access the airway and then placed a metal and silicone stent to hold the airway open. After placing it, we used a balloon to expand it fully. She is breathing much better now through that lung."""

entities_8 = [
    {"label": "DEV_STENT", **get_span(text_8, "stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "placed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "left main airway", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "crushing the airway closed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "rigid tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "placed", 2)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_8, "metal and silicone", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "stent", 2)},
    {"label": "PROC_ACTION", **get_span(text_8, "placing", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "expand", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "breathing much better", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 308212892_syn_9
# ==========================================
text_9 = """Intervention: Bronchial stenting.
Pathology: Extrinsic compression of the left main bronchus.
Procedure: A 12x40mm Aero prosthesis was inserted into the stenotic segment. Radial expansion was performed with a balloon catheter. Airway caliber was restored."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchial stenting", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Extrinsic compression", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "left main bronchus", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_9, "12x40mm", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "Aero prosthesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "inserted", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "stenotic segment", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Radial expansion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "balloon catheter", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "Airway caliber was restored", 1)},
]
BATCH_DATA.append({"id": "308212892_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)