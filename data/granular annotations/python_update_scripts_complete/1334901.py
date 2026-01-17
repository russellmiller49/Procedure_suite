import sys
from pathlib import Path

# Set up the repository root path
# Assumes the script is running within the 'scripts' subdirectory or similar depth
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ==========================================
# Note 1: 1334901_syn_1
# ==========================================
text_1 = """Target: 13mm LLL nodule.
Nav: Galaxy + TiLT (1.9cm div).
Tools: rEBUS (adjacent), TBNA.
ROSE: Suspicious for NSCLC.
Disposition: D/C."""
entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "13mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for NSCLC", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1334901_syn_2
# ==========================================
text_2 = """The patient underwent evaluation of a 13mm LLL nodule. Galaxy robotic navigation was employed. Intraoperative TiLT imaging revealed a significant 1.9cm divergence due to respiratory motion, which was corrected. Following adjacent rEBUS confirmation, 21G TBNA was performed. Cytology is suspicious for non-small cell lung cancer."""
entities_2 = [
    {"label": "MEAS_SIZE", **get_span(text_2, "13mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "robotic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "suspicious for non-small cell lung cancer", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1334901_syn_3
# ==========================================
text_3 = """31629 (TBNA), 31627 (Nav), 31654 (EBUS). 1.9cm divergence corrected by TiLT+."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "TiLT+", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1334901_syn_4
# ==========================================
text_4 = """LLL Nodule (13mm).
- Galaxy to LB10.
- TiLT: 1.9cm shift.
- rEBUS: Adjacent.
- TBNA x6.
- ROSE: Suspicious NSCLC."""
entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "13mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB10", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Suspicious NSCLC", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1334901_syn_5
# ==========================================
text_5 = """carol here for lll nodule 13mm. galaxy scope. breathing moved the target 1.9cm tilt fixed it. adjacent ebus view. just did needles. rose thinks nsclc."""
entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "13mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "galaxy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "tilt", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ebus", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "nsclc", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1334901_syn_6
# ==========================================
text_6 = """Peripheral pulmonary nodule 13mm in LLL. General anesthesia. Noah Galaxy bronchoscope. Navigated to LB10. TiLT+ sweep revealed 1.9cm divergence. Corrected. rEBUS adjacent. TBNA 21G performed. ROSE Suspicious for non-small cell carcinoma."""
entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "13mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Noah Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB10", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "21G", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "Suspicious for non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1334901_syn_7
# ==========================================
text_7 = """[Indication]
13mm nodule, LLL.
[Anesthesia]
General.
[Description]
Galaxy Nav. TiLT correction 1.9cm. rEBUS adjacent. TBNA performed.
[Plan]
Follow up."""
entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "13mm", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1334901_syn_8
# ==========================================
text_8 = """[REDACTED] a 13mm nodule in the back of the left lower lobe. We used the Galaxy robot. The TiLT scan showed it was almost 2cm away from where we expected due to her breathing, so we updated the target and found it. We did six needle passes. It looks suspicious for cancer."""
entities_8 = [
    {"label": "MEAS_SIZE", **get_span(text_8, "13mm", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left lower lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Galaxy robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "2cm", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "six", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "suspicious for cancer", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1334901_syn_9
# ==========================================
text_9 = """Reason: Peripheral nodule.
Action: Galaxy navigation to LLL. TiLT+ adjusted for 1.9cm shift. Sampled via TBNA. ROSE: Suspicious for NSCLC."""
entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Galaxy navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "1.9cm", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "TBNA", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "Suspicious for NSCLC", 1)},
]
BATCH_DATA.append({"id": "1334901_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1334901
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Christopher Brown

Indication: Peripheral pulmonary nodule
Target: 13mm nodule in LLL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
VCV	10	351	14	100	5	24

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the LLL (LB10) based on the pre-operative CT navigational plan. Registration accuracy: 2.4mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 1.9cm divergence between the pre-op CT target and the actual lesion location due to respiratory motion.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Adjacent.

Transbronchial needle aspiration performed with 21G needle. 6 passes obtained. Samples sent for Cytology and Cell block.

ROSE Result: Suspicious for non-small cell carcinoma

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Brown, MD"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "13mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Noah Galaxy bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LB10", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.9cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "tomosynthesis (TiLT)", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "21G", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Suspicious for non-small cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": "1334901", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)