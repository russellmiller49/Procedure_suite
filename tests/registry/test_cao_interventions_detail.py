from __future__ import annotations

from modules.registry.processing.cao_interventions_detail import extract_cao_interventions_detail


def _by_location(items: list[dict]) -> dict[str, dict]:
    return {str(item.get("location")): item for item in items if isinstance(item, dict) and item.get("location")}


def test_extract_cao_interventions_detail_multisite_with_end_of_procedure_post_values() -> None:
    note = (
        "POSTOPERATIVE DIAGNOSIS: Malignant airway obstruction\n"
        "PREOPERATIVE DIAGNOSIS: Malignant lung mass with left main-stem obstruction\n"
        "DESCRIPTION OF PROCEDURE: In the distal left mainstem a white fungating tumor was seen causing "
        "complete obstruction of the left lower lobe and causing complete obstruction of the lingula and "
        "80% obstruction of the left mainstem.\n"
        "At the end of the procedure distal left mainstem was only 15% obstructed.\n"
        "The lingula was 80% obstructed and the left lower lobe remained completely obstructed with distal tumor.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)

    assert by_loc["LMS"]["pre_obstruction_pct"] == 80
    assert by_loc["LMS"]["post_obstruction_pct"] == 15

    assert by_loc["Lingula"]["pre_obstruction_pct"] == 100
    assert by_loc["Lingula"]["post_obstruction_pct"] == 80

    assert by_loc["LLL"]["pre_obstruction_pct"] == 100
    assert by_loc["LLL"]["post_obstruction_pct"] == 100


def test_extract_cao_interventions_detail_dynamic_tracheal_obstruction_and_stent_considered() -> None:
    note = (
        "INDICATIONS: Tracheal Obstruction\n"
        "Approximately 2.5 cm distal to the vocal cords there were lesions blocking about 90% of the airway "
        "during exhalation resulting in about 50% obstruction of the airway.\n"
        "At the end of the procedure the trachea was approximately 90% open in comparison to unaffected areas.\n"
        "Of note we considered airway stent placement; the patient was reluctant to have stent placed.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)

    assert by_loc["Trachea"]["pre_obstruction_pct"] == 90
    assert by_loc["Trachea"]["post_obstruction_pct"] == 10
    assert by_loc["Trachea"]["stent_placed_at_site"] is False


def test_extract_cao_interventions_detail_tracheal_lesion_count_and_morphology() -> None:
    note = (
        "DESCRIPTION OF PROCEDURE: Approximately 2.5 cm distal to the vocal cords there were 3 polypoid lesions "
        "blocking about 90% of the airway.\n"
        "Additionally there were multiple small polypoid (> 50) lesions surrounding distal to the lesion.\n"
        "We then used APC to paint and shave the remaining tumor area on the posterior and lateral trachea walls.\n"
        "At the end of the procedure the trachea was approximately 90% open.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)
    trachea = by_loc["Trachea"]
    assert trachea["lesion_morphology"] == "Polypoid"
    assert "3" in str(trachea.get("lesion_count_text") or "")
    assert ">50" in str(trachea.get("lesion_count_text") or "")


def test_extract_cao_interventions_detail_patency_is_converted_to_obstruction_pct() -> None:
    note = (
        "TRACHEAL STENOSIS\n"
        "Endobronchial obstruction at Trachea (Proximal 1/3) was treated.\n"
        "Prior to treatment, affected airway was note to be 20% patent.\n"
        "After treatment, the airway was 40% patent.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)
    assert by_loc["Trachea"]["pre_obstruction_pct"] == 80
    assert by_loc["Trachea"]["post_obstruction_pct"] == 60


def test_extract_cao_interventions_detail_patency_to_phrase_is_converted_to_obstruction_pct() -> None:
    note = (
        "TRACHEAL STENOSIS\n"
        "Prior to treatment, affected airway was patent to 20%.\n"
        "After treatment, the airway was open to 60%.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)
    assert by_loc["Trachea"]["pre_obstruction_pct"] == 80
    assert by_loc["Trachea"]["post_obstruction_pct"] == 40


def test_extract_cao_interventions_detail_initial_inspection_vs_post_dilation_context() -> None:
    note = (
        "Initial Inspection:\n"
        "Trachea stenosis is 80%.\n"
        "Post-Dilation:\n"
        "Trachea patent to 70%.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)
    assert by_loc["Trachea"]["pre_obstruction_pct"] == 80
    assert by_loc["Trachea"]["post_obstruction_pct"] == 30


def test_extract_cao_interventions_detail_extrinsic_compression_sets_obstruction_type() -> None:
    note = (
        "The right mainstem at the orifice was significantly externally compressed (85%).\n"
        "At the end of the procedure the right mainstem was only 10% obstructed.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)
    assert by_loc["RMS"]["pre_obstruction_pct"] == 85
    assert by_loc["RMS"]["post_obstruction_pct"] == 10
    assert by_loc["RMS"]["obstruction_type"] == "Extrinsic"


def test_extract_cao_interventions_detail_myer_cotton_classification_is_attached() -> None:
    note = (
        "Myer-Cotton Grade III\n"
        "Trachea stenosis is 80%.\n"
    )

    details = extract_cao_interventions_detail(note)
    by_loc = _by_location(details)
    assert by_loc["Trachea"]["pre_obstruction_pct"] == 80
    assert "myer" in str(by_loc["Trachea"].get("classification") or "").lower()
