import sys
from pathlib import Path

# Set the root directory of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in a text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ==========================================
# Case 1: 1391425_syn_1
# ==========================================
text_1 = """Indication: RLL nodule (Brock high risk).
Tools: Galaxy, TiLT+, 22G Needle, Forceps, Fiducial.
Nav: 1.7cm divergence found on TiLT. Corrected.
Actions: rEBUS concentric. TBNA x7. Forceps x4. Brush. Gold fiducial placed.
ROSE: Suspicious for malignancy."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "TiLT+", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "22G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "TiLT", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 2)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious for malignancy", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 1391425_syn_2
# ==========================================
text_2 = """PROCEDURE: The patient was intubated for robotic bronchoscopy targeting a 9mm RLL nodule. The Galaxy system was utilized. Registration was performed (3.8mm error). Crucially, a TiLT+ spin demonstrated 1.7cm of target divergence. The virtual target was updated to match reality. rEBUS showed a concentric view. We performed TBNA, forceps biopsies, and brushing. A gold fiducial marker was deployed under TiLT-augmented fluoroscopy for future SBRT."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "robotic", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "brushing", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "TiLT", 2)},
    {"label": "PROC_METHOD", **get_span(text_2, "fluoroscopy", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 1391425_syn_3
# ==========================================
text_3 = """CPT Coding:
- 31626: Placement of fiducial markers (SBRT planning).
- 31629: TBNA.
- 31623: Brush.
- 31627: Navigation (Galaxy).
- 31654: rEBUS.
Note: TiLT+ used to verify tool-in-lesion."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "rEBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "TiLT+", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 1391425_syn_4
# ==========================================
text_4 = """Resident Note
Pt: E. Lewis
Case: RLL Nodule Biopsy + Fiducial
1. GA/ETT.
2. Nav to RB6.
3. TiLT showed 1.7cm divergence (atelectasis).
4. Adjusted.
5. rEBUS concentric (good view).
6. Samples: TBNA, Bx, Brush.
7. Dropped 1 fiducial.
8. ROSE: Suspicious."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Nodule", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RB6", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "TiLT", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "divergence", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Bx", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Suspicious", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 1391425_syn_5
# ==========================================
text_5 = """elizabeth lewis here for rll nodule biopsy and marker placement. galaxy robot used. pretty big divergence on the tilt spin 1.7cm so good thing we checked. fixed it. concentric view on ultrasound. did 7 needle passes 4 bites and a brush. put a gold marker in for radiation. rose looks suspicious for cancer."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "robot", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "tilt", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "concentric", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "7", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "4", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "suspicious for cancer", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 1391425_syn_6
# ==========================================
text_6 = """Suspicious nodule with high Brock score. 9mm nodule in RLL. General anesthesia. Galaxy robotic platform. Navigated to RB6. TiLT+ sweep generated updated 3D volume showing 1.7cm divergence. Target updated. rEBUS: Concentric. TBNA (22G), Forceps biopsy, Brush. Gold fiducial marker placed. ROSE: Suspicious for malignancy."""

entities_6 = [
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RB6", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "22G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "Suspicious for malignancy", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 1391425_syn_7
# ==========================================
text_7 = """[Indication]
9mm RLL nodule, high risk.
[Anesthesia]
GA.
[Description]
Galaxy nav to RB6. TiLT+ corrected 1.7cm divergence. rEBUS Concentric. TBNA, Bx, Brush done. Fiducial placed.
[Plan]
Oncology referral pending final path."""

entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RB6", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "divergence", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Bx", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Brush", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 1391425_syn_8
# ==========================================
text_8 = """We performed a robotic biopsy on [REDACTED] lobe nodule. The Galaxy system helped us navigate, and the TiLT+ feature was essential as it showed the nodule was 1.7cm away from the expected spot due to atelectasis. Once corrected, we got a concentric ultrasound view. We took multiple samples and placed a gold marker for future radiation therapy."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "TiLT+", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodule", 2)},
    {"label": "MEAS_SIZE", **get_span(text_8, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "atelectasis", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "concentric", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 1391425_syn_9
# ==========================================
text_9 = """Procedure: Robotic navigation and sampling.
Lesion: 9mm RLL.
Correction: TiLT+ detected a 1.7cm drift; we compensated.
Sampling: Needle aspiration, forceps extraction, and brushing were executed. A fiducial was implanted.
Outcome: ROSE suspicious."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Robotic", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "navigation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "9mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "1.7cm", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "Needle", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspiration", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "brushing", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "suspicious", 1)},
]
BATCH_DATA.append({"id": "1391425_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 1391425
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. James Rodriguez
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Suspicious nodule with high Brock score
Target: 9mm nodule in RLL

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t10\t342\t16\t80\t8\t20

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the RLL (RB6) based on the pre-operative CT navigational plan. Registration accuracy: 3.8mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 1.7cm divergence between the pre-op CT target and the actual lesion location due to atelectasis.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Concentric.

Transbronchial needle aspiration performed with 22G needle. 7 passes obtained. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed. 4 specimens obtained under fluoroscopic guidance with TiLT overlay. Samples sent for Surgical Pathology.

Cytology brushings obtained. Samples sent for Cytology.

Gold fiducial marker placed under TiLT-augmented fluoroscopic guidance for SBRT planning.

ROSE Result: Atypical cells present, suspicious for malignancy

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Rodriguez, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "9mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretions", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Navigational", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB6", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Tool-in-Lesion Tomosynthesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "divergence", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "atelectasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "augmented fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Concentric", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "22G", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "7 passes", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "4 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT", 4)},
    {"label": "SPECIMEN", **get_span(text_10, "Cytology brushings", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "TiLT", 5)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic", 2)},
    {"label": "OBS_ROSE", **get_span(text_10, "Atypical cells present", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "suspicious for malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Galaxy", 2)},
]
BATCH_DATA.append({"id": "1391425", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)