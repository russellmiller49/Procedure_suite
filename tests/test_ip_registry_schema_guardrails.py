from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft7Validator


_SCHEMA_PATH = Path("data/knowledge/IP_Registry.json")


def _load_validator() -> Draft7Validator:
    schema = json.loads(_SCHEMA_PATH.read_text())
    Draft7Validator.check_schema(schema)
    return Draft7Validator(schema)


def _base_entry() -> dict:
    return {
        "patient_mrn": "MRN-001",
        "procedure_date": "2026-01-01",
        "providers": {"attending_name": "Dr Test"},
        "metadata": {"data_entry_status": "Complete"},
    }


def _errors(entry: dict) -> list[str]:
    validator = _load_validator()
    return sorted(err.message for err in validator.iter_errors(entry))


def test_granular_ebus_requires_performed_true():
    entry = _base_entry()
    entry["granular_data"] = {"linear_ebus_stations_detail": [{"station": "7"}]}
    assert _errors(entry)

    entry["procedures_performed"] = {"linear_ebus": {"performed": True}}
    assert not _errors(entry)


def test_performed_false_disallows_ebus_details():
    entry = _base_entry()
    entry["procedures_performed"] = {"linear_ebus": {"performed": False, "stations_sampled": ["7"]}}
    assert _errors(entry)


def test_never_smoker_requires_zero_pack_years():
    entry = _base_entry()
    entry["patient_demographics"] = {"smoking_status": "Never", "pack_years": 10}
    assert _errors(entry)

    entry["patient_demographics"]["pack_years"] = 0
    assert not _errors(entry)


def test_dlt_sizing_supported():
    entry = _base_entry()
    entry["procedure_setting"] = {"airway_device_type": "DLT", "dlt_size_fr": 37}
    assert not _errors(entry)

    entry["procedure_setting"]["dlt_size_fr"] = 100
    assert _errors(entry)


def test_any_complication_false_disallows_complication_list_items():
    entry = _base_entry()
    entry["complications"] = {"any_complication": False, "complication_list": ["Hypoxia"]}
    assert _errors(entry)


def test_trainee_present_requires_name():
    entry = _base_entry()
    entry["providers"]["trainee_present"] = True
    assert _errors(entry)

    entry["providers"]["fellow_name"] = "Dr Fellow"
    assert not _errors(entry)

