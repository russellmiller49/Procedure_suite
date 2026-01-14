from __future__ import annotations

from modules.registry.schema import RegistryRecord
from modules.registry.self_correction.keyword_guard import scan_for_omissions


def test_scan_for_omissions_warns_for_missing_brushings() -> None:
    record = RegistryRecord()
    note_text = "Bronchial brushings were obtained from the right upper lobe."
    warnings = scan_for_omissions(note_text, record)
    assert any("brush" in w.lower() for w in warnings)


def test_scan_for_omissions_no_warning_when_brushings_present() -> None:
    record = RegistryRecord.model_validate({"procedures_performed": {"brushings": {"performed": True}}})
    note_text = "Bronchial brushings were obtained from the right upper lobe."
    warnings = scan_for_omissions(note_text, record)
    assert not warnings


def test_scan_for_omissions_warns_for_missing_rigid_bronchoscopy() -> None:
    record = RegistryRecord()
    note_text = "Rigid bronchoscopy performed with rigid barrel for airway obstruction."
    warnings = scan_for_omissions(note_text, record)
    assert any("rigid" in w.lower() for w in warnings)


def test_scan_for_omissions_warns_for_missing_thermal_ablation() -> None:
    record = RegistryRecord()
    note_text = "Electrocautery was used for tumor debulking."
    warnings = scan_for_omissions(note_text, record)
    assert any("electrocautery" in w.lower() for w in warnings) or any("argon" in w.lower() for w in warnings)

