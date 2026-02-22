from __future__ import annotations

from app.text_cleaning.camera_ocr_fuzzy import (
    clear_camera_ocr_fuzzy_phrase_cache,
    normalize_camera_ocr_for_extraction,
)


def test_camera_ocr_fuzzy_normalizes_high_value_phrases() -> None:
    text = "Successful therapevtic aspiratlon performed. Bronchoalvealar lavage obtained."
    out = normalize_camera_ocr_for_extraction(text)

    assert "therapeutic aspiration" in out.text.lower()
    assert "bronchoalveolar lavage" in out.text.lower()
    assert out.replacement_count >= 2


def test_camera_ocr_fuzzy_preserves_bracket_tokens() -> None:
    text = "[REDACTED] had therapevtic aspiratlon and [DATE: T+5 DAYS] follow-up."
    out = normalize_camera_ocr_for_extraction(text)

    assert "[REDACTED]" in out.text
    assert "[DATE: T+5 DAYS]" in out.text


def test_camera_ocr_fuzzy_phrase_json_override(monkeypatch) -> None:
    monkeypatch.setenv("CAMERA_OCR_FUZZY_PHRASES_JSON", '["therapeutic aspiration"]')
    monkeypatch.delenv("CAMERA_OCR_FUZZY_PHRASES_PATH", raising=False)
    clear_camera_ocr_fuzzy_phrase_cache()

    text = "therapevtic aspiratlon done. Bronchoalvealar lavage obtained."
    out = normalize_camera_ocr_for_extraction(text)

    assert "therapeutic aspiration" in out.text.lower()
    assert "bronchoalveolar lavage" not in out.text.lower()

    clear_camera_ocr_fuzzy_phrase_cache()


def test_camera_ocr_fuzzy_phrase_file_override(tmp_path, monkeypatch) -> None:
    config_path = tmp_path / "camera_ocr_phrases.json"
    config_path.write_text(
        '[{"phrase":"custom phrase","threshold_full":70,"threshold_token_avg":60,"threshold_token_min":50}]',
        encoding="utf-8",
    )
    monkeypatch.delenv("CAMERA_OCR_FUZZY_PHRASES_JSON", raising=False)
    monkeypatch.setenv("CAMERA_OCR_FUZZY_PHRASES_PATH", str(config_path))
    clear_camera_ocr_fuzzy_phrase_cache()

    text = "The cust0m phraze was documented."
    out = normalize_camera_ocr_for_extraction(text)
    assert "custom phrase" in out.text.lower()

    clear_camera_ocr_fuzzy_phrase_cache()


def test_camera_ocr_fuzzy_invalid_json_falls_back_to_defaults(monkeypatch) -> None:
    monkeypatch.setenv("CAMERA_OCR_FUZZY_PHRASES_JSON", "{not valid json")
    monkeypatch.delenv("CAMERA_OCR_FUZZY_PHRASES_PATH", raising=False)
    clear_camera_ocr_fuzzy_phrase_cache()

    text = "therapevtic aspiratlon was successful."
    out = normalize_camera_ocr_for_extraction(text)
    assert "therapeutic aspiration" in out.text.lower()

    clear_camera_ocr_fuzzy_phrase_cache()
