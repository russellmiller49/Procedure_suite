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
    """
    start = -1
    for _ in range(occurrence):
        start = text.find(term, start + 1)
        if start == -1:
            raise ValueError(f"Term '{term}' not found {occurrence} times in text.")
    
    return {"start": start, "end": start + len(term)}

# ==========================================
# Note 1: SYN_BRONCH_1_8
# ==========================================
t1 = """The patient was brought to the bronchoscopy suite for management of airway stent occlusion. Under general anesthesia, we inserted an LMA and advanced the therapeutic bronchoscope. The silicone Y-stent was in good position, but the limbs were heavily obstructed by thick, dry mucus, particularly on the right side involving the metallic stent. We proceeded to clear these obstructions using a combination of mechanical disruption, forceps removal, and sodium bicarbonate instillation. This successfully recanalized the stents. We also noted a tumor at the LUL takeoff but decided against intervention at this time. Finally, we performed a mini-BAL in the left upper lobe anterior segment before concluding the procedure."""

e1 = [
    # Finding: "airway stent occlusion"
    {"label": "OBS_FINDING", **get_span(t1, "airway stent occlusion", 1)},
    
    # Device: "therapeutic bronchoscope"
    {"label": "DEV_INSTRUMENT", **get_span(t1, "therapeutic bronchoscope", 1)},
    
    # Stent 1: "silicone" (Material) + "Y-stent" (Type)
    {"label": "DEV_STENT_MATERIAL", **get_span(t1, "silicone", 1)},
    {"label": "DEV_STENT", **get_span(t1, "Y-stent", 1)},
    
    # Finding: "thick, dry mucus"
    {"label": "OBS_FINDING", **get_span(t1, "thick, dry mucus", 1)},
    
    # Anatomy/Laterality: "right"
    {"label": "LATERALITY", **get_span(t1, "right", 1)},
    
    # Stent 2: "metallic" (Material) + "stent" (Type)
    {"label": "DEV_STENT_MATERIAL", **get_span(t1, "metallic", 1)},
    {"label": "DEV_STENT", **get_span(t1, "stent", 2)},
    
    # Actions: "mechanical disruption", "forceps removal", "sodium bicarbonate instillation"
    {"label": "PROC_ACTION", **get_span(t1, "mechanical disruption", 1)},
    {"label": "DEV_INSTRUMENT", **get_span(t1, "forceps", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "removal", 1)},
    {"label": "MEDICATION", **get_span(t1, "sodium bicarbonate", 1)},
    {"label": "PROC_ACTION", **get_span(t1, "instillation", 1)},
    
    # Lesion: "tumor"
    {"label": "OBS_LESION", **get_span(t1, "tumor", 1)},
    
    # Anatomy: "LUL"
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "LUL", 1)},
    
    # Action: "mini-BAL"
    {"label": "PROC_ACTION", **get_span(t1, "mini-BAL", 1)},
    
    # Anatomy: "left upper lobe anterior segment"
    {"label": "ANAT_LUNG_LOC", **get_span(t1, "left upper lobe anterior segment", 1)},
]

BATCH_DATA.append({"id": "SYN_BRONCH_1_8", "text": t1, "entities": e1})

if __name__ == "__main__":
    print(f"Starting batch processing of {len(BATCH_DATA)} notes...")
    for case in BATCH_DATA:
        add_case(case["id"], case["text"], case["entities"], REPO_ROOT)