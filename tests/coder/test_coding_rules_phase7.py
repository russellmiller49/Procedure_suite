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
    ]

    for name in procedure_names:
        proc = MagicMock()
        if name in kwargs and kwargs[name] is True:
            proc.performed = True
        else:
            proc.performed = False
        setattr(procedures_performed, name, proc)

    record.procedures_performed = procedures_performed

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
