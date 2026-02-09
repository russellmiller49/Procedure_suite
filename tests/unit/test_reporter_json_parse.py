from __future__ import annotations

import json

import pytest

from ml.lib.reporter_bundle_codec import encode_bundle_keys_v1
from ml.lib.reporter_json_parse import (
    ReporterJSONParseError,
    parse_and_validate_bundle,
    parse_json_object_strict,
)


def _bundle_payload() -> dict:
    return {
        "patient": {},
        "encounter": {},
        "procedures": [
            {
                "proc_type": "other",
                "schema_id": "other.v1",
                "data": {"procedures_performed": {"bal": {"performed": True}}},
                "cpt_candidates": ["31624"],
            }
        ],
    }


def test_parse_json_object_strict_handles_markdown_fences_and_trailing_commas() -> None:
    raw = """```json
{
  "patient": {},
  "encounter": {},
  "procedures": [
    {"proc_type": "other", "schema_id": "other.v1", "data": {},}
  ],
}
```"""
    payload, notes = parse_json_object_strict(raw)
    assert isinstance(payload, dict)
    assert payload["procedures"][0]["proc_type"] == "other"
    assert "removed_trailing_commas" in notes


def test_parse_json_object_strict_extracts_balanced_object_from_wrapped_text() -> None:
    raw = 'prefix text {"patient":{},"encounter":{},"procedures":[{"proc_type":"other","schema_id":"other.v1","data":{}}]} suffix'
    payload, notes = parse_json_object_strict(raw)
    assert payload["patient"] == {}
    assert "used_balanced_object_extraction" in notes


def test_parse_json_object_strict_raises_on_unrecoverable_input() -> None:
    with pytest.raises(ReporterJSONParseError):
        parse_json_object_strict("not json")


def test_parse_and_validate_bundle_decodes_codec_payload() -> None:
    encoded = encode_bundle_keys_v1(_bundle_payload())
    raw = json.dumps(encoded)
    bundle, payload, _notes = parse_and_validate_bundle(raw, decode_codec=True)
    assert bundle.procedures
    assert payload["procedures"][0]["proc_type"] == "other"

