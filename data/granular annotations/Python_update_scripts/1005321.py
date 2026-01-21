import sys
from pathlib import Path

# Set up the repository root path
# (Assumes this script is running in a structure like /repo/scripts/add_case_1005321.py)
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add repo root to sys.path to allow importing from scripts module
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for (case-sensitive).
        occurrence (int): The 1-based index of the occurrence to find.
    
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None  # Term not found enough times
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1005321
# ==========================================
id_1 = "1005321"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (46 years old)
Date: [REDACTED]
Location: [REDACTED]

Attending: Dr. Rachel Kim, MD
Fellow: Dr. Ahmed Hassan, MD (PGY-5)

PREOPERATIVE DIAGNOSIS: Recurrent post-intubation tracheal stenosis

POSTOPERATIVE DIAGNOSIS: Same - Grade III tracheal stenosis, 8mm web-like

PROCEDURE:
1. Rigid bronchoscopy
2. Balloon dilation of tracheal stenosis
3. Biodegradable tracheal stent placement (BD-Stent, Merit Endotek)

INDICATION: 46-year-old male with history of prolonged intubation (28 days) for ARDS secondary to COVID-19 in 2021. Developed tracheal stenosis requiring multiple dilations. Has failed 3 prior balloon dilations with recurrence within 4-6 weeks. After discussion of options including T-tube, surgical resection, and biodegradable stent, patient elected for biodegradable stent trial given relatively young age and desire to avoid permanent stent or surgery.

ANESTHESIA: Total intravenous anesthesia (propofol/remifentanil)

PROCEDURE DETAILS:
Under TIVA, rigid bronchoscopy performed using 12mm Storz ventilating rigid bronchoscope. Airway anatomy:
- Subglottic region: Normal
- Tracheal stenosis: Located 2.5cm below vocal cords, approximately 8mm thick web-like stenosis narrowing the lumen to 5mm (Grade III, Myer-Cotton)
- Distal trachea and bilateral mainstem: Normal

Balloon dilation performed using 15mm x 40mm CRE balloon (Boston Scientific). Balloon inflated to 8 ATM x 60 seconds x 3 inflations with radial fracturing of the stenosis observed. Post-dilation diameter approximately 12mm.

Merit Endotek BD-Stent (18mm diameter x 30mm length, polydioxanone-based) selected based on tracheal measurements. Stent delivery system advanced through the rigid bronchoscope and deployed under direct visualization with the proximal and distal markers positioned 1cm beyond the stenosis margins. Stent expanded fully to approximately 16mm. Confirmation of good apposition to tracheal wall.

Post-procedure bronchoscopy confirmed patent airway through the stent with no evidence of stent migration. Mucosa intact with minimal bleeding from dilation site.

SPECIMENS: None

COMPLICATIONS: None

EBL: <5mL

DISPOSITION: PACU recovery, discharge home same day with post-procedure instructions. No activity restrictions. Soft diet x 24 hours.

FOLLOW-UP:
- Bronchoscopy in 8 weeks for stent assessment
- BD-Stent expected to degrade over 4-6 months
- CT airway in 3 months

Dr. Rachel Kim, MD
Dr. Ahmed Hassan, MD"""

entities_1 = [
    # Header / Diagnosis
    {"label": "OBS_LESION", **get_span(text_1, "tracheal stenosis", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "tracheal stenosis", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "Grade III", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8mm", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "web-like", 1)},

    # Procedure List
    {"label": "PROC_ACTION", **get_span(text_1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Balloon dilation", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "tracheal stenosis", 3)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_1, "Biodegradable", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheal", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "stent placement", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "BD-Stent", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "Merit Endotek", 1)},

    # Indication
    {"label": "OBS_LESION", **get_span(text_1, "tracheal stenosis", 4)},
    {"label": "PROC_ACTION", **get_span(text_1, "dilations", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_1, "prior", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "balloon dilations", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_1, "biodegradable", 2)}, # "biodegradable stent"
    {"label": "DEV_STENT", **get_span(text_1, "stent", 2)}, # "biodegradable stent"

    # Anesthesia
    {"label": "MEDICATION", **get_span(text_1, "propofol", 1)},
    {"label": "MEDICATION", **get_span(text_1, "remifentanil", 1)},

    # Procedure Details
    # FIXED: "rigid bronchoscopy" (lowercase) only appears once in the text (under PROCEDURE DETAILS).
    # The first instance in the text is "Rigid bronchoscopy" (uppercase), which was tagged separately above.
    {"label": "PROC_ACTION", **get_span(text_1, "rigid bronchoscopy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Storz", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Subglottic region", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Tracheal stenosis", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "2.5cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "vocal cords", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "8mm", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "web-like stenosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "narrowing the lumen to 5mm", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "Grade III", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Distal trachea", 1)},
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "mainstem", 1)},

    # Dilation
    {"label": "PROC_ACTION", **get_span(text_1, "Balloon dilation", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "15mm x 40mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "CRE balloon", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Boston Scientific", 1)},
    {"label": "MEAS_PRESS", **get_span(text_1, "8 ATM", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "60 seconds", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "3", 2)}, # "3 inflations"
    {"label": "OBS_LESION", **get_span(text_1, "stenosis", 7)}, # "fracturing of the stenosis"
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "Post-dilation diameter approximately 12mm", 1)},

    # Stenting
    {"label": "DEV_STENT", **get_span(text_1, "Merit Endotek", 2)},
    {"label": "DEV_STENT", **get_span(text_1, "BD-Stent", 2)},
    {"label": "DEV_STENT_SIZE", **get_span(text_1, "18mm diameter x 30mm length", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_1, "polydioxanone-based", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheal", 6)},
    {"label": "DEV_STENT", **get_span(text_1, "Stent", 3)}, # "Stent delivery system"
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "rigid bronchoscope", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "stenosis", 8)}, # "stenosis margins"
    {"label": "DEV_STENT", **get_span(text_1, "Stent", 4)}, # "Stent expanded"
    {"label": "MEAS_SIZE", **get_span(text_1, "16mm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "tracheal wall", 1)},

    # Results/Complications
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "patent airway", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 5)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 6)}, # "stent migration"
    {"label": "OBS_FINDING", **get_span(text_1, "Mucosa intact", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "minimal bleeding", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "dilation site", 1)}, # Conceptually airway location
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "None", 2)}, # Under COMPLICATIONS

    # Follow-up
    {"label": "DEV_STENT", **get_span(text_1, "BD-Stent", 3)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)