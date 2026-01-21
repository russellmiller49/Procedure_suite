import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
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
# Note 1: 502118_syn_1
# ==========================================
id_s1 = "502118_syn_1"
text_s1 = """Indication: Aspiration (Peanut).
Proc: Foreign Body Removal.
Findings: R main/RLL occluded by nuts.
Action: Basket/Forceps removal piecemeal.
Result: Airways cleared.
Plan: CXR, extubate tomorrow."""
entities_s1 = [
    {"label": "OBS_LESION", **get_span(text_s1, "Peanut", 1)},
    {"label": "OBS_LESION", **get_span(text_s1, "Foreign Body", 1)},
    {"label": "PROC_ACTION", **get_span(text_s1, "Removal", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_s1, "R main", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_s1, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_s1, "nuts", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s1, "Basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s1, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_s1, "removal", 1)}, # Fixed: Changed from 2 to 1 (only one lowercase instance)
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_s1, "Airways cleared", 1)}
]
BATCH_DATA.append({"id": id_s1, "text": text_s1, "entities": entities_s1})

# ==========================================
# Note 2: 502118_syn_2
# ==========================================
id_s2 = "502118_syn_2"
text_s2 = """OPERATIVE SUMMARY: Emergent bronchoscopy was performed for acute airway obstruction. Inspection confirmed a foreign body (peanut fragments) occluding the right mainstem bronchus. Using a retrieval basket and forceps, the foreign material was extracted piecemeal. Following removal, the distal airways were inspected and found to be patent and free of residual debris."""
entities_s2 = [
    {"label": "PROC_ACTION", **get_span(text_s2, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_s2, "foreign body", 1)},
    {"label": "OBS_LESION", **get_span(text_s2, "peanut fragments", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_s2, "right mainstem bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s2, "retrieval basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s2, "forceps", 1)},
    {"label": "OBS_LESION", **get_span(text_s2, "foreign material", 1)},
    {"label": "PROC_ACTION", **get_span(text_s2, "extracted", 1)},
    {"label": "PROC_ACTION", **get_span(text_s2, "removal", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_s2, "patent", 1)}
]
BATCH_DATA.append({"id": id_s2, "text": text_s2, "entities": entities_s2})

# ==========================================
# Note 3: 502118_syn_3
# ==========================================
id_s3 = "502118_syn_3"
text_s3 = """Code: 31635 (Bronchoscopy with removal of foreign body).
Detail: Removal of aspirated organic material from Right Mainstem/RLL using basket and forceps. Complexity: Piecemeal removal required."""
entities_s3 = [
    {"label": "PROC_ACTION", **get_span(text_s3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_s3, "removal", 1)},
    {"label": "OBS_LESION", **get_span(text_s3, "foreign body", 1)},
    {"label": "PROC_ACTION", **get_span(text_s3, "Removal", 1)},
    {"label": "OBS_LESION", **get_span(text_s3, "aspirated organic material", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_s3, "Right Mainstem", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_s3, "RLL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s3, "basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s3, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_s3, "removal", 2)} # "Piecemeal removal"
]
BATCH_DATA.append({"id": id_s3, "text": text_s3, "entities": entities_s3})

