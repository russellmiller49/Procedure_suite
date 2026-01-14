from __future__ import annotations

from modules.common.spans import Span
from modules.registry.evidence.verifier import verify_evidence_integrity
from modules.registry.postprocess import sanitize_ebus_events
from modules.registry.schema import RegistryRecord


def test_verify_evidence_integrity_hallucinated_therapeutic_aspiration_flips_false() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "therapeutic_aspiration": {
                    "performed": True,
                    "material": "Mucus plug",
                    "location": "LMB",
                }
            }
        }
    )
    record.evidence = {
        "therapeutic_aspiration": [
            Span(text="Therapeutic aspiration of mucus plug", start=0, end=10),
        ]
    }

    note_text = "Diagnostic bronchoscopy performed. No mucus plug was seen."
    record, warnings = verify_evidence_integrity(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.therapeutic_aspiration is not None
    assert record.procedures_performed.therapeutic_aspiration.performed is False
    assert record.procedures_performed.therapeutic_aspiration.material is None
    assert record.procedures_performed.therapeutic_aspiration.location is None
    assert "WIPED_VERIFICATION_FAILED: procedures_performed.therapeutic_aspiration" in warnings


def test_verify_evidence_integrity_wipes_hallucinated_trach_device_name() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "percutaneous_tracheostomy": {
                    "performed": True,
                    "device_name": "Portex",
                }
            }
        }
    )

    note_text = "Percutaneous tracheostomy performed. A Shiley trach was placed."
    record, warnings = verify_evidence_integrity(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.percutaneous_tracheostomy is not None
    assert record.procedures_performed.percutaneous_tracheostomy.device_name is None
    assert (
        "WIPED_DEVICE_NAME_NOT_IN_TEXT: procedures_performed.percutaneous_tracheostomy.device_name"
        in warnings
    )


def test_verify_evidence_integrity_does_not_flip_when_quote_present() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "therapeutic_aspiration": {
                    "performed": True,
                    "material": "Mucus plug",
                }
            }
        }
    )
    record.evidence = {
        "procedures_performed.therapeutic_aspiration.performed": [
            Span(text="Large mucus plug removal was performed", start=0, end=10),
        ]
    }

    note_text = "Large mucus plug removal was performed in the left mainstem bronchus."
    record, warnings = verify_evidence_integrity(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.therapeutic_aspiration is not None
    assert record.procedures_performed.therapeutic_aspiration.performed is True
    assert warnings == []


def test_sanitize_ebus_events_flips_needle_aspiration_when_not_biopsied() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["4R", "7"],
                    "node_events": [
                        {
                            "station": "4R",
                            "action": "needle_aspiration",
                            "outcome": None,
                            "evidence_quote": "FNA of station 4R performed",
                        },
                        {
                            "station": "7",
                            "action": "needle_aspiration",
                            "outcome": None,
                            "evidence_quote": "FNA of station 7 performed",
                        },
                    ],
                }
            }
        }
    )

    note_text = "Station 4R: benign ultrasound characteristics, not biopsied.\nStation 7: TBNA performed."
    warnings = sanitize_ebus_events(record, note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    events = linear.node_events

    by_station = {e.station.upper(): e for e in events}
    assert by_station["4R"].action == "inspected_only"
    assert "AUTO-CORRECTED" in by_station["4R"].evidence_quote
    assert by_station["7"].action == "needle_aspiration"

    assert linear.stations_sampled == ["7"]
    assert "AUTO_CORRECTED_EBUS_NEGATION: 4R" in warnings


def test_sanitize_ebus_events_flips_on_benign_ultrasound_characteristics_without_sampling() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "node_events": [
                        {
                            "station": "4R",
                            "action": "needle_aspiration",
                            "outcome": None,
                            "evidence_quote": "FNA of station 4R performed",
                        }
                    ],
                }
            }
        }
    )

    note_text = "Station 4R: benign ultrasound characteristics. Inspected."
    warnings = sanitize_ebus_events(record, note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    assert linear.node_events[0].action == "inspected_only"
    assert "AUTO_CORRECTED_EBUS_NEGATION: 4R" in warnings
