
from pathlib import Path
from modules.registry.engine import RegistryEngine


def test_complex_tracheal_extraction():
    fixture_path = Path("tests/fixtures/complex_tracheal_stenosis.txt")
    if not fixture_path.exists():
        return

    note_text = fixture_path.read_text()
    engine = RegistryEngine()
    record = engine.run(note_text)

    assert record.patient_mrn == "30020568"
    assert record.version == "0.5.0"
    data = record.model_dump()
    assert "patient_mrn" in data
    assert "follow_up_plan" in data
