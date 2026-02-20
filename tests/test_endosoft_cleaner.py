from __future__ import annotations

import re
from pathlib import Path

from app.document_fingerprint.registry import fingerprint_document, split_pdf_fulltext
from app.text_cleaning.endosoft_cleaner import clean_endosoft_page_with_meta


def _captionish_lines(text: str) -> int:
    number_only = re.compile(r"^\s*\d+\s*$")
    anatomy_short = re.compile(r"(?i)^(right|left|upper|lower|middle|trachea|bronchus)(\s+\w+){0,6}$")
    count = 0
    for line in (text or "").splitlines():
        clean = line.strip()
        if not clean:
            continue
        if number_only.match(clean):
            count += 1
        elif anatomy_short.match(clean) and len(clean) <= 70 and not re.search(r"[.?!:;]", clean):
            count += 1
    return count


def test_endosoft_cleaner_masks_footers_captions_and_dedupes() -> None:
    fixture = Path("tests/fixtures/vendor/endosoft_photoreport_sample.txt").read_text(encoding="utf-8")
    doc = split_pdf_fulltext(fixture)
    fp = fingerprint_document(fixture, doc.page_texts)
    assert fp.vendor == "endosoft"

    before = "\n".join(doc.page_texts)
    before_caption_count = _captionish_lines(before)

    cleaned_pages = []
    for page_text, page_type in zip(doc.page_texts, fp.page_types, strict=True):
        cleaned, _meta = clean_endosoft_page_with_meta(page_text, page_type)
        cleaned_pages.append(cleaned)

    after = "\n".join(cleaned_pages)
    after_caption_count = _captionish_lines(after)

    # Footers/boilerplate should be masked out.
    assert "PHOTOREPORT" not in after.upper()
    assert "ELECTRONICALLY SIGNED" not in after.upper()
    assert "PAGE 1 OF 2" not in after.upper()

    # Core headings should remain.
    assert "PROCEDURE PERFORMED" in after.upper()
    assert "FINDINGS" in after.upper()
    assert "RECOMMENDATIONS" in after.upper()

    # Caption-like lines should drop substantially.
    assert before_caption_count >= 6
    assert after_caption_count <= max(1, int(before_caption_count * 0.4))

    # Dedupe: repeated findings sentence should only appear once post-clean.
    assert after.count("Trachea normal. RUL lesion biopsied.") == 1

    # Guardrail: specimen/jar lines should be preserved.
    assert "Jar 1 - biopsy specimen: RUL" in after


def test_endosoft_cleaner_drops_short_anatomy_labels_but_keeps_clinical_lines() -> None:
    page = "\n".join(
        [
            "Left Mainstem",
            "Right Lower Lobe Entrance",
            "Trachea was inspected and appeared normal.",
            "The bronchoscope was advanced into the right lower lobe.",
        ]
    )

    cleaned, _meta = clean_endosoft_page_with_meta(page, "procedure_report")

    assert "Left Mainstem" not in cleaned
    assert "Right Lower Lobe Entrance" not in cleaned
    assert "Trachea was inspected and appeared normal." in cleaned
    assert "The bronchoscope was advanced into the right lower lobe." in cleaned
