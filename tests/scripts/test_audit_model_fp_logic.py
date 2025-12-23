import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")

from scripts import audit_model_fp


def test_cpt_split_accepts_two_token_pattern():
    tokens = ["316", "##53"]
    assert audit_model_fp.is_stable_cpt_split(tokens, 0) == "31653"


def test_cpt_split_rejects_three_token_pattern():
    tokens = ["770", "##0", "##2"]
    assert audit_model_fp.is_stable_cpt_split(tokens, 0) is None


def test_volume_exemption_detects_liters_drained():
    tokens = ["1", ".", "1", "##l", "drained"]
    assert audit_model_fp.is_volume_context(tokens, 2) is True
