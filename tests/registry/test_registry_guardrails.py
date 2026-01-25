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


def test_verify_evidence_integrity_keeps_therapeutic_aspiration_with_contextual_suction() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "therapeutic_aspiration": {
                    "performed": True,
                }
            }
        }
    )
    record.evidence = {}

    note_text = "Routine suctioning performed. Copious secretions were suctioned from the airway."
    record, warnings = verify_evidence_integrity(record, note_text)

    assert record.procedures_performed is not None
    assert record.procedures_performed.therapeutic_aspiration is not None
    assert record.procedures_performed.therapeutic_aspiration.performed is True
    assert warnings == []
    assert "procedures_performed.therapeutic_aspiration.performed" in (record.evidence or {})


def test_verify_evidence_integrity_keeps_therapeutic_aspiration_across_newlines() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "therapeutic_aspiration": {
                    "performed": True,
                }
            }
        }
    )
    record.evidence = {}

    note_text = "Routine suctioning performed.\nCopious secretions\nwere suctioned from the airway."
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


def test_sanitize_ebus_events_drops_sampling_for_criteria_only_stations() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["10R", "11L", "11RS", "2R", "4L", "4R", "7"],
                    "node_events": [
                        {"station": "10R", "action": "needle_aspiration", "outcome": None, "evidence_quote": "10R"},
                        {"station": "4L", "action": "needle_aspiration", "outcome": None, "evidence_quote": "4L"},
                        {"station": "11Rs", "action": "needle_aspiration", "outcome": None, "evidence_quote": "11Rs"},
                        {"station": "7", "action": "needle_aspiration", "outcome": None, "evidence_quote": "7"},
                        {"station": "4R", "action": "needle_aspiration", "outcome": None, "evidence_quote": "4R"},
                        {"station": "2R", "action": "needle_aspiration", "outcome": None, "evidence_quote": "2R"},
                        {"station": "11L", "action": "needle_aspiration", "outcome": None, "evidence_quote": "11L"},
                    ],
                }
            }
        }
    )

    note_text = (
        "A systematic hilar and mediastinal lymph node survey was carried out. "
        "Sampling criteria (5mm short axis diameter) were met in station 11Rs (6.7mm), 10R (5.7mm), 4R (9.1mm), "
        "2R (7.1 mm), 7 (15.7mm), 4L (6.9mm), and 11L (21.1mm) lymph nodes.\n"
        "Sampling by transbronchial needle aspiration was performed beginning with the 11Rs lymph node followed by 7, "
        "and 4R, 2R lymph nodes using an Olympus EBUSTBNA 22 gauge needle.\n"
        "We then moved to the large 11L lymph node and took 8 additional passes.\n"
    )

    warnings = sanitize_ebus_events(record, note_text)

    linear = record.procedures_performed.linear_ebus  # type: ignore[union-attr]
    by_station = {e.station.upper(): e for e in (linear.node_events or [])}

    assert by_station["10R"].action == "inspected_only"
    assert by_station["4L"].action == "inspected_only"
    assert by_station["7"].action == "needle_aspiration"
    assert by_station["4R"].action == "needle_aspiration"
    assert by_station["2R"].action == "needle_aspiration"
    assert by_station["11RS"].action == "needle_aspiration"
    assert by_station["11L"].action == "needle_aspiration"

    assert linear.stations_sampled == ["11L", "11RS", "2R", "4R", "7"]
    assert "AUTO_CORRECTED_EBUS_CRITERIA_ONLY: 10R" in warnings
    assert "AUTO_CORRECTED_EBUS_CRITERIA_ONLY: 4L" in warnings
