from __future__ import annotations

from app.registry.deterministic_extractors import extract_providers
from app.registry.postprocess import normalize_attending_name


def test_normalize_attending_name_bans_common_header_words() -> None:
    assert normalize_attending_name("Participation") is None
    assert normalize_attending_name("ATTENDING") is None
    assert normalize_attending_name("SIGNED") is None


def test_extract_providers_attending_participation_captures_name_not_header() -> None:
    note_text = "Attending Participation: Dr John Smith\nFellow: Dr Jane Doe\n"
    providers = extract_providers(note_text)
    assert providers.get("attending_name") == "John Smith"

