import sys
from pathlib import Path

# Set the root of the repository (adjust '3' if your script is deeper in the folder structure)
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(REPO_ROOT))

from scripts.add_training_case import add_case

BATCH_DATA = []

def get_span(text, term, occurrence=1):
    """
    Finds the start and end indices of the nth occurrence of a term in the text.
    Returns a dictionary with 'start', 'end', and 'text' keys.
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {
        "start": start,
        "end": start + len(term),
        "text": term
    }

# ==========================================
# Note 1: 700007_syn_1
# ==========================================
t1 = """Indication: Pleurodesis achieved. Catheter not draining.
Proc: PleurX removal.
Action: Cuff dissected. Catheter pulled intact.
Result: No air leak. Suture closed.
Plan: Home."""

e1 = [
    {"label": "OUTCOME_PLEURAL", **get_span(t1, "Pleurodesis", 1)},
    {"label": "DEV_CATHETER",    **get_span(t1, "Catheter", 1)},
    {"label": "DEV_CATHETER",    **get_span(t1, "PleurX", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "removal", 1)},
    {"label": "PROC_ACTION",     **get_span(t1, "dissected", 1)},
    {"label": "DEV_CATHETER",    **get_span(t1, "Catheter", 2)},
    {"label": "PROC_ACTION",     **get_span(t1, "pulled", 1)},
    {"label": "OBS_FINDING",     **get_span(t1, "air leak", 1)},
]
BATCH_DATA.append({"id": "700007_syn_1", "text": t1, "entities": e1})

# ==========================================
# Note 2: 700007_syn_2
# ==========================================
t2 = """PROCEDURE: Removal of tunneled indwelling pleural catheter.
PATIENT: [REDACTED], 64F, with history of breast cancer.
DETAILS: The right-sided PleurX catheter was removed following successful spontaneous pleurodesis. The cuff was dissected free from the subcutaneous tissue, and the catheter was withdrawn without resistance. The exit site was sutured. No complications occurred."""

e2 = [
    {"label": "PROC_ACTION",      **get_span(t2, "Removal", 1)},
    {"label": "DEV_CATHETER",     **get_span(t2, "tunneled indwelling pleural catheter", 1)},
    {"label": "CTX_HISTORICAL",   **get_span(t2, "history of", 1)},
    {"label": "OBS_LESION",       **get_span(t2, "breast cancer", 1)},
    {"label": "LATERALITY",       **get_span(t2, "right", 1)},
    {"label": "DEV_CATHETER",     **get_span(t2, "PleurX", 1)},
    {"label": "DEV_CATHETER",     **get_span(t2, "catheter", 2)},
    {"label": "PROC_ACTION",      **get_span(t2, "removed", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t2, "spontaneous pleurodesis", 1)},
    {"label": "PROC_ACTION",      **get_span(t2, "dissected", 1)},
    {"label": "DEV_CATHETER",     **get_span(t2, "catheter", 3)},
    {"label": "PROC_ACTION",      **get_span(t2, "withdrawn", 1)},
    {"label": "PROC_ACTION",      **get_span(t2, "sutured", 1)},
]
BATCH_DATA.append({"id": "700007_syn_2", "text": t2, "entities": e2})

# ==========================================
# Note 3: 700007_syn_3
# ==========================================
t3 = """Code: 32552 (Removal of indwelling tunneled pleural catheter).
Condition: Catheter no longer needed (autopleurodesis). Cuff dissected/removed intact."""

e3 = [
    {"label": "PROC_ACTION",      **get_span(t3, "Removal", 1)},
    {"label": "DEV_CATHETER",     **get_span(t3, "indwelling tunneled pleural catheter", 1)},
    {"label": "DEV_CATHETER",     **get_span(t3, "Catheter", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t3, "autopleurodesis", 1)},
    {"label": "PROC_ACTION",      **get_span(t3, "dissected", 1)},
    {"label": "PROC_ACTION",      **get_span(t3, "removed", 1)},
]
BATCH_DATA.append({"id": "700007_syn_3", "text": t3, "entities": e3})

# ==========================================
# Note 4: 700007_syn_4
# ==========================================
t4 = """Procedure: IPC Removal
Patient: [REDACTED]
Steps:
1. Prepped site.
2. Local anesthesia.
3. Dissected cuff.
4. Removed catheter.
5. Sutured wound.
No complications."""

e4 = [
    {"label": "DEV_CATHETER",     **get_span(t4, "IPC", 1)},
    {"label": "PROC_ACTION",      **get_span(t4, "Removal", 1)},
    {"label": "PROC_ACTION",      **get_span(t4, "Dissected", 1)},
    {"label": "PROC_ACTION",      **get_span(t4, "Removed", 1)},
    {"label": "DEV_CATHETER",     **get_span(t4, "catheter", 1)},
    {"label": "PROC_ACTION",      **get_span(t4, "Sutured", 1)},
]
BATCH_DATA.append({"id": "700007_syn_4", "text": t4, "entities": e4})

# ==========================================
# Note 5: 700007_syn_5
# ==========================================
t5 = """Removed [REDACTED] shes dried up. Right side. Cut down to the cuff and freed it up pulled it out no problem. Stitched it up. She can go home."""

e5 = [
    {"label": "PROC_ACTION",      **get_span(t5, "Removed", 1)},
    {"label": "LATERALITY",       **get_span(t5, "Right", 1)},
    {"label": "PROC_ACTION",      **get_span(t5, "freed", 1)},
    {"label": "PROC_ACTION",      **get_span(t5, "pulled", 1)},
    {"label": "PROC_ACTION",      **get_span(t5, "Stitched", 1)},
]
BATCH_DATA.append({"id": "700007_syn_5", "text": t5, "entities": e5})

# ==========================================
# Note 6: 700007_syn_6
# ==========================================
t6 = """Removal of right tunneled pleural catheter. Indication: Autopleurodesis. Cuff mobilized and catheter removed intact. Exit site closed with nylon suture. Patient discharged."""

e6 = [
    {"label": "PROC_ACTION",      **get_span(t6, "Removal", 1)},
    {"label": "LATERALITY",       **get_span(t6, "right", 1)},
    {"label": "DEV_CATHETER",     **get_span(t6, "tunneled pleural catheter", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t6, "Autopleurodesis", 1)},
    {"label": "PROC_ACTION",      **get_span(t6, "mobilized", 1)},
    {"label": "DEV_CATHETER",     **get_span(t6, "catheter", 2)},
    {"label": "PROC_ACTION",      **get_span(t6, "removed", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(t6, "nylon suture", 1)},
]
BATCH_DATA.append({"id": "700007_syn_6", "text": t6, "entities": e6})

# ==========================================
# Note 7: 700007_syn_7
# ==========================================
t7 = """[Indication]
Resolved malignant effusion, spontaneous pleurodesis.
[Anesthesia]
Local.
[Description]
Dissection and removal of right tunneled pleural catheter. Closure of site.
[Plan]
Suture removal in 7-10 days."""

e7 = [
    {"label": "OBS_LESION",       **get_span(t7, "malignant effusion", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t7, "spontaneous pleurodesis", 1)},
    {"label": "PROC_ACTION",      **get_span(t7, "Dissection", 1)},
    {"label": "PROC_ACTION",      **get_span(t7, "removal", 1)},
    {"label": "LATERALITY",       **get_span(t7, "right", 1)},
    {"label": "DEV_CATHETER",     **get_span(t7, "tunneled pleural catheter", 1)},
]
BATCH_DATA.append({"id": "700007_syn_7", "text": t7, "entities": e7})

# ==========================================
# Note 8: 700007_syn_8
# ==========================================
t8 = """[REDACTED] has resolved, so we removed her PleurX catheter today. After numbing the area, we dissected the fibrous cuff from the tunnel and pulled the catheter out. The site was closed with a suture. She tolerated the removal well."""

e8 = [
    {"label": "PROC_ACTION",      **get_span(t8, "removed", 1)},
    {"label": "DEV_CATHETER",     **get_span(t8, "PleurX", 1)},
    {"label": "DEV_CATHETER",     **get_span(t8, "catheter", 1)},
    {"label": "PROC_ACTION",      **get_span(t8, "dissected", 1)},
    {"label": "PROC_ACTION",      **get_span(t8, "pulled", 1)},
    {"label": "DEV_CATHETER",     **get_span(t8, "catheter", 2)},
    {"label": "DEV_INSTRUMENT",   **get_span(t8, "suture", 1)},
    {"label": "PROC_ACTION",      **get_span(t8, "removal", 1)},
]
BATCH_DATA.append({"id": "700007_syn_8", "text": t8, "entities": e8})

# ==========================================
# Note 9: 700007_syn_9
# ==========================================
t9 = """Procedure: Extraction of tunneled pleural drain.
Reason: Autopleurodesis.
Action: The retention cuff was liberated. The device was withdrawn.
Result: Site closed."""

e9 = [
    {"label": "PROC_ACTION",      **get_span(t9, "Extraction", 1)},
    {"label": "DEV_CATHETER",     **get_span(t9, "tunneled pleural drain", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t9, "Autopleurodesis", 1)},
    {"label": "PROC_ACTION",      **get_span(t9, "liberated", 1)},
    {"label": "DEV_CATHETER",     **get_span(t9, "device", 1)},
    {"label": "PROC_ACTION",      **get_span(t9, "withdrawn", 1)},
]
BATCH_DATA.append({"id": "700007_syn_9", "text": t9, "entities": e9})

# ==========================================
# Note 10: 700007 (Original)
# ==========================================
t10 = """PATIENT: [REDACTED]
MRN: [REDACTED]
AGE: 64 years
DATE OF PROCEDURE: [REDACTED]
LOCATION: [REDACTED]

