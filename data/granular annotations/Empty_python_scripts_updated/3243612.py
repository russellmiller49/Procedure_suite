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
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3243612_syn_1
# ==========================================
t1 = """Indication: Lung-RADS 4B nodule, Lingula.
Anesthesia: GA, ETT.
Device: Noah Galaxy.
Action: Navigated to LB4. TiLT+ sweep showed 1.8cm divergence. Adjusted. Confirmed via rEBUS (adjacent).
Sampling:
- TBNA 22G: 5 passes.
- Forceps: 4 samples.
- Brush: 1 sample.
ROSE: SqCC.
Plan: Recovery. CXR."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Noah Galaxy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "22G", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "5 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "4 samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Brush", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "1 sample", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "SqCC", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 3243612_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: The patient was brought to the endoscopy suite for investigation of a Lingular nodule. Following the induction of general anesthesia, the Noah Galaxy robotic platform was deployed. Initial registration yielded a 2.1mm accuracy. Intraprocedural Tool-in-Lesion Tomosynthesis (TiLT+) id[REDACTED] a significant divergence of 1.8cm, likely secondary to positioning. The target was realigned utilizing augmented fluoroscopy. Radial EBUS confirmed an adjacent signature. Extensive sampling was performed via transbronchial needle aspiration and forceps biopsy. Rapid On-Site Evaluation was positive for malignant cells consistent with squamous cell carcinoma."""

