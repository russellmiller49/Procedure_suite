from __future__ import annotations

import re
from pathlib import Path

from app.document_fingerprint.registry import fingerprint_document, split_pdf_fulltext
from app.text_cleaning.provation_cleaner import clean_provation


def _captionish_lines(text: str) -> int:
    number_prefix = re.compile(r"^\s*\d+\s+.{1,60}$")
    anatomy_short = re.compile(r"(?i)^(right|left|upper|lower|middle|trachea|bronchus)(\s+\w+){0,8}$")
    count = 0
    for line in (text or "").splitlines():
        clean = line.strip()
        if not clean:
            continue
        if number_prefix.match(clean):
            count += 1
        elif anatomy_short.match(clean) and len(clean) <= 70 and not re.search(r"[.?!:;]", clean):
            count += 1
    return count


def test_provation_cleaner_masks_boilerplate_captions_and_keeps_clinical_lines() -> None:
    fixture = Path("tests/fixtures/vendor/provation_va_sd_sample.txt").read_text(encoding="utf-8")
    doc = split_pdf_fulltext(fixture)
    fp = fingerprint_document(fixture, doc.page_texts)
    assert fp.vendor == "provation"

    before = "\n".join(doc.page_texts)
    before_caption_count = _captionish_lines(before)

    cleaned_pages = clean_provation(doc.page_texts, fp.page_types)
    after = "\n".join(p.clean_text for p in cleaned_pages)
    after_caption_count = _captionish_lines(after)

    assert "POWERED BY PROVATION" not in after.upper()
    assert "AMA CPT COPYRIGHT" not in after.upper()
    assert "PAGE 1 OF 3" not in after.upper()

    # Caption-like lines should drop substantially.
    assert before_caption_count >= 4
    assert after_caption_count <= max(1, int(before_caption_count * 0.5))

    # Guardrail: keep clinical verbs + units.
    assert "Returned blood-tinged fluid 20 mL." in after

    # Dedupe: repeated recommendations line should only appear once.
    assert after.count("Follow up pathology.") == 1


def test_provation_cleaner_strips_header_gibberish_noise() -> None:
    pages = [
        "\n".join(
            [
                "Aeecrnimt #2: IIENOI IW",
                "Date nf Birch: 19/9G/4GA1",
                "Date of Birth: 09/15/1950",
                "Procedure performed with moderate sedation.",
            ]
        )
    ]

    cleaned = clean_provation(pages, ["procedure_report"])[0]
    text = cleaned.clean_text

    assert "Aeecrnimt #2: IIENOI IW" not in text
    assert "Date nf Birch: 19/9G/4GA1" not in text
    assert "Date of Birth: 09/15/1950" in text
    assert "Procedure performed with moderate sedation." in text
    assert cleaned.metrics.get("masked_header_noise_lines", 0) >= 2
