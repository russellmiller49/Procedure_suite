import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add cases
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for local testing if the module isn't strictly in 'scripts'
    sys.path.append(str(REPO_ROOT))
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
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 5018184_syn_1
# ==========================================
t1 = """Indication: Malignant CAO RMS.
Findings: 60% obstruction.
Procedure:
- Rigid bronch.
- Laser ablation/excision.
- Multiple passes.
Result: 35% residual.
EBL: 150ml.
Plan: ICU."""

e1 = [
    {"label": "ANAT_AIRWAY", **get_span(t1, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t1, "60% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Rigid bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "ablation", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "excision", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "35% residual", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "150ml", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 5018184_syn_2
# ==========================================
t2 = """OPERATIVE SUMMARY: [REDACTED] 60% obstruction of the right mainstem (RMS) bronchus. Under general anesthesia, rigid bronchoscopy was initiated. The tumor was addressed via laser photoresection and mechanical excision to facilitate removal. Multiple passes were required to debulk the lesion. Post-intervention, the obstruction was reduced to 35%. Hemostasis was secured. Specimens were submitted for pathologic evaluation."""

e2 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t2, "60% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "right mainstem (RMS) bronchus", 1)},
    {"label": "PROC_METHOD", **get_span(t2, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t2, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t2, "lesion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "reduced to 35%", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 5018184_syn_3
# ==========================================
t3 = """CPT Code: 31640 (Bronchoscopy with excision of tumor).
Technique: Laser ablation and mechanical removal.
Location: Right Mainstem Bronchus.
Details:
- Visualization of 60% stenosis.
- Laser applied to devitalize tissue.
- Mechanical excision of tumor mass.
- Hemostasis.
Outcome: 35% residual obstruction."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "ablation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "Right Mainstem Bronchus", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t3, "60% stenosis", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "excision", 2)},
    {"label": "OBS_LESION", **get_span(t3, "tumor mass", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "35% residual obstruction", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 5018184_syn_4
# ==========================================
t4 = """Procedure: Tumor Excision/Ablation
Patient: [REDACTED]
Steps:
1. Rigid scope inserted.
2. RMS tumor visualized (60%).
3. Laser used to ablate/excise.
4. Tumor removed.
5. Hemostasis confirmed.
Plan: ICU."""

e4 = [
    {"label": "OBS_LESION", **get_span(t4, "Tumor", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Excision", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Ablation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "Rigid scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t4, "RMS", 1)},
    {"label": "OBS_LESION", **get_span(t4, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t4, "60%", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "ablate", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "excise", 1)},
    {"label": "OBS_LESION", **get_span(t4, "Tumor", 2)}
]
BATCH_DATA.append({"id": "5018184_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 5018184_syn_5
# ==========================================
t5 = """[REDACTED] here for tumor removal in the RMS blocking 60 percent. Used the rigid scope and the laser to cut it out. Did a few passes. Got it down to 35 percent. Bleeding was 150cc stopped it okay. Sending samples to lab and patient to ICU."""

e5 = [
    {"label": "OBS_LESION", **get_span(t5, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t5, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t5, "blocking 60 percent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "rigid scope", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t5, "35 percent", 1)},
    {"label": "MEAS_VOL", **get_span(t5, "150cc", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 5018184_syn_6
# ==========================================
t6 = """Indication: Malignant central airway obstruction, ~60% obstruction at RMS. Under general anesthesia, rigid bronchoscopy was performed. Endobronchial tumor id[REDACTED] at RMS. Laser ablation performed with sequential tumor removal. Multiple passes performed to achieve maximal debulking. Post-procedure obstruction was ~35% residual obstruction. EBL was ~150mL. Hemostasis achieved. Specimens sent for histology."""

e6 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t6, "~60% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(t6, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "RMS", 2)},
    {"label": "PROC_ACTION", **get_span(t6, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(t6, "tumor", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "~35% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "~150mL", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 5018184_syn_7
# ==========================================
t7 = """[Indication]
Malignant CAO, RMS (60%).
[Anesthesia]
General, Rigid Bronch.
[Description]
Laser ablation and excision performed. Tumor removed. Residual obstruction 35%. EBL 150ml.
[Plan]
ICU observation."""

e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "RMS", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t7, "60%", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "ablation", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "excision", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "Residual obstruction 35%", 1)},
    {"label": "MEAS_VOL", **get_span(t7, "150ml", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 5018184_syn_8
# ==========================================
t8 = """[REDACTED] bronchoscopy for a tumor in the right mainstem bronchus causing 60% obstruction. We used the laser to ablate and excise the tumor tissue. After multiple passes, we reduced the obstruction to 35%. Bleeding was controlled, and the patient remained stable. He was transferred to the ICU for overnight care."""

e8 = [
    {"label": "OBS_LESION", **get_span(t8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t8, "right mainstem bronchus", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t8, "60% obstruction", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "ablate", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "excise", 1)},
    {"label": "OBS_LESION", **get_span(t8, "tumor", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "35%", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 5018184_syn_9
# ==========================================
t9 = """Indication: Malignant central airway blockage.
Pre-procedure: ~60% occlusion at RMS.
PROCEDURE: Under general anesthesia, rigid bronchoscopy was conducted. Endobronchial neoplasm detected at RMS. Laser ablation executed with sequential tumor extraction. Multiple passes were done to attain maximal debulking.
Post-procedure: ~35% residual occlusion.
EBL: ~150mL."""

e9 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t9, "~60% occlusion", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "neoplasm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "RMS", 2)},
    {"label": "PROC_ACTION", **get_span(t9, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(t9, "tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t9, "~35% residual occlusion", 1)},
    {"label": "MEAS_VOL", **get_span(t9, "~150mL", 1)}
]
BATCH_DATA.append({"id": "5018184_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 5018184
# ==========================================
t10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Mark Taylor

Indication: Malignant central airway obstruction
Pre-procedure: ~60% obstruction at RMS

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at RMS.
Laser ablation performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Post-procedure: ~35% residual obstruction.
EBL: ~150mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Taylor, MD"""

e10 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(t10, "~60% obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RMS", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "RMS", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(t10, "tumor", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "~35% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "~150mL", 1)}
]
BATCH_DATA.append({"id": "5018184", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)