e2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Lingular", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Noah Galaxy robotic platform", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "2.1mm", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Tool-in-Lesion Tomosynthesis (TiLT+)", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "augmented fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "transbronchial needle aspiration", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 3243612_syn_3
# ==========================================
t3 = """Procedure Codes Justification:
- 31629 (TBNA): Performed on Lingula lesion using 22G needle.
- 31623 (Brush): Cytology brushing performed on same site.
- 31627 (Navigational Bronchoscopy): Galaxy robotic system used for guidance.
- 31654 (rEBUS): Radial probe used for localization.
Note: TiLT+ tomosynthesis was utilized for divergence correction (1.8cm)."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "TBNA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t3, "lesion", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Brush", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "brushing", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Navigational Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "Galaxy robotic system", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "Radial probe", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "TiLT+ tomosynthesis", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "1.8cm", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 3243612_syn_4
# ==========================================
t4 = """Resident Procedure Note
Patient: [REDACTED]
Attending: Dr. Wilson
Procedure: Robotic Bronchoscopy (Galaxy)
Steps:
1. ETT placed.
2. Galaxy registered (2.1mm error).
3. TiLT+ sweep done; found 1.8cm divergence.
4. Adjusted to new target.
5. rEBUS: Adjacent.
6. Biopsied: TBNA x5, Forceps x4, Brush.
7. ROSE positive for SqCC.
No complications."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Robotic Bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Galaxy", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Galaxy", 2)},
    {"label": "MEAS_SIZE", **get_span(t4, "2.1mm", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsied", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "SqCC", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No complications", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 3243612_syn_5
# ==========================================
t5 = """patient [REDACTED] here for lung nodule biopsy used the galaxy robot today under general anesthesia tube was fine. navigated to the lingula lb4 registered ok. did the tilt spin and saw the nodule was way off like 1.8cm so we fixed that on the screen. confirmed with rebus then did tbna forceps and brush rose came back squamous cell so we stopped. patient woke up ok sending to recovery thanks."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "lung nodule", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "galaxy robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lb4", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "tilt", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 2)},
    {"label": "MEAS_SIZE", **get_span(t5, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rebus", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "tbna", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "squamous cell", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 3243612_syn_6
# ==========================================
t6 = """Lung-RADS 4B nodule. 26mm nodule in Lingula. General anesthesia. Noah Galaxy bronchoscope introduced. Navigational registration performed. Scope navigated to LB4. Tool-in-Lesion Tomosynthesis (TiLT+) sweep performed. 1.8cm divergence noted and corrected. Radial EBUS view: Adjacent. Transbronchial needle aspiration (22G, 5 passes). Transbronchial forceps biopsy (4 specimens). Cytology brushings. ROSE Result: Malignant cells id[REDACTED], consistent with squamous cell carcinoma. No complications."""

e6 = [
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "26mm", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Noah Galaxy bronchoscope", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Navigational", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Tool-in-Lesion Tomosynthesis (TiLT+)", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Radial EBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "22G", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "5 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "4 specimens", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Cytology brushings", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 3243612_syn_7
# ==========================================
t7 = """[Indication]
Lung-RADS 4B nodule (26mm, Lingula).
[Anesthesia]
General, ETT.
[Description]
Galaxy robotic scope used. Registration error 2.1mm. TiLT+ id[REDACTED] 1.8cm divergence; target updated. rEBUS: Adjacent. Sampling: TBNA (5 passes), Forceps (4 samples), Brush.
[Plan]
Results conference 5-7 days. CXR."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "26mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Galaxy robotic scope", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "2.1mm", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "5 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "4 samples", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Brush", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 3243612_syn_8
# ==========================================
t8 = """[REDACTED] biopsy of a 26mm Lingular nodule. We utilized the Noah Galaxy robotic system. After intubation, we navigated to the target but noted a 1.8cm divergence on the TiLT+ spin, which we corrected. We confirmed the location with rEBUS and proceeded to sample the lesion using a needle, forceps, and brush. The on-site pathologist confirmed squamous cell carcinoma."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "26mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "Lingular", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Noah Galaxy robotic system", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "1.8cm", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "TiLT+", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "rEBUS", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lesion", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 3243612_syn_9
# ==========================================
t9 = """Context: Lung-RADS 4B mass.
Technique: The Galaxy scope was piloted to the Lingula. A TiLT+ scan exposed a 1.8cm deviation, which was rectified. The lesion was localized via rEBUS. We aspirated the site with a 22G needle, harvested tissue with forceps, and brushed the area.
Result: ROSE indicated squamous cell carcinoma."""

e9 = [
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Galaxy scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "TiLT+", 1)},
    {"label": "MEAS_SIZE", **get_span(t9, "1.8cm", 1)},
    {"label": "OBS_LESION", **get_span(t9, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "brushed", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "squamous cell carcinoma", 1)},
]
BATCH_DATA.append({"id": "3243612_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 3243612
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. David Wilson
Fellow: Dr. Alex Chen (PGY-5)

Indication: Lung-RADS 4B nodule
Target: 26mm nodule in Lingula

PROCEDURE:

After successful induction of general anesthesia, a timeout was performed. ETT secured in good position.

Initial Airway Inspection:
Trachea normal caliber, carina sharp. Bilateral airways inspected to subsegmental level. No endobronchial lesions. Minimal secretions cleared.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PRVC\t13\t293\t8\t80\t5\t17

The single-use disposable Noah Galaxy bronchoscope was introduced into the airway. Navigational registration was performed using the electromagnetic field generator placed beneath the patient.

The scope was navigated to the approximate target location in the Lingula (LB4) based on the pre-operative CT navigational plan. Registration accuracy: 2.1mm.

Once in the target vicinity, a Tool-in-Lesion Tomosynthesis (TiLT+) sweep was performed using the C-arm. The system generated an updated intra-operative 3D volume, revealing a 1.8cm divergence between the pre-op CT target and the actual lesion location due to patient positioning.

The augmented reality target was updated on the navigation screen to match real-time anatomy. Intra-operative tomosynthesis (TiLT) performed to update target location and correct for divergence.

The scope was adjusted to align with the corrected TiLT target. Confirmation of tool position was verified using the augmented fluoroscopy overlay provided by the TiLT system.

Radial EBUS performed to confirm lesion location. rEBUS view: Adjacent.

Transbronchial needle aspiration performed with 22G needle. 5 passes obtained. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed. 4 specimens obtained under fluoroscopic guidance with TiLT overlay. Samples sent for Surgical Pathology.

Cytology brushings obtained. Samples sent for Cytology.

ROSE Result: Malignant cells id[REDACTED], consistent with squamous cell carcinoma

Final airway inspection performed - no significant bleeding or complications. The disposable Galaxy scope was removed and discarded at the end of the case.

Patient [REDACTED] well. No immediate complications.

DISPOSITION: Recovery, post-procedure CXR, discharge if stable.
Follow-up: Results conference in 5-7 days.

Wilson, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "26mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Noah Galaxy bronchoscope", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Navigational", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB4", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "2.1mm", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Tool-in-Lesion Tomosynthesis (TiLT+)", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "1.8cm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "tomosynthesis (TiLT)", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "augmented fluoroscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "22G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 passes", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cytology", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "4 specimens", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Cytology brushings", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cytology", 2)},
    {"label": "OBS_ROSE", **get_span(t10, "Malignant cells", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "squamous cell carcinoma", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no significant bleeding or complications", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": "3243612", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)