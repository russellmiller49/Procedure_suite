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
# Note 1: 459598_syn_1
# ==========================================
text_1 = """Target: 22mm RLL nodule.
Tool: Galaxy + TiLT+.
Div: 2.3cm (atelectasis). Corrected.
rEBUS: Adjacent.
Action: TBNA x4, Bx x4, BAL, Fiducial.
ROSE: Suspicious NSCLC."""

entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "22mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.3cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bx", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious NSCLC", 1)},
]
BATCH_DATA.append({"id": "459598_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 459598_syn_2
# ==========================================
text_2 = """OPERATIVE SUMMARY: [REDACTED] bronchoscopy for a 22mm RLL nodule. The Galaxy system was deployed to RB10. TiLT+ imaging revealed a significant 2.3cm divergence due to atelectasis, which was corrected. rEBUS showed an adjacent view. We performed TBNA, forceps biopsy, and BAL. A fiducial marker was placed for SBRT. ROSE suggests non-small cell carcinoma."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "22mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Galaxy system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RB10", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "2.3cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "BAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": "459598_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 459598_syn_3
# ==========================================
text_3 = """Codes: 31626 (Marker), 31629 (TBNA), 31624 (BAL), 31627 (Nav), 31654 (rEBUS).
Note: 2.3cm divergence corrected via TiLT+."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "BAL", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "rEBUS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "2.3cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "TiLT+", 1)},
]
BATCH_DATA.append({"id": "459598_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 459598_syn_4
# ==========================================
text_4 = """Resident Note
Pt: C. Rodriguez
RLL 22mm
1. Galaxy to RB10.
2. TiLT found 2.3cm error (atelectasis).
3. Adjusted.
4. rEBUS adjacent.
5. TBNA, Bx, BAL.
6. Fiducial placed.
ROSE: Suspicious NSCLC."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "22mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RB10", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "2.3cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Bx", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Suspicious NSCLC", 1)},
]
BATCH_DATA.append({"id": "459598_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 459598_syn_5
# ==========================================
text_5 = """charles rodriguez rll nodule. galaxy robot. huge divergence on tilt 2.3cm atelectasis. fixed it. adjacent ultrasound. needle biopsy forceps and a wash. put a fiducial in. rose thinks its non small cell cancer."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "galaxy robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "tilt", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "2.3cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "wash", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "non small cell cancer", 1)},
]
BATCH_DATA.append({"id": "459598_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 459598_syn_6
# ==========================================
text_6 = """Multiple pulmonary nodules. 22mm nodule in RLL. General anesthesia. Noah Galaxy bronchoscope. Navigated to RB10. TiLT+ sweep revealed 2.3cm divergence due to atelectasis. Target updated. rEBUS view: Adjacent. TBNA (22G). Transbronchial forceps biopsy. Bronchoalveolar lavage. Gold fiducial marker placed. ROSE Result: Suspicious for non-small cell carcinoma."""

entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "pulmonary nodules", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "22mm", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Noah Galaxy bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RB10", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "2.3cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "22G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Bronchoalveolar lavage", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "Suspicious for non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": "459598_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 459598_syn_7
# ==========================================
text_7 = """[Indication]
22mm RLL nodule.
[Anesthesia]
GA.
[Description]
Galaxy nav. TiLT+ corrected 2.3cm divergence. rEBUS adjacent. TBNA, Bx, BAL, Fiducial.
[Plan]
Oncology."""

entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "22mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Galaxy nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "2.3cm", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Bx", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Fiducial", 1)},
]
BATCH_DATA.append({"id": "459598_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 459598_syn_8
# ==========================================
text_8 = """[REDACTED] a robotic biopsy. The Galaxy system's TiLT+ feature helped us correct a 2.3cm error caused by lung collapse. We sampled the area with a needle, forceps, and wash, and placed a marker. It looks suspicious for lung cancer."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Galaxy system's", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "2.3cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "lung collapse", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "wash", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "suspicious for lung cancer", 1)},
]
BATCH_DATA.append({"id": "459598_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 459598_syn_9
# ==========================================
text_9 = """Procedure: Robotic RLL biopsy + marker.
Correction: TiLT+ fixed 2.3cm offset.
Sampling: TBNA, forceps, BAL.
Marker: Fiducial implanted.
Result: Suspicious for NSCLC."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "marker", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "2.3cm", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "BAL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Fiducial", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "Suspicious for NSCLC", 1)},
]
BATCH_DATA.append({"id": "459598_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 459598
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Amanda Garcia
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Multiple pulmonary nodules - dominant lesion biopsy
Target: 22mm nodule in RLL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PRVC\t10\t375\t12\t80\t8\t24

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the RLL (RB10) based on the pre-operative CT navigational plan. Registration accuracy: 3.2mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 2.3cm divergence between the pre-op CT target and the actual lesion location due to atelectasis.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Adjacent.

Transbronchial needle aspiration performed with 22G needle. 4 passes obtained. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed. 4 specimens obtained under fluoroscopic guidance with TiLT overlay. Samples sent for Surgical Pathology.

Bronchoalveolar lavage performed at target segment. 40mL instilled, 16mL return. Sent for Cytology and Culture.

Gold fiducial marker placed under TiLT-augmented fluoroscopic guidance for SBRT planning.

ROSE Result: Suspicious for non-small cell carcinoma

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Garcia, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "pulmonary nodules", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "22mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Noah Galaxy bronchoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB10", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Tool-in-Lesion Tomosynthesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.3cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Intra-operative tomosynthesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 passes", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoalveolar lavage", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "40mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "16mL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "fiducial marker", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Suspicious for non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": "459598", "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)