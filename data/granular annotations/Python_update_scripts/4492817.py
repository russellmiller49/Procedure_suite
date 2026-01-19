import sys
from pathlib import Path

# Set up the repository root path
# This assumes the script is running within the structured environment
# containing the 'scripts' package.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add REPO_ROOT to sys.path to ensure imports work
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
    return start, start + len(term)

# ==========================================
# Note 1: 4492817_syn_1
# ==========================================
text_1 = """Dx: Recurrent malignant R effusion.
Action: Chemical Pleurodesis (32560).
- Chest tube confirmed functional.
- 4g Talc slurry instilled.
- Dwell time: 1 hr with rotation.
- Tube to suction.
Outcome: Tolerated well w/ morphine."""

entities_1 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "effusion", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_1, "R", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "Pleurodesis", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_1, "Chest tube", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_1, "Talc", 1)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_1, "1 hr", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_1, "Tube", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_1, "morphine", 1)))}
]
BATCH_DATA.append({"id": "4492817_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4492817_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: Instillation of Sclerosing Agent.
INDICATION: [REDACTED], a 76-year-old female with metastatic breast carcinoma, required palliation for a recurrent right malignant pleural effusion.
PROCEDURE: The existing right-sided 14Fr chest tube was utilized. A slurry comprising 4 grams of sterile talc suspended in 50mL of normal saline was prepared. This suspension was instilled into the pleural cavity. The tubing was clamped for sixty minutes, during which the patient was rotated to facilitate widespread pleural contact. Subsequently, the tube was unclamped and placed on -20cmH2O suction to appose the pleural surfaces."""

entities_2 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "Instillation", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "carcinoma", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_2, "right", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(text_2, "pleural", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "effusion", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_2, "right-sided", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_2, "14Fr chest tube", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_2, "talc", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_2, "50mL", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(text_2, "pleural cavity", 1)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_2, "sixty minutes", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_2, "tube", 2)))},
    {"label": "MEAS_PRESS", **dict(zip(["start", "end"], get_span(text_2, "-20cmH2O", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(text_2, "pleural", 3)))}
]
BATCH_DATA.append({"id": "4492817_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4492817_syn_3
# ==========================================
text_3 = """Code: 32560 (Instillation of agent for pleurodesis).
Agent: Talc (4g).
Method: Slurry via existing chest tube.
Location: Right pleural space.
Requirements met: Instillation of sclerosing agent for therapeutic pleurodesis of malignant effusion."""

entities_3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Instillation", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "pleurodesis", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_3, "Talc", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_3, "chest tube", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_3, "Right", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(text_3, "pleural space", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Instillation", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "pleurodesis", 2)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_3, "effusion", 1)))}
]
BATCH_DATA.append({"id": "4492817_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4492817_syn_4
# ==========================================
text_4 = """Procedure: Talc Pleurodesis
Patient: [REDACTED]
Steps:
1. Checked chest tube output (<100ml).
2. Mixed 4g talc in saline.
3. Pushed slurry into tube.
4. Clamped tube.
5. Rotated patient q15 mins.
6. Unclamped after 1 hour.
Pain managed with morphine."""

entities_4 = [
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_4, "Talc", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Pleurodesis", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_4, "chest tube", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_4, "100ml", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_4, "talc", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_4, "tube", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_4, "tube", 2)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_4, "1 hour", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_4, "morphine", 1)))}
]
BATCH_DATA.append({"id": "4492817_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4492817_syn_5
# ==========================================
text_5 = """doing pleurodesis on [REDACTED] breast cancer effusion. tube drain looks good so we put the talc in today. 4 grams mixed with saline. shot it in the tube and clamped it. moved her around for an hour then put it back on suction. she had some chest pain gave morphine. hope it sticks."""

entities_5 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_5, "pleurodesis", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "cancer", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "effusion", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_5, "tube drain", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_5, "talc", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_5, "tube", 2)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_5, "an hour", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_5, "morphine", 1)))}
]
BATCH_DATA.append({"id": "4492817_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4492817_syn_6
# ==========================================
text_6 = """Instillation of talc slurry via chest tube for pleurodesis performed on Dorothy Adams. Indication was recurrent right malignant pleural effusion. 4 grams of talc were mixed in 50mL saline and instilled through the existing chest tube. The tube was clamped for 1 hour with patient rotation. The patient received morphine for chest pain. The tube was returned to suction to facilitate pleurodesis."""

entities_6 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "Instillation", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_6, "talc", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_6, "chest tube", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "pleurodesis", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_6, "right", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(text_6, "pleural", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "effusion", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_6, "talc", 2)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_6, "50mL", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_6, "chest tube", 2)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_6, "tube", 3)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_6, "1 hour", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_6, "morphine", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_6, "tube", 4)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "pleurodesis", 2)))}
]
BATCH_DATA.append({"id": "4492817_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4492817_syn_7
# ==========================================
text_7 = """[Indication]
Recurrent Right Malignant Pleural Effusion (Breast CA).
[Anesthesia]
Local/IV Morphine for pain.
[Description]
4g Talc slurry instilled via 14Fr chest tube. Clamped 1 hour with rotation. Returned to suction.
[Plan]
Monitor output. Pull tube when <150mL/day."""

entities_7 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_7, "Right", 1)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(text_7, "Pleural", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "Effusion", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "CA", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_7, "Morphine", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_7, "Talc", 1)))},
    {"label": "DEV_CATHETER_SIZE", **dict(zip(["start", "end"], get_span(text_7, "14Fr chest tube", 1)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_7, "1 hour", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_7, "tube", 2)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_7, "150mL", 1)))}
]
BATCH_DATA.append({"id": "4492817_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4492817_syn_8
# ==========================================
text_8 = """[REDACTED] coming back around her right lung because of her cancer. We decided to 'glue' the lung to the chest wall to stop the fluid. We used her existing chest tube to put a mixture of talc and water inside. We clamped the tube and had her roll around in bed for an hour to coat the inside of her chest. Afterward, we put the tube back on suction. She had some pain but we treated it with medication."""

entities_8 = [
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_8, "right", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_8, "lung", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "cancer", 1)))},
    {"label": "ANAT_LUNG_LOC", **dict(zip(["start", "end"], get_span(text_8, "lung", 2)))},
    {"label": "ANAT_PLEURA", **dict(zip(["start", "end"], get_span(text_8, "chest wall", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_8, "chest tube", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_8, "talc", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_8, "tube", 1)))},
    {"label": "MEAS_TIME", **dict(zip(["start", "end"], get_span(text_8, "an hour", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_8, "tube", 2)))}
]
BATCH_DATA.append({"id": "4492817_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4492817_syn_9
# ==========================================
text_9 = """Procedure: Introduction of sclerosing agent.
Context: Recurrent right thoracic effusion.
Action: Talc suspension (4g) was infused via the indwelling thoracostomy tube. Following a dwell period with repositioning, negative pressure was re-applied to promote symphysis."""

entities_9 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "Introduction of sclerosing agent", 1)))},
    {"label": "LATERALITY", **dict(zip(["start", "end"], get_span(text_9, "right", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "effusion", 1)))},
    {"label": "MEDICATION", **dict(zip(["start", "end"], get_span(text_9, "Talc", 1)))},
    {"label": "DEV_CATHETER", **dict(zip(["start", "end"], get_span(text_9, "thoracostomy tube", 1)))}
]
BATCH_DATA.append({"id": "4492817_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)