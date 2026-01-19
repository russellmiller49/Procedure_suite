import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note: 3309146
# ==========================================
t_3309146 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Michael Chen
Fellow: Dr. James Liu (PGY-5)

Indication: Primary lung adenocarcinoma with CAO
Pre-procedure obstruction: ~76% Trachea

PROCEDURE:
Under general anesthesia with jet ventilation, rigid bronchoscopy performed.
Airway measured and Novatech Silicone - Dumon stent (20x60mm) deployed in Trachea.
Stent position confirmed with good expansion and patency.
Post-procedure obstruction: ~15%
No complications. EBL minimal.

DISPOSITION: Recovery then floor admission for overnight observation.
F/U: Clinic in 4-6 weeks with repeat bronchoscopy.

Chen, MD"""
e_3309146 = [
    {"label": "OBS_FINDING", **get_span(t_3309146, "CAO", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146, "76%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146, "Trachea", 1)},
    {"label": "PROC_METHOD", **get_span(t_3309146, "rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146, "Silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146, "Dumon", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146, "20x60mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146, "Trachea", 2)},
    {"label": "DEV_STENT", **get_span(t_3309146, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146, "15%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3309146, "No complications", 1)},
]
BATCH_DATA.append({"id": "3309146", "text": t_3309146, "entities": e_3309146})

# ==========================================
# Note: 3309146_syn_1
# ==========================================
t_3309146_syn_1 = """Dx: Lung Adenocarcinoma, Tracheal CAO.
Proc: Rigid bronch, Stent.
Implant: Novatech Silicone 20x60mm Trachea.
Result: 76% -> 15% obstruction.
Complications: None.
Plan: Floor admit."""
e_3309146_syn_1 = [
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_1, "Tracheal", 1)},
    {"label": "OBS_FINDING", **get_span(t_3309146_syn_1, "CAO", 1)},
    {"label": "PROC_METHOD", **get_span(t_3309146_syn_1, "Rigid bronch", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_1, "Stent", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_1, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_1, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_1, "20x60mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_1, "Trachea", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_1, "76%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_1, "15%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3309146_syn_1, "None", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_1", "text": t_3309146_syn_1, "entities": e_3309146_syn_1})

# ==========================================
# Note: 3309146_syn_2
# ==========================================
t_3309146_syn_2 = """OPERATIVE NOTE: [REDACTED] critical central airway obstruction (76% Trachea) secondary to primary lung adenocarcinoma. Rigid bronchoscopy was performed under general anesthesia. The tracheal lumen was sized, and a 20x60mm Novatech Silicone (Dumon) stent was deployed. Post-deployment inspection confirmed excellent expansion and restoration of airway caliber (15% residual)."""
e_3309146_syn_2 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_2, "76%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_2, "Trachea", 1)},
    {"label": "PROC_METHOD", **get_span(t_3309146_syn_2, "Rigid bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_2, "tracheal", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_2, "20x60mm", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_2, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_2, "Silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_2, "Dumon", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_2, "stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_2, "15%", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_2", "text": t_3309146_syn_2, "entities": e_3309146_syn_2})

# ==========================================
# Note: 3309146_syn_3
# ==========================================
t_3309146_syn_3 = """CPT Justification: 31631 (Bronchoscopy with placement of tracheal stent).
Device: Novatech Silicone Stent (20x60mm).
Location: Trachea (Distinct from bronchial codes).
Indication: 76% obstruction reduced to 15%."""
e_3309146_syn_3 = [
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_3, "tracheal", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_3, "stent", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_3, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_3, "Silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_3, "Stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_3, "20x60mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_3, "Trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_3, "76%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_3, "15%", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_3", "text": t_3309146_syn_3, "entities": e_3309146_syn_3})

# ==========================================
# Note: 3309146_syn_4
# ==========================================
t_3309146_syn_4 = """Resident: Dr. Liu
Attending: Dr. Chen
Pt: [REDACTED]
Proc: Tracheal Stent
1. Rigid scope inserted.
2. Measured tracheal stenosis (76%).
3. Deployed Novatech stent 20x60mm.
4. Verified patency.
5. No complications.
Plan: Admit."""
e_3309146_syn_4 = [
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_4, "Tracheal", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_4, "Stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_3309146_syn_4, "Rigid scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_4, "tracheal", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_4, "76%", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_4, "Novatech", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_4, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_4, "20x60mm", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3309146_syn_4, "No complications", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_4", "text": t_3309146_syn_4, "entities": e_3309146_syn_4})

# ==========================================
# Note: 3309146_syn_5
# ==========================================
t_3309146_syn_5 = """procedure note for thomas allen. he has lung cancer blocking the trachea pretty bad about 76 percent. dr chen and i did a rigid bronch. put in a dumon silicone stent 20 by 60 right in the trachea. opened up great residual is only 15 percent now. no bleeding issues. admit to floor for observation."""
e_3309146_syn_5 = [
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_5, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_5, "76 percent", 1)},
    {"label": "PROC_METHOD", **get_span(t_3309146_syn_5, "rigid bronch", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_5, "dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_5, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_5, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_5, "20 by 60", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_5, "trachea", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_5, "15 percent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3309146_syn_5, "no bleeding issues", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_5", "text": t_3309146_syn_5, "entities": e_3309146_syn_5})

# ==========================================
# Note: 3309146_syn_6
# ==========================================
t_3309146_syn_6 = """Primary lung adenocarcinoma with CAO. Pre-procedure obstruction 76% Trachea. Under general anesthesia with jet ventilation, rigid bronchoscopy performed. Airway measured and Novatech Silicone - Dumon stent (20x60mm) deployed in Trachea. Stent position confirmed with good expansion and patency. Post-procedure obstruction 15%. No complications. EBL minimal. Recovery then floor admission for overnight observation."""
e_3309146_syn_6 = [
    {"label": "OBS_FINDING", **get_span(t_3309146_syn_6, "CAO", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_6, "76%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_6, "Trachea", 1)},
    {"label": "PROC_METHOD", **get_span(t_3309146_syn_6, "rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_6, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_6, "Silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_6, "Dumon", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_6, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_6, "20x60mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_6, "Trachea", 2)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_6, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_6, "15%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t_3309146_syn_6, "No complications", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_6", "text": t_3309146_syn_6, "entities": e_3309146_syn_6})

# ==========================================
# Note: 3309146_syn_7
# ==========================================
t_3309146_syn_7 = """[Indication]
Lung AdenoCA, 76% Tracheal obstruction.
[Anesthesia]
General, Jet Vent.
[Description]
Rigid bronchoscopy. Novatech Silicone stent (20x60mm) deployed in Trachea. Expansion confirmed. Residual obstruction 15%.
[Plan]
Floor admission. Repeat bronch 4-6 wks."""
e_3309146_syn_7 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_7, "76%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_7, "Tracheal", 1)},
    {"label": "PROC_METHOD", **get_span(t_3309146_syn_7, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_7, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_7, "Silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_7, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_7, "20x60mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_7, "Trachea", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_7, "15%", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_7", "text": t_3309146_syn_7, "entities": e_3309146_syn_7})

# ==========================================
# Note: 3309146_syn_8
# ==========================================
t_3309146_syn_8 = """[REDACTED] for a significant tracheal obstruction caused by lung adenocarcinoma. Under general anesthesia, we advanced the rigid bronchoscope and measured the affected area. We then successfully deployed a 20x60mm Novatech Silicone stent. The stent expanded fully, reducing the obstruction from 76% to 15%, providing immediate relief."""
e_3309146_syn_8 = [
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_8, "tracheal", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_8, "20x60mm", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_8, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_8, "Silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_8, "stent", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_8, "stent", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t_3309146_syn_8, "76%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_8, "15%", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_8", "text": t_3309146_syn_8, "entities": e_3309146_syn_8})

# ==========================================
# Note: 3309146_syn_9
# ==========================================
t_3309146_syn_9 = """Under general anesthesia with jet ventilation, rigid bronchoscopy was performed. The airway was measured and a Novatech Silicone - Dumon stent (20x60mm) was inserted in the Trachea. Stent placement was verified with good expansion and patency. Post-procedure blockage was ~15%. No adverse events."""
e_3309146_syn_9 = [
    {"label": "PROC_METHOD", **get_span(t_3309146_syn_9, "rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_9, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(t_3309146_syn_9, "Silicone", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_9, "Dumon", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_9, "stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(t_3309146_syn_9, "20x60mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t_3309146_syn_9, "Trachea", 1)},
    {"label": "DEV_STENT", **get_span(t_3309146_syn_9, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t_3309146_syn_9, "15%", 1)},
]
BATCH_DATA.append({"id": "3309146_syn_9", "text": t_3309146_syn_9, "entities": e_3309146_syn_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)