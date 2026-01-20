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
# Synthetic Case Set: NEG_STENT Batch 2 - Additional Negation Patterns
# ==============================================================================

# Case 1: "Stent contraindicated"
t1 = """Flexible bronchoscopy performed for hemoptysis workup.
Diffuse mucosal inflammation throughout the tracheobronchial tree.
Stent placement is contraindicated given active infection.
Cultures obtained and sent to microbiology."""
e1 = [
    {"label": "PROC_METHOD", **get_span(t1, "Flexible bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Diffuse mucosal inflammation", 1)},
    {"label": "NEG_STENT", **get_span(t1, "Stent", 1)},
]
BATCH_DATA.append((t1, e1))

# Case 2: "Opted against"
t2 = """Severe tracheomalacia noted with expiratory collapse exceeding 90%.
After informed consent discussion, patient opted against stent insertion.
Will pursue CPAP therapy as alternative."""
e2 = [
    {"label": "OBS_FINDING", **get_span(t2, "tracheomalacia", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "expiratory collapse exceeding 90%", 1)},
    {"label": "NEG_STENT", **get_span(t2, "stent", 1)},
]
BATCH_DATA.append((t2, e2))

# Case 3: "Precluded"
t3 = """Complete tumor encasement of the left mainstem bronchus.
Friable tissue with high bleeding risk.
Active hemorrhage precluded safe stent deployment.
Hemostatic measures applied with cold saline and epinephrine."""
e3 = [
    {"label": "ANAT_AIRWAY", **get_span(t3, "left mainstem bronchus", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "Friable tissue", 1)},
    {"label": "NEG_STENT", **get_span(t3, "stent", 1)},
    {"label": "MEDICATION", **get_span(t3, "epinephrine", 1)},
]
BATCH_DATA.append((t3, e3))

# Case 4: "Unnecessary"
t4 = """Post-dilation assessment showed excellent luminal patency.
Airway caliber restored to near-normal.
Stent deemed unnecessary given durable response to dilation."""
e4 = [
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t4, "excellent luminal patency", 1)},
    {"label": "NEG_STENT", **get_span(t4, "Stent", 1)},
    {"label": "PROC_METHOD", **get_span(t4, "dilation", 2)},
]
BATCH_DATA.append((t4, e4))

# Case 5: "Postponed"
t5 = """Rigid bronchoscopy for subglottic stenosis.
Mechanical dilation performed with serial bougie dilators.
Stenting postponed until inflammation resolves.
Patient scheduled for repeat procedure in 6 weeks."""
e5 = [
    {"label": "PROC_METHOD", **get_span(t5, "Rigid bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(t5, "subglottic stenosis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t5, "bougie dilators", 1)},
    {"label": "NEG_STENT", **get_span(t5, "Stenting", 1)},
]
BATCH_DATA.append((t5, e5))

# Case 6: "Not warranted"
t6 = """Surveillance bronchoscopy 3 months post-lobectomy.
Bronchial anastomosis intact and widely patent.
No granulation tissue identified.
Stent not warranted at this time."""
e6 = [
    {"label": "OBS_FINDING", **get_span(t6, "anastomosis intact", 1)},
    {"label": "NEG_STENT", **get_span(t6, "Stent", 1)},
]
BATCH_DATA.append((t6, e6))

# Case 7: "No indication for"
t7 = """Complete airway survey performed.
Bilateral mainstem bronchi patent.
Carina sharp without compression.
No indication for stent placement identified."""
e7 = [
    {"label": "ANAT_AIRWAY", **get_span(t7, "mainstem bronchi", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "Carina", 1)},
    {"label": "NEG_STENT", **get_span(t7, "stent", 1)},
]
BATCH_DATA.append((t7, e7))

# Case 8: "Held"
t8 = """Bronchoscopy for stridor evaluation.
Tracheal narrowing at 50% secondary to goiter compression.
Pending thyroidectomy, airway stenting held.
ENT consulted for surgical planning."""
e8 = [
    {"label": "OBS_FINDING", **get_span(t8, "Tracheal narrowing at 50%", 1)},
    {"label": "NEG_STENT", **get_span(t8, "stenting", 1)},
]
BATCH_DATA.append((t8, e8))

