import sys
from pathlib import Path

# Set up the repository root directory (Adjust if your folder structure is different)
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
# Synthetic Case Set: CTX_STENT_PRESENT (Existing Stents)
# ==============================================================================

# Case 1: Routine surveillance of an existing stent
t1 = """Patient presents for surveillance bronchoscopy. 
The previously placed tracheal stent was inspected. 
It appears patent with no granulation tissue at the distal end. 
Secretions were cleared from the stent lumen."""
e1 = [
    {"label": "PROC_METHOD", **get_span(t1, "surveillance bronchoscopy", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t1, "tracheal stent", 1)}, # "previously placed" context
    {"label": "OBS_FINDING", **get_span(t1, "patent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t1, "stent", 2)}, # Reference to existing object
]
BATCH_DATA.append((t1, e1))

# Case 2: Stent migration (Existing stent moved)
t2 = """Upon entry, the metallic stent was found to have migrated distally. 
The proximal edge of the stent was now covering the RUL orifice. 
We grasped the stent edge to reposition it."""
e2 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t2, "metallic stent", 1)}, # Found upon entry
    {"label": "OBS_FINDING", **get_span(t2, "migrated", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t2, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "RUL orifice", 1)},
    {"label": "DEV_STENT", **get_span(t2, "stent", 3)}, # Object of active manipulation (borderline, but usually DEV_STENT if manipulated)
]
BATCH_DATA.append((t2, e2))

# Case 3: Granulation tissue around old stent
t3 = """Significant granulation tissue was noted at the proximal aspect of the silicone stent. 
APC was applied to the granulation. 
The stent itself remains intact."""
e3 = [
    {"label": "OBS_FINDING", **get_span(t3, "granulation tissue", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t3, "silicone stent", 1)},
    {"label": "PROC_METHOD", **get_span(t3, "APC", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t3, "stent", 2)},
]
BATCH_DATA.append((t3, e3))

# Case 4: Cleaning an obstructed stent
t4 = """The patient has a history of malignant airway obstruction. 
The indwelling stent was 80% occluded with mucus plugging. 
Therapeutic aspiration was performed to clear the stent."""
e4 = [
    {"label": "OBS_FINDING", **get_span(t4, "malignant airway obstruction", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t4, "indwelling stent", 1)}, # "indwelling" = existing
    {"label": "OBS_FINDING", **get_span(t4, "occluded", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "Therapeutic aspiration", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t4, "stent", 2)},
]
BATCH_DATA.append((t4, e4))

# Case 5: Stent removal (Transition from CTX to Action)
t5 = """The temporary stent has been in place for 6 weeks. 
Inspection showed good mucosal healing behind the stent. 
The stent was then grasped with rigid forceps and removed."""
e5 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t5, "temporary stent", 1)}, # Context describing state
    {"label": "CTX_STENT_PRESENT", **get_span(t5, "stent", 2)},
    {"label": "DEV_STENT", **get_span(t5, "stent", 3)}, # Object of the removal action
    {"label": "PROC_METHOD", **get_span(t5, "removed", 1)},
]
BATCH_DATA.append((t5, e5))

# Case 6: Multiple existing stents (Y-stent)
t6 = """Examination of the carina revealed the silicone Y-stent in proper position. 
Both the right limb and left limb of the stent were patent. 
No intervention required."""
e6 = [
    {"label": "ANAT_AIRWAY", **get_span(t6, "carina", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t6, "silicone Y-stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t6, "stent", 2)},
]
BATCH_DATA.append((t6, e6))

# Case 7: Fracture of existing stent
t7 = """Bronchoscopy demonstrated a fractured metallic stent in the LMB. 
A wire strut from the stent was protruding into the airway lumen. 
It was trimmed using laser."""
e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "fractured", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t7, "metallic stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "LMB", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t7, "stent", 2)},
]
BATCH_DATA.append((t7, e7))

# Case 8: Stent-within-stent (Complex)
t8 = """Recurrent tumor ingrowth was seen through the mesh of the uncovered stent. 
We decided to place a new covered stent inside the existing stent to seal the tumor."""
e8 = [
    {"label": "OBS_FINDING", **get_span(t8, "tumor ingrowth", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t8, "uncovered stent", 1)}, # The old one
    {"label": "DEV_STENT", **get_span(t8, "covered stent", 1)}, # The new one being placed
    {"label": "CTX_STENT_PRESENT", **get_span(t8, "stent", 3)}, # The old one again
]
BATCH_DATA.append((t8, e8))

# Case 9: History/Context only
t9 = """Patient s/p stent placement 3 months ago. 
Current exam shows the stent is well-epithelialized. 
Airway caliber is maintained."""
e9 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t9, "stent", 1)}, # Referring to the history/object
    {"label": "CTX_STENT_PRESENT", **get_span(t9, "stent", 2)},
]
BATCH_DATA.append((t9, e9))

