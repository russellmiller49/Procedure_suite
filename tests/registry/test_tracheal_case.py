from modules.registry.engine import RegistryEngine
from modules.coder.dictionary import get_site_pattern_map

def test_site_patterns_include_trachea():
    patterns = get_site_pattern_map()
    assert "Trachea" in patterns or "TRACHEA" in patterns
    
def test_complex_tracheal_case():
    note = """
    Seely, Robert MRN: 30020568
    PREOPERATIVE DIAGNOSIS: Tracheal stenosis
    POSTOPERATIVE DIAGNOSIS: Complex Tracheal stenosis s/p stent placement 
    PROCEDURE PERFORMED: Tracheal self-expandable airway stent placement
    SURGEON: George Cheng MD
    INDICATIONS: Symptomatic tracheal stenosis
    Sedation: General Anesthesia
    DESCRIPTION OF PROCEDURE: The procedure was performed in the bronchoscopy suite. 
    ...
    Approximately 2.5 cm distal to the vocal cords was a long segment of circumferential complex stenosis...
    A 16x40 mm Ultraflex uncovered self-expandable metallic stent was then inserted...
    A 14/16.5/18 mm Elation dilatational balloon was used to dilate the stent...
    The bronchoscope was removed and the procedure was completed. 
    Recommendations:
    - Transfer to PACU
    - Discharge once criteria met.
    """
    
    engine = RegistryEngine()
    record = engine.run(note)
    
    # Check Indication
    assert record.indication == "Airway Stenosis"
    
    # Check Stents (Deduplication)
    assert len(record.stents) == 1
    stent = record.stents[0]
    
    # Debug output if it fails
    if stent.site != "Trachea":
        print(f"DEBUG: Extracted site: {stent.site}")
        
    assert stent.site == "Trachea" # Assuming "Trachea" matches from dictionary
    assert "16x40mm" in stent.size
    assert "uncovered metallic" in stent.stent_type.lower()
    
    # Check Dilation (Multi-stage)
    assert len(record.dilation_events) == 1
    dilation = record.dilation_events[0]
    assert dilation.balloon_size == "14/16.5/18mm" # Or similar depending on regex capture
    
    # Check Disposition
    assert record.disposition == "PACU"
    
    # Check Patient ID
    assert record.patient_id == "30020568"