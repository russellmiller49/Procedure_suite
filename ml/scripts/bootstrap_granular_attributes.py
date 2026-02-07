#!/usr/bin/env python3
"""Bootstrap high-precision granular attribute spans for Prodigy review.

Input JSONL accepts records with either:
- {"text": "..."}
- {"note_text": "..."}

Output JSONL records contain:
- text
- spans: [{start, end, label, text}, ...]
- meta: {note_id, source} when available
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable

DEFAULT_INPUT = Path("data/ml_training/granular_ner/ner_dataset_all.jsonl")
DEFAULT_OUTPUT = Path("data/ml_training/granular_ner/silver_attributes.jsonl")

# Labels for attribute annotation candidates.
LBL_STENT_TYPE = "DEV_STENT_TYPE"
LBL_STENT_DIM = "DEV_STENT_DIM"
LBL_NODULE_SIZE = "NODULE_SIZE"
LBL_OBS_PRE = "OBS_VAL_PRE"
LBL_OBS_POST = "OBS_VAL_POST"

_STENT_TERM_RE = re.compile(r"\bstent\b", re.IGNORECASE)
_STENT_TYPE_RE = re.compile(r"\b(?:silicone|metallic|covered|uncovered|y[- ]?stent)\b", re.IGNORECASE)
_STENT_DIM_COMPLEX_RE = re.compile(r"\b\d{1,2}\s?(?:x|×)\s?\d{1,2}(?:\s?(?:x|×)\s?\d{1,2})?\s?mm\b", re.IGNORECASE)
_STENT_DIM_SIMPLE_RE = re.compile(r"\b\d{1,2}\s?mm\b", re.IGNORECASE)

_SIZE_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:mm|cm)\b", re.IGNORECASE)
_LESION_CONTEXT_RE = re.compile(r"\b(?:nodule|lesion|mass)\b", re.IGNORECASE)

_OBS_PCT_RE = re.compile(r"\b\d{1,3}\s?%\s?(?:obstruction|occlusion)\b", re.IGNORECASE)
_OBS_NEAR_COMPLETE_RE = re.compile(r"\bnear\s+complete\s+obstruction\b", re.IGNORECASE)
_OBS_WIDELY_PATENT_RE = re.compile(r"\bwidely\s+patent\b", re.IGNORECASE)

_PRE_CUES_RE = re.compile(r"\b(?:pre|before|prior|initial|baseline)\b", re.IGNORECASE)
_POST_CUES_RE = re.compile(r"\b(?:post|after|following|final)\b", re.IGNORECASE)


def _iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_num}: {exc}") from exc
            if isinstance(obj, dict):
                yield obj


def _in_bounds(text: str, start: int, end: int) -> bool:
    return 0 <= start < end <= len(text)


def _has_nearby(pattern: re.Pattern[str], text: str, start: int, end: int, window: int = 50) -> bool:
    left = max(0, start - window)
    right = min(len(text), end + window)
    return pattern.search(text[left:right]) is not None


def _span_dict(text: str, start: int, end: int, label: str) -> dict[str, Any] | None:
    if not _in_bounds(text, start, end):
        return None
    return {
        "start": start,
        "end": end,
        "label": label,
        "text": text[start:end],
    }


def extract_attribute_spans(text: str) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []

    # Stent material/type terms.
    for match in _STENT_TYPE_RE.finditer(text):
        token = match.group(0).lower()
        if "stent" in token or _has_nearby(_STENT_TERM_RE, text, match.start(), match.end(), window=40):
            span = _span_dict(text, match.start(), match.end(), LBL_STENT_TYPE)
            if span:
                spans.append(span)

    # Stent dimensions (NxM[xK] mm, and short mm values near "stent").
    for pattern in (_STENT_DIM_COMPLEX_RE, _STENT_DIM_SIMPLE_RE):
        for match in pattern.finditer(text):
            if _has_nearby(_STENT_TERM_RE, text, match.start(), match.end(), window=45):
                span = _span_dict(text, match.start(), match.end(), LBL_STENT_DIM)
                if span:
                    spans.append(span)

    # Lesion/nodule/mass size values.
    for match in _SIZE_RE.finditer(text):
        if _has_nearby(_LESION_CONTEXT_RE, text, match.start(), match.end(), window=60):
            span = _span_dict(text, match.start(), match.end(), LBL_NODULE_SIZE)
            if span:
                spans.append(span)

    # Obstruction values/phrases.
    for match in _OBS_PCT_RE.finditer(text):
        left = max(0, match.start() - 80)
        right = min(len(text), match.end() + 80)
        window = text[left:right]
        label = LBL_OBS_POST if _POST_CUES_RE.search(window) and not _PRE_CUES_RE.search(window) else LBL_OBS_PRE
        span = _span_dict(text, match.start(), match.end(), label)
        if span:
            spans.append(span)

    for match in _OBS_NEAR_COMPLETE_RE.finditer(text):
        span = _span_dict(text, match.start(), match.end(), LBL_OBS_PRE)
        if span:
            spans.append(span)

    for match in _OBS_WIDELY_PATENT_RE.finditer(text):
        span = _span_dict(text, match.start(), match.end(), LBL_OBS_POST)
        if span:
            spans.append(span)

    # Deterministic de-dup + sort.
    seen: set[tuple[int, int, str]] = set()
    deduped: list[dict[str, Any]] = []
    for span in sorted(spans, key=lambda s: (s["start"], s["end"], s["label"], s["text"])):
        key = (span["start"], span["end"], span["label"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(span)

    return deduped


def _record_text(record: dict[str, Any]) -> str:
    text = record.get("text")
    if isinstance(text, str) and text.strip():
        return text
    note_text = record.get("note_text")
    if isinstance(note_text, str) and note_text.strip():
        return note_text
    return ""


def _record_meta(record: dict[str, Any]) -> dict[str, str]:
    meta: dict[str, str] = {}

    note_id = record.get("note_id") or record.get("id")
    if note_id is not None and str(note_id).strip():
        meta["note_id"] = str(note_id)

    source = record.get("source") or record.get("source_file")
    if source is not None and str(source).strip():
        meta["source"] = str(source)

    return meta


def bootstrap_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for record in records:
        text = _record_text(record)
        if not text:
            continue

        row: dict[str, Any] = {
            "text": text,
            "spans": extract_attribute_spans(text),
            "meta": _record_meta(record),
        }

        # Keep a stable id when available; useful for downstream merging.
        rid = record.get("id") or record.get("note_id")
        if rid is not None and str(rid).strip():
            row["id"] = str(rid)

        out.append(row)
    return out


def write_bootstrap_file(input_path: Path, output_path: Path) -> int:
    rows = bootstrap_records(_iter_jsonl(input_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    return len(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", "--input", dest="input_path", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out", "--output", dest="output_path", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    n_rows = write_bootstrap_file(args.input_path, args.output_path)
    print(f"Wrote {n_rows} records to {args.output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
