import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the utility function
try:
    from scripts.add_training_case import add_case
except ImportError:
    sys.path.append(str(REPO_ROOT))
    from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns: {"start": int, "end": int} or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 1923847_syn_1
# ==========================================
id_1 = "1923847_syn_1"
text_1 = """Procedure: Emergent Bronchoscopy.
- Indication: Massive hemoptysis (LUL).
- Action: Balloon tamponade (Fogarty).
- Findings: Bleeding from Lingula/Anterior LUL.
- Result: Bleeding stopped with tamponade.
- Plan: IR for embolization."""
entities_1 = [
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Massive hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LUL", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "tamponade", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Fogarty", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "Bleeding", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "Anterior LUL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Bleeding stopped", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "IR", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "embolization", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 1923847_syn_2
# ==========================================
id_2 = "1923847_syn_2"
text_2 = """OPERATIVE REPORT: The patient required emergent bronchoscopy for life-threatening hemoptysis. The source was localized to the Left Upper Lobe. Initial conservative measures (iced saline, epinephrine) failed. Endobronchial balloon tamponade was employed, isolating the bleeding segments (Lingula/Anterior). Hemostasis was achieved. Interventional Radiology was consulted for urgent bronchial artery embolization."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Left Upper Lobe", 1)},
    {"label": "MEDICATION", **get_span(text_2, "iced saline", 1)},
    {"label": "MEDICATION", **get_span(text_2, "epinephrine", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "tamponade", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "bleeding", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Lingula", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Anterior", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "Hemostasis was achieved", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Interventional Radiology", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchial artery embolization", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 1923847_syn_3
# ==========================================
id_3 = "1923847_syn_3"
text_3 = """CPT: 31634 (Balloon occlusion). Indication: Hemoptysis. Technique: Flexible bronchoscopy with Fogarty balloon tamponade. Adjuncts: Iced saline, TXA."""
entities_3 = [
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "occlusion", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "Hemoptysis", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Flexible", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "bronchoscopy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Fogarty balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "tamponade", 1)},
    {"label": "MEDICATION", **get_span(text_3, "Iced saline", 1)},
    {"label": "MEDICATION", **get_span(text_3, "TXA", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 1923847_syn_4
# ==========================================
id_4 = "1923847_syn_4"
text_4 = """Resident Note: Hemoptysis Code
1. Called for bleed.
2. Scope down -> Blood everywhere.
3. Source LUL.
4. Tried saline/epi -> No stop.
5. Put balloon in LUL -> Stopped bleeding.
Plan: IR BAE."""
entities_4 = [
    {"label": "OBS_FINDING", **get_span(text_4, "Hemoptysis", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "Blood", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 1)},
    {"label": "MEDICATION", **get_span(text_4, "saline", 1)},
    {"label": "MEDICATION", **get_span(text_4, "epi", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "balloon", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LUL", 2)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "Stopped bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "IR", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAE", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 1923847_syn_5
# ==========================================
id_5 = "1923847_syn_5"
text_5 = """emergency bronch for marcus johnson bleeding out from the lul. massive amount of blood. tried iced saline didnt work. put a fogarty balloon up there and inflated it. that finally stopped the bleeding. ir is coming to coil the vessel."""
entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "bronch", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "bleeding", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lul", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "blood", 1)},
    {"label": "MEDICATION", **get_span(text_5, "iced saline", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fogarty balloon", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "stopped the bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "ir", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "coil", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 1923847_syn_6
# ==========================================
id_6 = "1923847_syn_6"
text_6 = """Emergency bronchoscopy was performed for massive hemoptysis. Findings revealed heavy bleeding from the LUL. Iced saline and epinephrine were ineffective. Balloon tamponade using a Fogarty catheter was performed, achieving hemostasis. The patient was stabilized and referred to IR for bronchial artery embolization."""
entities_6 = [
    {"label": "PROC_ACTION", **get_span(text_6, "bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "hemoptysis", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "bleeding", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LUL", 1)},
    {"label": "MEDICATION", **get_span(text_6, "Iced saline", 1)},
    {"label": "MEDICATION", **get_span(text_6, "epinephrine", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "tamponade", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "Fogarty catheter", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "hemostasis", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "IR", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "bronchial artery embolization", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 1923847_syn_7
# ==========================================
id_7 = "1923847_syn_7"
text_7 = """[Indication]
Massive Hemoptysis.
[Anesthesia]
Sedation (Intubated).
[Description]
LUL bleeding source id[REDACTED]. Balloon tamponade performed. Hemostasis achieved.
[Plan]
Angiography/Embolization."""
entities_7 = [
    {"label": "OBS_FINDING", **get_span(text_7, "Hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LUL", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "bleeding", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "tamponade", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "Hemostasis achieved", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Angiography", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Embolization", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 1923847_syn_8
# ==========================================
id_8 = "1923847_syn_8"
text_8 = """I was called to the ICU for [REDACTED] having massive bleeding from his lungs. I performed an emergency bronchoscopy and found the blood coming from the left upper lobe. Washing with cold saline didn't stop it, so I inserted a balloon catheter and inflated it to block the airway. This stopped the bleeding. He is now stable and heading to IR for a permanent fix."""
entities_8 = [
    {"label": "OBS_FINDING", **get_span(text_8, "bleeding", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lungs", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "blood", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "left upper lobe", 1)},
    {"label": "MEDICATION", **get_span(text_8, "cold saline", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "balloon catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "airway", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "stopped the bleeding", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "IR", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 1923847_syn_9
# ==========================================
id_9 = "1923847_syn_9"
text_9 = """Procedure: Emergency airway hemorrhage control.
Technique: Bronchoscopic balloon tamponade.
Site: Left Upper Lobe.
Outcome: Temporary cessation of hemoptysis. 
Disposition: Angiographic intervention."""
entities_9 = [
    {"label": "ANAT_AIRWAY", **get_span(text_9, "airway", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "hemorrhage", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "Bronchoscopic", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "balloon", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "tamponade", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "Left Upper Lobe", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_9, "cessation of hemoptysis", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Angiographic intervention", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 1923847
# ==========================================
id_10 = "1923847"
text_10 = """EMERGENCY BRONCHOSCOPY - HEMOPTYSIS
[REDACTED] - 02:35AM
Pt: [REDACTED], 57M, MRN [REDACTED]
CALLED FOR: Massive hemoptysis, ICU bed 8
Got called by ICU resident at 2am - patient with known left upper lobe cavitary lesion (likely TB vs fungal) started having massive hemoptysis, estimated 300cc bright red blood over 20 minutes. Oxygen sats dropping to high 80s. Already intubated by ICU team with 8.0 ETT.
RUSHED TO BEDSIDE
Arrived 02:15. Patient sedated on propofol/fent. Sats 91% on FiO2 100%, PEEP 10. Significant blood coming from ETT with suctioning.
SCOPE FINDINGS:
ETT in good position. Massive blood in trachea - suctioned approximately 50cc out just to see.
RIGHT SIDE: Clean, no blood, all segments patent and normal
LEFT SIDE: This is the source. Heavy bleeding coming from LUL. Can't see individual segments yet due to blood volume.
INITIAL MEASURES:

Iced saline lavage: 50cc aliquots x 4 = 200cc total through scope
Some temporary improvement but bleeding continues
Epi 1:10,000: 10cc instilled to LUL - minimal effect
Tranexamic acid: 500mg in 50mL saline instilled via bronch - slight reduction

BALLOON TAMPONADE:
Blood still coming. Advanced 7Fr Fogarty balloon catheter to LUL orifice. Inflated with 6cc saline. IMMEDIATE cessation of blood flow. Good seal.
Kept balloon inflated for 5 minutes. Deflated to check - slight oozing but much slower. Re-inflated for another 5 minutes.
Second deflation - persistent slow oozing from what looks like lingula now that I can see better. Advanced balloon to lingular orifice. Inflated with 4cc. Held 3 minutes. Deflated - bleeding stopped.
FINAL ASSESSMENT @ 03:15AM:
After tamponade cycles, bleeding under control. Can now visualize - appears to be coming from anterior segment LUL and lingula. Mucosa very friable. Likely bleeding from cavitary lesion eroding into vessels.
SPECIMENS: Blood sent for culture (TB, fungal)
PLAN:

ICU team notified - called IR for possible BAE (bronchial artery embolization)
Keep intubated, sedate, minimize suctioning
Reverse any coagulopathy (check labs)
CTA chest to id[REDACTED] bleeding vessel
IR consulted - agree with BAE plan, going to angio suite at 6am
I'll be on standby if rebleeds before IR
If rebleeds: will place endobronchial blocker to LUL for longer-term isolation

UPDATE 03:45AM: Patient stable, no further bleeding currently. IR taking to angio suite. Will follow up later this AM."""
entities_10 = [
    {"label": "PROC_ACTION", **get_span(text_10, "BRONCHOSCOPY", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "HEMOPTYSIS", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "hemoptysis", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "left upper lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "cavitary lesion", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "hemoptysis", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "300cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "blood", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "20 minutes", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "8.0", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "ETT", 1)},
    {"label": "MEDICATION", **get_span(text_10, "propofol", 1)},
    {"label": "MEDICATION", **get_span(text_10, "fent", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "blood", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "ETT", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "suctioning", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "ETT", 3)},
    {"label": "OBS_FINDING", **get_span(text_10, "blood", 3)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "trachea", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "50cc", 1)},
    {"label": "LATERALITY", **get_span(text_10, "RIGHT SIDE", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "blood", 4)},
    {"label": "LATERALITY", **get_span(text_10, "LEFT SIDE", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "bleeding", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "blood", 5)},
    {"label": "MEDICATION", **get_span(text_10, "Iced saline", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "lavage", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "50cc", 2)},
    {"label": "MEAS_VOL", **get_span(text_10, "200cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "bleeding", 2)},
    {"label": "MEDICATION", **get_span(text_10, "Epi", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "10cc", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 2)},
    {"label": "MEDICATION", **get_span(text_10, "Tranexamic acid", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "50mL", 1)},
    {"label": "MEDICATION", **get_span(text_10, "saline", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronch", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TAMPONADE", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "Blood", 1)},
    {"label": "MEAS_SIZE", **get_span(text_10, "7Fr", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "Fogarty balloon catheter", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LUL orifice", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "6cc", 1)},
    {"label": "MEDICATION", **get_span(text_10, "saline", 3)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "cessation of blood flow", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "balloon", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "5 minutes", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "oozing", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "5 minutes", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "oozing", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lingula", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "balloon", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "lingular orifice", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "4cc", 1)},
    {"label": "MEAS_TIME", **get_span(text_10, "3 minutes", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "bleeding stopped", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "bleeding", 3)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "anterior segment LUL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "lingula", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "bleeding", 4)},
    {"label": "OBS_LESION", **get_span(text_10, "cavitary lesion", 2)},
    {"label": "SPECIMEN", **get_span(text_10, "Blood", 2)},
    {"label": "PROC_METHOD", **get_span(text_10, "IR", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "BAE", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "bronchial artery embolization", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "IR", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "BAE", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "rebleeds", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "IR", 3)},
    {"label": "OBS_FINDING", **get_span(text_10, "rebleeds", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "endobronchial blocker", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LUL", 3)},
    {"label": "OBS_FINDING", **get_span(text_10, "bleeding", 5)},
    {"label": "PROC_METHOD", **get_span(text_10, "IR", 4)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)