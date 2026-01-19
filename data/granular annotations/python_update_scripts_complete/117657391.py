import sys
from pathlib import Path

# Set up the repository root (assumes this script is in a subdirectory like 'scripts/')
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
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
            break
    
    if start == -1:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 117657391_syn_1
# ==========================================
id_1 = "117657391_syn_1"
text_1 = """Indication: Malignant effusion.
Procedure: Medical Thoracoscopy (Left).
Findings: Carcinomatosis, adhesions.
Action: Adhesiolysis. 800cc fluid drained. 5 biopsies parietal pleura.
Closure: 14Fr Pigtail placed.
Plan: Await path."""
entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "effusion", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Medical Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Carcinomatosis", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "adhesions", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Adhesiolysis", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "800cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "drained", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "5", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal pleura", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Pigtail", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placed", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 117657391_syn_2
# ==========================================
id_2 = "117657391_syn_2"
text_2 = """PROCEDURE: Left Medical Thoracoscopy (Pleuroscopy). The pleural space was accessed via the 8th intercostal space. Inspection revealed diffuse carcinomatosis and dense adhesions. Approximately 1275cc of serosanguinous fluid was evacuated. Forceps biopsies were obtained from the parietal pleura. A 14Fr chest tube was placed under direct vision. 
IMPRESSION: Malignant pleural effusion with extensive metastatic deposits."""
entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "8th intercostal space", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "carcinomatosis", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "adhesions", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "1275cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "evacuated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal pleura", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "effusion", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 117657391_syn_3
# ==========================================
id_3 = "117657391_syn_3"
text_3 = """Code: 32609 (Thoracoscopy with biopsy of pleura).
Details: Rigid pleuroscopy performed. Trocar entry. Visualization of pleural cavity. Biopsy of parietal pleura nodules (x5). Drainage of effusion. Placement of indwelling chest catheter."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleura", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleuroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Trocar", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleural cavity", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodules", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "x5", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Drainage", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "effusion", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "indwelling chest catheter", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 117657391_syn_4
# ==========================================
id_4 = "117657391_syn_4"
text_4 = """Resident Note
Patient: [REDACTED]
Procedure: Pleuroscopy
Steps:
1. Local/Sedation.
2. Trocar in left 8th rib space.
3. Drained fluid.
4. Saw nodules -> Biopsied x5.
5. Put in Pigtail catheter.
Complications: None.
Path: Sent fluid and tissue."""
entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "Pleuroscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Trocar", 1)},
    {"label": "LATERALITY", **get_span(text_4, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "8th rib space", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Drained", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "x5", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Pigtail catheter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "None", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 117657391_syn_5
# ==========================================
id_5 = "117657391_syn_5"
text_5 = """Doing a thoracoscopy on [REDACTED] effusion. Put the port in the left side drained a liter of bloody fluid. The lung looked stuck down and there were bumps everywhere. Took 5 biopsies of the bumps. Put a pigtail chest tube in at the end. Biopsies went to pathology."""
entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_5, "left side", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "a liter", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lung", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "stuck down", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "bumps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "5", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "bumps", 2)},
    {"label": "DEV_CATHETER", **get_span(text_5, "pigtail chest tube", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "Biopsies", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 117657391_syn_6
# ==========================================
id_6 = "117657391_syn_6"
text_6 = """Medical Thoracoscopy (Pleuroscopy), left side. Indication: Malignant pleural effusion. 1275cc fluid removed. Diffuse carcinomatosis noted. Multiple biopsies of parietal pleura performed. 14Fr Wayne pigtail catheter placed. Lung re-expansion confirmed on post-procedure CXR."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Pleuroscopy", 1)},
    {"label": "LATERALITY", **get_span(text_6, "left side", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "effusion", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "1275cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "removed", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "carcinomatosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal pleura", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "14Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "Wayne pigtail catheter", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_6, "Lung re-expansion", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 117657391_syn_7
# ==========================================
id_7 = "117657391_syn_7"
text_7 = """[Indication]
Malignant pleural effusion.
[Anesthesia]
Moderate Sedation + Local.
[Description]
Left thoracoscopy. 1275cc drained. Diffuse mets seen. Biopsies taken. Pigtail placed.
[Plan]
Pathology pending. Suture removal 2 weeks."""
entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_7, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "thoracoscopy", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "1275cc", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "drained", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "mets", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsies", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Pigtail", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 117657391_syn_8
# ==========================================
id_8 = "117657391_syn_8"
text_8 = """We performed a procedure to look inside [REDACTED]. We drained the fluid and saw extensive signs of cancer on the lining of the lung. We took several biopsy samples for the lab. We left a small chest tube in place to keep the fluid from building up again."""
entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "drained", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "signs of cancer", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "lining of the lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 117657391_syn_9
# ==========================================
id_9 = "117657391_syn_9"
text_9 = """Procedure: Medical Thoracoscopy with pleural sampling.
Findings: Effusion and carcinomatosis.
Action: Fluid was evacuated. Pleural nodules were sampled. A drainage catheter was inserted.
Result: Samples submitted for analysis."""
entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Medical Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "pleural sampling", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "Effusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "carcinomatosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "evacuated", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "Pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampled", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "drainage catheter", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)