# Case 10: Comparison (Stent vs Anatomy)
t10 = """The proximal trachea is normal. 
The mid-tracheal stent is patent. 
The distal trachea beyond the stent shows mild malacia."""
e10 = [
    {"label": "ANAT_AIRWAY", **get_span(t10, "proximal trachea", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t10, "mid-tracheal stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "distal trachea", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t10, "stent", 2)},
]
BATCH_DATA.append((t10, e10))

# Case 11: Halitosis / Infection source
t11 = """Patient complains of bad breath. 
Inspection revealed food particles trapped behind the stent. 
Lavage was performed around the stent exterior."""
e11 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t11, "stent", 1)},
    {"label": "PROC_METHOD", **get_span(t11, "Lavage", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t11, "stent", 2)},
]
BATCH_DATA.append((t11, e11))

# Case 12: Size mismatch (Existing)
t12 = """The previously deployed 14mm stent appears undersized. 
It is loose within the airway. 
We will plan for removal and replacement with a larger stent."""
e12 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t12, "14mm stent", 1)},
    {"label": "OBS_FINDING", **get_span(t12, "loose", 1)},
    {"label": "DEV_STENT", **get_span(t12, "stent", 2)}, # Future plan/replacement object
]
BATCH_DATA.append((t12, e12))

# Case 13: Mucostasis
t13 = """Thick secretions were noted adhering to the inner wall of the stent. 
Saline flush was used to clean the stent surface."""
e13 = [
    {"label": "OBS_FINDING", **get_span(t13, "Thick secretions", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t13, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t13, "stent", 2)},
]
BATCH_DATA.append((t13, e13))

# Case 14: Overlap
t14 = """The distal end of the tracheal stent overlaps with the proximal end of the bronchial stent. 
This overlap region is patent."""
e14 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t14, "tracheal stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t14, "bronchial stent", 1)},
]
BATCH_DATA.append((t14, e14))

# Case 15: Degradation
t15 = """The bioabsorbable stent placed 4 months ago is largely dissolved. 
Only fragments of the stent structure remain visible."""
e15 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t15, "bioabsorbable stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t15, "stent", 2)},
]
BATCH_DATA.append((t15, e15))

# Case 16: Hybrid stent
t16 = """The hybrid stent shows good incorporation into the airway wall. 
No signs of rejection or infection around the stent."""
e16 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t16, "hybrid stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t16, "stent", 2)},
]
BATCH_DATA.append((t16, e16))

# Case 17: Fistula coverage
t17 = """The TE fistula is fully covered by the esophageal stent. 
We inspected the airway side of the stent and found no leak."""
e17 = [
    {"label": "OBS_FINDING", **get_span(t17, "TE fistula", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t17, "esophageal stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t17, "stent", 2)},
]
BATCH_DATA.append((t17, e17))

# Case 18: Hourglass deformity
t18 = """The stent has developed an hourglass deformity in the center. 
Balloon dilation was performed within the stent to expand it."""
e18 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t18, "stent", 1)},
    {"label": "PROC_METHOD", **get_span(t18, "Balloon dilation", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t18, "stent", 2)},
]
BATCH_DATA.append((t18, e18))

# Case 19: Valve vs Stent
t19 = """The endobronchial valve in the LUL is seated correctly. 
The airway stent in the mainstem is also stable."""
e19 = [
    {"label": "DEV_VALVE", **get_span(t19, "endobronchial valve", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t19, "airway stent", 1)},
]
BATCH_DATA.append((t19, e19))

# Case 20: Pre-anesthesia check
t20 = """Review of systems: Patient has a tracheal stent. 
Anesthesia team alerted to presence of stent prior to intubation."""
e20 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t20, "tracheal stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t20, "stent", 2)},
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
    print(f"Successfully added {len(BATCH_DATA)} training cases with CTX_STENT_PRESENT labels.")
