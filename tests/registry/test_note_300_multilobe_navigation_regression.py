from __future__ import annotations

from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from app.registry.processing.navigation_targets import extract_cryobiopsy_sites, extract_navigation_targets
from app.registry.schema import RegistryRecord
from app.registry.schema_granular import derive_procedures_from_granular


def test_note300_multilobe_navigation_targets_drive_addon_codes_and_imaging() -> None:
    note_text = """
    CT Chest scan was placed on separate planning station to generate 3D rendering of the pathway to target.

    RIGHT LOWER LOBE TARGET
    Robotic navigation bronchoscopy was performed with Ion platform.
    Ion robotic catheter was used to engage the Superior Segment of RLL (RB6). Target lesion is about 1 cm in diameter.
    Radial EBUS was performed to confirm that the location of the nodule is Concentric.
    Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation.
    Transbronchial needle aspiration was performed. Total 8 samples were collected.
    Transbronchial cryobiopsy was performed with 1.1mm cryoprobe. Freeze time of 6 seconds were used. Total 5 samples were collected.
    Fiducial marker (0.8mm x 3mm) was loaded and placed under fluoroscopy guidance.

    RIGHT UPPER LOBE TARGET
    Robotic navigation bronchoscopy was performed with Ion platform.
    Ion robotic catheter was used to engage the Anterior Segment of RUL (RB3). Target lesion is about 1 cm in diameter.
    Radial EBUS was performed to confirm that the location of the nodule is Concentric.
    Cone Beam CT was performed: 3-D reconstructions were performed on an independent workstation.
    Transbronchial needle aspiration was performed. Total 6 samples were collected.
    Transbronchial cryobiopsy was performed with 1.1mm cryoprobe. Freeze time of 6 seconds were used. Total 5 samples were collected.
    Fiducial marker (0.8mm x 3mm) was loaded and placed under fluoroscopy guidance.
    """

    targets = extract_navigation_targets(note_text)
    assert len(targets) == 2
    assert targets[0]["target_location_text"] == "Superior Segment of RLL (RB6)"
    assert targets[0]["target_lobe"] == "RLL"
    assert targets[0]["fiducial_marker_placed"] is True
    assert targets[1]["target_location_text"] == "Anterior Segment of RUL (RB3)"
    assert targets[1]["target_lobe"] == "RUL"
    assert targets[1]["fiducial_marker_placed"] is True

    cryo_sites = extract_cryobiopsy_sites(note_text)
    assert len(cryo_sites) == 2
    assert {s["lobe"] for s in cryo_sites} == {"RLL", "RUL"}

    granular = {"navigation_targets": targets, "cryobiopsy_sites": cryo_sites}
    procedures, _warnings = derive_procedures_from_granular(granular, existing_procedures={})

    record = RegistryRecord(
        equipment={
            "navigation_platform": "Ion",
            "cbct_used": True,
            "augmented_fluoroscopy": True,
        },
        procedures_performed=procedures,
        granular_data=granular,
    )

    codes, _rationales, _warnings = derive_all_codes_with_meta(record)
    # Multi-lobe add-ons
    assert "31632" in codes
    assert "31633" in codes
    # Imaging adjuncts
    assert "77012" in codes
    assert "76377" in codes


def test_navigation_targets_support_mass_and_nodule_headers_with_fiducial_outcome_qualifier() -> None:
    note_text = """
    Left upper lobe LB1/LB2 mass:
    Robotic navigation bronchoscopy was performed with Intuitive Ion platform.
    The Ion robotic catheter was used to engage the Apical-Posterior Segment of LUL (LB1/2).
    Target lesion is about 7.4 cm in diameter.
    Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.

    Right middle lobe RB4 nodule:
    Robotic navigation bronchoscopy was performed with Intuitive Ion platform.
    The Ion robotic catheter was used to engage the Lateral Segment of RML (RB4).
    Target lesion is about 2.3 cm in diameter.
    Fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance. However, this fiducial marker appeared to fall out and did not enter the nodule.
    """

    targets = extract_navigation_targets(note_text)
    assert len(targets) == 2
    assert targets[0]["target_lobe"] == "LUL"
    assert targets[0]["lesion_size_mm"] == 74.0
    assert targets[0]["fiducial_marker_placed"] is True
    assert targets[1]["target_lobe"] == "RML"
    assert targets[1]["lesion_size_mm"] == 23.0
    assert targets[1]["fiducial_marker_placed"] is True
