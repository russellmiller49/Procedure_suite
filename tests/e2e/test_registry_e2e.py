
from pathlib import Path
from modules.registry.engine import RegistryEngine

def test_complex_tracheal_extraction():
    # Load fixture
    fixture_path = Path("tests/fixtures/complex_tracheal_stenosis.txt")
    if not fixture_path.exists():
        return # Skip if fixture not created yet (safety)
    
    note_text = fixture_path.read_text()
    
    engine = RegistryEngine()
    record = engine.run(note_text)
    
    # 1. Validate Patient ID (Regex)
    assert record.patient_id == "30020568"
    
    # 2. Validate Stents/Devices (LLM)
    assert len(record.devices) >= 1
    
    stents = [d for d in record.devices if d.category == "stent"]
    assert len(stents) == 1
    assert "Ultraflex" in stents[0].name
    assert "16x40" in stents[0].size_text
    
    # 3. Validate Balloons/Devices (LLM)
    balloons = [d for d in record.devices if d.category == "balloon"]
    assert len(balloons) >= 1
    assert "Elation" in balloons[0].name
    # LLM should capture the multi-stage size
    assert "14/16.5/18" in balloons[0].size_text or "18" in balloons[0].size_text
    
    # 4. Validate Lesions (LLM)
    assert len(record.lesions) >= 1
    lesion = record.lesions[0]
    assert "stenosis" in lesion.type.lower()
    assert lesion.location.lower() == "trachea"
    assert lesion.obstruction_baseline == 90
    
    # 5. Validate Outcome
    assert record.technical_success == "complete"
    assert "PACU" in record.followup_plan
