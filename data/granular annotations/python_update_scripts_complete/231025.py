import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
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
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 231025_syn_1
# ==========================================
t1 = """Target: 33mm RML (RB4).
Tech: Monarch.
rEBUS: Concentric.
Bx: 19G TBNA x5, Forceps x7, Brush.
No BAL.
ROSE: Benign."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "33mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RB4", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Benign", 1)}
]
BATCH_DATA.append({"id": "231025_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 231025_syn_2
# ==========================================
t2 = """NARRATIVE: Robotic bronchoscopy for 33mm RML nodule. Navigation to Lateral Segment (RB4) achieved. rEBUS showed concentric view. 19G TBNA (5 passes), Forceps (7 specimens), and Brush biopsy performed. No lavage. ROSE benign."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Robotic", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "33mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Lateral Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB4", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "5 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "7 specimens", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "benign", 1)}
]
BATCH_DATA.append({"id": "231025_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 231025_syn_3
# ==========================================
t3 = """CPT: 31629, 31628, 31623, 31627, 31654. No BAL. 19G needle, forceps, brush used on RML nodule. rEBUS concentric."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "BAL", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "19G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "brush", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "concentric", 1)}
]
BATCH_DATA.append({"id": "231025_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 231025_syn_4
# ==========================================
t4 = """Monarch Case.
RML nodule.
1. Nav to RB4.
2. rEBUS Concentric.
3. 19G Needle x 5.
4. Forceps x 7.
5. Brush.
ROSE: Benign."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB4", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "19G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "Needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x 5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x 7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Benign", 1)}
]
BATCH_DATA.append({"id": "231025_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 231025_syn_5
# ==========================================
t5 = """[REDACTED] rml nodule 33mm robotic bronch monarch used navigated to rb4 rebus concentric 19g needle 5 passes forceps 7 passes brush rose benign no bal done."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rml", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "33mm", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "robotic bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "rb4", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rebus", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "19g", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "7 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "benign", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "bal", 1)}
]
BATCH_DATA.append({"id": "231025_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 231025_syn_6
# ==========================================
t6 = """Anesthesia induced. Monarch robot navigated to RML RB4. rEBUS concentric. 19G TBNA x 5. Forceps x 7. Brush. ROSE benign. No BAL. Patient stable."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RB4", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "x 5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "x 7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "benign", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "BAL", 1)}
]
BATCH_DATA.append({"id": "231025_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 231025_syn_7
# ==========================================
t7 = """[Indication] 33mm RML nodule.
[Anesthesia] General.
[Description] Nav to RB4. rEBUS concentric. 19G TBNA x5. Forceps x7. Brush. ROSE benign.
[Plan] Discharge."""

e7 = [
    {"label": "MEAS_SIZE", **get_span(t7, "33mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RML", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB4", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Brush", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "benign", 1)}
]
BATCH_DATA.append({"id": "231025_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 231025_syn_8
# ==========================================
t8 = """We used the Monarch robot to navigate to the lateral segment of the right middle lobe. Radial EBUS showed a concentric view of the large 33mm nodule. We performed five passes with a 19-gauge needle, followed by seven forceps biopsies and brushing. The on-site evaluation was benign."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "lateral segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right middle lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "concentric", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "33mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "five", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "19-gauge", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "seven", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "brushing", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "benign", 1)}
]
BATCH_DATA.append({"id": "231025_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 231025_syn_9
# ==========================================
t9 = """The robotic system was piloted to the RML. The instrument reached RB4. Sonography indicated a concentric mass. Aspiration via 19G needle was conducted 5 times. Tissue extraction via forceps occurred 7 times. Brushing was performed. Initial pathology was benign."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "robotic system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RB4", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Sonography", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "concentric", 1)},
    {"label": "OBS_LESION", **get_span(t9, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "19G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "needle", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "5 times", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "7 times", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Brushing", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "benign", 1)}
]
BATCH_DATA.append({"id": "231025_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 231025
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams

Indication: Incidental pulmonary nodule requiring tissue diagnosis
Target: 33mm nodule in RML

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t10\t287\t8\t80\t8\t16

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 2.2mm.

The device was navigated to the RML. The outer sheath was parked and locked at the ostium of the segmental airway (RB4) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Lateral Segment of RML.

Radial EBUS performed via the working channel. rEBUS view: Concentric. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 19G aspiration needle under direct endoscopic and fluoroscopic guidance. 5 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 7 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

ROSE Result: Lymphocytes and benign cells, adequate for evaluation

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Williams, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "pulmonary nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "33mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "anterior chest wall", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "robotic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "endoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "right and left mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "lobar carinas", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lateral Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RML", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Concentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "needle", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "19G", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "aspiration needle", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "fluoroscopic", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "cytology brushings", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "benign cells", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "robotic system", 1)}
]
BATCH_DATA.append({"id": "231025", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)