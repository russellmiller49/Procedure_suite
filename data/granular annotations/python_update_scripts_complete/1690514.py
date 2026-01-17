import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Error: Could not import 'add_case' from 'scripts.add_training_case'. Make sure the script is run from the correct directory.")
    sys.exit(1)

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of a term in the text based on its occurrence.
    
    Args:
        text (str): The text to search within.
        term (str): The exact term to search for.
        occurrence (int): The 1-based occurrence index of the term.
        
    Returns:
        dict: A dictionary with "start" and "end" indices.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Case 1: 1690514_syn_1
# ==========================================
text_1 = """Procedure: Bronchoscopy (Stent Check).
- Findings: LMS stent in good position. Mucus plugging.
- Action: Toilet/suction. Mild granulation (no tx needed).
- Plan: Antibiotics, f/u 4 weeks."""

entities_1 = [
    {"label": "PROC_METHOD", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "LMS", 1)},
    {"label": "DEV_STENT", **get_span(text_1, "stent", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Mucus plugging", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Toilet", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "suction", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Mild granulation", 1)},
    {"label": "MEDICATION", **get_span(text_1, "Antibiotics", 1)},
    {"label": "CTX_TIME", **get_span(text_1, "4 weeks", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Case 2: 1690514_syn_2
# ==========================================
text_2 = """PROCEDURE NOTE: Surveillance bronchoscopy was performed to evaluate the left mainstem silicone stent. The stent was found to be in situ with no migration. Significant secretion burden was noted and cleared via therapeutic aspiration. Mild proximal granulation tissue was observed but did not require intervention. Patency is preserved."""

entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "left mainstem", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_2, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "stent", 1)},
    {"label": "DEV_STENT", **get_span(text_2, "stent", 2)},
    {"label": "OBS_FINDING", **get_span(text_2, "secretion burden", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "therapeutic aspiration", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "Mild proximal granulation tissue", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "Patency is preserved", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Case 3: 1690514_syn_3
# ==========================================
text_3 = """CPT: 31645 (Therapeutic aspiration) or 31622 (Dx). *Note: Registry says 31645.* Procedure involved extensive suctioning of secretions from stent. No destruction or excision performed."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Therapeutic aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "suctioning", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "secretions", 1)},
    {"label": "DEV_STENT", **get_span(text_3, "stent", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Case 4: 1690514_syn_4
# ==========================================
text_4 = """Stent Check Note
1. Flex scope via trach.
2. LMS stent looks good, not moving.
3. Suctioned thick secretions.
4. Mild granulation, left alone.
5. Airway patent.
Plan: Azithromycin."""

entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Flex scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "trach", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "LMS", 1)},
    {"label": "DEV_STENT", **get_span(text_4, "stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Suctioned", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "thick secretions", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Mild granulation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "Airway", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "patent", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Azithromycin", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Case 5: 1690514_syn_5
# ==========================================
text_5 = """checking [REDACTED]. went in through the trach. stent is sitting fine. lot of mucus though so i spent some time cleaning it out. little bit of granulation tissue but not blocking anything. gave her some antibiotics."""

entities_5 = [
    {"label": "ANAT_AIRWAY", **get_span(text_5, "trach", 1)},
    {"label": "DEV_STENT", **get_span(text_5, "stent", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "mucus", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "cleaning it out", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "granulation tissue", 1)},
    {"label": "MEDICATION", **get_span(text_5, "antibiotics", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Case 6: 1690514_syn_6
# ==========================================
text_6 = """Bronchoscopy for stent surveillance was performed. The patient has a left mainstem Dumon stent. Findings included mucous buildup and mild granulation tissue. Aggressive suctioning was performed. The stent remains patent. The patient was started on azithromycin."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "left mainstem", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_6, "Dumon", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "stent", 2)},
    {"label": "OBS_FINDING", **get_span(text_6, "mucous buildup", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "mild granulation tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "suctioning", 1)},
    {"label": "DEV_STENT", **get_span(text_6, "stent", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "patent", 1)},
    {"label": "MEDICATION", **get_span(text_6, "azithromycin", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Case 7: 1690514_syn_7
# ==========================================
text_7 = """[Indication]
Airway Stent Surveillance.
[Anesthesia]
Moderate.
[Description]
LMS stent inspected. Secretions cleared (Therapeutic Aspiration). Position stable.
[Plan]
Follow up 4 weeks."""

entities_7 = [
    {"label": "ANAT_AIRWAY", **get_span(text_7, "Airway", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "Stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "LMS", 1)},
    {"label": "DEV_STENT", **get_span(text_7, "stent", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "inspected", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "Secretions", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "cleared", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Therapeutic Aspiration", 1)},
    {"label": "CTX_TIME", **get_span(text_7, "4 weeks", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Case 8: 1690514_syn_8
# ==========================================
text_8 = """[REDACTED] for a check-up on her airway stent. We took a look with the bronchoscope and found the stent was holding its position well, but there was a fair amount of mucus built up inside. We cleaned that out thoroughly. There's a little bit of granulation tissue forming, but it's not causing a problem yet, so we'll just watch it."""

entities_8 = [
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "stent", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "bronchoscope", 1)},
    {"label": "DEV_STENT", **get_span(text_8, "stent", 2)},
    {"label": "OBS_FINDING", **get_span(text_8, "mucus built up", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "cleaned that out", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "granulation tissue", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Case 9: 1690514_syn_9
# ==========================================
text_9 = """Procedure: Endoscopic prosthesis evaluation.
Findings: Stent in situ. Retained secretions.
Intervention: Therapeutic aspiration/toilet.
Outcome: Patency maintained."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Endoscopic", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "prosthesis", 1)},
    {"label": "DEV_STENT", **get_span(text_9, "Stent", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "Retained secretions", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Therapeutic aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "toilet", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "Patency maintained", 1)},
]
BATCH_DATA.append({"id": "1690514_syn_9", "text": text_9, "entities": entities_9})

# ==========================================
# Case 10: 1690514
# ==========================================
text_10 = """Bronchoscopy Note
Patient: [REDACTED], 58 yo female
Date: [REDACTED]
Doc: Dr. Steven Park
MRN: [REDACTED]
So [REDACTED] today for her routine stent check. She's about 3 months out from when we placed that 14mm Dumon silicone stent in her left mainstem for malignant compression from lung cancer. She's been doing pretty well overall, no new dyspnea, though she mentioned maybe a bit more cough the last week or so.
Brought her over to the procedure room, gave her moderate sedation with the usual versed and fentanyl, topped up with some propofol. Once she was comfortable we got the scope in through her trach (she ended up needing a trach about 2 weeks after the stent because of overall disease progression).
So here's what I found: The trachea above the stent looks okay, maybe a touch more secretions than last time but nothing crazy. The stent itself is still in good position - hasn't migrated at all which is great. But there's definitely more mucous buildup than I'd like to see. Spent a good 10 minutes doing aggressive suctioning and toilet of the stent lumen. Got a bunch of thick tan-colored secretions out.
After cleaning it out I could see the proximal end of the stent has some mild granulation tissue forming - maybe 10% of the circumference, not enough to cause obstruction yet but something we'll need to watch. Thought about hitting it with APC today but honestly it wasn't causing any flow limitation so I decided to just keep an eye on it.
The distal end of the stent is sitting right where it should be. I could see the LUL and LLL takeoffs through the stent - both still patent. The tumor outside the stent looks about the same as last time, maybe slightly more bulky but hard to say. Stent is doing its job keeping the airway open though, I'd estimate we still have about 80% patency which is solid.
Did a quick peek at the right side while I was in there - everything looks normal, no new issues.
Recommendations going forward: I think we need to bring her back a bit sooner than usual, maybe 4 weeks instead of 8, just to make sure that granulation tissue doesn't get out of hand. Also talked to her about increasing her nebulizer treatments to help keep secretions looser. Started her on a 5 day course of azithromycin since the secretions looked a bit purulent.
Overall I'm happy with how the stent is functioning. The main challenge is going to be managing secretion burden and staying on top of any granulation tissue. Patient tolerated the procedure well, no complications, she'll follow up with me in 4 weeks."""

entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "3 months", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "14mm", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "Dumon", 1)},
    {"label": "DEV_STENT_MATERIAL", **get_span(text_10, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "left mainstem", 1)},
    {"label": "MEDICATION", **get_span(text_10, "versed", 1)},
    {"label": "MEDICATION", **get_span(text_10, "fentanyl", 1)},
    {"label": "MEDICATION", **get_span(text_10, "propofol", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "scope", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trach", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trach", 2)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 3)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 4)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretions", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 5)},
    {"label": "OBS_FINDING", **get_span(text_10, "mucous buildup", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "suctioning", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "toilet", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 6)},
    {"label": "OBS_FINDING", **get_span(text_10, "thick tan-colored secretions", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "cleaning it out", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 7)},
    {"label": "OBS_FINDING", **get_span(text_10, "mild granulation tissue", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 8)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 9)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 1)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 10)},
    {"label": "DEV_STENT", **get_span(text_10, "Stent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "80% patency", 1)},
    {"label": "CTX_TIME", **get_span(text_10, "4 weeks", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "granulation tissue", 2)},
    {"label": "MEDICATION", **get_span(text_10, "azithromycin", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretions", 2)},
    {"label": "DEV_STENT", **get_span(text_10, "stent", 11)},
    {"label": "OBS_FINDING", **get_span(text_10, "secretion burden", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "granulation tissue", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "no complications", 1)},
]
BATCH_DATA.append({"id": "1690514", "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)