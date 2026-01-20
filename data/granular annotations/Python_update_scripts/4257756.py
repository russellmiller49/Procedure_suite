import sys
from pathlib import Path

# Add the repository root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a substring.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 4257756_syn_1
# ==========================================
text_1 = """Loc: 20mm RLL (RB8).
Robot: Monarch.
rEBUS: Concentric.
Bx: 21G TBNA x6, Forceps x7, Brush.
Wash: BAL RB8.
ROSE: Atypical/Suspicious."""

entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "20mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RB8", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RB8", 2)},
    {"label": "OBS_ROSE", **get_span(text_1, "Atypical", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4257756_syn_2
# ==========================================
text_2 = """PROCEDURE: Robotic bronchoscopy for 20mm RLL nodule. Navigation to Anterior-Basal Segment (RB8) completed (4.8mm error). rEBUS confirmed concentric view. 21G TBNA (6 passes), Forceps (7 specimens), and Brush biopsy performed. BAL collected. ROSE suspicious for malignancy."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Robotic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "20mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Anterior-Basal Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RB8", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "6 passes", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "7 specimens", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "suspicious", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "malignancy", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4257756_syn_3
# ==========================================
text_3 = """Billing: 31629, 31628, 31623, 31627, 31654, 31624. Extensive sampling of RLL nodule. 21G needle, forceps, brush used. rEBUS concentric."""

entities_3 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodule", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "21G", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "rEBUS", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4257756_syn_4
# ==========================================
text_4 = """Procedure: RLL Biopsy.
Monarch.
1. Nav to RB8.
2. rEBUS Concentric.
3. 21G Needle x 6.
4. Forceps x 7.
5. Brush.
6. BAL.
ROSE: Suspicious."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Monarch", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RB8", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "21G", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x 6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x 7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Suspicious", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4257756_syn_5
# ==========================================
text_5 = """[REDACTED] rll nodule 20mm monarch robot used registration 4.8mm error navigated to rb8 rebus concentric 21g needle 6 times forceps 7 times brush and bal rose suspicious for cancer."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "20mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rb8", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "rebus", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "21g", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "6 times", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "7 times", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "bal", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "suspicious", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "cancer", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4257756_syn_6
# ==========================================
text_6 = """General anesthesia. Monarch robot used. Navigated to RLL RB8. rEBUS concentric. 21G TBNA x 6. Forceps x 7. Brush. BAL. ROSE suspicious. No complications."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "robot", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RB8", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "x 6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "x 7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "suspicious", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "No complications", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4257756_syn_7
# ==========================================
text_7 = """[Indication] 20mm RLL nodule.
[Anesthesia] General.
[Description] Nav to RB8. rEBUS concentric. 21G TBNA x6. Forceps x7. Brush. BAL. ROSE suspicious.
[Plan] Discharge."""

entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "20mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RB8", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_7, "suspicious", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4257756_syn_8
# ==========================================
text_8 = """We navigated the robotic scope to the anterior-basal segment of the right lower lobe. Radial EBUS confirmed a concentric view of the target. We performed six needle passes with a 21-gauge needle, followed by seven forceps biopsies and a cytology brush. A lavage was also performed. The on-site evaluation showed atypical cells suspicious for malignancy."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "anterior-basal segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right lower lobe", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Radial EBUS", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "six", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "21-gauge", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "seven", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "cytology brush", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "atypical cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "suspicious", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "malignancy", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4257756_syn_9
# ==========================================
text_9 = """The robotic device was steered to the RLL. Registration error was 4.8mm. The probe was anchored at RB8. Ultrasound showed a concentric lesion. 21G aspiration (6x), forceps extraction (7x), and brushing were performed. Lavage was done. Pathology was suspicious."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "robotic", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RB8", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Ultrasound", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "21G", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "6x", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "7x", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "brushing", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "suspicious", 1)},
]
BATCH_DATA.append({"id": "4257756_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 4257756
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Lisa Anderson
Fellow: Dr. Alex Chen (PGY-5)

Indication: Lung-RADS 4X nodule
Target: 20mm nodule in RLL

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
VCV\t11\t349\t11\t100\t6\t17

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 4.8mm.

The device was navigated to the RLL. The outer sheath was parked and locked at the ostium of the segmental airway (RB8) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Anterior-Basal Segment of RLL.

Radial EBUS performed via the working channel. rEBUS view: Concentric. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 21G aspiration needle under direct endoscopic and fluoroscopic guidance. 6 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 7 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

Bronchoalveolar lavage performed at RB8. 60mL NS instilled with 28mL return. Sent for Cell count, Culture, and Cytology.

ROSE Result: Atypical cells present, suspicious for malignancy

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Anderson, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "20mm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodule", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "carina", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretions", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "robotic", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "right and left mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "lobar carinas", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB8", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "Anterior-Basal Segment", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 3)},
    {"label": "PROC_METHOD", **get_span(text_10, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rEBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Lesion", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_10, "21G", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "fluoroscopic", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "6 passes", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Cell block", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "7 specimens", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "cytology brushings", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RB8", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "60mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "28mL", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "Atypical cells", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "suspicious", 1)},
    {"label": "OBS_ROSE", **get_span(text_10, "malignancy", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No immediate complications", 1)},
]
BATCH_DATA.append({"id": "4257756", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)