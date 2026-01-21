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
# Case 1: 829174_syn_1
# ------------------------------------------
t1 = """Indication: Hemoptysis.
Findings: RB4 sessile lesion, clot removed.
Action: 3 biopsies taken. Bleeding controlled w/ ice saline/epi.
Status: Hemostasis confirmed."""

e1 = [
    {"label": "OBS_FINDING",        **get_span(t1, "Hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "RB4", 1)},
    {"label": "OBS_LESION",         **get_span(t1, "lesion", 1)},
    {"label": "OBS_FINDING",        **get_span(t1, "clot", 1)},
    {"label": "PROC_ACTION",        **get_span(t1, "removed", 1)},
    {"label": "MEAS_COUNT",         **get_span(t1, "3", 1)},
    {"label": "PROC_ACTION",        **get_span(t1, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Bleeding controlled", 1)},
    {"label": "MEDICATION",         **get_span(t1, "epi", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Hemostasis confirmed", 1)},
]
BATCH_DATA.append({"id": "829174_syn_1", "text": t1, "entities": e1})

# ------------------------------------------
# Case 2: 829174_syn_2
# ------------------------------------------
t2 = """PROCEDURE: Bronchoscopic evaluation for hemoptysis. An 8mm sessile, erythematous lesion was visualized at the RB4 orifice after removal of an overlying coagulum. Three endobronchial biopsies were performed. The resultant brisk hemorrhage was managed successfully with the instillation of cold saline and topical epinephrine 1:10,000."""

e2 = [
    {"label": "PROC_METHOD",        **get_span(t2, "Bronchoscopic", 1)},
    {"label": "OBS_FINDING",        **get_span(t2, "hemoptysis", 1)},
    {"label": "MEAS_SIZE",          **get_span(t2, "8mm", 1)},
    {"label": "OBS_FINDING",        **get_span(t2, "erythematous", 1)},
    {"label": "OBS_LESION",         **get_span(t2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t2, "RB4", 1)},
    {"label": "PROC_ACTION",        **get_span(t2, "removal", 1)},
    {"label": "OBS_FINDING",        **get_span(t2, "coagulum", 1)},
    {"label": "MEAS_COUNT",         **get_span(t2, "Three", 1)},
    {"label": "PROC_ACTION",        **get_span(t2, "endobronchial biopsies", 1)},
    {"label": "OBS_FINDING",        **get_span(t2, "brisk hemorrhage", 1)},
    {"label": "PROC_ACTION",        **get_span(t2, "instillation", 1)},
    {"label": "MEDICATION",         **get_span(t2, "epinephrine", 1)},
]
BATCH_DATA.append({"id": "829174_syn_2", "text": t2, "entities": e2})

# ------------------------------------------
# Case 3: 829174_syn_3
# ------------------------------------------
t3 = """Billing Rationale: 31625 (Biopsy). Procedure included suctioning of blood/clot to visualize the lesion (incidental) and biopsy of the RB4 lesion. Hemostasis achieved via pharmacological agents (epi) and cold saline. No separate control of bleed code applicable."""

e3 = [
    {"label": "PROC_ACTION",        **get_span(t3, "Biopsy", 1)},
    {"label": "PROC_ACTION",        **get_span(t3, "suctioning", 1)},
    {"label": "OBS_FINDING",        **get_span(t3, "blood/clot", 1)},
    {"label": "OBS_LESION",         **get_span(t3, "lesion", 1)},
    {"label": "PROC_ACTION",        **get_span(t3, "biopsy", 1)}, # lowercase "biopsy" inside text
    {"label": "ANAT_LUNG_LOC",      **get_span(t3, "RB4", 1)},
    {"label": "OBS_LESION",         **get_span(t3, "lesion", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t3, "Hemostasis achieved", 1)},
    {"label": "MEDICATION",         **get_span(t3, "epi", 1)},
]
BATCH_DATA.append({"id": "829174_syn_3", "text": t3, "entities": e3})

# ------------------------------------------
# Case 4: 829174_syn_4
# ------------------------------------------
t4 = """Procedure: Bronchoscopy
Patient: K. O'Brien
Steps:
1. Nasal approach.
2. Suctioned clot from RML.
3. Saw lesion at RB4.
4. Biopsied x3.
5. Brisk bleeding -> Epi/Ice saline used.
6. Bleeding stopped."""

e4 = [
    {"label": "PROC_ACTION",        **get_span(t4, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION",        **get_span(t4, "Suctioned", 1)},
    {"label": "OBS_FINDING",        **get_span(t4, "clot", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t4, "RML", 1)},
    {"label": "OBS_LESION",         **get_span(t4, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t4, "RB4", 1)},
    {"label": "PROC_ACTION",        **get_span(t4, "Biopsied", 1)},
    {"label": "MEAS_COUNT",         **get_span(t4, "x3", 1)},
    {"label": "OBS_FINDING",        **get_span(t4, "Brisk bleeding", 1)},
    {"label": "MEDICATION",         **get_span(t4, "Epi", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "Bleeding stopped", 1)},
]
BATCH_DATA.append({"id": "829174_syn_4", "text": t4, "entities": e4})

# ------------------------------------------
# Case 5: 829174_syn_5
# ------------------------------------------
t5 = """[REDACTED] hemoptysis check went in through nose saw blood in rml sucked out a clot found a raised red lesion at rb4 took 3 biopsies it bled pretty good used ice saline and epi stopped eventually no bleeding at end."""

e5 = [
    {"label": "OBS_FINDING",        **get_span(t5, "hemoptysis", 1)},
    {"label": "OBS_FINDING",        **get_span(t5, "blood", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t5, "rml", 1)},
    {"label": "PROC_ACTION",        **get_span(t5, "sucked out", 1)},
    {"label": "OBS_FINDING",        **get_span(t5, "clot", 1)},
    {"label": "OBS_LESION",         **get_span(t5, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t5, "rb4", 1)},
    {"label": "MEAS_COUNT",         **get_span(t5, "3", 1)},
    {"label": "PROC_ACTION",        **get_span(t5, "biopsies", 1)},
    {"label": "OBS_FINDING",        **get_span(t5, "bled pretty good", 1)},
    {"label": "MEDICATION",         **get_span(t5, "epi", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": "829174_syn_5", "text": t5, "entities": e5})

# ------------------------------------------
# Case 6: 829174_syn_6
# ------------------------------------------
t6 = """Moderate sedation was used. The scope was introduced nasally. Blood-tinged secretions and a clot were cleared from the RML, revealing an 8mm sessile lesion at RB4. Three biopsies were taken. Brisk bleeding was controlled with ice saline and epinephrine. The airways were otherwise normal."""

e6 = [
    {"label": "DEV_INSTRUMENT",     **get_span(t6, "scope", 1)},
    {"label": "OBS_FINDING",        **get_span(t6, "Blood-tinged secretions", 1)},
    {"label": "OBS_FINDING",        **get_span(t6, "clot", 1)},
    {"label": "PROC_ACTION",        **get_span(t6, "cleared", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t6, "RML", 1)},
    {"label": "MEAS_SIZE",          **get_span(t6, "8mm", 1)},
    {"label": "OBS_LESION",         **get_span(t6, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t6, "RB4", 1)},
    {"label": "MEAS_COUNT",         **get_span(t6, "Three", 1)},
    {"label": "PROC_ACTION",        **get_span(t6, "biopsies", 1)},
    {"label": "OBS_FINDING",        **get_span(t6, "Brisk bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "controlled", 1)},
    {"label": "MEDICATION",         **get_span(t6, "epinephrine", 1)},
    {"label": "ANAT_AIRWAY",        **get_span(t6, "airways", 1)},
]
BATCH_DATA.append({"id": "829174_syn_6", "text": t6, "entities": e6})

# ------------------------------------------
# Case 7: 829174_syn_7
# ------------------------------------------
t7 = """[Indication]
Recurrent hemoptysis, RML lesion.
[Anesthesia]
Moderate sedation.
[Description]
Clot removed from RB4. Underlying lesion biopsied x3. Bleeding controlled with Epi/Saline.
[Plan]
Pathology pending. Return precautions."""

e7 = [
    {"label": "OBS_FINDING",        **get_span(t7, "Recurrent hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t7, "RML", 1)},
    {"label": "OBS_LESION",         **get_span(t7, "lesion", 1)},
    {"label": "OBS_FINDING",        **get_span(t7, "Clot", 1)},
    {"label": "PROC_ACTION",        **get_span(t7, "removed", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t7, "RB4", 1)},
    {"label": "OBS_LESION",         **get_span(t7, "lesion", 2)},
    {"label": "PROC_ACTION",        **get_span(t7, "biopsied", 1)},
    {"label": "MEAS_COUNT",         **get_span(t7, "x3", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "Bleeding controlled", 1)},
    {"label": "MEDICATION",         **get_span(t7, "Epi", 1)},
]
BATCH_DATA.append({"id": "829174_syn_7", "text": t7, "entities": e7})

# ------------------------------------------
# Case 8: 829174_syn_8
# ------------------------------------------
t8 = """Ms. O'Brien came in for hemoptysis. During the bronchoscopy, we cleared a clot from the right middle lobe and found a reddish lesion underneath. We took three biopsies. This caused some brisk bleeding, but we controlled it effectively with ice saline and epinephrine. She is stable with no further bleeding."""

e8 = [
    {"label": "OBS_FINDING",        **get_span(t8, "hemoptysis", 1)},
    {"label": "PROC_ACTION",        **get_span(t8, "bronchoscopy", 1)},
    {"label": "PROC_ACTION",        **get_span(t8, "cleared", 1)},
    {"label": "OBS_FINDING",        **get_span(t8, "clot", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t8, "right middle lobe", 1)},
    {"label": "OBS_LESION",         **get_span(t8, "lesion", 1)},
    {"label": "MEAS_COUNT",         **get_span(t8, "three", 1)},
    {"label": "PROC_ACTION",        **get_span(t8, "biopsies", 1)},
    {"label": "OBS_FINDING",        **get_span(t8, "brisk bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "controlled", 1)},
    {"label": "MEDICATION",         **get_span(t8, "epinephrine", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t8, "no further bleeding", 1)},
]
BATCH_DATA.append({"id": "829174_syn_8", "text": t8, "entities": e8})

# ------------------------------------------
# Case 9: 829174_syn_9
# ------------------------------------------
t9 = """Investigation of hemoptysis. Performed nasal bronchoscopy. Cleared coagulum. Sampled sessile lesion at RB4. Managed hemorrhage with vasoconstrictors and cryo-fluid. Hemostasis verified."""

e9 = [
    {"label": "OBS_FINDING",        **get_span(t9, "hemoptysis", 1)},
    {"label": "PROC_ACTION",        **get_span(t9, "bronchoscopy", 1)},
    {"label": "OBS_FINDING",        **get_span(t9, "coagulum", 1)},
    {"label": "PROC_ACTION",        **get_span(t9, "Sampled", 1)},
    {"label": "OBS_LESION",         **get_span(t9, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t9, "RB4", 1)},
    {"label": "OBS_FINDING",        **get_span(t9, "hemorrhage", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "Hemostasis verified", 1)},
]
BATCH_DATA.append({"id": "829174_syn_9", "text": t9, "entities": e9})

# ------------------------------------------
# Case 10: 829174
# ------------------------------------------
t10 = """Pt: O'Brien, Kathleen || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. David Kim

Dx: Recurrent hemoptysis, RML bronchial lesion on CT
Procedure: Bronchoscopy with endobronchial biopsy

Moderate sedation. Bronchoscopy via nasal approach with 4.9mm scope. Blood-tinged secretions in RML. Sessile raised lesion at RB4 with overlying clot. Clot gently removed with suction. Underlying 8mm reddish lesion visualized. 3 biopsies taken with small cup forceps. Brisk bleeding controlled with ice saline and topical epinephrine (1:10,000). No active bleeding at end. Remainder of airways normal.

Post-procedure stable. No further hemoptysis. F/U path in 1 week. Return precautions given.

D. Kim, MD"""

e10 = [
    {"label": "OBS_FINDING",        **get_span(t10, "Recurrent hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t10, "RML", 1)},
    {"label": "OBS_LESION",         **get_span(t10, "lesion", 1)},
    {"label": "PROC_ACTION",        **get_span(t10, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION",        **get_span(t10, "endobronchial biopsy", 1)},
    {"label": "PROC_ACTION",        **get_span(t10, "Bronchoscopy", 2)},
    {"label": "MEAS_SIZE",          **get_span(t10, "4.9mm", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t10, "scope", 1)},
    {"label": "OBS_FINDING",        **get_span(t10, "Blood-tinged secretions", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t10, "RML", 2)},
    {"label": "OBS_LESION",         **get_span(t10, "lesion", 2)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t10, "RB4", 1)},
    {"label": "OBS_FINDING",        **get_span(t10, "clot", 1)}, # "clot" appears twice ("overlying clot", "Clot gently...")
    {"label": "OBS_FINDING",        **get_span(t10, "Clot", 1)},
    {"label": "PROC_ACTION",        **get_span(t10, "removed", 1)},
    {"label": "MEAS_SIZE",          **get_span(t10, "8mm", 1)},
    {"label": "OBS_LESION",         **get_span(t10, "lesion", 3)},
    {"label": "MEAS_COUNT",         **get_span(t10, "3", 1)},
    {"label": "PROC_ACTION",        **get_span(t10, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t10, "forceps", 1)},
    {"label": "OBS_FINDING",        **get_span(t10, "Brisk bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "controlled", 1)},
    {"label": "MEDICATION",         **get_span(t10, "epinephrine", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No active bleeding", 1)},
    {"label": "ANAT_AIRWAY",        **get_span(t10, "airways", 1)},
    {"label": "OBS_FINDING",        **get_span(t10, "hemoptysis", 2)}, # "No further hemoptysis"
]
BATCH_DATA.append({"id": "829174", "text": t10, "entities": e10})

# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)