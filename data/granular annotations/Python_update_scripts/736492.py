import sys
from pathlib import Path

# Set the repository root based on the script's location
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a case-sensitive term.
    """
    start_index = -1
    for i in range(occurrence):
        start_index = text.find(term, start_index + 1)
        if start_index == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start_index, "end": start_index + len(term)}

# ==========================================
# Note 1: 736492_syn_1
# ==========================================
id_1 = "736492_syn_1"
text_1 = """Indication: Post-transplant surveillance.
Findings: Anastomotic granulation/polyps.
Action: EBBx anastomoses. TBBx RLL/LLL. BAL RML.
Plan: Transplant clinic."""
entities_1 = [
    {"label": "CTX_HISTORICAL", **get_span(text_1, "Post-transplant", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "Anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "granulation", 1)},
    {"label": "OBS_LESION", **get_span(text_1, "polyps", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "EBBx", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_1, "anastomoses", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_1, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_1, "RML", 1)},
]
BATCH_DATA.append({"id": id_1, "text": text_1, "entities": entities_1})

# ==========================================
# Note 2: 736492_syn_2
# ==========================================
id_2 = "736492_syn_2"
text_2 = """PROCEDURE: Surveillance bronchoscopy in a post-lung transplant recipient. Anastomotic evaluation revealed granulation tissue at the RMS and LMS. Endobronchial biopsies were performed. Transbronchial biopsies were obtained from the RLL and LLL to assess for rejection. A bronchoalveolar lavage was conducted in the RML."""
entities_2 = [
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoscopy", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_2, "post-lung transplant", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "Anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(text_2, "granulation tissue", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_2, "LMS", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Endobronchial biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_2, "bronchoalveolar lavage", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_2, "RML", 1)},
]
BATCH_DATA.append({"id": id_2, "text": text_2, "entities": entities_2})

# ==========================================
# Note 3: 736492_syn_3
# ==========================================
id_3 = "736492_syn_3"
text_3 = """Coding: 31628 (TBBx RLL), 31632 (TBBx LLL), 31625-XS (EBBx Anastomosis), 31624-XS (BAL RML). Procedure involved distinct techniques (forceps vs TBBx) and distinct locations (Anastomosis vs lobes vs lavage site)."""
entities_3 = [
    {"label": "PROC_ACTION", **get_span(text_3, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBBx", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "EBBx", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Anastomosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_3, "RML", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(text_3, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(text_3, "TBBx", 3)},
    {"label": "ANAT_AIRWAY", **get_span(text_3, "Anastomosis", 2)},
    {"label": "PROC_ACTION", **get_span(text_3, "lavage", 1)},
]
BATCH_DATA.append({"id": id_3, "text": text_3, "entities": entities_3})

# ==========================================
# Note 4: 736492_syn_4
# ==========================================
id_4 = "736492_syn_4"
text_4 = """Resident Note
Pt: [REDACTED] (Txp pt)
1. ETT/GA.
2. Checked anastomoses: Granulation tissue biopsied.
3. TBBx: RLL x4, LLL x4.
4. BAL: RML.
5. Minimal bleeding."""
entities_4 = [
    {"label": "CTX_HISTORICAL", **get_span(text_4, "Txp", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_4, "anastomoses", 1)},
    {"label": "OBS_LESION", **get_span(text_4, "Granulation tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "biopsied", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_4, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_4, "RML", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_4, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": id_4, "text": text_4, "entities": entities_4})

# ==========================================
# Note 5: 736492_syn_5
# ==========================================
id_5 = "736492_syn_5"
text_5 = """james wilson lung transplant checkup saw some granulation at the hookups took biopsies of that then did the transbronchial biopsies in rll and lll for rejection check and a bal in rml bleeding was fine continue meds."""
entities_5 = [
    {"label": "CTX_HISTORICAL", **get_span(text_5, "lung transplant", 1)},
    {"label": "OBS_LESION", **get_span(text_5, "granulation", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_5, "hookups", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rll", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "lll", 1)},
    {"label": "PROC_ACTION", **get_span(text_5, "bal", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_5, "rml", 1)},
]
BATCH_DATA.append({"id": id_5, "text": text_5, "entities": entities_5})

# ==========================================
# Note 6: 736492_syn_6
# ==========================================
id_6 = "736492_syn_6"
text_6 = """General anesthesia via ETT was used. Bilateral anastomoses showed granulation tissue and polyps; biopsies were taken. Transbronchial biopsies were obtained from the RLL and LLL. A BAL was performed in the RML. The patient tolerated the procedure well."""
entities_6 = [
    {"label": "ANAT_AIRWAY", **get_span(text_6, "anastomoses", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "granulation tissue", 1)},
    {"label": "OBS_LESION", **get_span(text_6, "polyps", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "biopsies", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "Transbronchial biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_6, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_6, "RML", 1)},
]
BATCH_DATA.append({"id": id_6, "text": text_6, "entities": entities_6})

# ==========================================
# Note 7: 736492_syn_7
# ==========================================
id_7 = "736492_syn_7"
text_7 = """[Indication]
Post-transplant surveillance.
[Anesthesia]
General.
[Description]
Anastomotic lesions biopsied. TBBx RLL and LLL performed. BAL RML. Minimal bleeding.
[Plan]
Transplant clinic follow-up."""
entities_7 = [
    {"label": "CTX_HISTORICAL", **get_span(text_7, "Post-transplant", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_7, "Anastomotic", 1)},
    {"label": "OBS_LESION", **get_span(text_7, "lesions", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "biopsied", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "TBBx", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_7, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_7, "RML", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_7, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": id_7, "text": text_7, "entities": entities_7})

# ==========================================
# Note 8: 736492_syn_8
# ==========================================
id_8 = "736492_syn_8"
text_8 = """[REDACTED] routine post-transplant bronchoscopy. We found some granulation tissue at the connection points and biopsied it. We also took deep lung biopsies from the lower lobes to check for rejection and washed the middle lobe. He had minimal bleeding and will follow up with the transplant team."""
entities_8 = [
    {"label": "CTX_HISTORICAL", **get_span(text_8, "post-transplant", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "bronchoscopy", 1)},
    {"label": "OBS_LESION", **get_span(text_8, "granulation tissue", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_8, "connection points", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "biopsied", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "lung biopsies", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "lower lobes", 1)},
    {"label": "PROC_ACTION", **get_span(text_8, "washed", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_8, "middle lobe", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_8, "minimal bleeding", 1)},
]
BATCH_DATA.append({"id": id_8, "text": text_8, "entities": entities_8})

# ==========================================
# Note 9: 736492_syn_9
# ==========================================
id_9 = "736492_syn_9"
text_9 = """Surveillance of lung allograft. Examined anastomoses; sampled granulation tissue. Performed transbronchial sampling of RLL and LLL. Lavaged RML. Continued immunosuppression."""
entities_9 = [
    {"label": "CTX_HISTORICAL", **get_span(text_9, "lung allograft", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_9, "anastomoses", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "sampled", 1)},
    {"label": "OBS_LESION", **get_span(text_9, "granulation tissue", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "transbronchial sampling", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_9, "Lavaged", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_9, "RML", 1)},
]
BATCH_DATA.append({"id": id_9, "text": text_9, "entities": entities_9})

# ==========================================
# Note 10: 736492
# ==========================================
id_10 = "736492"
text_10 = """Pt: [REDACTED] || MRN: [REDACTED] || DOB: [REDACTED]
Date: [REDACTED] || Location: [REDACTED]
MD: Dr. Catherine Moore

