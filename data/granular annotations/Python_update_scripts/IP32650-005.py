import sys
from pathlib import Path

# Set up the repository root (assumes this script is running two levels deep)
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the 'entities' list.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    end_index = start_index + len(term)
    return {"start": start_index, "end": end_index}

# ==========================================
# Note 1: IP32650-005_syn_1
# ==========================================
t1 = """Indication: Recurrent Left Spontaneous Pneumothorax.
Proc: Med Thoracoscopy + Talc Poudrage.
Findings: Apical blebs (stapled by Thoracic Surgery). 150ml fluid.
Action: Mechanical abrasion (apical/parietal) + 4g Talc insufflation (poudrage).
Plan: Chest tube to suction. Stop smoking."""

e1 = [
    {"label": "LATERALITY", **get_span(t1, "Left", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Pneumothorax", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Thoracoscopy", 1)},
    {"label": "MEDICATION", **get_span(t1, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Poudrage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "Apical", 1)},
    {"label": "OBS_LESION", **get_span(t1, "blebs", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "stapled", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "150ml", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Mechanical abrasion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "apical", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "parietal", 1)},
    {"label": "MEDICATION", **get_span(t1, "Talc", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "insufflation", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: IP32650-005_syn_2
# ==========================================
t2 = """OPERATIVE REPORT: Left medical thoracoscopy with pleurodesis for recurrent primary spontaneous pneumothorax.
FINDINGS: Entry into the left pleural cavity revealed a small effusion and apical bleb disease. The blebs were resected via stapling (refer to Thoracic Surgery note). Following resection, the Medical Pulmonary team performed mechanical pleurodesis of the apical pleura. This was augmented by the insufflation of 4 grams of sterile talc powder (poudrage) to ensure diffuse pleural symphysis.
OUTCOME: 24-French chest tube placed. Patient extubated and stable."""

e2 = [
    {"label": "LATERALITY", **get_span(t2, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "medical thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "pleurodesis", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "pneumothorax", 1)},
    {"label": "LATERALITY", **get_span(t2, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "pleural cavity", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "effusion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "apical", 1)},
    {"label": "OBS_LESION", **get_span(t2, "bleb", 1)},
    {"label": "OBS_LESION", **get_span(t2, "blebs", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "resected", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "stapling", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "mechanical pleurodesis", 1)},
    {"label": "ANAT_PLEURA", **get_span(t2, "apical pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "insufflation", 1)},
    {"label": "MEDICATION", **get_span(t2, "talc powder", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "poudrage", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t2, "24-French", 1)},
    {"label": "DEV_CATHETER", **get_span(t2, "chest tube", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: IP32650-005_syn_3
# ==========================================
t3 = """Code: 32650 (Thoracoscopy w/ pleurodesis).
Note: Stapling reported separately by surgery.
Technique:
- Lung isolation (DLT).
- Id[REDACTED] of apical pathology.
- Mechanical abrasion performed.
- Talc Poudrage (Insufflation of dry powder) used instead of slurry.
Medical Necessity: Recurrent pneumothorax (3rd episode)."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Stapling", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "DLT", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "apical", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Mechanical abrasion", 1)},
    {"label": "MEDICATION", **get_span(t3, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "Insufflation", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "pneumothorax", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: IP32650-005_syn_4
# ==========================================
t4 = """Procedure: Left Thoracoscopy for Pneumo
Patient: [REDACTED], 27M

1. GA, DLT.
2. Surgery stapled blebs first.
3. We did the pleurodesis.
4. Scratched the pleura (abrasion).
5. Puffed in 4g Talc powder.
6. Chest tube placed.

Events: Desat to 88% during single lung vent, fixed with recruitment."""

e4 = [
    {"label": "LATERALITY", **get_span(t4, "Left", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Thoracoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Pneumo", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t4, "DLT", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "stapled", 1)},
    {"label": "OBS_LESION", **get_span(t4, "blebs", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Scratched", 1)},
    {"label": "ANAT_PLEURA", **get_span(t4, "pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "abrasion", 1)},
    {"label": "MEDICATION", **get_span(t4, "Talc powder", 1)},
    {"label": "DEV_CATHETER", **get_span(t4, "Chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "Desat", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "recruitment", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: IP32650-005_syn_5
# ==========================================
t5 = """Liam is the young guy with the collapsed lung again. We went in with the surgeons. They stapled the blebs. We did the pleurodesis part. Rubbed the apex with gauze and blew in the talc powder 4 grams. He desatted a bit when we dropped the lung but came back up. Tube is in. Tell him to stop smoking seriously."""

e5 = [
    {"label": "OBS_FINDING", **get_span(t5, "collapsed lung", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "stapled", 1)},
    {"label": "OBS_LESION", **get_span(t5, "blebs", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(t5, "Rubbed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t5, "apex", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "gauze", 1)},
    {"label": "MEDICATION", **get_span(t5, "talc powder", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "desatted", 1)},
    {"label": "DEV_CATHETER", **get_span(t5, "Tube", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: IP32650-005_syn_6
# ==========================================
t6 = """Medical thoracoscopy with talc pleurodesis for recurrent spontaneous pneumothorax. Patient is a 27-year-old male. The patient was positioned in right lateral decubitus. Entry into the left pleural space at the 5th intercostal space yielded a small amount of serosanguinous fluid and air. Thoracoscopic inspection revealed several apical blebs. The apical blebs were stapled by the thoracic surgery team. Medical thoracoscopy team performed mechanical pleurodesis along the apical and parietal pleura using gauze pads, followed by insufflation of 4 g sterile talc as dry powder. A 24 Fr chest tube was left at the apex."""

e6 = [
    {"label": "PROC_ACTION", **get_span(t6, "Medical thoracoscopy", 1)},
    {"label": "MEDICATION", **get_span(t6, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "pleurodesis", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "pneumothorax", 1)},
    {"label": "LATERALITY", **get_span(t6, "right", 1)},
    {"label": "LATERALITY", **get_span(t6, "left", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t6, "5th intercostal space", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "fluid", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "air", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "apical", 1)},
    {"label": "OBS_LESION", **get_span(t6, "blebs", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "apical", 2)},
    {"label": "OBS_LESION", **get_span(t6, "blebs", 2)},
    {"label": "PROC_ACTION", **get_span(t6, "stapled", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "mechanical pleurodesis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "apical", 3)},
    {"label": "ANAT_PLEURA", **get_span(t6, "parietal pleura", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t6, "gauze pads", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "insufflation", 1)},
    {"label": "MEDICATION", **get_span(t6, "talc", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t6, "24 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t6, "chest tube", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "apex", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: IP32650-005_syn_7
# ==========================================
t7 = """[Indication]
Recurrent left spontaneous pneumothorax.
[Anesthesia]
General, DLT.
[Description]
Blebs stapled by surgery. Mechanical abrasion performed. 4g Talc poudrage insufflated.
[Plan]
Daily CXR. Tube removal when air leak resolves. Smoking cessation."""

e7 = [
    {"label": "LATERALITY", **get_span(t7, "left", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "pneumothorax", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t7, "DLT", 1)},
    {"label": "OBS_LESION", **get_span(t7, "Blebs", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "stapled", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Mechanical abrasion", 1)},
    {"label": "MEDICATION", **get_span(t7, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "poudrage", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "insufflated", 1)},
    {"label": "DEV_CATHETER", **get_span(t7, "Tube", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "air leak", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: IP32650-005_syn_8
# ==========================================
t8 = """Liam came in for his third collapsed lung. We worked with the surgery team; they stapled off the weak spots (blebs) on his lung. Then, we performed the pleurodesis to stick the lung to the chest wall. We used a scratch pad on the lining and blew in dry talc powder. He had a brief drop in oxygen levels during the procedure but recovered quickly. He has a chest tube in now."""

e8 = [
    {"label": "OBS_FINDING", **get_span(t8, "collapsed lung", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "stapled", 1)},
    {"label": "OBS_LESION", **get_span(t8, "blebs", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "pleurodesis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t8, "scratch pad", 1)},
    {"label": "ANAT_PLEURA", **get_span(t8, "lining", 1)},
    {"label": "MEDICATION", **get_span(t8, "talc powder", 1)},
    {"label": "OBS_FINDING", **get_span(t8, "drop in oxygen levels", 1)},
    {"label": "DEV_CATHETER", **get_span(t8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: IP32650-005_syn_9
# ==========================================
t9 = """Procedure: Medical thoracoscopy with talc poudrage.
Context: Recurrent primary spontaneous pneumothorax.
Intervention: Apical blebs were resected by surgery. The parietal pleura was abraded. 4 g of talc was insufflated as a dry powder.
Complication: Intraoperative desaturation resolved with recruitment maneuvers."""

e9 = [
    {"label": "PROC_ACTION", **get_span(t9, "Medical thoracoscopy", 1)},
    {"label": "MEDICATION", **get_span(t9, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "poudrage", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "pneumothorax", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t9, "Apical", 1)},
    {"label": "OBS_LESION", **get_span(t9, "blebs", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "resected", 1)},
    {"label": "ANAT_PLEURA", **get_span(t9, "parietal pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "abraded", 1)},
    {"label": "MEDICATION", **get_span(t9, "talc", 2)},
    {"label": "PROC_ACTION", **get_span(t9, "insufflated", 1)},
    {"label": "OBS_FINDING", **get_span(t9, "desaturation", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "recruitment maneuvers", 1)},
]
BATCH_DATA.append({"id": "IP32650-005_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: IP32650-005
# ==========================================
t10 = """Interventional Pulmonology Procedure Note
Procedure: Medical thoracoscopy with talc pleurodesis for recurrent spontaneous pneumothorax.
Patient: [REDACTED], 27-year-old male with recurrent primary left spontaneous pneumothorax.
Anesthesia: General anesthesia with left lung isolation using a double-lumen ETT.
Indication: Third episode of left spontaneous pneumothorax with persistent air leak after chest tube drainage.
Procedure details: The patient was positioned in right lateral decubitus. Entry into the left pleural space at the 5th intercostal space yielded a small amount of serosanguinous fluid and air. Thoracoscopic inspection revealed several apical blebs and normal visceral pleura elsewhere. The apical blebs were stapled with an endoscopic stapler by the thoracic surgery team (documented separately). Medical thoracoscopy team performed mechanical pleurodesis along the apical and parietal pleura using gauze pads, followed by insufflation of 4 g sterile talc as dry powder. A 24 Fr chest tube was left at the apex.
Complications: Brief intraoperative desaturation to 88% during lung isolation, resolved with recruitment maneuvers.
Estimated blood loss: 20 mL.
Disposition: Admitted to floor with chest tube to suction.
Plan: Daily CXRs; chest tube removal when no air leak and lung fully expanded on water seal; smoking cessation counseling."""

e10 = [
    {"label": "PROC_ACTION", **get_span(t10, "Medical thoracoscopy", 1)},
    {"label": "MEDICATION", **get_span(t10, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "pleurodesis", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "pneumothorax", 1)},
    {"label": "LATERALITY", **get_span(t10, "left", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "pneumothorax", 2)},
    {"label": "LATERALITY", **get_span(t10, "left", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "double-lumen ETT", 1)},
    {"label": "LATERALITY", **get_span(t10, "left", 3)},
    {"label": "OBS_FINDING", **get_span(t10, "pneumothorax", 3)},
    {"label": "OBS_FINDING", **get_span(t10, "air leak", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "LATERALITY", **get_span(t10, "left", 4)},
    {"label": "ANAT_PLEURA", **get_span(t10, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "5th intercostal space", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "fluid", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "air", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "apical", 1)},
    {"label": "OBS_LESION", **get_span(t10, "blebs", 1)},
    {"label": "ANAT_PLEURA", **get_span(t10, "visceral pleura", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "apical", 2)},
    {"label": "OBS_LESION", **get_span(t10, "blebs", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "stapled", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "endoscopic stapler", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "mechanical pleurodesis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "apical", 3)},
    {"label": "ANAT_PLEURA", **get_span(t10, "parietal pleura", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t10, "gauze pads", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "insufflation", 1)},
    {"label": "MEDICATION", **get_span(t10, "talc", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(t10, "24 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "apex", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "desaturation", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "recruitment maneuvers", 1)},
    {"label": "MEAS_VOL", **get_span(t10, "20 mL", 1)},
    {"label": "DEV_CATHETER", **get_span(t10, "chest tube", 3)},
]
BATCH_DATA.append({"id": "IP32650-005", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)