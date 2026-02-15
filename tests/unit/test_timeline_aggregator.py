from __future__ import annotations

from app.agents.aggregator.timeline_aggregator import (
    BundleDocInput,
    aggregate_entity_ledger,
)


def test_entity_ledger_clusters_nav_targets_and_links_specimens() -> None:
    docs = [
        BundleDocInput(
            timepoint_role="INDEX_PROCEDURE",
            seq=1,
            doc_t_offset_days=0,
            registry={
                "granular_data": {
                    "navigation_targets": [
                        {
                            "target_number": 1,
                            "target_location_text": "RUL RB1 apical segment",
                            "target_lobe": "RUL",
                            "target_segment": "RB1",
                            "lesion_size_mm": 22,
                            "tool_in_lesion_confirmed": True,
                        }
                    ],
                    "specimens_collected": [
                        {
                            "specimen_number": 1,
                            "source_procedure": "Navigation biopsy",
                            "source_location": "RUL RB1",
                            "final_pathology_diagnosis": "Adenocarcinoma",
                        }
                    ],
                }
            },
        ),
        BundleDocInput(
            timepoint_role="FOLLOW_UP",
            seq=2,
            doc_t_offset_days=5,
            registry={
                "granular_data": {
                    "navigation_targets": [
                        {
                            "target_number": 1,
                            "target_location_text": "RUL RB1",
                            "target_lobe": "RUL",
                            "target_segment": "RB1",
                            "lesion_size_mm": 23,
                        }
                    ]
                }
            },
        ),
    ]

    ledger = aggregate_entity_ledger(docs)

    lesions = [e for e in ledger.entities if e.kind == "canonical_lesion"]
    assert len(lesions) == 1
    lesion_id = lesions[0].entity_id

    nav_targets = [e for e in ledger.entities if e.kind == "nav_target"]
    assert len(nav_targets) == 2
    nav_target_ids = {e.entity_id for e in nav_targets}

    nav_links = [
        link for link in ledger.link_proposals if link.relation == "linked_to_lesion"
    ]
    assert nav_target_ids.issubset({link.entity_id for link in nav_links})
    assert all(link.linked_to_id == lesion_id for link in nav_links)
    assert all(0.0 <= link.confidence <= 1.0 for link in nav_links)

    specimens = [e for e in ledger.entities if e.kind == "specimen"]
    assert len(specimens) == 1
    specimen_id = specimens[0].entity_id

    specimen_links = [
        link
        for link in ledger.link_proposals
        if link.relation == "specimen_from_lesion"
    ]
    assert len(specimen_links) == 1
    assert specimen_links[0].entity_id == specimen_id
    assert specimen_links[0].linked_to_id == lesion_id
    assert specimen_links[0].confidence >= 0.6
