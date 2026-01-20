import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is located in 'scripts/' or similar relative to the root
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to import utility functions
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function to add cases
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of a term in the text.
    
    Args:
        text (str): The text to search.
        term (str): The term to find.
        occurrence (int): The occurrence number (1-based).
        
    Returns:
        dict: A dictionary with 'start' and 'end' indices.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
            
    if start == -1:
        raise ValueError(f"Term '{term}' not found (occurrence {occurrence}) in text.")
        
    return {'start': start, 'end': start + len(term)}

# ==========================================
# Note 1: 4229850_syn_1
# ==========================================
text_1 = """Indication: Lung adenocarcinoma CAO at BI.
Findings: 74% obstruction.
Procedure:
- Rigid bronch.
- Mechanical debulking w/ biopsy forceps.
- Multiple passes.
Result: 12% residual. Hemostasis achieved.
EBL: 75ml.
Plan: ICU."""

entities_1 = [
    {"label": "OBS_LESION", "text": "Lung adenocarcinoma", **get_span(text_1, "Lung adenocarcinoma", 1)},
    {"label": "OBS_LESION", "text": "CAO", **get_span(text_1, "CAO", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_1, "BI", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "74% obstruction", **get_span(text_1, "74% obstruction", 1)},
    {"label": "PROC_METHOD", "text": "Rigid bronch", **get_span(text_1, "Rigid bronch", 1)},
    {"label": "PROC_ACTION", "text": "Mechanical debulking", **get_span(text_1, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", "text": "biopsy forceps", **get_span(text_1, "biopsy forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "12% residual", **get_span(text_1, "12% residual", 1)},
    {"label": "OUTCOME_COMPLICATION", "text": "Hemostasis achieved", **get_span(text_1, "Hemostasis achieved", 1)},
    {"label": "MEAS_VOL", "text": "75ml", **get_span(text_1, "75ml", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 4229850_syn_2
# ==========================================
text_2 = """OPERATIVE SUMMARY: [REDACTED] a 74% obstruction of the bronchus intermedius (BI) due to lung adenocarcinoma. The patient was placed under general anesthesia. Rigid bronchoscopic inspection id[REDACTED] the exophytic tumor. Mechanical excision was performed utilizing rigid biopsy forceps. Sequential bites were taken to debulk the lesion until the airway lumen was satisfactorily restored (12% residual). Hemostasis was maintained throughout.
PATHOLOGY: Tissue submitted for histological analysis."""

entities_2 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "74% obstruction", **get_span(text_2, "74% obstruction", 1)},
    {"label": "ANAT_AIRWAY", "text": "bronchus intermedius", **get_span(text_2, "bronchus intermedius", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_2, "BI", 1)},
    {"label": "OBS_LESION", "text": "lung adenocarcinoma", **get_span(text_2, "lung adenocarcinoma", 1)},
    {"label": "PROC_METHOD", "text": "Rigid bronchoscopic", **get_span(text_2, "Rigid bronchoscopic", 1)},
    {"label": "OBS_LESION", "text": "exophytic tumor", **get_span(text_2, "exophytic tumor", 1)},
    {"label": "PROC_ACTION", "text": "Mechanical excision", **get_span(text_2, "Mechanical excision", 1)},
    {"label": "DEV_INSTRUMENT", "text": "rigid biopsy forceps", **get_span(text_2, "rigid biopsy forceps", 1)},
    {"label": "PROC_ACTION", "text": "debulk", **get_span(text_2, "debulk", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "12% residual", **get_span(text_2, "12% residual", 1)},
    {"label": "OUTCOME_COMPLICATION", "text": "Hemostasis was maintained", **get_span(text_2, "Hemostasis was maintained", 1)},
    {"label": "SPECIMEN", "text": "Tissue", **get_span(text_2, "Tissue", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 4229850_syn_3
# ==========================================
text_3 = """Code: 31640 (Bronchoscopy with excision of tumor).
Method: Mechanical excision via rigid forceps.
Location: Bronchus Intermedius (BI).
Details:
- Tumor visualization (74% block).
- Physical removal of tissue.
- Hemostasis.
- Final patency check (12% residual).
Pathology: Samples sent."""

entities_3 = [
    {"label": "PROC_ACTION", "text": "Bronchoscopy with excision", **get_span(text_3, "Bronchoscopy with excision", 1)},
    {"label": "OBS_LESION", "text": "tumor", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_ACTION", "text": "Mechanical excision", **get_span(text_3, "Mechanical excision", 1)},
    {"label": "DEV_INSTRUMENT", "text": "rigid forceps", **get_span(text_3, "rigid forceps", 1)},
    {"label": "ANAT_AIRWAY", "text": "Bronchus Intermedius", **get_span(text_3, "Bronchus Intermedius", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_3, "BI", 1)},
    {"label": "OBS_LESION", "text": "Tumor", **get_span(text_3, "Tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "74% block", **get_span(text_3, "74% block", 1)},
    {"label": "OUTCOME_COMPLICATION", "text": "Hemostasis", **get_span(text_3, "Hemostasis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "12% residual", **get_span(text_3, "12% residual", 1)},
    {"label": "SPECIMEN", "text": "Samples", **get_span(text_3, "Samples", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 4229850_syn_4
# ==========================================
text_4 = """Procedure: Tumor Excision (Forceps)
Patient: [REDACTED]teps:
1. Rigid scope inserted.
2. Tumor at BI visualized.
3. Used biopsy forceps for mechanical debulking.
4. Removed tumor in pieces.
5. Hemostasis achieved.
Plan: ICU obs."""

entities_4 = [
    {"label": "PROC_ACTION", "text": "Tumor Excision", **get_span(text_4, "Tumor Excision", 1)},
    {"label": "DEV_INSTRUMENT", "text": "Forceps", **get_span(text_4, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", "text": "Rigid scope", **get_span(text_4, "Rigid scope", 1)},
    {"label": "OBS_LESION", "text": "Tumor", **get_span(text_4, "Tumor", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_4, "BI", 1)},
    {"label": "DEV_INSTRUMENT", "text": "biopsy forceps", **get_span(text_4, "biopsy forceps", 1)},
    {"label": "PROC_ACTION", "text": "mechanical debulking", **get_span(text_4, "mechanical debulking", 1)},
    {"label": "OBS_LESION", "text": "tumor", **get_span(text_4, "tumor", 1)},
    {"label": "OUTCOME_COMPLICATION", "text": "Hemostasis achieved", **get_span(text_4, "Hemostasis achieved", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 4229850_syn_5
# ==========================================
text_5 = """Kevin Hernandez here for tumor removal in the BI blocking 74 percent. We used the rigid scope and the big biopsy forceps to just grab and pull the tumor out. Did a bunch of passes got it down to 12 percent. Bleeding was okay about 75cc. Samples sent to lab. He goes to ICU tonight."""

entities_5 = [
    {"label": "OBS_LESION", "text": "tumor", **get_span(text_5, "tumor", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_5, "BI", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "blocking 74 percent", **get_span(text_5, "blocking 74 percent", 1)},
    {"label": "DEV_INSTRUMENT", "text": "rigid scope", **get_span(text_5, "rigid scope", 1)},
    {"label": "DEV_INSTRUMENT", "text": "biopsy forceps", **get_span(text_5, "biopsy forceps", 1)},
    {"label": "OBS_LESION", "text": "tumor", **get_span(text_5, "tumor", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "12 percent", **get_span(text_5, "12 percent", 1)},
    {"label": "MEAS_VOL", "text": "75cc", **get_span(text_5, "75cc", 1)},
    {"label": "SPECIMEN", "text": "Samples", **get_span(text_5, "Samples", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 4229850_syn_6
# ==========================================
text_6 = """Indication: Primary lung adenocarcinoma with CAO, ~74% obstruction at BI. Under general anesthesia, rigid bronchoscopy was performed. Endobronchial tumor was id[REDACTED] at BI. Rigid bronchoscopy debulking with biopsy forceps was performed with sequential tumor removal. Multiple passes were performed to achieve maximal debulking. Post-procedure obstruction was ~12% residual obstruction. EBL was ~75mL and hemostasis was achieved. Specimens were sent for histology."""

entities_6 = [
    {"label": "OBS_LESION", "text": "lung adenocarcinoma", **get_span(text_6, "lung adenocarcinoma", 1)},
    {"label": "OBS_LESION", "text": "CAO", **get_span(text_6, "CAO", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "~74% obstruction", **get_span(text_6, "~74% obstruction", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_6, "BI", 1)},
    {"label": "PROC_METHOD", "text": "rigid bronchoscopy", **get_span(text_6, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", "text": "Endobronchial tumor", **get_span(text_6, "Endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_6, "BI", 2)},
    {"label": "PROC_METHOD", "text": "Rigid bronchoscopy", **get_span(text_6, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", "text": "debulking", **get_span(text_6, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", "text": "biopsy forceps", **get_span(text_6, "biopsy forceps", 1)},
    {"label": "PROC_ACTION", "text": "debulking", **get_span(text_6, "debulking", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "~12% residual obstruction", **get_span(text_6, "~12% residual obstruction", 1)},
    {"label": "MEAS_VOL", "text": "~75mL", **get_span(text_6, "~75mL", 1)},
    {"label": "OUTCOME_COMPLICATION", "text": "hemostasis was achieved", **get_span(text_6, "hemostasis was achieved", 1)},
    {"label": "SPECIMEN", "text": "Specimens", **get_span(text_6, "Specimens", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 4229850_syn_7
# ==========================================
text_7 = """[Indication]
Lung adenocarcinoma, BI obstruction (74%).
[Anesthesia]
General, Rigid Bronch.
[Description]
Mechanical debulking with forceps performed. Tumor excised. Residual obstruction 12%. EBL 75ml.
[Plan]
ICU observation. Oncology follow-up."""

entities_7 = [
    {"label": "OBS_LESION", "text": "Lung adenocarcinoma", **get_span(text_7, "Lung adenocarcinoma", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_7, "BI", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "obstruction (74%)", **get_span(text_7, "obstruction (74%)", 1)},
    {"label": "PROC_METHOD", "text": "Rigid Bronch", **get_span(text_7, "Rigid Bronch", 1)},
    {"label": "PROC_ACTION", "text": "Mechanical debulking", **get_span(text_7, "Mechanical debulking", 1)},
    {"label": "DEV_INSTRUMENT", "text": "forceps", **get_span(text_7, "forceps", 1)},
    {"label": "OBS_LESION", "text": "Tumor", **get_span(text_7, "Tumor", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "Residual obstruction 12%", **get_span(text_7, "Residual obstruction 12%", 1)},
    {"label": "MEAS_VOL", "text": "75ml", **get_span(text_7, "75ml", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 4229850_syn_8
# ==========================================
text_8 = """We performed a rigid bronchoscopy on [REDACTED] a tumor obstructing his bronchus intermedius. The blockage was approximately 74%. We used rigid biopsy forceps to mechanically excise the tumor tissue piece by piece. We continued this until the obstruction was reduced to 12%. The bleeding was controlled, and we collected sufficient samples for pathology. He was transferred to the ICU for recovery."""

entities_8 = [
    {"label": "PROC_METHOD", "text": "rigid bronchoscopy", **get_span(text_8, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", "text": "tumor", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_AIRWAY", "text": "bronchus intermedius", **get_span(text_8, "bronchus intermedius", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "blockage was approximately 74%", **get_span(text_8, "blockage was approximately 74%", 1)},
    {"label": "DEV_INSTRUMENT", "text": "rigid biopsy forceps", **get_span(text_8, "rigid biopsy forceps", 1)},
    {"label": "PROC_ACTION", "text": "mechanically excise", **get_span(text_8, "mechanically excise", 1)},
    {"label": "OBS_LESION", "text": "tumor", **get_span(text_8, "tumor", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "obstruction was reduced to 12%", **get_span(text_8, "obstruction was reduced to 12%", 1)},
    {"label": "OUTCOME_COMPLICATION", "text": "bleeding was controlled", **get_span(text_8, "bleeding was controlled", 1)},
    {"label": "SPECIMEN", "text": "samples", **get_span(text_8, "samples", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 4229850_syn_9
# ==========================================
text_9 = """Indication: Primary lung adenocarcinoma with CAO.
Pre-procedure: ~74% occlusion at BI.
PROCEDURE: Under general anesthesia, rigid bronchoscopy was conducted. Endobronchial neoplasm detected at BI. Rigid bronchoscopy resection with biopsy forceps was executed with sequential tumor extraction. Multiple passes were done to attain maximal debulking.
Post-procedure: ~12% residual occlusion.
EBL: ~75mL."""

entities_9 = [
    {"label": "OBS_LESION", "text": "lung adenocarcinoma", **get_span(text_9, "lung adenocarcinoma", 1)},
    {"label": "OBS_LESION", "text": "CAO", **get_span(text_9, "CAO", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "~74% occlusion", **get_span(text_9, "~74% occlusion", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_9, "BI", 1)},
    {"label": "PROC_METHOD", "text": "rigid bronchoscopy", **get_span(text_9, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", "text": "Endobronchial neoplasm", **get_span(text_9, "Endobronchial neoplasm", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_9, "BI", 2)},
    {"label": "PROC_METHOD", "text": "Rigid bronchoscopy", **get_span(text_9, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", "text": "resection", **get_span(text_9, "resection", 1)},
    {"label": "DEV_INSTRUMENT", "text": "biopsy forceps", **get_span(text_9, "biopsy forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "~12% residual occlusion", **get_span(text_9, "~12% residual occlusion", 1)},
    {"label": "MEAS_VOL", "text": "~75mL", **get_span(text_9, "~75mL", 1)}
]
BATCH_DATA.append({"id": "4229850_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# Note 10: 4229850
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Michael Chen

Indication: Primary lung adenocarcinoma with CAO
Pre-procedure: ~74% obstruction at BI

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at BI.
Rigid bronchoscopy debulking with biopsy forceps performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Post-procedure: ~12% residual obstruction.
EBL: ~75mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Chen, MD"""

entities_10 = [
    {"label": "OBS_LESION", "text": "lung adenocarcinoma", **get_span(text_10, "lung adenocarcinoma", 1)},
    {"label": "OBS_LESION", "text": "CAO", **get_span(text_10, "CAO", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", "text": "~74% obstruction", **get_span(text_10, "~74% obstruction", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_10, "BI", 1)},
    {"label": "PROC_METHOD", "text": "rigid bronchoscopy", **get_span(text_10, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", "text": "Endobronchial tumor", **get_span(text_10, "Endobronchial tumor", 1)},
    {"label": "ANAT_AIRWAY", "text": "BI", **get_span(text_10, "BI", 2)},
    {"label": "PROC_METHOD", "text": "Rigid bronchoscopy", **get_span(text_10, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", "text": "debulking", **get_span(text_10, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", "text": "biopsy forceps", **get_span(text_10, "biopsy forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", "text": "~12% residual obstruction", **get_span(text_10, "~12% residual obstruction", 1)},
    {"label": "MEAS_VOL", "text": "~75mL", **get_span(text_10, "~75mL", 1)},
    {"label": "OUTCOME_COMPLICATION", "text": "Hemostasis achieved", **get_span(text_10, "Hemostasis achieved", 1)},
    {"label": "SPECIMEN", "text": "Specimens", **get_span(text_10, "Specimens", 1)},
    {"label": "DEV_STENT", "text": "stent", **get_span(text_10, "stent", 1)}
]
BATCH_DATA.append({"id": "4229850", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case['id'], case['text'], case['entities'], REPO_ROOT)