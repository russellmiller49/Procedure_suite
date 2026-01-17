import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add the case
# Ensure this script is run from a location where 'scripts.add_training_case' is accessible
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback/Mock for standalone testing if needed, though strictly we assume the environment exists
    print("Warning: Could not import 'add_case'. Ensure you are in the correct repo structure.")
    def add_case(case_id, text, entities, root):
        print(f"Would add case {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term in the text.
    Returns None if the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 1808730
# ==========================================
id_1 = "1808730"
text_1 = """OPERATIVE REPORT - INTERVENTIONAL PULMONOLOGY

PATIENT: [REDACTED]
MRN: [REDACTED]  
DOB: [REDACTED]
AGE: 69
DATE OF PROCEDURE: [REDACTED]

SURGEON: Dr. David Chen, MD
ASSISTANT: Dr. Katherine Wong, MD (IP Fellow)
ANESTHESIOLOGIST: Dr. Paul Martinez, MD
FACILITY: [REDACTED]

PREOPERATIVE DIAGNOSIS: Fractured right mainstem bronchus self-expanding metallic stent (SEMS)

POSTOPERATIVE DIAGNOSIS: Same; stent granulation tissue ingrowth

PROCEDURES PERFORMED:
1. Rigid bronchoscopy with stent removal
2. Bronchoscopy with destruction of endobronchial granulation tissue using APC

INDICATION: 69-year-old male with history of esophageal cancer status post esophagectomy complicated by recurrent stricture of airway fistula 18 months ago for which a covered SEMS was placed in the right mainstem bronchus. Recent CT showed stent fracture with proximal wire protruding into the trachea. Patient symptomatic with worsening cough and hemoptysis.

ANESTHESIA: General anesthesia, jet ventilation

DESCRIPTION OF PROCEDURE:
Under general anesthesia, the patient was intubated with a 12mm Bryan-Dumon ventilating rigid bronchoscope. Examination of the trachea revealed the fractured proximal portion of the right mainstem SEMS protruding approximately 1.5cm into the distal trachea. The fractured wire ends were sharp and had caused mucosal injury with surrounding granulation tissue formation.

A flexible bronchoscope was passed through the rigid scope to examine beyond the stent. The stent lumen was narrowed by approximately 40% due to granulation tissue ingrowth at the proximal end. The distal right bronchus intermedius appeared patent.

The granulation tissue was treated with APC (ERBE VIO, 30W, Effect 2) at the proximal stent margin, achieving adequate hemostasis and improving visualization.

Using a combination of rigid optical forceps and alligator forceps, the proximal edge of the stent was grasped. The stent was collapsed using the forceps in a rolling fashion and withdrawn en bloc through the rigid bronchoscope.

Inspection of the airway post-removal revealed:
- Mild residual granulation tissue at the former stent site (treated with APC)
- No perforation or significant bleeding
- Bronchus intermedius patent
- Right upper, middle, and lower lobe orifices patent

Final inspection showed no debris, no significant bleeding, patent airways bilaterally. The patient was extubated and transferred to PACU in stable condition.

SPECIMENS: None (stent sent to pathology for documentation)

COMPLICATIONS: None

EBL: 15mL

DISPOSITION: Same day discharge anticipated. Follow-up bronchoscopy in 6 weeks to assess granulation tissue recurrence.

Dr. David Chen, MD
Dr. Katherine Wong, MD"""

entities_1 = [
    # Diagnosis / Header
    {"label": "ANAT_AIRWAY", **get_span(text_1, "right mainstem bronchus", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "self-expanding metallic stent", 1)}, # Full descriptor
    {"label": "DEV_STENT", **get_span(text_1, "SEMS", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "granulation tissue", 1)},

    # Procedures List
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "stent removal", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "destruction", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "granulation tissue", 2)}, # "endobronchial granulation tissue"
    {"label": "PROC_METHOD", **get_span(text_1, "APC", 1)},

    # Indication
    {"label": "CTX_HISTORICAL", **get_span(text_1, "history of", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "esophageal cancer", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_1, "covered", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "SEMS", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "right mainstem bronchus", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "stent fracture", 1)}, # Not explicitly in guide, but matches clinical finding
    {"label": "ANAT_AIRWAY", **get_span(text_1, "trachea", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "hemoptysis", 1)},

    # Anesthesia / Description
    # jet ventilation is a specific method, technically PROC_METHOD but often excluded if not interventional. Including for completeness.
    {"label": "PROC_METHOD", **get_span(text_1, "jet ventilation", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "12mm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "rigid bronchoscope", 1)}, # Specific instrument
    {"label": "ANAT_AIRWAY", **get_span(text_1, "trachea", 2)},
    {"label": "DEV_STENT", **get_span(text_1, "SEMS", 3)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.5cm", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "trachea", 3)}, # "distal trachea"
    {"label": "OBS_FINDING", **get_span(text_1, "granulation tissue", 3)},

    # Flexible Scope / Lumen
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "flexible bronchoscope", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 2)}, # "examine beyond the stent"
    {"label": "DEV_STENT", **get_span(text_1, "stent", 3)}, # "stent lumen"
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "narrowed by approximately 40%", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "granulation tissue", 4)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "bronchus intermedius", 1)},
    # "patent" here is pre-intervention assessment, so OBS_FINDING
    {"label": "OBS_FINDING", **get_span(text_1, "patent", 1)}, 

    # Treatment
    {"label": "OBS_FINDING", **get_span(text_1, "granulation tissue", 5)},
    {"label": "PROC_METHOD", **get_span(text_1, "APC", 2)},
    {"label": "MEAS_ENERGY", **get_span(text_1, "30W", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 4)},

    # Extraction
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "rigid optical forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "alligator forceps", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 5)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 6)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "forceps", 3)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "rigid bronchoscope", 2)},

    # Post-Removal Inspection
    {"label": "OBS_FINDING", **get_span(text_1, "granulation tissue", 6)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 7)}, # "former stent site"
    {"label": "PROC_METHOD", **get_span(text_1, "APC", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "No perforation", 1)},
    # "No ... significant bleeding" is the outcome concept
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "no significant bleeding", 1)},
    # Corrected below: "Bronchus intermedius" (Capitalized) appears for the 1st time here (previous one was lowercase)
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Bronchus intermedius", 1)}, # "Bronchus intermedius patent"
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "patent", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "middle", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "lower lobe", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "patent", 3)},
    
    # Final Inspection
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "patent", 4)},
    {"label": "LATERALITY", **get_span(text_1, "bilaterally", 1)},
    
    # EBL
    {"label": "MEAS_VOL", **get_span(text_1, "15mL", 1)},
    
    # Disposition
    # "6 weeks" -> CTX_TIME or similar not fully covered, usually procedure time.
    {"label": "OBS_FINDING", **get_span(text_1, "granulation tissue", 7)}
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)