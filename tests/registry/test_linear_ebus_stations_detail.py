from __future__ import annotations

from app.registry.processing.linear_ebus_stations_detail import extract_linear_ebus_stations_detail


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
    assert by_station["11Rs"]["lymphocytes_present"] is True

    assert by_station["7"]["sampled"] is True
    assert by_station["7"]["needle_gauge"] == 22
    assert by_station["7"]["number_of_passes"] == 3
    assert by_station["7"]["rose_result"] == "Malignant"
    assert by_station["7"].get("lymphocytes_present") is None

    assert by_station["4R"]["sampled"] is False
    assert by_station["4R"].get("lymphocytes_present") is None


def test_extract_linear_ebus_stations_detail_lymphocytes_present_negative_from_rose() -> None:
    note = (
        "EBUS Lymph Nodes Sampled:\n"
        "Station 7: biopsied with 22G, 4 passes. ROSE: scant lymphocytes, blood only.\n"
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert by_station["7"]["sampled"] is True
    assert by_station["7"]["lymphocytes_present"] is False


def test_extract_linear_ebus_stations_detail_prefers_ebus_scoped_gauge_over_peripheral_tbna() -> None:
    note = (
        "Robotic navigation bronchoscopy was performed with Ion platform.\n"
        "Transbronchial needle aspiration was performed with 21G Needle through the catheter. Total 4 samples were collected.\n"
        "\n"
        "EBUS-Findings\n"
        "Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 22-gauge Needle.\n"
        "\n"
        "Station 4L: biopsied with 5 passes.\n"
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert by_station["4L"]["sampled"] is True
    assert by_station["4L"]["needle_gauge"] == 22
    assert by_station["4L"]["number_of_passes"] == 5


def test_extract_linear_ebus_stations_detail_inline_paren_format_avoids_count_false_positives() -> None:
    note = (
        "Ion robotic bronchoscopy and staging EBUS. "
        "5 peripheral needle biopsies were obtained. "
        "Biopsy of 4L (7.6mm) 5 passes 22G needle ROSE adequate, "
        "7 (6.2 mm) 5 passes 22G needle ROSE adequate, "
        "4R (8.2mm) 5 passes 22G needle ROSE malignant."
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert by_station["4L"]["sampled"] is True
    assert by_station["4L"]["short_axis_mm"] == 7.6
    assert by_station["4L"]["number_of_passes"] == 5
    assert by_station["4L"]["rose_result"] == "Adequate lymphocytes"

    assert by_station["7"]["sampled"] is True
    assert by_station["7"]["short_axis_mm"] == 6.2
    assert by_station["7"]["number_of_passes"] == 5
    assert by_station["7"]["rose_result"] == "Adequate lymphocytes"

    assert by_station["4R"]["sampled"] is True
    assert by_station["4R"]["short_axis_mm"] == 8.2
    assert by_station["4R"]["number_of_passes"] == 5
    assert by_station["4R"]["rose_result"] == "Malignant"

    # Ensure numeric counts (e.g., "5 peripheral needle biopsies") do not become station "5".
    assert "5" not in by_station


def test_extract_linear_ebus_stations_detail_rose_negative_for_malignancy_not_marked_malignant() -> None:
    note = (
        "EBUS staging performed.\n"
        "Station 7: biopsied with 22G, 4 passes. ROSE adequate lymphocytes, negative for malignancy.\n"
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert by_station["7"]["sampled"] is True
    assert by_station["7"]["rose_result"] == "Adequate lymphocytes"
    assert by_station["7"].get("morphologic_impression") != "malignant"


def test_extract_linear_ebus_stations_detail_rose_malignant_cells_marked_malignant() -> None:
    note = (
        "EBUS staging performed.\n"
        "Station 4R: biopsied with 22G, 3 passes. ROSE adequate with malignant cells.\n"
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert by_station["4R"]["sampled"] is True
    assert by_station["4R"]["rose_result"] == "Malignant"


def test_extract_linear_ebus_stations_detail_site_header_number_does_not_become_station() -> None:
    note = (
        "EBUS-Findings\n"
        "Lymph Nodes Evaluated:\n"
        "Site 5: The 11Ri lymph node was < 10 mm on CT. "
        "The site was not sampled: Sampling this lymph node was not clinically indicated. "
        "Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics. "
        "The target lymph node demonstrated a Type 2 elastographic pattern with mixed soft and stiff regions.\n"
    )

    details = extract_linear_ebus_stations_detail(note)
    by_station = _by_station(details)

    assert "5" not in by_station
    assert by_station["11Ri"]["sampled"] is False
    assert by_station["11Ri"]["elastography_performed"] is True
    assert by_station["11Ri"]["elastography_pattern"] == "blue_green"
