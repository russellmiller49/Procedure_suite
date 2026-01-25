from __future__ import annotations

from modules.coder.adapters.persistence.csv_kb_adapter import JsonKnowledgeBaseAdapter


def test_kb_prefers_fee_schedule_professional_descriptions() -> None:
    kb = JsonKnowledgeBaseAdapter("data/knowledge/ip_coding_billing_v3_0.json")

    info = kb.get_procedure_info("31641")
    assert info is not None
    assert (
        info.description
        == "Bronchoscopy; with destruction of tumor or relief of stenosis by any method"
    )

    # Fallback: codes without fee schedule descriptions keep the short descriptor.
    info2 = kb.get_procedure_info("32609")
    assert info2 is not None
    assert info2.description == "Thoracoscopy w/bx pleura"

