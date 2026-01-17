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
# 2. Data Definition
# ==========================================

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text: {text[:50]}...")
    return {"text": term, "start": start, "end": start + len(term)}

# ------------------------------------------
# Note 1: 1045878_syn_1
# ------------------------------------------
t1 = """Indication: PET-avid RLL nodule (15mm).
Anesthesia: GA, 8.0 ETT.
Technique: Monarch robotic nav to RLL (Anterior-Basal).
Verification: rEBUS (Adjacent).
Sampling: 22G TBNA x6 passes.
Result: ROSE atypical/cannot exclude malignancy.
Complications: None."""

e1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "OBS_LESION",    **get_span(t1, "nodule", 1)},
    {"label": "MEAS_SIZE",     **get_span(t1, "15mm", 1)},
    {"label": "PROC_METHOD",   **get_span(t1, "Monarch", 1)},
    {"label": "PROC_METHOD",   **get_span(t1, "robotic nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Anterior-Basal", 1)},
    {"label": "PROC_METHOD",   **get_span(t1, "rEBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t1, "22G", 1)},
    {"label": "PROC_ACTION",   **get_span(t1, "TBNA", 1)},
    {"label": "MEAS_COUNT",    **get_span(t1, "6 passes", 1)},
    {"label": "OBS_ROSE",      **get_span(t1, "atypical", 1)},
    {"label": "OBS_ROSE",      **get_span(t1, "malignancy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "None", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_1", "text": t1, "entities": e1})

# ------------------------------------------
# Note 2: 1045878_syn_2
# ------------------------------------------
t2 = """PROCEDURE: Robotic bronchoscopy with transbronchial needle aspiration. The patient, a male with a PET-avid 15mm nodule in the Right Lower Lobe, was placed under general anesthesia. We utilized the Monarch platform for navigation to the RB8 segment. Electromagnetic registration error was 2.2mm. Radial EBUS confirmed the target location (adjacent view). We performed 22G needle aspiration under direct visualization. Preliminary pathology (ROSE) revealed atypical cells, malignancy not excluded. The patient remained stable throughout."""

e2 = [
    {"label": "PROC_METHOD",   **get_span(t2, "Robotic", 1)},
    {"label": "PROC_ACTION",   **get_span(t2, "transbronchial needle aspiration", 1)},
    {"label": "MEAS_SIZE",     **get_span(t2, "15mm", 1)},
    {"label": "OBS_LESION",    **get_span(t2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Right Lower Lobe", 1)},
    {"label": "PROC_METHOD",   **get_span(t2, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "RB8", 1)},
    {"label": "PROC_METHOD",   **get_span(t2, "Electromagnetic", 1)},
    {"label": "MEAS_SIZE",     **get_span(t2, "2.2mm", 1)},
    {"label": "PROC_METHOD",   **get_span(t2, "Radial EBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t2, "22G", 1)},
    {"label": "PROC_ACTION",   **get_span(t2, "needle aspiration", 1)},
    {"label": "OBS_ROSE",      **get_span(t2, "atypical cells", 1)},
    {"label": "OBS_ROSE",      **get_span(t2, "malignancy", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_2", "text": t2, "entities": e2})

# ------------------------------------------
# Note 3: 1045878_syn_3
# ------------------------------------------
t3 = """Code Selection:
- 31629 (TBNA): Primary intervention, 6 passes with 22G needle.
- 31627 (Nav): Electromagnetic guidance used to reach RLL target.
- 31654 (rEBUS): Used to confirm peripheral lesion.
Note: No forceps or brush used (supports only 31629 for sampling).
Site: RLL Anterior-Basal Segment.
Outcome: ROSE atypical."""

e3 = [
    {"label": "PROC_ACTION",   **get_span(t3, "TBNA", 1)},
    {"label": "MEAS_COUNT",    **get_span(t3, "6 passes", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t3, "22G", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t3, "needle", 1)},
    {"label": "PROC_METHOD",   **get_span(t3, "Electromagnetic guidance", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RLL", 1)},
    {"label": "PROC_METHOD",   **get_span(t3, "rEBUS", 1)},
    {"label": "OBS_LESION",    **get_span(t3, "lesion", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t3, "forceps", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t3, "brush", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Anterior-Basal Segment", 1)},
    {"label": "OBS_ROSE",      **get_span(t3, "atypical", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_3", "text": t3, "entities": e3})

# ------------------------------------------
# Note 4: 1045878_syn_4
# ------------------------------------------
t4 = """Procedure: RLL Nodule Biopsy
Attending: Dr. Martinez
Fellow: Dr. Torres
Steps:
1. ETT placed.
2. Monarch nav to RLL (RB8).
3. rEBUS: Adjacent.
4. TBNA: 22G needle, 6 passes.
5. ROSE: Atypical cells.
6. No bleeding.
Plan: Monitor, discharge."""

e4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 1)},
    {"label": "OBS_LESION",    **get_span(t4, "Nodule", 1)},
    {"label": "PROC_ACTION",   **get_span(t4, "Biopsy", 1)},
    {"label": "PROC_METHOD",   **get_span(t4, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RB8", 1)},
    {"label": "PROC_METHOD",   **get_span(t4, "rEBUS", 1)},
    {"label": "PROC_ACTION",   **get_span(t4, "TBNA", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t4, "22G", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t4, "needle", 1)},
    {"label": "MEAS_COUNT",    **get_span(t4, "6 passes", 1)},
    {"label": "OBS_ROSE",      **get_span(t4, "Atypical cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t4, "No bleeding", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_4", "text": t4, "entities": e4})

# ------------------------------------------
# Note 5: 1045878_syn_5
# ------------------------------------------
t5 = """Hernandez John 15mm nodule in the RLL we used the robot today. Good registration 2.2mm. Navigated down to the anterior basal segment RB8. rEBUS showed it adjacent. Just did the needle today 22 gauge 6 passes. Cytology came back atypical cant rule out cancer. Patient did fine no bleeding extubated sent to PACU."""

e5 = [
    {"label": "MEAS_SIZE",     **get_span(t5, "15mm", 1)},
    {"label": "OBS_LESION",    **get_span(t5, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RLL", 1)},
    {"label": "PROC_METHOD",   **get_span(t5, "robot", 1)},
    {"label": "MEAS_SIZE",     **get_span(t5, "2.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "anterior basal segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "RB8", 1)},
    {"label": "PROC_METHOD",   **get_span(t5, "rEBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t5, "needle", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t5, "22 gauge", 1)},
    {"label": "MEAS_COUNT",    **get_span(t5, "6 passes", 1)},
    {"label": "OBS_ROSE",      **get_span(t5, "atypical", 1)},
    {"label": "OBS_ROSE",      **get_span(t5, "cancer", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no bleeding", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_5", "text": t5, "entities": e5})

# ------------------------------------------
# Note 6: 1045878_syn_6
# ------------------------------------------
t6 = """Robotic bronchoscopy was performed for a 15mm RLL nodule. Under general anesthesia, the Monarch endoscope was navigated to the anterior-basal segment. Registration error was 2.2mm. Radial EBUS showed an adjacent view. Transbronchial needle aspiration was performed using a 22G needle for 6 passes under fluoroscopic and endoscopic guidance. ROSE results showed atypical cells. No complications occurred."""

e6 = [
    {"label": "PROC_METHOD",   **get_span(t6, "Robotic", 1)},
    {"label": "MEAS_SIZE",     **get_span(t6, "15mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "RLL", 1)},
    {"label": "OBS_LESION",    **get_span(t6, "nodule", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t6, "Monarch endoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "anterior-basal segment", 1)},
    {"label": "MEAS_SIZE",     **get_span(t6, "2.2mm", 1)},
    {"label": "PROC_METHOD",   **get_span(t6, "Radial EBUS", 1)},
    {"label": "PROC_ACTION",   **get_span(t6, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t6, "22G", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t6, "needle", 1)},
    {"label": "MEAS_COUNT",    **get_span(t6, "6 passes", 1)},
    {"label": "PROC_METHOD",   **get_span(t6, "fluoroscopic", 1)},
    {"label": "OBS_ROSE",      **get_span(t6, "atypical cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_6", "text": t6, "entities": e6})

# ------------------------------------------
# Note 7: 1045878_syn_7
# ------------------------------------------
t7 = """[Indication]
PET-avid lung nodule, RLL (15mm).
[Anesthesia]
General, 8.0 ETT.
[Description]
Monarch nav to RB8. rEBUS: Adjacent. TBNA performed with 22G needle (6 passes). Continuous visualization maintained. ROSE: Atypical cells, cannot exclude malignancy.
[Plan]
Recovery, CXR, discharge."""

e7 = [
    {"label": "OBS_LESION",    **get_span(t7, "lung nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "MEAS_SIZE",     **get_span(t7, "15mm", 1)},
    {"label": "PROC_METHOD",   **get_span(t7, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RB8", 1)},
    {"label": "PROC_METHOD",   **get_span(t7, "rEBUS", 1)},
    {"label": "PROC_ACTION",   **get_span(t7, "TBNA", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t7, "22G", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t7, "needle", 1)},
    {"label": "MEAS_COUNT",    **get_span(t7, "6 passes", 1)},
    {"label": "OBS_ROSE",      **get_span(t7, "Atypical cells", 1)},
    {"label": "OBS_ROSE",      **get_span(t7, "malignancy", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_7", "text": t7, "entities": e7})

# ------------------------------------------
# Note 8: 1045878_syn_8
# ------------------------------------------
t8 = """We brought [REDACTED] the operating room to biopsy a 15mm nodule in his right lower lobe. Once he was asleep, we inserted the Monarch robotic scope and navigated to the target in the anterior-basal segment. The radial EBUS confirmed we were right next to the lesion. We decided to use a 22-gauge needle for aspiration and completed six passes. The preliminary results were atypical, so we couldn't rule out cancer yet. He handled the procedure well."""

e8 = [
    {"label": "PROC_ACTION",   **get_span(t8, "biopsy", 1)},
    {"label": "MEAS_SIZE",     **get_span(t8, "15mm", 1)},
    {"label": "OBS_LESION",    **get_span(t8, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "right lower lobe", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t8, "Monarch robotic scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "anterior-basal segment", 1)},
    {"label": "PROC_METHOD",   **get_span(t8, "radial EBUS", 1)},
    {"label": "OBS_LESION",    **get_span(t8, "lesion", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t8, "22-gauge", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t8, "needle", 1)},
    {"label": "PROC_ACTION",   **get_span(t8, "aspiration", 1)},
    {"label": "MEAS_COUNT",    **get_span(t8, "six passes", 1)},
    {"label": "OBS_ROSE",      **get_span(t8, "atypical", 1)},
    {"label": "OBS_ROSE",      **get_span(t8, "cancer", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_8", "text": t8, "entities": e8})

# ------------------------------------------
# Note 9: 1045878_syn_9
# ------------------------------------------
t9 = """Procedure: Robotic navigational bronchoscopy.
Site: RLL Anterior-Basal.
Action: The scope was guided to the target. rEBUS corroborated the location. The lesion was aspirated using a 22G needle. Six samples were collected.
Result: ROSE suggested atypical cells. No adverse events.
Disposition: Outpatient discharge."""

e9 = [
    {"label": "PROC_METHOD",   **get_span(t9, "Robotic navigational bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Anterior-Basal", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t9, "scope", 1)},
    {"label": "PROC_METHOD",   **get_span(t9, "rEBUS", 1)},
    {"label": "OBS_LESION",    **get_span(t9, "lesion", 1)},
    {"label": "PROC_ACTION",   **get_span(t9, "aspirated", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t9, "22G", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t9, "needle", 1)},
    {"label": "MEAS_COUNT",    **get_span(t9, "Six samples", 1)},
    {"label": "OBS_ROSE",      **get_span(t9, "atypical cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t9, "No adverse events", 1)}
]
BATCH_DATA.append({"id": "1045878_syn_9", "text": t9, "entities": e9})

# ------------------------------------------
# Note 10: 1045878 (Original)
# ------------------------------------------
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Robert Martinez
Fellow: LT Michelle Torres, MD (PGY-5)

Indication: PET-avid lung nodule
Target: 15mm nodule in RLL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PCV	11	296	11	80	5	16

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 2.2mm.

The device was navigated to the RLL. The outer sheath was parked and locked at the ostium of the segmental airway (RB8) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Anterior-Basal Segment of RLL.

Radial EBUS performed via the working channel. rEBUS view: Adjacent. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 22G aspiration needle under direct endoscopic and fluoroscopic guidance. 6 passes performed. Samples sent for Cytology and Cell block.

ROSE Result: Atypical cells, cannot exclude malignancy

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Martinez, MD"""

e10 = [
    {"label": "OBS_LESION",    **get_span(t10, "lung nodule", 1)},
    {"label": "MEAS_SIZE",     **get_span(t10, "15mm", 1)},
    {"label": "OBS_LESION",    **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(t10, "carina", 1)},
    {"label": "OBS_FINDING",   **get_span(t10, "secretions", 1)},
    {"label": "ANAT_PLEURA",   **get_span(t10, "anterior chest wall", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t10, "Monarch robotic endoscope", 1)},
    {"label": "PROC_METHOD",   **get_span(t10, "Electromagnetic", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(t10, "main carina", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(t10, "right and left mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY",   **get_span(t10, "lobar carinas", 1)},
    {"label": "MEAS_SIZE",     **get_span(t10, "2.2mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 2)},
    {"label": "DEV_INSTRUMENT",**get_span(t10, "sheath", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RB8", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t10, "scope", 1)},
    {"label": "OBS_LESION",    **get_span(t10, "lesion", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Anterior-Basal Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "RLL", 3)},
    {"label": "PROC_METHOD",   **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD",   **get_span(t10, "rEBUS", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t10, "needle", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t10, "scope", 2)},
    {"label": "PROC_ACTION",   **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t10, "22G", 1)},
    {"label": "DEV_NEEDLE",    **get_span(t10, "aspiration needle", 1)},
    {"label": "PROC_METHOD",   **get_span(t10, "endoscopic", 1)},
    {"label": "PROC_METHOD",   **get_span(t10, "fluoroscopic", 1)},
    {"label": "MEAS_COUNT",    **get_span(t10, "6 passes", 1)},
    {"label": "SPECIMEN",      **get_span(t10, "Cell block", 1)},
    {"label": "OBS_ROSE",      **get_span(t10, "Atypical cells", 1)},
    {"label": "OBS_ROSE",      **get_span(t10, "malignancy", 1)},
    {"label": "DEV_INSTRUMENT",**get_span(t10, "scope", 3)},
    {"label": "DEV_INSTRUMENT",**get_span(t10, "sheath", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no significant bleeding", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate complications", 1)}
]
BATCH_DATA.append({"id": "1045878", "text": t10, "entities": e10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)