import sys
from pathlib import Path

# 1. Dynamic Repo Root (adjusts to environment)
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# 2. Import Utility
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start/end indices of the Nth occurrence of a substring.
    Strict case-sensitivity is enforced to ensure exact data mapping.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 789456_syn_1
# ==========================================
text_1 = """Indication: Middle mediastinal cyst.
Proc: VATS excision.
- 3 ports.
- Cyst 6cm, adherent to esophagus/bronchus.
- Aspirated -> Dissected.
- Complete wall removal.
- Chest tube."""

entities_1 = [
    {"label": "OBS_LESION",     **get_span(text_1, "cyst", 1)},
    {"label": "PROC_METHOD",    **get_span(text_1, "VATS", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "excision", 1)},
    {"label": "OBS_LESION",     **get_span(text_1, "Cyst", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_1, "6cm", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_1, "bronchus", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "Aspirated", 1)},
    {"label": "PROC_ACTION",    **get_span(text_1, "Dissected", 1)},
    {"label": "DEV_CATHETER",   **get_span(text_1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "789456_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Case 2: 789456_syn_2
# ==========================================
text_2 = """OPERATIVE SUMMARY: Thoracoscopic resection of bronchogenic cyst.
FINDINGS: A 6 cm cystic lesion was id[REDACTED] in the middle mediastinum, intimately associated with the esophagus and right mainstem bronchus.
PROCEDURE: Following aspiration of mucinous fluid to facilitate handling, the cyst wall was meticulously dissected from the airway and esophagus using blunt and sharp dissection. Complete excision of the cyst wall was achieved without injury to surrounding structures."""

entities_2 = [
    {"label": "PROC_METHOD",    **get_span(text_2, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "resection", 1)},
    {"label": "OBS_LESION",     **get_span(text_2, "bronchogenic cyst", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_2, "6 cm", 1)},
    {"label": "OBS_LESION",     **get_span(text_2, "cystic lesion", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_2, "right mainstem bronchus", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "aspiration", 1)},
    {"label": "SPECIMEN",       **get_span(text_2, "mucinous fluid", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "dissected", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_2, "airway", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "dissection", 1)},
    {"label": "PROC_ACTION",    **get_span(text_2, "excision", 1)},
]
BATCH_DATA.append({"id": "789456_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Case 3: 789456_syn_3
# ==========================================
text_3 = """CPT 32662: VATS excision of mediastinal cyst.
Type: Bronchogenic cyst.
Complexity: Adherent to esophagus and airway.
Steps: Aspiration, dissection of wall, removal, chest tube."""

entities_3 = [
    {"label": "PROC_METHOD",    **get_span(text_3, "VATS", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3, "excision", 1)},
    {"label": "OBS_LESION",     **get_span(text_3, "mediastinal cyst", 1)},
    {"label": "OBS_LESION",     **get_span(text_3, "Bronchogenic cyst", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_3, "airway", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3, "Aspiration", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3, "dissection", 1)},
    {"label": "PROC_ACTION",    **get_span(text_3, "removal", 1)},
    {"label": "DEV_CATHETER",   **get_span(text_3, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789456_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Case 4: 789456_syn_4
# ==========================================
text_4 = """Procedure: VATS Cyst Excision
1. 3 ports.
2. Found cyst middle mediastinum.
3. Aspirated fluid.
4. Dissected wall off esophagus/bronchus.
5. Removed specimen.
6. Chest tube."""

entities_4 = [
    {"label": "PROC_METHOD",    **get_span(text_4, "VATS", 1)},
    {"label": "OBS_LESION",     **get_span(text_4, "Cyst", 1)},
    {"label": "PROC_ACTION",    **get_span(text_4, "Excision", 1)},
    {"label": "OBS_LESION",     **get_span(text_4, "cyst", 1)},
    {"label": "PROC_ACTION",    **get_span(text_4, "Aspirated", 1)},
    {"label": "SPECIMEN",       **get_span(text_4, "fluid", 1)},
    {"label": "PROC_ACTION",    **get_span(text_4, "Dissected", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_4, "bronchus", 1)},
    {"label": "PROC_ACTION",    **get_span(text_4, "Removed", 1)},
    {"label": "DEV_CATHETER",   **get_span(text_4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "789456_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Case 5: 789456_syn_5
# ==========================================
text_5 = """George Nakamura 73M with the big cyst in the middle of the chest vats 3 ports stuck to the esophagus and airway carefully peeled it off after draining it got the whole wall out chest tube placed no leaks."""

entities_5 = [
    {"label": "OBS_LESION",     **get_span(text_5, "cyst", 1)},
    {"label": "PROC_METHOD",    **get_span(text_5, "vats", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_5, "airway", 1)},
    {"label": "PROC_ACTION",    **get_span(text_5, "draining", 1)},
    {"label": "DEV_CATHETER",   **get_span(text_5, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789456_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Case 6: 789456_syn_6
# ==========================================
text_6 = """VATS Excision of Mediastinal Cyst. 6cm middle mediastinal cyst causing dysphagia. Large cystic lesion id[REDACTED] in middle mediastinum closely abutting the esophagus and right mainstem bronchus. Cyst aspirated clear mucinous fluid. Cyst wall dissected carefully from esophagus and airway using combination of sharp and blunt dissection. Complete excision achieved."""

entities_6 = [
    {"label": "PROC_METHOD",    **get_span(text_6, "VATS", 1)},
    {"label": "PROC_ACTION",    **get_span(text_6, "Excision", 1)},
    {"label": "OBS_LESION",     **get_span(text_6, "Mediastinal Cyst", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_6, "6cm", 1)},
    {"label": "OBS_LESION",     **get_span(text_6, "cyst", 1)},
    {"label": "OBS_LESION",     **get_span(text_6, "cystic lesion", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_6, "right mainstem bronchus", 1)},
    {"label": "OBS_LESION",     **get_span(text_6, "Cyst", 1)},
    {"label": "PROC_ACTION",    **get_span(text_6, "aspirated", 1)},
    {"label": "SPECIMEN",       **get_span(text_6, "mucinous fluid", 1)},
    {"label": "OBS_LESION",     **get_span(text_6, "Cyst", 2)},
    {"label": "PROC_ACTION",    **get_span(text_6, "dissected", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_6, "airway", 1)},
    {"label": "PROC_ACTION",    **get_span(text_6, "dissection", 1)},
    {"label": "PROC_ACTION",    **get_span(text_6, "excision", 1)},
]
BATCH_DATA.append({"id": "789456_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Case 7: 789456_syn_7
# ==========================================
text_7 = """[Indication]
Symptomatic mediastinal cyst (Bronchogenic).
[Anesthesia]
General, DLT.
[Description]
3-port VATS. Cyst aspirated. Wall dissected from esophagus/bronchus. Complete excision.
[Plan]
Admit."""

entities_7 = [
    {"label": "OBS_LESION",     **get_span(text_7, "mediastinal cyst", 1)},
    {"label": "OBS_LESION",     **get_span(text_7, "Bronchogenic", 1)},
    {"label": "PROC_METHOD",    **get_span(text_7, "VATS", 1)},
    {"label": "OBS_LESION",     **get_span(text_7, "Cyst", 1)},
    {"label": "PROC_ACTION",    **get_span(text_7, "aspirated", 1)},
    {"label": "PROC_ACTION",    **get_span(text_7, "dissected", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_7, "bronchus", 1)},
    {"label": "PROC_ACTION",    **get_span(text_7, "excision", 1)},
]
BATCH_DATA.append({"id": "789456_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Case 8: 789456_syn_8
# ==========================================
text_8 = """[REDACTED] a large cyst pressing on his esophagus. We performed a VATS procedure to remove it. Once we were inside, we drained the fluid from the cyst to make it smaller, then carefully peeled the cyst wall off of the esophagus and the main airway. We got the whole thing out without damaging any organs."""

entities_8 = [
    {"label": "OBS_LESION",     **get_span(text_8, "cyst", 1)},
    {"label": "PROC_METHOD",    **get_span(text_8, "VATS", 1)},
    {"label": "PROC_ACTION",    **get_span(text_8, "drained", 1)},
    {"label": "SPECIMEN",       **get_span(text_8, "fluid", 1)},
    {"label": "OBS_LESION",     **get_span(text_8, "cyst", 2)},
    {"label": "OBS_LESION",     **get_span(text_8, "cyst", 3)},
    {"label": "ANAT_AIRWAY",    **get_span(text_8, "main airway", 1)},
]
BATCH_DATA.append({"id": "789456_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Case 9: 789456_syn_9
# ==========================================
text_9 = """Diagnosis: Middle mediastinal fluid-filled lesion.
Action: Thoracoscopic resection of mediastinal cyst.
Details: Lesion drained. Capsule separated from adjacent airway and esophagus. Complete removal. Drainage tube inserted."""

entities_9 = [
    {"label": "OBS_LESION",     **get_span(text_9, "lesion", 1)},
    {"label": "PROC_METHOD",    **get_span(text_9, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION",    **get_span(text_9, "resection", 1)},
    {"label": "OBS_LESION",     **get_span(text_9, "mediastinal cyst", 1)},
    {"label": "OBS_LESION",     **get_span(text_9, "Lesion", 1)},
    {"label": "PROC_ACTION",    **get_span(text_9, "drained", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_9, "airway", 1)},
    {"label": "PROC_ACTION",    **get_span(text_9, "removal", 1)},
    {"label": "DEV_CATHETER",   **get_span(text_9, "Drainage tube", 1)},
]
BATCH_DATA.append({"id": "789456_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# Case 10: 789456
# ==========================================
text_10 = """Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (73 years old)
Date: [REDACTED]
Facility: [REDACTED]

Procedure: VATS Excision of Mediastinal Cyst

Surgeon: Dr. Patricia Hayes, MD - Thoracic Surgery
Anesthesia: General (DLT)

Indication: 73M with symptomatic 6cm middle mediastinal cyst causing dysphagia and chest discomfort. MRI suggests bronchogenic cyst.

Technique:
Right lateral decubitus. Standard three-port VATS approach. 30-degree thoracoscope inserted. Large cystic lesion id[REDACTED] in middle mediastinum, closely abutting the esophagus and right mainstem bronchus. Cyst aspirated - clear mucinous fluid. Cyst wall dissected carefully from esophagus and airway using combination of sharp and blunt dissection. Complete excision achieved without violation of esophagus or airway.

Final specimen: 5.8 x 5.2 cm cyst with thickened wall.

Chest tube placed. Full lung expansion confirmed. Patient extubated and transferred to recovery.

EBL: 40mL
No complications.

P. Hayes MD"""

entities_10 = [
    {"label": "PROC_METHOD",    **get_span(text_10, "VATS", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "Excision", 1)},
    {"label": "OBS_LESION",     **get_span(text_10, "Mediastinal Cyst", 1)},
    {"label": "MEAS_SIZE",      **get_span(text_10, "6cm", 1)},
    {"label": "OBS_LESION",     **get_span(text_10, "cyst", 1)},
    {"label": "OBS_LESION",     **get_span(text_10, "bronchogenic cyst", 1)},
    {"label": "PROC_METHOD",    **get_span(text_10, "VATS", 2)},
    {"label": "OBS_LESION",     **get_span(text_10, "cystic lesion", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_10, "right mainstem bronchus", 1)},
    {"label": "OBS_LESION",     **get_span(text_10, "Cyst", 2)},
    {"label": "PROC_ACTION",    **get_span(text_10, "aspirated", 1)},
    {"label": "SPECIMEN",       **get_span(text_10, "mucinous fluid", 1)},
    {"label": "OBS_LESION",     **get_span(text_10, "Cyst", 3)},
    {"label": "PROC_ACTION",    **get_span(text_10, "dissected", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_10, "airway", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "dissection", 1)},
    {"label": "PROC_ACTION",    **get_span(text_10, "excision", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(text_10, "airway", 2)},
    {"label": "MEAS_SIZE",      **get_span(text_10, "5.8 x 5.2 cm", 1)},
    {"label": "OBS_LESION",     **get_span(text_10, "cyst", 2)},
    {"label": "DEV_CATHETER",   **get_span(text_10, "Chest tube", 1)},
    {"label": "MEAS_VOL",       **get_span(text_10, "40mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
]
BATCH_DATA.append({"id": "789456", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)