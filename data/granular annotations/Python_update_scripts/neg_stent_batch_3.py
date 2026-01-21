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
# Synthetic Case Set: NEG_STENT Batch 3 - Extended Negation Patterns
# ==============================================================================

# Case 1: "Inappropriate"
t1 = """Bronchoscopy for evaluation of chronic cough.
Mild tracheal narrowing of 20% noted.
Stent placement inappropriate for this degree of stenosis.
Recommend speech therapy for cough suppression techniques."""
e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "tracheal narrowing of 20%", 1)},
    {"label": "NEG_STENT", **get_span(t1, "Stent", 1)},
]
BATCH_DATA.append((t1, e1))

# Case 2: "Unsuitable"
t2 = """Assessment for airway stabilization in relapsing polychondritis.
Diffuse cartilaginous involvement from glottis to carina.
Anatomy unsuitable for conventional stent therapy.
Multidisciplinary discussion recommended."""
e2 = [
    {"label": "OBS_FINDING", **get_span(t2, "relapsing polychondritis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "glottis", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "carina", 1)},
    {"label": "NEG_STENT", **get_span(t2, "stent", 1)},
]
BATCH_DATA.append((t2, e2))

# Case 3: "Suspended"
t3 = """Scheduled metallic stent insertion for esophageal compression.
Intraoperative finding of unsuspected vocal cord paralysis.
Stent procedure suspended pending laryngology evaluation.
Patient extubated without complication."""
e3 = [
    {"label": "DEV_STENT", **get_span(t3, "metallic stent", 1)},
    # Fix: "Stent" (capitalized) appears only once in t3.
    {"label": "NEG_STENT", **get_span(t3, "Stent", 1)},
]
BATCH_DATA.append((t3, e3))

# Case 4: "Waived"
t4 = """Second opinion consultation for recurrent benign stenosis.
Patient has undergone 12 prior dilations.
Stent placement waived in favor of tracheal resection.
Referred to thoracic surgery for sleeve resection."""
e4 = [
    {"label": "OBS_FINDING", **get_span(t4, "recurrent benign stenosis", 1)},
    {"label": "NEG_STENT", **get_span(t4, "Stent", 1)},
]
BATCH_DATA.append((t4, e4))

# Case 5: "Ruled out" alternative phrasing
t5 = """Bronchoscopy for stridor in post-transplant patient.
Anastomotic stricture identified at 60% narrowing.
Balloon dilation performed to 12mm.
Stent was ruled out due to immunosuppression risks."""
e5 = [
    {"label": "OBS_FINDING", **get_span(t5, "Anastomotic stricture", 1)},
    {"label": "PROC_METHOD", **get_span(t5, "Balloon dilation", 1)},
    {"label": "NEG_STENT", **get_span(t5, "Stent", 1)},
]
BATCH_DATA.append((t5, e5))

# Case 6: "Inapplicable"
t6 = """Flexible bronchoscopy through tracheostomy.
Granulation tissue at stoma site debrided.
Tracheal stenting inapplicable given tracheostomy dependence.
Stoma revision discussed with ENT."""
e6 = [
    {"label": "OBS_FINDING", **get_span(t6, "Granulation tissue", 1)},
    {"label": "NEG_STENT", **get_span(t6, "stenting", 1)},
]
BATCH_DATA.append((t6, e6))

# Case 7: "Negative stent trial"
t7 = """Trial of temporary silicone stent last month was unsuccessful.
Patient reported intractable cough and mucus retention.
Further stenting not recommended based on negative trial.
Conservative management with mucolytics initiated."""
e7 = [
    {"label": "DEV_STENT", **get_span(t7, "silicone stent", 1)},
    {"label": "NEG_STENT", **get_span(t7, "stenting", 1)},
]
BATCH_DATA.append((t7, e7))

# Case 8: "Without stent"
t8 = """Therapeutic bronchoscopy for post-TB stricture.
Radial incisions made with electrocautery knife.
Balloon dilation to 14mm performed.
Procedure completed without stent given benign etiology."""
e8 = [
    {"label": "OBS_FINDING", **get_span(t8, "post-TB stricture", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "electrocautery knife", 1)},
    {"label": "PROC_METHOD", **get_span(t8, "Balloon dilation", 1)},
    {"label": "NEG_STENT", **get_span(t8, "stent", 1)},
]
BATCH_DATA.append((t8, e8))

# Case 9: "Not performed"
t9 = """Interventional pulmonology consulted for airway management.
CT shows extrinsic compression from thyroid mass.
Stent insertion not performed pending thyroid surgery.
Will reassess airway post-operatively."""
e9 = [
    {"label": "OBS_FINDING", **get_span(t9, "extrinsic compression", 1)},
    {"label": "NEG_STENT", **get_span(t9, "Stent", 1)},
]
BATCH_DATA.append((t9, e9))

# Case 10: "Unlikely to benefit"
t10 = """Bronchoscopy for worsening dyspnea in advanced lung cancer.
Diffuse endobronchial disease throughout both lungs.
Patient unlikely to benefit from airway stent.
Focus shifted to symptom management and opioid titration."""
e10 = [
    {"label": "OBS_FINDING", **get_span(t10, "Diffuse endobronchial disease", 1)},
    {"label": "NEG_STENT", **get_span(t10, "stent", 1)},
]
BATCH_DATA.append((t10, e10))

# Case 11: "Reserved"
t11 = """Initial bronchoscopy for new diagnosis of squamous cell carcinoma.
LMB obstruction at 70% treated with mechanical debulking.
Stent reserved for disease progression or recurrence.
Chemoradiation to be initiated next week."""
e11 = [
    {"label": "ANAT_AIRWAY", **get_span(t11, "LMB", 1)},
    {"label": "PROC_METHOD", **get_span(t11, "mechanical debulking", 1)},
    {"label": "NEG_STENT", **get_span(t11, "Stent", 1)},
]
BATCH_DATA.append((t11, e11))

# Case 12: "Chose not to"
t12 = """Multidisciplinary tumor board discussion completed.
Given short life expectancy and patient preferences.
Team chose not to pursue airway stenting.
Best supportive care recommended."""
e12 = [
    {"label": "NEG_STENT", **get_span(t12, "stenting", 1)},
]
BATCH_DATA.append((t12, e12))

# Case 13: "Passed on"
t13 = """Consult for tracheobronchomalacia in morbidly obese patient.
Dynamic collapse exceeds 80% on expiration.
Stent placement passed on in favor of weight loss surgery.
Bariatric surgery referral completed."""
e13 = [
    {"label": "OBS_FINDING", **get_span(t13, "tracheobronchomalacia", 1)},
    {"label": "OBS_FINDING", **get_span(t13, "Dynamic collapse exceeds 80%", 1)},
    {"label": "NEG_STENT", **get_span(t13, "Stent", 1)},
]
BATCH_DATA.append((t13, e13))

# Case 14: "Obviated"
t14 = """Follow-up bronchoscopy after 6 weeks of chemotherapy.
Dramatic tumor response with only residual mucosal changes.
Excellent airway patency obviated the need for stent.
Continue current oncologic regimen."""
e14 = [
    {"label": "OBS_FINDING", **get_span(t14, "tumor response", 1)},
    {"label": "NEG_STENT", **get_span(t14, "stent", 1)},
]
BATCH_DATA.append((t14, e14))

# Case 15: "Escaped" (colloquial)
t15 = """Post-dilation assessment encouraging.
No immediate elastic recoil observed.
Patient escaped stent placement this procedure.
Return in 3 months for surveillance."""
e15 = [
    {"label": "NEG_STENT", **get_span(t15, "stent", 1)},
]
BATCH_DATA.append((t15, e15))

# Case 16: "Abandon"
t16 = """Complex Y-stent sizing attempted.
Multiple configurations trialed without adequate fit.
Decision to abandon stent placement due to anatomical mismatch.
Custom stent to be ordered from manufacturer."""
e16 = [
    {"label": "DEV_STENT", **get_span(t16, "Y-stent", 1)},
    {"label": "NEG_STENT", **get_span(t16, "stent", 2)},
]
BATCH_DATA.append((t16, e16))

# Case 17: "Steered away from"
t17 = """Discussion with patient regarding management options.
Given history of poor stent tolerance previously.
Steered away from repeat stenting toward surgical correction.
Cardiothoracic surgery appointment scheduled."""
e17 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t17, "stent", 1)},
    {"label": "NEG_STENT", **get_span(t17, "stenting", 1)},
]
BATCH_DATA.append((t17, e17))

