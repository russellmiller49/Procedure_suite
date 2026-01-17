import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
sys.path.append(str(REPO_ROOT))
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the Nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' (occurrence {occurrence}) not found in text.")
    
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 1553685
# ==========================================
id_1 = "1553685"
text_1 = """PROCEDURE NOTE - INTERVENTIONAL PULMONOLOGY

DATE: [REDACTED]
PATIENT: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED]
AGE: 84 years old
SEX: Female

ATTENDING: Dr. Michael Santos, MD
LOCATION: [REDACTED]

PREOPERATIVE DIAGNOSIS:
1. Recurrent bilateral pleural effusions
2. New York Heart Association Class IV heart failure with reduced ejection fraction (EF 15%)
3. Not candidate for mechanical circulatory support or transplant

POSTOPERATIVE DIAGNOSIS: Same

PROCEDURE: Left-sided tunneled indwelling pleural catheter (PleurX) placement

INDICATION: This 84-year-old female with end-stage heart failure has required hospitalization 6 times in the past 3 months for symptomatic bilateral pleural effusions despite maximum medical therapy. After multidisciplinary discussion including heart failure, palliative care, and IP, decision was made for left-sided IPC given larger effusion on left. Patient and family understand palliative intent.

ANESTHESIA: Local anesthesia only (2% lidocaine) - patient unable to tolerate any sedation given severity of cardiac dysfunction.

PROCEDURE:
Patient [REDACTED]-recumbent at 45 degrees (unable to lay flat due to orthopnea). Timeout completed. Ultrasound id[REDACTED] large left pleural effusion. Skin marked at 6th intercostal space, anterior axillary line.

Skin prepped with ChloraPrep. Local anesthesia infiltrated liberally along proposed tract. 3cm skin incision made. Tunneling device used to create 8cm subcutaneous tunnel anteriorly. PleurX 15.5Fr catheter threaded through tunnel.

Pleural space entered using Seldinger technique under ultrasound guidance. Catheter advanced without difficulty. Initial drainage of 800mL clear yellow fluid - drainage stopped per institutional protocol for heart failure patients (max 500-1000mL to avoid re-expansion issues and volume shifts).

Catheter secured with suture. Dry sterile dressing applied. Post-procedure portable CXR confirms good catheter position, no pneumothorax.

Fluid sent for: Cell count, chemistry, NT-proBNP

ESTIMATED BLOOD LOSS: Minimal

COMPLICATIONS: None. Patient tolerated procedure well with no hemodynamic changes.

PLAN:
1. Overnight telemetry monitoring
2. Home health for IPC drainage teaching
3. Drainage frequency to be determined based on symptoms - anticipate every 2-3 days
4. Continue diuretics and guideline-directed medical therapy
5. Follow-up with heart failure team and IP clinic

Dr. Michael Santos, MD
Interventional Pulmonology"""

entities_1 = [
    # Preoperative Diagnosis
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "pleural effusions", 1)},

    # Procedure Title
    {"label": "LATERALITY", **get_span(text_1, "Left-sided", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "tunneled indwelling pleural catheter", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "PleurX", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "placement", 1)},

    # Indication
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "pleural effusions", 2)},
    {"label": "LATERALITY", **get_span(text_1, "left-sided", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "IPC", 1)},
    # Note: occurrence 1 is in "left-sided" (lowercase), occurrence 2 is "effusion on left"
    {"label": "LATERALITY", **get_span(text_1, "left", 2)}, # "effusion on left"

    # Anesthesia
    {"label": "MEDICATION", **get_span(text_1, "lidocaine", 1)},

    # Procedure Body
    {"label": "PROC_METHOD", **get_span(text_1, "Ultrasound", 1)},
    # Note: occurrence 3 is "large left pleural..."
    {"label": "LATERALITY", **get_span(text_1, "left", 3)}, 
    {"label": "OBS_FINDING", **get_span(text_1, "pleural effusion", 1)}, # singular
    {"label": "ANAT_PLEURA", **get_span(text_1, "6th intercostal space", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Tunneling device", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8cm", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "PleurX", 2)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "15.5Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 2)}, # 1 is 'pleural catheter' in title, 2 is '15.5Fr catheter'
    {"label": "ANAT_PLEURA", **get_span(text_1, "Pleural space", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Seldinger technique", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "ultrasound guidance", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 1)}, # Capitalized "Catheter advanced"
    {"label": "MEAS_VOL", **get_span(text_1, "800mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "clear yellow fluid", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "Catheter", 2)}, # Capitalized "Catheter secured"
    {"label": "DEV_CATHETER", **get_span(text_1, "catheter", 3)}, # lowercase "catheter position" (occ 3)
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no pneumothorax", 1)},

    # Post-Procedure / Specimens
    {"label": "SPECIMEN", **get_span(text_1, "Fluid", 1)}, # Capitalized "Fluid sent for"

    # Complications / Plan
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 1)}, # Under COMPLICATIONS
    {"label": "DEV_CATHETER", **get_span(text_1, "IPC", 2)} # Plan section
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)