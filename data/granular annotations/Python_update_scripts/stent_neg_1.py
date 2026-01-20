import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the n-th occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==============================================================================
# Synthetic Case Set: NEG_STENT vs. CTX_STENT_PRESENT vs. DEV_STENT
# ==============================================================================

# Case 1: Explicit negation (No stent placed)
t1 = """Airway inspection revealed 40% stenosis in the mid-trachea. 
Balloon dilation was performed with a 14mm CRE balloon. 
Post-dilation inspection showed widely patent airway. 
No stent was placed due to sufficient patency."""
e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "40% stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "mid-trachea", 1)},
    {"label": "PROC_METHOD", **get_span(t1, "Balloon dilation", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "CRE balloon", 1)},
    {"label": "NEG_STENT", **get_span(t1, "No stent", 1)},
]
BATCH_DATA.append((t1, e1))

# Case 2: Negation via "Not indicated"
t2 = """Central airway obstruction was ruled out. 
The right mainstem was clear. 
Stent placement was not indicated at this time. 
Procedure terminated."""
e2 = [
    {"label": "OBS_FINDING", **get_span(t2, "Central airway obstruction", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "right mainstem", 1)},
    {"label": "NEG_STENT", **get_span(t2, "Stent", 1)},
]
BATCH_DATA.append((t2, e2))

# Case 3: Negation via "Deferred"
t3 = """Tumor debulking was successful using APC and forceps. 
Airway lumen improved to 80%. 
Airway stent deployment was deferred pending pathology results."""
e3 = [
    {"label": "PROC_METHOD", **get_span(t3, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t3, "forceps", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t3, "improved to 80%", 1)},
    {"label": "NEG_STENT", **get_span(t3, "Airway stent", 1)},
]
BATCH_DATA.append((t3, e3))

# Case 4: Discussion but no action
t4 = """We discussed the risks and benefits of silicone stents. 
The patient opted for conservative management. 
Therefore, without stent placement, we concluded the case."""
e4 = [
    {"label": "NEG_STENT", **get_span(t4, "silicone stents", 1)},
    {"label": "NEG_STENT", **get_span(t4, "stent", 2)},
]
BATCH_DATA.append((t4, e4))

# Case 5: Contrast - Stent REMOVAL (DEV_STENT) vs New Stent (NEG_STENT)
t5 = """The existing metallic stent was fractured and causing granulation. 
We successfully removed the stent using rigid forceps. 
The mucosa was cauterized. 
No new stent was inserted."""
e5 = [
    {"label": "DEV_STENT", **get_span(t5, "metallic stent", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "fractured", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "removed", 1)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 2)},
    {"label": "NEG_STENT", **get_span(t5, "stent", 3)},
]
BATCH_DATA.append((t5, e5))

# Case 6: CTX_STENT_PRESENT (Background)
t6 = """Patient presents for surveillance. 
Previous Dumon stent in the left mainstem appears patent. 
Secretions were cleared from the stent lumen. 
No migration noted."""
e6 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t6, "Dumon stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t6, "left mainstem", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "cleared", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t6, "stent", 2)},
]
BATCH_DATA.append((t6, e6))

# Case 7: Equipment confusion (Stent Sizer)
t7 = """Sizing was performed to estimate airway diameter. 
The stent sizer was passed through the vocal cords. 
Measurements indicated 12mm diameter. 
Stent not placed due to extensive necrosis."""
e7 = [
    {"label": "DEV_INSTRUMENT", **get_span(t7, "stent sizer", 1)},
    # Fixed: "Stent" occurs only once with capital S in t7
    {"label": "NEG_STENT", **get_span(t7, "Stent", 1)}, 
]
BATCH_DATA.append((t7, e7))

# Case 8: "Free of" negation
t8 = """Inspection of the distal trachea showed healthy mucosa. 
The bronchial tree was free of stents or foreign bodies. 
BAL was performed in the RUL."""
e8 = [
    {"label": "NEG_STENT", **get_span(t8, "stents", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "BAL", 1)},
]
BATCH_DATA.append((t8, e8))

# Case 9: "Ruled out" negation
t9 = """Consult for airway compromise. 
Bronchoscopy ruled out need for stent. 
Laser resection was sufficient to restore airflow."""
e9 = [
    {"label": "NEG_STENT", **get_span(t9, "stent", 1)},
    {"label": "PROC_METHOD", **get_span(t9, "Laser resection", 1)},
]
BATCH_DATA.append((t9, e9))