PRE-PROCEDURE DIAGNOSIS: Right malignant pleural effusion status post tunneled pleural catheter with clinical autopleurodesis.
POST-PROCEDURE DIAGNOSIS: Same.

PROCEDURE: Removal of tunneled indwelling pleural catheter.

PHYSICIAN: Thomas Nguyen, MD (Interventional Pulmonology)

INDICATION:
64-year-old female with metastatic breast cancer and right malignant pleural effusion managed with a PleurX catheter placed 7 months ago. She has had no drainage for 6 weeks and imaging shows a small residual effusion with lung expansion, consistent with spontaneous pleurodesis. The catheter site is mildly irritated and the patient wishes to have it removed.

PROCEDURE DESCRIPTION:
The patient was placed in the supine position. The right lateral chest and catheter exit site were prepped and draped in sterile fashion. Local anesthesia was provided with 1% lidocaine infiltrated around the cuff and exit site.

The tunnel tract and cuff were gently dissected free using a small scalpel and blunt dissection. Once the cuff was fully mobilized, steady traction was applied and the PleurX catheter was removed intact without resistance. The tunnel was probed digitally to confirm no retained cuff material.

Hemostasis was achieved with gauze and direct pressure. The exit site was closed with a single 3-0 nylon suture and covered with a sterile dressing.