# Case 9: "Rejected" (patient decision)
t9 = """Discussed management options including silicone stent placement.
Patient rejected stenting due to concerns about mucus plugging.
Agreed on surveillance protocol with quarterly bronchoscopy."""
e9 = [
    {"label": "NEG_STENT", **get_span(t9, "silicone stent", 1)},
    {"label": "NEG_STENT", **get_span(t9, "stenting", 1)},
]
BATCH_DATA.append((t9, e9))

# Case 10: "Negative for... no stent needed"
t10 = """Bronchoscopy negative for recurrent stenosis.
Tracheal lumen remains adequate at 14mm diameter.
No stent needed at follow-up."""
e10 = [
    {"label": "OBS_FINDING", **get_span(t10, "negative for recurrent stenosis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "Tracheal lumen", 1)},
    {"label": "NEG_STENT", **get_span(t10, "stent", 1)},
]
BATCH_DATA.append((t10, e10))

# Case 11: "Forgone"
t11 = """Palliation with cryotherapy and tumor debulking completed.
Given limited prognosis, stent placement was forgone per goals of care.
Comfort measures emphasized."""
e11 = [
    {"label": "PROC_METHOD", **get_span(t11, "cryotherapy", 1)},
    {"label": "PROC_METHOD", **get_span(t11, "tumor debulking", 1)},
    {"label": "NEG_STENT", **get_span(t11, "stent", 1)},
]
BATCH_DATA.append((t11, e11))

# Case 12: "Omitted"
t12 = """Interventional bronchoscopy for malignant airway obstruction.
Laser ablation achieved 70% recanalization.
Stent was omitted to preserve future treatment options.
Radiation oncology consulted for external beam therapy."""
e12 = [
    {"label": "OBS_FINDING", **get_span(t12, "malignant airway obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(t12, "Laser ablation", 1)},
    {"label": "NEG_STENT", **get_span(t12, "Stent", 1)},
]
BATCH_DATA.append((t12, e12))

# Case 13: "No need for"
t13 = """Follow-up bronchoscopy post radiation therapy.
Tumor regression with near-complete response.
Airway patent without obstruction.
No need for stent at this time."""
e13 = [
    {"label": "OBS_FINDING", **get_span(t13, "Tumor regression", 1)},
    {"label": "NEG_STENT", **get_span(t13, "stent", 1)},
]
BATCH_DATA.append((t13, e13))

# Case 14: "Cancelled"
t14 = """Patient arrived for scheduled stent placement.
Pre-procedure CT showed new pulmonary embolism.
Stent procedure cancelled for anticoagulation initiation.
Rescheduled for 4 weeks."""
e14 = [
    {"label": "NEG_STENT", **get_span(t14, "stent", 1)},
    # Fixed: "Stent" (capitalized) appears only once in t14
    {"label": "NEG_STENT", **get_span(t14, "Stent", 1)},
]
BATCH_DATA.append((t14, e14))

# Case 15: "Aborted"
t15 = """Rigid bronchoscopy initiated for Y-stent placement.
Unable to ventilate adequately during the procedure.
Oxygen desaturation to 78% despite FiO2 100%.
Stent deployment aborted due to respiratory compromise."""
e15 = [
    {"label": "PROC_METHOD", **get_span(t15, "Rigid bronchoscopy", 1)},
    {"label": "DEV_STENT", **get_span(t15, "Y-stent", 1)},
    # Fixed: "Stent" (capitalized) appears only once in t15
    {"label": "NEG_STENT", **get_span(t15, "Stent", 1)},
]
BATCH_DATA.append((t15, e15))

# Case 16: "Refrained from"
t16 = """Bronchoscopy for post-intubation tracheal stenosis.
Web-like stenosis successfully incised with electrocautery.
Refrained from stenting given circumferential mucosal involvement.
Mitomycin C applied topically."""
e16 = [
    {"label": "OBS_FINDING", **get_span(t16, "post-intubation tracheal stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(t16, "electrocautery", 1)},
    {"label": "NEG_STENT", **get_span(t16, "stenting", 1)},
    {"label": "MEDICATION", **get_span(t16, "Mitomycin C", 1)},
]
BATCH_DATA.append((t16, e16))

# Case 17: "Not pursued"
t17 = """EBUS-TBNA performed for mediastinal lymphadenopathy staging.
No airway compromise visualized.
Stent placement not pursued given diagnostic-only procedure."""
e17 = [
    {"label": "PROC_METHOD", **get_span(t17, "EBUS-TBNA", 1)},
    {"label": "NEG_STENT", **get_span(t17, "Stent", 1)},
]
BATCH_DATA.append((t17, e17))

# Case 18: "Did not require"
t18 = """Bronchoscopy for mucus plug removal in RML.
Copious thick secretions suctioned.
Airway architecture normal after clearance.
Patient did not require stent intervention."""
e18 = [
    {"label": "OBS_FINDING", **get_span(t18, "mucus plug", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t18, "RML", 1)},
    {"label": "NEG_STENT", **get_span(t18, "stent", 1)},
]
BATCH_DATA.append((t18, e18))

# Case 19: "Elect not to"
t19 = """Recurrent tracheal stenosis after multiple dilations.
Discussed definitive surgical resection versus repeat stenting.
Patient elected not to proceed with stent given surgical candidacy.
Thoracic surgery referral placed."""
e19 = [
    {"label": "OBS_FINDING", **get_span(t19, "Recurrent tracheal stenosis", 1)},
    {"label": "NEG_STENT", **get_span(t19, "stenting", 1)},
    {"label": "NEG_STENT", **get_span(t19, "stent", 2)},
]
BATCH_DATA.append((t19, e19))

# Case 20: "Without the need for"
t20 = """Therapeutic bronchoscopy for endobronchial carcinoid.
Tumor resected en bloc using cryoprobe extraction.
Complete removal achieved without the need for stent placement.
Specimen sent for pathology."""
e20 = [
    {"label": "OBS_FINDING", **get_span(t20, "endobronchial carcinoid", 1)},
    {"label": "PROC_METHOD", **get_span(t20, "cryoprobe extraction", 1)},
    {"label": "NEG_STENT", **get_span(t20, "stent", 1)},
]
BATCH_DATA.append((t20, e20))

# Case 21: "Declined" (provider decision)
t21 = """Complex tracheoesophageal fistula identified.
Stent placement declined in favor of surgical repair.
GI and thoracic surgery consulted for joint operative planning."""
e21 = [
    {"label": "OBS_FINDING", **get_span(t21, "tracheoesophageal fistula", 1)},
    {"label": "NEG_STENT", **get_span(t21, "Stent", 1)},
]
BATCH_DATA.append((t21, e21))

# Case 22: "None placed"
t22 = """Rigid bronchoscopy with core-out of endobronchial tumor.
Hemostasis achieved with electrocautery.
Airway stents: none placed.
Patient tolerated procedure well."""
e22 = [
    {"label": "PROC_METHOD", **get_span(t22, "core-out", 1)},
    {"label": "PROC_METHOD", **get_span(t22, "electrocautery", 1)},
    {"label": "NEG_STENT", **get_span(t22, "stents", 1)},
]
BATCH_DATA.append((t22, e22))

# Case 23: "Excluded"
t23 = """Evaluation for airway stabilization in severe COPD.
Dynamic airway collapse present but not flow-limiting.
Stent therapy excluded based on functional testing results."""
e23 = [
    {"label": "OBS_FINDING", **get_span(t23, "Dynamic airway collapse", 1)},
    {"label": "NEG_STENT", **get_span(t23, "Stent", 1)},
]
BATCH_DATA.append((t23, e23))

# Case 24: "Not deployed"
t24 = """Planned deployment of covered SEMS for malignant stricture.
Bronchoscope advanced to distal trachea.
Excessive tortuosity prevented safe positioning.
Stent not deployed due to anatomical constraints."""
e24 = [
    {"label": "DEV_STENT", **get_span(t24, "covered SEMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t24, "distal trachea", 1)},
    # Fixed: "Stent" (capitalized) appears only once in t24
    {"label": "NEG_STENT", **get_span(t24, "Stent", 1)},
]
BATCH_DATA.append((t24, e24))

# Case 25: "Spared from"
t25 = """Successful APC ablation of granulation tissue.
Tracheal lumen restored to 90% patency.
Patient spared from stent placement this session.
Re-evaluate in 4 weeks."""
e25 = [
    {"label": "PROC_METHOD", **get_span(t25, "APC ablation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t25, "90% patency", 1)},
    {"label": "NEG_STENT", **get_span(t25, "stent", 1)},
]
BATCH_DATA.append((t25, e25))

# Case 26: "Cannot be placed"
t26 = """Bronchoscopy reveals complete obliteration of RUL bronchus.
Guidewire unable to traverse the obstruction.
Stent cannot be placed without luminal access.
Referred for possible pneumonectomy evaluation."""
e26 = [
    {"label": "ANAT_AIRWAY", **get_span(t26, "RUL bronchus", 1)},
    {"label": "NEG_STENT", **get_span(t26, "Stent", 1)},
]
BATCH_DATA.append((t26, e26))

# Case 27: "No stent complication" vs "No stent" (disambiguation)
t27 = """Patient with known tracheomalacia managed conservatively.
Surveillance bronchoscopy shows stable airway dynamics.
No airway stent in place and none indicated.
Will continue nocturnal BiPAP."""
e27 = [
    {"label": "OBS_FINDING", **get_span(t27, "tracheomalacia", 1)},
    {"label": "NEG_STENT", **get_span(t27, "stent", 1)},
]
BATCH_DATA.append((t27, e27))

# Case 28: "Deferred indefinitely"
t28 = """Recurrent aspiration events with poor functional status.
Goals of care discussion held with family.
Airway stenting deferred indefinitely given comfort-focused care.
Hospice referral initiated."""
e28 = [
    {"label": "NEG_STENT", **get_span(t28, "stenting", 1)},
]
BATCH_DATA.append((t28, e28))

# Case 29: "Not feasible"
t29 = """Bronchoscopy for bilateral mainstem involvement.
Tumor extends from carina to both lobar bronchi.
Y-stent placement not feasible due to distal extent of disease.
Palliative radiation recommended."""
e29 = [
    {"label": "ANAT_AIRWAY", **get_span(t29, "carina", 1)},
    {"label": "NEG_STENT", **get_span(t29, "Y-stent", 1)},
]
BATCH_DATA.append((t29, e29))

# Case 30: Complex scenario with stent removal and no replacement
t30 = """Removal of occluded Ultraflex stent from bronchus intermedius.
Stent extracted using alligator forceps through rigid bronchoscope.
Underlying airway showed mild malacia but adequate caliber.
New stent not inserted given acceptable airway patency.
Patient to follow up in 6 weeks for reassessment."""
e30 = [
    {"label": "DEV_STENT", **get_span(t30, "Ultraflex stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t30, "bronchus intermedius", 1)},
    {"label": "PROC_METHOD", **get_span(t30, "extracted", 1)},
    # Fixed: "Stent" (capitalized) appears only once in t30
    {"label": "DEV_STENT", **get_span(t30, "Stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t30, "alligator forceps", 1)},
    {"label": "OBS_FINDING", **get_span(t30, "mild malacia", 1)},
    # Fixed: "stent" (lowercase) appears twice (Ultraflex, New stent).
    # We want "New stent", which is the 2nd lowercase occurrence.
    {"label": "NEG_STENT", **get_span(t30, "stent", 2)},
]
BATCH_DATA.append((t30, e30))


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