# Case 18: "Left unstented"
t18 = """Rigid bronchoscopy with tumor debulking using microdebrider.
Significant hemorrhage controlled with balloon tamponade.
Given bleeding risk, airway left unstented.
Close monitoring in ICU overnight."""
e18 = [
    {"label": "PROC_METHOD", **get_span(t18, "Rigid bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t18, "microdebrider", 1)},
    {"label": "PROC_METHOD", **get_span(t18, "balloon tamponade", 1)},
    {"label": "NEG_STENT", **get_span(t18, "unstented", 1)},
]
BATCH_DATA.append((t18, e18))

# Case 19: "Abstained from"
t19 = """Bronchoscopy in patient with active aspergillosis.
Fungal plaques seen in distal trachea and RMB.
Abstained from stent placement given infection.
Antifungal therapy to be intensified."""
e19 = [
    {"label": "OBS_FINDING", **get_span(t19, "Fungal plaques", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t19, "distal trachea", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t19, "RMB", 1)},
    {"label": "NEG_STENT", **get_span(t19, "stent", 1)},
]
BATCH_DATA.append((t19, e19))

# Case 20: "No stent-related" (disambiguation - not a negation of placement)
t20 = """Surveillance of previously placed Aero stent.
Stent patent without migration or fracture.
No stent-related complications identified.
Continue annual surveillance protocol."""
e20 = [
    {"label": "CTX_STENT_PRESENT", **get_span(t20, "Aero stent", 1)},
    # Fix: "Stent" (capitalized) appears only once in t20.
    {"label": "CTX_STENT_PRESENT", **get_span(t20, "Stent", 1)},
]
BATCH_DATA.append((t20, e20))

# Case 21: "Skipped"
t21 = """Planned staged procedure for complex airway disease.
Today focused on LMB tumor debulking only.
Stent placement skipped until RMB addressed next session.
Patient stable for discharge."""
e21 = [
    {"label": "ANAT_AIRWAY", **get_span(t21, "LMB", 1)},
    {"label": "PROC_METHOD", **get_span(t21, "tumor debulking", 1)},
    {"label": "NEG_STENT", **get_span(t21, "Stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t21, "RMB", 1)},
]
BATCH_DATA.append((t21, e21))

# Case 22: "Shelved"
t22 = """Interventional bronchoscopy consultation completed.
Patient currently on dual antiplatelet therapy post-PCI.
Stent placement shelved for 6 months per cardiology.
Reassess after DAPT completion."""
e22 = [
    {"label": "NEG_STENT", **get_span(t22, "Stent", 1)},
]
BATCH_DATA.append((t22, e22))

# Case 23: "Premature"
t23 = """Bronchoscopy 2 weeks after radiation therapy initiation.
Tumor unchanged with persistent 60% obstruction.
Stent placement considered premature at this stage.
Repeat bronchoscopy after radiation completion."""
e23 = [
    {"label": "OBS_FINDING", **get_span(t23, "60% obstruction", 1)},
    {"label": "NEG_STENT", **get_span(t23, "Stent", 1)},
]
BATCH_DATA.append((t23, e23))

# Case 24: "Superseded"
t24 = """Initial plan for palliative stenting revised.
New PET scan shows oligometastatic disease amenable to SBRT.
Stent plan superseded by curative-intent treatment approach.
Radiation oncology to proceed with treatment planning."""
e24 = [
    {"label": "NEG_STENT", **get_span(t24, "stenting", 1)},
    # Fix: "Stent" (capitalized) appears only once in t24.
    {"label": "NEG_STENT", **get_span(t24, "Stent", 1)},
]
BATCH_DATA.append((t24, e24))

# Case 25: "In lieu of stent"
t25 = """Therapeutic bronchoscopy for web-like tracheal stenosis.
Radial incisions with cold knife and balloon dilation.
Intralesional steroid injection performed in lieu of stent.
Triamcinolone 40mg injected circumferentially."""
e25 = [
    {"label": "OBS_FINDING", **get_span(t25, "web-like tracheal stenosis", 1)},
    {"label": "PROC_METHOD", **get_span(t25, "Radial incisions", 1)},
    {"label": "PROC_METHOD", **get_span(t25, "balloon dilation", 1)},
    {"label": "NEG_STENT", **get_span(t25, "stent", 1)},
    {"label": "MEDICATION", **get_span(t25, "Triamcinolone", 1)},
]
BATCH_DATA.append((t25, e25))

# Case 26: "Circumvented"
t26 = """Novel approach using serial cryospray therapy.
Circumferential freeze-thaw cycles applied to stenotic segment.
Need for stent circumvented with this technique.
Patient to return weekly for 4 treatments."""
e26 = [
    {"label": "PROC_METHOD", **get_span(t26, "cryospray therapy", 1)},
    {"label": "NEG_STENT", **get_span(t26, "stent", 1)},
]
BATCH_DATA.append((t26, e26))

# Case 27: "Rather than stent"
t27 = """Tracheal stenosis secondary to prolonged intubation.
Opted for endoscopic management rather than stent placement.
Balloon dilation with mitomycin application performed.
Follow-up scheduled in 4 weeks."""
e27 = [
    {"label": "OBS_FINDING", **get_span(t27, "Tracheal stenosis", 1)},
    {"label": "NEG_STENT", **get_span(t27, "stent", 1)},
    {"label": "PROC_METHOD", **get_span(t27, "Balloon dilation", 1)},
    {"label": "MEDICATION", **get_span(t27, "mitomycin", 1)},
]
BATCH_DATA.append((t27, e27))

# Case 28: "Nixed"
t28 = """Family meeting held regarding treatment escalation.
Given poor functional status and DNR status.
Airway stent proposal nixed by healthcare proxy.
Comfort care measures to continue."""
e28 = [
    {"label": "NEG_STENT", **get_span(t28, "stent", 1)},
]
BATCH_DATA.append((t28, e28))

# Case 29: "Sidestepped"
t29 = """Challenging case of idiopathic subglottic stenosis.
Multiple prior interventions with rapid recurrence.
Stent placement sidestepped given proximity to vocal cords.
Referred for laryngotracheal reconstruction."""
e29 = [
    {"label": "OBS_FINDING", **get_span(t29, "idiopathic subglottic stenosis", 1)},
    {"label": "NEG_STENT", **get_span(t29, "Stent", 1)},
]
BATCH_DATA.append((t29, e29))

# Case 30: Complex mixed scenario
t30 = """Removal of migrated Polyflex stent from RMB.
Stent successfully extracted with rat-tooth forceps.
Underlying stricture dilated to 10mm with CRE balloon.
Replacement stent not inserted given adequate post-dilation caliber.
Patient discharged same day with follow-up in 6 weeks."""
e30 = [
    {"label": "DEV_STENT", **get_span(t30, "Polyflex stent", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t30, "RMB", 1)},
    # Fix: "Stent" (capitalized) appears only once (at the start of 2nd sentence).
    {"label": "DEV_STENT", **get_span(t30, "Stent", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t30, "rat-tooth forceps", 1)},
    {"label": "PROC_METHOD", **get_span(t30, "dilated", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t30, "CRE balloon", 1)},
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
