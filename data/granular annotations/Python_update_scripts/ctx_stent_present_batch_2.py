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
# Synthetic Case Set: CTX_STENT_PRESENT (Existing Stents) - Batch 2
# ==============================================================================

# Case 21: Post-transplant stent surveillance
t21 = """Patient is 6 months post bilateral lung transplant. 
The silicone stent at the left anastomosis was evaluated. 
The stent remains well-positioned with no evidence of stenosis."""
e21 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t21, "silicone stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t21, "stent", 2)},
]
BATCH_DATA.append((t21, e21))

# Case 22: Stent in anastomotic stricture
t22 = """Bronchoscopy for anastomotic stricture follow-up. 
The covered metallic stent placed at the RMB anastomosis is patent. 
Minimal granulation at the stent margins was observed."""
e22 = [
    {"label": "OBS_FINDING", **get_span(t22, "anastomotic stricture", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t22, "covered metallic stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t22, "RMB", 1)},
    {"label": "OBS_FINDING", **get_span(t22, "granulation", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t22, "stent", 2)},
]
BATCH_DATA.append((t22, e22))

# Case 23: Chronic stent with biofilm
t23 = """The long-term indwelling stent shows yellowish biofilm coating. 
Brushings were taken from the stent surface for culture. 
The stent lumen remains greater than 70% open."""
e23 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t23, "indwelling stent", 1)},
    {"label": "OBS_FINDING", **get_span(t23, "biofilm", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t23, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t23, "stent", 3)},
]
BATCH_DATA.append((t23, e23))

# Case 24: Stent with recurrent tumor
t24 = """Follow-up for malignant obstruction. 
Tumor has regrown at the distal margin of the existing stent. 
The stent itself is not obstructed but extension is needed."""
e24 = [
    {"label": "OBS_FINDING", **get_span(t24, "malignant obstruction", 1)},
    {"label": "OBS_FINDING", **get_span(t24, "Tumor", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t24, "existing stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t24, "stent", 2)},
]
BATCH_DATA.append((t24, e24))

# Case 25: Stent patency assessment post-radiation
t25 = """Patient completed radiation therapy 2 weeks ago. 
The tracheal stent protecting the irradiated segment is intact. 
No radiation-induced changes visible through the stent mesh."""
e25 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t25, "tracheal stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t25, "stent", 2)},
]
BATCH_DATA.append((t25, e25))

# Case 26: Drug-eluting stent follow-up
t26 = """Evaluation of the paclitaxel-eluting stent placed for benign stricture. 
The stent shows expected drug coating dissolution. 
Airway caliber is maintained without restenosis."""
e26 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t26, "paclitaxel-eluting stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t26, "stent", 2)},
]
BATCH_DATA.append((t26, e26))

# Case 27: Stent with fungal colonization
t27 = """White plaques consistent with fungal colonization noted on the stent. 
The Dumon stent was lavaged with antifungal solution. 
Cultures pending from stent surface samples."""
e27 = [
    {"label": "OBS_FINDING", **get_span(t27, "fungal colonization", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t27, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t27, "Dumon stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t27, "stent", 3)},
]
BATCH_DATA.append((t27, e27))

# Case 28: Stent in post-intubation stenosis
t28 = """History of prolonged intubation with subsequent subglottic stenosis. 
The Montgomery T-tube stent remains functional. 
External limb of the stent is clean and patent."""
e28 = [
    {"label": "OBS_FINDING", **get_span(t28, "subglottic stenosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t28, "Montgomery T-tube stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t28, "stent", 2)},
]
BATCH_DATA.append((t28, e28))

# Case 29: Stent monitoring during chemoradiation
t29 = """Mid-treatment bronchoscopy during concurrent chemoradiation. 
The palliative stent in the LMB shows no tumor progression. 
Stent position unchanged from baseline imaging."""
e29 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t29, "palliative stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t29, "LMB", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t29, "Stent", 1)},
]
BATCH_DATA.append((t29, e29))

# Case 30: Stent in severe tracheomalacia
t30 = """Severe expiratory tracheomalacia managed with stent. 
Dynamic bronchoscopy shows the stent prevents complete collapse. 
The posterior membrane bulges into the stent but patency is maintained."""
e30 = [
    {"label": "OBS_FINDING", **get_span(t30, "tracheomalacia", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t30, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t30, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t30, "stent", 3)},
]
BATCH_DATA.append((t30, e30))

# Case 31: Stent assessment prior to surgery
t31 = """Preoperative evaluation requested by thoracic surgery. 
The airway stent must be removed prior to planned lobectomy. 
Assessment shows the stent can be safely extracted."""
e31 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t31, "airway stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t31, "stent", 2)},
]
BATCH_DATA.append((t31, e31))

