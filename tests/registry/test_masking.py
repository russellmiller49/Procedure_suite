import re

from modules.registry.processing.masking import PATTERNS, mask_offset_preserving


def _newline_positions(text: str) -> list[int]:
    return [idx for idx, char in enumerate(text) if char == "\n"]


def test_mask_offset_preserving_length_and_newlines() -> None:
    raw = (
        "HEADER\n"
        "CPT CODES:\n"
        "31623 Bronchoscopy\n"
        "\n"
        "PROCEDURE:\n"
        "Bronchoscopy performed.\n"
    )
    masked = mask_offset_preserving(raw)

    assert len(masked) == len(raw)
    assert _newline_positions(masked) == _newline_positions(raw)


def test_mask_offset_preserving_masks_header_only() -> None:
    raw = (
        "CPT CODES:\n"
        "31623 Bronchoscopy\n"
        "\n"
        "PROCEDURE:\n"
        "Bronchoscopy performed.\n"
    )
    masked = mask_offset_preserving(raw)

    match = re.search(PATTERNS[0], raw)
    assert match is not None

    masked_segment = masked[match.start() : match.end()]
    assert re.search(r"[^\n ]", masked_segment) is None

    phrase = "Bronchoscopy performed."
    start = raw.index(phrase)
    end = start + len(phrase)
    assert masked[start:end] == phrase


def test_mask_offset_preserving_idempotent() -> None:
    raw = (
        "CPT CODES:\n"
        "31624 BAL\n"
        "\n"
        "PROCEDURE:\n"
        "Bronchoscopy performed.\n"
    )
    masked_once = mask_offset_preserving(raw)
    masked_twice = mask_offset_preserving(masked_once)

    assert masked_twice == masked_once


def test_mask_offset_preserving_masks_cpt_code_line() -> None:
    raw = (
        "31624 BAL\n"
        "PROCEDURE:\n"
        "Bronchoscopy performed.\n"
    )
    masked = mask_offset_preserving(raw)

    first_line = masked.splitlines()[0]
    assert re.search(r"[^\n ]", first_line) is None
