import sys
from pathlib import Path

# Set up the repository root directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term)
    }

# ==========================================
# Note 1: 781244_syn_1
# ==========================================
t1 = """Indication: Hypoxemia, mucus plugging.
Proc: Therapeutic bronchoscopy.
Findings: Thick secretions R lung.
Action: Suctioned R main/RML/RLL. Saline lavage.
Result: Airways patent. Improved saturations.
Plan: Wean vent."""

e1 = [
    {"label": "OBS_FINDING", **get_span(t1, "mucus plugging", 1)},
    {"label": "OBS_FINDING", **get_span(t1, "Thick secretions", 1)},
    {"label": "LATERALITY", **get_span(t1, "R", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "lung", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "Suctioned", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "R main", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "RLL", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "lavage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t1, "Airways", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t1, "patent", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t1, "Improved saturations", 1)}
]
BATCH_DATA.append({"id": "781244_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 781244_syn_2
# ==========================================
t2 = """PROCEDURE NOTE: Bedside Therapeutic Bronchoscopy.
INDICATION: Acute hypoxemic respiratory failure secondary to severe pneumonia and suspected mucus plugging.
PROCEDURE: The bronchoscope was introduced via the endotracheal tube. Significant tenacious, purulent secretions were id[REDACTED] obstructing the right bronchial tree. Extensive therapeutic aspiration and saline lavage were performed until the airways were patent. The left lung was relatively clear. 
IMPRESSION: Successful clearance of mucous plugs leading to immediate improvement in ventilator mechanics."""

e2 = [
    {"label": "OBS_FINDING", **get_span(t2, "mucus plugging", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "secretions", 1)},
    {"label": "LATERALITY", **get_span(t2, "right", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "bronchial tree", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "aspiration", 1)},
    {"label": "PROC_ACTION", **get_span(t2, "lavage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t2, "airways", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t2, "patent", 1)},
    {"label": "LATERALITY", **get_span(t2, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t2, "lung", 1)},
    {"label": "OBS_FINDING", **get_span(t2, "mucous plugs", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t2, "improvement in ventilator mechanics", 1)}
]
BATCH_DATA.append({"id": "781244_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 781244_syn_3
# ==========================================
t3 = """Code Selection: 31645 (Therapeutic aspiration of tracheobronchial tree).
Justification: Procedure performed for initial therapeutic purposes to resolve mucus plugging causing respiratory failure. Extensive suctioning and lavage required to clear right mainstem, RML, and RLL bronchi. No biopsy or diagnostic washing performed."""

e3 = [
    {"label": "PROC_ACTION", **get_span(t3, "aspiration", 1)},
    {"label": "OBS_FINDING", **get_span(t3, "mucus plugging", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "suctioning", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "lavage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "right mainstem", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t3, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t3, "bronchi", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(t3, "washing", 1)}
]
BATCH_DATA.append({"id": "781244_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 781244_syn_4
# ==========================================
t4 = """Procedure: Bronchoscopy (ICU)
Resident: Dr. Resident
Attending: Dr. Holloway
1. Time out.
2. Scope down ETT.
3. R lung full of mucus. Suctioned.
4. Lavaged with saline.
5. Cleared RML/RLL.
6. L lung okay.
7. Pt tolerated well."""

e4 = [
    {"label": "LATERALITY", **get_span(t4, "R", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "lung", 1)},
    {"label": "OBS_FINDING", **get_span(t4, "mucus", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Suctioned", 1)},
    {"label": "PROC_ACTION", **get_span(t4, "Lavaged", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "RLL", 1)},
    {"label": "LATERALITY", **get_span(t4, "L", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t4, "lung", 2)}
]
BATCH_DATA.append({"id": "781244_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 781244_syn_5
# ==========================================
t5 = """bedside bronch for [REDACTED] up again tube in place went down with the scope tons of thick junk on the right side vacuumed it all out used some saline took a while but got it open left side looked fine no masses or anything just pneumonia improving sats afterwards."""

e5 = [
    {"label": "OBS_FINDING", **get_span(t5, "thick junk", 1)},
    {"label": "LATERALITY", **get_span(t5, "right side", 1)},
    {"label": "LATERALITY", **get_span(t5, "left side", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t5, "improving sats", 1)}
]
BATCH_DATA.append({"id": "781244_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 781244_syn_6
# ==========================================
t6 = """Flexible bronchoscopy was performed at the bedside for mucus plugging. The patient was already intubated. Examination revealed copious thick secretions in the right lung. These were aspirated. Saline was instilled to facilitate removal. The right middle and lower lobes were cleared. The left lung was inspected and found to be patent. The patient's respiratory status improved following the intervention."""

e6 = [
    {"label": "OBS_FINDING", **get_span(t6, "mucus plugging", 1)},
    {"label": "OBS_FINDING", **get_span(t6, "thick secretions", 1)},
    {"label": "LATERALITY", **get_span(t6, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "lung", 1)},
    {"label": "PROC_ACTION", **get_span(t6, "aspirated", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "right middle", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "lower lobes", 1)},
    {"label": "LATERALITY", **get_span(t6, "left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t6, "lung", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t6, "patent", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t6, "respiratory status improved", 1)}
]
BATCH_DATA.append({"id": "781244_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 781244_syn_7
# ==========================================
t7 = """[Indication]
Acute hypoxemic respiratory failure, mucus plugging.
[Anesthesia]
ICU Sedation (Propofol/Fentanyl).
[Description]
Therapeutic aspiration performed. Large mucus plugs removed from R main/RML/RLL. Lavage utilized. Airways cleared.
[Plan]
Continue mechanical ventilation. Monitor secretions."""

e7 = [
    {"label": "OBS_FINDING", **get_span(t7, "mucus plugging", 1)},
    {"label": "MEDICATION", **get_span(t7, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(t7, "Fentanyl", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "aspiration", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "mucus plugs", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "R main", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RML", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t7, "RLL", 1)},
    {"label": "PROC_ACTION", **get_span(t7, "Lavage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t7, "Airways", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t7, "cleared", 1)},
    {"label": "OBS_FINDING", **get_span(t7, "secretions", 1)}
]
BATCH_DATA.append({"id": "781244_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 781244_syn_8
# ==========================================
t8 = """Dr. Holloway performed a bedside bronchoscopy on [REDACTED] her dropping oxygen levels. We passed the scope through her breathing tube and immediately found heavy mucus blocking the right lung. We spent significant time suctioning and washing the area with saline until the breathing tubes were clear. The left side looked much better. Afterward, her ventilator pressures went down, which is a good sign."""

e8 = [
    {"label": "OBS_FINDING", **get_span(t8, "heavy mucus", 1)},
    {"label": "LATERALITY", **get_span(t8, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t8, "lung", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "suctioning", 1)},
    {"label": "PROC_ACTION", **get_span(t8, "washing", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t8, "clear", 1)},
    {"label": "LATERALITY", **get_span(t8, "left side", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t8, "ventilator pressures went down", 1)}
]
BATCH_DATA.append({"id": "781244_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 781244_syn_9
# ==========================================
t9 = """Intervention: Bronchoscopic airway clearance.
Reason: Compromised oxygenation due to bronchial obstruction.
Technique: The endoscope was navigated through the airway. Copious exudate was evacuated from the right hemithorax using suction and lavage. The bronchial lumen was restored. 
Outcome: Improved aeration."""

e9 = [
    {"label": "ANAT_AIRWAY", **get_span(t9, "airway", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "bronchial", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "airway", 2)},
    {"label": "OBS_FINDING", **get_span(t9, "Copious exudate", 1)},
    {"label": "LATERALITY", **get_span(t9, "right", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "suction", 1)},
    {"label": "PROC_ACTION", **get_span(t9, "lavage", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t9, "bronchial lumen", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t9, "Improved aeration", 1)}
]
BATCH_DATA.append({"id": "781244_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 781244
# ==========================================
t10 = """BRONCHOSCOPY NOTE - ICU BEDSIDE
Date: [REDACTED]
Patient: [REDACTED] | 68F | MRN [REDACTED]
Location: [REDACTED]
Attending: Dr. James Holloway
Indication: Acute hypoxemic respiratory failure with suspected mucus plugging of right lung in patient with severe COPD and pneumonia on mechanical ventilation.
Airway: 7.5 ETT at 22 cm, ventilator VC 16/400/5/60%
Sedation: Propofol and fentanyl infusions running; no additional IV pushes documented.

Procedure:
- Flexible bronchoscope passed through the ETT under continuous cardiac and pulse ox monitoring.
- Large amounts of thick tenacious secretions suctioned from right mainstem, right middle lobe and right lower lobe bronchi.
- Saline instillation and repeated therapeutic aspiration until airways cleared.
- No biopsies, brushings, BAL or EBUS performed.
- Left lung inspected; minimal thin secretions suctioned, no lesions.

Findings:
- Diffuse purulent secretions consistent with pneumonia.
- No endobronchial mass or foreign body.

Complications: None. Estimated blood loss <5 mL.
Disposition: Remains intubated in ICU with improved breath sounds and lower peak pressures; repeat bronchoscopy only if clinically indicated."""

e10 = [
    {"label": "OBS_FINDING", **get_span(t10, "mucus plugging", 1)},
    {"label": "LATERALITY", **get_span(t10, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "lung", 1)},
    {"label": "MEDICATION", **get_span(t10, "Propofol", 1)},
    {"label": "MEDICATION", **get_span(t10, "fentanyl", 1)},
    {"label": "OBS_FINDING", **get_span(t10, "thick tenacious secretions", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "suctioned", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "right mainstem", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "right middle lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "right lower lobe", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "bronchi", 1)},
    {"label": "PROC_ACTION", **get_span(t10, "aspiration", 1)},
    {"label": "ANAT_AIRWAY", **get_span(t10, "airways", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(t10, "cleared", 1)},
    {"label": "LATERALITY", **get_span(t10, "Left", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(t10, "lung", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 2)},
    {"label": "PROC_ACTION", **get_span(t10, "suctioned", 2)},
    {"label": "OBS_FINDING", **get_span(t10, "secretions", 3)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "improved breath sounds", 1)},
    {"label": "OUTCOME_SYMPTOMS", **get_span(t10, "lower peak pressures", 1)}
]
BATCH_DATA.append({"id": "781244", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)