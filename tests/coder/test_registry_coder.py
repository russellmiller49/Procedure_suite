"""Tests for RegistryBasedCoder - deterministic CPT derivation from clinical actions.

These tests validate the extraction-first architecture by ensuring
CPT codes are correctly derived from ClinicalActions and bundling
rules are properly applied.
"""

import pytest

from app.registry.ml.models import (
    ClinicalActions,
    EBUSActions,
    BiopsyActions,
    NavigationActions,
    BALActions,
    BrushingsActions,
    PleuralActions,
    CAOActions,
    StentActions,
    BLVRActions,
)
from app.coder.adapters.registry_coder import (
    RegistryBasedCoder,
    DerivedCode,
    DerivationResult,
    derive_codes_from_actions,
)


@pytest.fixture
def coder():
    """Create RegistryBasedCoder instance for testing."""
    return RegistryBasedCoder()


@pytest.fixture
def coder_no_bundling():
    """Create RegistryBasedCoder without bundling for isolated testing."""
    return RegistryBasedCoder(apply_bundling=False)


class TestEBUSCodeDerivation:
    """Test EBUS CPT code derivation based on station count."""

    def test_ebus_three_plus_stations_derives_31653(self, coder):
        """Test: 3+ stations → 31653."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7", "11L"]),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31653" in codes
        assert "31652" not in codes

    def test_ebus_two_stations_derives_31652(self, coder):
        """Test: 1-2 stations → 31652."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7"]),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31652" in codes
        assert "31653" not in codes

    def test_ebus_one_station_derives_31652(self, coder):
        """Test: 1 station → 31652."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["7"]),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31652" in codes

    def test_ebus_no_stations_documented_defaults_31652(self, coder):
        """Test: EBUS performed but no stations → 31652 with lower confidence."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=[]),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31652" in codes

        # Should have lower confidence
        ebus_code = next(c for c in result.codes if c.code == "31652")
        assert ebus_code.confidence < 1.0

    def test_ebus_not_performed_no_ebus_codes(self, coder):
        """Test: EBUS not performed → no EBUS codes."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=False),
            bal=BALActions(performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31652" not in codes
        assert "31653" not in codes

    def test_ebus_rationale_includes_stations(self, coder):
        """Test: Rationale includes station names."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7", "11L"]),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        ebus_code = next(c for c in result.codes if c.code == "31653")
        assert "4R" in ebus_code.rationale
        assert "7" in ebus_code.rationale
        assert "11L" in ebus_code.rationale


