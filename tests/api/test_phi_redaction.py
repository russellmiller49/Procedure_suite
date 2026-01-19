"""Unit tests for PHI redaction helper module.

Tests the apply_phi_redaction function which provides unified PHI
redaction at the API route handler level.
"""

from dataclasses import dataclass
from typing import List
from unittest.mock import Mock

from modules.api.phi_redaction import RedactionResult, apply_phi_redaction


@dataclass
class MockEntity:
    """Mock PHI entity for testing."""
    entity_type: str
    start: int
    end: int


@dataclass
class MockScrubResult:
    """Mock scrub result for testing."""
    scrubbed_text: str
    entities: List[MockEntity]


class TestApplyPhiRedaction:
    """Tests for apply_phi_redaction function."""

    def test_scrubs_text_when_scrubber_available(self):
        """Text is scrubbed when a valid scrubber is provided."""
        # Arrange
        raw_text = "Patient John Smith has diabetes"
        mock_scrubber = Mock()
        mock_scrubber.scrub.return_value = MockScrubResult(
            scrubbed_text="Patient <PERSON> has diabetes",
            entities=[MockEntity("PERSON", 8, 18)],
        )

        # Act
        result = apply_phi_redaction(raw_text, mock_scrubber)

        # Assert
        assert result.text == "Patient <PERSON> has diabetes"
        assert result.was_scrubbed is True
        assert result.entity_count == 1
        assert result.warning is None
        mock_scrubber.scrub.assert_called_once_with(raw_text)

    def test_skips_scrubbing_when_already_scrubbed(self):
        """Text is passed through unchanged when already_scrubbed=True."""
        # Arrange
        already_scrubbed_text = "Patient <PERSON> has diabetes"
        mock_scrubber = Mock()

        # Act
        result = apply_phi_redaction(
            already_scrubbed_text,
            mock_scrubber,
            already_scrubbed=True,
        )

        # Assert
        assert result.text == already_scrubbed_text
        assert result.was_scrubbed is False
        assert result.entity_count == 0
        assert result.warning is None
        mock_scrubber.scrub.assert_not_called()

    def test_returns_original_text_when_no_scrubber(self):
        """Returns original text with warning when scrubber is None."""
        # Arrange
        raw_text = "Patient John Smith has diabetes"

        # Act
        result = apply_phi_redaction(raw_text, scrubber=None)

        # Assert
        assert result.text == raw_text
        assert result.was_scrubbed is False
        assert result.entity_count == 0
        assert result.warning == "PHI scrubber not configured"

    def test_returns_original_text_when_scrubber_fails(self):
        """Returns original text with warning when scrubber raises exception."""
        # Arrange
        raw_text = "Patient John Smith has diabetes"
        mock_scrubber = Mock()
        mock_scrubber.scrub.side_effect = RuntimeError("Presidio model not loaded")

        # Act
        result = apply_phi_redaction(raw_text, mock_scrubber)

        # Assert
        assert result.text == raw_text
        assert result.was_scrubbed is False
        assert result.entity_count == 0
        assert "PHI scrubbing failed" in result.warning
        assert "Presidio model not loaded" in result.warning

    def test_handles_empty_text(self):
        """Handles empty text input gracefully."""
        # Arrange
        mock_scrubber = Mock()
        mock_scrubber.scrub.return_value = MockScrubResult(
            scrubbed_text="",
            entities=[],
        )

        # Act
        result = apply_phi_redaction("", mock_scrubber)

        # Assert
        assert result.text == ""
        assert result.was_scrubbed is True
        assert result.entity_count == 0

    def test_handles_no_phi_in_text(self):
        """Handles text with no PHI entities detected."""
        # Arrange
        clean_text = "The procedure was completed successfully"
        mock_scrubber = Mock()
        mock_scrubber.scrub.return_value = MockScrubResult(
            scrubbed_text=clean_text,
            entities=[],
        )

        # Act
        result = apply_phi_redaction(clean_text, mock_scrubber)

        # Assert
        assert result.text == clean_text
        assert result.was_scrubbed is True
        assert result.entity_count == 0
        assert result.warning is None

    def test_handles_multiple_entities(self):
        """Handles text with multiple PHI entities."""
        # Arrange
        raw_text = "Patient John Smith, DOB 01/01/1990, MRN 12345"
        mock_scrubber = Mock()
        mock_scrubber.scrub.return_value = MockScrubResult(
            scrubbed_text="Patient <PERSON>, DOB <DATE_TIME>, MRN <MRN>",
            entities=[
                MockEntity("PERSON", 8, 18),
                MockEntity("DATE_TIME", 24, 34),
                MockEntity("MRN", 40, 45),
            ],
        )

        # Act
        result = apply_phi_redaction(raw_text, mock_scrubber)

        # Assert
        assert result.text == "Patient <PERSON>, DOB <DATE_TIME>, MRN <MRN>"
        assert result.was_scrubbed is True
        assert result.entity_count == 3


class TestRedactionResult:
    """Tests for RedactionResult dataclass."""

    def test_dataclass_fields(self):
        """RedactionResult has expected fields."""
        result = RedactionResult(
            text="scrubbed text",
            was_scrubbed=True,
            entity_count=5,
            warning=None,
        )

        assert result.text == "scrubbed text"
        assert result.was_scrubbed is True
        assert result.entity_count == 5
        assert result.warning is None

    def test_warning_field_optional(self):
        """Warning field can be None or a string."""
        result_no_warning = RedactionResult(
            text="text",
            was_scrubbed=True,
            entity_count=0,
            warning=None,
        )
        assert result_no_warning.warning is None

        result_with_warning = RedactionResult(
            text="text",
            was_scrubbed=False,
            entity_count=0,
            warning="Scrubber unavailable",
        )
        assert result_with_warning.warning == "Scrubber unavailable"
