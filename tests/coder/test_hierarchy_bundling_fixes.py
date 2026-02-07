"""Tests for hierarchy, bundling, and EBUS counting fixes.

These tests verify the fixes for:
1. Hierarchy/Add-on Logic (Stents): 31636 -> +31637 when 31631 present
2. Bundling Rules: EBUS bundles aspiration (31645/31646)
3. EBUS Counting: Sampled vs inspected stations
4. Data Ingestion: Smart text truncation
"""

import pytest

from app.coder.domain_rules import (
    apply_addon_family_rules,
    apply_ebus_aspiration_bundles,
    count_sampled_ebus_stations,
    determine_ebus_code,
)
from app.coder.posthoc import enforce_addon_family_consistency
from app.coder.schema import CodeDecision


class TestAddonFamilyRules:
    """Test add-on family consistency rules (Failure 1 fix)."""

    def test_stent_family_conversion(self):
        """When 31631 (tracheal) present, 31636 (bronchial initial) -> +31637."""
        codes = ["31631", "31636"]
        result = apply_addon_family_rules(codes)

        assert result.converted_codes == ["31631", "+31637"]
        assert len(result.conversions) == 1
        assert result.conversions[0][0] == "31636"  # original
        assert result.conversions[0][1] == "+31637"  # converted

    def test_stent_family_multiple_bronchial(self):
        """Multiple bronchial stents all become add-ons when tracheal present."""
        codes = ["31631", "31636", "31636"]
        result = apply_addon_family_rules(codes)

        assert result.converted_codes == ["31631", "+31637", "+31637"]
        assert len(result.conversions) == 2

    def test_no_conversion_without_primary(self):
        """31636 stays as-is when 31631 not present."""
        codes = ["31636", "31636"]
        result = apply_addon_family_rules(codes)

        assert result.converted_codes == ["31636", "31636"]
        assert len(result.conversions) == 0

    def test_already_addon_unchanged(self):
        """Existing +31637 codes are not modified."""
        codes = ["31631", "+31637"]
        result = apply_addon_family_rules(codes)

        assert result.converted_codes == ["31631", "+31637"]
        assert len(result.conversions) == 0


class TestEBUSAspirationBundling:
    """Test EBUS-Aspiration bundling rules (Failure 2 fix)."""

    def test_ebus_bundles_aspiration(self):
        """31652/31653 bundles 31645/31646."""
        codes = ["31652", "31645"]
        result = apply_ebus_aspiration_bundles(codes)

        assert "31652" in result.kept_codes
        assert "31645" not in result.kept_codes
        assert "31645" in result.removed_codes

    def test_ebus_3plus_bundles_aspiration(self):
        """31653 also bundles aspiration."""
        codes = ["31653", "31645", "31646"]
        result = apply_ebus_aspiration_bundles(codes)

        assert result.kept_codes == ["31653"]
        assert set(result.removed_codes) == {"31645", "31646"}

    def test_aspiration_kept_without_ebus(self):
        """Aspiration codes kept when EBUS not present."""
        codes = ["31628", "31645"]  # TBLB + aspiration
        result = apply_ebus_aspiration_bundles(codes)

        assert result.kept_codes == ["31628", "31645"]
        assert result.removed_codes == []


class TestEBUSStationCounting:
    """Test EBUS station counting logic (Failure 3 fix)."""

    def test_count_sampled_stations(self):
        """Correctly count sampled (not inspected) stations."""
        text = """
        EBUS Procedure:
        Sites Inspected: 4R, 7, 10R, 11R, 11L, 4L

        TBNA performed at station 7 with 3 passes. Adequate sample obtained.
        Station 11L was sampled with FNA, ROSE positive for malignancy.
        """
        count = count_sampled_ebus_stations(text)
        assert count == 2  # Only 7 and 11L were sampled

    def test_inspection_only_not_counted(self):
        """Inspection-only stations should not be counted."""
        text = """
        Lymph Nodes Inspected: 4R, 7, 11L
        All stations appeared normal, no masses identified.
        No sampling performed.
        """
        count = count_sampled_ebus_stations(text)
        assert count == 0

    def test_mixed_sampled_inspected(self):
        """Mixed sampling and inspection correctly counted."""
        text = """
        Station 4R was inspected and appeared unremarkable.
        Station 7 was sampled with TBNA, 4 passes obtained.
        Station 11L inspected, normal appearing nodes.
        """
        count = count_sampled_ebus_stations(text)
        assert count == 1  # Only station 7 was sampled

    def test_determine_code_1_2_stations(self):
        """1-2 sampled stations -> 31652."""
        assert determine_ebus_code(1) == "31652"
        assert determine_ebus_code(2) == "31652"

    def test_determine_code_3plus_stations(self):
        """3+ sampled stations -> 31653."""
        assert determine_ebus_code(3) == "31653"
        assert determine_ebus_code(5) == "31653"

    def test_determine_code_no_stations(self):
        """0 sampled stations -> empty string."""
        assert determine_ebus_code(0) == ""


