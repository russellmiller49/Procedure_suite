#!/usr/bin/env python3
"""Make scan/mixed QA renditions of an explicitly synthetic PDF, keeping family provenance."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas


def create(source, output):
    reader = PdfReader(source)
    if not all("SYNTHETIC" in (page.extract_text() or "").upper() for page in reader.pages):
        raise ValueError("Only explicitly marked synthetic PDFs are accepted")
    output.mkdir(parents=True, exist_ok=False)
    prefix = output / "page"
    subprocess.run(["pdftoppm", "-png", "-r", "150", str(source), str(prefix)], check=True)
    images = sorted(output.glob("page-*.png"))
    assert len(images) == len(reader.pages)
    for rendition in ("scanned", "mixed"):
        canvas = Canvas(str(output / (rendition + ".pdf")))
        for page, image in zip(reader.pages, images, strict=True):
            width, height = float(page.mediabox.width), float(page.mediabox.height)
            canvas.setPageSize((width, height))
            canvas.drawImage(str(image), 0, 0, width=width, height=height)
            if rendition == "mixed":
                canvas.setFillColorRGB(1, 1, 1)
                canvas.rect(0, height - 13, width, 13, stroke=0, fill=1)
                canvas.setFillColorRGB(0, 0, 0)
                canvas.setFont("Helvetica", 8)
                canvas.drawString(12, height - 10, "SYNTHETIC MIXED PDF QA: native header, scanned procedure body")
            canvas.showPage()
        canvas.save()
    manifest = {"source_name": source.name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "family_policy": "All renditions remain in the source case family; never independent test cases",
                "purpose": "browser format regression only; synthetic, not clinical validation",
                "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in output.glob("*.pdf")}}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    create(args.source, args.output)