# Case 32: Stent in bronchopleural fistula
t32 = """BPF post pneumonectomy with stent coverage. 
The silicone stent over the bronchial stump is well-seated. 
No air leak detected around the stent."""
e32 = [
    {"label": "OBS_FINDING", **get_span(t32, "BPF", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t32, "silicone stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t32, "stent", 2)},
]
BATCH_DATA.append((t32, e32))

# Case 33: Stent with reactive hyperplasia
t33 = """Polypoid tissue proliferation seen at both ends of the stent. 
This reactive hyperplasia is causing partial obstruction. 
Cryotherapy was applied to the tissue surrounding the stent."""
e33 = [
    {"label": "OBS_FINDING", **get_span(t33, "Polypoid tissue", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t33, "stent", 1)},
    {"label": "OBS_FINDING", **get_span(t33, "reactive hyperplasia", 1)},
    {"label": "PROC_METHOD", **get_span(t33, "Cryotherapy", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t33, "stent", 2)},
]
BATCH_DATA.append((t33, e33))

# Case 34: Stent surveillance in RML syndrome
t34 = """Right middle lobe syndrome with chronic stenosis managed by stent. 
The RML bronchial stent is patent with good distal ventilation. 
Secretions cleared from the stent interior."""
e34 = [
    {"label": "ANAT_AIRWAY", **get_span(t34, "Right middle lobe", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t34, "RML bronchial stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t34, "stent", 2)},
]
BATCH_DATA.append((t34, e34))

# Case 35: Stent post-sleeve resection
t35 = """Post-sleeve lobectomy bronchoscopy at 3 months. 
The prophylactic stent at the anastomosis shows good healing. 
Plan to remove the stent at next follow-up if stable."""
e35 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t35, "prophylactic stent", 1)},
    {"label": "DEV_STENT", **get_span(t35, "stent", 2)},  # Object of future removal
]
BATCH_DATA.append((t35, e35))

# Case 36: Stent in bronchial dehiscence
t36 = """Emergent stenting for bronchial dehiscence 2 weeks ago. 
The covered stent is providing adequate seal of the defect. 
The stent extends from the carina to the RLL takeoff."""
e36 = [
    {"label": "OBS_FINDING", **get_span(t36, "bronchial dehiscence", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t36, "covered stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t36, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t36, "carina", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t36, "RLL", 1)},
]
BATCH_DATA.append((t36, e36))

# Case 37: Stent with inspissated secretions
t37 = """Dense inspissated secretions filling the stent lumen. 
Aggressive suctioning performed through the obstructed stent. 
After clearance, the stent walls appear intact."""
e37 = [
    {"label": "OBS_FINDING", **get_span(t37, "inspissated secretions", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t37, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t37, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t37, "stent", 3)},
]
BATCH_DATA.append((t37, e37))

# Case 38: Stent follow-up post completion pneumonectomy
t38 = """Surveillance after completion pneumonectomy. 
The remaining bronchial stump stent is stable. 
No evidence of recurrence at the stent margins."""
e38 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t38, "bronchial stump stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t38, "stent", 2)},
]
BATCH_DATA.append((t38, e38))

# Case 39: Stent in benign web
t39 = """Congenital tracheal web with prior stent placement. 
The pediatric stent is now too small for patient growth. 
The current stent will need upsizing."""
e39 = [
    {"label": "OBS_FINDING", **get_span(t39, "tracheal web", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t39, "pediatric stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t39, "stent", 2)},
]
BATCH_DATA.append((t39, e39))

# Case 40: Stent in post-TB stenosis
t40 = """History of endobronchial tuberculosis with residual stenosis. 
The self-expanding metallic stent has been in place for 8 months. 
The stent shows good epithelialization without active infection."""
e40 = [
    {"label": "OBS_FINDING", **get_span(t40, "endobronchial tuberculosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t40, "self-expanding metallic stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t40, "stent", 2)},
]
BATCH_DATA.append((t40, e40))

# Case 41: Stent with bacterial colonization
t41 = """Chronic Pseudomonas colonization of the indwelling stent. 
Purulent secretions emanating from within the stent. 
The stent structure is intact despite chronic infection."""
e41 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t41, "indwelling stent", 1)},
    {"label": "OBS_FINDING", **get_span(t41, "Purulent secretions", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t41, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t41, "stent", 3)},
]
BATCH_DATA.append((t41, e41))

# Case 42: Stent in carinal reconstruction
t42 = """Post carinal resection and reconstruction with stent support. 
The carinal Y-stent maintains airway patency bilaterally. 
Both limbs of the stent are well-positioned."""
e42 = [
    {"label": "ANAT_AIRWAY", **get_span(t42, "carinal", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t42, "carinal Y-stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t42, "stent", 2)},
]
BATCH_DATA.append((t42, e42))

# Case 43: Stent readiness for removal assessment
t43 = """Trial of stent occlusion to assess removal readiness. 
The silicone stent was temporarily occluded for 48 hours. 
Patient tolerated occlusion well, stent removal can proceed."""
e43 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t43, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t43, "silicone stent", 1)},
    {"label": "DEV_STENT", **get_span(t43, "stent", 3)},  # Object of removal action
]
BATCH_DATA.append((t43, e43))

