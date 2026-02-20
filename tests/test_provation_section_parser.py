from __future__ import annotations

from pathlib import Path

from app.document_fingerprint.registry import fingerprint_document, split_pdf_fulltext
from app.sectioning.provation_section_parser import parse_provation_procedure_pages
from app.text_cleaning.provation_cleaner import clean_provation


def test_provation_section_parser_extracts_demographics_sections_codes_and_signatures() -> None:
    fixture = Path("tests/fixtures/vendor/provation_va_sd_sample.txt").read_text(encoding="utf-8")
    doc = split_pdf_fulltext(fixture)
    fp = fingerprint_document(fixture, doc.page_texts)
    assert fp.vendor == "provation"

    cleaned_pages = clean_provation(doc.page_texts, fp.page_types)
    clean_texts = [p.clean_text for p in cleaned_pages]

    notes = parse_provation_procedure_pages(
        raw_pages=doc.page_texts,
        clean_pages=clean_texts,
        page_types=fp.page_types,
        template_family=fp.template_family,
    )

    assert notes, "Expected at least one procedure_report canonical note"
    note = notes[0]
    assert note.demographics.get("patient_name")
    assert note.demographics.get("mrn")
    assert note.demographics.get("procedure_datetime")
    assert note.sections.get("procedure")
    assert note.sections.get("findings")
    assert "31622" in note.codes.get("cpt", [])
    assert note.signatures.get("note_status") == "Finalized"

