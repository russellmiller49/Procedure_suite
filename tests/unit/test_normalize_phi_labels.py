from typing import Literal

from scripts.normalize_phi_labels import normalize_tags

PasswordPolicy = Literal["id", "drop"]


def _normalize(tags: list[str], *, password_policy: PasswordPolicy = "id") -> list[str]:
    normalized, _, _, _, _ = normalize_tags(tags, password_policy=password_policy)
    return normalized


def test_password_policy_id_maps_to_id() -> None:
    tags = ["B-PASSWORD", "I-PASSWORD"]
    assert _normalize(tags, password_policy="id") == ["B-ID", "I-ID"]


def test_password_policy_drop_maps_to_o() -> None:
    tags = ["B-PASSWORD", "I-PASSWORD"]
    assert _normalize(tags, password_policy="drop") == ["O", "O"]


def test_street_maps_to_geo() -> None:
    tags = ["B-STREET", "I-STREET"]
    assert _normalize(tags) == ["B-GEO", "I-GEO"]


def test_dateofbirth_maps_to_date() -> None:
    tags = ["B-DATEOFBIRTH"]
    assert _normalize(tags) == ["B-DATE"]


def test_bio_repair_o_then_i() -> None:
    tags = ["O", "I-ID"]
    assert _normalize(tags) == ["O", "B-ID"]


def test_bio_repair_mismatch_converts_i_to_b() -> None:
    tags = ["B-GEO", "I-ID"]
    assert _normalize(tags) == ["B-GEO", "B-ID"]
