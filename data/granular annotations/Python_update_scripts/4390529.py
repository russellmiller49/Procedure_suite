import sys
from pathlib import Path

# Set up the repository root path
# Assuming this script is running in a structure like: repo/scripts/your_script.py
# We want to import from repo/scripts/add_training_case.py
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

try:
    from scripts.add_training_case import add_case
except ImportError:
    print("Warning: Could not import 'add_case'. Ensure the script is run from the correct context.")
    # Mocking add_case for standalone testing purposes if import fails
    def add_case(case_id, text, entities, root):
        print(f"Processing {case_id} with {len(entities)} entities.")

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            break
            
    if start != -1:
        return {"start": start, "end": start + len(term)}
    else:
        raise ValueError(f"Term '{term}' not found {occurrence} times in text.")

# ==========================================
# Note 1: 4390529_syn_1
# ==========================================
text_1 = """Indication: Malignant CAO RLL.
Findings: 78% obstruction.
Procedure:
- Rigid bronch.
- APC tumor destruction/debulking.
- Multiple passes.
Result: 18% residual. Hemostasis achieved.
EBL: 50ml.
Plan: ICU."""

entities_1 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    # Observations/Lesions
    {"label": "OBS_LESION", **get_span(text_1, "tumor", 1)},
    # Measurements/Outcomes
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_1, "78% obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_1, "18% residual", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_1, "Hemostasis achieved", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "50ml", 1)},
    # Procedures/Actions
    {"label": "PROC_METHOD", **get_span(text_1, "Rigid bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "destruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "debulking", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_1", "text": text_1, "entities": entities_1})


# ==========================================
# Note 2: 4390529_syn_2
# ==========================================
text_2 = """OPERATIVE REPORT: [REDACTED] malignant central airway obstruction at the right lower lobe (RLL) orifice. Under general anesthesia, rigid bronchoscopy revealed an endobronchial tumor causing 78% occlusion. Thermal ablation was performed utilizing Argon Plasma Coagulation (APC), followed by mechanical debulking. This sequence was repeated to maximize luminal gain. Post-intervention assessment showed a significant reduction in tumor burden with 18% residual obstruction. Hemostasis was secured via APC application to the tumor base."""

entities_2 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "right lower lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(text_2, "tumor", 3)},
    # Measurements/Outcomes
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_2, "78% occlusion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_2, "18% residual obstruction", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_2, "Hemostasis was secured", 1)},
    # Procedures
    {"label": "PROC_METHOD", **get_span(text_2, "rigid bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Thermal ablation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "Argon Plasma Coagulation", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "mechanical debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_2, "APC", 2)},
]
BATCH_DATA.append({"id": "4390529_syn_2", "text": text_2, "entities": entities_2})


# ==========================================
# Note 3: 4390529_syn_3
# ==========================================
text_3 = """CPT Code: 31641 (Bronchoscopy with destruction of tumor).
Modality: Argon Plasma Coagulation (APC).
Location: RLL Orifice.
Work Performed:
- Id[REDACTED] of tumor (78% occlusion).
- Thermal destruction of tissue.
- Mechanical removal of debris.
- Hemostasis.
Outcome: Obstruction reduced to 18%."""

entities_3 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 2)},
    # Measurements/Outcomes
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_3, "78% occlusion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_3, "Obstruction reduced to 18%", 1)},
    # Procedures
    {"label": "PROC_METHOD", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "destruction", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "Argon Plasma Coagulation", 1)},
    {"label": "PROC_METHOD", **get_span(text_3, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Thermal destruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "removal", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Hemostasis", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_3", "text": text_3, "entities": entities_3})


# ==========================================
# Note 4: 4390529_syn_4
# ==========================================
text_4 = """Procedure: Tumor Debulking (APC)
Patient: [REDACTED]
Steps:
1. Rigid bronchoscopy initiated.
2. Tumor found at RLL orifice (78%).
3. APC applied for destruction.
4. Debris removed.
5. Repeat until maximal debulking achieved (18% residual).
6. Hemostasis confirmed.
Plan: ICU observation."""