class TestBiopsyCodeDerivation:
    """Test biopsy CPT code derivation."""

    def test_transbronchial_biopsy_derives_31628(self, coder):
        """Test: Transbronchial biopsy → 31628."""
        actions = ClinicalActions(
            biopsy=BiopsyActions(
                transbronchial_performed=True,
                transbronchial_sites=["RUL"],
            ),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31628" in codes

    def test_multiple_lobes_adds_31632(self, coder_no_bundling):
        """Test: Multiple lobe biopsies → 31628 + 31632 add-ons."""
        actions = ClinicalActions(
            biopsy=BiopsyActions(
                transbronchial_performed=True,
                transbronchial_sites=["RUL", "LLL", "RML"],
            ),
            diagnostic_bronchoscopy=True,
        )
        result = coder_no_bundling.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31628" in codes
        assert codes.count("+31632") == 2  # Two additional lobes

    def test_endobronchial_biopsy_derives_31625(self, coder):
        """Test: Endobronchial biopsy → 31625."""
        actions = ClinicalActions(
            biopsy=BiopsyActions(endobronchial_performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31625" in codes

    def test_cryobiopsy_derives_31628(self, coder):
        """Test: Cryobiopsy → 31628 (same as transbronchial)."""
        actions = ClinicalActions(
            biopsy=BiopsyActions(
                cryobiopsy_performed=True,
                cryobiopsy_sites=["RLL"],
            ),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31628" in codes


class TestSamplingCodeDerivation:
    """Test BAL and brushings code derivation."""

    def test_bal_derives_31624(self, coder):
        """Test: BAL → 31624."""
        actions = ClinicalActions(
            bal=BALActions(performed=True, sites=["RML"]),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31624" in codes

    def test_brushings_derives_31623(self, coder):
        """Test: Brushings → 31623."""
        actions = ClinicalActions(
            brushings=BrushingsActions(performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31623" in codes


class TestNavigationCodeDerivation:
    """Test navigation add-on code derivation."""

    def test_navigation_with_ebus_derives_31627(self, coder):
        """Test: Navigation + EBUS → 31627 add-on."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7", "11L"]),
            navigation=NavigationActions(performed=True, platform="superDimension"),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31653" in codes  # Primary
        assert "31627" in codes  # Add-on

    def test_navigation_with_biopsy_derives_31627(self, coder):
        """Test: Navigation + biopsy → 31627 add-on."""
        actions = ClinicalActions(
            biopsy=BiopsyActions(
                transbronchial_performed=True,
                transbronchial_sites=["RUL"],
            ),
            navigation=NavigationActions(performed=True, platform="Ion"),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31628" in codes  # Primary
        assert "31627" in codes  # Add-on

    def test_navigation_without_primary_no_31627(self, coder):
        """Test: Navigation without primary procedure → no 31627."""
        actions = ClinicalActions(
            navigation=NavigationActions(performed=True, platform="Monarch"),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        # Should only have diagnostic bronchoscopy, not navigation add-on
        assert "31627" not in codes

    def test_navigation_rationale_includes_platform(self, coder):
        """Test: Rationale includes navigation platform."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7", "11L"]),
            navigation=NavigationActions(performed=True, platform="superDimension"),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        nav_code = next(c for c in result.codes if c.code == "31627")
        assert "superDimension" in nav_code.rationale


class TestPleuralCodeDerivation:
    """Test pleural procedure code derivation."""

    def test_thoracentesis_derives_32555(self, coder):
        """Test: Thoracentesis → 32555 (with imaging assumed)."""
        actions = ClinicalActions(
            pleural=PleuralActions(thoracentesis_performed=True),
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "32555" in codes

    def test_ipc_derives_32550(self, coder):
        """Test: IPC insertion → 32550."""
        actions = ClinicalActions(
            pleural=PleuralActions(ipc_performed=True, ipc_action="insertion"),
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "32550" in codes

    def test_chest_tube_derives_32556(self, coder):
        """Test: Chest tube → 32556."""
        actions = ClinicalActions(
            pleural=PleuralActions(chest_tube_performed=True),
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "32556" in codes

    def test_thoracoscopy_with_pleurodesis_derives_32650(self, coder):
        """Test: Thoracoscopy + pleurodesis → 32650."""
        actions = ClinicalActions(
            pleural=PleuralActions(
                thoracoscopy_performed=True,
                pleurodesis_performed=True,
            ),
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "32650" in codes

    def test_diagnostic_thoracoscopy_derives_32601(self, coder):
        """Test: Diagnostic thoracoscopy → 32601."""
        actions = ClinicalActions(
            pleural=PleuralActions(thoracoscopy_performed=True),
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "32601" in codes


class TestCAOCodeDerivation:
    """Test CAO (central airway obstruction) code derivation."""

    def test_thermal_ablation_derives_31641(self, coder):
        """Test: Thermal ablation → 31641."""
        actions = ClinicalActions(
            cao=CAOActions(performed=True, thermal_ablation_performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31641" in codes

    def test_cryotherapy_derives_31641(self, coder):
        """Test: Cryotherapy → 31641."""
        actions = ClinicalActions(
            cao=CAOActions(performed=True, cryotherapy_performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31641" in codes

    def test_balloon_dilation_derives_31638(self, coder):
        """Test: Balloon dilation → 31638."""
        actions = ClinicalActions(
            cao=CAOActions(performed=True, dilation_performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31638" in codes


class TestStentCodeDerivation:
    """Test stent code derivation."""

    def test_bronchial_stent_derives_31636(self, coder):
        """Test: Bronchial stent → 31636."""
        actions = ClinicalActions(
            stent=StentActions(
                performed=True,
                action="insertion",
                location="RMS",
            ),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31636" in codes

    def test_tracheal_stent_derives_31631(self, coder):
        """Test: Tracheal stent → 31631."""
        actions = ClinicalActions(
            stent=StentActions(
                performed=True,
                action="insertion",
                location="trachea",
            ),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31631" in codes


class TestBLVRCodeDerivation:
    """Test BLVR code derivation."""

    def test_chartis_derives_31647(self, coder):
        """Test: Chartis assessment → 31647."""
        actions = ClinicalActions(
            blvr=BLVRActions(chartis_performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31647" in codes

    def test_valve_placement_derives_31651_per_valve(self, coder_no_bundling):
        """Test: Valve placement → one 31651 per valve."""
        actions = ClinicalActions(
            blvr=BLVRActions(
                performed=True,
                chartis_performed=True,
                valve_count=4,
                target_lobe="RUL",
            ),
            diagnostic_bronchoscopy=True,
        )
        result = coder_no_bundling.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31647" in codes  # Chartis/assessment
        assert codes.count("+31651") == 4  # One per valve


class TestBundlingRules:
    """Test NCCI bundling rule application."""

    def test_thoracentesis_bundled_into_ipc(self, coder):
        """Test: Thoracentesis bundled into IPC placement."""
        actions = ClinicalActions(
            pleural=PleuralActions(
                thoracentesis_performed=True,
                ipc_performed=True,
            ),
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        # IPC should remain, thoracentesis should be bundled
        assert "32550" in codes
        assert "32555" not in codes
        assert "32555" in result.bundled_codes or "32554" in result.bundled_codes

    def test_bundling_reasons_populated(self, coder):
        """Test: Bundling reasons are populated."""
        actions = ClinicalActions(
            pleural=PleuralActions(
                thoracentesis_performed=True,
                ipc_performed=True,
            ),
        )
        result = coder.derive_codes(actions)

        assert len(result.bundling_reasons) > 0


class TestDiagnosticBronchoscopy:
    """Test diagnostic bronchoscopy fallback code."""

    def test_diagnostic_bronch_only_derives_31622(self, coder):
        """Test: Diagnostic bronchoscopy with no procedures → 31622."""
        actions = ClinicalActions(diagnostic_bronchoscopy=True)
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31622" in codes
        assert len(codes) == 1

    def test_diagnostic_bronch_suppressed_when_other_codes(self, coder):
        """Test: No 31622 when other bronchoscopy codes present."""
        actions = ClinicalActions(
            bal=BALActions(performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31624" in codes  # BAL code
        assert "31622" not in codes  # Diagnostic suppressed


class TestDerivationResult:
    """Test DerivationResult structure and methods."""

    def test_get_code_list_returns_strings(self, coder):
        """Test: get_code_list returns code strings."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7", "11L"]),
            bal=BALActions(performed=True),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        code_list = result.get_code_list()
        assert isinstance(code_list, list)
        assert all(isinstance(c, str) for c in code_list)
        assert "31653" in code_list
        assert "31624" in code_list


class TestComplexProcedures:
    """Test complex multi-procedure scenarios."""

    def test_ebus_navigation_biopsy_bal(self, coder):
        """Test: Complex procedure with EBUS, navigation, biopsy, BAL."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7", "11L"]),
            navigation=NavigationActions(performed=True, platform="superDimension"),
            biopsy=BiopsyActions(
                transbronchial_performed=True,
                transbronchial_sites=["RUL"],
            ),
            bal=BALActions(performed=True, sites=["RML"]),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31653" in codes  # EBUS 3+ stations
        assert "31627" in codes  # Navigation add-on
        assert "31628" in codes  # Transbronchial biopsy
        assert "31624" in codes  # BAL

    def test_cao_with_stent_and_dilation(self, coder):
        """Test: CAO procedure with stent and dilation."""
        actions = ClinicalActions(
            cao=CAOActions(
                performed=True,
                thermal_ablation_performed=True,
                dilation_performed=True,
            ),
            stent=StentActions(
                performed=True,
                action="insertion",
                location="RMS",
            ),
            diagnostic_bronchoscopy=True,
        )
        result = coder.derive_codes(actions)

        codes = [c.code for c in result.codes]
        assert "31641" in codes  # Tumor destruction
        assert "31638" in codes  # Balloon dilation
        assert "31636" in codes  # Bronchial stent


class TestConvenienceFunction:
    """Test the convenience function."""

    def test_derive_codes_from_actions(self):
        """Test: Convenience function works."""
        actions = ClinicalActions(
            ebus=EBUSActions(performed=True, stations=["4R", "7"]),
            diagnostic_bronchoscopy=True,
        )
        result = derive_codes_from_actions(actions)

        assert isinstance(result, DerivationResult)
        codes = [c.code for c in result.codes]
        assert "31652" in codes
