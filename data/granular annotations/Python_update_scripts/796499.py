import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from inside the repo)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to sys.path to access the utility function
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            return None  # Occurence not found
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 796499_syn_1
# ==========================================
t1 = """Indication: 10mm LUL GGO.
Procedure:
- Monarch nav to LB3.
- rEBUS: Adjacent.
- TBNA (19G), Forceps x7, Brush, BAL.
ROSE: Benign.
Plan: D/C."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "10mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t1, "GGO", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LB3", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "19G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Benign", 1)}
]

BATCH_DATA.append({"id": "796499_syn_1", "text": t1, "entities": e1})


# ==========================================
# Note 2: 796499_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: [REDACTED] bronchoscopy for a 10mm ground glass opacity in the Anterior Segment of the LUL. Navigation was performed via the Monarch platform to LB3. Radial EBUS demonstrated an adjacent view. We utilized a 19G needle for TBNA, followed by forceps biopsies and protected brushings. A BAL was performed. ROSE showed benign respiratory epithelium and macrophages."""

e2 = [
    {"label": "MEAS_SIZE", **get_span(t2, "10mm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "ground glass opacity", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LUL", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Navigation", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LB3", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "benign", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "respiratory epithelium", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "macrophages", 1)}
]

BATCH_DATA.append({"id": "796499_syn_2", "text": t2, "entities": e2})


# ==========================================
# Note 3: 796499_syn_3
# ==========================================
t3 = """Billing: 31629, 31628, 31623, 31624, 31627, 31654.
Site: LUL Anterior (LB3).
Note: 19G needle used.
Outcome: Benign ROSE."""

e3 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Anterior", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "LB3", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "19G", 1)},
    {"label": "OBS_ROSE", **get_span(t3, "Benign", 1)}
]

BATCH_DATA.append({"id": "796499_syn_3", "text": t3, "entities": e3})


# ==========================================
# Note 4: 796499_syn_4
# ==========================================
t4 = """Trainee Note
Pt: [REDACTED].
Loc: LUL 10mm.
Steps:
1. GA.
2. Nav to LB3.
3. rEBUS adjacent.
4. 19G TBNA x5.
5. Forceps x7.
6. Brush.
7. BAL.
ROSE: Benign.
Complications: None."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LUL", 1)},
    {"label": "MEAS_SIZE", **get_span(t4, "10mm", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LB3", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Benign", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "None", 1)}
]

BATCH_DATA.append({"id": "796499_syn_4", "text": t4, "entities": e4})


# ==========================================
# Note 5: 796499_syn_5
# ==========================================
t5 = """Andrew Adams 10mm nodule LUL anterior segment. Used the monarch robot registration 2.9mm. Went to LB3 rEBUS adjacent. Used the 19 gauge needle forceps brush and did a wash. ROSE says benign. Patient doing fine."""

e5 = [
    {"label": "MEAS_SIZE", **get_span(t5, "10mm", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "monarch robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "LB3", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "19 gauge", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "wash", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "benign", 1)}
]

BATCH_DATA.append({"id": "796499_syn_5", "text": t5, "entities": e5})


# ==========================================
# Note 6: 796499_syn_6
# ==========================================
t6 = """Robotic bronchoscopy was performed for a 10mm LUL nodule. The Monarch system was navigated to the anterior segment (LB3). rEBUS showed an adjacent view. Sampling included 19G TBNA, forceps biopsy, brushings, and BAL. ROSE results were benign. The patient tolerated the procedure without complications."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Robotic", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "10mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LUL", 1)},
    {"label": "OBS_LESION", **get_span(t6, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Monarch system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "anterior segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LB3", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "brushings", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "benign", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "without complications", 1)}
]

BATCH_DATA.append({"id": "796499_syn_6", "text": t6, "entities": e6})


# ==========================================
# Note 7: 796499_syn_7
# ==========================================
t7 = """[Indication]
Ground glass opacity, LUL (10mm).
[Anesthesia]
General, 8.0 ETT.
[Description]
Monarch nav to LB3. rEBUS: Adjacent. Sampling: 19G TBNA, Forceps, Brush, BAL. ROSE: Benign.
[Plan]
CXR, Discharge."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Ground glass opacity", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LUL", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "10mm", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LB3", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "Benign", 1)}
]

BATCH_DATA.append({"id": "796499_syn_7", "text": t7, "entities": e7})


# ==========================================
# Note 8: 796499_syn_8
# ==========================================
t8 = """[REDACTED] for a biopsy of a small 10mm nodule in his left upper lobe. We used the robotic system to navigate to the anterior segment. EBUS confirmed we were adjacent to the lesion. We took samples with a 19-gauge needle, forceps, and brush, and also washed the area. The preliminary results were benign. He recovered well."""

e8 = [
    {"label": "PROC_ACTION", **get_span(t8, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t8, "10mm", 1)},
    {"label": "OBS_LESION", **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "left upper lobe", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "robotic system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "anterior segment", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "EBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "19-gauge", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "washed", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "benign", 1)}
]

BATCH_DATA.append({"id": "796499_syn_8", "text": t8, "entities": e8})


# ==========================================
# Note 9: 796499_syn_9
# ==========================================
t9 = """Procedure: Robotic navigational bronchoscopy.
Site: LUL Anterior Segment.
Action: The scope was navigated to the target. rEBUS verified the position. The lesion was aspirated, biopsied, and brushed. Lavage was performed.
Result: ROSE indicated benign findings."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "Robotic navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Anterior Segment", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspirated", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "biopsied", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "brushed", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "benign", 1)}
]

BATCH_DATA.append({"id": "796499_syn_9", "text": t9, "entities": e9})


# ==========================================
# Note 10: 796499
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Jennifer Lee
Fellow: LT Michelle Torres, MD (PGY-5)

Indication: Ground glass opacity requiring biopsy
Target: 10mm nodule in LUL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PRVC	14	282	13	100	6	21

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 2.9mm.

The device was navigated to the LUL. The outer sheath was parked and locked at the ostium of the segmental airway (LB3) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Anterior Segment of LUL.

Radial EBUS performed via the working channel. rEBUS view: Adjacent. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 19G aspiration needle under direct endoscopic and fluoroscopic guidance. 5 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 7 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

Bronchoalveolar lavage performed at LB3. 40mL NS instilled with 19mL return. Sent for Cell count, Culture, and Cytology.

ROSE Result: Benign respiratory epithelium and macrophages

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Lee, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "Ground glass opacity", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "10mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Monarch robotic endoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "right and left mainstem bronchi", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB3", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Anterior Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LUL", 3)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "19G", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 passes", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "7 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "cytology brushings", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB3", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "40mL", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "19mL", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Benign respiratory epithelium and macrophages", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate complications", 1)}
]

BATCH_DATA.append({"id": "796499", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)