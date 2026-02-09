from __future__ import annotations

from app.reporting.macro_engine import CATEGORY_MACROS, get_category_macros
from app.reporting.macro_registry import get_macro_registry


def test_category_macros_loaded_from_schema_and_exposed() -> None:
    expected = {
        "minor_trach_laryngoscopy": [
            "minor_trach_bleeding",
            "chemical_cauterization",
            "trach_tube_change",
            "percutaneous_trach",
            "trach_revision",
            "tracheobronchoscopy_via_trach",
            "trach_decannulation",
            "trach_downsize",
            "granulation_debridement",
            "flexible_laryngoscopy",
        ],
        "core_bronchoscopy": [
            "bronchial_washing",
            "bronchial_brushings",
            "bronchoalveolar_lavage",
            "endobronchial_biopsy",
            "transbronchial_lung_biopsy",
            "transbronchial_needle_aspiration",
            "balloon_dilation",
            "airway_stent_placement",
            "endobronchial_tumor_destruction",
            "tumor_destruction_multimodal",
            "therapeutic_aspiration",
            "endobronchial_tumor_excision",
            "rigid_bronchoscopy",
            "foreign_body_removal",
            "endobronchial_hemostasis",
            "endobronchial_blocker",
            "awake_foi",
            "dlt_confirmation",
            "stent_surveillance",
        ],
        "navigation_robotic_ebus": [
            "emn_bronchoscopy",
            "fiducial_marker_placement",
            "radial_ebus_survey",
            "robotic_bronchoscopy_ion",
            "ion_registration_complete",
            "ion_registration_partial",
            "ion_registration_drift",
            "linear_ebus_tbna",
            "rebus_guide_sheath_sampling",
            "cbct_assisted_bronchoscopy",
            "transbronchial_dye_marking",
            "robotic_bronchoscopy_monarch",
            "ebus_intranodal_forceps_biopsy",
            "ebus_19g_fnb",
        ],
        "blvr_cryo": [
            "endobronchial_valve_placement",
            "endobronchial_valve_removal_exchange",
            "post_blvr_protocol",
            "transbronchial_cryobiopsy",
            "endobronchial_cryoablation",
            "cryoablation_alternative",
        ],
        "pleural": [
            "chest_tube_placement",
            "thoracentesis",
            "thoracentesis_manometry",
            "tpc_placement",
            "tpc_removal",
            "intrapleural_fibrinolysis",
            "medical_thoracoscopy",
            "pigtail_catheter_placement",
            "transthoracic_needle_biopsy",
            "thoravent_placement",
            "chemical_pleurodesis_chest_tube",
            "chemical_pleurodesis_ipc",
            "ipc_exchange",
            "chest_tube_exchange",
            "chest_tube_removal",
            "us_guided_pleural_biopsy",
            "focused_thoracic_ultrasound",
        ],
        "other_interventions": [
            "whole_lung_lavage",
            "eus_b",
            "paracentesis",
            "peg_placement",
            "peg_removal_exchange",
            "bpf_localization",
            "ebv_for_air_leak",
            "bpf_sealant_application",
        ],
        "clinical_assessment": [
            "pre_anesthesia_assessment",
            "general_bronchoscopy_note",
            "ip_operative_report",
            "tpc_discharge_instructions",
            "blvr_discharge_instructions",
            "chest_tube_discharge_instructions",
            "peg_discharge_instructions",
        ],
    }

    registry = get_macro_registry()
    assert registry.category_macros == expected
    assert CATEGORY_MACROS == expected
    for category, macros in expected.items():
        assert get_category_macros(category, registry=registry) == macros
