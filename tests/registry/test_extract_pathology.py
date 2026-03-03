from __future__ import annotations

from pathlib import Path

from app.registry.aggregation.pathology.extract_pathology import extract_pathology_event


_FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "case_events"


def _read(name: str) -> str:
    return (_FIXTURE_DIR / name).read_text()


def test_extract_pathology_station_negative_granulomatous() -> None:
    payload = extract_pathology_event(_read("path_ebus_granulomatous_negative.txt"))
    assert payload["qa_flags"] == []

    stations = {row["station"]: row for row in payload["node_updates"]}
    assert "11R" in stations
    assert stations["11R"]["path_result"] == "Negative"
    assert stations["11R"]["path_diagnosis_text"] == "Granulomatous lymphadenitis"


def test_extract_pathology_station_negative_simple() -> None:
    payload = extract_pathology_event(_read("path_ebus_negative_simple.txt"))
    stations = {row["station"]: row for row in payload["node_updates"]}
    assert "11L" in stations
    assert stations["11L"]["path_result"] == "Negative"


def test_extract_pathology_peripheral_malignant_adeno() -> None:
    payload = extract_pathology_event(_read("path_peripheral_malignant_adeno.txt"))
    assert payload["peripheral_updates"]
    row = payload["peripheral_updates"][0]
    assert row["lobe"] == "RLL"
    assert row["laterality"] == "R"
    assert row["path_result"] == "Positive"
    assert "Adenocarcinoma" in (row.get("path_diagnosis_text") or "")


def test_extract_pathology_final_diagnosis_keeps_station_specific_outcomes() -> None:
    payload = extract_pathology_event(_read("path_ebus_station_specific_final_diagnosis.txt"))
    stations = {row["station"]: row for row in payload["node_updates"]}

    assert stations["4R"]["path_result"] == "Negative"
    assert stations["4L"]["path_result"] == "Negative"
    assert stations["7"]["path_result"] == "Positive"
    assert stations["11RS"]["path_result"] == "Non-diagnostic"

    assert "adenocarcinoma" in str(stations["7"]["path_diagnosis_text"]).lower()
    assert "adenocarcinoma" not in str(stations["4R"]["path_diagnosis_text"]).lower()
    assert "adenocarcinoma" not in str(stations["4L"]["path_diagnosis_text"]).lower()
