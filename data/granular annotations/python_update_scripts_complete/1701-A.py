import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("CRITICAL ERROR: Could not import 'add_case'. Check REPO_ROOT path.")
    sys.exit(1)

def get_span(text, term, occurrence=1):
    start = -1
    for i in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
             raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    return {"text": term, "start": start, "end": start + len(term)}

BATCH_DATA = []

# Syn 6 was the failure point in your log
t6 = "Rigid bronchoscopy with laser tumor destruction and tracheal stent placement. Patient 60M. Malignant tracheal stenosis. Nd:YAG laser used for tumor ablation. Mechanical debulking performed. 16x40mm Dumon silicone stent deployed in mid-trachea. Airway patent. Hemostasis achieved. Complications none."

# Note: In your JSON provided earlier, 1701-A_syn_6 text was slightly different ("Bronchoscopic microwave ablation..."?). 
# I am using the text from the 1701-A.json you uploaded in THIS turn.
# Wait, looking at 1701-A.json content you just uploaded:
# "1701-A_syn_6": "Rigid bronchoscopy with laser tumor destruction... Nd:YAG laser used for tumor ablation... 16x40mm Dumon..."
# There is NO capital "Ablation" in this text. There is only "ablation" (lowercase).
# The previous script likely failed because it looked for "Ablation" (Cap) which doesn't exist.

e6 = [
    {"label": "PROC_ACTION",    **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",    **get_span(t6, "tumor destruction", 1)},
    {"label": "PROC_ACTION",    **get_span(t6, "tumor ablation", 1)}, # Lowercase match
    {"label": "DEV_INSTRUMENT", **get_span(t6, "Nd:YAG laser", 1)},
    {"label": "DEV_STENT",      **get_span(t6, "Dumon silicone stent", 1)},
    {"label": "ANAT_AIRWAY",    **get_span(t6, "mid-trachea", 1)}
]
BATCH_DATA.append({"id": "1701-A_syn_6", "text": t6, "entities": e6})

# Base Note
t_base = "**OPERATIVE REPORT**\n\n**PATIENT:** James T. Kirk\n**MRN:** 1701-A\n**DATE:** [REDACTED]\n**SURGEON:** Dr. Leonard McCoy\n**ANESTHESIA:** General (TIVA)\n\n**PRE-OP DIAGNOSIS:** Tracheal Stenosis (Malignant)\n**POST-OP DIAGNOSIS:** Same, Status Post Laser Resection and Stenting\n**PROCEDURE:** Rigid Bronchoscopy, Laser Tumor Destruction, Silicone Stent Placement\n\n**FINDINGS:**\n1.  Exophytic tumor obstructing 80% of mid-trachea.\n2.  Rest of airways patent.\n\n**DESCRIPTION:**\nPatient [REDACTED]. Rigid bronchoscope (14mm) inserted. Tumor visualized in mid-trachea. Nd:YAG Laser used to coagulate and vaporize tumor tissue (30W, 2040J total). Mechanical debulking performed with rigid barrel. Hemostasis achieved. Airway opened to 90%.\n\nA 16x40mm Dumon silicone stent was deployed into the mid-trachea using the rigid deployer. Position confirmed with flexible scope. Stent patent and stable. Patient extubated in OR.\n\n**COMPLICATIONS:** None.\n**EBL:** 20cc."
e_base = [
    {"label": "OBS_LESION",     **get_span(t_base, "Tracheal Stenosis", 1)},
    {"label": "PROC_ACTION",    **get_span(t_base, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION",    **get_span(t_base, "Laser Tumor Destruction", 1)},
    {"label": "PROC_ACTION",    **get_span(t_base, "Silicone Stent Placement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_base, "Rigid bronchoscope", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t_base, "Nd:YAG Laser", 1)},
    {"label": "PROC_ACTION",    **get_span(t_base, "vaporize", 1)},
    {"label": "PROC_ACTION",    **get_span(t_base, "Mechanical debulking", 1)},
    {"label": "DEV_STENT",      **get_span(t_base, "Dumon silicone stent", 1)},
    {"label": "MEAS_SIZE",      **get_span(t_base, "16x40mm", 1)}
]
BATCH_DATA.append({"id": "1701-A", "text": t_base, "entities": e_base})

if __name__ == "__main__":
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)