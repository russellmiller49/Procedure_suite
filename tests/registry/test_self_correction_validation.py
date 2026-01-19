from __future__ import annotations

import pytest

from modules.registry.self_correction.judge import PatchProposal
from modules.registry.self_correction.validation import validate_proposal


def _proposal(path: str) -> PatchProposal:
    return PatchProposal(
        rationale="test",
        json_patch=[{"op": "add", "path": path, "value": True}],
        evidence_quote="brushings performed",
    )


def test_validate_proposal_allows_nested_prefix_path() -> None:
    proposal = _proposal("/procedures_performed/brushings/details/source")
    is_valid, reason = validate_proposal(proposal, "brushings performed")
    assert is_valid, reason


def test_validate_proposal_respects_env_prefix_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REGISTRY_SELF_CORRECT_ALLOWLIST", "/procedures_performed/brushings/*")

    allowed = _proposal("/procedures_performed/brushings/details/source")
    is_valid, reason = validate_proposal(allowed, "brushings performed")
    assert is_valid, reason

    blocked = _proposal("/procedures_performed/tbna_conventional/performed")
    is_valid, reason = validate_proposal(blocked, "brushings performed")
    assert not is_valid
    assert "Path not allowed" in reason


def test_validate_proposal_allows_mechanical_debulking_prefix_path() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[{"op": "add", "path": "/procedures_performed/mechanical_debulking/method", "value": "Rigid coring"}],
        evidence_quote="mechanical debulking",
    )
    is_valid, reason = validate_proposal(proposal, "mechanical debulking")
    assert is_valid, reason
