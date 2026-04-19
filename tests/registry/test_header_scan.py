from unittest.mock import MagicMock

import pytest

from app.registry.application.registry_service import (
    RegistryService,
    _extract_procedure_header_block,
    _scan_header_for_codes,
)
from app.registry.schema import RegistryRecord


class _StubRegistryEngine:
    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        return RegistryRecord()


class _StaticRegistryEngine:
    def __init__(self, record: RegistryRecord) -> None:
        self._record = record

    def run(self, note_text: str, *, context=None, **_kwargs):  # type: ignore[no-untyped-def]
        return self._record.model_copy(deep=True)


def _stub_raw_ml_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    from ml.lib.ml_coder.predictor import CaseClassification, MLCoderPredictor
    from ml.lib.ml_coder.thresholds import CaseDifficulty

    monkeypatch.setattr(MLCoderPredictor, "__init__", lambda self, *a, **k: None)
    monkeypatch.setattr(
        MLCoderPredictor,
        "classify_case",
        lambda self, raw_note_text: CaseClassification(
            predictions=[],
            high_conf=[],
            gray_zone=[],
            difficulty=CaseDifficulty.LOW_CONF,
        ),
    )


def _make_service(monkeypatch: pytest.MonkeyPatch, *, record: RegistryRecord | None = None) -> RegistryService:
    monkeypatch.setenv("PROCSUITE_PIPELINE_MODE", "extraction_first")
    monkeypatch.setenv("REGISTRY_AUDITOR_SOURCE", "raw_ml")
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ENABLED", "0")

    _stub_raw_ml_empty(monkeypatch)

    registry_engine = _StubRegistryEngine() if record is None else _StaticRegistryEngine(record)
    return RegistryService(hybrid_orchestrator=MagicMock(), registry_engine=registry_engine)


def test_header_scan_extracts_codes() -> None:
    note = (
        "HPI: cough and weight loss.\n"
        "PROCEDURE:\n"
        "31653 EBUS-TBNA of station 7.\n"
        "ANESTHESIA: General\n"
    )
    header = _extract_procedure_header_block(note)
    assert header is not None
    assert "31653" in header
    assert _scan_header_for_codes(note) == {"31653"}


def test_header_scan_skips_indication_for_operation_noise() -> None:
    note = (
        "INDICATION FOR OPERATION: 74 year old female with tracheal stenosis.\n"
        "PROCEDURE:\n"
        "31622 Dx bronchoscopy/cell washing\n"
        "PROCEDURE IN DETAIL: The airway was inspected.\n"
        "ANESTHESIA: General\n"
    )
    header = _extract_procedure_header_block(note)
    assert header is not None
    assert "31622" in header
    assert "tracheal stenosis" not in header.lower()
    assert _scan_header_for_codes(note) == {"31622"}


def test_header_trigger_adds_high_conf_omissions(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _make_service(monkeypatch)
    note_text = (
        "PROCEDURE:\n"
        "31653 EBUS-TBNA of station 7.\n"
        "ANESTHESIA: General\n"
    )
    result = service.extract_fields(note_text)

    assert result.audit_report is not None
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}
    assert omissions.get("31653") == "HEADER_EXPLICIT"
    assert any("HEADER_EXPLICIT:" in warning for warning in result.audit_warnings)


