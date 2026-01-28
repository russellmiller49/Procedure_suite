from __future__ import annotations

from modules.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta
from modules.registry.processing.navigation_targets import extract_cryobiopsy_sites, extract_navigation_targets
from modules.registry.schema import RegistryRecord
from modules.registry.schema_granular import derive_procedures_from_granular


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

