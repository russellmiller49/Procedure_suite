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
# Synthetic Case Set: CTX_STENT_PRESENT (Existing Stents) - Batch 3
# ==============================================================================

# Case 51: Stent in relapsing polychondritis
t51 = """Patient with relapsing polychondritis and diffuse airway collapse. 
Multiple silicone stents span the trachea and bilateral mainstems. 
All stents appear well-positioned on today's examination."""
e51 = [
    {"label": "OBS_FINDING", **get_span(t51, "relapsing polychondritis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t51, "silicone stents", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t51, "trachea", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t51, "stents", 2)},
]
BATCH_DATA.append((t51, e51))

# Case 52: Stent with hemoptysis evaluation
t52 = """Bronchoscopy for hemoptysis in patient with airway stent. 
Blood noted originating from granulation at the stent edge. 
The stent body shows no erosion into vessels."""
e52 = [
    {"label": "OBS_FINDING", **get_span(t52, "hemoptysis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t52, "airway stent", 1)},
    {"label": "OBS_FINDING", **get_span(t52, "granulation", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t52, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t52, "stent", 3)},
]
BATCH_DATA.append((t52, e52))

# Case 53: Stent in extrinsic compression from lymphoma
t53 = """Mediastinal lymphoma causing airway compression. 
The deployed stent maintains airway caliber despite mass effect. 
The stent shows mild narrowing at the level of compression."""
e53 = [
    {"label": "OBS_FINDING", **get_span(t53, "lymphoma", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t53, "deployed stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t53, "stent", 2)},
]
BATCH_DATA.append((t53, e53))

# Case 54: Stent patency with CT correlation
t54 = """CT showed possible stent obstruction. 
Bronchoscopic evaluation confirms the stent is actually patent. 
Mucus stranding within the stent caused the CT artifact."""
e54 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t54, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t54, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t54, "stent", 3)},
]
BATCH_DATA.append((t54, e54))

# Case 55: Stent after esophageal surgery
t55 = """History of esophagectomy with airway fistula requiring stent. 
The tracheal stent continues to seal the fistula site. 
No contrast extravasation seen around the stent."""
e55 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t55, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t55, "tracheal stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t55, "stent", 3)},
]
BATCH_DATA.append((t55, e55))

# Case 56: Stent surveillance post-immunotherapy
t56 = """Restaging bronchoscopy after immunotherapy response. 
The stent placed for tumor obstruction now has visible airway. 
Tumor regression seen distal to the stent."""
e56 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t56, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t56, "stent", 2)},
]
BATCH_DATA.append((t56, e56))

# Case 57: Stent with mucosal ischemia
t57 = """Pale ischemic mucosa noted at the proximal stent margin. 
Possible pressure necrosis from the stent edge. 
The stent may need repositioning to relieve pressure."""
e57 = [
    {"label": "OBS_FINDING", **get_span(t57, "ischemic mucosa", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t57, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t57, "stent", 2)},
    {"label": "DEV_STENT", **get_span(t57, "stent", 3)},
]
BATCH_DATA.append((t57, e57))

# Case 58: Stent in GPA (Wegener's)
t58 = """Granulomatosis with polyangiitis with subglottic stenosis. 
The subglottic stent is in stable position. 
Disease appears quiescent around the stent."""
e58 = [
    {"label": "OBS_FINDING", **get_span(t58, "Granulomatosis with polyangiitis", 1)},
    {"label": "OBS_FINDING", **get_span(t58, "subglottic stenosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t58, "subglottic stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t58, "stent", 2)},
]
BATCH_DATA.append((t58, e58))

# Case 59: Stent in idiopathic tracheal stenosis
t59 = """Young female with idiopathic subglottic stenosis. 
The silicone stent placed after serial dilations remains patent. 
Plan to continue surveillance of the stent every 3 months."""
e59 = [
    {"label": "OBS_FINDING", **get_span(t59, "idiopathic subglottic stenosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t59, "silicone stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t59, "stent", 2)},
]
BATCH_DATA.append((t59, e59))

