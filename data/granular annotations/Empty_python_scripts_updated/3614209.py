import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 3614209_syn_1
# ==========================================
t1 = """Target: 11mm RUL nodule.
Nav: Galaxy. Reg error 3.0mm.
Verify: Fluoroscopy.
Tools: rEBUS (eccentric), TBNA, Forceps.
ROSE: Granuloma.
Result: Benign."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "11mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Granuloma", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Benign", 1)}
]
BATCH_DATA.append({"id": "3614209_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 3614209_syn_2
# ==========================================
t2 = """Diagnostic bronchoscopy for an 11mm RUL nodule in a patient with prior malignancy history. Galaxy navigation was utilized to reach RB2. Fluoroscopic confirmation was obtained. Sampling via TBNA and forceps revealed granulomatous inflammation, arguing against recurrence."""

e2 = [
    {"label": "PROC_ACTION", **get_span(t2, "Diagnostic bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "11mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t2, "prior", 1)},
    {"label": "OBS_LESION", **get_span(t2, "malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB2", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Fluoroscopic", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "granulomatous inflammation", 1)}
]
BATCH_DATA.append({"id": "3614209_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 3614209_syn_3
# ==========================================
t3 = """31629 (TBNA), 31627 (Nav), 31654 (EBUS). Forceps bundled. 11mm target reached with Galaxy/Fluoroscopy."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "EBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Forceps", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "11mm", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Fluoroscopy", 1)}
]
BATCH_DATA.append({"id": "3614209_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 3614209_syn_4
# ==========================================
t4 = """RUL Nodule (11mm).
- Galaxy Nav to RB2.
- Fluoro confirm.
- rEBUS: Eccentric.
- TBNA x5, Forceps x6.
- ROSE: Granuloma."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RUL", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "11mm", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB2", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Fluoro", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x6", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Granuloma", 1)}
]
BATCH_DATA.append({"id": "3614209_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 3614209_syn_5
# ==========================================
t5 = """amanda has a history of cancer now has 11mm nodule rul. galaxy scope. saw it on fluoro. eccentric ebus. needle and forceps. rose says granuloma so probably not cancer. good news."""

e5 = [
    {"label": "CTX_HISTORICAL", **get_span(t5, "history of", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rul", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "fluoro", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "eccentric", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "ebus", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "granuloma", 1)},
    {"label": "OBS_LESION", **get_span(t5, "cancer", 2)}
]
BATCH_DATA.append({"id": "3614209_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 3614209_syn_6
# ==========================================
t6 = """Pulmonary nodule 11mm in RUL. General anesthesia. Noah Galaxy bronchoscope. Navigated to RB2. Fluoroscopic guidance. rEBUS eccentric. TBNA 22G and Transbronchial forceps biopsy performed. ROSE Granulomatous inflammation."""

e6 = [
    {"label": "OBS_LESION", **get_span(t6, "Pulmonary nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "11mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RB2", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Fluoroscopic", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "22G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsy", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "Granulomatous inflammation", 1)}
]
BATCH_DATA.append({"id": "3614209_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 3614209_syn_7
# ==========================================
t7 = """[Indication]
11mm nodule, RUL.
[Anesthesia]
General.
[Description]
Galaxy Nav. Fluoroscopy. rEBUS eccentric. TBNA and Forceps performed.
[Plan]
Follow up."""

e7 = [
    {"label": "MEAS_SIZE", **get_span(t7, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)}
]
BATCH_DATA.append({"id": "3614209_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 3614209_syn_8
# ==========================================
t8 = """[REDACTED] a history of cancer and a new 11mm spot in the right upper lobe. We used the Galaxy system to reach it and confirmed with fluoroscopy. We took samples with needles and forceps. The preliminary read shows granulomas, which is a relief as it suggests inflammation rather than cancer."""

e8 = [
    {"label": "CTX_HISTORICAL", **get_span(t8, "history of", 1)},
    {"label": "OBS_LESION", **get_span(t8, "cancer", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "spot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right upper lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "fluoroscopy", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "needles", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "granulomas", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "inflammation", 1)},
    {"label": "OBS_LESION", **get_span(t8, "cancer", 2)}
]
BATCH_DATA.append({"id": "3614209_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 3614209_syn_9
# ==========================================
t9 = """Reason: Pulmonary nodule.
Action: Galaxy navigation to RUL. Position verified via fluoroscopy. Sampled via TBNA and forceps. ROSE: Granulomatous inflammation."""

e9 = [
    {"label": "OBS_LESION", **get_span(t9, "Pulmonary nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RUL", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "fluoroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "Granulomatous inflammation", 1)}
]
BATCH_DATA.append({"id": "3614209_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 3614209
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: CAPT Russell Miller, MD
Fellow: Dr. Maria Santos (PGY-6)

Indication: Pulmonary nodule in patient with prior malignancy
Target: 11mm nodule in RUL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PRVC	12	325	16	100	6	22

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the RUL (RB2) based on the pre-operative CT navigational plan. Registration accuracy: 3.0mm.

Fluoroscopic guidance used to confirm scope position relative to target. Navigation alignment confirmed.

Radial EBUS performed to confirm lesion location. rEBUS view: Eccentric.

Transbronchial needle aspiration performed with 22G needle. 5 passes obtained. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed. 6 specimens obtained under fluoroscopic guidance with TiLT overlay. Samples sent for Surgical Pathology.

ROSE Result: Granulomatous inflammation

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Miller, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Pulmonary nodule", 1)},
    {"label": "CTX_HISTORICAL", **get_span(t10, "prior", 1)},
    {"label": "OBS_LESION", **get_span(t10, "malignancy", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "11mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB2", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Fluoroscopic", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 passes", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "6 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "TiLT", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Granulomatous inflammation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no significant bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Galaxy", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate complications", 1)}
]
BATCH_DATA.append({"id": "3614209", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)