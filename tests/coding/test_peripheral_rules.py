"""Unit tests for peripheral lesion evidence to code mapping."""

from __future__ import annotations

from modules.coder.peripheral_rules import peripheral_lesions_to_candidates
from modules.coder.types import PeripheralLesionEvidence


def _codes_for(lesions: list[PeripheralLesionEvidence]) -> set[str]:
    return {candidate.code.lstrip("+") for candidate in peripheral_lesions_to_candidates(lesions)}


def test_peripheral_rules_empty_input_returns_no_candidates():
    assert peripheral_lesions_to_candidates([]) == []


def test_peripheral_rules_map_complex_peripheral_case():
    lesions = [
        PeripheralLesionEvidence(
            lobe="LLL",
            segment="LB10",
            actions=["Cryobiopsy", "TBNA", "Brush", "BAL", "Fiducial"],
            navigation=True,
            radial_ebus=True,
        )
    ]

    codes = _codes_for(lesions)
    assert {"31628", "31626", "31624", "31627", "31654"}.issubset(codes)


def test_peripheral_rules_ignore_tbna_only_lesion():
    lesions = [
        PeripheralLesionEvidence(
            lobe="LLL",
            segment="LB10",
            actions=["TBNA", "Brush"],
            navigation=False,
            radial_ebus=False,
        )
    ]

    codes = _codes_for(lesions)
    assert codes == set()
