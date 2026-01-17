import sys
from pathlib import Path

# 1. Dynamic Repo Root Setup
try:
    REPO_ROOT = Path(__file__).resolve().parents[3]
    sys.path.append(str(REPO_ROOT))
except NameError:
    REPO_ROOT = Path('.').resolve()

# 2. Import Utility
from scripts.add_training_case import add_case

# 3. Helper Function
def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a substring.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term),
        "token": term
    }

# 4. Data Payload
BATCH_DATA = []

# ==========================================
# Case 1: 1776_syn_1
# ==========================================
text_1 = """Indication: Recurrent pleural effusion (L).
Proc: US-guided pleural drainage/catheter.
- Site marked US.
- Thoracentesis attempt 1: Dry tap.
- Repositioned 2 spaces lower.
- 18G needle entered fluid. Wire passed.
- 8Fr Pigtail placed.
- Output: 1400cc clear yellow.
Plan: Culture/Cyto. Catheter to drainage."""

entities_1 = [
    {"label": "CTX_HISTORICAL",     **get_span(text_1, "Recurrent", 1)},
    {"label": "OBS_LESION",         **get_span(text_1, "pleural effusion", 1)},
    {"label": "LATERALITY",         **get_span(text_1, "(L)", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "US-guided", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_1, "pleural", 1)},
    {"label": "PROC_ACTION",        **get_span(text_1, "drainage", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_1, "catheter", 1)},
    {"label": "PROC_METHOD",        **get_span(text_1, "US", 2)}, # "Site marked US"
    {"label": "PROC_ACTION",        **get_span(text_1, "Thoracentesis", 1)},
    {"label": "OBS_FINDING",        **get_span(text_1, "Dry tap", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_1, "18G", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "needle", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_1, "Wire", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "8Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_1, "Pigtail", 1)},
    {"label": "MEAS_VOL",           **get_span(text_1, "1400cc", 1)},
    {"label": "OBS_FINDING",        **get_span(text_1, "clear yellow", 1)},
    # FIX: Changed occurrence from 2 to 1 because "Catheter" (capitalized) only appears once.
    {"label": "DEV_CATHETER",       **get_span(text_1, "Catheter", 1)},
]
BATCH_DATA.append({"id": "1776_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 1776_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: The patient presented with a recurrent large left pleural effusion. Ultrasound guidance was utilized to id[REDACTED] a pocket of fluid. An initial thoracentesis attempt at the primary site yielded no return. The puncture site was adjusted two intercostal spaces caudally. A Seldinger technique was then successfully employed to access the pleural space. An 8-French pigtail catheter was inserted and secured. Immediate drainage yielded 1400 mL of clear, exudative-appearing fluid. The patient tolerated the procedure well."""

entities_2 = [
    {"label": "CTX_HISTORICAL",     **get_span(text_2, "recurrent", 1)},
    {"label": "OBS_FINDING",        **get_span(text_2, "large", 1)},
    {"label": "LATERALITY",         **get_span(text_2, "left", 1)},
    {"label": "OBS_LESION",         **get_span(text_2, "pleural effusion", 1)},
    {"label": "PROC_METHOD",        **get_span(text_2, "Ultrasound guidance", 1)},
    {"label": "PROC_ACTION",        **get_span(text_2, "thoracentesis", 1)},
    {"label": "PROC_METHOD",        **get_span(text_2, "Seldinger technique", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_2, "pleural space", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_2, "8-French", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_2, "pigtail catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_2, "drainage", 1)},
    {"label": "MEAS_VOL",           **get_span(text_2, "1400 mL", 1)},
    {"label": "OBS_FINDING",        **get_span(text_2, "clear, exudative-appearing", 1)},
    {"label": "SPECIMEN",           **get_span(text_2, "fluid", 2)},
]
BATCH_DATA.append({"id": "1776_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 1776_syn_3
# ==========================================
text_3 = """Code: 32557 (Pleural drainage with indwelling catheter, with imaging).
Narrative:
- Ultrasound guidance used to verify fluid and entry.
- Percutaneous entry made (initial dry tap bundled).
- Guide wire inserted, tract dilated.
- Tunneled indwelling catheter (Pigtail 8Fr) placed.
- 1400cc drained.
Note: Imaging guidance is integral to 32557."""

entities_3 = [
    {"label": "PROC_ACTION",        **get_span(text_3, "Pleural drainage", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_3, "indwelling catheter", 1)},
    {"label": "PROC_METHOD",        **get_span(text_3, "Ultrasound guidance", 1)},
    {"label": "OBS_FINDING",        **get_span(text_3, "dry tap", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_3, "Guide wire", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_3, "indwelling catheter", 2)},
    {"label": "DEV_CATHETER",       **get_span(text_3, "Pigtail", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_3, "8Fr", 1)},
    {"label": "MEAS_VOL",           **get_span(text_3, "1400cc", 1)},
]
BATCH_DATA.append({"id": "1776_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 1776_syn_4
# ==========================================
text_4 = """Procedure: Chest Tube/Pigtail Placement
Patient: G. Washington
1. US scan of L chest.
2. Local lidocaine.
3. First stick dry.
4. Moved down. Hit fluid.
5. Seldinger technique -> 8Fr Pigtail.
6. Drained 1.4L yellow fluid.
7. Secured and dressed."""

entities_4 = [
    {"label": "DEV_CATHETER",       **get_span(text_4, "Chest Tube", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_4, "Pigtail", 1)},
    {"label": "PROC_ACTION",        **get_span(text_4, "Placement", 1)},
    {"label": "PROC_METHOD",        **get_span(text_4, "US scan", 1)},
    {"label": "LATERALITY",         **get_span(text_4, "L", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_4, "chest", 1)},
    {"label": "MEDICATION",         **get_span(text_4, "lidocaine", 1)},
    {"label": "OBS_FINDING",        **get_span(text_4, "dry", 1)},
    {"label": "PROC_METHOD",        **get_span(text_4, "Seldinger technique", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_4, "8Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_4, "Pigtail", 2)},
    {"label": "MEAS_VOL",           **get_span(text_4, "1.4L", 1)},
    {"label": "OBS_FINDING",        **get_span(text_4, "yellow fluid", 1)},
]
BATCH_DATA.append({"id": "1776_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 1776_syn_5
# ==========================================
text_5 = """Mr [REDACTED] needed his chest drained again recurrent effusion left side. used the ultrasound. tried one spot with the needle and got nothing dry tap. moved down a couple ribs and got it. put the wire in then the 8 french pigtail catheter. drained about 1400cc of yellow fluid. leaving the tube in for now sending fluid to lab."""

entities_5 = [
    {"label": "ANAT_PLEURA",        **get_span(text_5, "chest", 1)},
    {"label": "PROC_ACTION",        **get_span(text_5, "drained", 1)},
    {"label": "CTX_HISTORICAL",     **get_span(text_5, "recurrent", 1)},
    {"label": "OBS_LESION",         **get_span(text_5, "effusion", 1)},
    {"label": "LATERALITY",         **get_span(text_5, "left", 1)},
    {"label": "PROC_METHOD",        **get_span(text_5, "ultrasound", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_5, "needle", 1)},
    {"label": "OBS_FINDING",        **get_span(text_5, "dry tap", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_5, "wire", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_5, "8 french", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_5, "pigtail catheter", 1)},
    {"label": "MEAS_VOL",           **get_span(text_5, "1400cc", 1)},
    {"label": "OBS_FINDING",        **get_span(text_5, "yellow fluid", 1)},
]
BATCH_DATA.append({"id": "1776_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 1776_syn_6
# ==========================================
text_6 = """Ultrasound-guided placement of indwelling pleural catheter. Indication was recurrent left pleural effusion. Local anesthesia was administered. An initial thoracentesis attempt was dry. The site was repositioned. The pleural space was accessed, and an 8Fr pigtail catheter was placed using Seldinger technique. 1400cc of clear yellow fluid was drained. The catheter was secured."""

entities_6 = [
    {"label": "PROC_METHOD",        **get_span(text_6, "Ultrasound-guided", 1)},
    {"label": "PROC_ACTION",        **get_span(text_6, "placement", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_6, "indwelling pleural catheter", 1)},
    {"label": "CTX_HISTORICAL",     **get_span(text_6, "recurrent", 1)},
    {"label": "LATERALITY",         **get_span(text_6, "left", 1)},
    {"label": "OBS_LESION",         **get_span(text_6, "pleural effusion", 1)},
    {"label": "PROC_ACTION",        **get_span(text_6, "thoracentesis", 1)},
    {"label": "OBS_FINDING",        **get_span(text_6, "dry", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_6, "pleural space", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_6, "8Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_6, "pigtail catheter", 1)},
    {"label": "PROC_METHOD",        **get_span(text_6, "Seldinger technique", 1)},
    {"label": "MEAS_VOL",           **get_span(text_6, "1400cc", 1)},
    {"label": "OBS_FINDING",        **get_span(text_6, "clear yellow fluid", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_6, "catheter", 3)},
]
BATCH_DATA.append({"id": "1776_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 1776_syn_7
# ==========================================
text_7 = """[Indication]
Recurrent large left pleural effusion.
[Anesthesia]
Local (Lidocaine).
[Description]
US guidance used. Initial attempt dry. Successful access 2 interspaces lower. 8Fr Pigtail catheter placed. 1400cc drained.
[Plan]
Drainage to bag. Fluid analysis."""

entities_7 = [
    {"label": "CTX_HISTORICAL",     **get_span(text_7, "Recurrent", 1)},
    {"label": "OBS_FINDING",        **get_span(text_7, "large", 1)},
    {"label": "LATERALITY",         **get_span(text_7, "left", 1)},
    {"label": "OBS_LESION",         **get_span(text_7, "pleural effusion", 1)},
    {"label": "MEDICATION",         **get_span(text_7, "Lidocaine", 1)},
    {"label": "PROC_METHOD",        **get_span(text_7, "US guidance", 1)},
    {"label": "OBS_FINDING",        **get_span(text_7, "dry", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_7, "8Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_7, "Pigtail catheter", 1)},
    {"label": "MEAS_VOL",           **get_span(text_7, "1400cc", 1)},
    {"label": "PROC_ACTION",        **get_span(text_7, "drained", 1)},
]
BATCH_DATA.append({"id": "1776_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 1776_syn_8
# ==========================================
text_8 = """Due to the patient's recurrent left pleural effusion, we proceeded with drainage. Using ultrasound, we marked the site. Our first attempt with the needle yielded no fluid, so we repositioned lower on the chest wall. On the second attempt, we successfully accessed the fluid pocket. We placed an 8 French pigtail catheter over a guidewire and drained 1400cc of fluid. The catheter was secured for ongoing drainage."""

entities_8 = [
    {"label": "CTX_HISTORICAL",     **get_span(text_8, "recurrent", 1)},
    {"label": "LATERALITY",         **get_span(text_8, "left", 1)},
    {"label": "OBS_LESION",         **get_span(text_8, "pleural effusion", 1)},
    {"label": "PROC_ACTION",        **get_span(text_8, "drainage", 1)},
    {"label": "PROC_METHOD",        **get_span(text_8, "ultrasound", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_8, "needle", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_8, "chest wall", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_8, "8 French", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_8, "pigtail catheter", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_8, "guidewire", 1)},
    {"label": "MEAS_VOL",           **get_span(text_8, "1400cc", 1)},
    {"label": "SPECIMEN",           **get_span(text_8, "fluid", 2)},
    {"label": "DEV_CATHETER",       **get_span(text_8, "catheter", 2)},
]
BATCH_DATA.append({"id": "1776_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 1776_syn_9
# ==========================================
text_9 = """Intervention: Percutaneous pleural drainage with catheter insertion.
Method: Sonographic localization. The initial aspiration was non-productive. A subsequent puncture inferiorly successfully engaged the effusion. An 8Fr drainage catheter was sited. 
Volume: 1400ml of serous fluid was evacuated."""

entities_9 = [
    {"label": "ANAT_PLEURA",        **get_span(text_9, "pleural", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "drainage", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_9, "catheter", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "insertion", 1)},
    {"label": "PROC_METHOD",        **get_span(text_9, "Sonographic", 1)},
    {"label": "PROC_ACTION",        **get_span(text_9, "aspiration", 1)},
    {"label": "OBS_LESION",         **get_span(text_9, "effusion", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_9, "8Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_9, "drainage catheter", 1)},
    {"label": "MEAS_VOL",           **get_span(text_9, "1400ml", 1)},
    {"label": "OBS_FINDING",        **get_span(text_9, "serous fluid", 1)},
]
BATCH_DATA.append({"id": "1776_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 1776
# ==========================================
text_10 = """**Procedure Note: Pleural Intervention**
**Date:** [REDACTED]
**Patient:** G. Washington (MRN: [REDACTED])
**Attending:** Dr. B. Ross

**History:** Recurrent large left pleural effusion. Previous thoracentesis showed exudate, cytology negative. 

**Procedure:**
US guidance used to mark site. 1% Lidocaine. 
Attempted thoracentesis with 18G needle - no fluid returned (Dry Tap). Repositioned 2 interspaces lower. 

Successfully accessed pleural space with 18G needle. Guide wire passed. Dilated tract. 8Fr Pigtail catheter placed. 
Drained 1400cc clear yellow fluid. 

**Plan:** Leave pigtail in place for drainage. Send fluid for culture/cyto."""

entities_10 = [
    {"label": "PROC_ACTION",        **get_span(text_10, "Pleural Intervention", 1)},
    {"label": "CTX_HISTORICAL",     **get_span(text_10, "Recurrent", 1)},
    {"label": "OBS_FINDING",        **get_span(text_10, "large", 1)},
    {"label": "LATERALITY",         **get_span(text_10, "left", 1)},
    {"label": "OBS_LESION",         **get_span(text_10, "pleural effusion", 1)},
    {"label": "CTX_HISTORICAL",     **get_span(text_10, "Previous", 1)},
    {"label": "PROC_ACTION",        **get_span(text_10, "thoracentesis", 1)},
    {"label": "OBS_FINDING",        **get_span(text_10, "exudate", 1)},
    {"label": "PROC_METHOD",        **get_span(text_10, "US guidance", 1)},
    {"label": "MEDICATION",         **get_span(text_10, "Lidocaine", 1)},
    {"label": "PROC_ACTION",        **get_span(text_10, "thoracentesis", 2)},
    {"label": "DEV_NEEDLE",         **get_span(text_10, "18G", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "needle", 1)},
    {"label": "OBS_FINDING",        **get_span(text_10, "Dry Tap", 1)},
    {"label": "ANAT_PLEURA",        **get_span(text_10, "pleural space", 1)},
    {"label": "DEV_NEEDLE",         **get_span(text_10, "18G", 2)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "needle", 2)},
    {"label": "DEV_INSTRUMENT",     **get_span(text_10, "Guide wire", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_10, "8Fr", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "Pigtail catheter", 1)},
    {"label": "MEAS_VOL",           **get_span(text_10, "1400cc", 1)},
    {"label": "OBS_FINDING",        **get_span(text_10, "clear yellow fluid", 1)},
    {"label": "DEV_CATHETER",       **get_span(text_10, "pigtail", 1)},
]
BATCH_DATA.append({"id": "1776", "text": text_10, "entities": entities_10})

# ==========================================
# Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
