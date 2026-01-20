import sys
from pathlib import Path

# Set up the repository root path
# This assumes the script is running from the expected directory structure
REPO_ROOT = Path(__file__).resolve().parent.parent

# Add the scripts directory to the path so we can import the utility
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start' and 'end' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

BATCH_DATA = []

# ==========================================
# Note 1: 4744854_syn_1
# ==========================================
text_1 = """Pre-op: RLL bronchus SCC (T1a). Pt declined surgery.
Anesthesia: GA, 8.0 ETT.
Procedure:
- Bronchoscopy: Normal upper airway.
- Tumor: RLL, 1.2x1.1cm, flat/plaque.
- PDT: 630nm laser via 3cm diffuser. 200 J/cm2. 500s. 1.2W.
- No visible change/bleeding.
Plan: Extubate. Light precautions. F/u 48h for debridement."""

entities_1 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "bronchus", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "SCC", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "Bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "Tumor", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 2)},
    {"label": "MEAS_SIZE", **get_span(text_1, "1.2x1.1cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_1, "flat/plaque", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "PDT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "laser", 1)},
    {"label": "MEAS_SIZE", **get_span(text_1, "3cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_1, "diffuser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_1, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(text_1, "500s", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_1, "1.2W", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "debridement", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_1", "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 4744854_syn_2
# ==========================================
text_2 = """OPERATIVE NARRATIVE: The patient, [REDACTED], presenting with Stage IA1 endobronchial squamous cell carcinoma of the right lower lobe, was brought to the operating theater for photodynamic therapy. Following induction of general anesthesia, the airway was secured. A thorough bronchoscopic interrogation id[REDACTED] the lesion within the RLL bronchus. A cylindrical diffusing fiber (3.0 cm) was positioned centrally across the malignancy. Laser energy at 630 nm was delivered to achieve a total fluence of 200 J/cm², activating the previously administered Porfimer sodium. The procedure concluded without hemodynamic instability or immediate localized tissue reaction."""

entities_2 = [
    {"label": "OBS_LESION", **get_span(text_2, "squamous cell carcinoma", 1)},
    {"label": "LATERALITY", **get_span(text_2, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "lower lobe", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "photodynamic therapy", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "lesion", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "bronchus", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "cylindrical diffusing fiber", 1)},
    {"label": "MEAS_SIZE", **get_span(text_2, "3.0 cm", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "malignancy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_2, "Laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_2, "200 J/cm²", 1)},
    {"label": "MEDICATION", **get_span(text_2, "Porfimer sodium", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_2", "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 4744854_syn_3
# ==========================================
text_3 = """Procedure: Bronchoscopy with destruction of tumor (CPT 31641).
Technique: Photodynamic Therapy (PDT).
Device: 630nm Diode Laser, 3.0cm Diffusing Fiber.
Dosimetry: Power 1.2W, Fluence 200 J/cm2, Duration 500s.
Target: Right Lower Lobe (RLL) endobronchial tumor.
Justification: Destruction of malignant tissue via photochemical activation of photosensitizer. Pre-procedure calculation confirmed dosimetry. Safety protocols followed."""

entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "Bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "destruction", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "Photodynamic Therapy", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "PDT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "630nm Diode Laser", 1)},
    {"label": "MEAS_SIZE", **get_span(text_3, "3.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "Diffusing Fiber", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_3, "1.2W", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_3, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(text_3, "500s", 1)},
    {"label": "LATERALITY", **get_span(text_3, "Right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "Lower Lobe", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_3, "tumor", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "Destruction", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_3", "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 4744854_syn_4
# ==========================================
text_4 = """Procedure: PDT Light Application
Attending: Dr. Walsh
Steps:
1. Time out verified Photofrin admin 48h prior.
2. ETT placed.
3. Scope advanced to RLL.
4. Lesion measured (1.2cm). Fiber placed.
5. Laser activation: 630nm, 8min 20sec.
6. Fiber removed. No bleeding.
Plan: PACU, light precautions."""

entities_4 = [
    {"label": "PROC_ACTION", **get_span(text_4, "PDT", 1)},
    {"label": "MEDICATION", **get_span(text_4, "Photofrin", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_4, "1.2cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Fiber", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Laser", 1)},
    {"label": "MEAS_TIME", **get_span(text_4, "8min 20sec", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_4, "Fiber", 2)},
    {"label": "OBS_FINDING", **get_span(text_4, "bleeding", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_4", "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 4744854_syn_5
# ==========================================
text_5 = """patient [REDACTED] for pdt light session right lower lobe tumor anesthesia was general tube size 8 used the olympus scope saw the tumor in the rll looked flat about 1cm put the fiber in 3cm diffuser turned the laser on for 500 seconds settings were standard 200 joules per cm2 no issues during light delivery patient stable extubated sent to recovery remind him about the sunlight precautions thanks"""

entities_5 = [
    {"label": "PROC_ACTION", **get_span(text_5, "pdt", 1)},
    {"label": "LATERALITY", **get_span(text_5, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "olympus scope", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "tumor", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "OBS_FINDING", **get_span(text_5, "flat", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "1cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "fiber", 1)},
    {"label": "MEAS_SIZE", **get_span(text_5, "3cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "diffuser", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_5, "laser", 1)},
    {"label": "MEAS_TIME", **get_span(text_5, "500 seconds", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_5, "200 joules per cm2", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_5", "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 4744854_syn_6
# ==========================================
text_6 = """The patient was brought to the endoscopy suite and placed under general anesthesia with an 8.0mm ETT. Initial survey showed a 1.2cm flat lesion in the Right Lower Lobe bronchus causing 54% obstruction. We proceeded with Photodynamic Therapy. A 3.0cm cylindrical diffusing fiber was inserted and 630nm red laser light was delivered at 400mW/cm for 500 seconds (Total 200 J/cm2). The patient tolerated the procedure well with no immediate complications. Post-procedure light precautions were reviewed and the patient was transferred to recovery."""

entities_6 = [
    {"label": "MEAS_SIZE", **get_span(text_6, "1.2cm", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "flat", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "lesion", 1)},
    {"label": "LATERALITY", **get_span(text_6, "Right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "Lower Lobe", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_6, "bronchus", 1)},
    {"label": "OBS_FINDING", **get_span(text_6, "obstruction", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Photodynamic Therapy", 1)},
    {"label": "MEAS_SIZE", **get_span(text_6, "3.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "cylindrical diffusing fiber", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_6, "red laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_6, "400mW/cm", 1)},
    {"label": "MEAS_TIME", **get_span(text_6, "500 seconds", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_6, "200 J/cm2", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_6, "no immediate complications", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_6", "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 4744854_syn_7
# ==========================================
text_7 = """[Indication]
RLL endobronchial SCC, T1aN0M0, declined surgery.
[Anesthesia]
General, 8.0 ETT.
[Description]
Scope passed to RLL. Tumor visualized. 3.0cm diffuser fiber placed. Laser energy delivered (630nm, 200 J/cm2, 500s). No immediate tissue change.
[Plan]
Debridement in 48 hours. Strict light avoidance."""

entities_7 = [
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "SCC", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 2)},
    {"label": "OBS_LESION", **get_span(text_7, "Tumor", 1)},
    {"label": "MEAS_SIZE", **get_span(text_7, "3.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "diffuser fiber", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_7, "Laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_7, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(text_7, "500s", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "Debridement", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_7", "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 4744854_syn_8
# ==========================================
text_8 = """[REDACTED] and intubated for his scheduled PDT session. We advanced the bronchoscope to the right lower lobe, id[REDACTED] the squamous cell carcinoma which appeared as a flat, plaque-like lesion. We inserted the 3.0cm diffusing fiber and centered it over the tumor. The laser was activated at 630nm, delivering 200 J/cm2 over 500 seconds. The patient remained stable throughout the illumination phase. Upon completion, we removed the fiber and noted no immediate bleeding or edema. The patient was extubated and transferred to the PACU with instructions for strict light avoidance."""

entities_8 = [
    {"label": "PROC_ACTION", **get_span(text_8, "PDT", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "bronchoscope", 1)},
    {"label": "LATERALITY", **get_span(text_8, "right", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lower lobe", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "squamous cell carcinoma", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "flat", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "plaque-like", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "lesion", 1)},
    {"label": "MEAS_SIZE", **get_span(text_8, "3.0cm", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "diffusing fiber", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "laser", 1)},
    {"label": "MEAS_ENERGY", **get_span(text_8, "200 J/cm2", 1)},
    {"label": "MEAS_TIME", **get_span(text_8, "500 seconds", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_8, "fiber", 2)},
    {"label": "OBS_FINDING", **get_span(text_8, "bleeding", 1)},
    {"label": "OBS_FINDING", **get_span(text_8, "edema", 1)}
]
BATCH_DATA.append({"id": "4744854_syn_8", "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 4744854_syn_9
# ==========================================
text_9 = """PROCEDURES EXECUTED: 1. Photodynamic therapy - laser illumination. 2. Flexible bronchoscopy with tumor gauging.
DETAILS: Following anesthesia, the scope was navigated to the RLL. The malignancy was located. A light fiber was deployed. Laser energy was emitted at 630nm for 500 seconds to activate the photosensitizer. No thermal damage was noted. The fiber was retracted. The patient was awakened and moved to recovery."""

entities_9 = [
    {"label": "PROC_ACTION", **get_span(text_9, "Photodynamic therapy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "laser", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Flexible bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "tumor", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "scope", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "malignancy", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "light fiber", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "Laser", 1)},
    {"label": "MEAS_TIME", **get_span(text_9, "500 seconds", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_9, "fiber", 2)}
]
BATCH_DATA.append({"id": "4744854_syn_9", "text": text_9, "entities": entities_9})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)