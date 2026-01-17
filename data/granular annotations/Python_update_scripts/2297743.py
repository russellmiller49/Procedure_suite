import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is located in 'scripts/' and the repo root is one level up
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a substring.
    """
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 2297743_syn_1
# ==========================================
id_1 = "2297743_syn_1"
text_1 = """Indication: Thyroid cancer, tracheal compression.
Pre-op: 79% stenosis.
Procedure:
- Rigid bronchoscopy, jet ventilation.
- Balloon dilation.
- Dumon stent (12x60mm) deployed in Trachea.
- Good expansion confirmed.
Post-op: 11% obstruction.
Complications: None."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Thyroid cancer", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "tracheal compression", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "79% stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "jet ventilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilation", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "Dumon stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_1, "12x60mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "11% obstruction", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2297743_syn_2
# ==========================================
id_2 = "2297743_syn_2"
text_2 = """HISTORY: [REDACTED] significant airway compromise secondary to thyroid malignancy. Quantitative assessment revealed 79% tracheal stenosis.
OPERATIVE NARRATIVE: Under general anesthesia utilizing jet ventilation, the airway was secured via rigid bronchoscopy. Mechanical dilation of the stenotic segment was performed to facilitate appliance delivery. A 12x60mm Novatech Silicone Dumon stent was precisely deployed within the trachea. Post-deployment endoscopic inspection confirmed restoration of airway caliber to near-physiologic dimensions (11% residual narrowing) and excellent stent apposition.
PLAN: Admitted for observation."""
entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "thyroid malignancy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "79% tracheal stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_2, "12x60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "Novatech Silicone Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_2, "Silicone", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "11% residual narrowing", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2297743_syn_3
# ==========================================
id_3 = "2297743_syn_3"
text_3 = """Procedure: Bronchoscopy with Tracheal Stent Placement (CPT 31631).
Technique:
1. Introduction of rigid bronchoscope under GA.
2. Assessment of tracheal stenosis (79%).
3. Therapeutic dilation performed to prepare site.
4. Measurement and selection of Novatech Dumon Stent (12x60mm).
5. Deployment of stent into trachea covering the stenotic region.
6. Verification of patency and lack of migration.
Necessity: Malignant neoplasm causing central airway obstruction."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Tracheal", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Stent Placement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "rigid bronchoscope", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "tracheal stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "79%", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "dilation", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "Novatech Dumon Stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_3, "12x60mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Deployment", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "trachea", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Malignant neoplasm", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "central airway obstruction", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2297743_syn_4
# ==========================================
id_4 = "2297743_syn_4"
text_4 = """Procedure: Rigid Bronchoscopy with Stent Placement
Attending: Dr. Davis
Steps:
1. Time out performed.
2. General anesthesia with jet ventilation.
3. Rigid scope inserted.
4. Tracheal stenosis id[REDACTED] and dilated.
5. Stent (Dumon 12x60mm) placed in trachea.
6. Position confirmed.
7. Scope removed.
No complications encountered."""
entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Stent Placement", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "jet ventilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Tracheal stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Tracheal", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "dilated", 1)},
    {"label": "DEV_STENT", **get_span(text_4, "Stent", 1)},
    {"label": "DEV_STENT", **get_span(text_4, "Dumon", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_4, "12x60mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "trachea", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No complications", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2297743_syn_5
# ==========================================
id_5 = "2297743_syn_5"
text_5 = """Patient [REDACTED] here for the tracheal stent she has thyroid cancer compressing the airway about 80 percent blocked we used the rigid scope with jet vent dilated it open then put in a novatech dumon stent 12 by 60 millimeter right in the trachea looks good now wide open only maybe 10 percent blocked no bleeding really sent to recovery then admit thanks."""
entities_5 = [
    {"label": "ANAT_AIRWAY", **get_span(text_5, "tracheal", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "stent", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "thyroid cancer", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "compressing the airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "80 percent blocked", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "rigid scope", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "jet vent", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "dilated", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "novatech dumon stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_5, "12 by 60 millimeter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "10 percent blocked", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2297743_syn_6
# ==========================================
id_6 = "2297743_syn_6"
text_6 = """The patient presented with thyroid cancer causing tracheal compression. Pre-procedure obstruction was estimated at 79%. Under general anesthesia with jet ventilation, rigid bronchoscopy was performed. Sequential balloon dilation of the tracheal stenosis was carried out. The airway was measured, and a Novatech Silicone Dumon stent (12x60mm) was deployed in the trachea. Stent position was confirmed with good expansion and patency. Post-procedure obstruction was reduced to approximately 11%. There were no complications, and EBL was minimal. The patient was sent to recovery and then admitted for overnight observation."""
entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "thyroid cancer", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "tracheal compression", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "79%", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dilation", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "tracheal stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "tracheal", 2)},
    {"label": "DEV_STENT", **get_span(text_6, "Novatech Silicone Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_6, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_6, "12x60mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "11%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no complications", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2297743_syn_7
# ==========================================
id_7 = "2297743_syn_7"
text_7 = """[Indication]
Thyroid cancer with 79% tracheal compression.
[Anesthesia]
General with jet ventilation.
[Description]
Rigid bronchoscopy performed. Stenosis dilated. Novatech Dumon stent (12x60mm) deployed in trachea. Patency restored (11% residual).
[Plan]
Admit for observation. Clinic follow-up 4-6 weeks."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Thyroid cancer", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "79% tracheal compression", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dilated", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "Novatech Dumon stent", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_7, "12x60mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "11% residual", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2297743_syn_8
# ==========================================
id_8 = "2297743_syn_8"
text_8 = """[REDACTED] a rigid bronchoscopy today to address her tracheal compression caused by thyroid cancer. We utilized general anesthesia and jet ventilation. After id[REDACTED] the 79% stenosis, we performed sequential balloon dilation. Subsequently, a 12x60mm Novatech Silicone Dumon stent was deployed into the trachea. The stent expanded well, and we confirmed good patency with a residual obstruction of only 11%. She tolerated the procedure well with minimal blood loss."""
entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "rigid bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "tracheal compression", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "thyroid cancer", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "jet ventilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "79% stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dilation", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_8, "12x60mm", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "Novatech Silicone Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_8, "Silicone", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "trachea", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "obstruction of only 11%", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2297743_syn_9
# ==========================================
id_9 = "2297743_syn_9"
text_9 = """Indication: Thyroid carcinoma with tracheal impingement.
Pre-procedure blockage: ~79% Trachea.
PROCEDURE: Under general anesthesia, rigid bronchoscopy was executed. Sequential balloon expansion of the trachea stenosis was conducted. The airway was gauged and a Novatech Silicone - Dumon stent (12x60mm) was implanted in the Trachea. Stent seating was validated with good expansion and openness.
Post-procedure blockage: ~11%.
No adverse events."""
entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "Thyroid carcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "tracheal impingement", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_9, "~79%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "Trachea", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "expansion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "trachea", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "stenosis", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "Novatech Silicone - Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_9, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_9, "12x60mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "implanted", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "Trachea", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "~11%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "No adverse events", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 2297743
# ==========================================
id_10 = "2297743"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: CDR Patricia Davis, MD

Indication: Thyroid cancer with tracheal compression
Pre-procedure obstruction: ~79% Trachea

PROCEDURE:
Under general anesthesia with jet ventilation, rigid bronchoscopy performed.
Sequential balloon dilation of trachea stenosis performed.
Airway measured and Novatech Silicone - Dumon stent (12x60mm) deployed in Trachea.
Stent position confirmed with good expansion and patency.
Post-procedure obstruction: ~11%
No complications. EBL minimal.

DISPOSITION: Recovery then floor admission for overnight observation.
F/U: Clinic in 4-6 weeks with repeat bronchoscopy.

Davis, MD"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Thyroid cancer", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "tracheal compression", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "~79%", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "jet ventilation", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "dilation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "stenosis", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "Novatech Silicone - Dumon stent", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "Silicone", 1)},
    {"label": "DEV_STENT_SIZE", **get_span(text_10, "12x60mm", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "deployed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "~11%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)