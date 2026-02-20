from __future__ import annotations

from pathlib import Path

from app.document_fingerprint.registry import fingerprint_document, split_pdf_fulltext


def test_provation_fingerprint_va_sd_fixture() -> None:
    fixture = Path("tests/fixtures/vendor/provation_va_sd_sample.txt").read_text(encoding="utf-8")
    doc = split_pdf_fulltext(fixture)
    fp = fingerprint_document(fixture, doc.page_texts)

    assert fp.vendor == "provation"
    assert fp.template_family == "provation_va_sd"
    assert fp.confidence > 0.8
    assert len(fp.page_types) == len(doc.pages)
    assert fp.page_types.count("procedure_report") >= 1
    assert fp.page_types.count("images_page") >= 1

