from __future__ import annotations

from app.agents.aggregator.timeline_aggregator import LinkProposal
from app.agents.relation_extraction.shadow_mode import merge_relations_shadow_mode


def test_merge_prefers_high_confidence_ml() -> None:
    heuristic = [
        LinkProposal(
            entity_id="e1",
            linked_to_id="l_old",
            relation="linked_to_lesion",
            confidence=0.6,
            reasoning_short="heuristic",
        )
    ]
    ml = [
        LinkProposal(
            entity_id="e1",
            linked_to_id="l_new",
            relation="linked_to_lesion",
            confidence=0.92,
            reasoning_short="ml confident",
        )
    ]

    merged = merge_relations_shadow_mode(
        relations_heuristic=heuristic,
        relations_ml=ml,
        confidence_threshold=0.85,
    )

    assert merged.relations == [ml[0]]
    assert merged.warnings == []
    assert merged.metrics["override_keys"] == 1
    assert merged.metrics["used_ml_keys"] == 1


def test_merge_falls_back_when_ml_below_threshold() -> None:
    heuristic = [
        LinkProposal(
            entity_id="e1",
            linked_to_id="l_old",
            relation="specimen_from_lesion",
            confidence=0.7,
            reasoning_short="heuristic",
        )
    ]
    ml = [
        LinkProposal(
            entity_id="e1",
            linked_to_id="l_new",
            relation="specimen_from_lesion",
            confidence=0.8,
            reasoning_short="ml unsure",
        )
    ]

    merged = merge_relations_shadow_mode(
        relations_heuristic=heuristic,
        relations_ml=ml,
        confidence_threshold=0.85,
    )

    assert merged.relations == heuristic
    assert merged.warnings
    assert "RELATIONS_ML_BELOW_THRESHOLD" in merged.warnings[0]
    assert merged.metrics["below_threshold_keys"] == 1
    assert merged.metrics["used_ml_keys"] == 0


def test_merge_keeps_ml_edge_when_no_heuristic() -> None:
    merged = merge_relations_shadow_mode(
        relations_heuristic=[],
        relations_ml=[
            LinkProposal(
                entity_id="e2",
                linked_to_id="l2",
                relation="linked_to_lesion",
                confidence=0.95,
                reasoning_short="ml only",
            )
        ],
        confidence_threshold=0.85,
    )

    assert len(merged.relations) == 1
    assert merged.relations[0].entity_id == "e2"
    assert merged.metrics["ml_only_keys"] == 1
    assert merged.metrics["override_keys"] == 0
