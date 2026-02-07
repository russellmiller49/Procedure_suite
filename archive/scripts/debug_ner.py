import sys
import logging
import re
from pathlib import Path

# 1. Setup paths and imports
sys.path.append(str(Path.cwd()))
from app.ner.inference import GranularNERPredictor

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)

_STATION_FOLLOW_RE = re.compile(r"^(station)\s+([0-9]{1,2}[A-Za-z]{0,4})\b", re.IGNORECASE)


def _display_entity_text(note_text: str, label: str, start: int | None, end: int | None, text: str) -> str:
    """
    Display-only helper:
    - Prefer slicing from offsets (if present) for truth.
    - For ANAT_LN_STATION, if the model returns only 'station', try to show 'station 11Ri' style text
      based on immediate following characters.
    """
    extracted = None
    if isinstance(start, int) and isinstance(end, int) and 0 <= start <= end <= len(note_text):
        extracted = note_text[start:end]

    base = extracted if extracted is not None else (text or "")

    if label == "ANAT_LN_STATION":
        # If the model split "station 11Ri" and only tagged "station", expand for readability.
        if base.strip().lower() == "station" and isinstance(start, int):
            window = note_text[start : min(len(note_text), start + 32)]
            m = _STATION_FOLLOW_RE.match(window.strip())
            if m:
                return f"{m.group(1)} {m.group(2)}"

    return base


def test_ner(text: str, model_path: str):
    print(f"\n--- Loading Model from: {model_path} ---")
    
    try:
        # Initialize the predictor
        ner = GranularNERPredictor(model_dir=model_path, device="cpu")
        
        print("\n--- Input Text ---")
        print(text)
        print("-" * 50)
        
        # Run inference
        # FIX: predict() returns a NERExtractionResult object, not a list
        result = ner.predict(text)
        entities = result.entities  # Access the list of entities inside the object
        
        print(f"\n--- Found {len(entities)} Entities ---")
        if not entities:
            print("❌ NO ENTITIES FOUND. The model sees nothing relevant in this text.")
        
        for ent in entities:
            # Handle dataclass / pydantic-ish objects and dicts.
            if hasattr(ent, "label"):
                label = getattr(ent, "label", "UNKNOWN")
                chunk = getattr(ent, "text", "") or ""
                conf = getattr(ent, "confidence", getattr(ent, "score", 0.0))
                start = getattr(ent, "start_char", getattr(ent, "start", None))
                end = getattr(ent, "end_char", getattr(ent, "end", None))
                evidence = getattr(ent, "evidence_quote", "") or ""
            else:
                label = ent.get("label", "UNKNOWN")
                chunk = ent.get("text", "") or ""
                conf = ent.get("confidence", ent.get("score", 0.0))
                start = ent.get("start_char", ent.get("start"))
                end = ent.get("end_char", ent.get("end"))
                evidence = ent.get("evidence_quote", "") or ""

            disp = _display_entity_text(text, str(label), start, end, chunk)
            loc = ""
            if isinstance(start, int) and isinstance(end, int):
                loc = f" chars={start}:{end}"
            conf_s = ""
            try:
                conf_s = f" conf={float(conf):.3f}"
            except Exception:
                conf_s = ""

            print(f"[{label}] '{disp}'{conf_s}{loc}")
            if evidence:
                print(f"  evidence: {evidence}")
            
    except Exception as e:
        print(f"\n❌ ERROR loading or running model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Default text: The complex note snippet that failed
    default_text = """
Following intravenous medications as per the record and topical anesthesia to the upper airway and tracheobronchial tree, the Q190 video bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree. The laryngeal mask airway is in good position. The vocal cords appeared normal. The subglottic space was normal. The trachea is of normal caliber. The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level. Bronchial mucosa and anatomy were normal; there are no endobronchial lesions, and no secretions. The video bronchoscope was then removed and the UC180F convex probe EBUS bronchoscope was introduced through the mouth, via laryngeal mask airway and advanced to the tracheobronchial tree. Ultrasound was utilized to identify and measure the radiographically suspicious station 11Ri lymph node. Sampling by transbronchial needle aspiration was performed beginning with the Olympus EBUS-TBNA 22 gauge needle. Rapid onsite evaluation read as malignancy. All samples were sent for routine cytology. Following completion of EBUS bronchoscopy the video bronchoscope was re-inserted and blood was suctioned from the airway. The bronchoscope was removed and procedure completed.



Complications: No immediate complications

Estimated Blood Loss: 10 cc.

Post Procedure Diagnosis:

- Technically successful flexible bronchoscopy with endobronchial ultrasound-guided biopsies.

- The patient <PERSON> and has been transferred in good condition to the post-surgical monitoring unit.

- Will await final pathology results    """
    
    # Allow passing text via command line args, otherwise use default
    input_text = sys.argv[1] if len(sys.argv) > 1 else default_text
    
    # CHECK BOTH COMMON LOCATIONS
    biomed_path = "artifacts/registry_biomedbert_ner"
    distil_path = "artifacts/registry_biomedbert_ner"
    
    # Prefer the one that exists
    target_model = biomed_path if Path(biomed_path).exists() else distil_path
    
    test_ner(input_text, target_model)
