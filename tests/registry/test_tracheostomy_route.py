from __future__ import annotations

from app.registry.deterministic_extractors import extract_established_tracheostomy_route


def test_established_tracheostomy_route_detected() -> None:
    note_text = "Bronchoscope inserted through existing tracheostomy stoma."
    result = extract_established_tracheostomy_route(note_text)
    assert result.get("established_tracheostomy_route") is True


def test_established_tracheostomy_route_not_for_new_trach() -> None:
    note_text = "Percutaneous tracheostomy performed. Bronchoscopy via trach."
    result = extract_established_tracheostomy_route(note_text)
    assert result == {}


def test_established_tracheostomy_route_not_for_immature_tract_reinsertion() -> None:
    note_text = (
        "Tracheostomy tube exchange performed after accidental decannulation on day 6. "
        "Stoma partially closed and tract immature, not yet epithelialized. "
        "Bronchoscopy used only for confirmation after reinsertion."
    )
    result = extract_established_tracheostomy_route(note_text)
    assert result == {}