# Case 10: Mixed Context (Removal + No Replacement)
t10 = """The migrated silicone Y-stent was grasped and removed. 
Inspection revealed malacia but adequate caliber. 
Decision made to leave airway stent-free."""
e10 = [
    {"label": "DEV_STENT", **get_span(t10, "silicone Y-stent", 1)},
    {"label": "PROC_METHOD", **get_span(t10, "removed", 1)},
    {"label": "NEG_STENT", **get_span(t10, "stent", 2)},
]
BATCH_DATA.append((t10, e10))

# Case 11: Complex list with negation
t11 = """Plan: 
1. Surveillance bronchoscopy. 
2. APC of granulation tissue. 
3. No stent placement anticipated."""
e11 = [
    {"label": "PROC_METHOD", **get_span(t11, "APC", 1)},
    {"label": "NEG_STENT", **get_span(t11, "stent", 1)},
]
BATCH_DATA.append((t11, e11))

# Case 12: "Withheld" negation
t12 = """Given the active infection, therapeutic stenting was withheld. 
Antibiotics were initiated. 
Re-evaluation planned in 2 weeks."""
e12 = [
    {"label": "NEG_STENT", **get_span(t12, "stenting", 1)},
    {"label": "MEDICATION", **get_span(t12, "Antibiotics", 1)},
]
BATCH_DATA.append((t12, e12))

# Case 13: Technical failure negation (Rare but useful)
t13 = """Attempted to deploy 14x40mm stent but device malfunctioned. 
Device removed. 
Procedure aborted without successful stent deployment."""
e13 = [
    {"label": "DEV_STENT", **get_span(t13, "stent", 1)},
    {"label": "NEG_STENT", **get_span(t13, "stent", 2)},
]
BATCH_DATA.append((t13, e13))

# Case 14: Equipment adjective (Stent Loader)
t14 = """The stent loader was inspected and found to be defective. 
A new delivery system was requested. 
Ultimately, no stent was used."""
e14 = [
    {"label": "DEV_INSTRUMENT", **get_span(t14, "stent loader", 1)},
    {"label": "NEG_STENT", **get_span(t14, "stent", 2)},
]
BATCH_DATA.append((t14, e14))

# Case 15: "Avoided" negation
t15 = """To preserve mucociliary clearance, we avoided stenting the distal airway. 
Simple balloon dilation was effective."""
e15 = [
    {"label": "NEG_STENT", **get_span(t15, "stenting", 1)},
    {"label": "PROC_METHOD", **get_span(t15, "balloon dilation", 1)},
]
BATCH_DATA.append((t15, e15))

# Case 16: Trial negation
t16 = """Stent trial was discussed but declined by patient. 
Will proceed with serial dilations instead."""
e16 = [
    {"label": "NEG_STENT", **get_span(t16, "Stent", 1)},
    {"label": "PROC_METHOD", **get_span(t16, "serial dilations", 1)},
]
BATCH_DATA.append((t16, e16))

# Case 17: Post-removal status
t17 = """Following extraction of the foreign body, the airway was examined. 
No granulation seen. 
No stent required."""
e17 = [
    {"label": "OBS_FINDING", **get_span(t17, "foreign body", 1)},
    {"label": "NEG_STENT", **get_span(t17, "stent", 1)},
]
BATCH_DATA.append((t17, e17))

# Case 18: "Sparing"
t18 = """Carina was spared. 
RMB and LMB patent. 
Stent sparing strategy was employed successfully."""
e18 = [
    {"label": "NEG_STENT", **get_span(t18, "Stent", 1)},
]
BATCH_DATA.append((t18, e18))

# Case 19: Long range negation
t19 = """Despite the malacia, the patient remains asymptomatic. 
We will continue to observe without intervention or stenting."""
e19 = [
    {"label": "OBS_FINDING", **get_span(t19, "malacia", 1)},
    {"label": "NEG_STENT", **get_span(t19, "stenting", 1)},
]
BATCH_DATA.append((t19, e19))

# Case 20: Explicit Deferral
t20 = """Airway is stable. 
Stent placement deferred indefinitely."""
e20 = [
    {"label": "NEG_STENT", **get_span(t20, "Stent", 1)},
]
BATCH_DATA.append((t20, e20))


# ==============================================================================
# Execute Batch Addition
# ==============================================================================

if __name__ == "__main__":
    # Signature: add_case(note_id, raw_text, entities, repo_root)
    source_id = Path(__file__).name
    for idx, (text, entities) in enumerate(BATCH_DATA, start=1):
        note_id = f"{source_id}#{idx:03d}"
        add_case(note_id, text, entities, REPO_ROOT)

    print(f"Successfully added {len(BATCH_DATA)} training cases with NEG_STENT labels.")