entities_4 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_4, "Tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Tumor", 2)},
    # Measurements/Outcomes
    # Note: "78%" alone is ambiguous but clearly implies obstruction in this context, 
    # but strictly per guide, usually requires unit or descriptor like "obstruction". 
    # Skipping "78%" to be safe, or mapping if "obstruction" implied by "Tumor... (78%)".
    # I will stick to explicit phrases. "18% residual" is explicit.
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_4, "18% residual", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "Hemostasis confirmed", 1)},
    # Procedures
    {"label": "PROC_ACTION", **get_span(text_4, "Debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "APC", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "Rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_4, "APC", 2)},
    {"label": "PROC_ACTION", **get_span(text_4, "destruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "removed", 1)},
    # CORRECTED: Changed occurrence from 2 to 1 because "debulking" (lowercase) only appears once.
    # The first "Debulking" is title case, which get_span treats as distinct.
    {"label": "PROC_ACTION", **get_span(text_4, "debulking", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_4", "text": text_4, "entities": entities_4})


# ==========================================
# Note 5: 4390529_syn_5
# ==========================================
text_5 = """Daniel Allen here for debulking of a tumor in the RLL it was blocking about 78 percent. We used the rigid scope and the APC argon plasma to burn and remove the tumor. Did a few passes and got it down to 18 percent. Bleeding was controlled about 50cc loss. Sending him to the ICU for tonight just to be safe."""

entities_5 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "RLL", 1)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 2)},
    # Measurements/Outcomes
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_5, "blocking about 78 percent", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_5, "down to 18 percent", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_5, "Bleeding was controlled", 1)},
    {"label": "MEAS_VOL", **get_span(text_5, "50cc", 1)},
    # Procedures
    {"label": "PROC_ACTION", **get_span(text_5, "debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "rigid scope", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "APC", 1)},
    {"label": "PROC_METHOD", **get_span(text_5, "argon plasma", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "remove", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_5", "text": text_5, "entities": entities_5})


# ==========================================
# Note 6: 4390529_syn_6
# ==========================================
text_6 = """Indication: Malignant central airway obstruction with ~78% obstruction at RLL orifice. Under general anesthesia, rigid bronchoscopy was performed. Endobronchial tumor was id[REDACTED] at the RLL orifice. Argon plasma coagulation (APC) was performed with sequential tumor removal. Multiple passes were performed to achieve maximal debulking. Additional APC/laser was used for hemostasis and tumor base ablation. Post-procedure obstruction was ~18%. EBL was ~50mL and hemostasis was achieved. Specimens were sent for histology."""

entities_6 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 2)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(text_6, "tumor", 3)},
    # Measurements/Outcomes
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_6, "~78% obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_6, "obstruction was ~18%", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "~50mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "hemostasis was achieved", 1)},
    # Procedures
    {"label": "PROC_METHOD", **get_span(text_6, "rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "Argon plasma coagulation", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "removal", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_6, "APC", 2)},
    {"label": "PROC_METHOD", **get_span(text_6, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "hemostasis", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "ablation", 1)},
    {"label": "SPECIMEN", **get_span(text_6, "Specimens", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_6", "text": text_6, "entities": entities_6})


# ==========================================
# Note 7: 4390529_syn_7
# ==========================================
text_7 = """[Indication]
Malignant CAO, RLL orifice (78%).
[Anesthesia]
General, Rigid Bronch.
[Description]
APC destruction of tumor performed. Sequential removal. Hemostasis achieved. Residual obstruction 18%.
[Plan]
ICU observation. Oncology follow-up."""

entities_7 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_7, "tumor", 1)},
    # Measurements/Outcomes
    # "78%" in parens next to indication: context implies obstruction.
    # Guide example: "~80% obstruction". "78%" alone is borderline, but "Residual obstruction 18%" validates the metric.
    # I will strictly label "Residual obstruction 18%" and likely skip "78%" to avoid false positives unless "obstruction" is explicit in the span.
    # Actually, guide says "Only when explicit... measurement/grade stated".
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_7, "Residual obstruction 18%", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "Hemostasis achieved", 1)},
    # Procedures
    {"label": "PROC_METHOD", **get_span(text_7, "Rigid Bronch", 1)},
    {"label": "PROC_METHOD", **get_span(text_7, "APC", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "destruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "removal", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_7", "text": text_7, "entities": entities_7})


