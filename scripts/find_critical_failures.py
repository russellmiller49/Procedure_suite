#!/usr/bin/env python3

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from typing import TextIO

# --- CONFIGURATION: Define your keywords here ---
# These are "critical" classes you want to increase coverage for by finding notes
# that likely contain these concepts.
CRITICAL_CLASSES: dict[str, str] = {
    "PROC_MEDICATION": r"(?i)\b(lidocaine|fentanyl|midazolam|epinephrine|heparin|propofol|versed|saline|romazicon|narcan)\b",
    "CTX_INDICATION": r"(?i)\b(indication|history of|reason for|suspicion of|evaluate|eval|suspected|diagnosis)\b",
    "DISPOSITION": r"(?i)\b(discharged|admitted|transferred|follow-up|return to|released|stable condition)\b",
    "ANAT_INTERCOSTAL_SPACE": r"(?i)\b(intercostal|rib space|ics)\b",
    "OBS_FLUID_COLOR": r"(?i)\b(serous|sanguineous|purulent|straw|bloody|yellow|clear|cloudy|turbid|amber)\b",
    "MEAS_VOLUME": r"(?i)\b(\d+(\.\d+)?\s*(ml|cc|liters?|l))\b",
    "OBS_NO_COMPLICATION": r"(?i)\b(no complication|tolerated well|no adverse|uncomplicated|no immediate|no pneumothorax)\b",
    "PROC_NAME": r"(?i)\b(bronchoscopy|thoracentesis|biopsy|ebus|lavage|aspiration|pleuroscopy)\b",
}


@dataclass(frozen=True)
class NoteRecord:
    source_file: str
    note_id: str
    note_text: str
    record_index: int | None = None


def find_context(text: str, match_obj: re.Match[str], window: int = 50) -> str:
    start, end = match_obj.span()
    ctx_start = max(0, start - window)
    ctx_end = min(len(text), end + window)
    snippet = text[ctx_start:start] + "[[ " + text[start:end] + " ]]" + text[end:ctx_end]
    return snippet.replace("\n", " ")


