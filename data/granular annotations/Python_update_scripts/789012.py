import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function to add cases to the dataset
# Assumes the script is located in 'scripts/' and the module is accessible
try:
    from scripts.add_training_case import add_case
except ImportError:
    # Fallback for local testing or if structure differs
    def add_case(case_id, text, entities, root):
        print(f"Adding case {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary suitable for the entity list.
    """
    start_index = -1
    current_occurrence = 0
    
    # Loop to find the correct occurrence
    while current_occurrence < occurrence:
        # Find next instance starting after the previous one
        start_index = text.find(term, start_index + 1)
        
        # If term not found, return None or handle error (here we assume strict checking)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
            
        current_occurrence += 1

    return {
        "span_start": start_index,
        "span_end": start_index + len(term)
    }

# ==========================================
# Note 1: 789012_syn_1
# ==========================================
text_1 = """Indication: Sarcoidosis suspicion.
Proc: Thoracoscopy w/ biopsy.
- 5th ICS.
- Biopsied 4R (x6) and 7 (x4).
- 16Fr chest tube."""

entities_1 = [
    # Indication/Diagnosis
    # "Sarcoidosis" is the disease, but often acts as the indication/lesion context here.
    # However, strictly adhering to OBS_LESION = Mass/Nodule/Adenopathy.
    # "Thoracoscopy" is the procedure, usually implied or captured if it's the method. 
    # Focus on specific actions/anatomy/devices.

    # Anatomy: Entry
    {"label": "ANAT_PLEURA", **get_span(text_1, "5th ICS", 1)},

    # Procedure: Action
    {"label": "PROC_ACTION", **get_span(text_1, "Biopsied", 1)},

    # Anatomy: LN Stations
    {"label": "ANAT_LN_STATION", **get_span(text_1, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_1, "7", 1)},

    # Measurements: Counts
    {"label": "MEAS_COUNT", **get_span(text_1, "x6", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "x4", 1)},

    # Device & Measurements: Chest Tube
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_1, "16Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789012_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 789012_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: Medical thoracoscopy for mediastinal lymph node sampling.
INDICATION: Evaluation of mediastinal adenopathy for sarcoidosis.
DESCRIPTION: Under moderate sedation, the pleural space was accessed. The mediastinal pleura was opened to expose stations 4R and 7. Adequate biopsy specimens were obtained from both sites for histological and microbiological analysis. A 16Fr chest tube was placed."""

entities_2 = [
    # Indication/Findings
    {"label": "OBS_LESION", **get_span(text_2, "mediastinal adenopathy", 1)},

    # Anatomy
    {"label": "ANAT_LN_STATION", **get_span(text_2, "mediastinal lymph node", 1)}, # Generic reference
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural space", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "mediastinal pleura", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "stations 4R", 1)}, # Capturing "stations 4R" or just "4R" - usually strict token.
    # "stations 4R" is not a standard token, usually just "4R". Using "4R".
    {"label": "ANAT_LN_STATION", **get_span(text_2, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_2, "7", 1)},

    # Procedure
    {"label": "PROC_ACTION", **get_span(text_2, "biopsy", 1)},
    {"label": "SPECIMEN", **get_span(text_2, "specimens", 1)}, # "biopsy specimens"

    # Device
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_2, "16Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789012_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 789012_syn_3
# ==========================================
text_3 = """CPT 32606: Thoracoscopy with biopsy of mediastinal lymph nodes.
Nodes: 4R and 7.
Indication: Suspected sarcoidosis.
Specimens: Sent for H&E, cultures, polarized light.
Device: 16Fr chest tube."""

entities_3 = [
    # Procedure
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "mediastinal lymph nodes", 1)},

    # Anatomy
    {"label": "ANAT_LN_STATION", **get_span(text_3, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_3, "7", 1)},

    # Device
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_3, "16Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789012_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 789012_syn_4
# ==========================================
text_4 = """Procedure: Thoracoscopy
1. Sedation.
2. Port 5th ICS.
3. Biopsied 4R and 7.
4. 16Fr tube placed.
No complications."""

entities_4 = [
    # Anatomy
    {"label": "ANAT_PLEURA", **get_span(text_4, "5th ICS", 1)},

    # Procedure
    {"label": "PROC_ACTION", **get_span(text_4, "Biopsied", 1)},
    
    # Anatomy Stations
    {"label": "ANAT_LN_STATION", **get_span(text_4, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_4, "7", 1)},

    # Device
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_4, "16Fr", 1)},
    # "tube" fits generic DEV_CATHETER in context of chest tube
    {"label": "DEV_CATHETER", **get_span(text_4, "tube", 1)},

    # Outcome
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No complications", 1)},
]
BATCH_DATA.append({"id": "789012_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 789012_syn_5
# ==========================================
text_5 = """Robert Jackson sarcoid workup medical thoracoscopy right side 5th ics normal pleura biopsied 4r and 7 good cores sent for cultures too 16fr tube in done."""

entities_5 = [
    # Anatomy/Laterality
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "5th ics", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "normal pleura", 1)},

    # Procedure
    {"label": "PROC_ACTION", **get_span(text_5, "biopsied", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "4r", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_5, "7", 1)},
    {"label": "SPECIMEN", **get_span(text_5, "cores", 1)},

    # Device
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_5, "16fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "tube", 1)},
]
BATCH_DATA.append({"id": "789012_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 789012_syn_6
# ==========================================
text_6 = """Thoracoscopy with mediastinal node sampling. Moderate sedation. Right lateral decubitus. Standard thoracoscopic entry 5th ICS. Normal pleural surfaces. Mediastinal pleura over paratracheal region opened. Large 2.5cm node id[REDACTED] at station 4R. Multiple punch biopsies x6 obtained. Additional sampling from subcarinal region station 7 x4 biopsies. 16Fr chest tube placed."""

entities_6 = [
    # Procedure context
    {"label": "PROC_ACTION", **get_span(text_6, "node sampling", 1)}, # "sampling" implies biopsy/TBNA

    # Anatomy/Position
    {"label": "LATERALITY", **get_span(text_6, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "5th ICS", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Normal pleural surfaces", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "Mediastinal pleura", 1)},
    
    # Target 1
    # "paratracheal region" is an anatomical descriptor for station 4R
    {"label": "ANAT_LN_STATION", **get_span(text_6, "paratracheal region", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "2.5cm", 1)},
    # "node" is vague, but often labeled as ANAT_LN_STATION if no number, or ignored if generic. 
    # Labeling "station 4R".
    {"label": "ANAT_LN_STATION", **get_span(text_6, "station 4R", 1)},
    
    # Action 1
    {"label": "PROC_ACTION", **get_span(text_6, "punch biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "x6", 1)},

    # Target 2
    {"label": "PROC_ACTION", **get_span(text_6, "sampling", 2)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "subcarinal region", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_6, "station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "x4", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 2)},

    # Device
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_6, "16Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789012_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 789012_syn_7
# ==========================================
text_7 = """[Indication]
Suspected Sarcoidosis.
[Anesthesia]
Moderate Sedation.
[Description]
Thoracoscopy. Biopsied 4R and 7. 16Fr tube placed.
[Plan]
Obs."""

entities_7 = [
    # Procedure
    {"label": "PROC_ACTION", **get_span(text_7, "Biopsied", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_7, "7", 1)},

    # Device
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_7, "16Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_7, "tube", 1)},
]
BATCH_DATA.append({"id": "789012_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 789012_syn_8
# ==========================================
text_8 = """[REDACTED] confirmation for suspected sarcoidosis. We performed a thoracoscopy with sedation. We found enlarged lymph nodes in the chest and took several samples from two different locations. These will be tested for sarcoidosis and infections. A chest tube was placed at the end."""

entities_8 = [
    # Findings ("enlarged lymph nodes" acts as lesion/indication)
    {"label": "OBS_LESION", **get_span(text_8, "enlarged lymph nodes", 1)},
    
    # Procedure
    {"label": "PROC_ACTION", **get_span(text_8, "samples", 1)},
    
    # Device
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789012_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 789012_syn_9
# ==========================================
text_9 = """Diagnosis: Mediastinal adenopathy (Sarcoidosis).
Action: Thoracoscopic nodal sampling.
Details: Nodes at 4R and 7 harvested. Drain inserted."""

entities_9 = [
    # Indication
    {"label": "OBS_LESION", **get_span(text_9, "Mediastinal adenopathy", 1)},

    # Procedure
    {"label": "PROC_ACTION", **get_span(text_9, "nodal sampling", 1)},

    # Anatomy
    {"label": "ANAT_LN_STATION", **get_span(text_9, "4R", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_9, "7", 1)},
    
    # Device
    {"label": "DEV_CATHETER", **get_span(text_9, "Drain", 1)},
]
BATCH_DATA.append({"id": "789012_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# Note 10: 789012
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Lisa Park

Dx: Suspected sarcoidosis with extensive mediastinal and hilar adenopathy
Procedure: Thoracoscopy with mediastinal node sampling

Hx: 70M with fatigue, dry cough. CT showed bilateral hilar and mediastinal adenopathy. Bronchoscopy with EBUS limited by poor access to enlarged nodes. Decision made for thoracoscopic sampling.

Procedure:
Moderate sedation with propofol/fentanyl. Right lateral decubitus. Standard thoracoscopic entry 5th ICS. Normal pleural surfaces. Mediastinal pleura over paratracheal region opened. Large 2.5cm node id[REDACTED] at station 4R. Multiple punch biopsies (x6) obtained with excellent tissue.

Additional sampling from subcarinal region (station 7, x4 biopsies).

No significant bleeding. 16Fr chest tube placed. Patient tolerated well.

Specimens to path for H&E, AFB, fungal stains, and polarized light.

L. Park MD"""

entities_10 = [
    # Header/Dx
    {"label": "OBS_LESION", **get_span(text_10, "mediastinal and hilar adenopathy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "mediastinal node sampling", 1)},

    # History (Historical Context)
    {"label": "LATERALITY", **get_span(text_10, "bilateral", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "hilar and mediastinal adenopathy", 1)},
    # "Bronchoscopy with EBUS" is prior history here
    {"label": "CTX_HISTORICAL", **get_span(text_10, "Bronchoscopy", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_10, "EBUS", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "enlarged nodes", 1)},
    
    # Plan/Current Procedure
    {"label": "PROC_ACTION", **get_span(text_10, "sampling", 2)}, # "thoracoscopic sampling"

    # Procedure Detail
    {"label": "MEDICATION", **get_span(text_10, "propofol", 1)},
    {"label": "MEDICATION", **get_span(text_10, "fentanyl", 1)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "5th ICS", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Normal pleural surfaces", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "Mediastinal pleura", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "paratracheal region", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "2.5cm", 1)},
    # "node" is target, but "station 4R" is specific location
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 4R", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "punch biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x6", 1)},

    # Second target
    {"label": "PROC_ACTION", **get_span(text_10, "sampling", 3)}, # "Additional sampling"
    {"label": "ANAT_LN_STATION", **get_span(text_10, "subcarinal region", 1)},
    {"label": "ANAT_LN_STATION", **get_span(text_10, "station 7", 1)},
    {"label": "MEAS_COUNT", **get_span(text_10, "x4", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},

    # Completion
    {"label": "MEAS_PLEURAL_DRAIN", **get_span(text_10, "16Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
]
BATCH_DATA.append({"id": "789012", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)