# Case 60: Stent with voice changes
t60 = """Patient reports hoarse voice since stent placement. 
The proximal stent margin is 1 cm below the vocal cords. 
No direct stent contact with the larynx identified."""
e60 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t60, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t60, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t60, "vocal cords", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t60, "stent", 3)},
]
BATCH_DATA.append((t60, e60))

# Case 61: Stent fluoroscopy correlation
t61 = """Fluoroscopy-guided assessment of stent position. 
The radiopaque markers on the stent align with the carina. 
Bronchoscopic view confirms appropriate stent placement."""
e61 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t61, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t61, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t61, "carina", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t61, "stent", 3)},
]
BATCH_DATA.append((t61, e61))

# Case 62: Stent in sarcoidosis
t62 = """Stage IV sarcoidosis with fibrosing mediastinitis. 
The LMB stent prevents complete collapse from fibrosis. 
The stent appears stable compared to prior exam."""
e62 = [
    {"label": "OBS_FINDING", **get_span(t62, "sarcoidosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t62, "LMB stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t62, "stent", 2)},
]
BATCH_DATA.append((t62, e62))

# Case 63: Stent with blood clot
t63 = """Old blood clot adherent to the inner stent wall. 
The clot was suctioned from within the stent. 
Underlying stent surface appears intact without erosion."""
e63 = [
    {"label": "OBS_FINDING", **get_span(t63, "blood clot", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t63, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t63, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t63, "stent", 3)},
]
BATCH_DATA.append((t63, e63))

# Case 64: Stent in thyroid cancer invasion
t64 = """Anaplastic thyroid cancer with tracheal invasion. 
The emergently placed stent maintains the airway. 
Tumor visible at the proximal and distal stent margins."""
e64 = [
    {"label": "OBS_FINDING", **get_span(t64, "thyroid cancer", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t64, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t64, "stent", 2)},
]
BATCH_DATA.append((t64, e64))

# Case 65: Stent in burned airway
t65 = """Thermal inhalation injury with subsequent tracheal stenosis. 
The stent placed during recovery phase is well-tolerated. 
Scarring visible around the stent but lumen maintained."""
e65 = [
    {"label": "OBS_FINDING", **get_span(t65, "inhalation injury", 1)},
    {"label": "OBS_FINDING", **get_span(t65, "tracheal stenosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t65, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t65, "stent", 2)},
]
BATCH_DATA.append((t65, e65))

# Case 66: Stent diameter measurement
t66 = """Measurement of the existing stent inner diameter performed. 
The 16mm stent shows 14mm luminal patency. 
Thin biofilm accounts for the 2mm reduction in stent caliber."""
e66 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t66, "existing stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t66, "16mm stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t66, "stent", 3)},
]
BATCH_DATA.append((t66, e66))

# Case 67: Stent in amyloidosis
t67 = """Tracheobronchial amyloidosis with diffuse narrowing. 
The segmental stent in the RMB maintains distal ventilation. 
Amyloid deposits visible at the stent ends."""
e67 = [
    {"label": "OBS_FINDING", **get_span(t67, "amyloidosis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t67, "segmental stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t67, "RMB", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t67, "stent", 2)},
]
BATCH_DATA.append((t67, e67))

# Case 68: Stent with aspiration evaluation
t68 = """Recurrent aspiration pneumonia in stented patient. 
The upper stent margin does not impair swallowing mechanism. 
Food particles noted distal to the stent in RLL."""
e68 = [
    {"label": "OBS_FINDING", **get_span(t68, "aspiration pneumonia", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t68, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t68, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t68, "RLL", 1)},
]
BATCH_DATA.append((t68, e68))

# Case 69: Stent after mediastinal radiation
t69 = """Post-radiation fibrosis causing airway compromise. 
The protective stent has been in place for 18 months. 
No radiation-related changes to the stent material observed."""
e69 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t69, "protective stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t69, "stent", 2)},
]
BATCH_DATA.append((t69, e69))

# Case 70: Stent in tracheopathia osteochondroplastica
t70 = """Tracheopathia osteochondroplastica with nodular airway. 
The stent bridges the most severely affected segment. 
Bony nodules visible proximal and distal to the stent."""
e70 = [
    {"label": "OBS_FINDING", **get_span(t70, "Tracheopathia osteochondroplastica", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t70, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t70, "stent", 2)},
]
BATCH_DATA.append((t70, e70))

