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

BATCH_DATA = []

# ==========================================
# Note 1: 1037685_syn_1
# ==========================================
t1 = """Dx: 14mm nodule RML (Lung-RADS 4B).
Method: Galaxy Nav + TiLT + rEBUS.
Findings: 2.1cm divergence corrected via TiLT. rEBUS concentric.
Actions: TBNA 21G x 7 passes.
ROSE: Necrotic debris, rare atypical cells.
Complication: None. Pneumothorax negative on post-op scan."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Galaxy Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "TiLT", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "TiLT", 2)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "21G", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "7 passes", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Necrotic debris, rare atypical cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "Pneumothorax negative", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 1037685_syn_2
# ==========================================
t2 = """The patient underwent elective robotic bronchoscopy for a suspicious 14mm nodule in the Right Middle Lobe. The Noah Galaxy platform was utilized. Intra-procedural tomosynthesis (TiLT+) revealed a 2.1cm target divergence attributed to respiratory motion, which was digitally corrected. Following concentric rEBUS confirmation, transbronchial needle aspiration was executed. Rapid on-site evaluation suggested necrosis with atypia."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "robotic bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Right Middle Lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Noah Galaxy platform", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "tomosynthesis", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "transbronchial needle aspiration", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "necrosis with atypia", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 1037685_syn_3
# ==========================================
t3 = """Billable Services:
- 31627 (Navigational Bronchoscopy): Required for 14mm RML nodule.
- 31629 (Transbronchial Needle Aspiration): Primary sampling modality.
- 31654 (Peripheral EBUS): Used for localization.
Note: High complexity due to 2.1cm divergence requiring TiLT+ correction."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "Navigational Bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Transbronchial Needle Aspiration", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Peripheral EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "TiLT+", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 1037685_syn_4
# ==========================================
t4 = """Resident Note:
Attending: Dr. Thompson
Pt: 65F, RML nodule.
1. ETT placed.
2. Galaxy nav to RB4.
3. TiLT spin -> updated target (2.1cm shift).
4. rEBUS concentric.
5. TBNA x7.
6. ROSE: Atypical.
Stable."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Galaxy nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB4", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x7", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Atypical", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 1037685_syn_5
# ==========================================
t5 = """sandra came in for the rml nodule. galaxy scope used. reg was 3.9mm. got to the rml and did the tilt spin thing, huge shift 2.1cm from breathing i guess. fixed it and saw concentric view on ebus. stuck it with the 21g needle 7 times. rose showed necrotic junk and maybe cancer. shes fine going home."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rml", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "galaxy scope", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "3.9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rml", 2)},
    {"label": "PROC_METHOD", **get_span(t5, "tilt", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ebus", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "21g", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "7 times", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "necrotic junk", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "maybe cancer", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 1037685_syn_6
# ==========================================
t6 = """Lung-RADS 4B nodule 14mm in RML. General anesthesia. Noah Galaxy bronchoscope introduced. Registration error 3.9mm. TiLT+ sweep performed showing 2.1cm divergence. Target updated. rEBUS concentric. TBNA 21G performed. ROSE necrotic debris. Patient tolerated well."""

e6 = [
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RML", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Noah Galaxy bronchoscope", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "3.9mm", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "TiLT+ sweep", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "21G", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "necrotic debris", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 1037685_syn_7
# ==========================================
t7 = """[Indication]
Lung-RADS 4B, 14mm RML.
[Anesthesia]
General.
[Description]
Galaxy navigation. TiLT+ used to sync target (2.1cm divergence). rEBUS concentric. TBNA performed.
[Plan]
Monitor for pneumothorax (negative on immediate check). Discharge."""

e7 = [
    {"label": "MEAS_SIZE", **get_span(t7, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RML", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Galaxy navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t7, "pneumothorax (negative", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 1037685_syn_8
# ==========================================
t8 = """After inducing anesthesia, we inserted the Galaxy scope to biopsy the 14mm nodule in the right middle lobe. Because of significant respiratory motion, the TiLT system showed a 2.1cm difference from the pre-op CT, which we corrected. We confirmed the position with a nice concentric EBUS view and took seven needle passes. The pathologist saw some atypical cells on the slide."""

e8 = [
    {"label": "DEV_INSTRUMENT", **get_span(t8, "Galaxy scope", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right middle lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "TiLT system", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "EBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "seven needle passes", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "atypical cells", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 1037685_syn_9
# ==========================================
t9 = """Reason: Lung-RADS 4B lesion.
Action: The Galaxy system was guided to the RML. A 2.1cm divergence was rectified using TiLT+. The nodule was localized via rEBUS. Samples were acquired using a 21G needle.
Result: ROSE showed atypical cells."""

e9 = [
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Galaxy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RML", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "TiLT+", 1)},
    {"label": "OBS_LESION", **get_span(t9, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "needle", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "atypical cells", 1)}
]
BATCH_DATA.append({"id": "1037685_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 1037685
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Emily Thompson

Indication: Lung-RADS 4B nodule
Target: 14mm nodule in RML

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PCV	14	345	15	100	5	24

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the RML (RB4) based on the pre-operative CT navigational plan. Registration accuracy: 3.9mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 2.1cm divergence between the pre-op CT target and the actual lesion location due to respiratory motion.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Concentric.

Transbronchial needle aspiration performed with 21G needle. 7 passes obtained. Samples sent for Cytology and Cell block.

ROSE Result: Necrotic debris with rare atypical cells

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Thompson, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesions", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Noah Galaxy bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB4", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "3.9mm", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Tool-in-Lesion Tomosynthesis (TiLT+) sweep", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.1cm", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Intra-operative tomosynthesis (TiLT)", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "TiLT", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "TiLT", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "21G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "7 passes", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cell block", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Necrotic debris with rare atypical cells", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Galaxy scope", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate complications", 1)}
]
BATCH_DATA.append({"id": "1037685", "text": t10, "entities": e10})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)