# Case 44: Stent in recurrent respiratory papillomatosis
t44 = """Recurrent respiratory papillomatosis with tracheal involvement. 
The stent placed to maintain airway has papilloma regrowth. 
Laser ablation performed around the stent circumference."""
e44 = [
    {"label": "OBS_FINDING", **get_span(t44, "papillomatosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t44, "stent", 1)},
    {"label": "OBS_FINDING", **get_span(t44, "papilloma", 1)},
    {"label": "PROC_METHOD", **get_span(t44, "Laser ablation", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t44, "stent", 2)},
]
BATCH_DATA.append((t44, e44))

# Case 45: Stent in post-tracheostomy stenosis
t45 = """Complex subglottic stenosis following tracheostomy. 
The Hood stent extends from subglottis to mid-trachea. 
Stent position is stable with adequate voice quality."""
e45 = [
    {"label": "OBS_FINDING", **get_span(t45, "subglottic stenosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t45, "Hood stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t45, "subglottis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t45, "mid-trachea", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t45, "Stent", 1)},
]
BATCH_DATA.append((t45, e45))

# Case 46: Crushed stent appearance
t46 = """The uncovered SEMS shows partial collapse from external compression. 
The stent lumen is reduced to approximately 50%. 
Consideration for placing a second stent inside the crushed stent."""
e46 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t46, "uncovered SEMS", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t46, "stent", 1)},
    {"label": "DEV_STENT", **get_span(t46, "stent", 2)},  # New stent to be placed
    {"label": "CTX_STENT_PRESENT", **get_span(t46, "stent", 3)},  # Crushed existing stent
]
BATCH_DATA.append((t46, e46))

# Case 47: Double stent configuration
t47 = """Patient has tandem stents in the trachea and left mainstem. 
The proximal tracheal stent abuts the distal bronchial stent. 
Both stents are patent without overlap complication."""
e47 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t47, "stents", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t47, "trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t47, "left mainstem", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t47, "tracheal stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t47, "bronchial stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t47, "stents", 2)},
]
BATCH_DATA.append((t47, e47))

# Case 48: Stent migration into lobar bronchus
t48 = """The RMB stent has migrated into the bronchus intermedius. 
The stent is now partially obstructing the RUL orifice. 
Repositioning of the stent is required."""
e48 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t48, "RMB stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t48, "bronchus intermedius", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t48, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t48, "RUL orifice", 1)},
    {"label": "DEV_STENT", **get_span(t48, "stent", 3)},  # Being repositioned
]
BATCH_DATA.append((t48, e48))

# Case 49: Stent with embedded edges
t49 = """The metallic stent edges have become embedded in the mucosa. 
Granulation tissue has grown over the proximal stent rim. 
Careful dissection needed if stent removal is attempted."""
e49 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t49, "metallic stent", 1)},
    {"label": "OBS_FINDING", **get_span(t49, "Granulation tissue", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t49, "stent", 2)},
    {"label": "DEV_STENT", **get_span(t49, "stent", 3)},  # Potential removal
]
BATCH_DATA.append((t49, e49))

# Case 50: Stent evaluation with EBUS
t50 = """EBUS performed to evaluate peristent lymphadenopathy. 
The existing stent does not interfere with EBUS imaging. 
Lymph node sampling performed adjacent to the stent."""
e50 = [
    {"label": "PROC_METHOD", **get_span(t50, "EBUS", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t50, "existing stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t50, "stent", 2)},
]
BATCH_DATA.append((t50, e50))


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
