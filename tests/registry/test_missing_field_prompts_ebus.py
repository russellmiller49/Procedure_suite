from __future__ import annotations

from app.registry.completeness import generate_missing_field_prompts
from app.registry.schema import RegistryRecord


def _ebus_prompts(record: RegistryRecord):
    return [p for p in generate_missing_field_prompts(record) if p.group == "EBUS"]


def test_ebus_passes_from_node_events_suppress_pass_prompt() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["11RI", "11RS", "7"],
                    "needle_gauge": "22G",
                    "node_events": [
                        {
                            "station": "7",
                            "action": "needle_aspiration",
                            "passes": 5,
                            "pass_count": 5,
                            "evidence_quote": "station 7 sampled with five passes",
                        },
                        {
                            "station": "11RS",
                            "action": "needle_aspiration",
                            "passes": 5,
                            "outcome": "benign",
                            "evidence_quote": "station 11RS sampled with five passes",
                        },
                        {
                            "station": "11RI",
                            "action": "needle_aspiration",
                            "passes": 5,
                            "outcome": "benign",
                            "evidence_quote": "station 11RI sampled with five passes",
                        },
                    ],
                }
            },
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "7", "sampled": True, "needle_gauge": 22},
                ]
            },
        }
    )

    prompts = _ebus_prompts(record)
    labels = {p.label for p in prompts}

    assert "Passes (station 7)" not in labels
    assert "Passes (station 11RI)" not in labels
    assert "Passes (station 11RS)" not in labels
    assert "Per-station detail row (station 11RI)" not in labels
    assert "Per-station detail row (station 11RS)" not in labels


def test_ebus_pass_prompt_is_station_specific_for_missing_station_only() -> None:
    record = RegistryRecord.model_validate(
        {
            "procedures_performed": {
                "linear_ebus": {
                    "performed": True,
                    "stations_sampled": ["7", "4R"],
                }
            },
            "granular_data": {
                "linear_ebus_stations_detail": [
                    {"station": "7", "sampled": True, "number_of_passes": 4},
                    {"station": "4R", "sampled": True},
                ]
            },
        }
    )

    prompts = _ebus_prompts(record)
    labels = {p.label for p in prompts}

    assert "Passes (station 7)" not in labels
    assert "Passes (station 4R)" in labels

    passes_prompt = next(p for p in prompts if p.label == "Passes (station 4R)")
    assert passes_prompt.target_path == "granular_data.linear_ebus_stations_detail[1].number_of_passes"
