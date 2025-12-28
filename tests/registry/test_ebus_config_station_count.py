"""Tests for config-driven EBUS station counting.

These tests verify the behavior of _count_sampled_nodes() with:
- Config-driven allow-list filtering
- Alias resolution
- Backward compatibility when config not passed
"""

from dataclasses import dataclass
from typing import Optional
from unittest.mock import patch

import pytest

from modules.coder.ebus_rules import (
    _count_sampled_nodes,
    ebus_nodes_to_candidates,
    get_sampled_station_list,
)
from modules.registry.ebus_config import (
    load_ebus_config,
    resolve_station_alias,
    is_valid_station,
)


@dataclass
class MockEBUSEvidence:
    """Mock EBUS evidence for testing."""

    station: str
    action: str = "Sampling"
    method: Optional[str] = None


class TestEBUSConfigLoader:
    """Tests for the EBUS config loader."""

    def test_load_ebus_config_returns_expected_structure(self):
        """Config should have target_action, valid_stations, and aliases."""
        config = load_ebus_config()

        assert "target_action" in config
        assert "valid_stations" in config
        assert "aliases" in config
        assert isinstance(config["valid_stations"], set)
        assert isinstance(config["aliases"], dict)

    def test_load_ebus_config_valid_stations_normalized(self):
        """Valid stations should be uppercase."""
        config = load_ebus_config()

        for station in config["valid_stations"]:
            assert station == station.upper()

    def test_load_ebus_config_aliases_normalized(self):
        """Alias keys and values should be uppercase."""
        config = load_ebus_config()

        for key, value in config["aliases"].items():
            assert key == key.upper()
            assert value == value.upper()


class TestStationAliasResolution:
    """Tests for alias resolution."""

    def test_resolve_alias_subcarinal_to_7(self):
        """SUBCARINAL should resolve to 7."""
        aliases = {"SUBCARINAL": "7"}
        assert resolve_station_alias("Subcarinal", aliases) == "7"
        assert resolve_station_alias("SUBCARINAL", aliases) == "7"
        assert resolve_station_alias("subcarinal", aliases) == "7"

    def test_resolve_alias_preserves_unknown(self):
        """Unknown stations should be returned as-is (uppercase)."""
        aliases = {"SUBCARINAL": "7"}
        assert resolve_station_alias("4R", aliases) == "4R"
        assert resolve_station_alias("10L", aliases) == "10L"

    def test_resolve_alias_handles_whitespace(self):
        """Whitespace should be stripped."""
        aliases = {"SUBCARINAL": "7"}
        assert resolve_station_alias("  Subcarinal  ", aliases) == "7"


class TestStationValidation:
    """Tests for station validation."""

    def test_is_valid_station_with_known_station(self):
        """Known stations should be valid."""
        valid = {"4R", "7", "10L"}
        aliases = {}
        assert is_valid_station("4R", valid, aliases) is True
        assert is_valid_station("7", valid, aliases) is True

    def test_is_valid_station_with_alias(self):
        """Aliased stations should be valid after resolution."""
        valid = {"7"}
        aliases = {"SUBCARINAL": "7"}
        assert is_valid_station("Subcarinal", valid, aliases) is True

    def test_is_valid_station_with_unknown(self):
        """Unknown stations should be invalid."""
        valid = {"4R", "7"}
        aliases = {}
        assert is_valid_station("KIDNEY", valid, aliases) is False
        assert is_valid_station("4RR", valid, aliases) is False


