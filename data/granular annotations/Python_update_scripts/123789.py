import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is run from within the repository structure
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

# Helper function to find text spans
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
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

BATCH_DATA = []

# ==========================================
# Note 1: 123789_syn_1
# ==========================================
t1 = """Indication: Thymoma.
Procedure: VATS thymectomy/mass excision.
- 3 ports.
- Mass dissected from pericardium/innominate.
- Margins clear.
- Removed via endobag.
- 24Fr chest tube."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "Thymoma", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "thymectomy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "excision", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "3", 1)},
    {"label": "OBS_LESION", **get_span(t1, "Mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "endobag", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t1, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "chest tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 123789_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: Video-assisted thoracoscopic excision of anterior mediastinal mass.
FINDINGS: A 4.5 cm well-circumscribed thymic mass was id[REDACTED] in the anterior mediastinum. There was no evidence of invasion into the pericardium or great vessels.
PROCEDURE: Using a three-port VATS approach, the mediastinal pleura was incised. The mass was dissected free from the pericardial and thymic bed using ultrasonic energy. Complete resection was achieved, and the specimen was extracted via an endo-catch bag."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Video-assisted thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 1)},
    {"label": "MEAS_SIZE", **get_span(t2, "4.5 cm", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 2)},
    {"label": "MEAS_COUNT", **get_span(t2, "three", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "VATS", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "mediastinal pleura", 1)},
    {"label": "OBS_LESION", **get_span(t2, "mass", 3)},
    {"label": "PROC_ACTION", **get_span(t2, "resection", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "endo-catch bag", 1)},
]
BATCH_DATA.append({"id": "123789_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 123789_syn_3
# ==========================================
t3 = """CPT 32662: VATS excision of mediastinal cyst, tumor, or mass.
Approach: 3-port VATS.
Pathology: Thymoma (4.5cm).
Work: Complete dissection from pericardium and innominate vein; extraction via bag; chest tube placement."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t3, "cyst", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(t3, "mass", 1)},
    {"label": "MEAS_COUNT", **get_span(t3, "3", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "VATS", 2)},
    {"label": "OBS_LESION", **get_span(t3, "Thymoma", 1)},
    {"label": "MEAS_SIZE", **get_span(t3, "4.5cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "bag", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "chest tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 123789_syn_4
# ==========================================
t4 = """Procedure: VATS Resection Mediastinal Mass
1. GA / DLT / Lateral decubitus.
2. Ports: 5th, 3rd, 7th ICS.
3. Id[REDACTED] mass anterior mediastinum.
4. Dissected with harmonic.
5. Bagged and removed.
6. Chest tube placed."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Resection", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Mass", 1)},
    {"label": "OBS_LESION", **get_span(t4, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "harmonic", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 123789_syn_5
# ==========================================
t5 = """Vats for thymoma right side wait left side 3 ports mass was anterior dissected it off the vessels and heart looked contained put it in a bag and pulled it out chest tube in blood loss minimal patient fine."""

e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "Vats", 1)},
    {"label": "OBS_LESION", **get_span(t5, "thymoma", 1)},
    {"label": "LATERALITY", **get_span(t5, "right", 1)},
    {"label": "LATERALITY", **get_span(t5, "left", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "3", 1)},
    {"label": "OBS_LESION", **get_span(t5, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "bag", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 123789_syn_6
# ==========================================
t6 = """Video-assisted thoracoscopic surgery (VATS) with excision of mediastinal lesion. 65-year-old male with 4.2cm anterior mediastinal mass. Three port placements. Thoracoscope introduced. Anterior mediastinum visualized with well-encapsulated mass arising from thymic tissue. Careful dissection performed using harmonic scalpel separating mass from pericardium and left innominate vein. Specimen removed via endo-bag. Single 24Fr chest tube placed."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Video-assisted thoracoscopic surgery", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t6, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(t6, "4.2cm", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 1)},
    {"label": "MEAS_COUNT", **get_span(t6, "Three", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Thoracoscope", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "harmonic scalpel", 1)},
    {"label": "OBS_LESION", **get_span(t6, "mass", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "endo-bag", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t6, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "chest tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 123789_syn_7
# ==========================================
t7 = """[Indication]
Anterior mediastinal mass (Thymoma).
[Anesthesia]
General, DLT.
[Description]
3-port VATS. 4.5cm mass dissected from anterior mediastinum. Complete excision. Endo-bag extraction.
[Plan]
Admit, chest tube management."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Thymoma", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "3", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "VATS", 1)},
    {"label": "MEAS_SIZE", **get_span(t7, "4.5cm", 1)},
    {"label": "OBS_LESION", **get_span(t7, "mass", 2)},
    {"label": "PROC_ACTION", **get_span(t7, "excision", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "Endo-bag", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "chest tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 123789_syn_8
# ==========================================
t8 = """[REDACTED] a VATS procedure to remove a suspicious mass in his chest. We used three small incisions to access the space. The mass, located in the anterior mediastinum, was carefully separated from the heart and major veins. We were able to remove it completely in a retrieval bag. A chest tube was left in place to drain any fluid or air."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "VATS", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 1)},
    {"label": "MEAS_COUNT", **get_span(t8, "three", 1)},
    {"label": "OBS_LESION", **get_span(t8, "mass", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "retrieval bag", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 123789_syn_9
# ==========================================
t9 = """Diagnosis: Anterior mediastinal neoplasm.
Action: Thoracoscopic resection of mediastinal tumor.
Details: Three-port access established. Tumor separated from surrounding structures. Complete removal achieved via retrieval sac. Drainage tube inserted."""

e9 = [
    {"label": "OBS_LESION", **get_span(t9, "neoplasm", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "resection", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "MEAS_COUNT", **get_span(t9, "Three", 1)},
    {"label": "OBS_LESION", **get_span(t9, "Tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t9, "retrieval sac", 1)},
    {"label": "DEV_CATHETER", **get_span(t9, "Drainage tube", 1)},
]
BATCH_DATA.append({"id": "123789_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 123789
# ==========================================
t10 = """OPERATIVE REPORT

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (65 years old)
Date of Service: [REDACTED]
Location: [REDACTED]

Surgeons:
Attending: Dr. Elizabeth Warren, MD - Thoracic Surgery
Assistant: Dr. Michael Chen, MD - Thoracic Surgery Fellow

Anesthesia: General endotracheal anesthesia
Anesthesiologist: Dr. Peter Williams, MD

Preoperative Diagnosis: Mediastinal mass, suspected thymoma

Postoperative Diagnosis: Anterior mediastinal mass - thymoma confirmed

Procedure: Video-assisted thoracoscopic surgery (VATS) with excision of mediastinal lesion

Indications: 65-year-old male with incidentally discovered 4.2cm anterior mediastinal mass on CT chest. PET showed mild FDG uptake (SUV 3.2). MRI confirmed well-circumscribed anterior mediastinal lesion. Patient elected for surgical excision.

Procedure Details:
Patient [REDACTED] supine position with left side elevated 30 degrees. Double-lumen ETT placed. General anesthesia induced. Left chest prepped and draped in sterile fashion.

Three port placements:
- 10mm camera port, 5th intercostal space, anterior axillary line
- 5mm working port, 3rd intercostal space, mid-clavicular line
- 5mm working port, 7th intercostal space, anterior axillary line

Thoracoscope introduced. Pleural space inspected - no effusion, no adhesions. Anterior mediastinum visualized with well-encapsulated mass arising from thymic tissue. Careful dissection performed using harmonic scalpel, separating mass from pericardium and left innominate vein. All margins appeared grossly clear. Specimen removed via endo-bag through enlarged camera port.

Hemostasis confirmed. Single 24Fr chest tube placed. Lung re-expanded under direct visualization. Ports closed in layers.

Specimen: 4.5 x 3.8 x 3.2 cm encapsulated mass, sent for permanent pathology.

EBL: 75mL
Complications: None
Disposition: To PACU in stable condition

E. Warren, MD"""

e10 = [
    {"label": "OBS_LESION", **get_span(t10, "mass", 1)},
    {"label": "OBS_LESION", **get_span(t10, "thymoma", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 2)},
    {"label": "OBS_LESION", **get_span(t10, "thymoma", 2)},
    {"label": "PROC_METHOD", **get_span(t10, "Video-assisted thoracoscopic surgery", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "4.2cm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 3)},
    {"label": "OBS_LESION", **get_span(t10, "lesion", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "excision", 2)},
    {"label": "LATERALITY", **get_span(t10, "left", 1)},
    {"label": "LATERALITY", **get_span(t10, "Left", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "Three", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "10mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "5mm", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "5mm", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "Thoracoscope", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "Pleural space", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 4)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "harmonic scalpel", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 5)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "endo-bag", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t10, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "MEAS_SIZE", **get_span(t10, "4.5 x 3.8 x 3.2 cm", 1)},
    {"label": "OBS_LESION", **get_span(t10, "mass", 6)},
    {"label": "MEAS_VOL", **get_span(t10, "75mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "None", 1)},
]
BATCH_DATA.append({"id": "123789", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)