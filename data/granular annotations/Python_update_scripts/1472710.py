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
# 2. Data Definition
# ==========================================
BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# Case 1: 1472710
# ==========================================
id_1 = "1472710"
t1 = """OPERATIVE REPORT - INTERVENTIONAL PULMONOLOGY / THORACIC SURGERY

DATE: [REDACTED]
PATIENT: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (64 years old)

SURGEONS:
IP: Dr. Mark Anderson, MD (started case)
Thoracic Surgery: Dr. Sarah Kim, MD (completed case after conversion)

LOCATION: [REDACTED]

PREOPERATIVE DIAGNOSIS: Right-sided exudative pleural effusion, unknown etiology

POSTOPERATIVE DIAGNOSIS: Dense pleural adhesions with loculated effusion; trapped lung

PLANNED PROCEDURE: Medical thoracoscopy (pleuroscopy) with pleural biopsy and potential talc poudrage

ACTUAL PROCEDURES PERFORMED:
1. Attempted medical thoracoscopy (aborted)
2. Conversion to VATS (Video-Assisted Thoracoscopic Surgery)
3. VATS lysis of adhesions
4. VATS pleural biopsy
5. Decortication (partial)
6. Chest tube placement

INDICATION: 64-year-old female with 2-month history of progressive dyspnea. CT chest revealed large right pleural effusion with mild enhancement of pleura concerning for malignancy. Thoracentesis x 2 showed exudative effusion with negative cytology. Medical thoracoscopy planned for definitive diagnosis and potential pleurodesis.

ANESTHESIA: General anesthesia with double-lumen endotracheal tube (left-sided)

PROCEDURE NARRATIVE:

MEDICAL THORACOSCOPY ATTEMPT (Dr. Anderson):
Patient [REDACTED] left lateral decubitus. After induction of general anesthesia and lung isolation, the right chest was prepped and draped. Ultrasound examination revealed a small pocket of fluid in the mid-axillary line but significant lung adherence to chest wall throughout.

A 2cm incision was made in the 6th intercostal space. Upon blunt dissection into the pleural space, immediate dense adhesions were encountered. The 7mm trocar could not be safely advanced due to extensive lung-to-chest-wall adhesions. A small pocket of loculated fluid (~200mL) was drained but no window could be created for safe pleuroscopy. Multiple attempts at different intercostal spaces (5th, 7th) encountered similar dense adhesions.

DECISION TO CONVERT: After thorough discussion with thoracic surgery colleagues and the patient's family (who had been counseled preoperatively about this possibility), the decision was made to convert to VATS for safe completion of the procedure.

VATS PROCEDURE (Dr. Kim):
The incision was extended and a 10mm port placed under direct vision where a small pleural space was id[REDACTED]. Two additional 5mm ports were placed. Dense adhesions were found throughout the hemithorax. Using a combination of blunt dissection, electrocautery, and harmonic scalpel, extensive adhesiolysis was performed over approximately 90 minutes.

Findings:
- Dense fibrinous adhesions throughout
- Thickened visceral pleura with trapped lung
- Nodular thickening of parietal pleura (multiple biopsies taken)
- Approximately 500mL of loculated, amber-colored fluid drained

Multiple parietal pleural biopsies were obtained from chest wall and diaphragmatic pleura. Partial decortication of the visceral pleura was performed to allow lung expansion, though complete expansion could not be achieved due to chronic entrapment.

A 28Fr chest tube was placed. Negative-pressure water seal established. Lung expansion approximately 70% at end of case.

SPECIMENS:
- Pleural fluid: Cytology, cell count, chemistry, cultures, adenosine deaminase
- Pleural biopsies (multiple): Surgical pathology

ESTIMATED BLOOD LOSS: 150mL

COMPLICATIONS: None intraoperatively. Conversion was planned contingency.

DISPOSITION: Transferred to SICU for overnight monitoring. Chest tube to suction.

POST-OPERATIVE PLAN:
1. Monitor chest tube output
2. CXR in AM
3. Await pathology - concern for malignant mesothelioma or chronic fibrinous pleuritis
4. If lung remains trapped, may require chronic indwelling pleural catheter

Dr. Mark Anderson, MD - Interventional Pulmonology
Dr. Sarah Kim, MD - Thoracic Surgery"""

