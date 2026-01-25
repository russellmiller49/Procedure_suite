from __future__ import annotations

from modules.registry.application.pathology_extraction import apply_pathology_extraction
from modules.registry.schema import RegistryRecord


def test_pathology_extracts_histology_biomarkers_and_pdl1_percent() -> None:
    note = (
        "FINAL PATHOLOGY:\n"
        "Lung biopsy: Invasive adenocarcinoma.\n"
        "PD-L1 Tumor Proportion Score (TPS): 55%.\n"
        "EGFR: Negative.\n"
    )

    record, warnings = apply_pathology_extraction(RegistryRecord(), note)

    assert record.pathology_results is not None
    assert record.pathology_results.histology == "Adenocarcinoma"
    assert record.pathology_results.pdl1_tps_percent == 55
    assert record.pathology_results.pdl1_tps_text is None
    assert record.pathology_results.molecular_markers is not None, warnings
    assert record.pathology_results.molecular_markers.get("EGFR") is not None

    assert "pathology_results.histology" in record.evidence
    assert "pathology_results.pdl1_tps_percent" in record.evidence
    assert any("PATHOLOGY_EXTRACTED:" in w for w in warnings)


def test_pathology_extracts_pdl1_range_text() -> None:
    note = "PD-L1 TPS <1%. ALK rearrangement: positive."

    record, _warnings = apply_pathology_extraction(RegistryRecord(), note)

    assert record.pathology_results is not None
    assert record.pathology_results.pdl1_tps_percent is None
    assert record.pathology_results.pdl1_tps_text == "<1%"
    assert record.pathology_results.molecular_markers is not None
    assert record.pathology_results.molecular_markers.get("ALK") is not None

    assert "pathology_results.pdl1_tps_text" in record.evidence
