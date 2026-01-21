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
# 2. Helper Function
# ==========================================
def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

# ==========================================
# 3. Data Payload
# ==========================================
BATCH_DATA = []

# ------------------------------------------
# Case: 3060386
# ------------------------------------------
id_1 = "3060386"
text_1 = """OPERATIVE REPORT - INTERVENTIONAL PULMONOLOGY
Date: [REDACTED]
Patient: [REDACTED] | MRN: [REDACTED] | DOB: [REDACTED]

Attending: Dr. James Walker, MD
Location: [REDACTED]

PREOP DX: Recurrent tracheomalacia with carinal involvement, s/p prior metallic stent placement with stent-in-stent failure

POSTOP DX: Same

PROCEDURE: 
1. Rigid bronchoscopy
2. Removal of prior SEMS
3. Silicone Y-stent (Dumon) placement

ANESTHESIA: General, jet ventilation

PROCEDURE: Under GA with rigid bronchoscopy (14mm Dumon), the previously placed covered SEMS was removed using rigid forceps with en bloc extraction. Tracheomalacia confirmed with >75% collapse on expiration involving distal trachea and proximal mainstems bilaterally.

A Novatech silicone Y-stent (18mm trachea, 14mm bilateral limbs, 50mm body length) was loaded on the deployment rod. Under direct visualization, the Y-stent was advanced and deployed with the carinal spur appropriately positioned. Both mainstem limbs expanded well. Post-deployment bronchoscopy confirmed patent airways bilaterally, good stent positioning, no mucus impaction.

COMPLICATIONS: None
EBL: 10mL
DISPOSITION: PACU, discharge same day

Dr. James Walker, MD"""

entities_1 = [
    # Diagnosis / History
    {"label": "OBS_LESION",          **get_span(text_1, "Recurrent tracheomalacia", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "carinal", 1)},
    {"label": "CTX_HISTORICAL",      **get_span(text_1, "prior", 1)},
    {"label": "DEV_STENT_MATERIAL",  **get_span(text_1, "metallic", 1)},
    {"label": "DEV_STENT",           **get_span(text_1, "stent", 1)},
    {"label": "DEV_STENT",           **get_span(text_1, "stent-in-stent", 1)},
    
    # Procedure Header
    {"label": "PROC_METHOD",         **get_span(text_1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "Removal", 1)},
    {"label": "CTX_HISTORICAL",      **get_span(text_1, "prior", 2)},
    {"label": "DEV_STENT",           **get_span(text_1, "SEMS", 1)},
    {"label": "DEV_STENT_MATERIAL",  **get_span(text_1, "Silicone", 1)},
    {"label": "DEV_STENT",           **get_span(text_1, "Y-stent", 1)},
    {"label": "DEV_STENT_MATERIAL",  **get_span(text_1, "Dumon", 1)}, # Dumon silicone stent
    {"label": "PROC_ACTION",         **get_span(text_1, "placement", 1)},
    
    # Anesthesia
    {"label": "PROC_METHOD",         **get_span(text_1, "jet ventilation", 1)},

    # Procedure Body
    {"label": "PROC_METHOD",         **get_span(text_1, "rigid bronchoscopy", 1)},
    {"label": "MEAS_SIZE",           **get_span(text_1, "14mm", 1)},
    {"label": "DEV_INSTRUMENT",      **get_span(text_1, "Dumon", 2)}, # Refers to the scope here
    {"label": "CTX_HISTORICAL",      **get_span(text_1, "previously", 1)},
    {"label": "DEV_STENT_MATERIAL",  **get_span(text_1, "covered", 1)},
    {"label": "DEV_STENT",           **get_span(text_1, "SEMS", 2)},
    {"label": "PROC_ACTION",         **get_span(text_1, "removed", 1)},
    {"label": "DEV_INSTRUMENT",      **get_span(text_1, "rigid forceps", 1)},
    {"label": "PROC_METHOD",         **get_span(text_1, "en bloc", 1)},
    
    # Findings
    # FIX: Changed occurrence from 2 to 1. The first instance in the document is lowercase ("tracheomalacia").
    # The term requested here is capitalized ("Tracheomalacia"), so this matches the FIRST capitalized instance.
    {"label": "OBS_LESION",          **get_span(text_1, "Tracheomalacia", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, ">75% collapse", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "trachea", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "mainstems", 1)},
    {"label": "LATERALITY",          **get_span(text_1, "bilaterally", 1)},
    
    # Intervention
    {"label": "DEV_STENT_MATERIAL",  **get_span(text_1, "Novatech", 1)},
    {"label": "DEV_STENT_MATERIAL",  **get_span(text_1, "silicone", 1)},
    {"label": "DEV_STENT",           **get_span(text_1, "Y-stent", 2)},
    {"label": "DEV_STENT_SIZE",      **get_span(text_1, "18mm", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "trachea", 2)},
    {"label": "DEV_STENT_SIZE",      **get_span(text_1, "14mm", 2)},
    {"label": "LATERALITY",          **get_span(text_1, "bilateral", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "limbs", 1)},
    {"label": "DEV_STENT_SIZE",      **get_span(text_1, "50mm", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "loaded", 1)},
    {"label": "DEV_INSTRUMENT",      **get_span(text_1, "deployment rod", 1)},
    
    # Deployment
    {"label": "PROC_METHOD",         **get_span(text_1, "direct visualization", 1)},
    {"label": "DEV_STENT",           **get_span(text_1, "Y-stent", 3)},
    {"label": "PROC_ACTION",         **get_span(text_1, "advanced", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "deployed", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "carinal spur", 1)},
    {"label": "PROC_ACTION",         **get_span(text_1, "positioned", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "mainstem", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "limbs", 2)},
    {"label": "OBS_FINDING",         **get_span(text_1, "expanded", 1)},
    
    # Outcome
    {"label": "PROC_METHOD",         **get_span(text_1, "Post-deployment bronchoscopy", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "patent", 1)},
    {"label": "ANAT_AIRWAY",         **get_span(text_1, "airways", 1)},
    {"label": "LATERALITY",          **get_span(text_1, "bilaterally", 2)},
    {"label": "OBS_FINDING",         **get_span(text_1, "mucus impaction", 1)},
    
    # Complications / EBL
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)},
    {"label": "MEAS_VOL",            **get_span(text_1, "10mL", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


# ==========================================
# 4. Execution Loop
# ==========================================
if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)