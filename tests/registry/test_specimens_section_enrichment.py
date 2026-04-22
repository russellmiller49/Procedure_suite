from __future__ import annotations

from app.registry.postprocess import enrich_specimens_from_specimen_section
from app.registry.schema import RegistryRecord


def test_enrich_specimens_from_specimen_section_populates_bal_item() -> None:
    record = RegistryRecord.model_validate({"procedures_performed": {"bal": {"performed": True}}})
    note_text = (
        "SPECIMEN(S):\n"
        "--LUL BAL (cell count, micro, cyto)\n"
        "\n"
        "IMPRESSION/PLAN: done\n"
    )

    warnings = enrich_specimens_from_specimen_section(record, note_text)
    assert any("AUTO_SPECIMENS" in str(w) for w in warnings)

    assert record.specimens is not None
    specimens = record.specimens.specimens_collected
    assert specimens is not None
    assert len(specimens) == 1
    assert specimens[0].type == "BAL"
    assert str(specimens[0].location or "").upper() == "LUL"
    assert set(specimens[0].sent_for or []) >= {"Cytology", "Microbiology", "Other"}


def test_enrich_specimens_from_specimen_section_keeps_blank_separated_tbna_and_bal_items() -> None:
    record = RegistryRecord.model_validate(
        {"procedures_performed": {"bal": {"performed": True}, "linear_ebus": {"performed": True}}}
    )
    note_text = (
        "SPECIMEN(S):\n"
        "\n"
        "“4R TBNA” (passes 1-5)\n"
        "\n"
        "“7 TBNA” (passes 1-6)\n"
        "\n"
        "“11L TBNA” (passes 1-3)\n"
        "\n"
        "“RUL BAL”\n"
        "\n"
        "IMPRESSION/PLAN: done\n"
    )

    warnings = enrich_specimens_from_specimen_section(record, note_text)
    assert any("AUTO_SPECIMENS" in str(w) for w in warnings)

    assert record.specimens is not None
    specimens = record.specimens.specimens_collected
    assert specimens is not None
    assert [(spec.type, spec.location) for spec in specimens] == [
        ("TBNA", "4R"),
        ("TBNA", "7"),
        ("TBNA", "11L"),
        ("BAL", "RUL"),
    ]
