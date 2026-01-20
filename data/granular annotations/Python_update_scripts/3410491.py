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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Note: 3410491_syn_1
# ==========================================
id_1 = "3410491_syn_1"
text_1 = """Site: 35mm Lingula.
System: Monarch.
rEBUS: Adjacent.
Tools: 19G needle (7x), Forceps (6x), Brush.
Fluid: BAL LB4.
ROSE: Suspicious NSCC."""
entities_1 = [
    {"label": "MEAS_SIZE", **get_span(text_1, "35mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Monarch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Adjacent", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_1, "19G needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "7x", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "6x", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LB4", 1)},
    {"label": "OBS_ROSE", **get_span(text_1, "Suspicious NSCC", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note: 3410491_syn_2
# ==========================================
id_2 = "3410491_syn_2"
text_2 = """OPERATIVE REPORT: The patient presented for biopsy of a 35mm Lingula mass. Robotic navigation (Monarch) was employed with 3.0mm accuracy. Upon reaching the Superior Lingula (LB4), radial EBUS demonstrated an adjacent view. Extensive sampling was performed including 19G TBNA (7 passes), Transbronchial Forceps Biopsy (6 specimens), and Protected Brushing. A BAL was also collected. Immediate evaluation suggests non-small cell carcinoma."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "35mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Robotic navigation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Monarch", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "3.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Superior Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "adjacent", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_2, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "7 passes", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Transbronchial Forceps Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "6 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Protected Brushing", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_2, "non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note: 3410491_syn_3
# ==========================================
id_3 = "3410491_syn_3"
text_3 = """Codes: 31629 (TBNA), 31628 (Forceps), 31623 (Brush), 31627 (Nav), 31654 (EBUS), 31624 (BAL). Extensive sampling of Lingula mass. 19G needle, standard forceps, and brush used under continuous visualization."""
entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "TBNA", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Nav", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "mass", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "19G needle", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "standard forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "brush", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note: 3410491_syn_4
# ==========================================
id_4 = "3410491_syn_4"
text_4 = """Resident Procedure Note:
Lingula Mass Biopsy.
Monarch Robot used.
Navigated to LB4.
rEBUS: Adjacent.
1. 19G TBNA x 7.
2. Forceps x 6.
3. Brush.
4. BAL.
ROSE: Suspicious."""
entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Monarch Robot", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Adjacent", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x 7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x 6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "BAL", 1)},
    {"label": "OBS_ROSE", **get_span(text_4, "Suspicious", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note: 3410491_syn_5
# ==========================================
id_5 = "3410491_syn_5"
text_5 = """brian hernandez 35mm lingula mass biopsy with monarch robot navigation ok 3mm error saw it on rebus adjacent 19g needle 7 times forceps 6 times brush and bal rose looks like nscc patient did fine."""
entities_5 = [
    {"label": "MEAS_SIZE", **get_span(text_5, "35mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lingula", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "monarch robot navigation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "3mm", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "rebus", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "adjacent", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_5, "19g needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "7 times", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "6 times", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "bal", 1)},
    {"label": "OBS_ROSE", **get_span(text_5, "nscc", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note: 3410491_syn_6
# ==========================================
id_6 = "3410491_syn_6"
text_6 = """General anesthesia induced. Monarch robotic scope inserted. Navigated to Superior Lingula. rEBUS adjacent. 19G TBNA x 7. Forceps biopsy x 6. Brush biopsy. BAL LB4. ROSE suspicious for non-small cell carcinoma. No complications."""
entities_6 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Monarch robotic scope", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Navigated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "Superior Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "adjacent", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_6, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "x 7", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Forceps biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "x 6", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Brush biopsy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LB4", 1)},
    {"label": "OBS_ROSE", **get_span(text_6, "suspicious for non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note: 3410491_syn_7
# ==========================================
id_7 = "3410491_syn_7"
text_7 = """[Indication] 35mm Lingula mass.
[Anesthesia] General.
[Description] Robotic nav to LB4. rEBUS adjacent. 19G TBNA x7. Forceps x6. Brush. BAL.
[Plan] Discharge."""
entities_7 = [
    {"label": "MEAS_SIZE", **get_span(text_7, "35mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "Lingula", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Robotic nav", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "adjacent", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_7, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "TBNA", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x7", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x6", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "BAL", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note: 3410491_syn_8
# ==========================================
id_8 = "3410491_syn_8"
text_8 = """We navigated the robotic system to the superior lingula segment. Radial EBUS confirmed the target was adjacent to the airway. We performed a comprehensive biopsy using a 19-gauge needle for seven passes, followed by six forceps biopsies and a cytology brush. A bronchoalveolar lavage was also completed. The on-site analysis was suspicious for non-small cell carcinoma."""
entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "navigated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "robotic system", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "superior lingula segment", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "Radial EBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "adjacent", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_8, "19-gauge needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "seven passes", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "six", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "forceps biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "cytology brush", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "bronchoalveolar lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_8, "suspicious for non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note: 3410491_syn_9
# ==========================================
id_9 = "3410491_syn_9"
text_9 = """The robotic endoscope was driven to the Lingula. Registration error was 3.0mm. The device was locked at LB4. Ultrasound showed an adjacent lesion. Sampling included 19G aspiration (7x), tissue forceps (6x), and brushing. Lavage was performed. Preliminary findings pointed to carcinoma."""
entities_9 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "robotic endoscope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Lingula", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "3.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LB4", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "adjacent", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "lesion", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_9, "19G", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "aspiration", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "7x", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "tissue forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "6x", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "brushing", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Lavage", 1)},
    {"label": "OBS_ROSE", **get_span(text_9, "carcinoma", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note: 3410491
# ==========================================
id_main = "3410491"
text_main = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Jennifer Lee

Indication: Lung cancer screening detected nodule
Target: 35mm nodule in Lingula

PROCEDURE:

After the successful induction of general anesthesia, a timeout was performed confirming patient id[REDACTED], procedure, and laterality. An 8.0 ETT was secured in good position.

Initial Airway Inspection:
The visualized trachea is of normal caliber with sharp carina. Airways examined to the subsegmental level bilaterally. No endobronchial lesions id[REDACTED]. Mild secretions cleared with suction.

Ventilation Parameters:
Mode	RR	TV	PEEP	FiO2	Flow Rate	Pmean
PRVC	10	302	9	80	6	19

The patient was positioned on the bed within the electromagnetic field. Reference sensors were placed on the anterior chest wall. The Monarch robotic endoscope was introduced through the ETT.

Electromagnetic registration was completed by correlating the live bronchoscopic view with the virtual airway model at multiple anatomic landmarks including the main carina, right and left mainstem bronchi, and lobar carinas. Registration accuracy confirmed with error of 3.0mm.

The device was navigated to the Lingula. The outer sheath was parked and locked at the ostium of the segmental airway (LB4) to provide stability. The inner scope was then telescoped distally into the sub-segmental airways to reach the target lesion in the Superior Lingula.

Radial EBUS performed via the working channel. rEBUS view: Adjacent. Lesion confirmed at target location.

Crucially, continuous visualization was maintained throughout sampling. The needle was advanced through the working channel, and needle exit from the scope tip was visually confirmed before entering the bronchial wall.

Transbronchial needle aspiration performed with 19G aspiration needle under direct endoscopic and fluoroscopic guidance. 7 passes performed. Samples sent for Cytology and Cell block.

Transbronchial forceps biopsy performed with standard forceps through the working channel. 6 specimens obtained. Continuous visualization maintained during each pass. Samples sent for Surgical Pathology.

Protected cytology brushings obtained under direct visualization. Samples sent for Cytology.

Bronchoalveolar lavage performed at LB4. 40mL NS instilled with 21mL return. Sent for Cell count, Culture, and Cytology.

ROSE Result: Suspicious for non-small cell carcinoma

The inner scope was retracted into the outer sheath. Final airway inspection performed - no significant bleeding or airway trauma. The robotic system was removed.

The patient tolerated the procedure well. No immediate complications.

DISPOSITION: Recovery area, post-procedure CXR, discharge if stable.
Follow-up: Results in 5-7 days.

Lee, MD"""
entities_main = [
    {"label": "MEAS_SIZE", **get_span(text_main, "35mm", 1)},
    {"label": "OBS_LESION", **get_span(text_main, "nodule", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "Lingula", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_main, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_main, "carina", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_main, "chest wall", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_main, "Monarch robotic endoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_main, "main carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_main, "mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_main, "lobar carinas", 1)},
    {"label": "MEAS_SIZE", **get_span(text_main, "3.0mm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "Lingula", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "LB4", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "Superior Lingula", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "Radial EBUS", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "rEBUS", 1)},
    {"label": "OBS_FINDING", **get_span(text_main, "Adjacent", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "Transbronchial needle aspiration", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_main, "19G aspiration needle", 1)},
    {"label": "MEAS_COUNT", **get_span(text_main, "7 passes", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "Transbronchial forceps biopsy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_main, "standard forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_main, "6 specimens", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "Protected cytology brushings", 1)},
    {"label": "PROC_METHOD", **get_span(text_main, "Bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_main, "LB4", 2)},
    {"label": "MEAS_VOL", **get_span(text_main, "40mL", 1)},
    {"label": "MEAS_VOL", **get_span(text_main, "21mL", 1)},
    {"label": "OBS_ROSE", **get_span(text_main, "Suspicious for non-small cell carcinoma", 1)},
]
BATCH_DATA.append({"id": id_main, "text": text_main, "entities": entities_main})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        print(f"Adding case: {case['id']}")
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Done.")