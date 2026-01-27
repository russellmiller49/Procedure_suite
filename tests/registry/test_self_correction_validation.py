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


def test_validate_proposal_allows_granular_data_prefix_path() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[{"op": "add", "path": "/granular_data/cryobiopsy_sites/0/lobe", "value": "RUL"}],
        evidence_quote="cryobiopsy performed",
    )
    is_valid, reason = validate_proposal(proposal, "cryobiopsy performed")
    assert is_valid, reason


def test_validate_proposal_normalizes_whitespace_in_quote_matching() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[{"op": "add", "path": "/procedures_performed/brushings/performed", "value": True}],
        evidence_quote="Brushings performed",
    )
    note_text = "Brushings\nperformed"
    is_valid, reason = validate_proposal(proposal, note_text)
    assert is_valid, reason


def test_validate_proposal_canonicalizes_known_alias_paths() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[{"op": "add", "path": "/procedures_performed/balloon_dilation/performed", "value": True}],
        evidence_quote="balloon dilation",
    )
    is_valid, reason = validate_proposal(proposal, "balloon dilation")
    assert is_valid, reason
    assert proposal.json_patch[0]["path"] == "/procedures_performed/airway_dilation/performed"


def test_validate_proposal_canonicalizes_fibrinolysis_instillation_alias_path() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[{"op": "add", "path": "/pleural_procedures/fibrinolysis_instillation/performed", "value": True}],
        evidence_quote="tPA/DNase instillation",
    )
    is_valid, reason = validate_proposal(proposal, "tPA/DNase instillation via chest tube")
    assert is_valid, reason
    assert proposal.json_patch[0]["path"] == "/pleural_procedures/fibrinolytic_therapy/performed"


def test_validate_proposal_canonicalizes_tunneled_pleural_catheter_alias_path() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[
            {"op": "add", "path": "/pleural_procedures/tunneled_pleural_catheter/performed", "value": True}
        ],
        evidence_quote="tunneled pleural catheter",
    )
    is_valid, reason = validate_proposal(proposal, "tunneled pleural catheter inserted")
    assert is_valid, reason
    assert proposal.json_patch[0]["path"] == "/pleural_procedures/ipc/performed"


def test_validate_proposal_allows_established_tracheostomy_route_path() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[{"op": "add", "path": "/established_tracheostomy_route", "value": True}],
        evidence_quote="established tracheostomy",
    )
    is_valid, reason = validate_proposal(proposal, "bronchoscopy through established tracheostomy")
    assert is_valid, reason


def test_validate_proposal_canonicalizes_ebus_elastography_alias_path() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[
            {"op": "add", "path": "/procedures_performed/ebus_elastography/performed", "value": True}
        ],
        evidence_quote="EBUS elastography",
    )
    is_valid, reason = validate_proposal(proposal, "EBUS elastography was performed")
    assert is_valid, reason
    assert proposal.json_patch[0]["path"] == "/procedures_performed/linear_ebus/elastography_used"


def test_validate_proposal_canonicalizes_linear_ebus_elastography_performed_alias_path() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[
            {"op": "add", "path": "/procedures_performed/linear_ebus/elastography_performed", "value": True}
        ],
        evidence_quote="EBUS elastography",
    )
    is_valid, reason = validate_proposal(proposal, "EBUS elastography was performed")
    assert is_valid, reason
    assert proposal.json_patch[0]["path"] == "/procedures_performed/linear_ebus/elastography_used"


def test_validate_proposal_expands_ebus_elastography_root_object_patch() -> None:
    proposal = PatchProposal(
        rationale="test",
        json_patch=[
            {
                "op": "add",
                "path": "/procedures_performed/ebus_elastography",
                "value": {"performed": True, "pattern": "Type 1 elastographic pattern"},
            }
        ],
        evidence_quote="EBUS elastography",
    )
    is_valid, reason = validate_proposal(proposal, "EBUS elastography was performed")
    assert is_valid, reason
    assert {op["path"] for op in proposal.json_patch} == {
        "/procedures_performed/linear_ebus/elastography_used",
        "/procedures_performed/linear_ebus/elastography_pattern",
    }