class TestCountSampledNodesWithConfig:
    """Tests for _count_sampled_nodes with explicit config."""

    def test_ebus_count_only_counts_sampling_action(self):
        """Only entries with action='Sampling' should be counted."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R"},
            "aliases": {},
        }
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="4R", action="Inspection"),
            MockEBUSEvidence(station="4R", action="Visual"),
        ]

        count = _count_sampled_nodes(evidence, config)
        assert count == 1

    def test_ebus_aliases_are_resolved(self):
        """Aliased stations should map to canonical code."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"7"},
            "aliases": {"SUBCARINAL": "7"},
        }
        evidence = [
            MockEBUSEvidence(station="Subcarinal", action="Sampling"),
            MockEBUSEvidence(station="7", action="Sampling"),
        ]

        count = _count_sampled_nodes(evidence, config)
        # Both map to "7", so count should be 1
        assert count == 1

    def test_ebus_ignores_unknown_stations(self):
        """Stations not in valid_stations should be ignored."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R"},
            "aliases": {},
        }
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),  # valid
            MockEBUSEvidence(station="KIDNEY", action="Sampling"),  # invalid
            MockEBUSEvidence(station="4RR", action="Sampling"),  # typo, invalid
        ]

        count = _count_sampled_nodes(evidence, config)
        assert count == 1

    def test_ebus_empty_valid_stations_accepts_all(self):
        """Empty valid_stations set should accept all stations."""
        config = {
            "target_action": "Sampling",
            "valid_stations": set(),  # Empty = accept all
            "aliases": {},
        }
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="ANYTHING", action="Sampling"),
        ]

        count = _count_sampled_nodes(evidence, config)
        assert count == 2

    def test_ebus_counts_unique_stations_only(self):
        """Multiple samples at same station should count as one."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R", "7"},
            "aliases": {},
        }
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="4R", action="Sampling"),  # duplicate
            MockEBUSEvidence(station="7", action="Sampling"),
        ]

        count = _count_sampled_nodes(evidence, config)
        assert count == 2

    def test_ebus_case_insensitive_matching(self):
        """Station matching should be case-insensitive."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R"},
            "aliases": {},
        }
        evidence = [
            MockEBUSEvidence(station="4r", action="Sampling"),
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="4r ", action="Sampling"),
        ]

        count = _count_sampled_nodes(evidence, config)
        assert count == 1  # All normalize to "4R"


class TestEBUSNodesToCandidates:
    """Tests for ebus_nodes_to_candidates code selection."""

    def test_zero_stations_returns_empty(self):
        """No sampling should return empty candidates."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R"},
            "aliases": {},
        }
        evidence = [
            MockEBUSEvidence(station="4R", action="Inspection"),
        ]

        candidates = ebus_nodes_to_candidates(evidence, config)
        assert candidates == []

    def test_one_to_two_stations_returns_31652(self):
        """1-2 stations sampled should return code 31652."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R", "7"},
            "aliases": {},
        }

        # One station
        evidence1 = [MockEBUSEvidence(station="4R", action="Sampling")]
        candidates1 = ebus_nodes_to_candidates(evidence1, config)
        assert len(candidates1) == 1
        assert candidates1[0].code == "31652"

        # Two stations
        evidence2 = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="7", action="Sampling"),
        ]
        candidates2 = ebus_nodes_to_candidates(evidence2, config)
        assert len(candidates2) == 1
        assert candidates2[0].code == "31652"

    def test_three_plus_stations_returns_31653(self):
        """3+ stations sampled should return code 31653."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R", "4L", "7", "10R"},
            "aliases": {},
        }
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="4L", action="Sampling"),
            MockEBUSEvidence(station="7", action="Sampling"),
        ]

        candidates = ebus_nodes_to_candidates(evidence, config)
        assert len(candidates) == 1
        assert candidates[0].code == "31653"


class TestGetSampledStationList:
    """Tests for get_sampled_station_list helper."""

    def test_returns_sorted_unique_stations(self):
        """Should return sorted list of unique station codes."""
        config = {
            "target_action": "Sampling",
            "valid_stations": {"4R", "7", "10L"},
            "aliases": {"SUBCARINAL": "7"},
        }
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="Subcarinal", action="Sampling"),  # -> 7
            MockEBUSEvidence(station="10L", action="Sampling"),
            MockEBUSEvidence(station="7", action="Sampling"),  # duplicate after alias
        ]

        result = get_sampled_station_list(evidence, config)
        assert result == ["10L", "4R", "7"]


class TestBackwardCompatibility:
    """Tests for backward compatibility when config not passed."""

    def test_count_sampled_nodes_works_without_config(self):
        """Function should work when config is not passed (uses default)."""
        # Create evidence with known valid stations from default config
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="7", action="Sampling"),
        ]

        # Should not raise, should return a count
        count = _count_sampled_nodes(evidence)
        assert isinstance(count, int)
        assert count >= 0

    def test_ebus_nodes_to_candidates_works_without_config(self):
        """Function should work when config is not passed."""
        evidence = [
            MockEBUSEvidence(station="4R", action="Sampling"),
            MockEBUSEvidence(station="7", action="Sampling"),
            MockEBUSEvidence(station="10L", action="Sampling"),
        ]

        candidates = ebus_nodes_to_candidates(evidence)
        assert len(candidates) == 1
        assert candidates[0].code in {"31652", "31653"}
