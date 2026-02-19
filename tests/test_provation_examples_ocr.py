from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(
    not os.getenv("PROVATION_EXAMPLES_PDF"),
    reason="Set PROVATION_EXAMPLES_PDF to run Provation OCR regression test.",
)
def test_provation_examples_ocr_regression(tmp_path: Path) -> None:
    pdf_path = Path(os.environ["PROVATION_EXAMPLES_PDF"]).expanduser()
    if not pdf_path.exists():
        pytest.skip(f"Fixture PDF not found: {pdf_path}")

    out_txt = tmp_path / "ocr_out.txt"
    out_json = tmp_path / "ocr_out.json"

    cmd = [
        sys.executable,
        "ops/tools/ocr_debug_one_pdf.py",
        "--pdf",
        str(pdf_path),
        "--pages",
        "1-2",
        "--out",
        str(out_txt),
        "--dump-json",
        str(out_json),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        stderr = (proc.stderr or "") + (proc.stdout or "")
        if "Missing dependency" in stderr:
            pytest.skip(stderr.strip())
        pytest.fail(stderr.strip() or "OCR debug command failed")

    text = out_txt.read_text(encoding="utf-8")
    payload = json.loads(out_json.read_text(encoding="utf-8"))

    assert "Procedure:" in text
    assert "Provation" in text
    assert re.search(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b", text)

    pages = payload.get("pages") or []
    assert pages, "Expected at least one page in OCR debug JSON"
    for page in pages:
        post = page.get("metrics", {}).get("post_filter", {})
        assert int(post.get("char_count", 0)) > 80
