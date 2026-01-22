"""Unit tests for Phase 7 deterministic CPT derivation rules.

Tests cover:
- Radial EBUS → 31654 (not 31620)
- Navigation → 31627
- Fiducial placement → 31626
- Dilation/Destruction bundling
- BAL and therapeutic aspiration extraction
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from modules.coder.domain_rules.registry_to_cpt.coding_rules import (
    derive_all_codes,
    derive_all_codes_with_meta,
)
from modules.registry.deterministic_extractors import (
    extract_bal,
    extract_cryotherapy,
    extract_linear_ebus,
    extract_navigational_bronchoscopy,
    extract_tbna_conventional,
    extract_brushings,
    extract_rigid_bronchoscopy,
    extract_transbronchial_cryobiopsy,
    extract_peripheral_ablation,
    extract_thermal_ablation,
    extract_radial_ebus,
    extract_therapeutic_aspiration,
)


def make_record(**kwargs) -> MagicMock:
    """Create a mock RegistryRecord with specified procedure flags."""
    record = MagicMock()
    record.granular_data = None
    record.fluoroscopy_used = None

    # Set up procedures_performed
    procedures_performed = MagicMock()

    # Default all procedures to None
    procedure_names = [
        "diagnostic_bronchoscopy",
        "bal",
        "brushings",
        "endobronchial_biopsy",
        "tbna_conventional",
        "peripheral_tbna",
        "linear_ebus",
        "radial_ebus",
        "navigational_bronchoscopy",
        "transbronchial_biopsy",
        "transbronchial_cryobiopsy",
        "therapeutic_aspiration",
        "foreign_body_removal",
        "airway_dilation",
        "airway_stent",
        "thermal_ablation",
        "cryotherapy",
        "blvr",
        "bronchial_thermoplasty",
        "whole_lung_lavage",
        "rigid_bronchoscopy",
        "fiducial_placement",
        "percutaneous_tracheostomy",
        "neck_ultrasound",
    ]

    for name in procedure_names:
        proc = MagicMock()
        if name in kwargs and kwargs[name] is True:
            proc.performed = True
        else:
            proc.performed = False
        setattr(procedures_performed, name, proc)

    # Ensure common list-like fields are real lists (avoids MagicMock iteration surprises).
    procedures_performed.linear_ebus.stations_sampled = []
    procedures_performed.linear_ebus.node_events = []
    procedures_performed.tbna_conventional.stations_sampled = []
    procedures_performed.peripheral_tbna.targets_sampled = []

    record.procedures_performed = procedures_performed
    record.established_tracheostomy_route = kwargs.get("established_tracheostomy_route", False)

    # Set up pleural_procedures
    pleural_procedures = MagicMock()
    pleural_names = ["ipc", "thoracentesis", "chest_tube", "medical_thoracoscopy", "pleurodesis", "fibrinolytic_therapy"]
    for name in pleural_names:
        proc = MagicMock()
        proc.performed = False
        setattr(pleural_procedures, name, proc)
    record.pleural_procedures = pleural_procedures

    # Handle linear_ebus stations_sampled
    if kwargs.get("linear_ebus"):
        stations = kwargs.get("stations_sampled", [])
        linear = procedures_performed.linear_ebus
        linear.stations_sampled = stations

    if kwargs.get("peripheral_tbna"):
        targets = kwargs.get("peripheral_tbna_targets_sampled", [])
        procedures_performed.peripheral_tbna.targets_sampled = targets

    return record


class TestRadialEBUS:
    """Tests for Radial EBUS → 31654."""

    def test_radial_ebus_derives_31654(self):
        """Radial EBUS should produce 31654, not 31620."""
        record = make_record(radial_ebus=True, linear_ebus=True, stations_sampled=["4R", "7"])
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31654" in codes, f"Expected 31654 in codes, got {codes}"
        assert "31620" not in codes, f"31620 should NOT be in codes"

    def test_radial_ebus_is_addon_code(self):
        """31654 is an add-on code requiring a primary bronchoscopy."""
        # Radial EBUS alone should not produce 31654 (requires primary)
        record = make_record(radial_ebus=True)
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        # 31654 should be excluded because no primary bronchoscopy
        assert "31654" not in codes, f"31654 requires primary bronchoscopy"

    def test_radial_ebus_with_therapeutic_aspiration_keeps_addon(self):
        record = make_record(radial_ebus=True, therapeutic_aspiration=True)
        codes, _rationales, _warnings = derive_all_codes_with_meta(record)
        assert "31645" in codes
        assert "31654" in codes


class TestNavigation:
    """Tests for Navigation → 31627."""

    def test_navigation_derives_31627(self):
        """Navigation bronchoscopy should produce 31627."""
        # Need a primary bronchoscopy too
        record = make_record(navigational_bronchoscopy=True, linear_ebus=True, stations_sampled=["7"])
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31627" in codes, f"Expected 31627 in codes, got {codes}"

    def test_navigation_alone_no_primary(self):
        """Navigation alone without primary should not produce 31627."""
        record = make_record(navigational_bronchoscopy=True)
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        # 31627 is an add-on, requires primary
        assert "31627" not in codes

    def test_navigation_with_therapeutic_aspiration_keeps_addon(self):
        record = make_record(navigational_bronchoscopy=True, therapeutic_aspiration=True)
        codes, _rationales, _warnings = derive_all_codes_with_meta(record)
        assert "31645" in codes
        assert "31627" in codes


class TestEndobronchialBiopsy:
    def test_endobronchial_biopsy_derives_31625(self):
        record = make_record(endobronchial_biopsy=True)
        codes, _rationales, _warnings = derive_all_codes_with_meta(record)
        assert "31625" in codes


class TestFiducialPlacement:
    """Tests for Fiducial placement → 31626."""

    def test_fiducial_from_procedure_field(self):
        """Fiducial placement from procedure field should produce 31626."""
        record = make_record(fiducial_placement=True, linear_ebus=True, stations_sampled=["7"])
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31626" in codes, f"Expected 31626 in codes, got {codes}"

    def test_fiducial_from_granular_data(self):
        """Fiducial placement from granular navigation target should produce 31626."""
        record = make_record(linear_ebus=True, stations_sampled=["7"])

        # Set up granular_data with fiducial marker
        granular = MagicMock()
        nav_target = MagicMock()
        nav_target.fiducial_marker_placed = True
        nav_target.fiducial_marker_details = None
        granular.navigation_targets = [nav_target]
        record.granular_data = granular

        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31626" in codes, f"Expected 31626 in codes, got {codes}"


class TestDilationBundling:
    """Tests for Dilation/Destruction bundling."""

    def test_dilation_bundled_with_destruction(self):
        """31630 should be bundled when 31641 (destruction) present (same lobe)."""
        record = make_record(airway_dilation=True, thermal_ablation=True)
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31641" in codes, f"Expected 31641 in codes"
        assert "31630" not in codes, f"31630 should be bundled into 31641"
        assert any("bundled" in w.lower() for w in warnings), f"Expected bundling warning"

    def test_dilation_not_bundled_distinct_lobes(self):
        """31630 should NOT be bundled when in distinct lobe from destruction."""
        record = make_record(airway_dilation=True, thermal_ablation=True)

        # Set up granular data with distinct lobes
        granular = MagicMock()

        dilation_target = MagicMock()
        dilation_target.lobe = "RUL"
        granular.dilation_targets = [dilation_target]

        ablation_target = MagicMock()
        ablation_target.lobe = "LLL"
        granular.ablation_targets = [ablation_target]

        record.granular_data = granular

        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31641" in codes
        assert "31630" in codes, f"31630 should NOT be bundled when in distinct lobe"


class TestBALExtractor:
    """Tests for BAL deterministic extractor."""

    def test_extract_bal_positive(self):
        """Should detect BAL from text."""
        text = "Bronchoalveolar lavage was performed in the right middle lobe."
        result = extract_bal(text)

        assert result == {"bal": {"performed": True}}

    def test_extract_bal_bronchial_alveolar_variant(self):
        text = "Bronchial alveolar lavage was performed at the lingula."
        result = extract_bal(text)
        assert result == {"bal": {"performed": True}}

    def test_extract_bal_abbreviation(self):
        """Should detect BAL abbreviation."""
        text = "BAL was obtained from the RML."
        result = extract_bal(text)

        assert result == {"bal": {"performed": True}}

    def test_extract_bal_negative(self):
        """Should not detect BAL when negated."""
        text = "We did not perform bronchoalveolar lavage."
        result = extract_bal(text)

        assert result == {}

    def test_extract_bal_score_not_matched(self):
        """Should not match 'BAL score' (different meaning)."""
        text = "The BAL score was elevated."
        result = extract_bal(text)

        assert result == {}


class TestTherapeuticAspirationExtractor:
    """Tests for therapeutic aspiration deterministic extractor."""

    def test_extract_therapeutic_aspiration_mucus(self):
        """Should detect therapeutic aspiration of mucus plug."""
        text = "Large mucus plug removal was performed in the left main bronchus."
        result = extract_therapeutic_aspiration(text)

        assert result.get("therapeutic_aspiration", {}).get("performed") is True
        assert result.get("therapeutic_aspiration", {}).get("material") == "Mucus plug"

    def test_extract_therapeutic_aspiration_clot(self):
        """Should detect therapeutic aspiration of blood clot."""
        text = "Blood clot aspiration was performed."
        result = extract_therapeutic_aspiration(text)

        assert result.get("therapeutic_aspiration", {}).get("performed") is True
        assert result.get("therapeutic_aspiration", {}).get("material") == "Blood clot"

    def test_extract_routine_suction_not_therapeutic(self):
        """Should not detect routine suction as therapeutic aspiration."""
        text = "Routine suction was performed. Minimal secretions noted."
        result = extract_therapeutic_aspiration(text)

        assert result == {}

    def test_extract_scant_secretions_not_therapeutic(self):
        """Should not detect scant secretions as therapeutic aspiration."""
        text = "Scant secretions were suctioned."
        result = extract_therapeutic_aspiration(text)

        assert result == {}


class TestRadialEBUSExtractor:
    def test_extract_radial_ebus_phrase(self):
        text = "Radial EBUS was utilized to identify vasculature and airways."
        result = extract_radial_ebus(text)
        assert result == {"radial_ebus": {"performed": True}}


class TestCryotherapyExtractor:
    def test_extract_cryotherapy_phrase(self):
        text = "Cryotherapy was applied for further debulking."
        result = extract_cryotherapy(text)
        assert result == {"cryotherapy": {"performed": True}}

    def test_extract_cryotherapy_cryo_probe(self):
        text = "Cryo probe was used for tumor debulking."
        result = extract_cryotherapy(text)
        assert result == {"cryotherapy": {"performed": True}}


class TestRigidBronchoscopyExtractor:
    def test_extract_rigid_bronchoscopy_phrase(self):
        text = "Rigid bronchoscopy was performed for central airway obstruction."
        result = extract_rigid_bronchoscopy(text)
        assert result == {"rigid_bronchoscopy": {"performed": True}}


class TestLinearEBUSExtractor:
    def test_extract_linear_ebus_with_stations(self):
        text = "Stations sampled: 4R, 7, 11L. Linear EBUS bronchoscopy performed."
        result = extract_linear_ebus(text)
        assert result.get("linear_ebus", {}).get("performed") is True
        assert set(result.get("linear_ebus", {}).get("stations_sampled") or []) == {"4R", "7", "11L"}

    def test_extract_linear_ebus_not_from_radial_ebus(self):
        text = "Radial EBUS performed to confirm lesion location. rEBUS view: Concentric."
        result = extract_linear_ebus(text)
        assert result == {}

    def test_extract_linear_ebus_excludes_negated_station(self):
        text = (
            "PROCEDURE IN DETAIL:\n"
            "Linear EBUS bronchoscopy performed.\n"
            "4L node - decision to not perform transbronchial sampling of this lymph node.\n"
            "11Ri lymph node - TBNA was performed.\n"
            "Station 7 lymph node - TBNA was performed.\n"
        )
        result = extract_linear_ebus(text)
        assert result.get("linear_ebus", {}).get("performed") is True
        stations = {str(s).strip().upper() for s in (result.get("linear_ebus", {}).get("stations_sampled") or [])}
        assert stations == {"11RI", "7"}

class TestNavigationExtractor:
    def test_extract_navigation_platform(self):
        text = "Ion robotic bronchoscopy was performed for a peripheral lesion."
        result = extract_navigational_bronchoscopy(text)
        assert result == {"navigational_bronchoscopy": {"performed": True}}


class TestTBNAExtractor:
    def test_extract_tbna(self):
        text = "TBNA was performed with 22G needle."
        result = extract_tbna_conventional(text)
        assert result.get("peripheral_tbna", {}).get("performed") is True

    def test_extract_tbna_skips_ebus_context(self):
        text = (
            "Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration "
            "was performed using 25-gauge needle."
        )
        result = extract_tbna_conventional(text)
        assert result == {}

    def test_extract_tbna_does_not_steal_ebus_stations(self):
        text = (
            "PROCEDURE IN DETAIL:\n"
            "Transbronchial needle aspiration was performed with 21G needle.\n"
            "\n"
            "The endobronchial ultrasound-capable (EBUS) bronchoscope was introduced.\n"
            "4L node - decision to not perform transbronchial sampling of this lymph node.\n"
            "11Ri node - TBNA was performed.\n"
            "7 node - TBNA was performed.\n"
        )
        result = extract_tbna_conventional(text)
        assert result.get("peripheral_tbna", {}).get("performed") is True
        assert "tbna_conventional" not in result


class TestBrushingsExtractor:
    def test_extract_brushings(self):
        text = "Brushings x2 were obtained for cytology."
        result = extract_brushings(text)
        assert result == {"brushings": {"performed": True}}

    def test_extract_brushings_with_location(self):
        text = "Endobronchial brushing was performed at the takeoff of the right upper lobe."
        result = extract_brushings(text)
        assert result.get("brushings", {}).get("performed") is True
        assert result.get("brushings", {}).get("locations") == ["RUL"]


class TestCryobiopsyExtractor:
    def test_extract_transbronchial_cryobiopsy(self):
        text = "Transbronchial cryobiopsy performed using a 1.9mm probe."
        result = extract_transbronchial_cryobiopsy(text)
        assert result == {"transbronchial_cryobiopsy": {"performed": True}}


class TestPeripheralAblationExtractor:
    def test_extract_peripheral_ablation_mwa(self):
        text = "Microwave ablation performed for a peripheral lung nodule."
        result = extract_peripheral_ablation(text)
        assert result.get("peripheral_ablation", {}).get("performed") is True
        assert result.get("peripheral_ablation", {}).get("modality") == "Microwave"


class TestThermalAblationExtractor:
    def test_extract_thermal_ablation_apc(self):
        text = "APC was applied to control bleeding."
        result = extract_thermal_ablation(text)
        assert result.get("thermal_ablation", {}).get("performed") is True
        assert result.get("thermal_ablation", {}).get("modality") == "APC"


class TestEBUSStationCounts:
    """Tests for EBUS station count → 31652/31653."""

    def test_ebus_three_plus_stations_produces_31653(self):
        """EBUS with 3+ stations should produce 31653."""
        record = make_record(linear_ebus=True, stations_sampled=["4R", "7", "11L"])
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31653" in codes
        assert "31652" not in codes

    def test_ebus_two_stations_produces_31652(self):
        """EBUS with 1-2 stations should produce 31652."""
        record = make_record(linear_ebus=True, stations_sampled=["4R", "7"])
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31652" in codes
        assert "31653" not in codes

    def test_ebus_no_stations_warning(self):
        """EBUS with no stations should produce warning."""
        record = make_record(linear_ebus=True, stations_sampled=[])
        codes, rationales, warnings = derive_all_codes_with_meta(record)

        assert "31652" not in codes
        assert "31653" not in codes
        assert any("stations_sampled missing" in w for w in warnings)

class TestTBNABundling:
    def test_tbna_conventional_bundled_into_ebus(self):
        record = make_record(linear_ebus=True, stations_sampled=["4R", "7", "11L"], tbna_conventional=True)
        codes, _rationales, warnings = derive_all_codes_with_meta(record)
        assert "31653" in codes
        assert "31629" not in codes
        assert any("Suppressed 31629" in w for w in warnings)

    def test_peripheral_tbna_kept_with_modifier_when_ebus(self):
        record = make_record(
            linear_ebus=True,
            stations_sampled=["4R", "7", "11L"],
            peripheral_tbna=True,
            peripheral_tbna_targets_sampled=["LUL nodule", "RML nodule"],
        )
        codes, _rationales, warnings = derive_all_codes_with_meta(record)
        assert "31653" in codes
        assert "31629" in codes
        assert "31633" in codes
        assert any("Modifier 59" in w for w in warnings)


class TestTracheostomyCPTLogic:
    def test_established_tracheostomy_route_derives_31615(self):
        record = make_record(established_tracheostomy_route=True)
        codes, rationales, warnings = derive_all_codes_with_meta(record)
        assert "31615" in codes

    def test_percutaneous_tracheostomy_without_established_route_derives_31600(self):
        record = make_record(percutaneous_tracheostomy=True, established_tracheostomy_route=False)
        codes, rationales, warnings = derive_all_codes_with_meta(record)
        assert "31600" in codes
        assert "31615" not in codes

    def test_established_route_suppresses_31600_even_if_percutaneous_tracheostomy_true(self):
        record = make_record(percutaneous_tracheostomy=True, established_tracheostomy_route=True)
        codes, rationales, warnings = derive_all_codes_with_meta(record)
        assert "31615" in codes
        assert "31600" not in codes


class TestNeckUltrasoundCPTLogic:
    def test_neck_ultrasound_derives_76536(self):
        record = make_record(neck_ultrasound=True)
        codes, rationales, warnings = derive_all_codes_with_meta(record)
        assert "76536" in codes
