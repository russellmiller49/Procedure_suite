from app.reporting.normalization.compat_enricher import _add_compat_flat_fields


def test_add_compat_flat_fields_brushings_counts_text_does_not_require_brushings_object() -> None:
    raw = {"procedures_performed": {}, "source_text": "Brush x 2"}
    out = _add_compat_flat_fields(raw)
    assert out is raw
    assert isinstance(raw.get("bronchial_brushings"), dict)
    assert raw["bronchial_brushings"]["samples_collected"] == 2
    assert raw["bronchial_brushings"]["brush_tool"] is None

