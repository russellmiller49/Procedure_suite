#!/usr/bin/env python3
"""
Dedupe granular NER training artifacts in-place (or to new files).

This repo's NER artifacts are sometimes generated via append-only scripts,
which can leave duplicate note IDs (same `id` appearing multiple times across
`ner_dataset_all.jsonl`, `notes.jsonl`, and derived BIO files).

Default behavior:
- chooses the "best" record per note_id (max entities, then text length, then last)
- writes deduped files next to originals unless `--write` is passed
- optionally creates timestamped backups (enabled by default for `--write`)
"""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def _iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {path} at line {line_num}: {e}") from e
            if not isinstance(obj, dict):
                continue
            yield obj


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    return n


def _stable_key(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _note_id_from_record(rec: dict[str, Any]) -> str | None:
    rid = rec.get("id") or rec.get("note_id")
    return str(rid) if rid is not None else None


@dataclass(frozen=True)
class _Candidate:
    idx: int
    rec: dict[str, Any]

    @property
    def note_id(self) -> str:
        rid = _note_id_from_record(self.rec)
        if rid is None:
            raise ValueError("record missing id/note_id")
        return rid

    @property
    def text(self) -> str:
        t = self.rec.get("text", self.rec.get("note_text", ""))
        return t if isinstance(t, str) else str(t)

    @property
    def entities_count(self) -> int:
        ents = self.rec.get("entities")
        return len(ents) if isinstance(ents, list) else 0


def _pick_best(cands: list[_Candidate], strategy: str) -> _Candidate:
    if not cands:
        raise ValueError("no candidates")

    if strategy == "last":
        return max(cands, key=lambda c: c.idx)
    if strategy == "max_text":
        return max(cands, key=lambda c: (len(c.text), c.entities_count, c.idx))
    if strategy == "max_entities":
        return max(cands, key=lambda c: (c.entities_count, len(c.text), c.idx))
    raise ValueError(f"Unknown strategy: {strategy}")


def dedupe_ner_dataset(in_path: Path, out_path: Path, *, strategy: str) -> tuple[int, int, set[str]]:
    by_id: dict[str, list[_Candidate]] = {}
    first_idx: dict[str, int] = {}

    for idx, rec in enumerate(_iter_jsonl(in_path), 1):
        rid = _note_id_from_record(rec)
        if not rid:
            continue
        first_idx.setdefault(rid, idx)
        by_id.setdefault(rid, []).append(_Candidate(idx=idx, rec=rec))

    kept: dict[str, _Candidate] = {}
    for rid, cands in by_id.items():
        kept[rid] = _pick_best(cands, strategy)

    ordered_ids = sorted(kept.keys(), key=lambda rid: first_idx.get(rid, 0))
    records = [kept[rid].rec for rid in ordered_ids]
    written = _write_jsonl(out_path, records)
    return sum(len(v) for v in by_id.values()), written, set(ordered_ids)


def dedupe_notes(in_path: Path, out_path: Path, *, keep_ids: set[str], strategy: str) -> tuple[int, int]:
    by_id: dict[str, list[_Candidate]] = {}
    first_idx: dict[str, int] = {}
    for idx, rec in enumerate(_iter_jsonl(in_path), 1):
        rid = _note_id_from_record(rec)
        if not rid or rid not in keep_ids:
            continue
        first_idx.setdefault(rid, idx)
        by_id.setdefault(rid, []).append(_Candidate(idx=idx, rec=rec))

    kept: dict[str, _Candidate] = {}
    for rid, cands in by_id.items():
        kept[rid] = _pick_best(cands, strategy)

    ordered_ids = sorted(kept.keys(), key=lambda rid: first_idx.get(rid, 0))
    records = [kept[rid].rec for rid in ordered_ids]
    written = _write_jsonl(out_path, records)
    return sum(len(v) for v in by_id.values()), written


def dedupe_spans(in_path: Path, out_path: Path, *, keep_ids: set[str]) -> tuple[int, int]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    total = 0

    for rec in _iter_jsonl(in_path):
        total += 1
        note_id = rec.get("note_id")
        if note_id is None or str(note_id) not in keep_ids:
            continue
        key = _stable_key(rec)
        if key in seen:
            continue
        seen.add(key)
        out.append(rec)

    written = _write_jsonl(out_path, out)
    return total, written


def _backup(paths: list[Path], backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if p.exists():
            shutil.copy2(p, backup_dir / p.name)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--base-dir",
        type=Path,
        default=Path("data/ml_training/granular_ner"),
        help="Directory containing granular NER artifacts (default: data/ml_training/granular_ner).",
    )
    ap.add_argument(
        "--strategy",
        choices=["max_entities", "last", "max_text"],
        default="max_entities",
        help="How to pick which duplicate record to keep (default: max_entities).",
    )
    ap.add_argument(
        "--write",
        action="store_true",
        help="Overwrite existing files (default: write *.deduped.jsonl next to originals).",
    )
    ap.add_argument(
        "--no-backup",
        action="store_true",
        help="Disable backups when using --write.",
    )
    args = ap.parse_args()

    base: Path = args.base_dir
    ner_in = base / "ner_dataset_all.jsonl"
    notes_in = base / "notes.jsonl"
    spans_in = base / "spans.jsonl"

    if not ner_in.exists():
        raise SystemExit(f"Missing: {ner_in}")

    suffix = "" if args.write else ".deduped"
    ner_out = base / f"ner_dataset_all{suffix}.jsonl"
    notes_out = base / f"notes{suffix}.jsonl" if notes_in.exists() else None
    spans_out = base / f"spans{suffix}.jsonl" if spans_in.exists() else None

    # Backups (only relevant for in-place overwrites).
    if args.write and not args.no_backup:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_dir = base / f"_backup_{stamp}"
        _backup([ner_in, notes_in, spans_in], backup_dir)
        print(f"Backed up originals to: {backup_dir}")

    total_in, total_out, keep_ids = dedupe_ner_dataset(ner_in, ner_out, strategy=args.strategy)
    print(f"ner_dataset_all: {total_in} -> {total_out} records ({total_in - total_out} removed)")

    if notes_in.exists() and notes_out is not None:
        notes_in_count, notes_out_count = dedupe_notes(
            notes_in, notes_out, keep_ids=keep_ids, strategy=args.strategy
        )
        print(f"notes: {notes_in_count} -> {notes_out_count} records ({notes_in_count - notes_out_count} removed)")

    if spans_in.exists() and spans_out is not None:
        spans_in_count, spans_out_count = dedupe_spans(spans_in, spans_out, keep_ids=keep_ids)
        print(f"spans: {spans_in_count} -> {spans_out_count} lines ({spans_in_count - spans_out_count} removed)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

