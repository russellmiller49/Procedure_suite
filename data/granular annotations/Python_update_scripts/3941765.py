import sys
from pathlib import Path

# Set up REPO_ROOT to point to the root of the repository
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: 3941765_syn_1
# ==========================================
id_1 = "3941765_syn_1"
text_1 = """Dx: Thyroid CA compression/invasion RLL (80%).
Procedure: Rigid Bronchoscopy.
Actions:
- APC debulking of RLL tumor.
- Multiple passes.
- APC/Laser for hemostasis.
Result: 24% residual. EBL 200mL.
Plan: ICU."""

entities_1 = [
    {"label": "OBS_LESION", **get_span(text_1, "Thyroid CA", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "80%", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "debulking", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_1, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "APC", 2)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "Laser", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "24% residual", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "200mL", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 3941765_syn_2
# ==========================================
id_2 = "3941765_syn_2"
text_2 = """OPERATIVE REPORT: [REDACTED] airway compromise due to thyroid carcinoma invading the Right Lower Lobe (RLL) orifice (80% obstruction). Rigid bronchoscopy was undertaken. The tumor was addressed primarily via Argon Plasma Coagulation (APC) for devitalization and debulking, performed in sequential passes. Laser energy was utilized adjunctively for tumor base ablation and hemostasis. Post-procedure evaluation showed a patent RLL orifice with 24% residual obstruction. EBL was approximately 200mL."""

entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "thyroid carcinoma", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "Right Lower Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "orifice", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "80% obstruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Argon Plasma Coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Laser", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_2, "ablation", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "orifice", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "24% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "200mL", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 3941765_syn_3
# ==========================================
id_3 = "3941765_syn_3"
text_3 = """Coding: 31641 (Bronchoscopy with destruction of tumor, e.g., laser, APC, cryo).
Site: RLL Orifice.
Technique: APC debulking and Laser ablation.
Condition: Malignant obstruction (Thyroid CA).
Outcome: Improvement from 80% to 24% obstruction."""

entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "APC", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Orifice", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "APC", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "debulking", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "ablation", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "Thyroid CA", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "80%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "24% obstruction", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 3941765_syn_4
# ==========================================
id_4 = "3941765_syn_4"
text_4 = """Procedure: RLL APC Debulking
Pt: [REDACTED], 54M
Indication: Thyroid CA.
Steps:
1. GA, Rigid scope.
2. Found RLL tumor.
3. Used APC to debulk it.
4. Used Laser for bleeding/cleanup.
5. RLL open now (24% residual).
6. 200cc blood loss, controlled.
Plan: ICU."""

entities_4 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Debulking", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Thyroid CA", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Rigid scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_4, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "APC", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "debulk", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Laser", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 3)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "24% residual", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "200cc", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 3941765_syn_5
# ==========================================
id_5 = "3941765_syn_5"
text_5 = """Kenneth Green 54 male thyroid cancer pushing into the RLL about 80 percent blocked. We went in with the rigid scope. Used the APC to burn and remove the tumor. Did a bunch of passes. Used laser too for the bleeding. Lost about 200ml blood but stopped it. RLL is open to 24 percent obstruction now. ICU for him."""

entities_5 = [
    {"label": "OBS_LESION", **get_span(text_5, "thyroid cancer", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RLL", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "80 percent blocked", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "rigid scope", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "APC", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "laser", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "200ml", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RLL", 2)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "24 percent obstruction", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 3941765_syn_6
# ==========================================
id_6 = "3941765_syn_6"
text_6 = """Under general anesthesia, rigid bronchoscopy performed. Endobronchial tumor id[REDACTED] at RLL orifice. Apc (argon plasma coagulation) performed with sequential tumor removal. Multiple passes performed to achieve maximal debulking. Additional APC/laser used for hemostasis and tumor base ablation. Post-procedure: ~24% residual obstruction. EBL: ~200mL. Hemostasis achieved. Specimens sent for histology."""

entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "Endobronchial tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "orifice", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Apc", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "argon plasma coagulation", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_6, "removal", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "laser", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 3)},
    {"label": "PROC_ACTION", **get_span(text_6, "ablation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "24% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "200mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "Hemostasis achieved", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "Specimens", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 3941765_syn_7
# ==========================================
id_7 = "3941765_syn_7"
text_7 = """[Indication]
Thyroid cancer with 80% obstruction at RLL orifice.
[Anesthesia]
General anesthesia.
[Description]
Rigid bronchoscopy. APC debulking of RLL tumor performed. Laser used for hemostasis. Residual obstruction 24%. EBL 200mL.
[Plan]
ICU observation. Oncology follow-up."""

entities_7 = [
    {"label": "OBS_LESION", **get_span(text_7, "Thyroid cancer", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_7, "80% obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "orifice", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "debulking", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Laser", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "Residual obstruction 24%", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "200mL", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 3941765_syn_8
# ==========================================
id_8 = "3941765_syn_8"
text_8 = """We performed a rigid bronchoscopy on [REDACTED] the tumor obstructing his RLL orifice. Using Argon Plasma Coagulation (APC), we sequentially debulked the tumor tissue. We also used laser therapy to ablate the base and control bleeding. The procedure successfully reduced the obstruction from 80% to 24%, with about 200mL of blood loss which was controlled."""

entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "orifice", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "Argon Plasma Coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "debulked", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor tissue", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "ablate", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "80%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "24%", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "200mL", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 3941765_syn_9
# ==========================================
id_9 = "3941765_syn_9"
text_9 = """Procedure: Rigid bronchoscopy with thermal ablation of neoplasm.
Site: RLL orifice.
Method: Argon Plasma Coagulation (APC) was employed for tumor reduction. Laser energy was applied for hemostasis.
Result: Blockage reduced to 24%."""

entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "thermal ablation", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "neoplasm", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "orifice", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Argon Plasma Coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "APC", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "reduction", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Laser", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "24%", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 3941765
# ==========================================
id_10 = "3941765"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: 6/7/1971
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. David Wilson

Indication: Thyroid cancer with tracheal compression
Pre-procedure: ~80% obstruction at RLL orifice

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at RLL orifice.
Apc (argon plasma coagulation) performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Additional APC/laser used for hemostasis and tumor base ablation.
Post-procedure: ~24% residual obstruction.
EBL: ~200mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Wilson, MD"""

entities_10 = [
    {"label": "OBS_LESION", **get_span(text_10, "Thyroid cancer", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "tracheal", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "80% obstruction", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "orifice", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "rigid bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "Endobronchial tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "orifice", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "Apc", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "argon plasma coagulation", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "removal", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "debulking", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "APC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "laser", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 3)},
    {"label": "PROC_ACTION", **get_span(text_10, "ablation", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "24% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "200mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Hemostasis achieved", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Specimens", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)