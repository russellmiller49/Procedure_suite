"""Generate a structured PHI redaction audit report for a note.

Writes a JSON report to artifacts/phi_audit/<timestamp>.json and prints it.
Intended for synthetic notes only (do not run on real PHI).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes")


if not _truthy_env("PROCSUITE_SKIP_DOTENV"):
    load_dotenv(override=False)


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


app = typer.Typer(add_completion=False)


@app.command()
def run(
    note_path: Path = typer.Option(
        Path("tests/fixtures/notes/phi_example_note.txt"),
        exists=True,
        readable=True,
        help="Path to the note text file (synthetic only).",
    ),
    output_dir: Path = typer.Option(
        Path("artifacts/phi_audit"),
        help="Directory for audit outputs.",
    ),
    golden: Path | None = typer.Option(
        None,
        help="Optional path to write a regression fixture JSON (synthetic only).",
    ),
) -> None:
    """Run the current Presidio scrubber and emit a JSON audit report."""

    from app.phi.adapters.presidio_scrubber import PresidioScrubber

    text = note_path.read_text(encoding="utf-8")
    scrubber = PresidioScrubber()

    scrub_result, audit = scrubber.scrub_with_audit(text)
    report: dict[str, Any] = {
        "timestamp_utc": _utc_timestamp(),
        "note_path": str(note_path),
        "original_text": text,
        **audit,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"{report['timestamp_utc']}.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Append to a JSONL decision log for easy diffing across changes.
    jsonl_path = output_dir / "redaction_decisions.jsonl"
    jsonl_record = {
        "timestamp_utc": report["timestamp_utc"],
        "note_path": report["note_path"],
        "original_text": text,
        "redacted_text": scrub_result.scrubbed_text,
        "removed_detections": audit.get("removed_detections", []),
    }
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(jsonl_record, ensure_ascii=False) + "\n")

    if golden is not None:
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden_payload = dict(report)
        golden_payload.pop("timestamp_utc", None)
        golden_path = golden
        golden_path.write_text(json.dumps(golden_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    typer.echo(json.dumps(report, indent=2, ensure_ascii=False))
    typer.echo(f"Wrote {out_path}", err=True)


if __name__ == "__main__":
    app()
