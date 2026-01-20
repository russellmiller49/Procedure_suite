import sys
from pathlib import Path

# Set up the repository root path
# Assuming the script is run from a location where 'scripts' is a subdirectory or sibling
# Adjust REPO_ROOT calculation as per your actual directory structure
try:
    REPO_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    REPO_ROOT = Path('.').resolve()

# Add the repository root to sys.path to allow importing the utility function
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

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
            return None  # Term not found enough times
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 2844661
# ==========================================
id_1 = "2844661"
text_1 = """BRONCHOSCOPY PROCEDURE NOTE

Date: [REDACTED]
Patient: [REDACTED]
MRN: [REDACTED]
DOB: [REDACTED] (53 years old)

Attending: Dr. Jennifer Liu, MD
Location: [REDACTED]

INDICATION: 53-year-old male with 30 pack-year smoking history presenting with 3-day history of moderate hemoptysis (approximately 100mL/day). CT chest showed bilateral upper lobe bronchiectasis and tree-in-bud opacities. Sputum cultures pending. Bronchoscopy for airway inspection and clearance of blood/secretions.

PREOPERATIVE DIAGNOSIS: Hemoptysis, likely infectious etiology vs bronchiectasis

POSTOPERATIVE DIAGNOSIS: Diffuse bronchiectasis with mucopurulent secretions; no endobronchial lesion or active bleeding source id[REDACTED]

PROCEDURE: Diagnostic flexible bronchoscopy with therapeutic suctioning

SEDATION: Moderate sedation (Midazolam 3mg IV, Fentanyl 50mcg IV)

PROCEDURE DESCRIPTION:
The patient was sedated and the flexible bronchoscope (Olympus BF-P190) was introduced via the oropharynx. The vocal cords appeared normal without lesions or edema. The trachea was patent with normal mucosa. Carina was sharp.

AIRWAY FINDINGS:
- Right mainstem: Patent. Old blood coating the mucosa.
- Right upper lobe: Multiple segments with thick mucopurulent secretions and old blood. Significant bronchiectatic changes. No endobronchial lesions. No active bleeding visualized.
- Bronchus intermedius: Patent with mild inflammation
- Right middle lobe: Mucopurulent secretions, no masses
- Right lower lobe: Bronchiectatic changes, thick secretions
- Left mainstem: Patent, old blood noted
- Left upper lobe: Similar bronchiectatic changes with mucopurulent secretions. No tumor or active bleeding.
- Lingula: Mild secretions
- Left lower lobe: Bronchiectasis, mucopurulent secretions, no source of bleeding id[REDACTED]

THERAPEUTIC INTERVENTION:
Extensive suctioning performed throughout all visualized airways. Large quantities of thick mucopurulent secretions and old blood were cleared from bilateral bronchi. No single bleeding source could be id[REDACTED] - the hemoptysis appears to be diffuse from inflamed bronchiectatic airways.

No biopsy was performed as no discrete lesion id[REDACTED]. No BAL performed as secretions already sent from suctioning.

SPECIMENS: 
- Bronchial aspirate/secretions: Bacterial culture, fungal culture, AFB culture, cytology

COMPLICATIONS: None. No active bleeding during or after procedure.

EBL: Trace

POST-PROCEDURE: Patient tolerated well. No respiratory distress. CXR unchanged from pre-procedure.

IMPRESSION & PLAN:
1. Diffuse bilateral bronchiectasis with mucopurulent secretions - no discrete bleeding source id[REDACTED]
2. Hemoptysis likely from diffuse bronchiectatic mucosal inflammation with superimposed infection
3. No endobronchial malignancy id[REDACTED]
4. Continue empiric antibiotics pending cultures
5. Pulmonary hygiene with chest physiotherapy
6. Follow-up in 2 weeks; consider repeat CT if hemoptysis persists

Dr. Jennifer Liu, MD
Pulmonary/Critical Care"""

entities_1 = [
    # Indication
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "upper lobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchiectasis", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "tree-in-bud opacities", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "clearance", 1)},

    # Pre/Post Op
    {"label": "OBS_FINDING", **get_span(text_1, "bronchiectasis", 2)}, # In PreOp
    {"label": "OBS_FINDING", **get_span(text_1, "bronchiectasis", 3)}, # In PostOp
    {"label": "OBS_FINDING", **get_span(text_1, "mucopurulent secretions", 1)},

    # Procedure Line
    {"label": "PROC_ACTION", **get_span(text_1, "flexible bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "suctioning", 1)},

    # Sedation
    {"label": "MEDICATION", **get_span(text_1, "Midazolam", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Fentanyl", 1)},

    # Description
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "flexible bronchoscope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "oropharynx", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "vocal cords", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "trachea", 1)}, # Fixed casing from "Trachea" to "trachea"
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Carina", 1)},

    # Airway Findings - Right
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Right mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Old blood", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right upper lobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "thick mucopurulent secretions", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "old blood", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "bronchiectatic changes", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Bronchus intermedius", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "inflammation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right middle lobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Mucopurulent secretions", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Right lower lobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bronchiectatic changes", 1)}, # Capital B
    {"label": "OBS_FINDING", **get_span(text_1, "thick secretions", 1)},

    # Airway Findings - Left
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Left mainstem", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "old blood", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Left upper lobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "mucopurulent secretions", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Lingula", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Mild secretions", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Left lower lobe", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bronchiectasis", 1)}, # Capital B
    {"label": "OBS_FINDING", **get_span(text_1, "mucopurulent secretions", 3)},

    # Therapeutic
    {"label": "PROC_ACTION", **get_span(text_1, "suctioning", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "thick mucopurulent secretions", 2)},
    {"label": "OBS_FINDING", **get_span(text_1, "old blood", 3)},
    {"label": "LATERALITY", **get_span(text_1, "bilateral", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "bronchi", 1)},
    
    # Specimens
    {"label": "SPECIMEN", **get_span(text_1, "Bronchial aspirate/secretions", 1)},
]

BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)