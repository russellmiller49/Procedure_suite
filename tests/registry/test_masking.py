import re

from app.registry.processing.masking import PATTERNS, mask_extraction_noise, mask_offset_preserving


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


def test_mask_offset_preserving_masks_checkbox_template_negatives() -> None:
    raw = (
        "0- Chest tube\n"
        "[ ] Tunneled Pleural Catheter\n"
        "☐ Airway dilation\n"
        "\n"
        "PROCEDURE:\n"
        "Bronchoscopy performed.\n"
    )
    masked = mask_offset_preserving(raw)

    assert len(masked) == len(raw)
    assert _newline_positions(masked) == _newline_positions(raw)

    for line in ("0- Chest tube", "[ ] Tunneled Pleural Catheter", "☐ Airway dilation"):
        start = raw.index(line)
        end = start + len(line)
        assert re.search(r"[^\n ]", masked[start:end]) is None

    phrase = "Bronchoscopy performed."
    start = raw.index(phrase)
    end = start + len(phrase)
    assert masked[start:end] == phrase


def test_mask_extraction_noise_masks_appended_extraction_quality_report() -> None:
    raw = (
        "PROCEDURE IN DETAIL:\n"
        "Therapeutic aspiration was performed.\n"
        "\n"
        "Extraction Quality Report\n"
        "Hallucination: cryotherapy was performed.\n"
    )

    masked, meta = mask_extraction_noise(raw)
    assert meta.get("masked_external_report_count") == 1
    marker = raw.index("Extraction Quality Report")
    tail = masked[marker:]
    assert re.search(r"[^\n ]", tail) is None

    phrase = "Therapeutic aspiration was performed."
    start = raw.index(phrase)
    end = start + len(phrase)
    assert masked[start:end] == phrase


def test_mask_extraction_noise_does_not_overmask_procedure_detail_without_colon_headings() -> None:
    raw = (
        "INDICATION FOR OPERATION: airway stenosis\n"
        "\n"
        "CONSENT\n"
        "Obtained before procedure.\n"
        "\n"
        "PROCEDURE IN DETAIL\n"
        "Therapeutic aspiration of retained secretions was performed.\n"
        "A custom silicone Y-stent was placed and seated appropriately.\n"
    )

    masked, meta = mask_extraction_noise(raw)
    assert "INDICATION FOR OPERATION" in (meta.get("masked_non_procedural_sections") or [])

    phrase = "Therapeutic aspiration of retained secretions was performed."
    start = raw.index(phrase)
    end = start + len(phrase)
    assert masked[start:end] == phrase

    stent_phrase = "A custom silicone Y-stent was placed and seated appropriately."
    start = raw.index(stent_phrase)
    end = start + len(stent_phrase)
    assert masked[start:end] == stent_phrase
