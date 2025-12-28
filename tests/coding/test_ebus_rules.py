"""Unit tests for EBUS evidence counting and mapping."""

from __future__ import annotations

from modules.coder.ebus_rules import ebus_nodes_to_candidates, _count_sampled_nodes
from modules.coder.types import EBUSNodeEvidence


def test_count_sampled_nodes_ignores_inspection_only():
    evidence = [
        EBUSNodeEvidence(station="7", action="Inspection"),
        EBUSNodeEvidence(station="4R", action="Sampling", method="EBUS-linear"),
        EBUSNodeEvidence(station="11L", action="Sampling", method=None),
    ]
    assert _count_sampled_nodes(evidence) == 2


def test_ebus_nodes_to_candidates_returns_empty_for_zero_sampling():
    evidence = [EBUSNodeEvidence(station="7", action="Inspection")]
    assert ebus_nodes_to_candidates(evidence) == []


def test_ebus_nodes_to_candidates_maps_counts_to_cpt_codes():
    evidence = [EBUSNodeEvidence(station="7", action="Sampling")]
    candidates = ebus_nodes_to_candidates(evidence)
    assert len(candidates) == 1
    assert candidates[0].code == "31652"
    assert "ebus_nodes:sampled_count=1" in (candidates[0].reason or "")


def test_ebus_nodes_to_candidates_three_plus_nodes():
    evidence = [
        EBUSNodeEvidence(station="4R", action="Sampling"),
        EBUSNodeEvidence(station="7", action="Sampling"),
        EBUSNodeEvidence(station="11L", action="Sampling"),
    ]
    candidates = ebus_nodes_to_candidates(evidence)
    assert candidates and candidates[0].code == "31653"
