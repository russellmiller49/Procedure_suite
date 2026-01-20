import sys
from pathlib import Path

# Set up the repository root directory
# (Assumes this script is running in a subdirectory of the repo, e.g., scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repo root to sys.path to allow imports from scripts.
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
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
# Note 1: 4888069_syn_1
# ==========================================
t1 = """Target: 14mm Lingula (LB5).
Robot: Monarch.
rEBUS: Eccentric.
Bx: 19G TBNA x5, Forceps x5, Brush.
Wash: BAL LB5.
ROSE: Benign/Lymphocytes."""

e1 = [
    {"label": "MEAS_SIZE", **get_span(t1, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t1, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "x5", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LB5", 2)},
    {"label": "OBS_ROSE", **get_span(t1, "Benign", 1)},
    {"label": "OBS_ROSE", **get_span(t1, "Lymphocytes", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 4888069_syn_2
# ==========================================
t2 = """NARRATIVE: The patient underwent robotic bronchoscopy for a 14mm nodule in the Inferior Lingula. Navigation to LB5 was successful (4.7mm error). Radial EBUS showed an eccentric view. We performed 19G TBNA (5 passes), Forceps Biopsy (5 specimens), and Protected Brushing. BAL was also performed. ROSE showed lymphocytes and benign cells."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "robotic bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "Inferior Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Navigation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t2, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "5 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(t2, "5 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "Brushing", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(t2, "benign cells", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 4888069_syn_3
# ==========================================
t3 = """CPT: 31629, 31628, 31623, 31627, 31654, 31624. Full sampling suite used on 14mm Lingula nodule. 19G needle, forceps, brush, and lavage."""

e3 = [
    {"label": "MEAS_SIZE", **get_span(t3, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t3, "nodule", 1)},
    {"label": "DEV_NEEDLE", **get_span(t3, "19G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "lavage", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 4888069_syn_4
# ==========================================
t4 = """Monarch Case.
Lingula nodule.
1. Nav to LB5.
2. rEBUS Eccentric.
3. 19G Needle x 5.
4. Forceps x 5.
5. Brush.
6. BAL.
ROSE: Benign."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t4, "19G", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x 5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "x 5", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t4, "Benign", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 4888069_syn_5
# ==========================================
t5 = """edward hall lingula nodule 14mm robotic bronch used monarch nav to lb5 rebus eccentric 19g needle 5 passes forceps 5 passes brush and bal rose benign lymphocytes pt did fine."""

e5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lingula", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t5, "14mm", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "robotic bronch", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "monarch", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "lb5", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "rebus", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t5, "19g", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "5 passes", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "bal", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "benign", 1)},
    {"label": "OBS_ROSE", **get_span(t5, "lymphocytes", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 4888069_syn_6
# ==========================================
t6 = """General anesthesia. Monarch robot used. Navigated to Lingula LB5. rEBUS eccentric. 19G TBNA x 5. Forceps x 5. Brush. BAL. ROSE benign. No complications."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "robot", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t6, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "x 5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "x 5", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t6, "benign", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t6, "No complications", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 4888069_syn_7
# ==========================================
t7 = """[Indication] 14mm Lingula nodule.
[Anesthesia] General.
[Description] Nav to LB5. rEBUS eccentric. 19G TBNA x5. Forceps x5. Brush. BAL. ROSE benign.
[Plan] Discharge."""

e7 = [
    {"label": "MEAS_SIZE", **get_span(t7, "14mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(t7, "nodule", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t7, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x5", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "x5", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(t7, "benign", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 4888069_syn_8
# ==========================================
t8 = """We navigated the robotic scope to the inferior lingula segment. Radial EBUS showed an eccentric view of the target. We performed five needle passes with a 19-gauge needle, followed by five forceps biopsies and brushing. A lavage was also collected. The on-site evaluation showed only benign cells and lymphocytes."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "robotic scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "inferior lingula segment", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "eccentric", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "five", 1)},
    {"label": "DEV_NEEDLE", **get_span(t8, "19-gauge", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "five", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "brushing", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "benign cells", 1)},
    {"label": "OBS_ROSE", **get_span(t8, "lymphocytes", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 4888069_syn_9
# ==========================================
t9 = """The robotic device was steered to the Lingula. Registration error was 4.7mm. The probe was anchored at LB5. Ultrasound showed an eccentric lesion. 19G aspiration (5x), forceps extraction (5x), and brushing were performed. Lavage was done. Pathology was benign."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "robotic device", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "LB5", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "eccentric", 1)},
    {"label": "DEV_NEEDLE", **get_span(t9, "19G", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "5x", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "extraction", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "5x", 2)},
    {"label": "PROC_ACTION", **get_span(t9, "brushing", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "Lavage", 1)},
    {"label": "OBS_ROSE", **get_span(t9, "benign", 1)}
]
BATCH_DATA.append({"id": "4888069_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 4888069
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: 7/19/1950
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Jennifer Lee
Fellow: Dr. Kevin Patel (PGY-5)

Indication: Growing lung nodule on surveillance
Target: 14mm nodule in Lingula

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
PCV\t13\t350\t13\t80\t5\t23

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 4.7mm.

The device was navigated to the Lingula. The outer sheath was parked and locked at the ostium of the segmental airway (LB5) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Inferior Lingula.

Radial EBUS performed via the working channel. rEBUS view: Eccentric. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 19G aspiration needle under direct endoscopic and fluoroscopic guidance. 5 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 5 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

Bronchoalveolar lavage performed at LB5. 60mL NS instilled with 22mL return. Sent for Cell count, Culture, and Cytology.

ROSE Result: Lymphocytes and benign cells, adequate for evaluation

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Lee, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "lung nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "14mm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "carina", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Monarch robotic endoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "right and left mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "lobar carinas", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Lingula", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB5", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "Inferior Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "Eccentric", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(t10, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "fluoroscopic", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 passes", 1)},
    {"label": "SPECIMEN", **get_span(t10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "5 specimens", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "cytology brushings", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "LB5", 2)},
    {"label": "MEAS_VOL", **get_span(t10, "60mL", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "22mL", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "Lymphocytes", 1)},
    {"label": "OBS_ROSE", **get_span(t10, "benign cells", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "No immediate complications", 1)}
]
BATCH_DATA.append({"id": "4888069", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)