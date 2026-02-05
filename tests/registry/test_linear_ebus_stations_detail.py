from __future__ import annotations

from modules.registry.processing.linear_ebus_stations_detail import extract_linear_ebus_stations_detail


def _by_station(items: list[dict]) -> dict[str, dict]:
    return {str(item.get("station")): item for item in items if isinstance(item, dict) and item.get("station")}


def test_extract_linear_ebus_stations_detail_station_paragraphs_and_stop_at_mass_header() -> None:
    note = (
        "Procedure Name: Bronchoscopy with Endobronchial Ultrasound\n"
        "Sampling was performed using an Olympus 22-gauge EBUS-TBNA needle and sent for routine cytology.\n"
        "\n"
        "Station 4R (lower paratracheal): Measured 1.9 mm by EBUS and 2.4 mm by CT. "
        "Ultrasound characteristics included hypoechoic, heterogeneous, irregular shape with sharp margins. "
        "This node was not biopsied due to benign ultrasound characteristics and size criteria.\n"
        "\n"
        "Station 7 (subcarinal): Measured 5.4 mm by EBUS and 4.8 mm by CT. "
        "Ultrasound characteristics included heterogeneous, irregular shape with sharp margins. "
        "This node was biopsied using a 22-gauge needle with five passes. "
        "ROSE preliminary analysis indicated adequate tissue.\n"
        "\n"
        "Station 11Rs: Measured 7.3 mm by EBUS and 5.4 mm by CT. "
        "Ultrasound characteristics included heterogeneous, irregular shape with sharp margins. "
        "This node was biopsied using a 22-gauge needle with five passes. "
        "ROSE preliminary analysis indicated adequate tissue.\n"
        "\n"
        "Right upper lobe mass: Measured 19 mm by EBUS and 22 mm by CT. "
        "This lesion was biopsied using a 22-gauge needle with eight passes. "
        "ROSE preliminary analysis indicated malignancy.\n"
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert by_station["4R"]["sampled"] is False
    assert by_station["4R"]["short_axis_mm"] == 1.9
    assert "needle_gauge" not in by_station["4R"]  # avoid "ghost gauge" on unsampled nodes

    assert by_station["7"]["sampled"] is True
    assert by_station["7"]["needle_gauge"] == 22
    assert by_station["7"]["number_of_passes"] == 5
    assert by_station["7"]["rose_result"] == "Adequate lymphocytes"

    assert by_station["11Rs"]["sampled"] is True
    assert by_station["11Rs"]["needle_gauge"] == 22
    assert by_station["11Rs"]["number_of_passes"] == 5
    assert by_station["11Rs"]["rose_result"] == "Adequate lymphocytes"

    # Non-station diagnostic targets should still be captured as entries.
    assert by_station["Right Upper Lobe Mass"]["sampled"] is True
    assert by_station["Right Upper Lobe Mass"]["short_axis_mm"] == 19.0
    assert by_station["Right Upper Lobe Mass"]["needle_gauge"] == 22
    assert by_station["Right Upper Lobe Mass"]["number_of_passes"] == 8
    assert by_station["Right Upper Lobe Mass"]["rose_result"] == "Malignant"


def test_extract_linear_ebus_stations_detail_numbered_station_list_items() -> None:
    note = (
        "EBUS Lymph Nodes Sampled:\n"
        "1. 11Rs: biopsied with a 22-gauge needle, 4 passes. ROSE: adequate lymphocytes.\n"
        "2) 7 (subcarinal): biopsied with 22G, 3 passes. ROSE showed malignant cells.\n"
        "3. 4R: not biopsied due to size criteria.\n"
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert by_station["11Rs"]["sampled"] is True
    assert by_station["11Rs"]["needle_gauge"] == 22
    assert by_station["11Rs"]["number_of_passes"] == 4
    assert by_station["11Rs"]["rose_result"] == "Adequate lymphocytes"

    assert by_station["7"]["sampled"] is True
    assert by_station["7"]["needle_gauge"] == 22
    assert by_station["7"]["number_of_passes"] == 3
    assert by_station["7"]["rose_result"] == "Malignant"

    assert by_station["4R"]["sampled"] is False