# ==========================================
# Note 8: 4390529_syn_8
# ==========================================
text_8 = """[REDACTED] bronchoscopy for a tumor obstructing his right lower lobe bronchus by about 78%. We used argon plasma coagulation to destroy the tumor tissue and removed it sequentially. After several passes, we successfully debulked the lesion down to an 18% residual obstruction. We ensured all bleeding was stopped using APC. He is going to the ICU for overnight monitoring."""

entities_8 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "right lower lobe", 1)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 1)},
    # Measurements/Outcomes
    # "obstructing... by about 78%" captures the metric.
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_8, "obstructing his right lower lobe bronchus by about 78%", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_8, "18% residual obstruction", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "bleeding was stopped", 1)},
    # Procedures
    {"label": "PROC_METHOD", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "argon plasma coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "destroy", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "removed", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "debulked", 1)},
    {"label": "PROC_METHOD", **get_span(text_8, "APC", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_8", "text": text_8, "entities": entities_8})


# ==========================================
# Note 9: 4390529_syn_9
# ==========================================
text_9 = """Indication: Malignant central airway blockage.
Pre-procedure: ~78% occlusion at RLL orifice.
PROCEDURE: Under general anesthesia, rigid bronchoscopy was conducted. Endobronchial neoplasm found at RLL orifice. APC (argon plasma coagulation) was utilized with sequential tumor extraction. Multiple passes were done to attain maximal volume reduction. Additional APC/laser used for hemostasis and tumor base cauterization.
Post-procedure: ~18% residual occlusion.
EBL: ~50mL."""

entities_9 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 2)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_9, "neoplasm", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 2)},
    # Measurements/Outcomes
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_9, "~78% occlusion", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_9, "~18% residual occlusion", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "~50mL", 1)},
    # Procedures
    {"label": "PROC_METHOD", **get_span(text_9, "rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "APC", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "argon plasma coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "extraction", 1)},
    {"label": "PROC_METHOD", **get_span(text_9, "APC", 2)},
    {"label": "PROC_METHOD", **get_span(text_9, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "hemostasis", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "cauterization", 1)},
]
BATCH_DATA.append({"id": "4390529_syn_9", "text": text_9, "entities": entities_9})


# ==========================================
# Note 10: 4390529 (Original)
# ==========================================
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
Attending: Dr. Christopher Brown
Fellow: Dr. Lauren Walsh (PGY-6)

Indication: Malignant central airway obstruction
Pre-procedure: ~78% obstruction at RLL orifice

PROCEDURE:
Under general anesthesia, rigid bronchoscopy performed.
Endobronchial tumor id[REDACTED] at RLL orifice.
Apc (argon plasma coagulation) performed with sequential tumor removal.
Multiple passes performed to achieve maximal debulking.
Additional APC/laser used for hemostasis and tumor base ablation.
Post-procedure: ~18% residual obstruction.
EBL: ~50mL. Hemostasis achieved.
Specimens sent for histology.

DISPOSITION: Recovery then ICU observation overnight.
Plan: Consider stent if re-obstruction. Oncology f/u.

Brown, MD"""

entities_10 = [
    # Anatomy
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 2)},
    # Observations
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "tumor", 3)},
    # Measurements/Outcomes
    {"label": "OUTCOME_AIRWAY_LUMEN_PRE", **get_span(text_10, "~78% obstruction", 1)},
    {"label": "OUTCOME_AIRWAY_LUMEN_POST", **get_span(text_10, "~18% residual obstruction", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "~50mL", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Hemostasis achieved", 1)},
    # Procedures
    {"label": "PROC_METHOD", **get_span(text_10, "rigid bronchoscopy", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Apc", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "argon plasma coagulation", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "removal", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "debulking", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "APC", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "hemostasis", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "ablation", 1)},
    {"label": "SPECIMEN", **get_span(text_10, "Specimens", 1)},
]
BATCH_DATA.append({"id": "4390529", "text": text_10, "entities": entities_10})


if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)
    print("Batch processing complete.")