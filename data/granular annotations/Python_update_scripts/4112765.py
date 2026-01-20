import sys
from pathlib import Path

# Set up the repository root path
# (Assuming this script is run from inside the repository or a subdirectory)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports from 'scripts'
sys.path.append(str(REPO_ROOT))

# Import the utility function
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
    
    return start, start + len(term)

# ==========================================
# Note 1: 4112765_syn_1
# ==========================================
t1 = """Pre-op: 33mm RML nodule.
Anesthesia: GA.
Procedure: Monarch nav to RB5. rEBUS Concentric. TBNA (21G), Forceps x7, Brush. Fiducial placed.
ROSE: Negative for malignancy.
Disposition: Recovery."""
e1 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t1, "33mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t1, "RML", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t1, "nodule", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t1, "Monarch", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t1, "RB5", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t1, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t1, "TBNA", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t1, "21G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t1, "Forceps", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t1, "x7", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t1, "Brush", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t1, "Negative for malignancy", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 4112765_syn_2
# ==========================================
t2 = """OPERATIVE NARRATIVE: [REDACTED] a PET-avid 33mm nodule in the Medial Segment of the RML. Under general anesthesia, we utilized the Monarch robotic endoscope. Navigation was registered (4.0mm error). We confirmed the lesion location with concentric radial EBUS. Transbronchial needle aspiration (21G), forceps biopsies, and brushings were obtained. A fiducial marker was placed for radiation planning. ROSE was negative for malignant neoplasm."""
e2 = [
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t2, "33mm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t2, "nodule", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t2, "Medial Segment of the RML", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t2, "Monarch", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t2, "robotic", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t2, "radial EBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "Transbronchial needle aspiration", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t2, "21G", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t2, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t2, "biopsies", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t2, "negative for malignant neoplasm", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 4112765_syn_3
# ==========================================
t3 = """Codes:
- 31629 (TBNA)
- 31628 (Forceps)
- 31623 (Brush)
- 31626 (Fiducial)
- +31627 (Nav) / +31654 (EBUS)
Site: RML Medial Segment.
Technique: Robotic nav, rEBUS confirmation, Multimodal sampling."""
e3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t3, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t3, "Forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t3, "Brush", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t3, "Nav", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t3, "EBUS", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t3, "RML Medial Segment", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t3, "Robotic", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t3, "rEBUS", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 4112765_syn_4
# ==========================================
t4 = """Resident Note
Pt: [REDACTED], E.
Loc: RML.
Steps:
1. GA induced.
2. Monarch nav to RB5.
3. rEBUS concentric.
4. 21G TBNA x8.
5. Forceps x7.
6. Brush.
7. Fiducial placed.
ROSE: Negative.
Plan: Follow up 5-7 days."""
e4 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t4, "RML", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t4, "Monarch", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t4, "RB5", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t4, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t4, "21G", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t4, "TBNA", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t4, "x8", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t4, "Forceps", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t4, "x7", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t4, "Brush", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t4, "Negative", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 4112765_syn_5
# ==========================================
t5 = """Emily White RML nodule 33mm. We used the monarch robot today. Navigated to the medial segment RB5. Concentric view on rEBUS. Did the needle biopsy 21g then forceps then brush. Dropped a fiducial marker in there too. Cytology says no cancer seen so far. No bleeding patient fine."""
e5 = [
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t5, "RML", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t5, "nodule", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t5, "33mm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t5, "monarch", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t5, "robot", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t5, "medial segment", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t5, "RB5", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t5, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t5, "needle", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t5, "biopsy", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t5, "21g", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t5, "forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t5, "brush", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t5, "no cancer seen", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 4112765_syn_6
# ==========================================
t6 = """Robotic bronchoscopy was undertaken for a 33mm RML nodule. Navigation to the medial segment (RB5) was performed with the Monarch system. rEBUS showed a concentric view. The lesion was sampled via 21G TBNA, forceps biopsy, and brushings. A fiducial marker was placed. ROSE results showed no evidence of malignancy. No complications were noted."""
e6 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t6, "Robotic", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t6, "33mm", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t6, "RML", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t6, "nodule", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t6, "medial segment", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t6, "RB5", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t6, "Monarch", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t6, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t6, "21G", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t6, "forceps", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t6, "biopsy", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t6, "no evidence of malignancy", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t6, "No complications", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 4112765_syn_7
# ==========================================
t7 = """[Indication]
PET-avid nodule, RML (33mm).
[Anesthesia]
General, 8.0 ETT.
[Description]
Monarch nav to RB5. rEBUS: Concentric. Sampling: 21G TBNA, Forceps, Brush. Fiducial placed. ROSE: No malignancy.
[Plan]
CXR, Discharge."""
e7 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t7, "nodule", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t7, "RML", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t7, "33mm", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t7, "Monarch", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t7, "RB5", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t7, "rEBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t7, "21G", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t7, "TBNA", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t7, "Forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t7, "Brush", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t7, "No malignancy", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 4112765_syn_8
# ==========================================
t8 = """[REDACTED] for a biopsy of her right middle lobe nodule. We used the robotic scope to get to the medial segment. The EBUS confirmed we were right in the center of the lesion. We took plenty of samples using a needle, forceps, and a brush. We also placed a marker for radiation therapy just in case. The preliminary results didn't show any cancer, which is good news, but we'll wait for the final report."""
e8 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t8, "biopsy", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t8, "right middle lobe", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t8, "nodule", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t8, "robotic", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t8, "medial segment", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t8, "EBUS", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t8, "needle", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t8, "forceps", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t8, "brush", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t8, "didn't show any cancer", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 4112765_syn_9
# ==========================================
t9 = """Procedure: Robotic-assisted bronchoscopic biopsy and marker placement.
Site: RML Medial Segment.
Action: The robotic device was steered to RB5. rEBUS confirmed the lesion. Samples were collected via aspiration, forceps excision, and brushing. A fiducial was implanted.
Result: ROSE was negative for malignancy."""
e9 = [
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t9, "Robotic", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "biopsy", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t9, "RML Medial Segment", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t9, "robotic", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t9, "RB5", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t9, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t9, "aspiration", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t9, "forceps", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t9, "negative for malignancy", 1)))},
]
BATCH_DATA.append({"id": "4112765_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 4112765
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Christopher Brown
Fellow: Dr. Maria Santos (PGY-6)

Indication: PET-avid lung nodule
Target: 33mm nodule in RML

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode\tRR\tTV\tPEEP\tFiO2\tFlow Rate\tPmean
VCV\t13\t398\t18\t100\t6\t24

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 4.0mm.

The device was navigated to the RML. The outer sheath was parked and locked at the ostium of the segmental airway (RB5) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Medial Segment of RML.

Radial EBUS performed via the working channel. rEBUS view: Concentric. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 21G aspiration needle under direct endoscopic and fluoroscopic guidance. 8 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 7 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

Gold fiducial marker placed under fluoroscopic guidance for radiation therapy planning.

ROSE Result: No evidence of malignant neoplasm

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Brown, MD"""
e10 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "lung nodule", 1)))},
    {"label": "MEAS_SIZE", **dict(zip(["start", "end"], get_span(t10, "33mm", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(t10, "nodule", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RML", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "trachea", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(t10, "carina", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t10, "Monarch", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t10, "robotic", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RML", 2)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "RB5", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(t10, "Medial Segment of RML", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t10, "Radial EBUS", 1)))},
    {"label": "PROC_METHOD", **dict(zip(["start", "end"], get_span(t10, "rEBUS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "Transbronchial needle aspiration", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t10, "21G", 1)))},
    {"label": "DEV_NEEDLE", **dict(zip(["start", "end"], get_span(t10, "aspiration needle", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t10, "8 passes", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(t10, "Transbronchial forceps biopsy", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "forceps", 1)))},
    {"label": "MEAS_COUNT", **dict(zip(["start", "end"], get_span(t10, "7 specimens", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(t10, "cytology brushings", 1)))},
    {"label": "OBS_ROSE", **dict(zip(["start", "end"], get_span(t10, "No evidence of malignant neoplasm", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(t10, "No immediate complications", 1)))},
]
BATCH_DATA.append({"id": "4112765", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)