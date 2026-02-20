from __future__ import annotations

from pathlib import Path

from app.document_fingerprint.registry import fingerprint_document, split_pdf_fulltext
from app.sectioning.endosoft_section_parser import parse_endosoft_procedure_pages
from app.text_cleaning.endosoft_cleaner import clean_endosoft_page


def test_endosoft_section_parser_extracts_core_sections_and_codes() -> None:
    fixture = Path("tests/fixtures/vendor/endosoft_photoreport_sample.txt").read_text(encoding="utf-8")
    doc = split_pdf_fulltext(fixture)
    fp = fingerprint_document(fixture, doc.page_texts)
    assert fp.vendor == "endosoft"

    cleaned_pages = [
        clean_endosoft_page(page_text, page_type)
        for page_text, page_type in zip(doc.page_texts, fp.page_types, strict=True)
    ]

    notes = parse_endosoft_procedure_pages(
        raw_pages=doc.page_texts,
        clean_pages=cleaned_pages,
        page_types=fp.page_types,
        template_family=fp.template_family,
    )

    assert notes, "Expected at least one procedure_report canonical note"
    note = notes[0]
    assert note.demographics.get("patient_name")
    assert note.sections.get("procedure_performed")
    assert note.sections.get("findings")
    assert note.sections.get("recommendations")
    assert "31622" in note.codes.get("cpt", [])
    assert "R91.1" in note.codes.get("icd10", [])