def test_header_trigger_suppresses_bundled_diagnostic_bronchoscopy(monkeypatch: pytest.MonkeyPatch) -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "diagnostic_bronchoscopy": {"performed": True},
                "airway_dilation": {"performed": True},
            }
        }
    )
    service = _make_service(monkeypatch, record=record)
    note_text = (
        "PROCEDURE:\n"
        "31622 Dx bronchoscopy/cell washing\n"
        "31630 Balloon dilation\n"
        "PROCEDURE IN DETAIL: Balloon dilation of tracheal stenosis was performed.\n"
        "ANESTHESIA: General\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert "31630" in result.cpt_codes
    assert omissions.get("31622") is None
    assert not any("31622" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)


def test_header_trigger_suppresses_bundled_dilation_and_destruction(monkeypatch: pytest.MonkeyPatch) -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "airway_dilation": {"performed": True},
                "mechanical_debulking": {"performed": True},
                "thermal_ablation": {"performed": True},
            }
        }
    )
    service = _make_service(monkeypatch, record=record)
    note_text = (
        "PROCEDURE:\n"
        "31630 Balloon dilation\n"
        "31640 Excision of lesion\n"
        "31641 Destruction by APC\n"
        "PROCEDURE IN DETAIL: Mechanical debulking and APC were performed for airway obstruction. "
        "Balloon dilation was also performed.\n"
        "ANESTHESIA: General\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert "31640" in result.cpt_codes
    assert "31630" not in result.cpt_codes
    assert "31641" not in result.cpt_codes
    assert omissions.get("31630") is None
    assert omissions.get("31641") is None
    assert not any("31630" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)
    assert not any("31641" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)


def test_header_trigger_suppresses_blood_clot_foreign_body_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "therapeutic_aspiration": {"performed": True, "material": "Blood/clot"},
            }
        }
    )
    service = _make_service(monkeypatch, record=record)
    note_text = (
        "PROCEDURE:\n"
        "31635 Foreign body removal\n"
        "31645 Therapeutic aspiration\n"
        "PROCEDURE IN DETAIL: A large blood clot was therapeutically aspirated from the airway.\n"
        "ANESTHESIA: General\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert "31645" in result.cpt_codes
    assert omissions.get("31635") is None
    assert not any("31635" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)


def test_header_trigger_does_not_promote_tracheal_stent_from_dilation_only_note(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "bal": {"performed": True},
                "endobronchial_biopsy": {"performed": True},
                "airway_dilation": {"performed": True},
            }
        }
    )
    service = _make_service(monkeypatch, record=record)
    note_text = (
        "PROCEDURE:\n"
        "31624 Bronchoalveolar lavage\n"
        "31625 Endobronchial biopsy\n"
        "31630 Balloon dilation\n"
        "31631 Tracheal stent placement\n"
        "PROCEDURE IN DETAIL: Bronchoalveolar lavage was performed. Endobronchial forceps biopsies were obtained. "
        "Balloon dilation of tracheal stenosis was performed.\n"
        "ANESTHESIA: General\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert {"31624", "31625", "31630"}.issubset(set(result.cpt_codes))
    assert omissions.get("31631") is None
    assert not any("31631" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)


def test_header_trigger_suppresses_header_only_thoracentesis_noise(monkeypatch: pytest.MonkeyPatch) -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "therapeutic_aspiration": {"performed": True},
                "bal": {"performed": True},
            }
        }
    )
    service = _make_service(monkeypatch, record=record)
    note_text = (
        "PROCEDURE:\n"
        "31645 Therapeutic aspiration\n"
        "31624 Bronchoalveolar lavage\n"
        "32555 - pleural fluid on CT and unclear source of fevers\n"
        "PROCEDURE IN DETAIL: Thick secretions were therapeutically aspirated from both lower lobes. "
        "Bronchoalveolar lavage was also performed. No pleural procedure was performed.\n"
        "ANESTHESIA: General\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert {"31624", "31645"}.issubset(set(result.cpt_codes))
    assert omissions.get("32555") is None
    assert not any("32555" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)


def test_header_trigger_suppresses_unlisted_trach_change_header_noise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "therapeutic_aspiration": {"performed": True},
            }
        }
    )
    service = _make_service(monkeypatch, record=record)
    note_text = (
        "INDICATION FOR OPERATION: tracheostomy change.\n"
        "PROCEDURE:\n"
        "31899 Unlisted trach change procedure\n"
        "31615 Tracheobronchoscopy through established tracheostomy incision\n"
        "31645 Therapeutic aspiration\n"
        "PROCEDURE IN DETAIL: The tracheostomy tube was exchanged. Thick secretions were aspirated. "
        "No bronchoscopic inspection through the tracheostomy tract was described.\n"
        "ANESTHESIA: Moderate sedation\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert "31645" in result.cpt_codes
    assert omissions.get("31899") is None
    assert omissions.get("31615") is None
    assert not any("31899" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)
    assert not any("31615" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)


def test_header_trigger_suppresses_31633_without_base_31629(monkeypatch: pytest.MonkeyPatch) -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["11L", "7", "3P"],
                }
            }
        }
    )
    service = _make_service(monkeypatch, record=record)
    note_text = (
        "PROCEDURE:\n"
        "31633 Additional lobe TBNA\n"
        "31653 EBUS-TBNA of 3 or more stations\n"
        "PROCEDURE IN DETAIL: Convex probe EBUS was used to sample stations 11L, 7, and 3P.\n"
        "ANESTHESIA: General\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert "31653" in result.cpt_codes
    assert omissions.get("31633") is None
    assert not any("31633" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)


def test_header_trigger_does_not_promote_short_header_imaging_adjuncts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _make_service(monkeypatch)
    note_text = (
        "PROCEDURE:\n"
        "77012 CT guidance\n"
        "76377 3D rendering\n"
        "76981 Elastography\n"
        "PROCEDURE IN DETAIL: Robotic bronchoscopy was performed.\n"
        "ANESTHESIA: General\n"
    )

    result = service.extract_fields(note_text)
    omissions = {pred.cpt: pred.bucket for pred in result.audit_report.high_conf_omissions}

    assert omissions.get("77012") is None
    assert omissions.get("76377") is None
    assert omissions.get("76981") is None
    assert not any("77012" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)
    assert not any("76377" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)
    assert not any("76981" in warning for warning in result.audit_warnings if "HEADER_EXPLICIT" in warning)
