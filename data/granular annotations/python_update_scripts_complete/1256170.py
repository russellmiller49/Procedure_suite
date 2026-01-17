import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    """
    start_index = -1
    for _ in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start_index,
        "end": start_index + len(term)
    }

# ==========================================
# Note 1: 1256170_syn_1
# ==========================================
text_1 = """Procedure: Medical Thoracoscopy (Right).
- Findings: Parietal/visceral nodules, trapped lung.
- Action: Biopsy x8, Adhesiolysis, Talc poudrage (4g).
- Drain: 28Fr chest tube placed.
- Plan: Admit, suction -20."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Medical Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_1, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "Parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "visceral", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_1, "trapped lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsy", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x8", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Adhesiolysis", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "poudrage", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
    {"label": "MEAS_PRESS", **get_span(text_1, "-20", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1256170_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: The patient underwent right-sided medical thoracoscopy. Inspection of the pleural cavity revealed diffuse nodularity suggestive of malignancy and a trapped lung. Multiple biopsies were harvested from the parietal and visceral pleura. Given the findings, talc pleurodesis was performed via insufflation. A chest tube was placed for post-operative drainage."""

entities_2 = [
    {"label": "LATERALITY", **get_span(text_2, "right-sided", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural cavity", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodularity", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignancy", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_2, "trapped lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "visceral pleura", 1)},
    {"label": "MEDICATION", **get_span(text_2, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "pleurodesis", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "insufflation", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1256170_syn_3
# ==========================================
text_3 = """Billing Code: 32650 (Thoracoscopy with pleurodesis). Note: Biopsies (32602) are bundled/included in the primary procedure when performed. Indication: Undiagnosed effusion/suspected malignancy. Technique: Rigid thoracoscope, Talc insufflation."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "pleurodesis", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Biopsies", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "malignancy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Rigid thoracoscope", 1)},
    {"label": "MEDICATION", **get_span(text_3, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "insufflation", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1256170_syn_4
# ==========================================
text_4 = """Resident Note: Pleuroscopy
1. Local/Sedation.
2. Trocar in 5th ICS.
3. Drained fluid.
4. Saw nodules everywhere -> Biopsied.
5. Lung trapped -> Talc poudrage performed.
6. Chest tube in.
Plan: Admit."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "5th ICS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Drained", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_4, "Lung trapped", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "poudrage", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1256170_syn_5
# ==========================================
text_5 = """medical thoracoscopy on mr [REDACTED]. right side. drained the fluid. looked inside saw a bunch of nodules looks like cancer. took 8 biopsies. lung wouldnt come up all the way so we puffed in some talc for pleurodesis. put a chest tube in. sent him to the floor."""

entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "medical thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right side", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drained", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "cancer", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "8", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_5, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1256170_syn_6
# ==========================================
text_6 = """Medical thoracoscopy with pleural biopsies, talc pleurodesis, and chest tube placement was performed. The patient is a 66-year-old male with a large right pleural effusion. Rigid thoracoscopy revealed multiple nodules. Biopsies were taken. Talc slurry was insufflated. A 28Fr chest tube was inserted. The patient was transferred to the floor."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_6, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
    {"label": "LATERALITY", **get_span(text_6, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "pleural effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Rigid thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_6, "Talc slurry", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "insufflated", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_6, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 2)},
]
BATCH_DATA.append({"id": "1256170_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1256170_syn_7
# ==========================================
text_7 = """[Indication]
Right Pleural Effusion, suspected malignancy.
[Anesthesia]
MAC/Local.
[Description]
Thoracoscopy performed. Nodules biopsied (x8). Trapped lung noted. Talc pleurodesis performed. Chest tube placed.
[Plan]
Admit, suction."""

entities_7 = [
    {"label": "LATERALITY", **get_span(text_7, "Right", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Pleural Effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "Nodules", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsied", 1)},
    {"label": "MEAS_COUNT", **get_span(text_7, "x8", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_7, "Trapped lung", 1)},
    {"label": "MEDICATION", **get_span(text_7, "Talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "Chest tube", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1256170_syn_8
# ==========================================
text_8 = """[REDACTED] a medical thoracoscopy to investigate his right pleural effusion. After entering the chest, we found extensive nodules and a trapped lung. We took several biopsies for diagnosis and then performed a talc pleurodesis to prevent fluid recurrence. A chest tube was left in place to ensure drainage and facilitate lung re-expansion if possible."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "pleural effusion", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodules", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_8, "trapped lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_8, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1256170_syn_9
# ==========================================
text_9 = """Operation: Pleuroscopy with tissue sampling and chemical sclerosis.
Findings: Diffuse pleural modularity, non-expandable lung.
Intervention: Multiple biopsies. Insufflation of talc agent.
Hardware: Indwelling thoracic catheter (chest tube) placed."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Pleuroscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "pleural", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "modularity", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_9, "non-expandable lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Insufflation", 1)},
    {"label": "MEDICATION", **get_span(text_9, "talc agent", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Indwelling thoracic catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "chest tube", 1)},
]
BATCH_DATA.append({"id": "1256170_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1256170
# ==========================================
text_10 = """Patient: [REDACTED] | Age: 66 | Sex: M | MRN: [REDACTED]
Date: [REDACTED]
Attending: Dr. Nicole Turner
Clinical Summary: Patient is a 66 year old gentleman presenting with a large right sided pleural effusion, unclear etiology. Previous thoracentesis showed exudative fluid with negative cytology. CT shows pleural thickening concerning for malignancy versus infectious process.
We discussed the need for tissue diagnosis via medical thoracoscopy. Risks including bleeding, infection, pneumothorax, need for chest tube, and rare complications such as empyema or need for surgical intervention were explained. The patient understood and signed consent.
Procedure Performed: Medical thoracoscopy with pleural biopsies, talc pleurodesis, chest tube placement
How it went: Patient was positioned in left lateral decubitus. Right hemithorax prepped and draped. Ultrasound used to mark the 5th intercostal space at mid-axillary line - this showed large effusion with no loculations. After infiltrating with 20cc of 1% lidocaine, we made a 2cm incision and used blunt dissection to enter the pleural space. Initial gush of fluid noted. A 28Fr chest tube was inserted and connected to suction, draining approximately 800mL of bloody fluid initially.
Through the same incision site, we introduced the rigid thoracoscope. The pleural space was systematically examined. Findings were significant: The parietal pleura showed multiple white nodular lesions, largest about 1.5cm, scattered throughout. The visceral pleura had similar appearing nodules with some areas of thickened pleura. Lung appeared trapped with inability to fully expand. There were some loose adhesions which were lysed using blunt technique.
Multiple biopsies were taken from both parietal and visceral pleura using biopsy forceps - total of 8 samples obtained from various sites. Each biopsy site had minimal bleeding controlled with pressure.
After biopsies were complete, we decided to proceed with talc pleurodesis given the likely malignant etiology and trapped lung. Approximately 4 grams of sterile talc slurry mixed in 50mL normal saline was insufflated throughout the pleural cavity ensuring good distribution. The chest tube was left in place and secured with 0-silk suture. Dressing applied.
Pathology sent: Pleural biopsies x8 in formalin, pleural fluid for cytology and chemistry
Patient [REDACTED] throughout. No complications. Transferred to floor with chest tube to suction at -20cmH2O. Post procedure CXR pending.
Follow up plan: Monitor drainage. Chest tube likely to stay for several days given trapped lung. Await pathology. If malignancy confirmed, will need oncology consultation. Patient understands may need indwelling pleural catheter if lung doesn't re-expand."""

entities_10 = [
    {"label": "LATERALITY", **get_span(text_10, "right sided", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural effusion", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_10, "Previous", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "thoracentesis", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "exudative fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "pleural thickening", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "malignancy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "medical thoracoscopy", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "MEDICATION", **get_span(text_10, "talc", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 2)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "hemithorax", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "5th intercostal space", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "effusion", 2)},
    {"label": "MEDICATION", **get_span(text_10, "lidocaine", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural space", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_10, "28Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 3)},
    {"label": "MEAS_VOL", **get_span(text_10, "800mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "bloody fluid", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid thoracoscope", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural space", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodular lesions", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "1.5cm", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "visceral pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodules", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "thickened pleura", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "Lung appeared trapped", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "adhesions", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "lysed", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "visceral pleura", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "biopsy forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "8", 1)},
    {"label": "MEDICATION", **get_span(text_10, "talc", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "pleurodesis", 2)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "trapped lung", 1)},
    {"label": "MEDICATION", **get_span(text_10, "sterile talc slurry", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "50mL", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "insufflated", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural cavity", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 4)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 3)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x8", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "pleural fluid", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "No complications", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 5)},
    {"label": "MEAS_PRESS", **get_span(text_10, "-20cmH2O", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "Chest tube", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_10, "trapped lung", 2)},
    {"label": "DEV_CATHETER", **get_span(text_10, "indwelling pleural catheter", 1)},
]
BATCH_DATA.append({"id": "1256170", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)