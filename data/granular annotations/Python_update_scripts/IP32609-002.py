import sys
from pathlib import Path

# Set up the repository root path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(REPO_ROOT))

# Import the utility function
from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys, or None if not found.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            return None
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: IP32609-002_syn_1
# ==========================================
id_1 = "IP32609-002_syn_1"
text_1 = """Dx: R pleural thickening/effusion.
Proc: Med thoracoscopy.
Findings: 900cc serous fluid. Diffuse nodules/plaques parietal/diaphragmatic.
Action: 12 biopsies taken. No pleurodesis.
Plan: 24Fr chest tube. Admit."""
entities_1 = [
    {"label": "LATERALITY", **get_span(text_1, "R", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "pleural", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "thickening", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "effusion", 1)},
    {"label": "PROC_METHOD", **get_span(text_1, "Med thoracoscopy", 1)},
    {"label": "MEAS_VOL", **get_span(text_1, "900cc", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "serous fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "nodules", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "plaques", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_1, "diaphragmatic", 1)},
    {"label": "MEAS_COUNT", **get_span(text_1, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "pleurodesis", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_1, "24Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_1, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: IP32609-002_syn_2
# ==========================================
id_2 = "IP32609-002_syn_2"
text_2 = """OPERATIVE REPORT: Medical Thoracoscopy.
INDICATIONS: 69-year-old male with asbestos exposure and right-sided pleural thickening suspicious for malignant pleural mesothelioma.
DESCRIPTION: Under general anesthesia, the right hemithorax was accessed. Approximately 900 mL of serous fluid was aspirated. Thorough inspection demonstrated extensive nodular and plaque-like neoplastic-appearing thickening involving the parietal and diaphragmatic pleura. Twelve large-capacity biopsies were harvested for definitive histopathologic characterization. Pleurodesis was deferred pending final staging. A 24 Fr thoracostomy tube was secured."""
entities_2 = [
    {"label": "PROC_METHOD", **get_span(text_2, "Medical Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right-sided", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "thickening", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleural", 2)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "hemithorax", 1)},
    {"label": "MEAS_VOL", **get_span(text_2, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "serous fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "aspirated", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "nodular", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "plaque-like", 1)},
    {"label": "OBS_FINDING", **get_span(text_2, "thickening", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_2, "pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_2, "Twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Pleurodesis", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_2, "24 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_2, "thoracostomy tube", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: IP32609-002_syn_3
# ==========================================
id_3 = "IP32609-002_syn_3"
text_3 = """CPT: 32609 (Thoracoscopy, surgical; with biopsy of pleura).
Approach: Right 5th intercostal space via trocar.
Findings: Diffuse nodular thickening consistent with malignancy.
Intervention: Evacuation of 900 mL fluid. Multiple biopsies (n=12) obtained using rigid forceps for BAP1/MTAP testing.
Closure: 24 Fr chest tube inserted."""
entities_3 = [
    {"label": "PROC_METHOD", **get_span(text_3, "Thoracoscopy, surgical", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "pleura", 1)},
    {"label": "LATERALITY", **get_span(text_3, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_3, "5th intercostal space", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "trocar", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "nodular", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "thickening", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Evacuation", 1)},
    {"label": "MEAS_VOL", **get_span(text_3, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_3, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_3, "12", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "rigid forceps", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_3, "24 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_3, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: IP32609-002_syn_4
# ==========================================
id_4 = "IP32609-002_syn_4"
text_4 = """Resident Note: Medical Thoracoscopy
Patient: [REDACTED]
Attending: Dr. Stone
Indication: R effusion, r/o mesothelioma.
Procedure:
- GA / ETT.
- Port placed 5th ICS.
- Drained 900ml fluid.
- Saw nodules/plaques on pleura.
- Took 12 biopsies.
- Chest tube placed.
Complications: Minor oozing, cauterized."""
entities_4 = [
    {"label": "PROC_METHOD", **get_span(text_4, "Medical Thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_4, "R", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "effusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Port", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "5th ICS", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "Drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_4, "900ml", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "nodules", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "plaques", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_4, "pleura", 1)},
    {"label": "MEAS_COUNT", **get_span(text_4, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "biopsies", 1)},
    {"label": "DEV_CATHETER", **get_span(text_4, "Chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(text_4, "oozing", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "cauterized", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: IP32609-002_syn_5
# ==========================================
id_5 = "IP32609-002_syn_5"
text_5 = """thoracoscopy note for ryan brooks he has asbestos exposure and a right effusion suspicious for meso. did this under GA tube in. port in the 5th space drained 900 of fluid. looks like nodules everywhere especially diaphragm. took a bunch of biopsies like 12 of them. stopped a little bleeding with cautery. didn't do pleurodesis cause we need to know what it is first. chest tube is in."""
entities_5 = [
    {"label": "PROC_METHOD", **get_span(text_5, "thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "effusion", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "port", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "5th space", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "drained", 1)},
    # "900 of fluid" - volume unit missing but implied, skipped to adhere to strict unit mapping guidelines
    {"label": "OBS_FINDING", **get_span(text_5, "fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "nodules", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_5, "diaphragm", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "MEAS_COUNT", **get_span(text_5, "12", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "cautery", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_5, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: IP32609-002_syn_6
# ==========================================
id_6 = "IP32609-002_syn_6"
text_6 = """Medical thoracoscopy was performed under general anesthesia for a 69-year-old male with suspected mesothelioma. Access was established at the right 5th intercostal space. 900 mL of serous fluid was drained. The parietal and diaphragmatic pleura showed diffuse nodular thickening. Twelve biopsies were obtained using rigid forceps. Minor bleeding was controlled with cautery and epinephrine. A 24 Fr chest tube was placed. The patient was admitted to the thoracic surgery floor."""
entities_6 = [
    {"label": "PROC_METHOD", **get_span(text_6, "Medical thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_6, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "5th intercostal space", 1)},
    {"label": "MEAS_VOL", **get_span(text_6, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "serous fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "drained", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_6, "pleura", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "nodular", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "thickening", 1)},
    {"label": "MEAS_COUNT", **get_span(text_6, "Twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "rigid forceps", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "bleeding", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "cautery", 1)},
    {"label": "MEDICATION", **get_span(text_6, "epinephrine", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_6, "24 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_6, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: IP32609-002_syn_7
# ==========================================
id_7 = "IP32609-002_syn_7"
text_7 = """[Indication]
Suspected malignant pleural mesothelioma, R pleural thickening.
[Anesthesia]
General Anesthesia, ETT.
[Description]
900 mL fluid drained. Diffuse nodular/plaque-like thickening observed. 12 biopsies taken from parietal/diaphragmatic pleura. No pleurodesis.
[Plan]
Pathology/IHC. PET/CT pending results."""
entities_7 = [
    {"label": "ANAT_PLEURA", **get_span(text_7, "pleural", 1)},
    {"label": "LATERALITY", **get_span(text_7, "R", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "pleural", 2)},
    {"label": "OBS_FINDING", **get_span(text_7, "thickening", 1)},
    {"label": "MEAS_VOL", **get_span(text_7, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "drained", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "nodular", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "plaque-like", 1)},
    {"label": "OBS_FINDING", **get_span(text_7, "thickening", 2)},
    {"label": "MEAS_COUNT", **get_span(text_7, "12", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_7, "pleura", 3)},
    {"label": "PROC_ACTION", **get_span(text_7, "pleurodesis", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: IP32609-002_syn_8
# ==========================================
id_8 = "IP32609-002_syn_8"
text_8 = """The patient was brought to the operating room for a medical thoracoscopy to investigate suspected mesothelioma. After inducing general anesthesia, we accessed the right pleural space and drained 900 mL of fluid. The thoracoscopic view was significant for extensive nodular and plaque-like thickening covering the parietal and diaphragmatic pleura. We utilized rigid forceps to obtain twelve biopsies from these suspicious areas. Given the need for diagnostic clarity before staging, we opted not to perform pleurodesis. A chest tube was placed at the conclusion of the case."""
entities_8 = [
    {"label": "PROC_METHOD", **get_span(text_8, "medical thoracoscopy", 1)},
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleural space", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "drained", 1)},
    {"label": "MEAS_VOL", **get_span(text_8, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "fluid", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "nodular", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "plaque-like", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "thickening", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "parietal", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_8, "pleura", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "rigid forceps", 1)},
    {"label": "MEAS_COUNT", **get_span(text_8, "twelve", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "pleurodesis", 1)},
    {"label": "DEV_CATHETER", **get_span(text_8, "chest tube", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: IP32609-002_syn_9
# ==========================================
id_9 = "IP32609-002_syn_9"
text_9 = """Procedure: Thoracoscopic exploration and sampling.
Target: Right hemithorax.
Findings: 900mL serous fluid removed. Widespread nodularity/plaques noted. Tissue harvested (12 specimens) from chest wall and diaphragm. Hemostasis achieved. Drain positioned."""
entities_9 = [
    {"label": "PROC_METHOD", **get_span(text_9, "Thoracoscopic exploration", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampling", 1)},
    {"label": "LATERALITY", **get_span(text_9, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "hemithorax", 1)},
    {"label": "MEAS_VOL", **get_span(text_9, "900mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_9, "serous fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "removed", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "nodularity", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "plaques", 1)},
    {"label": "MEAS_COUNT", **get_span(text_9, "12", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "chest wall", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_9, "diaphragm", 1)},
    {"label": "DEV_CATHETER", **get_span(text_9, "Drain", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: IP32609-002
# ==========================================
id_10 = "IP32609-002"
text_10 = """Interventional Pulmonology Procedure Note
Procedure: Medical thoracoscopy with pleural biopsies for suspected pleural mesothelioma.
Patient: [REDACTED], 69-year-old male with occupational asbestos exposure and right pleural thickening with effusion.
Anesthesia: General anesthesia with single-lumen ETT.
Indication: Progressive right pleural thickening and moderate effusion seen on CT; need tissue diagnosis.
Procedure details: Right 5th intercostal space, midaxillary line, was chosen under ultrasound. After trocar placement, 900 mL of serous fluid was drained. Thoracoscopy revealed diffuse nodular and plaque-like thickening of the parietal pleura, especially over the diaphragmatic and posterior chest wall. Multiple large biopsies (12 samples) were obtained with rigid forceps from representative areas. No pleurodesis was performed due to diagnostic intent and uncertain staging plan. A 24 Fr chest tube was placed to water seal.
Complications: Mild oozing at biopsy sites controlled with cautery and topical epinephrine.
Estimated blood loss: 50 mL.
Disposition: Admitted to thoracic surgery floor.
Plan: Send specimens for histology and BAP1/MTAP staining; PET/CT and multidisciplinary tumor board discussion after diagnosis."""
entities_10 = [
    {"label": "PROC_METHOD", **get_span(text_10, "Medical thoracoscopy", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 2)},
    {"label": "LATERALITY", **get_span(text_10, "right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 3)},
    {"label": "OBS_FINDING", **get_span(text_10, "thickening", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "effusion", 1)},
    {"label": "LATERALITY", **get_span(text_10, "right", 2)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "pleural", 4)},
    {"label": "OBS_FINDING", **get_span(text_10, "thickening", 2)},
    {"label": "OBS_FINDING", **get_span(text_10, "effusion", 2)},
    {"label": "LATERALITY", **get_span(text_10, "Right", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "5th intercostal space", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "ultrasound", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "trocar", 1)},
    {"label": "MEAS_VOL", **get_span(text_10, "900 mL", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "serous fluid", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "drained", 1)},
    {"label": "PROC_METHOD", **get_span(text_10, "Thoracoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "nodular", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "plaque-like", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "thickening", 3)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "parietal pleura", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "diaphragmatic", 1)},
    {"label": "ANAT_PLEURA", **get_span(text_10, "posterior chest wall", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "biopsies", 2)},
    {"label": "MEAS_COUNT", **get_span(text_10, "12", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_10, "rigid forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "pleurodesis", 1)},
    {"label": "DEV_CATHETER_SIZE", **get_span(text_10, "24 Fr", 1)},
    {"label": "DEV_CATHETER", **get_span(text_10, "chest tube", 1)},
    {"label": "OBS_FINDING", **get_span(text_10, "oozing", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "cautery", 1)},
    {"label": "MEDICATION", **get_span(text_10, "epinephrine", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)