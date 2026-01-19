import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function to add cases
from scripts.add_training_case import add_case

# Define the helper function for span extraction
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of a term in the text for a specific occurrence.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {'start': start, 'end': start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 3653446_syn_1
# ==========================================
t1 = """Dx: Distal Trachea Mucoepidermoid CA. Fibrosis.
Sensitizer: Temoporfin (Foscan) 96h prior.
Anesthesia: GA, 8.0 ETT.
Procedure: PDT Light.
- Fiber: 1.5cm.
- Laser: 630nm, 200 J/cm2, 500s.
- Site: Distal Trachea.
Plan: Debride 72-96h."""

e1 = [
    {"label": "ANAT_AIRWAY", **get_span(t1, "Distal Trachea", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Mucoepidermoid CA", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Fibrosis", 1)},
    {"label": "MEDICATION", **get_span(t1, "Temoporfin", 1)},
    {"label": "MEDICATION", **get_span(t1, "Foscan", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "96h", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "PDT", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "1.5cm", 1)},
    {"label": "MEAS_ENERGY", **get_span(t1, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "500s", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Distal Trachea", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "Debride", 1)},
    {"label": "MEAS_TIME", **get_span(t1, "72-96h", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 3653446_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: [REDACTED] PDT of a distal tracheal mucoepidermoid carcinoma. Background of severe pulmonary fibrosis necessitated careful airway management. Following the 96-hour Temoporfin uptake period, we delivered 630 nm laser light via a 1.5 cm cylindrical diffuser. The total energy density was 200 J/cm² over 500 seconds. The tracheal location required precise fiber positioning to avoid cuff rupture, which was successfully achieved."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "PDT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "distal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mucoepidermoid carcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "fibrosis", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "96-hour", 1)},
    {"label": "MEDICATION", **get_span(t2, "Temoporfin", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "1.5 cm", 1)},
    {"label": "MEAS_ENERGY", **get_span(t2, "200 J/cm²", 1)},
    {"label": "MEAS_TIME", **get_span(t2, "500 seconds", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "tracheal", 2)},
]
BATCH_DATA.append({"id": "3653446_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 3653446_syn_3
# ==========================================
t3 = """Code: 31641.
Site: Distal Trachea.
Agent: Temoporfin.
Laser: 630nm.
Fiber: 1.5cm.
Energy: 200 J/cm2.
Time: 500s.
Indication: Destruction of airway tumor."""

e3 = [
    {"label": "ANAT_AIRWAY", **get_span(t3, "Distal Trachea", 1)},
    {"label": "MEDICATION", **get_span(t3, "Temoporfin", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "1.5cm", 1)},
    {"label": "MEAS_ENERGY", **get_span(t3, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(t3, "500s", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 3653446_syn_4
# ==========================================
t4 = """Procedure: PDT Trachea
Pt: [REDACTED]
1. GA, 8.0 ETT.
2. Scope to distal trachea.
3. 1.5cm fiber placed centrally.
4. Laser active 500s.
5. No complications.
Plan: Light precautions."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "PDT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "distal trachea", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "1.5cm", 1)},
    {"label": "MEAS_TIME", **get_span(t4, "500s", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No complications", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 3653446_syn_5
# ==========================================
t5 = """[REDACTED] for pdt trachea tumor she has bad fibrosis used foscan 4 days ago 1.5cm fiber laser 630nm for 500 seconds kept the fiber centered away from the tube cuff no issues patient stable extubated"""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "pdt", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "trachea", 1)},
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "fibrosis", 1)},
    {"label": "MEDICATION", **get_span(t5, "foscan", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "4 days", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "1.5cm", 1)},
    {"label": "MEAS_TIME", **get_span(t5, "500 seconds", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 3653446_syn_6
# ==========================================
t6 = """Under general anesthesia, the distal tracheal tumor was visualized. A 1.5cm cylindrical diffusing fiber was positioned ensuring clearance from the ETT cuff. 630nm light was delivered for 500 seconds to activate Temoporfin. The patient remained stable. Light precautions were reviewed upon transfer to recovery."""

e6 = [
    {"label": "ANAT_AIRWAY", **get_span(t6, "distal tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "1.5cm", 1)},
    {"label": "MEAS_TIME", **get_span(t6, "500 seconds", 1)},
    {"label": "MEDICATION", **get_span(t6, "Temoporfin", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 3653446_syn_7
# ==========================================
t7 = """[Indication]
Distal Tracheal Mucoepidermoid CA.
[Anesthesia]
General, 8.0 ETT.
[Description]
1.5cm fiber placed in distal trachea. 630nm light delivered (200 J/cm2, 500s). No thermal injury.
[Plan]
Light precautions. Debride Jan 05."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "Distal Tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Mucoepidermoid CA", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "1.5cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "distal trachea", 1)},
    {"label": "MEAS_ENERGY", **get_span(t7, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(t7, "500s", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Debride", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 3653446_syn_8
# ==========================================
t8 = """[REDACTED] for her tracheal tumor. We were very careful with fiber placement given the location in the distal trachea. We used a 1.5 cm fiber and delivered the standard light dose for Temoporfin activation. The procedure went smoothly with no desaturations despite her pulmonary fibrosis. She was extubated and taken to recovery."""

e8 = [
    {"label": "ANAT_AIRWAY", **get_span(t8, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "distal trachea", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "1.5 cm", 1)},
    {"label": "MEDICATION", **get_span(t8, "Temoporfin", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "fibrosis", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 3653446_syn_9
# ==========================================
t9 = """ACTION: 1. Photodynamic therapy - light exposure. 2. Bronchoscopy.
REPORT: The airway was entered. The tracheal mass was targeted. A 1.5cm fiber was deployed. 630nm laser energy was utilized for 500 seconds. No complications were noted. The patient was transferred to the PACU."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Photodynamic therapy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "tracheal", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "1.5cm", 1)},
    {"label": "MEAS_TIME", **get_span(t9, "500 seconds", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "No complications", 1)},
]
BATCH_DATA.append({"id": "3653446_syn_9", "text": t9, "entities": e9})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)