# Case 71: Stent symptom assessment
t71 = """Patient reports improved dyspnea since stent insertion. 
The stent provides approximately 80% luminal restoration. 
Continued stent surveillance recommended."""
e71 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t71, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t71, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t71, "stent", 3)},
]
BATCH_DATA.append((t71, e71))

# Case 72: Stent with secondary infection
t72 = """Acute bronchitis superimposed on chronic stent colonization. 
Purulent secretions pooling within the stent. 
Aggressive pulmonary toilet of the stent performed."""
e72 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t72, "stent", 1)},
    {"label": "OBS_FINDING", **get_span(t72, "Purulent secretions", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t72, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t72, "stent", 3)},
]
BATCH_DATA.append((t72, e72))

# Case 73: Stent in mediastinal fibrosis
t73 = """Fibrosing mediastinitis from histoplasmosis. 
The chronic indwelling stent prevents RMB occlusion. 
Dense fibrosis encases the stent externally."""
e73 = [
    {"label": "OBS_FINDING", **get_span(t73, "Fibrosing mediastinitis", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t73, "indwelling stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t73, "RMB", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t73, "stent", 2)},
]
BATCH_DATA.append((t73, e73))

# Case 74: Stent with mucus plug
t74 = """Large mucus plug causing acute stent obstruction. 
Emergent bronchoscopy cleared the stent successfully. 
The underlying stent is intact after plug removal."""
e74 = [
    {"label": "OBS_FINDING", **get_span(t74, "mucus plug", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t74, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t74, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t74, "stent", 3)},
]
BATCH_DATA.append((t74, e74))

# Case 75: Stent in COPD patient
t75 = """Severe COPD with tracheobronchomalacia requiring stent. 
The dynamic stent improves expiratory flow. 
PFTs show improvement since stent placement."""
e75 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t75, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t75, "dynamic stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t75, "stent", 3)},
]
BATCH_DATA.append((t75, e75))

# Case 76: Stent comparison to prior
t76 = """Comparison bronchoscopy at 6 month interval. 
The stent position is unchanged from prior examination. 
No new granulation tissue around the stent margins."""
e76 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t76, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t76, "stent", 2)},
]
BATCH_DATA.append((t76, e76))

# Case 77: Stent in metastatic disease
t77 = """Metastatic renal cell carcinoma to the airway. 
The stent traverses the endobronchial metastasis. 
Tumor visible through the stent mesh interstices."""
e77 = [
    {"label": "OBS_FINDING", **get_span(t77, "renal cell carcinoma", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t77, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t77, "stent", 2)},
]
BATCH_DATA.append((t77, e77))

# Case 78: Stent before PET scan
t78 = """Pre-PET bronchoscopy to assess stent-related uptake. 
The stent shows expected inflammatory rim on imaging. 
No concerning tumor progression around the stent."""
e78 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t78, "stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t78, "stent", 2)},
    {"label": "CTX_STENT_PRESENT", **get_span(t78, "stent", 3)},
]
BATCH_DATA.append((t78, e78))

# Case 79: Stent after cryospray ablation
t79 = """Follow-up after cryospray ablation for tumor debulking. 
The existing stent protected the airway during treatment. 
Post-ablation tissue noted at the stent margins."""
e79 = [
    {"label": "PROC_METHOD", **get_span(t79, "cryospray ablation", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t79, "existing stent", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t79, "stent", 2)},
]
BATCH_DATA.append((t79, e79))

# Case 80: Stent in post-lobectomy bronchus
t80 = """Status post RUL lobectomy with bronchial stump narrowing. 
The short stent maintains bronchus intermedius patency. 
The stent does not impinge on the RML orifice."""
e80 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t80, "short stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t80, "bronchus intermedius", 1)},
    {"label": "CTX_STENT_PRESENT", **get_span(t80, "stent", 2)},
    {"label": "ANAT_AIRWAY", **get_span(t80, "RML orifice", 1)},
]
BATCH_DATA.append((t80, e80))


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
