import sys
from pathlib import Path

# Add the repository root to the python path
try:
    REPO_ROOT = Path(__file__).resolve().parents[2]
except NameError:
    REPO_ROOT = Path('.').resolve().parents[2]

sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 940211_syn_1
# ==========================================
t1 = """Indication: Exudative effusion, nodules.
Proc: Med Thoracoscopy + Biopsy.
Findings: Diffuse nodules parietal pleura.
Action: Drained 900cc. 10 biopsies taken.
Result: No complications. Pigtail removed.
Plan: Admit."""

e1 = [
    {"label": "OBS_LESION", **get_span(t1, "effusion", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodules", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Med Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Biopsy", 1)},
    {"label": "OBS_LESION", **get_span(t1, "nodules", 2)},
    {"label": "ANAT_PLEURA", **get_span(t1, "parietal pleura", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "900cc", 1)},
    {"label": "MEAS_COUNT", **get_span(t1, "10", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "biopsies", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No complications", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Pigtail", 1)}
]
BATCH_DATA.append({"id": "940211_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 940211_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Medical Thoracoscopy.
INDICATION: Undiagnosed pleural effusion.
FINDINGS: Visual inspection of the right pleural space revealed diffuse nodularity of the parietal pleura. 
PROCEDURE: The space was accessed via a single port. 900 mL of fluid was evacuated. Multiple forceps biopsies were obtained from the parietal pleura for diagnostic evaluation. The lung was re-expanded and the catheter removed."""

e2 = [
    {"label": "PROC_METHOD", **get_span(t2, "Medical Thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t2, "pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(t2, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural space", 1)},
    {"label": "OBS_LESION", **get_span(t2, "nodularity", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "parietal pleura", 1)},
    {"label": "MEAS_VOL", **get_span(t2, "900 mL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t2, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "parietal pleura", 2)},
    {"label": "DEV_CATHETER", **get_span(t2, "catheter", 1)}
]
BATCH_DATA.append({"id": "940211_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 940211_syn_3
# ==========================================
t3 = """Code: 32604 (Thoracoscopy with pleural biopsy).
Details: Diagnostic inspection + Biopsy of parietal pleura. No talc (32650) or lung biopsy (32609) performed. Catheter was removed at end of case, so no chest tube code."""

e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "Thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "pleural", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t3, "parietal pleura", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "Catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(t3, "chest tube", 1)}
]
BATCH_DATA.append({"id": "940211_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 940211_syn_4
# ==========================================
t4 = """Procedure: Pleuroscopy
Patient: [REDACTED]
1. Port in R 6th ICS.
2. Drained 900cc fluid.
3. Saw nodules everywhere.
4. Biopsied x10.
5. Lung expanded.
6. Pulled tube, closed skin."""

e4 = [
    {"label": "PROC_METHOD", **get_span(t4, "Pleuroscopy", 1)},
    {"label": "LATERALITY", **get_span(t4, "R", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "6th ICS", 1)},
    {"label": "MEAS_VOL", **get_span(t4, "900cc", 1)},
    {"label": "OBS_LESION", **get_span(t4, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Biopsied", 1)},
    {"label": "MEAS_COUNT", **get_span(t4, "10", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "tube", 1)}
]
BATCH_DATA.append({"id": "940211_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 940211_syn_5
# ==========================================
t5 = """evelyn sanders fluid on the right lung looks like cancer. did the thoracoscopy looked inside nodules all over the wall. took a bunch of biopsies like 10 of them. drained the fluid out. didn't leave a chest tube just stitched it up. waiting on path."""

e5 = [
    {"label": "LATERALITY", **get_span(t5, "right", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t5, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(t5, "wall", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t5, "10", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "chest tube", 1)}
]
BATCH_DATA.append({"id": "940211_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 940211_syn_6
# ==========================================
t6 = """Medical thoracoscopy performed for pleural effusion. Right pleural space accessed. 900cc fluid removed. Parietal pleura showed diffuse studding; multiple biopsies taken. No pleurodesis performed. Catheter removed at conclusion. Patient stable."""

e6 = [
    {"label": "PROC_METHOD", **get_span(t6, "Medical thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t6, "pleural effusion", 1)},
    {"label": "LATERALITY", **get_span(t6, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "pleural space", 1)},
    {"label": "MEAS_VOL", **get_span(t6, "900cc", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "Parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "Catheter", 1)}
]
BATCH_DATA.append({"id": "940211_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 940211_syn_7
# ==========================================
t7 = """[Indication]
Pleural effusion, r/o malignancy.
[Anesthesia]
Moderate Sedation.
[Description]
Thoracoscopy R chest. Parietal pleura biopsies x10. Fluid drained. No drain left.
[Plan]
Admit. Path pending."""

e7 = [
    {"label": "OBS_LESION", **get_span(t7, "Pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(t7, "Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(t7, "R", 1)},
    {"label": "ANAT_PLEURA", **get_span(t7, "Parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(t7, "10", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "drain", 1)}
]
BATCH_DATA.append({"id": "940211_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 940211_syn_8
# ==========================================
t8 = """Dr. Rahman performed a thoracoscopy on [REDACTED]. We made a small cut in her side and put a camera into the chest cavity. We drained the fluid and saw many small lumps on the lining of the chest wall. We took samples of these lumps to test for cancer. We didn't need to leave a tube in."""

e8 = [
    {"label": "PROC_METHOD", **get_span(t8, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lumps", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "chest wall", 1)},
    {"label": "OBS_LESION", **get_span(t8, "lumps", 2)},
    {"label": "DEV_CATHETER", **get_span(t8, "tube", 1)}
]
BATCH_DATA.append({"id": "940211_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 940211_syn_9
# ==========================================
t9 = """Procedure: Diagnostic pleuroscopy with tissue sampling.
Findings: Diffuse pleural nodularity.
Action: Evacuation of effusion and biopsy of parietal pleura.
Disposition: Hospital admission."""

e9 = [
    {"label": "PROC_METHOD", **get_span(t9, "pleuroscopy", 1)},
    {"label": "OBS_LESION", **get_span(t9, "pleural nodularity", 1)},
    {"label": "OBS_LESION", **get_span(t9, "effusion", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "parietal pleura", 1)}
]
BATCH_DATA.append({"id": "940211_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 940211
# ==========================================
t10 = """MEDICAL THORACOSCOPY WITH PLEURAL BIOPSY
Date: [REDACTED]
Patient: [REDACTED] | 69F | MRN [REDACTED]
Location: [REDACTED]
Attending: Dr. Omar Rahman

PREOPERATIVE DIAGNOSIS: Unexplained exudative right pleural effusion with pleural nodularity on CT
POSTOPERATIVE DIAGNOSIS: Same (pathology pending)

PROCEDURE: Medical thoracoscopy with pleural biopsy (CPT 32604)

ANESTHESIA: Moderate sedation with midazolam and fentanyl; local anesthesia to chest wall. Patient breathing spontaneously with supplemental oxygen via nasal cannula.

TECHNIQUE:
Ultrasound confirmed a large free-flowing right pleural effusion. A 1-cm incision was made in the right mid-axillary line at the 6th intercostal space. A trocar and thoracoscope were introduced into the pleural space.

Approximately 900 mL of straw-colored fluid was evacuated. The parietal pleura demonstrated diffuse studding with small nodules over the diaphragmatic and posterolateral pleura. Ten large forceps biopsies were taken from abnormal areas and sent for histology and culture.

No talc pleurodesis was performed and no chest tube was left in place; a single 16 Fr pigtail catheter was used for drainage during the case and removed at the end after confirming lung expansion.

COMPLICATIONS: None.
DISPOSITION: Observed in PACU then admitted overnight for monitoring."""

e10 = [
    {"label": "PROC_METHOD", **get_span(t10, "MEDICAL THORACOSCOPY", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "PLEURAL", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "BIOPSY", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "OBS_LESION", **get_span(t10, "pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(t10, "pleural nodularity", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "Medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural", 3)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "chest wall", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 2)},
    {"label": "OBS_LESION", **get_span(t10, "pleural effusion", 2)},
    {"label": "LATERALITY", **get_span(t10, "right", 3)},
    {"label": "ANAT_PLEURA", **get_span(t10, "6th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "trocar", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "thoracoscope", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural space", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "900 mL", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(t10, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "posterolateral pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(t10, "Ten", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "talc pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t10, "16 Fr pigtail catheter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "None", 1)}
]
BATCH_DATA.append({"id": "940211", "text": t10, "entities": e10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)