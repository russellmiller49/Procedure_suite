#!/usr/bin/env python3
"""Merge Prodigy granular-attribute spans into NER training JSONL.

Converts Prodigy span records to the training schema used by
`scripts/convert_spans_to_bio.py`:
- id
- text
- entities: [{start, end, label, text}, ...]

Merging strategy:
- Start from base dataset records
- Merge Prodigy spans into existing notes when id or note_id matches
- Deduplicate final records by id, then note_id
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

DEFAULT_PRODIGY_INPUT = Path("data/ml_training/granular_ner/gold_attributes.jsonl")
DEFAULT_BASE_DATASET = Path("data/ml_training/granular_ner/ner_dataset_all.jsonl")
DEFAULT_OUTPUT = Path("data/ml_training/granular_ner/ner_dataset_all.plus_attrs.jsonl")


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


def _extract_text(record: dict[str, Any]) -> str:
    text = record.get("text")
    if isinstance(text, str) and text.strip():
        return text
    note_text = record.get("note_text")
    if isinstance(note_text, str) and note_text.strip():
        return note_text
    return ""


def _extract_ids(record: dict[str, Any]) -> tuple[str | None, str | None]:
    rid = record.get("id")
    note_id = record.get("note_id")

    meta = record.get("meta")
    if isinstance(meta, dict):
        if note_id is None:
            note_id = meta.get("note_id")
        if rid is None:
            rid = meta.get("id")

    rid_str = str(rid).strip() if rid is not None and str(rid).strip() else None
    note_id_str = str(note_id).strip() if note_id is not None and str(note_id).strip() else None
    return rid_str, note_id_str


def _normalize_span(span: Any, text: str) -> dict[str, Any] | None:
    start: int | None = None
    end: int | None = None
    label: str | None = None

    if isinstance(span, dict):
        raw_start = span.get("start")
        raw_end = span.get("end")
        if raw_start is None:
            raw_start = span.get("start_char", span.get("start_offset"))
        if raw_end is None:
            raw_end = span.get("end_char", span.get("end_offset"))
        label = span.get("label")
    elif isinstance(span, (list, tuple)) and len(span) >= 3:
        raw_start = span[0]
        raw_end = span[1]
        label = span[2]
    else:
        return None

    try:
        start = int(raw_start)
        end = int(raw_end)
    except (TypeError, ValueError):
        return None

    if start < 0 or end <= start or end > len(text):
        return None

    label_text = str(label).strip() if label is not None else ""
    if not label_text:
        return None

    return {
        "start": start,
        "end": end,
        "label": label_text,
        "text": text[start:end],
    }


def _dedupe_entities(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[int, int, str]] = set()
    out: list[dict[str, Any]] = []
    for ent in sorted(entities, key=lambda e: (e["start"], e["end"], e["label"], e["text"])):
        key = (int(ent["start"]), int(ent["end"]), str(ent["label"]))
        if key in seen:
            continue
        seen.add(key)
        out.append(ent)
    return out


def _extract_entities(record: dict[str, Any], text: str) -> list[dict[str, Any]]:
    raw_entities = record.get("entities")
    if not isinstance(raw_entities, list):
        raw_entities = record.get("spans") if isinstance(record.get("spans"), list) else []

    out: list[dict[str, Any]] = []
    for span in raw_entities:
        normalized = _normalize_span(span, text)
        if normalized:
            out.append(normalized)
    return _dedupe_entities(out)


def _stable_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def _record_key(record: dict[str, Any]) -> str:
    rid = record.get("id")
    if isinstance(rid, str) and rid.strip():
        return f"id:{rid.strip()}"
    note_id = record.get("note_id")
    if isinstance(note_id, str) and note_id.strip():
        return f"note_id:{note_id.strip()}"
    text = record.get("text")
    if isinstance(text, str) and text:
        return f"text:{_stable_hash(text)}"
    return f"anon:{id(record)}"


def _normalize_training_record(record: dict[str, Any]) -> dict[str, Any] | None:
    text = _extract_text(record)
    if not text:
        return None

    rid, note_id = _extract_ids(record)
    if note_id is None and rid is not None:
        note_id = rid
    entities = _extract_entities(record, text)

    normalized: dict[str, Any] = {
        "id": rid or note_id or f"text_{_stable_hash(text)}",
        "text": text,
        "entities": entities,
    }
    if note_id:
        normalized["note_id"] = note_id
    return normalized


def _merge_records(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    if not merged.get("text") and incoming.get("text"):
        merged["text"] = incoming["text"]

    # Keep stable id from base unless missing.
    if (not merged.get("id")) and incoming.get("id"):
        merged["id"] = incoming["id"]

    if (not merged.get("note_id")) and incoming.get("note_id"):
        merged["note_id"] = incoming["note_id"]

    text = str(merged.get("text") or "")
    existing_entities = _extract_entities(merged, text)
    incoming_entities = _extract_entities(incoming, text)
    merged["entities"] = _dedupe_entities([*existing_entities, *incoming_entities])

    return merged


def _better_record(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    a_score = (len(a.get("entities") or []), len(str(a.get("text") or "")))
    b_score = (len(b.get("entities") or []), len(str(b.get("text") or "")))
    return b if b_score > a_score else a


def _dedupe_by_field(records: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    by_value: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    passthrough: list[dict[str, Any]] = []

    for record in records:
        value = record.get(field)
        value_str = str(value).strip() if value is not None and str(value).strip() else ""
        if not value_str:
            passthrough.append(record)
            continue

        if value_str not in by_value:
            by_value[value_str] = record
            order.append(value_str)
            continue

        merged = _merge_records(by_value[value_str], record)
        by_value[value_str] = _better_record(by_value[value_str], merged)

    deduped = [by_value[value] for value in order]
    deduped.extend(passthrough)
    return deduped


def _merge_prodigy_into_base(
    base_records: list[dict[str, Any]],
    prodigy_records: list[dict[str, Any]],
    *,
    include_non_accept: bool,
) -> list[dict[str, Any]]:
    merged_records = [dict(record) for record in base_records]

    by_id: dict[str, int] = {}
    by_note_id: dict[str, int] = {}
    for idx, record in enumerate(merged_records):
        rid = str(record.get("id") or "").strip()
        if rid:
            by_id[rid] = idx
        note_id = str(record.get("note_id") or "").strip()
        if note_id:
            by_note_id[note_id] = idx

    for source in prodigy_records:
        answer = str(source.get("answer") or "").strip().lower()
        if (not include_non_accept) and answer and answer != "accept":
            continue

        normalized = _normalize_training_record(source)
        if normalized is None:
            continue

        rid = str(normalized.get("id") or "").strip()
        note_id = str(normalized.get("note_id") or "").strip()

        target_idx: int | None = None
        if rid and rid in by_id:
            target_idx = by_id[rid]
        elif note_id and note_id in by_note_id:
            target_idx = by_note_id[note_id]

        if target_idx is None:
            merged_records.append(normalized)
            target_idx = len(merged_records) - 1
        else:
            merged_records[target_idx] = _merge_records(merged_records[target_idx], normalized)

        canonical = merged_records[target_idx]
        canonical_id = str(canonical.get("id") or "").strip()
        canonical_note_id = str(canonical.get("note_id") or "").strip()
        if canonical_id:
            by_id[canonical_id] = target_idx
        if canonical_note_id:
            by_note_id[canonical_note_id] = target_idx

    merged_records = _dedupe_by_field(merged_records, "id")
    merged_records = _dedupe_by_field(merged_records, "note_id")

    # Deterministic output order.
    return sorted(merged_records, key=_record_key)


def merge_attribute_spans(
    *,
    prodigy_input: Path,
    base_input: Path,
    output_path: Path,
    include_non_accept: bool = False,
) -> int:
    base_records = [r for r in (_normalize_training_record(rec) for rec in _iter_jsonl(base_input)) if r is not None]
    prodigy_records = list(_iter_jsonl(prodigy_input))

    merged_records = _merge_prodigy_into_base(base_records, prodigy_records, include_non_accept=include_non_accept)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in merged_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return len(merged_records)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prodigy-input", type=Path, default=DEFAULT_PRODIGY_INPUT)
    parser.add_argument("--base-input", type=Path, default=DEFAULT_BASE_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--include-non-accept",
        action="store_true",
        help="Include examples with non-accept answers (default: false)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    count = merge_attribute_spans(
        prodigy_input=args.prodigy_input,
        base_input=args.base_input,
        output_path=args.output,
        include_non_accept=args.include_non_accept,
    )
    print(f"Wrote {count} merged records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
