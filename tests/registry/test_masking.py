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


def test_mask_offset_preserving_masks_empty_table_rows() -> None:
    raw = (
        "Modality\tTools\tSetting/Mode\tDuration\tResults\n"
        "Electrocautery\tKnife\tSoft coag\t4 sec\tRemoved tumor\n"
        "APC\t\t\t\t\n"
        "Laser\t\t\t\t\n"
    )
    masked = mask_offset_preserving(raw)

    assert len(masked) == len(raw)
    assert _newline_positions(masked) == _newline_positions(raw)

    apc_start = raw.index("APC")
    apc_end = raw.index("\n", apc_start) + 1
    masked_apc_row = masked[apc_start:apc_end]
    assert re.search(r"[^\n ]", masked_apc_row) is None

    assert "Electrocautery\tKnife" in masked


def test_mask_offset_preserving_masks_cpt_definition_continuation_lines() -> None:
    raw = (
        "PROCEDURE:\n"
        "31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg.\n"
        "  laser therapy, cryotherapy)\n"
        "\n"
        "PROCEDURE IN DETAIL:\n"
        "Mechanical debulking performed.\n"
    )
    masked = mask_offset_preserving(raw)

    assert len(masked) == len(raw)
    assert "laser" not in masked.lower()
    assert "cryotherapy" not in masked.lower()
