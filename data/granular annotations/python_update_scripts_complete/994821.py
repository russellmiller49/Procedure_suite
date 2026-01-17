import sys
from pathlib import Path

# ==========================================
# 1. Setup Environment
# ==========================================
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
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Case 1: 994821_syn_1
# ==========================================
id_1 = "994821_syn_1"
text_1 = """Indication: Massive recurrent right pleural effusion.
Procedure: US-Guided Chest Tube.
- US: Large free-flowing effusion.
- 14Fr pigtail placed (Seldinger).
- 1200mL drained.
- Fluid sent for cytology/culture.
- CXR confirmed placement.
Plan: Drain to dry."""

entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "US-Guided", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Chest Tube", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "US", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "free-flowing", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14Fr pigtail", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "1200mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "drained", 1)},
    {"label": "SPECIMEN", **get_span(text_1, "Fluid", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 994821_syn_2
# ==========================================
id_2 = "994821_syn_2"
text_2 = """HISTORY: [REDACTED], a 62-year-old male with Stage IV lung malignancy, presented with severe dyspnea secondary to a massive recurrent right pleural effusion.
PROCEDURE: The right hemithorax was prepared. Bedside ultrasound localized a large, free-flowing effusion amenable to drainage. Under local anesthesia, a 14 French pigtail catheter was inserted utilizing the Seldinger technique. Immediate drainage of 1200 mL of serous fluid provided symptomatic relief. The catheter was secured and placed to suction. Post-procedural imaging verified appropriate positioning.
IMPRESSION: Successful palliation of malignant pleural effusion via indwelling catheter."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignancy", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "hemithorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "free-flowing", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "effusion", 2)},
    {"label": "PROC_ACTION", **get_span(text_2, "drainage", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "14 French pigtail catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "pigtail catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "drainage", 2)},
    {"label": "MEAS_VOL", **get_span(text_2, "1200 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "serous", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_2, "symptomatic relief", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "catheter", 2)},
    {"label": "OBS_LESION", **get_span(text_2, "effusion", 3)},
    {"label": "DEV_CATHETER", **get_span(text_2, "indwelling catheter", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 994821_syn_3
# ==========================================
id_3 = "994821_syn_3"
text_3 = """Code: 32557 (Pleural drainage with insertion of indwelling catheter, with imaging guidance).
Technique: Percutaneous insertion of 14Fr pigtail catheter.
Guidance: Real-time ultrasound used to id[REDACTED] pocket and guide needle entry.
Drainage: 1200mL removed.
Device: Indwelling catheter left in place for continued drainage."""

entities_3 = [
    {"label": "ANAT_PLEURA", **get_span(text_3, "Pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "drainage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "indwelling catheter", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "14Fr pigtail catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "ultrasound", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_3, "needle", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "1200mL", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "Indwelling catheter", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "drainage", 2)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 994821_syn_4
# ==========================================
id_4 = "994821_syn_4"
text_4 = """Procedure: Chest Tube Placement
Patient: [REDACTED]
Steps:
1. Consent obtained. Time out.
2. US scan of right chest - large fluid pocket.
3. Lidocaine prep.
4. Needle in, wire down, dilated tract.
5. 14Fr pigtail over wire.
6. Drained 1.2L straw fluid.
7. Stitched in place. Hooked to suction.
Plan: CXR."""

entities_4 = [
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest Tube", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "US", 1)},
    {"label": "LATERALITY", **get_span(text_4, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "chest", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Lidocaine", 1)},
    {"label": "DEV_NEEDLE", **get_span(text_4, "Needle", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_4, "14Fr pigtail", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "pigtail", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "1.2L", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "straw", 1)},
    {"label": "SPECIMEN", **get_span(text_4, "fluid", 2)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 994821_syn_5
# ==========================================
id_5 = "994821_syn_5"
text_5 = """Note for [REDACTED] 62M lung ca with big effusion right side. Put a chest tube in today. Used ultrasound to find the spot. Put in a 14 french pigtail using the kit. Got a liter two out right away straw colored. Patient felt way better. Sewed it in connected to wall suction. Xray looks good."""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "ca", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ultrasound", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_5, "14 french pigtail", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "pigtail", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "liter two", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "straw colored", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_5, "Patient felt way better", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 994821_syn_6
# ==========================================
id_6 = "994821_syn_6"
text_6 = """Ultrasound-guided right chest tube placement. Patient 62M with metastatic lung cancer. Large right effusion. Local anesthesia. 14Fr pigtail catheter inserted via Seldinger technique. 1200mL drained. Catheter secured. Complications none. CXR confirms position. Plan drainage and possible pleurodesis."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Ultrasound-guided", 1)},
    {"label": "LATERALITY", **get_span(text_6, "right", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lung cancer", 1)},
    {"label": "LATERALITY", **get_span(text_6, "right", 2)},
    {"label": "OBS_LESION", **get_span(text_6, "effusion", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "14Fr pigtail catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "1200mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "drained", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Catheter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "Complications none", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "drainage", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "pleurodesis", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 994821_syn_7
# ==========================================
id_7 = "994821_syn_7"
text_7 = """[Indication]
Recurrent massive right pleural effusion, Stage IV lung cancer.
[Anesthesia]
Local (1% Lidocaine).
[Description]
US-guided insertion of 14Fr pigtail catheter (Seldinger technique). 1200mL drained. Tube secured and placed on suction.
[Plan]
Drain to dry, consider talc."""

entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "effusion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "cancer", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Lidocaine", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "US-guided", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_7, "14Fr pigtail catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "pigtail catheter", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "1200mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "drained", 1)},
    {"label": "MEDICATION", **get_span(text_7, "talc", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 994821_syn_8
# ==========================================
id_8 = "994821_syn_8"
text_8 = """[REDACTED] with a massive pleural effusion related to his lung cancer. We decided to place a chest tube for drainage. Using ultrasound guidance, we inserted a small-bore pigtail catheter into the right chest. We drained 1200mL of fluid immediately, which relieved his shortness of breath. The tube was secured, and he will be monitored on the floor."""

entities_8 = [
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "effusion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "cancer", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "drainage", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "ultrasound", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_8, "small-bore pigtail catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "pigtail catheter", 1)},
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "chest", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "1200mL", 1)},
    {"label": "SPECIMEN", **get_span(text_8, "fluid", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(text_8, "relieved his shortness of breath", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 994821_syn_9
# ==========================================
id_9 = "994821_syn_9"
text_9 = """Procedure: Image-guided pleural drainage with catheterization.
Action: The effusion was visualized sonographically. Access was established percutaneously. An indwelling catheter was advanced into the pleural space. Significant volume (1200mL) was evacuated. The device was anchored.
Result: Effective drainage."""

entities_9 = [
    {"label": "ANAT_PLEURA", **get_span(text_9, "pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "drainage", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "sonographically", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "indwelling catheter", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "pleural space", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "1200mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "drainage", 2)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 994821
# ==========================================
id_10 = "994821"
text_10 = """Procedure Note
Patient: [REDACTED] Miller (MRN: [REDACTED])
Date: [REDACTED]
Dr. Sarah O'Connor, Attending Pulmonologist.

[REDACTED] a 62M with Stage IV lung cancer and a recurrent massive right pleural effusion causing severe dyspnea. He was admitted for management. We discussed options including repeat thoracentesis vs. PleurX vs. Chest Tube/Pleurodesis. He opted for a chest tube for drainage and possible talc slurry.

Time Out performed. The patient was positioned sitting up. The right hemithorax was prepped and draped. Ultrasound id[REDACTED] a large free-flowing effusion. 1% Lidocaine was used for local anesthesia. A 14Fr pigtail catheter was inserted using Seldinger technique under real-time ultrasound guidance. 1200mL of straw-colored fluid was drained immediately. The tube was secured and connected to -20cmH2O suction. Fluid sent for cytology and culture. Post-procedure CXR confirmed placement. Patient tolerated well.

Assessment: Successful US-guided small-bore chest tube placement right hemithorax.
Plan: Drain to dry, then consider talc slurry."""

entities_10 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lung", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "cancer", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "thoracentesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "PleurX", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest Tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "drainage", 1)},
    {"label": "MEDICATION", **get_span(text_10, "talc slurry", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "hemithorax", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Ultrasound", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "free-flowing", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 2)},
    {"label": "MEDICATION", **get_span(text_10, "Lidocaine", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "14Fr pigtail catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "pigtail catheter", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ultrasound", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "1200mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "straw-colored", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "drained", 1)},
    {"label": "MEAS_PRESS", **get_span(text_10, "-20cmH2O", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Fluid", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "US-guided", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "small-bore chest tube", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 2)},
    {"label": "LATERALITY", **get_span(text_10, "right", 3)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "hemithorax", 2)},
    {"label": "MEDICATION", **get_span(text_10, "talc slurry", 2)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)