COMPLICATIONS:
Minimal bleeding, no pneumothorax, no air leak. The patient tolerated the procedure well.

DISPOSITION:
The patient was observed for 30 minutes and discharged home in stable condition with instructions for wound care and removal of sutures in 7–10 days.

IMPRESSION:
Uncomplicated removal of tunneled right pleural catheter after successful autopleurodesis."""

e10 = [
    {"label": "LATERALITY",       **get_span(t10, "Right", 1)},
    {"label": "OBS_LESION",       **get_span(t10, "malignant pleural effusion", 1)},
    {"label": "CTX_HISTORICAL",   **get_span(t10, "status post", 1)},
    {"label": "DEV_CATHETER",     **get_span(t10, "tunneled pleural catheter", 1)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t10, "clinical autopleurodesis", 1)},
    {"label": "PROC_ACTION",      **get_span(t10, "Removal", 1)},
    {"label": "DEV_CATHETER",     **get_span(t10, "tunneled indwelling pleural catheter", 1)},
    {"label": "OBS_LESION",       **get_span(t10, "metastatic breast cancer", 1)},
    {"label": "LATERALITY",       **get_span(t10, "right", 1)}, # Fixed from 2 to 1 (Indication)
    {"label": "OBS_LESION",       **get_span(t10, "malignant pleural effusion", 2)},
    {"label": "DEV_CATHETER",     **get_span(t10, "PleurX", 1)},
    {"label": "DEV_CATHETER",     **get_span(t10, "catheter", 2)},
    {"label": "OBS_LESION",       **get_span(t10, "effusion", 3)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t10, "spontaneous pleurodesis", 1)},
    {"label": "DEV_CATHETER",     **get_span(t10, "catheter", 3)},
    {"label": "LATERALITY",       **get_span(t10, "right", 2)}, # Fixed from 3 to 2 (Proc Desc)
    {"label": "DEV_CATHETER",     **get_span(t10, "catheter", 4)},
    {"label": "MEDICATION",       **get_span(t10, "lidocaine", 1)},
    {"label": "PROC_ACTION",      **get_span(t10, "dissected", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(t10, "scalpel", 1)},
    {"label": "PROC_ACTION",      **get_span(t10, "dissection", 1)},
    {"label": "PROC_ACTION",      **get_span(t10, "mobilized", 1)},
    {"label": "DEV_CATHETER",     **get_span(t10, "PleurX", 2)},
    {"label": "DEV_CATHETER",     **get_span(t10, "catheter", 5)},
    {"label": "PROC_ACTION",      **get_span(t10, "removed", 2)},
    {"label": "PROC_ACTION",      **get_span(t10, "probed", 1)},
    {"label": "DEV_INSTRUMENT",   **get_span(t10, "3-0 nylon suture", 1)},
    {"label": "OBS_FINDING",      **get_span(t10, "pneumothorax", 1)},
    {"label": "OBS_FINDING",      **get_span(t10, "air leak", 1)},
    {"label": "PROC_ACTION",      **get_span(t10, "removal", 2)}, # Fixed from 3 to 2 (Impression)
    {"label": "LATERALITY",       **get_span(t10, "right", 3)}, # Fixed from 4 to 3 (Impression)
    {"label": "DEV_CATHETER",     **get_span(t10, "pleural catheter", 2)},
    {"label": "OUTCOME_PLEURAL",  **get_span(t10, "autopleurodesis", 2)},
]
BATCH_DATA.append({"id": "700007", "text": t10, "entities": e10})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)