Dx: Post-lung transplant, new endobronchial lesions at anastomosis
Procedure: Surveillance bronchoscopy with endobronchial biopsy, TBBx

General anesthesia via ETT. Bilateral lung transplant 18 months ago. RMS anastomosis with granulation tissue and 2 small polyps. LMS anastomosis with single granuloma. Endobronchial biopsies: 2 from RMS, 1 from LMS. TBBx from RLL (4 specimens) and LLL (4 specimens) for rejection surveillance. BAL from RML. Minimal bleeding throughout.

Path pending. Continue current immunosuppression. F/U transplant clinic.

C. Moore, MD"""
entities_10 = [
    {"label": "CTX_HISTORICAL", **get_span(text_10, "Post-lung transplant", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "endobronchial lesions", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "anastomosis", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Surveillance bronchoscopy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "endobronchial biopsy", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBBx", 1)},
    {"label": "CTX_HISTORICAL", **get_span(text_10, "lung transplant", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "anastomosis", 2)},
    {"label": "OBS_LESION", **get_span(text_10, "granulation tissue", 1)},
    {"label": "OBS_LESION", **get_span(text_10, "polyps", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LMS", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "anastomosis", 3)},
    {"label": "OBS_LESION", **get_span(text_10, "granuloma", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "Endobronchial biopsies", 1)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "RMS", 2)},
    {"label": "ANAT_AIRWAY", **get_span(text_10, "LMS", 2)},
    {"label": "PROC_ACTION", **get_span(text_10, "TBBx", 2)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RLL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "LLL", 1)},
    {"label": "PROC_ACTION", **get_span(text_10, "BAL", 1)},
    {"label": "ANAT_LUNG_LOC", **get_span(text_10, "RML", 1)},
    {"label": "OUTCOME_COMPLICATION", **get_span(text_10, "Minimal bleeding", 1)},
]
BATCH_DATA.append({"id": id_10, "text": text_10, "entities": entities_10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)