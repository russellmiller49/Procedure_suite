from __future__ import annotations

from ml.lib.reporter_bundle_codec import (
    CODEC_MARKER_KEY,
    CODEC_VERSION_V1,
    decode_bundle_keys_v1,
    encode_bundle_keys_v1,
    rough_token_len,
)


def _sample_bundle_payload() -> dict:
    return {
        "patient": {"age": 62, "sex": "M"},
        "encounter": {"date": "2025-01-01"},
        "procedures": [
            {
                "proc_type": "bronchoscopy",
                "schema_id": "bronch.v1",
                "proc_id": "bronch_1",
                "data": {"procedures_performed": {"bal": {"performed": True}}},
                "cpt_candidates": ["31624"],
            }
        ],
        "free_text_hint": "example",
        "addons": ["post_op_note"],
    }


def test_codec_round_trip_preserves_payload() -> None:
    payload = _sample_bundle_payload()
    encoded = encode_bundle_keys_v1(payload)

    assert encoded[CODEC_MARKER_KEY] == CODEC_VERSION_V1
    assert "patient" not in encoded
    assert "pt" in encoded

    decoded = decode_bundle_keys_v1(encoded)
    assert decoded == payload


def test_decode_is_passthrough_without_marker() -> None:
    payload = _sample_bundle_payload()
    assert decode_bundle_keys_v1(payload) == payload


def test_rough_token_len_is_positive() -> None:
    assert rough_token_len("") == 1
    assert rough_token_len("abcd") == 1
    assert rough_token_len("abcdefgh") == 2

