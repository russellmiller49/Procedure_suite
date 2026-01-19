from __future__ import annotations

import pytest

from modules.registry.application.registry_service import RegistryService


def _extract(monkeypatch: pytest.MonkeyPatch, note_text: str):
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_EXTRACTION_ENGINE", "engine")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "disabled")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")
    service = RegistryService()
    return service.extract_fields(note_text)


def test_phase5_navigation_sampling_and_fiducials(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "PROCEDURE:\n"
        "Electromagnetic navigation bronchoscopy performed using the ION platform.\n"
        "Target lesion in RUL anterior segment.\n"
        "TBNA performed at station 7.\n"
        "Brushings obtained from the lesion.\n"
        "Transbronchial cryobiopsy performed.\n"
        "Fiducial markers placed for planning.\n"
    )

    result = _extract(monkeypatch, note_text)
    record = result.record

    assert record.procedures_performed is not None
    procs = record.procedures_performed
    assert procs.navigational_bronchoscopy is not None
    assert procs.navigational_bronchoscopy.performed is True
    assert procs.tbna_conventional is not None
    assert procs.tbna_conventional.performed is True
    assert procs.brushings is not None
    assert procs.brushings.performed is True
    assert procs.transbronchial_cryobiopsy is not None
    assert procs.transbronchial_cryobiopsy.performed is True

    granular = record.granular_data
    assert granular is not None
    assert granular.navigation_targets
    target0 = granular.navigation_targets[0]
    assert target0.fiducial_marker_placed is True
    assert target0.target_number == 1


def test_phase5_peripheral_ablation_mwa(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = "PROCEDURE:\nMicrowave ablation performed for peripheral lesion."
    result = _extract(monkeypatch, note_text)
    procs = result.record.procedures_performed

    assert procs is not None
    assert procs.peripheral_ablation is not None
    assert procs.peripheral_ablation.performed is True
    assert procs.peripheral_ablation.modality == "Microwave"


def test_phase5_peripheral_ablation_rfa(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = "PROCEDURE:\nRadiofrequency ablation performed for peripheral lesion."
    result = _extract(monkeypatch, note_text)
    procs = result.record.procedures_performed

    assert procs is not None
    assert procs.peripheral_ablation is not None
    assert procs.peripheral_ablation.performed is True
    assert procs.peripheral_ablation.modality == "Radiofrequency"


def test_phase5_no_cpt_header_false_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    note_text = (
        "CPT CODES:\n"
        "31624 BAL\n"
        "\n"
        "PROCEDURE:\n"
        "Bronchoscopy performed.\n"
    )
    result = _extract(monkeypatch, note_text)

    assert "31624" not in result.cpt_codes
    procs = result.record.procedures_performed
    assert not (procs and procs.bal and procs.bal.performed is True)
