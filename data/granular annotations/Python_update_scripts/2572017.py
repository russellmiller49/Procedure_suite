import sys
from pathlib import Path

# Set up the repository root directory
# The script is located in data/granular annotations/Python_update_scripts/
# We need to go up 4 levels to reach the project root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Add the scripts directory to the system path to allow importing the utility function
sys.path.append(str(REPO_ROOT / "scripts"))

# Import the utility function
from add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    
    Args:
        text (str): The text to search within.
        term (str): The term to search for.
        occurrence (int): The specific occurrence to find (1-based index).
    
    Returns:
        tuple: (start_index, end_index) of the term.
    
    Raises:
        ValueError: If the term is not found the specified number of times.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return start, start + len(term)

# ==========================================
# Note 1: 2572017_syn_1
# ==========================================
text_1 = """Ind: Squamous cell CA, RMS block.
Proc: Rigid bronch, Cryoextraction.
Action: Tumor frozen/removed piecemeal. Laser/APC for base.
Result: 77% -> 22% obstruction.
EBL: 50mL.
Plan: ICU."""

entities_1 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "Squamous cell CA", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_1, "RMS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "Rigid bronch", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "Cryoextraction", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_1, "Tumor", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "frozen", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_1, "removed", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "Laser", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_1, "APC", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_1, "77%", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_1, "22% obstruction", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_1, "50mL", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 2572017_syn_2
# ==========================================
text_2 = """PROCEDURE: Rigid bronchoscopy with cryotherapy for malignant airway obstruction.
PATIENT: [REDACTED], 58M.
FINDINGS: 77% obstruction of the Right Mainstem (RMS) by squamous cell carcinoma. Cryoextraction was utilized to debulk the exophytic tumor component. Following bulk removal, the tumor base was treated with APC and Laser to ensure hemostasis and further ablation (CPT 31641). Final airway inspection revealed 22% residual stenosis."""

entities_2 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "Rigid bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "cryotherapy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "malignant airway obstruction", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_2, "77% obstruction", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_2, "Right Mainstem", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_2, "RMS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "squamous cell carcinoma", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "Cryoextraction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "debulk", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "exophytic tumor", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_2, "tumor", 2)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "APC", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_2, "Laser", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_2, "ablation", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_2, "22% residual stenosis", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 2572017_syn_3
# ==========================================
text_3 = """Service: Bronchoscopy with tumor destruction (31641).
Method: Cryoextraction and Laser/APC ablation.
Site: Right Mainstem Bronchus.
Pre-op: 77% occlusion.
Post-op: 22% occlusion.
Specimens: Sent for histology."""

entities_3 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "tumor destruction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "Cryoextraction", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "Laser", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_3, "APC", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_3, "ablation", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_3, "Right Mainstem Bronchus", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_3, "77% occlusion", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_3, "22% occlusion", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_3, "Specimens", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 2572017_syn_4
# ==========================================
text_4 = """Procedure: Rigid Bronch w/ Cryo
Patient: [REDACTED]
Steps:
1. GA. Rigid scope to RMS.
2. Tumor found.
3. Cryo probe used to freeze and pull tumor chunks.
4. Laser used to clean up base.
5. Good hemostasis.
6. Residual 22%.
Plan: ICU."""

entities_4 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Rigid Bronch", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "Cryo", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Rigid scope", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_4, "RMS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_4, "Tumor", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Cryo probe", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "freeze", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_4, "pull", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_4, "tumor", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_4, "Laser", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_4, "Good hemostasis", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_4, "Residual 22%", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 2572017_syn_5
# ==========================================
text_5 = """[REDACTED]. squamous cell cancer blocking the right mainstem. we used the cryo probe to pull the tumor out frozen. did a bunch of passes. then used the laser to stop the bleeding at the base. went from 77 percent blocked to 22 percent. pretty good result. 50ml blood loss. sending him to icu."""

entities_5 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "squamous cell cancer", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_5, "right mainstem", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "cryo probe", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_5, "tumor", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_5, "frozen", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_5, "laser", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_5, "77 percent blocked", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_5, "22 percent", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_5, "50ml", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 2572017_syn_6
# ==========================================
text_6 = """Squamous cell carcinoma with airway compromise. Pre-procedure 77% obstruction at RMS. Under general anesthesia, rigid bronchoscopy performed. Endobronchial tumor id[REDACTED] at RMS. Cryoextraction performed with sequential tumor removal. Multiple passes performed to achieve maximal debulking. Additional APC/laser used for hemostasis and tumor base ablation. Post-procedure 22% residual obstruction. EBL 50mL."""

