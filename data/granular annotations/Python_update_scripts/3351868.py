import sys
from pathlib import Path

# Set up the repository root path (assuming script is run from a subfolder or root)
# Adjust this logic as needed for your specific environment structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the repository root to sys.path to allow imports
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for.
        occurrence (int): The 1-based occurrence number.
    
    Returns:
        dict: A dictionary with 'start' and 'end' keys, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3351868_syn_1
# ==========================================
text_1 = """Indication: Post-PDT Debridement (48h).
Procedure: Bronchoscopy, Debridement.
Findings: LUL necrosis. 74% obstructed -> 5% post-debridement.
Tools: Forceps, Rigid Coring, Cryoprobe.
Specimen: None.
Plan: Surveillance 6 wks."""

entities_1 = [
    {"label": "CTX_HISTORICAL", **get_span(text_1, "Post-PDT", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Debridement", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "48h", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Debridement", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "necrosis", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "74% obstructed", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "5% post-debridement", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Rigid Coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Cryoprobe", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "6 wks", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 3351868_syn_2
# ==========================================
text_2 = """OPERATIVE SUMMARY: [REDACTED] of the left upper lobe 48 hours after PDT light application. The airway was heavily obstructed by necrotic coagulum. We employed a multimodal approach using biopsy forceps, rigid coring, and cryotherapy to extract the adherent debris. This resulted in near-complete restoration of airway patency (5% residual obstruction). The procedure was well-tolerated."""

entities_2 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "left upper lobe", 1)},
    {"label": "CTX_TIME", **get_span(text_2, "48 hours", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_2, "after PDT", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "airway", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "necrotic coagulum", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "biopsy forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "rigid coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "cryotherapy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "extract", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "debris", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "airway", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "5% residual obstruction", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 3351868_syn_3
# ==========================================
text_3 = """Procedure: 31641 (Tumor Destruction/Debridement).
Site: Left Upper Lobe (LUL).
Tools: Forceps, Coring, Cryotherapy.
Complexity: Multimodal debridement required for adherent tissue.
Outcome: Obstruction reduced from 74% to 5%.
Note: Cryo used for debridement, not biopsy."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Tumor Destruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Debridement", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Left Upper Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Cryotherapy", 1)},
    # Fixed occurrences for "debridement" (lowercase). 
    # Occurrence 1 is in "Multimodal debridement"
    # Occurrence 2 is in "Cryo used for debridement"
    {"label": "PROC_ACTION", **get_span(text_3, "debridement", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "74%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "5%", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Cryo", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "debridement", 2)},
]
BATCH_DATA.append({"id": "3351868_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 3351868_syn_4
# ==========================================
text_4 = """Procedure: PDT Debridement
Pt: [REDACTED]
1. GA.
2. LUL inspection.
3. Necrosis debrided with forceps, coring, and cryo.
4. Airway wide open (5%).
5. No bleeding.
Plan: F/u 6 weeks."""

entities_4 = [
    {"label": "CTX_HISTORICAL", **get_span(text_4, "PDT", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Debridement", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "inspection", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Necrosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "debrided", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "cryo", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "5%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "No bleeding", 1)},
    {"label": "CTX_TIME", **get_span(text_4, "6 weeks", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 3351868_syn_5
# ==========================================
text_5 = """[REDACTED] for lul debridement 2 days after pdt lots of necrosis stuck pretty hard used everything forceps coring and the cryoprobe got it all out looks great 5 percent obstruction left patient did fine"""

entities_5 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lul", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "debridement", 1)},
    {"label": "CTX_TIME", **get_span(text_5, "2 days", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_5, "pdt", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "necrosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "coring", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "cryoprobe", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "5 percent obstruction", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 3351868_syn_6
# ==========================================
text_6 = """Debridement of the LUL was performed 48 hours post-PDT. Necrotic debris was removed using a combination of forceps, rigid coring, and cryotherapy. Airway obstruction improved from 74% to 5%. No biopsies were taken. The patient was stable and extubated."""

entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "Debridement", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "CTX_TIME", **get_span(text_6, "48 hours", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_6, "post-PDT", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "Necrotic debris", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "rigid coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "cryotherapy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "74%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "5%", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 3351868_syn_7
# ==========================================
text_7 = """[Indication]
Post-PDT Debridement (48h), LUL.
[Anesthesia]
General, 7.5 ETT.
[Description]
Necrosis debrided via forceps, coring, cryo. Airway patent. No biopsies.
[Plan]
Surveillance 6 weeks."""

entities_7 = [
    {"label": "CTX_HISTORICAL", **get_span(text_7, "Post-PDT", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Debridement", 1)},
    {"label": "CTX_TIME", **get_span(text_7, "48h", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Necrosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "debrided", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "cryo", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "Airway", 1)},
    {"label": "CTX_TIME", **get_span(text_7, "6 weeks", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 3351868_syn_8
# ==========================================
text_8 = """[REDACTED] significant cleaning 48 hours after his light treatment. The dead tissue was pretty stuck, so we had to use forceps, the coring tool, and the cryoprobe to get it all out. It worked perfectly though—the airway is basically completely open now. We didn't take biopsies this time. He's doing well."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "cleaning", 1)},
    {"label": "CTX_TIME", **get_span(text_8, "48 hours", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_8, "light treatment", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "dead tissue", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "forceps", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "coring tool", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "cryoprobe", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 3351868_syn_9
# ==========================================
text_9 = """PROCEDURES: 1. Bronchoscopy with extraction of necrotic tissue.
DETAILS: The LUL was assessed. Necrotic material was adherent. Forceps, coring, and cryotherapy were utilized to clear the passage. Patency was restored to near normal. No tissue samples were taken. The patient was recovered."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "extraction", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "necrotic tissue", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LUL", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Necrotic material", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "coring", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "cryotherapy", 1)},
]
BATCH_DATA.append({"id": "3351868_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)