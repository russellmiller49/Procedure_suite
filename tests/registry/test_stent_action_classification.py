from __future__ import annotations

from app.registry.deterministic_extractors import (
    classify_stent_action,
    extract_airway_stent,
    run_deterministic_extractors,
)
from app.registry.schema import RegistryRecord
from app.coder.domain_rules.registry_to_cpt.coding_rules import derive_all_codes_with_meta


def test_scope_removal_before_stent_advancement_is_not_stent_removal() -> None:
    # Classic placement workflow: the bronchoscope is removed, then the stent
    # loading device is advanced. Must classify as first-time placement.
    text = (
        "The flexible bronchoscope was removed and an Aero 30mm x 10mm fully covered "
        "self-expandable metallic stent loading device was advanced over the guidewire and "
        "the stent was positioned with the proximal end just distal to the RUL. The stent "
        "was deployed without difficulty and after minor adjustment the stent was observed "
        "to be well-seated in the bronchus intermedius."
    )
    classified = classify_stent_action(text)
    assert classified["action_type"] == "placement"
    assert classified["removal"] is False
    assert classified["preexisting_stent"] is False

    seed = run_deterministic_extractors(text)
    record = RegistryRecord(**seed)
    codes, _r, _w = derive_all_codes_with_meta(record)
    assert "31636" in codes
    assert "31638" not in codes


def test_bullet_style_ystent_deployment_detected_as_placement() -> None:
    text = (
        "Airway stenting:\n"
        "\n"
        "Silicone Y-stent (Novatec 14-10-10 mm) selected and customized (6 cm tracheal limb; "
        "1 cm each mainstem limb).\n"
        "\n"
        "Deployed under direct vision across trachea, carina, and both mainstem bronchi.\n"
        "\n"
        "Post-stent lumen ~90% of normal; final position satisfactory.\n"
    )
    classified = classify_stent_action(text)
    assert classified["action_type"] == "placement"
    assert classified["stent_type"] == "Y-Stent"

    stent = extract_airway_stent(text).get("airway_stent") or {}
    assert stent.get("performed") is True
    assert stent.get("action") == "Placement"

    seed = run_deterministic_extractors(text)
    record = RegistryRecord(**seed)
    codes, _r, _w = derive_all_codes_with_meta(record)
    # Y-stent spans the trachea/carina: tracheal placement family.
    assert "31631" in codes


def test_true_stent_removal_still_detected() -> None:
    text = "The migrated silicone stent was grasped with forceps and removed intact."
    classified = classify_stent_action(text)
    assert classified["removal"] is True


def test_migrated_stent_removal_plus_new_stent_remains_revision() -> None:
    # Same-session remove + replace of a stent at the same site codes as revision
    # (31638) per current policy.
    text = (
        "The migrated tracheal stent was removed with rigid forceps. After balloon dilation "
        "a new 12 x 40 Bonastent was deployed in the trachea in good position."
    )
    classified = classify_stent_action(text)
    assert classified["action_type"] == "revision"


def test_inspection_only_stent_remains_assessment() -> None:
    text = "The previously placed left mainstem stent was widely patent and in good position."
    classified = classify_stent_action(text)
    assert classified["action_type"] == "assessment_only"
    assert extract_airway_stent(text) == {}
