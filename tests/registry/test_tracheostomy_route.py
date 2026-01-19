from __future__ import annotations

from modules.registry.deterministic_extractors import extract_established_tracheostomy_route


def test_established_tracheostomy_route_detected() -> None:
    note_text = "Bronchoscope inserted through existing tracheostomy stoma."
    result = extract_established_tracheostomy_route(note_text)
    assert result.get("established_tracheostomy_route") is True


def test_established_tracheostomy_route_not_for_new_trach() -> None:
    note_text = "Percutaneous tracheostomy performed. Bronchoscopy via trach."
    result = extract_established_tracheostomy_route(note_text)
    assert result == {}
