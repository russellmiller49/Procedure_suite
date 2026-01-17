import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 12345678_syn_1
# ==========================================
t1 = """Procedure: BLVR RUL.
Indication: Severe emphysema, CV negative.
Action: 3 Zephyr valves placed in RB1 (4.0), RB2 (4.0), RB3 (5.5).
Result: Total lobar occlusion. No air leak.
Plan: Admit for obs."""

e1 = [
    {"label": "PROC_ACTION", **get_span(t1, "BLVR", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Severe emphysema", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "CV negative", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 1)},
    {"label": "DEV_VALVE", **get_span(t1, "Zephyr", 1)},
    {"label": "DEV_VALVE", **get_span(t1, "valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RB1", 1)},
    {"label": "DEV_VALVE", **get_span(t1, "4.0", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RB2", 1)},
    {"label": "DEV_VALVE", **get_span(t1, "4.0", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RB3", 1)},
    {"label": "DEV_VALVE", **get_span(t1, "5.5", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Total lobar occlusion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No air leak", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_1", "text": t1, "entities": e1})


# ==========================================
# Note 2: 12345678_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Mr. [REDACTED] presented for elective bronchoscopic lung volume reduction. Pre-procedural Chartis assessment confirmed the absence of collateral ventilation in the Right Upper Lobe (RUL). Using a flexible bronchoscope, the RUL segmental anatomy was id[REDACTED]. Three Zephyr endobronchial valves were deployed: a 4.0mm valve in RB1, a 4.0mm valve in RB2, and a 5.5mm valve in RB3. Bronchoscopic inspection confirmed optimal seating and complete lobar occlusion."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "bronchoscopic lung volume reduction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "collateral ventilation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Right Upper Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "flexible bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 2)},
    {"label": "MEAS_COUNT", **get_span(t2, "Three", 1)},
    {"label": "DEV_VALVE", **get_span(t2, "Zephyr", 1)},
    {"label": "DEV_VALVE", **get_span(t2, "endobronchial valves", 1)},
    {"label": "DEV_VALVE", **get_span(t2, "4.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB1", 1)},
    {"label": "DEV_VALVE", **get_span(t2, "4.0mm", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB2", 1)},
    {"label": "DEV_VALVE", **get_span(t2, "5.5mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB3", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "complete lobar occlusion", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_2", "text": t2, "entities": e2})


# ==========================================
# Note 3: 12345678_syn_3
# ==========================================
t3 = """CPT 31647 (Bronchoscopy with placement of bronchial valves, initial lobe).
- Site: Right Upper Lobe.
- Devices: 3 Zephyr Valves.
- Assessment: Chartis utilized to rule out collateral ventilation (bundled).
- Outcome: Complete occlusion achieved."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchoscopy with placement of bronchial valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Right Upper Lobe", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "3", 1)},
    {"label": "DEV_VALVE", **get_span(t3, "Zephyr Valves", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "collateral ventilation", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "Complete occlusion", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_3", "text": t3, "entities": e3})


# ==========================================
# Note 4: 12345678_syn_4
# ==========================================
t4 = """Procedure: Valve Placement (BLVR)
Attending: Dr. Thompson
Steps:
1. Airway inspection. RUL selected.
2. Chartis negative (good for valves).
3. Sized airways.
4. Placed valves in RB1, RB2, RB3.
5. Checked for leaks - none.
Plan: CXR to check for pneumothorax."""

e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "Valve Placement", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "BLVR", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Chartis", 1)},
    {"label": "DEV_VALVE", **get_span(t4, "valves", 1)},
    {"label": "DEV_VALVE", **get_span(t4, "valves", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB1", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB2", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB3", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "none", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_4", "text": t4, "entities": e4})


# ==========================================
# Note 5: 12345678_syn_5
# ==========================================
t5 = """We did the lung volume reduction on Mr [REDACTED] today for his emphysema right upper lobe. Chartis balloon showed no collateral ventilation so we proceeded. Put in three valves total two 4s and one 5.5. They fit good no leaks. RUL looks closed off. Patient woke up fine sending to recovery."""

e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "lung volume reduction", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "emphysema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "right upper lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "Chartis balloon", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "collateral ventilation", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "three", 1)},
    {"label": "DEV_VALVE", **get_span(t5, "valves", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "two", 1)},
    {"label": "DEV_VALVE", **get_span(t5, "4s", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "one", 1)},
    {"label": "DEV_VALVE", **get_span(t5, "5.5", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no leaks", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RUL", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "closed off", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_5", "text": t5, "entities": e5})


# ==========================================
# Note 6: 12345678_syn_6
# ==========================================
t6 = """Bronchoscopic lung volume reduction with endobronchial valve placement. The right upper lobe was targeted for treatment of severe emphysema. Chartis assessment confirmed the absence of collateral ventilation. Three Zephyr valves were deployed in the apical, posterior, and anterior segments of the RUL. Visual inspection confirmed appropriate placement and lobar occlusion. There were no immediate complications."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Bronchoscopic lung volume reduction", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "endobronchial valve placement", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "right upper lobe", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "severe emphysema", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "collateral ventilation", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Three", 1)},
    {"label": "DEV_VALVE", **get_span(t6, "Zephyr valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "apical", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "posterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "anterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "lobar occlusion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "no immediate complications", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_6", "text": t6, "entities": e6})


# ==========================================
# Note 7: 12345678_syn_7
# ==========================================
t7 = """[Indication]
Severe emphysema, RUL target.
[Anesthesia]
Moderate Sedation.
[Description]
Chartis: CV Negative. Valves placed: RB1, RB2, RB3. Total occlusion confirmed.
[Plan]
Overnight observation. CXR protocol."""

e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "Severe emphysema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "CV Negative", 1)},
    {"label": "DEV_VALVE", **get_span(t7, "Valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB1", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB2", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB3", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "Total occlusion", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_7", "text": t7, "entities": e7})


# ==========================================
# Note 8: 12345678_syn_8
# ==========================================
t8 = """[REDACTED] a procedure to help with his severe emphysema. We targeted the right upper lobe of his lung. After confirming that the lobe was isolated using a balloon catheter, we placed three one-way valves into the airways leading to that lobe. These valves will allow air to escape but not enter, hopefully reducing the size of the lobe and helping him breathe better. Everything went smoothly and the valves are sitting perfectly."""

e8 = [
    {"label": "OBS_FINDING", **get_span(t8, "severe emphysema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right upper lobe", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "balloon catheter", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "three", 1)},
    {"label": "DEV_VALVE", **get_span(t8, "one-way valves", 1)},
    {"label": "DEV_VALVE", **get_span(t8, "valves", 2)},
]
BATCH_DATA.append({"id": "12345678_syn_8", "text": t8, "entities": e8})


# ==========================================
# Note 9: 12345678_syn_9
# ==========================================
t9 = """Procedure: Endobronchial prosthesis implantation.
Target: Right Upper Lobe.
Action: Collateral ventilation was ruled out. Three occlusion devices were deployed in the segmental bronchi. 
Result: Complete lobar isolation observed."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Endobronchial prosthesis implantation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Right Upper Lobe", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Collateral ventilation", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "Three", 1)},
    {"label": "DEV_VALVE", **get_span(t9, "occlusion devices", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "segmental bronchi", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "Complete lobar isolation", 1)},
]
BATCH_DATA.append({"id": "12345678_syn_9", "text": t9, "entities": e9})


# ==========================================
# Note 10: 12345678 (Original)
# ==========================================
t10 = """PROCEDURE: BRONCHOSCOPIC LUNG VOLUME REDUCTION WITH ENDOBRONCHIAL VALVE PLACEMENT
Date: [REDACTED]
Patient: [REDACTED] | DOB: [REDACTED] | Age: 67 | MRN: [REDACTED]
Institution: [REDACTED]
Physician: Jennifer Martinez, MD, FCCP
Attending: David Thompson, MD

INDICATION:
Severe heterogeneous emphysema with hyperinflation, predominantly affecting the right upper lobe. FEV1 35% predicted, marked dyspnea, GOLD Stage IV COPD.

PRE-PROCEDURE ASSESSMENT:
- CT thorax: Severe heterogeneous emphysema, RUL destruction score 90%, fissure integrity 95%
- Chartis assessment: Negative collateral ventilation confirmed
- PFTs: FEV1 0.9L (35%), RV 285% predicted, TLC 145%

PROCEDURE DETAILS:
Flexible bronchoscopy performed under moderate sedation with midazolam 4mg and fentanyl 100mcg. Topical anesthesia with lidocaine. 

The bronchoscope was advanced through the oral cavity. Complete airway inspection performed. No endobronchial lesions noted. Moderate secretions cleared.

TARGET: Right upper lobe
- RB1: Zephyr EBV 4.0mm placed with good wall apposition
- RB2: Zephyr EBV 4.0mm placed with good wall apposition  
- RB3: Zephyr EBV 5.5mm placed with good wall apposition

All valves deployed successfully with complete occlusion confirmed. No air leaks detected. Procedure tolerated well.

COMPLICATIONS: None
ESTIMATED BLOOD LOSS: Minimal
SPECIMENS: None

IMPRESSION:
Successful bronchoscopic lung volume reduction with placement of 3 endobronchial valves in right upper lobe bronchi. Complete lobar occlusion achieved.

PLAN:
- Chest X-ray in recovery
- Observe overnight
- Follow-up CT chest in 30 days
- PFTs in 6 weeks"""

e10 = [
    {"label": "PROC_ACTION", **get_span(t10, "BRONCHOSCOPIC LUNG VOLUME REDUCTION", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "ENDOBRONCHIAL VALVE PLACEMENT", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Severe heterogeneous emphysema", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "right upper lobe", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Severe heterogeneous emphysema", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Chartis", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "collateral ventilation", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Flexible bronchoscopy", 1)},
    {"label": "MEDICATION", **get_span(t10, "midazolam", 1)},
    {"label": "MEDICATION", **get_span(t10, "fentanyl", 1)},
    {"label": "MEDICATION", **get_span(t10, "lidocaine", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Right upper lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB1", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Zephyr EBV", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "4.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB2", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Zephyr EBV", 2)},
    {"label": "DEV_VALVE", **get_span(t10, "4.0mm", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB3", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "Zephyr EBV", 3)},
    {"label": "DEV_VALVE", **get_span(t10, "5.5mm", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "valves", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "complete occlusion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No air leaks", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "bronchoscopic lung volume reduction", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "3", 1)},
    {"label": "DEV_VALVE", **get_span(t10, "endobronchial valves", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "right upper lobe", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "bronchi", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Complete lobar occlusion", 1)},
]
BATCH_DATA.append({"id": "12345678", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)