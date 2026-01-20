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
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ==========================================
# Note 1: 3871230_syn_1
# ==========================================
text_1 = """Dx: LLL Large Cell CA. T1cN0M0.
Anesthesia: GA, 8.5 ETT.
Procedure: PDT Light Delivery.
- Fiber: 5.0cm.
- Laser: 630nm, 200 J/cm2, 500s.
- Location: LLL.
Findings: No immediate reaction. No bleeding.
Plan: Debride 48h."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Large Cell CA", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "PDT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fiber", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "5.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_1, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "500s", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No bleeding", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 3871230_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: [REDACTED] photodynamic therapy of a large cell carcinoma in the left lower lobe. Given his ASA 4 status, careful anesthetic management was employed. The lesion, measuring 2.5 cm longitudinally, necessitated a 5.0 cm cylindrical diffuser. We delivered 2000 mW of 630 nm light for 500 seconds, achieving a fluence of 200 J/cm². The procedure was completed without complication, initiating the photochemical necrosis of the endobronchial tumor."""

entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "photodynamic therapy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "large cell carcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "2.5 cm", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "5.0 cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "cylindrical diffuser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_2, "2000 mW", 1)},
    {"label": "MEAS_TIME", **get_span(text_2, "500 seconds", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_2, "200 J/cm²", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "without complication", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 3871230_syn_3
# ==========================================
text_3 = """Service: Bronchoscopy w/ Tumor Destruction (31641).
Method: Photodynamic Therapy (Light application).
Target: Left Lower Lobe (LLL).
Tech Specs: 5.0cm Diffuser, 630nm Laser.
Settings: 400mW/cm, Total 2.0W, 500 sec.
Outcome: Successful illumination of target tissue. No complications."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Destruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Photodynamic Therapy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Left Lower Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LLL", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "5.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Diffuser", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_3, "400mW/cm", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_3, "2.0W", 1)},
    {"label": "MEAS_TIME", **get_span(text_3, "500 sec", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_3, "No complications", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 3871230_syn_4
# ==========================================
text_4 = """Resident Note
Pt: [REDACTED]
Proc: PDT Light
1. Pt intubated (8.5 ETT).
2. Scope to LLL.
3. Tumor visualized (large cell CA).
4. 5cm fiber utilized.
5. Laser active 500s @ 630nm.
6. Stable.
Plan: Light precautions, f/u 48h."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "PDT", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "large cell CA", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "5cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "fiber", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Laser", 1)},
    {"label": "MEAS_TIME", **get_span(text_4, "500s", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 3871230_syn_5
# ==========================================
text_5 = """david williams 74 male for pdt left lower lobe large cell ca high risk patient general anesthesia used 5cm fiber because the tumor was long laser on for 500 seconds total energy delivered appropriate no issues during the case extubated fine transfer to pacu watch for light sensitivity"""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "pdt", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "large cell ca", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "5cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fiber", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "laser", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "500 seconds", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 3871230_syn_6
# ==========================================
text_6 = """The patient was intubated with an 8.5mm ETT. Bronchoscopy revealed a 2.5cm tumor in the LLL. A 5.0cm cylindrical diffuser was selected to cover the lesion length. 630nm laser light was delivered at 200 J/cm2 for 500 seconds. Vital signs remained stable. No immediate tissue reaction was noted, consistent with the PDT mechanism. The patient was extubated and transferred to recovery."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "2.5cm", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "5.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "cylindrical diffuser", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lesion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_6, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(text_6, "500 seconds", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "PDT", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 3871230_syn_7
# ==========================================
text_7 = """[Indication]
LLL Large Cell Carcinoma, inoperable.
[Anesthesia]
General, 8.5 ETT.
[Description]
5.0cm fiber placed in LLL. 630nm laser delivered (2.0W, 500s). Target dose 200 J/cm2 achieved.
[Plan]
Light precautions. Return for debridement May 08."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Large Cell Carcinoma", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "5.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "fiber", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_7, "2.0W", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "500s", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_7, "200 J/cm2", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 3871230_syn_8
# ==========================================
text_8 = """[REDACTED] for his left lower lobe tumor. Under general anesthesia, we id[REDACTED] the 2.5 cm lesion. A 5.0 cm diffuser was required to ensure adequate coverage. We delivered the light therapy over 500 seconds without incident. The patient tolerated the anesthesia well despite his comorbidities. We removed the equipment and confirmed he was stable before transfer to the PACU."""

entities_8 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "2.5 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "5.0 cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "diffuser", 1)},
    {"label": "MEAS_TIME", **get_span(text_8, "500 seconds", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 3871230_syn_9
# ==========================================
text_9 = """OPERATIONS: 1. Photodynamic therapy - laser emission. 2. Bronchoscopy with measurement.
DETAILS: The airway was accessed. The LLL growth was located. A 5.0cm fiber was positioned. 630nm light was beamed onto the target for 500 seconds. No thermal injury was observed. The patient was revived and moved to post-op care."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Photodynamic therapy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "growth", 1)},
    {"label": "MEAS_SIZE", **get_span(text_9, "5.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "fiber", 1)},
    {"label": "MEAS_TIME", **get_span(text_9, "500 seconds", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "No thermal injury", 1)},
]
BATCH_DATA.append({"id": "3871230_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)