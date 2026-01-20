import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is running from standard location, adjust REPO_ROOT as needed
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

# Container for all processed notes
BATCH_DATA = []

# Helper function to locate spans
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
# Note 1: 4452109_syn_1
# ==========================================
t1 = """Rigid bronch. Chicken bone RLL. Removed with optical forceps en bloc. No injury."""
e1 = [
    {"label": "PROC_METHOD",        **get_span(t1, "Rigid bronch", 1)},
    {"label": "OBS_LESION",         **get_span(t1, "Chicken bone", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t1, "RLL", 1)},
    {"label": "PROC_ACTION",        **get_span(t1, "Removed", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t1, "optical forceps", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t1, "No injury", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 4452109_syn_2
# ==========================================
t2 = """[REDACTED] bronchoscopy for foreign body retrieval. The jagged osseous fragment was visualized within the right lower lobe. Utilizing optical forceps, the object was grasped and extracted en bloc with the rigid barrel to prevent glottic trauma."""
e2 = [
    {"label": "PROC_METHOD",        **get_span(t2, "bronchoscopy", 1)},
    {"label": "PROC_ACTION",        **get_span(t2, "retrieval", 1)},
    {"label": "OBS_LESION",         **get_span(t2, "foreign body", 1)},
    {"label": "OBS_LESION",         **get_span(t2, "jagged osseous fragment", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t2, "right lower lobe", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t2, "optical forceps", 1)},
    {"label": "PROC_ACTION",        **get_span(t2, "extracted", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t2, "rigid barrel", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 4452109_syn_3
# ==========================================
t3 = """CPT 31635: Rigid bronchoscopy with removal of foreign body. The scope was introduced, and the foreign object (bone) was id[REDACTED] in the RLL. It was removed using forceps. No separate code for suctioning."""
e3 = [
    {"label": "PROC_METHOD",        **get_span(t3, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",        **get_span(t3, "removal", 1)},
    {"label": "OBS_LESION",         **get_span(t3, "foreign body", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t3, "scope", 1)},
    {"label": "OBS_LESION",         **get_span(t3, "foreign object", 1)},
    {"label": "OBS_LESION",         **get_span(t3, "bone", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t3, "RLL", 1)},
    {"label": "PROC_ACTION",        **get_span(t3, "removed", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t3, "forceps", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 4452109_syn_4
# ==========================================
t4 = """Procedure: Rigid Bronchoscopy for FB Removal. Steps: 1. GA induced. 2. Rigid scope inserted. 3. FB id[REDACTED] RLL. 4. FB grasped and removed. 5. Airway re-inspected."""
e4 = [
    {"label": "PROC_METHOD",        **get_span(t4, "Rigid Bronchoscopy", 1)},
    {"label": "OBS_LESION",         **get_span(t4, "FB", 1)},
    {"label": "PROC_ACTION",        **get_span(t4, "Removal", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t4, "Rigid scope", 1)},
    {"label": "OBS_LESION",         **get_span(t4, "FB", 2)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t4, "RLL", 1)},
    {"label": "OBS_LESION",         **get_span(t4, "FB", 3)},
    {"label": "PROC_ACTION",        **get_span(t4, "removed", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 4452109_syn_5
# ==========================================
t5 = """rigid bronch for mr [REDACTED] swallowed a bone saw it in the rll used the forceps to grab it had to pull the whole scope out with it cause it was big no bleeding ok."""
e5 = [
    {"label": "PROC_METHOD",        **get_span(t5, "rigid bronch", 1)},
    {"label": "OBS_LESION",         **get_span(t5, "bone", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t5, "rll", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t5, "forceps", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t5, "scope", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t5, "no bleeding", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 4452109_syn_6
# ==========================================
t6 = """72-year-old male with foreign body aspiration. Rigid bronchoscopy performed. A chicken bone was seen in the RLL and removed using optical forceps. The airway was cleared of secretions."""
e6 = [
    {"label": "OBS_LESION",         **get_span(t6, "foreign body", 1)},
    {"label": "PROC_METHOD",        **get_span(t6, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION",         **get_span(t6, "chicken bone", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t6, "RLL", 1)},
    {"label": "PROC_ACTION",        **get_span(t6, "removed", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t6, "optical forceps", 1)},
    {"label": "OBS_FINDING",        **get_span(t6, "secretions", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 4452109_syn_7
# ==========================================
t7 = """[Indication] Foreign body aspiration. [Anesthesia] General. [Description] Rigid scope used. Bone removed from RLL with forceps. [Plan] Antibiotics."""
e7 = [
    {"label": "OBS_LESION",         **get_span(t7, "Foreign body", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t7, "Rigid scope", 1)},
    {"label": "OBS_LESION",         **get_span(t7, "Bone", 1)},
    {"label": "PROC_ACTION",        **get_span(t7, "removed", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t7, "RLL", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t7, "forceps", 1)},
    {"label": "MEDICATION",         **get_span(t7, "Antibiotics", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 4452109_syn_8
# ==========================================
t8 = """[REDACTED] to the OR for a rigid bronchoscopy to remove a chicken bone. We inserted the rigid scope and found the bone in the right lower lobe. We grabbed it with forceps and pulled everything out together. The airway looked fine afterwards."""
e8 = [
    {"label": "PROC_METHOD",        **get_span(t8, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION",        **get_span(t8, "remove", 1)},
    {"label": "OBS_LESION",         **get_span(t8, "chicken bone", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t8, "rigid scope", 1)},
    {"label": "OBS_LESION",         **get_span(t8, "bone", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t8, "right lower lobe", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t8, "forceps", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 4452109_syn_9
# ==========================================
t9 = """Therapeutic bronchoscopy with extraction of foreign material. A bone fragment was located in the basilar segments and withdrawn using grasping instruments."""
e9 = [
    {"label": "PROC_METHOD",        **get_span(t9, "Therapeutic bronchoscopy", 1)},
    {"label": "PROC_ACTION",        **get_span(t9, "extraction", 1)},
    {"label": "OBS_LESION",         **get_span(t9, "foreign material", 1)},
    {"label": "OBS_LESION",         **get_span(t9, "bone fragment", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t9, "basilar segments", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t9, "grasping instruments", 1)},
]
BATCH_DATA.append({"id": "4452109_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 4452109
# ==========================================
t10 = """**BRONCHOSCOPY REPORT**
**Patient:** Chen, Wei | **MRN:** 4452109 | **Date:** [REDACTED]
**Provider:** Dr. L. McCoy
**Diagnosis:** Foreign Body Aspiration

**History:** 72yo M with history of stroke and dysphagia, aspirated a chicken bone 2 days ago. Presents with cough and RLL infiltrate.

**Procedure:** Therapeutic Bronchoscopy (Rigid)
**Sedation:** General Anesthesia (ETT)

**Details:**
Rigid bronchoscope introduced. Right mainstem entered. Mucopurulent secretions suctioned from RLL. A jagged bone fragment was visualized wedged in the RLL basilar segments. 

Using optical forceps through the rigid barrel, the object was grasped. It could not be pulled through the glottis easily, so the object and scope were withdrawn en bloc. 

Repeat inspection showed minor mucosal abrasion but no perforation. Airways cleared of secretions. 

**Plan:** Antibiotics for post-obstructive pneumonia. Speech therapy consult."""
e10 = [
    {"label": "OBS_LESION",         **get_span(t10, "Foreign Body Aspiration", 1)},
    {"label": "OBS_LESION",         **get_span(t10, "chicken bone", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t10, "RLL", 1)},
    {"label": "PROC_METHOD",        **get_span(t10, "Therapeutic Bronchoscopy (Rigid)", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t10, "Rigid bronchoscope", 1)},
    {"label": "ANAT_AIRWAY",        **get_span(t10, "Right mainstem", 1)},
    {"label": "OBS_FINDING",        **get_span(t10, "Mucopurulent secretions", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t10, "RLL", 2)},
    {"label": "OBS_LESION",         **get_span(t10, "jagged bone fragment", 1)},
    {"label": "ANAT_LUNG_LOC",      **get_span(t10, "RLL basilar segments", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t10, "optical forceps", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t10, "rigid barrel", 1)},
    {"label": "DEV_INSTRUMENT",     **get_span(t10, "scope", 1)},
    {"label": "OBS_FINDING",        **get_span(t10, "mucosal abrasion", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(t10, "no perforation", 1)},
    {"label": "OBS_FINDING",        **get_span(t10, "secretions", 2)},
    {"label": "MEDICATION",         **get_span(t10, "Antibiotics", 1)},
]
BATCH_DATA.append({"id": "4452109", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)