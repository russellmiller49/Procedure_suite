import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent / "src"
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
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1587446_syn_1
# ==========================================
text_1 = """Indication: Malignant CAO RMS.
Findings: 66% obstruction.
Procedure:
- Rigid bronch.
- Cryoextraction of tumor.
- APC for hemostasis/base.
- Balloon dilation.
Result: 17% residual.
EBL: 200ml.
Plan: ICU."""

entities_1 = [
    {"label": "ANAT_AIRWAY", **get_span(text_1, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "66% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Cryoextraction", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "APC", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "hemostasis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "17% residual", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1587446_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: [REDACTED] 66% malignant obstruction of the right mainstem (RMS). Rigid bronchoscopy was utilized. The tumor was addressed via cryoextraction, allowing for en bloc removal of significant tissue volume. Following cryodebulking, the tumor base was treated with APC for hemostasis and ablation. Residual stenosis was managed with balloon dilation. Final assessment showed 17% residual obstruction. Estimated blood loss was 200mL.
DISPOSITION: ICU admission."""

entities_2 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "66% malignant obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "right mainstem", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "cryoextraction", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "cryodebulking", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(text_2, "APC", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "hemostasis", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "17% residual obstruction", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1587446_syn_3
# ==========================================
text_3 = """CPT Code: 31641 (Bronchoscopy with destruction of tumor).
Technique: Cryoextraction and APC.
Location: Right Mainstem Bronchus.
Notes: 
- Cryoprobe used to freeze and extract tumor chunks.
- APC used for base destruction.
- Balloon dilation included for residual stenosis.
- EBL 200ml controlled."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Cryoextraction", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "APC", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Right Mainstem Bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Cryoprobe", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(text_3, "APC", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "destruction", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "dilation", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1587446_syn_4
# ==========================================
text_4 = """Procedure: Tumor Debulking (Cryo)
Patient: [REDACTED]teps:
1. Rigid scope to RMS.
2. Tumor id[REDACTED] (66%).
3. Cryoprobe used to extract tumor.
4. APC used for clean up and bleeding.
5. Balloon dilation for remaining narrowing.
6. Hemostasis confirmed.
Plan: ICU."""

entities_4 = [
    {"label": "OBS_LESION", **get_span(text_4, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Cryo", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Rigid scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "RMS", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Tumor", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_4, "66%", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Cryoprobe", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "dilation", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "Hemostasis confirmed", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1587446_syn_5
# ==========================================
text_5 = """Anthony Baker for tumor debulking in the RMS blocking 66 percent. We used the cryo probe to freeze the tumor and pull it out in big chunks. Then used the APC to stop the bleeding and burn the base. Also dilated it a bit. Got it down to 17 percent. Lost about 200cc of blood but got it stopped. Sending him to ICU."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "debulking", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "66 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "cryo probe", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 2)},
    {"label": "PROC_METHOD", **get_span(text_5, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "dilated", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "17 percent", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1587446_syn_6
# ==========================================
text_6 = """Indication: Malignant central airway obstruction, ~66% obstruction at RMS. Under general anesthesia, rigid bronchoscopy was performed. Endobronchial tumor id[REDACTED] at RMS. Cryoextraction performed with sequential tumor removal. Multiple passes performed to achieve maximal debulking. Additional APC/laser used for hemostasis and tumor base ablation. Balloon dilation performed for residual stenosis. Post-procedure obstruction was ~17% residual obstruction. EBL was ~200mL. Specimens sent for histology."""

entities_6 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "~66% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "RMS", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "Cryoextraction", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "APC", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "laser", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 3)},
    {"label": "PROC_ACTION", **get_span(text_6, "ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "~17% residual obstruction", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1587446_syn_7
# ==========================================
text_7 = """[Indication]
Malignant CAO, RMS (66%).
[Anesthesia]
General, Rigid Bronch.
[Description]
Cryoextraction of tumor performed. APC for hemostasis. Balloon dilation. Residual obstruction 17%. EBL 200ml.
[Plan]
ICU observation."""

entities_7 = [
    {"label": "ANAT_AIRWAY", **get_span(text_7, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "66%", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Cryoextraction", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "tumor", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "APC", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "hemostasis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "17%", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1587446_syn_8
# ==========================================
text_8 = """[REDACTED] bronchoscopy for a tumor in his right mainstem bronchus. We used cryoextraction to remove the tumor tissue efficiently. After the bulk of the tumor was removed, we used APC to treat the base and control bleeding. We also dilated the airway with a balloon to maximize patency. The obstruction was reduced from 66% to 17%. He lost about 200mL of blood, but hemostasis was achieved before finishing. He is heading to the ICU."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "right mainstem bronchus", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "cryoextraction", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 3)},
    {"label": "PROC_METHOD", **get_span(text_8, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "dilated", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "balloon", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "66%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "17%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "hemostasis was achieved", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1587446_syn_9
# ==========================================
text_9 = """Indication: Malignant central airway blockage.
Pre-procedure: ~66% occlusion at RMS.
PROCEDURE: Under general anesthesia, rigid bronchoscopy was executed. Endobronchial neoplasm id[REDACTED] at RMS. Cryoextraction performed with sequential tumor withdrawal. Multiple passes were done to attain maximal debulking. Additional APC/laser utilized for hemostasis and tumor base cauterization. Balloon dilation executed for residual stenosis.
Post-procedure: ~17% residual occlusion.
EBL: ~200mL."""

entities_9 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_9, "~66% occlusion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "neoplasm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "RMS", 2)},
    {"label": "PROC_ACTION", **get_span(text_9, "Cryoextraction", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "APC", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "laser", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_9, "cauterization", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "~17% residual occlusion", 1)},
]
BATCH_DATA.append({"id": "1587446_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1587446
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Sarah Williams
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Malignant central airway obstruction
Pre-procedure: ~66% obstruction at RMS

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at RMS.
Cryoextraction performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Additional APC/laser used for hemostasis and tumor base ablation.
Balloon dilation performed for residual stenosis.
Post-procedure: ~17% residual obstruction.
EBL: ~200mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Williams, MD"""

entities_10 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "~66% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Cryoextraction", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "APC", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "laser", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "hemostasis", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "dilation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "~17% residual obstruction", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Hemostasis achieved", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 1)},
]
BATCH_DATA.append({"id": "1587446", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)