def _extract_text_from_record(record: dict[str, Any]) -> str | None:
    for key in ("note_text", "text", "content", "evidence"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _extract_id_from_record(record: dict[str, Any], *, fallback: str) -> str:
    for key in ("id", "note_id", "noteId", "noteID"):
        value = record.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return fallback


def iter_note_records(filepath: str) -> Iterable[NoteRecord]:
    """
    Yield NoteRecord objects from common JSON/JSONL shapes.

    Supported:
    - JSON dict mapping note_id -> note_text (this is how data/knowledge/patient_note_texts/*.json is structured)
    - JSON dict record: {"id": ..., "text"/"note_text": ...}
    - JSON list of dict records
    - JSONL of dict records
    """
    try:
        if filepath.endswith(".jsonl"):
            with open(filepath, "r", encoding="utf-8") as f:
                for idx, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    if not isinstance(obj, dict):
                        continue
                    text = _extract_text_from_record(obj)
                    if not text:
                        continue
                    note_id = _extract_id_from_record(obj, fallback=f"{os.path.basename(filepath)}:line_{idx}")
                    yield NoteRecord(source_file=filepath, note_id=note_id, note_text=text, record_index=idx)
            return

        if filepath.endswith(".json"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            # patient_note_texts format: { "note_123": "...", "note_123_syn_1": "..." }
            if isinstance(content, dict) and content and all(isinstance(v, str) for v in content.values()):
                for note_id, note_text in content.items():
                    if isinstance(note_text, str) and note_text.strip():
                        yield NoteRecord(source_file=filepath, note_id=str(note_id), note_text=note_text)
                return

            # single dict record: {"id": ..., "text": ...}
            if isinstance(content, dict):
                text = _extract_text_from_record(content)
                if text:
                    note_id = _extract_id_from_record(content, fallback=os.path.basename(filepath))
                    yield NoteRecord(source_file=filepath, note_id=note_id, note_text=text)
                return

            # list of dict records
            if isinstance(content, list):
                for idx, item in enumerate(content, 1):
                    if not isinstance(item, dict):
                        continue
                    text = _extract_text_from_record(item)
                    if not text:
                        continue
                    note_id = _extract_id_from_record(item, fallback=f"{os.path.basename(filepath)}:idx_{idx}")
                    yield NoteRecord(source_file=filepath, note_id=note_id, note_text=text, record_index=idx)
                return
    except Exception as e:
        print(f"Error reading {filepath}: {e}")


def scan_files(
    input_path: str,
    *,
    max_matches_per_label: int = 50,
    show_context: bool = True,
    output: TextIO | None = None,
) -> int:
    if os.path.isdir(input_path):
        files = glob.glob(os.path.join(input_path, "*.json*"))
    else:
        files = glob.glob(input_path)

    write_stdout = True

    def emit(line: str = "") -> None:
        nonlocal write_stdout
        if output is not None:
            output.write(line + "\n")
            output.flush()
        if write_stdout:
            try:
                print(line)
            except BrokenPipeError:
                # If stdout is piped (e.g., `| head`) and the reader closes early,
                # stop writing to stdout but keep writing to the output file.
                write_stdout = False

    emit(f"Scanning {len(files)} files for critical failure classes...\n")

    compiled = {label: re.compile(pattern) for label, pattern in CRITICAL_CLASSES.items()}
    hits_found = 0
    hits_by_label: dict[str, int] = {k: 0 for k in CRITICAL_CLASSES}
    notes_by_label: dict[str, set[str]] = {k: set() for k in CRITICAL_CLASSES}

    for file in files:
        for rec in iter_note_records(file):
            for label, rx in compiled.items():
                if max_matches_per_label >= 0 and hits_by_label[label] >= max_matches_per_label:
                    continue

                match = rx.search(rec.note_text)
                if not match:
                    continue

                hits_found += 1
                hits_by_label[label] += 1
                notes_by_label[label].add(rec.note_id)

                emit(f"[{label}]  note_id={rec.note_id}  file={os.path.basename(rec.source_file)}")
                if show_context:
                    emit(f"  Match: \"...{find_context(rec.note_text, match)}...\"")
                emit()

    if hits_found == 0:
        emit("No matches found. Check your keywords or input path.")
        return 0

    emit("Summary:")
    for label in sorted(CRITICAL_CLASSES.keys()):
        emit(f"- {label}: {hits_by_label[label]} matches across {len(notes_by_label[label])} notes")
    emit(f"\nDone. Found {hits_found} potential candidates.")
    return hits_found


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    default_output = repo_root / "reports" / "critical_failures.txt"

    parser = argparse.ArgumentParser(
        description="Scan JSONL/JSON note-text files for keywords indicating under-covered NER classes."
    )
    parser.add_argument("input", help="Path to a .jsonl file, a .json file, or a directory of files")
    parser.add_argument(
        "--max-matches-per-label",
        type=int,
        default=50,
        help="Limit printed matches per label (default: 50). Use -1 for unlimited.",
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Don't print match context (just note_id + file).",
    )
    parser.add_argument(
        "--output",
        default=str(default_output),
        help=(
            "Path to write the same output to a text file (overwrites). "
            f"Default: {default_output}. Use '-' to disable file output."
        ),
    )
    args = parser.parse_args()

    out_f: TextIO | None = None
    try:
        if args.output and str(args.output).strip() != "-":
            out_path = os.path.expanduser(str(args.output))
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            out_f = open(out_path, "w", encoding="utf-8")
            print(f"[output] writing report to: {out_path}")

        hits = scan_files(
            args.input,
            max_matches_per_label=int(args.max_matches_per_label),
            show_context=not bool(args.no_context),
            output=out_f,
        )
    finally:
        if out_f is not None:
            out_f.close()
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