# ==========================================
# Note 4: 502118_syn_4
# ==========================================
id_s4 = "502118_syn_4"
text_s4 = """Emergency Bronch Note
Patient: [REDACTED]
1. Intubated for aspiration.
2. Scope down -> Peanut parts in R lung.
3. Used basket and forceps.
4. Pulled out multiple pieces.
5. Suctioned clear.
6. R lung reinflated.
7. Done."""
entities_s4 = [
    {"label": "PROC_ACTION", **get_span(text_s4, "Bronch", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s4, "Scope", 1)},
    {"label": "OBS_LESION", **get_span(text_s4, "Peanut parts", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_s4, "R lung", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s4, "basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s4, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_s4, "Pulled out", 1)},
    {"label": "PROC_ACTION", **get_span(text_s4, "Suctioned", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_s4, "R lung reinflated", 1)}
]
BATCH_DATA.append({"id": id_s4, "text": text_s4, "entities": entities_s4})

# ==========================================
# Note 5: 502118_syn_5
# ==========================================
id_s5 = "502118_syn_5"
text_s5 = """jacob carter choked on a peanut ems intubated him. right lung down. went in with the scope giant peanut mess in the right main. used the basket and grabbers took a while to get it all out in pieces. cleaned it up nicely lung is up now on xray."""
entities_s5 = [
    {"label": "OBS_LESION", **get_span(text_s5, "peanut", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_s5, "right lung", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s5, "scope", 1)},
    {"label": "OBS_LESION", **get_span(text_s5, "peanut mess", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_s5, "right main", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s5, "basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s5, "grabbers", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_s5, "lung is up", 1)}
]
BATCH_DATA.append({"id": id_s5, "text": text_s5, "entities": entities_s5})

# ==========================================
# Note 6: 502118_syn_6
# ==========================================
id_s6 = "502118_syn_6"
text_s6 = """Emergency bronchoscopy for foreign body aspiration. The patient presented with right lung collapse. Bronchoscopy revealed peanut fragments obstructing the right mainstem. These were removed using a combination of basket and forceps. The airway was cleared of all visible foreign material. Ventilation improved immediately."""
entities_s6 = [
    {"label": "PROC_ACTION", **get_span(text_s6, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_s6, "foreign body", 1)},
    {"label": "OBS_FINDING", **get_span(text_s6, "right lung collapse", 1)},
    {"label": "PROC_ACTION", **get_span(text_s6, "Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_s6, "peanut fragments", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_s6, "right mainstem", 1)},
    {"label": "PROC_ACTION", **get_span(text_s6, "removed", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s6, "basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s6, "forceps", 1)},
    {"label": "OBS_LESION", **get_span(text_s6, "foreign material", 1)}
]
BATCH_DATA.append({"id": id_s6, "text": text_s6, "entities": entities_s6})

# ==========================================
# Note 7: 502118_syn_7
# ==========================================
id_s7 = "502118_syn_7"
text_s7 = """[Indication]
Foreign body aspiration, respiratory failure.
[Anesthesia]
General (Propofol/Fentanyl).
[Description]
FB id[REDACTED] (Peanut) R lung. Removal via basket/forceps. Airways patent post-removal.
[Plan]
Wean vent. CXR."""
entities_s7 = [
    {"label": "OBS_LESION", **get_span(text_s7, "Foreign body", 1)},
    {"label": "MEDICATION", **get_span(text_s7, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(text_s7, "Fentanyl", 1)},
    {"label": "OBS_LESION", **get_span(text_s7, "FB", 1)},
    {"label": "OBS_LESION", **get_span(text_s7, "Peanut", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_s7, "R lung", 1)},
    {"label": "PROC_ACTION", **get_span(text_s7, "Removal", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s7, "basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s7, "forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_s7, "Airways patent", 1)}
]
BATCH_DATA.append({"id": id_s7, "text": text_s7, "entities": entities_s7})

# ==========================================
# Note 8: 502118_syn_8
# ==========================================
id_s8 = "502118_syn_8"
text_s8 = """We performed an emergency procedure on [REDACTED] a peanut he inhaled. It was blocking his right lung. Using a small basket and grippers through the scope, we removed the peanut in several pieces. Once it was all out, we suctioned the airway clean, and his lung re-expanded."""
entities_s8 = [
    {"label": "OBS_LESION", **get_span(text_s8, "peanut", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_s8, "right lung", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s8, "basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s8, "grippers", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s8, "scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_s8, "removed", 1)},
    {"label": "OBS_LESION", **get_span(text_s8, "peanut", 2)},
    {"label": "PROC_ACTION", **get_span(text_s8, "suctioned", 1)},
    {"label": "OUTCOME_PLEURAL", **get_span(text_s8, "lung re-expanded", 1)}
]
BATCH_DATA.append({"id": id_s8, "text": text_s8, "entities": entities_s8})

# ==========================================
# Note 9: 502118_syn_9
# ==========================================
id_s9 = "502118_syn_9"
text_s9 = """Procedure: Retrieval of aspirated foreign material.
Target: Right bronchial tree.
Method: Extraction utilizing wire basket and forceps.
Outcome: Restoration of bronchial patency."""
entities_s9 = [
    {"label": "PROC_ACTION", **get_span(text_s9, "Retrieval", 1)},
    {"label": "OBS_LESION", **get_span(text_s9, "aspirated foreign material", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_s9, "Right bronchial tree", 1)},
    {"label": "PROC_ACTION", **get_span(text_s9, "Extraction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s9, "wire basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_s9, "forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_s9, "Restoration of bronchial patency", 1)}
]
BATCH_DATA.append({"id": id_s9, "text": text_s9, "entities": entities_s9})

# ==========================================
# Note 10: 502118 (Original)
# ==========================================
id_orig = "502118"
text_orig = """EMERGENCY BRONCHOSCOPY – FOREIGN BODY
Date: [REDACTED] 21:15
Patient: [REDACTED] | 32M | MRN [REDACTED]
Location: [REDACTED]
Attending: Dr. Alexis Nguyen

INDICATION:
Acute airway obstruction after aspiration of peanut while eating at home. EMS performed rapid sequence intubation en route. Persistent high peak pressures and right lung collapse on portable CXR.

AIRWAY / VENTILATION:
8.0 ETT at 24 cm, volume-control ventilation 18/450/5/100%.
Sedation with propofol and fentanyl infusions (general anesthesia–equivalent).

PROCEDURE:
Flexible bronchoscope was passed through the ETT. A large amount of particulate material was visualized in the right mainstem bronchus with near-complete occlusion and extension into the right lower lobe bronchus.

Using a 4-wire retrieval basket and alligator forceps, multiple peanut fragments were removed piecemeal from the right mainstem and right lower lobe bronchi. Airways were suctioned thoroughly until patent with visible subsegmental branches.

Left lung inspection was normal. No tumor, mass or blood clot id[REDACTED].

COMPLICATIONS: None. Estimated blood loss <5 mL.
PLAN: Repeat portable CXR to confirm re-expansion of the right lung. Continue mechanical ventilation overnight for airway protection."""
entities_orig = [
    {"label": "PROC_ACTION", **get_span(text_orig, "BRONCHOSCOPY", 1)},
    {"label": "OBS_LESION", **get_span(text_orig, "FOREIGN BODY", 1)},
    {"label": "OBS_LESION", **get_span(text_orig, "peanut", 1)},
    {"label": "OBS_FINDING", **get_span(text_orig, "right lung collapse", 1)},
    {"label": "MEDICATION", **get_span(text_orig, "propofol", 1)},
    {"label": "MEDICATION", **get_span(text_orig, "fentanyl", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_orig, "Flexible bronchoscope", 1)},
    {"label": "OBS_LESION", **get_span(text_orig, "particulate material", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_orig, "right mainstem bronchus", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_orig, "right lower lobe bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_orig, "4-wire retrieval basket", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_orig, "alligator forceps", 1)},
    {"label": "OBS_LESION", **get_span(text_orig, "peanut fragments", 1)},
    {"label": "PROC_ACTION", **get_span(text_orig, "removed", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_orig, "right mainstem", 2)}, # "from the right mainstem"
    {"label": "ANAT_AIRWAY", **get_span(text_orig, "right lower lobe bronchi", 1)},
    {"label": "PROC_ACTION", **get_span(text_orig, "suctioned", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_orig, "patent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_orig, "None", 1)}
]
BATCH_DATA.append({"id": id_orig, "text": text_orig, "entities": entities_orig})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)