entities_6 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "Squamous cell carcinoma", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_6, "77% obstruction", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_6, "RMS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "rigid bronchoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_6, "Endobronchial tumor", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_6, "RMS", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "Cryoextraction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "tumor removal", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "debulking", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "APC", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_6, "laser", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_6, "tumor base ablation", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_6, "22% residual obstruction", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_6, "50mL", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 2572017_syn_7
# ==========================================
text_7 = """[Indication]
Squamous Cell CA, 77% RMS obstruction.
[Anesthesia]
General.
[Description]
Rigid bronchoscopy. Cryoextraction for debulking. APC/Laser for base ablation. Residual obstruction 22%.
[Plan]
ICU admission."""

entities_7 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "Squamous Cell CA", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_7, "77%", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_7, "RMS", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_7, "obstruction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "Rigid bronchoscopy", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "Cryoextraction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "debulking", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "APC", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_7, "Laser", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_7, "ablation", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_7, "Residual obstruction 22%", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 2572017_syn_8
# ==========================================
text_8 = """We brought [REDACTED] OR to address the blockage in his right mainstem bronchus. Using a rigid bronchoscope, we employed cryoextraction to freeze and remove the tumor in sections. We then used APC and laser to treat the base of the tumor and control bleeding. The obstruction was reduced from 77% to 22%."""

entities_8 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "blockage", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_8, "right mainstem bronchus", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "rigid bronchoscope", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "cryoextraction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "freeze", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_8, "remove", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "tumor", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "APC", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_8, "laser", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_8, "tumor", 2)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_8, "77%", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_8, "22%", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 2572017_syn_9
# ==========================================
text_9 = """Under general anesthesia, rigid bronchoscopy was executed. An endobronchial tumor was id[REDACTED] at the RMS. Cryoextraction was carried out with sequential tumor extraction. Several passes were completed to attain maximal reduction. Supplemental APC/laser was used for hemostasis and tumor base destruction."""

entities_9 = [
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "rigid bronchoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_9, "endobronchial tumor", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_9, "RMS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "Cryoextraction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "tumor extraction", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "APC", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_9, "laser", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_9, "tumor base destruction", 1)))},
]
BATCH_DATA.append({"id": "2572017_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 2572017
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: CAPT Russell Miller, MD

Indication: Squamous cell carcinoma with airway compromise
Pre-procedure: ~77% obstruction at RMS

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at RMS.
Cryoextraction performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Additional APC/laser used for hemostasis and tumor base ablation.
Post-procedure: ~22% residual obstruction.
EBL: ~50mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Miller, MD"""

entities_10 = [
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "Squamous cell carcinoma", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **dict(zip(["start", "end"], get_span(text_10, "~77% obstruction", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "RMS", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "rigid bronchoscopy", 1)))},
    {"label": "OBS_LESION", **dict(zip(["start", "end"], get_span(text_10, "Endobronchial tumor", 1)))},
    {"label": "ANAT_AIRWAY", **dict(zip(["start", "end"], get_span(text_10, "RMS", 2)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "Cryoextraction", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "tumor removal", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "debulking", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "APC", 1)))},
    {"label": "DEV_INSTRUMENT", **dict(zip(["start", "end"], get_span(text_10, "laser", 1)))},
    {"label": "PROC_ACTION", **dict(zip(["start", "end"], get_span(text_10, "tumor base ablation", 1)))},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **dict(zip(["start", "end"], get_span(text_10, "~22% residual obstruction", 1)))},
    {"label": "MEAS_VOL", **dict(zip(["start", "end"], get_span(text_10, "~50mL", 1)))},
    {"label": "OUTCOME_COMPLICATION", **dict(zip(["start", "end"], get_span(text_10, "Hemostasis achieved", 1)))},
    {"label": "SPECIMEN", **dict(zip(["start", "end"], get_span(text_10, "Specimens", 1)))},
]
BATCH_DATA.append({"id": "2572017", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)