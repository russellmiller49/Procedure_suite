from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.agents.aggregator.timeline_aggregator import (
    EntityLedger,
    LedgerEntity,
    LinkProposal,
)
from app.agents.relation_extraction.llm_proposer import propose_relations_ml


class _StubLLM:
    def __init__(self, proposals: list[LinkProposal]) -> None:
        self._proposals = proposals

    def generate_json(self, **_kwargs):
        return SimpleNamespace(proposals=self._proposals)


@pytest.mark.usefixtures("baseline_env")
def test_propose_relations_ml_filters_and_dedupes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RELATIONS_ML_ENABLED", "1")
    monkeypatch.setenv("REGISTRY_USE_STUB_LLM", "0")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_OFFLINE", "0")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    ledger = EntityLedger(
        entities=[
            LedgerEntity(
                entity_id="lesion_1",
                kind="canonical_lesion",
                label="Lesion: RUL RB1 (~22mm)",
                doc_ref=None,
                attributes={"location_key": "RUL:RB1"},
            ),
            LedgerEntity(
                entity_id="spec_1",
                kind="specimen",
                label="Specimen 1: Navigation biopsy — RUL RB1",
                doc_ref=None,
                attributes={"source_location": "RUL RB1"},
            ),
            LedgerEntity(
                entity_id="spec_2",
                kind="specimen",
                label="Specimen 2: Navigation biopsy — RLL",
                doc_ref=None,
                attributes={"source_location": "RLL"},
            ),
            LedgerEntity(
                entity_id="nav_1",
                kind="nav_target",
                label="Nav target: RUL RB1 (22mm)",
                doc_ref=None,
                attributes={"target_lobe": "RUL", "target_segment": "RB1"},
            ),
        ],
        link_proposals=[],
    )

    stub = _StubLLM(
        proposals=[
            # Valid; should be kept (after dedupe, higher confidence wins).
            LinkProposal(
                entity_id="spec_1",
                linked_to_id="lesion_1",
                relation="specimen_from_lesion",
                confidence=0.81,
                reasoning_short="matches location",
            ),
            LinkProposal(
                entity_id="spec_1",
                linked_to_id="lesion_1",
                relation="specimen_from_lesion",
                confidence=0.93,
                reasoning_short="same lobe/segment",
            ),
            # Invalid target id; should be dropped.
            LinkProposal(
                entity_id="spec_2",
                linked_to_id="lesion_missing",
                relation="specimen_from_lesion",
                confidence=0.9,
                reasoning_short="unknown",
            ),
            # Invalid relation; should be dropped.
            LinkProposal(
                entity_id="spec_2",
                linked_to_id="lesion_1",
                relation="same_as",
                confidence=0.9,
                reasoning_short="n/a",
            ),
            # Not requested candidate kind by default (nav targets off); should be dropped.
            LinkProposal(
                entity_id="nav_1",
                linked_to_id="lesion_1",
                relation="linked_to_lesion",
                confidence=0.95,
                reasoning_short="location match",
            ),
        ]
    )

    result = propose_relations_ml(ledger=ledger, llm=stub)

    assert result.warnings == []
    assert len(result.relations_ml) == 1
    assert result.relations_ml[0].entity_id == "spec_1"
    assert result.relations_ml[0].linked_to_id == "lesion_1"
    assert result.relations_ml[0].confidence == 0.93
    assert result.metrics.get("candidate_entity_count") == 2
    assert result.metrics.get("proposal_count") == 1

