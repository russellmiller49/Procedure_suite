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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 567234_syn_1
# ==========================================
id_1 = "567234_syn_1"
text_1 = """Indication: Superior mediastinal lipoma (SVC syndrome).
Proc: VATS excision.
- 3 ports.
- 7cm fatty mass.
- Dissected from SVC.
- SVC decompressed.
- Chest tube."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "lipoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "SVC syndrome", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "excision", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "7cm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "fatty mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Dissected", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_1, "SVC decompressed", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 567234_syn_2
# ==========================================
id_2 = "567234_syn_2"
text_2 = """OPERATIVE REPORT: Video-assisted thoracoscopic resection of mediastinal lipoma.
INDICATION: Symptomatic compression of the superior vena cava.
FINDINGS: A 7 cm encapsulated adipose tumor in the superior mediastinum causing extrinsic compression of the SVC.
PROCEDURE: Meticulous dissection was performed to separate the tumor from the great vessels. The mass was excised in toto, resulting in immediate visual decompression of the superior vena cava."""
entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Video-assisted thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "resection", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lipoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "compression", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "7 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "encapsulated adipose tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "extrinsic compression", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dissection", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(text_2, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "excised", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_2, "decompression of the superior vena cava", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 567234_syn_3
# ==========================================
id_3 = "567234_syn_3"
text_3 = """CPT 32662: VATS excision of mediastinal tumor.
Pathology: Lipoma.
Size: 7cm.
Complication treated: SVC compression.
Work: Dissection from great vessels, removal via bag, chest tube."""
entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "excision", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "mediastinal tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Lipoma", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "7cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "SVC compression", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Dissection", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "removal", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "bag", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 567234_syn_4
# ==========================================
id_4 = "567234_syn_4"
text_4 = """Procedure: VATS Lipoma Excision
1. 3 ports.
2. Found fatty mass compressing SVC.
3. Dissected off vessels.
4. Removed in bag.
5. SVC looks better.
6. Chest tube."""
entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "VATS", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Lipoma", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Excision", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "fatty mass", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "compressing", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Dissected", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Removed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "bag", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_4, "SVC looks better", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 567234_syn_5
# ==========================================
id_5 = "567234_syn_5"
text_5 = """Henry Okonkwo with the lipoma pushing on his svc vats right side found the big fatty tumor 7cm peeled it off the vein vein opened up nicely mass out in a bag chest tube placed."""
entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "lipoma", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "vats", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "fatty tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "7cm", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_5, "vein opened up nicely", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "mass", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "bag", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 567234_syn_6
# ==========================================
id_6 = "567234_syn_6"
text_6 = """VATS excision of mediastinal tumor. Superior mediastinal lipoma causing SVC compression symptoms. Large fatty tumor id[REDACTED] in superior mediastinum compressing but not invading SVC. Meticulous dissection performed around great vessels. Tumor completely excised in one piece using endoscopic retrieval bag. SVC decompressed with visible improvement in venous caliber."""
entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "excision", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "mediastinal tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lipoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "SVC compression", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "fatty tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "compressing", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dissection", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "excised", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "endoscopic retrieval bag", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_6, "SVC decompressed", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_6, "visible improvement in venous caliber", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 567234_syn_7
# ==========================================
id_7 = "567234_syn_7"
text_7 = """[Indication]
Mediastinal lipoma with SVC compression.
[Anesthesia]
General.
[Description]
3-port VATS. 7cm mass dissected from SVC. Complete excision. SVC decompressed.
[Plan]
Admit."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "lipoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "SVC compression", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "VATS", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "7cm", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mass", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dissected", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "excision", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_7, "SVC decompressed", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 567234_syn_8
# ==========================================
id_8 = "567234_syn_8"
text_8 = """[REDACTED] a benign fatty tumor pressing on his superior vena cava, causing swelling. We used VATS to remove it. The tumor was large, about 7cm, and sitting right on the vein. We carefully dissected it away. Once it was removed, we could see the vein expand back to its normal size. We placed a chest tube and closed."""
entities_8 = [
    {"label": "OBS_LESION", **get_span(text_8, "fatty tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "swelling", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "remove", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "7cm", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dissected", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "removed", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "vein expand back to its normal size", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 567234_syn_9
# ==========================================
id_9 = "567234_syn_9"
text_9 = """Diagnosis: Superior mediastinal adipose tumor.
Action: Thoracoscopic removal of mediastinal mass.
Details: Lesion compressing the superior vena cava was isolated and resected. Vascular decompression confirmed. Drainage tube inserted."""
entities_9 = [
    {"label": "OBS_LESION", **get_span(text_9, "adipose tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Thoracoscopic", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "removal", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "mediastinal mass", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "compressing", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "resected", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_9, "Vascular decompression", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Drainage tube", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 567234
# ==========================================
id_10 = "567234"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Catherine Bell

Dx: Superior mediastinal lipoma causing SVC compression symptoms
Procedure: VATS excision of mediastinal tumor

Hx: 60M with 3-month history of facial swelling and arm edema. CT showed 7cm superior mediastinal mass with fat density. Lipoma confirmed on MRI. Due to symptomatic SVC compression, surgical excision recommended.

Procedure:
General anesthesia, right lateral decubitus. Three-port right VATS. Large fatty tumor id[REDACTED] in superior mediastinum, compressing but not invading SVC. Meticulous dissection performed around great vessels. Tumor completely excised in one piece using endoscopic retrieval bag. SVC decompressed with visible improvement in venous caliber.

Specimen: 7.2 x 6.5 x 4.8 cm encapsulated fatty mass.
EBL: 60mL
Chest tube placed. No complications.

C. Bell MD"""
entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "lipoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "SVC compression", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "VATS", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "excision", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mediastinal tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "facial swelling", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "arm edema", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "7cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "mediastinal mass", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Lipoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "SVC compression", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "excision", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "VATS", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "fatty tumor", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "compressing", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "dissection", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "excised", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "endoscopic retrieval bag", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "SVC decompressed", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_10, "visible improvement in venous caliber", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "7.2 x 6.5 x 4.8 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "fatty mass", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "60mL", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)