class TestPosthocAddonConversion:
    """Test posthoc addon conversion with CodeDecision objects."""

    def test_posthoc_converts_codes(self):
        """Posthoc function correctly converts codes."""
        codes = [
            CodeDecision(
                cpt="31631",
                description="Tracheal stent",
                rationale="Stent placed",
                evidence=[],
            ),
            CodeDecision(
                cpt="31636",
                description="Bronchial stent initial",
                rationale="Stent placed",
                evidence=[],
            ),
        ]

        result = enforce_addon_family_consistency(codes)

        assert result[0].cpt == "31631"
        assert result[1].cpt == "+31637"
        assert "addon_family_conversion" in result[1].rule_trace


class TestSmartTextTruncation:
    """Test smart text truncation for LLM processing (Failure 4 fix)."""

    def test_short_text_unchanged(self):
        """Text under limit is not modified."""
        from app.coder.adapters.llm.gemini_advisor import GeminiAdvisorAdapter

        adapter = GeminiAdvisorAdapter()
        short_text = "This is a short procedure note."
        result = adapter._prepare_text_for_llm(short_text)

        assert result == short_text

    def test_long_text_preserves_ends(self):
        """Long text preserves beginning and end."""
        from app.coder.adapters.llm.gemini_advisor import GeminiAdvisorAdapter

        adapter = GeminiAdvisorAdapter()

        # Create text longer than MAX_TEXT_SIZE
        begin_marker = "BEGIN_UNIQUE_MARKER"
        end_marker = "END_UNIQUE_MARKER"
        middle_content = "X" * 50000  # Long middle section

        long_text = f"{begin_marker} {middle_content} {end_marker}"
        result = adapter._prepare_text_for_llm(long_text)

        # Both markers should be present
        assert begin_marker in result
        assert end_marker in result
        # Should have truncation indicator
        assert "omitted" in result.lower() or "truncated" in result.lower()


class TestExpectedScenarios:
    """Test the specific scenarios from the issue description."""

    def test_note1_stent_scenario(self):
        """Note 1: Tracheal + Bronchial stents -> 31631 + +31637 (x2)."""
        codes = ["31631", "31636", "31636"]
        result = apply_addon_family_rules(codes)

        # Expected: 31631, +31637, +31637
        assert result.converted_codes == ["31631", "+31637", "+31637"]

    def test_note2_ebus_aspiration_bundle(self):
        """Note 2: EBUS present bundles aspiration."""
        codes = ["31652", "31645", "31628", "31626", "+31627", "+31654"]
        result = apply_ebus_aspiration_bundles(codes)

        # 31645 should be bundled into 31652
        assert "31645" in result.removed_codes
        assert "31645" not in result.kept_codes

        # Other codes should remain
        assert "31652" in result.kept_codes
        assert "31628" in result.kept_codes
        assert "31626" in result.kept_codes

    def test_note2_ebus_station_count(self):
        """Note 2: Only sampled stations counted (2 stations -> 31652)."""
        text = """
        Lymph Nodes Inspected: 4R, 7, 10R, 11R, 11L, 4L

        EBUS-TBNA performed:
        - Station 7: 4 passes, ROSE adequate
        - Station 11L: 3 passes, sample obtained for cytology

        All other stations inspected and appeared unremarkable.
        """
        count = count_sampled_ebus_stations(text)
        code = determine_ebus_code(count)

        assert count == 2
        assert code == "31652"  # NOT 31653 (which requires 3+ stations)