e1 = [
    # Diagnoses & Indications
    {"label": "LATERALITY", **get_span(t1, "Right-sided", 1)},
    {"label": "OBS_LESION", **get_span(t1, "pleural effusion", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Dense pleural adhesions", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "loculated effusion", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t1, "trapped lung", 1)},
    
    # Planned Procedures
    {"label": "PROC_ACTION", **get_span(t1, "Medical thoracoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "pleuroscopy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "pleural biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "talc poudrage", 1)},
    
    # Actual Procedures
    {"label": "PROC_ACTION", **get_span(t1, "medical thoracoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "VATS", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Video-Assisted Thoracoscopic Surgery", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "VATS", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "lysis of adhesions", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "VATS", 3)},
    {"label": "PROC_ACTION", **get_span(t1, "pleural biopsy", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "Decortication", 1)},
    {"label": "DEV_CATHETER", **get_span(t1, "Chest tube", 1)},
    
    # Indication Section
    {"label": "CTX_TIME", **get_span(t1, "2-month", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "CT chest", 1)},
    {"label": "LATERALITY", **get_span(t1, "right", 1)},
    {"label": "OBS_LESION", **get_span(t1, "pleural effusion", 2)},
    {"label": "ANAT_PLEURA", **get_span(t1, "pleura", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "Thoracentesis", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Medical thoracoscopy", 2)},
    {"label": "PROC_ACTION", **get_span(t1, "pleurodesis", 1)},
    
    # Anesthesia
    {"label": "DEV_INSTRUMENT", **get_span(t1, "double-lumen endotracheal tube", 1)},
    
    # Narrative
    {"label": "PROC_ACTION", **get_span(t1, "MEDICAL THORACOSCOPY", 1)},
    {"label": "LATERALITY", **get_span(t1, "left", 2)},
    {"label": "LATERALITY", **get_span(t1, "right", 2)},
    {"label": "ANAT_PLEURA", **get_span(t1, "chest", 3)},
    {"label": "PROC_METHOD", **get_span(t1, "Ultrasound", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "mid-axillary line", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "lung", 3)},
    {"label": "ANAT_PLEURA", **get_span(t1, "chest wall", 1)},
    
    {"label": "MEAS_SIZE", **get_span(t1, "2cm", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "6th intercostal space", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "blunt dissection", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "pleural space", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "dense adhesions", 1)},
    {"label": "MEAS_SIZE", **get_span(t1, "7mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "trocar", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "~200mL", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "pleuroscopy", 2)},
    {"label": "ANAT_PLEURA", **get_span(t1, "5th", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "7th", 1)},
    
    # Conversion
    {"label": "PROC_METHOD", **get_span(t1, "VATS", 4)},
    
    # VATS Procedure
    {"label": "PROC_METHOD", **get_span(t1, "VATS", 5)},
    {"label": "MEAS_SIZE", **get_span(t1, "10mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "port", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "pleural space", 2)},
    {"label": "MEAS_SIZE", **get_span(t1, "5mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "ports", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Dense adhesions", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "hemithorax", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "blunt dissection", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "electrocautery", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "harmonic scalpel", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "adhesiolysis", 1)},
    {"label": "CTX_TIME", **get_span(t1, "90 minutes", 1)},
    
    # Findings
    {"label": "OBS_FINDING", **get_span(t1, "Dense fibrinous adhesions", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Thickened", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "visceral pleura", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t1, "trapped lung", 2)},
    {"label": "OBS_FINDING", **get_span(t1, "Nodular thickening", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "parietal pleura", 1)},
    {"label": "MEAS_VOL", **get_span(t1, "500mL", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "amber-colored", 1)},
    
    # Additional Actions/Specimens
    {"label": "ANAT_PLEURA", **get_span(t1, "chest wall", 2)},
    {"label": "ANAT_PLEURA", **get_span(t1, "diaphragmatic pleura", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "decortication", 1)},
    {"label": "ANAT_PLEURA", **get_span(t1, "visceral pleura", 2)},
    
    {"label": "DEV_CATHETER_SIZE", **get_span(t1, "28Fr chest tube", 1)},
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(t1, "28Fr", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(t1, "Lung expansion approximately 70%", 1)},
    
    {"label": "SPECIMEN", **get_span(t1, "Pleural fluid", 1)},
    {"label": "SPECIMEN", **get_span(t1, "Pleural biopsies", 1)},
    
    # Plan
    # FIX: Changed "Chest tube" (occ 3) to lowercase "chest tube" (occ 2)
    # Context: "Monitor chest tube output"
    {"label": "DEV_CATHETER", **get_span(t1, "chest tube", 2)},
    {"label": "DEV_CATHETER", **get_span(t1, "pleural catheter", 1)},
]
BATCH_DATA.append({"id": id_1, "text": t1, "entities": e1})

# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)