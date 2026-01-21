import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 774930_syn_1
# ==========================================
t1 = """Indication: Severe Asthma.
Proc: Bronchial Thermoplasty (Session 2/3).
Target: RLL, LLL.
Activations: 92 total.
Complication: Mild bronchospasm (treated).
Plan: D/C."""
e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Severe Asthma", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Bronchial Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "92", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Mild bronchospasm", 1)}
]
BATCH_DATA.append({"id": "774930_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 774930_syn_2
# ==========================================
t2 = """OPERATIVE NOTE: Bronchial Thermoplasty, Session 2.
INDICATION: Refractory asthma.
PROCEDURE: The lower lobes were targeted for this session. The Alair catheter was deployed systematically in the segmental and subsegmental bronchi of the right and left lower lobes. A total of 92 radiofrequency activations were delivered. The patient tolerated the procedure with only mild, transient bronchospasm managed pharmacologically."""
e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "Bronchial Thermoplasty", 1)},
    {"label": "OBS_LESION", **get_span(t2, "Refractory asthma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "lower lobes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Alair catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "segmental and subsegmental bronchi", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "right and left lower lobes", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "92", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t2, "mild, transient bronchospasm", 1)}
]
BATCH_DATA.append({"id": "774930_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 774930_syn_3
# ==========================================
t3 = """Code: 31661 (Bronchial Thermoplasty, 2 or more lobes).
Details: Treated RLL and LLL (2 lobes). Total activations: 92. Session 2 of standard protocol."""
e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Bronchial Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "92", 1)}
]
BATCH_DATA.append({"id": "774930_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 774930_syn_4
# ==========================================
t4 = """Procedure: BT Session 2
Patient: [REDACTED]
1. General Anesthesia.
2. Treated RLL (48 hits) and LLL (44 hits).
3. Total 92 activations.
4. Pt got wheezy, gave albuterol/solumedrol.
5. Improved.
6. Extubated."""
e4 = [
    {"label": "PROC_ACTION", **get_span(t4, "BT", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "48", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "44", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "92", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t4, "wheezy", 1)},
    {"label": "MEDICATION", **get_span(t4, "albuterol", 1)},
    {"label": "MEDICATION", **get_span(t4, "solumedrol", 1)}
]
BATCH_DATA.append({"id": "774930_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 774930_syn_5
# ==========================================
t5 = """danielle morgan back for her second thermoplasty session doing the lower lobes today. went smoothly did about 90 burns total in the right and left lower lobes. she got a little tight during the case gave some nebs and steroids she opened up. going home today."""
e5 = [
    {"label": "PROC_ACTION", **get_span(t5, "thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lower lobes", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "90", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "right and left lower lobes", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t5, "tight", 1)},
    {"label": "MEDICATION", **get_span(t5, "steroids", 1)}
]
BATCH_DATA.append({"id": "774930_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 774930_syn_6
# ==========================================
t6 = """Bronchial thermoplasty performed for severe asthma. This was the second of three planned sessions targeting the lower lobes. Radiofrequency energy was delivered to the visible airways of the RLL and LLL. 92 activations total. Procedure complicated by mild bronchospasm which responded to medical therapy."""
e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Bronchial thermoplasty", 1)},
    {"label": "OBS_LESION", **get_span(t6, "severe asthma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "lower lobes", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "airways", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "92", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "mild bronchospasm", 1)}
]
BATCH_DATA.append({"id": "774930_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 774930_syn_7
# ==========================================
t7 = """[Indication]
Severe Asthma.
[Anesthesia]
General.
[Description]
Bronchial Thermoplasty RLL & LLL. 92 Activations. 
[Complications]
Transient bronchospasm.
[Plan]
Discharge. Session 3 in 3 weeks."""
e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Severe Asthma", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Bronchial Thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "92", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "Transient bronchospasm", 1)}
]
BATCH_DATA.append({"id": "774930_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 774930_syn_8
# ==========================================
t8 = """[REDACTED] for her second bronchial thermoplasty treatment for her asthma. Today we treated the bottom sections of both lungs. We used a special catheter to warm the airway walls to reduce muscle thickness. We did 92 treatments in total. She had a little asthma flare during the procedure but we treated it quickly and she is doing fine now."""
e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "bronchial thermoplasty", 1)},
    {"label": "OBS_LESION", **get_span(t8, "asthma", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "airway", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "92", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "asthma flare", 1)}
]
BATCH_DATA.append({"id": "774930_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 774930_syn_9
# ==========================================
t9 = """Intervention: Bronchial thermal remodeling.
Indication: Refractory reactive airway disease.
Technique: Radiofrequency energy application to the distal airways of the lower lobes.
Outcome: Successful completion of protocol session 2."""
e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Bronchial thermal remodeling", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Refractory reactive airway disease", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "distal airways", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "lower lobes", 1)}
]
BATCH_DATA.append({"id": "774930_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 774930
# ==========================================
t10 = """BRONCHIAL THERMOPLASTY – SESSION 2
Date: [REDACTED]
Patient: [REDACTED] | 49F | MRN [REDACTED]
Location: [REDACTED]
Attending: Dr. Steven Park

INDICATION: Severe persistent asthma uncontrolled on maximal inhaled therapy and biologic agent; patient enrolled in bronchial thermoplasty protocol.

PROCEDURE PERFORMED: Flexible bronchoscopy with bronchial thermoplasty of multiple lobes (CPT 31661)

ANESTHESIA: General anesthesia with 8.0 ETT

PROCEDURE SUMMARY:
This is session 2 of 3 (lower lobes treated today). Flexible bronchoscope was advanced via the ETT. The radiofrequency BT catheter was deployed sequentially in segmental and subsegmental bronchi of the right lower lobe and left lower lobe.

Total of 92 activations were delivered (RLL 48, LLL 44) per standard BT protocol. No biopsies, BAL or EBUS were performed.

FINDINGS: Normal tracheobronchial anatomy without mucus plugging or endobronchial lesions.

COMPLICATIONS: Mild transient bronchospasm during the case, resolved with inhaled albuterol and IV methylprednisolone. No bleeding.
DISPOSITION: Extubated in the OR, observed in PACU and discharged home after 4 hours of monitoring."""
e10 = [
    {"label": "PROC_ACTION", **get_span(t10, "BRONCHIAL THERMOPLASTY", 1)},
    {"label": "OBS_LESION", **get_span(t10, "Severe persistent asthma", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "bronchial thermoplasty", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "lower lobes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "BT catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "segmental and subsegmental bronchi", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "right lower lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "left lower lobe", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "92", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "48", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LLL", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "44", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Normal tracheobronchial anatomy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "Mild transient bronchospasm", 1)},
    {"label": "MEDICATION", **get_span(t10, "albuterol", 1)},
    {"label": "MEDICATION", **get_span(t10, "methylprednisolone", 1)}
]
BATCH_DATA.append({"id": "774930", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)