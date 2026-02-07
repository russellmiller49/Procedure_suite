from __future__ import annotations

from app.registry.application.pathology_extraction import apply_pathology_extraction
from app.registry.schema import RegistryRecord


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


def test_pathology_does_not_extract_histology_from_staging_indication_line() -> None:
    note = (
        "Endobronchial Ultrasound Findings and Sampling\n"
        "Lymph node sizing and sampling were performed for non–small cell lung cancer staging using an Olympus 22-gauge EBUS-TBNA needle. "
        "Samples were obtained from the following stations and sent for routine cytology:\n"
        "Station 4L: Rapid on-site evaluation indicated adequate tissue.\n"
    )

    record, warnings = apply_pathology_extraction(RegistryRecord(), note)

    assert record.pathology_results is None
    assert warnings == []
