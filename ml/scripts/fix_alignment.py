from __future__ import annotations

import argparse
import ast
import glob
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ================= CONFIGURATION =================
# Update these if your folder names or keys are different
REPO_ROOT = Path(__file__).resolve().parents[2]
# Directory containing your .json files (defaults to your full note-text store)
INPUT_DIR = REPO_ROOT / "data" / "knowledge" / "patient_note_texts_complete"
# Directory to save fixed files (write to a sibling folder by default)
OUTPUT_DIR = REPO_ROOT / "data" / "knowledge" / "patient_note_texts_complete_fixed"
TEXT_KEY = "text"           # Key for the full note text
LABELS_KEY = "labels"       # Key for the list of entities (e.g., "labels", "spans", "entities")
# =================================================

DEFAULT_UPDATE_SCRIPTS_DIR = REPO_ROOT / "data" / "granular annotations" / "Python_update_scripts"


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _find_candidates(haystack: str, needle: str) -> list[tuple[int, int]]:
    if not needle:
        return []
    pat = re.escape(needle)
    cands = [(m.start(), m.end()) for m in re.finditer(pat, haystack)]
    if cands:
        return cands
    return [(m.start(), m.end()) for m in re.finditer(pat, haystack, re.IGNORECASE)]


def _entity_get_offsets(entity: Any) -> tuple[int | None, int | None]:
    if isinstance(entity, dict):
        s = entity.get("start_char", entity.get("start"))
        e = entity.get("end_char", entity.get("end"))
        if s is None:
            s = entity.get("start_offset")
        if e is None:
            e = entity.get("end_offset")
        return (s if isinstance(s, int) else None), (e if isinstance(e, int) else None)
    if isinstance(entity, (list, tuple)) and len(entity) >= 2:
        s, e = entity[0], entity[1]
        return (s if isinstance(s, int) else None), (e if isinstance(e, int) else None)
    return None, None


def _entity_get_text(entity: Any) -> str | None:
    if isinstance(entity, dict):
        t = entity.get("text", entity.get("span_text"))
        return t if isinstance(t, str) else None
    if isinstance(entity, (list, tuple)) and len(entity) >= 4:
        t = entity[3]
        return t if isinstance(t, str) else None
    return None


def _entity_set(entity: Any, start: int, end: int, text: str | None) -> Any:
    if isinstance(entity, dict):
        entity["start"] = start
        entity["end"] = end
        if "start_char" in entity:
            entity["start_char"] = start
        if "end_char" in entity:
            entity["end_char"] = end
        if "start_offset" in entity:
            entity["start_offset"] = start
        if "end_offset" in entity:
            entity["end_offset"] = end
        if text is not None:
            entity["text"] = text
            if "span_text" in entity:
                entity["span_text"] = text
        return entity
    if isinstance(entity, list):
        if len(entity) >= 1:
            entity[0] = start
        if len(entity) >= 2:
            entity[1] = end
        if text is not None:
            if len(entity) >= 4:
                entity[3] = text
            elif len(entity) == 3:
                entity.append(text)
        return entity
    if isinstance(entity, tuple):
        lst = list(entity)
        if len(lst) >= 1:
            lst[0] = start
        if len(lst) >= 2:
            lst[1] = end
        if text is not None:
            if len(lst) >= 4:
                lst[3] = text
            elif len(lst) == 3:
                lst.append(text)
        return lst
    return entity


@dataclass
class FixCounts:
    notes_processed: int = 0
    notes_changed: int = 0
    notes_text_overridden: int = 0
    spans_checked: int = 0
    fixed_offsets: int = 0
    fixed_text: int = 0
    dropped: int = 0
    unchanged: int = 0
    invalid_kept: int = 0
    failures: list[dict[str, Any]] = field(default_factory=list)


def _resolve_str(node: ast.AST, env: dict[str, str]) -> str | None:
    """
    Resolve a string value from an AST node using a simple constant-name environment.
    Supports:
      - Constant("...")
      - Name("VAR") where env["VAR"] is a string constant
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return env.get(node.id)
    return None


def load_note_texts_from_update_scripts(update_scripts_dir: Path) -> dict[str, str]:
    """
    Build a note_id -> note_text mapping by statically parsing update scripts.

    Supported patterns in scripts:
      - BATCH_DATA.append({"id": "...", "text": text_1, ...}) where text_1 is a string literal
      - add_case(note_id="...", raw_text="...") or add_case(note_id=NOTE_ID, raw_text=RAW_TEXT)

    We do NOT execute these scripts.
    """
    mapping: dict[str, str] = {}

    py_files = sorted(update_scripts_dir.glob("*.py"))
    for p in py_files:
        try:
            src = p.read_text(encoding="utf-8")
        except Exception:
            continue

        try:
            tree = ast.parse(src, filename=str(p))
        except SyntaxError:
            continue

        # Collect simple constant string assignments.
        env: dict[str, str] = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                val = _resolve_str(node.value, env)
                if val is not None:
                    env[node.targets[0].id] = val
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.value is None:
                    continue
                val = _resolve_str(node.value, env)
                if val is not None:
                    env[node.target.id] = val

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            # Pattern 1: BATCH_DATA.append({...})
            if isinstance(node.func, ast.Attribute) and node.func.attr == "append":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "BATCH_DATA" and node.args:
                    arg0 = node.args[0]
                    if isinstance(arg0, ast.Dict):
                        keys = arg0.keys
                        vals = arg0.values
                        d: dict[str, ast.AST] = {}
                        for k, v in zip(keys, vals):
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                d[k.value] = v
                        if "id" in d and "text" in d:
                            note_id = _resolve_str(d["id"], env)
                            note_text = _resolve_str(d["text"], env)
                            if note_id and note_text:
                                mapping[note_id] = note_text

            # Pattern 2: add_case(note_id=..., raw_text=...)
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name == "add_case":
                kw = {k.arg: k.value for k in node.keywords if k.arg}
                if "note_id" in kw and "raw_text" in kw:
                    note_id = _resolve_str(kw["note_id"], env)
                    note_text = _resolve_str(kw["raw_text"], env)
                    if note_id and note_text:
                        mapping[note_id] = note_text

    return mapping


def _fix_entities_in_text(
    note_text: str,
    entities: list[Any],
    *,
    threshold: int,
    fix_whitespace_mismatch: bool,
    keep_text_on_mismatch: bool,
    drop_unfixable: bool,
    note_id: str | None,
    counts: FixCounts,
) -> list[Any]:
    fixed: list[Any] = []

    for idx, ent in enumerate(entities):
        counts.spans_checked += 1

        start, end = _entity_get_offsets(ent)
        ent_text = _entity_get_text(ent)

        # If offsets are valid, we can always make the record internally consistent.
        # Strategy:
        # - If text matches slice -> unchanged
        # - Else: try relocating offsets using ent_text (if available)
        # - Else: rewrite ent_text to match current offsets (unless opted out)
        if start is not None and end is not None and 0 <= start <= end <= len(note_text):
            extracted = note_text[start:end]

            if ent_text is None:
                fixed.append(_entity_set(ent, start, end, extracted))
                counts.fixed_text += 1
                continue

            if extracted == ent_text:
                fixed.append(ent)
                counts.unchanged += 1
                continue

            if fix_whitespace_mismatch and _normalize_whitespace(extracted) == _normalize_whitespace(ent_text):
                fixed.append(_entity_set(ent, start, end, extracted))
                counts.fixed_text += 1
                continue

            # Try to fix offsets by locating the labeled text.
            cands = _find_candidates(note_text, ent_text)
            if cands:
                new_start, new_end = min(cands, key=lambda x: abs(x[0] - start))
                diff = abs(new_start - start)
                if diff <= threshold:
                    fixed.append(_entity_set(ent, new_start, new_end, note_text[new_start:new_end]))
                    counts.fixed_offsets += 1
                    continue

            # Fall back: keep offsets, but rewrite the stored text to match them.
            if not keep_text_on_mismatch:
                fixed.append(_entity_set(ent, start, end, extracted))
                counts.fixed_text += 1
                continue

        # Otherwise, relocate using the entity text (if any).
        if not ent_text:
            if drop_unfixable:
                counts.dropped += 1
            else:
                fixed.append(ent)
                counts.invalid_kept += 1
                counts.failures.append(
                    {
                        "note_id": note_id,
                        "entity_index": idx,
                        "reason": "missing_text_and_invalid_offsets",
                        "start": start,
                        "end": end,
                    }
                )
            continue

        cands = _find_candidates(note_text, ent_text)
        if not cands:
            if drop_unfixable:
                counts.dropped += 1
            else:
                fixed.append(ent)
                counts.invalid_kept += 1
                counts.failures.append(
                    {
                        "note_id": note_id,
                        "entity_index": idx,
                        "reason": "text_not_found",
                        "start": start,
                        "end": end,
                        "text": ent_text[:200],
                    }
                )
            continue

        if start is None:
            new_start, new_end = cands[0]
            fixed.append(_entity_set(ent, new_start, new_end, note_text[new_start:new_end]))
            counts.fixed_offsets += 1
            continue

        new_start, new_end = min(cands, key=lambda x: abs(x[0] - start))
        diff = abs(new_start - start)
        if diff <= threshold:
            fixed.append(_entity_set(ent, new_start, new_end, note_text[new_start:new_end]))
            counts.fixed_offsets += 1
            continue

        if drop_unfixable:
            counts.dropped += 1
        else:
            fixed.append(ent)
            counts.invalid_kept += 1
            counts.failures.append(
                {
                    "note_id": note_id,
                    "entity_index": idx,
                    "reason": "candidate_too_far",
                    "distance": diff,
                    "start": start,
                    "end": end,
                    "best_start": new_start,
                    "best_end": new_end,
                    "text": ent_text[:200],
                }
            )

    return fixed


def fix_alignment_dir(
    *,
    input_dir: Path,
    output_dir: Path,
    text_key: str,
    labels_key: str,
    threshold: int,
    fix_whitespace_mismatch: bool,
    drop_unfixable: bool,
) -> FixCounts:
    counts = FixCounts()
    output_dir.mkdir(parents=True, exist_ok=True)

    files = glob.glob(os.path.join(str(input_dir), "*.json"))
    print(f"Found {len(files)} files in {input_dir}. Starting alignment fix (dir mode)...")

    for file_path in files:
        filename = os.path.basename(file_path)
        if filename in ["stats.json", "ner_bio_format.stats.json"]:
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            counts.failures.append({"file": filename, "reason": f"json_read_error: {e}"})
            continue

        if text_key not in data or labels_key not in data:
            continue

        note_text = data.get(text_key) or ""
        if not isinstance(note_text, str):
            note_text = str(note_text)

        ents = data.get(labels_key) or []
        if not isinstance(ents, list):
            continue

        counts.notes_processed += 1
        fixed_ents = _fix_entities_in_text(
            note_text=note_text,
            entities=ents,
            threshold=threshold,
            fix_whitespace_mismatch=fix_whitespace_mismatch,
            keep_text_on_mismatch=False,
            drop_unfixable=drop_unfixable,
            note_id=filename,
            counts=counts,
        )
        if fixed_ents != ents:
            counts.notes_changed += 1
            data[labels_key] = fixed_ents

        out_path = output_dir / filename
        out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    return counts


def fix_alignment_jsonl(
    *,
    input_jsonl: Path,
    output_jsonl: Path,
    entities_key: str,
    threshold: int,
    fix_whitespace_mismatch: bool,
    keep_text_on_mismatch: bool,
    drop_unfixable: bool,
    limit_records: int | None,
    report_path: Path | None,
    note_text_map: dict[str, str] | None = None,
    only_note_ids: set[str] | None = None,
) -> FixCounts:
    counts = FixCounts()
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    with input_jsonl.open("r", encoding="utf-8") as f_in, output_jsonl.open("w", encoding="utf-8") as f_out:
        for line_num, line in enumerate(f_in, 1):
            raw = line.strip()
            if not raw:
                continue
            rec = json.loads(raw)

            note_id = str(rec.get("id") or rec.get("note_id") or f"line_{line_num}")
            if only_note_ids is not None and note_id not in only_note_ids:
                f_out.write(json.dumps(rec) + "\n")
                continue

            # Use update-script text as authoritative note text if available.
            if note_text_map is not None and note_id in note_text_map:
                note_text = note_text_map[note_id]
                # Ensure the output record uses the authoritative text so offsets align.
                if rec.get("text") != note_text:
                    counts.notes_text_overridden += 1
                rec["text"] = note_text
            else:
                note_text = rec.get("text") or ""
                if not isinstance(note_text, str):
                    note_text = str(note_text)

            ents = rec.get(entities_key, [])
            if not isinstance(ents, list):
                counts.failures.append({"note_id": note_id, "line": line_num, "reason": f"{entities_key}_not_a_list"})
                f_out.write(json.dumps(rec) + "\n")
                continue

            counts.notes_processed += 1
            fixed_ents = _fix_entities_in_text(
                note_text=note_text,
                entities=ents,
                threshold=threshold,
                fix_whitespace_mismatch=fix_whitespace_mismatch,
                keep_text_on_mismatch=keep_text_on_mismatch,
                drop_unfixable=drop_unfixable,
                note_id=note_id,
                counts=counts,
            )
            if fixed_ents != ents:
                counts.notes_changed += 1
                rec[entities_key] = fixed_ents

            f_out.write(json.dumps(rec) + "\n")

            if limit_records is not None and counts.notes_processed >= limit_records:
                break

    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "input_jsonl": str(input_jsonl),
            "output_jsonl": str(output_jsonl),
            "entities_key": entities_key,
            "threshold": threshold,
            "fix_whitespace_mismatch": fix_whitespace_mismatch,
            "drop_unfixable": drop_unfixable,
            "limit_records": limit_records,
            "counts": {
                "notes_processed": counts.notes_processed,
                "notes_changed": counts.notes_changed,
                "notes_text_overridden": counts.notes_text_overridden,
                "spans_checked": counts.spans_checked,
                "fixed_offsets": counts.fixed_offsets,
                "fixed_text": counts.fixed_text,
                "dropped": counts.dropped,
                "unchanged": counts.unchanged,
                "invalid_kept": counts.invalid_kept,
            },
            "failures_sample": counts.failures[:200],
        }
        report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return counts


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Fix misaligned start/end offsets in labeled note data (JSON dir or JSONL).")
    mode = ap.add_mutually_exclusive_group(required=False)
    mode.add_argument(
        "--input-jsonl",
        default=None,
        help="JSONL file to fix (e.g. data/ml_training/granular_ner/ner_dataset_all.jsonl).",
    )
    mode.add_argument(
        "--input-dir",
        default=str(INPUT_DIR),
        help="Directory containing note JSON files (default: data/knowledge/patient_note_texts_complete).",
    )
    ap.add_argument(
        "--output-jsonl",
        default=None,
        help="Where to write fixed JSONL (default: <input>.fixed.jsonl).",
    )
    ap.add_argument(
        "--entities-key",
        default="entities",
        help="JSONL key for entity list (default: entities).",
    )
    ap.add_argument(
        "--threshold",
        type=int,
        default=100,
        help="Max allowed shift (chars) when relocating entity text (default: 100).",
    )
    ap.add_argument(
        "--fix-whitespace-mismatch",
        action="store_true",
        help="If offsets are valid but entity text differs only by whitespace, rewrite text to match slice.",
    )
    ap.add_argument(
        "--keep-text-on-mismatch",
        action="store_true",
        help="If offsets are valid but entity text mismatches, do NOT rewrite text to match offsets (default: rewrite).",
    )
    ap.add_argument(
        "--drop-unfixable",
        action="store_true",
        help="Drop spans that cannot be aligned (default: keep and report).",
    )
    ap.add_argument(
        "--limit-records",
        type=int,
        default=None,
        help="Only process first N JSONL records (debugging).",
    )
    ap.add_argument(
        "--report",
        default="reports/fix_alignment_report.json",
        help="Where to write a JSON report for JSONL mode (default: reports/fix_alignment_report.json).",
    )
    ap.add_argument(
        "--use-update-scripts-text",
        action="store_true",
        help="In JSONL mode, override record['text'] using note texts parsed from update scripts.",
    )
    ap.add_argument(
        "--update-scripts-dir",
        default=str(DEFAULT_UPDATE_SCRIPTS_DIR),
        help="Directory containing update scripts (default: data/granular annotations/Python_update_scripts).",
    )
    ap.add_argument(
        "--only-note-ids",
        default=None,
        help="Comma-separated list of note IDs to process (others are passed through unchanged).",
    )
    ap.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Directory to write fixed note JSON files (default: data/knowledge/patient_note_texts_complete_fixed).",
    )
    ap.add_argument(
        "--text-key",
        default=TEXT_KEY,
        help="JSON key for the note text (default: text).",
    )
    ap.add_argument(
        "--labels-key",
        default=LABELS_KEY,
        help="JSON key for the list of spans/entities (default: labels).",
    )
    return ap.parse_args()

if __name__ == "__main__":
    args = parse_args()
    if args.input_jsonl:
        in_path = Path(args.input_jsonl)
        out_path = Path(args.output_jsonl) if args.output_jsonl else in_path.with_suffix(".fixed.jsonl")

        note_text_map = None
        if args.use_update_scripts_text:
            note_text_map = load_note_texts_from_update_scripts(Path(args.update_scripts_dir))

        only_ids = None
        if args.only_note_ids:
            only_ids = {s.strip() for s in str(args.only_note_ids).split(",") if s.strip()}

        counts = fix_alignment_jsonl(
            input_jsonl=in_path,
            output_jsonl=out_path,
            entities_key=args.entities_key,
            threshold=int(args.threshold),
            fix_whitespace_mismatch=bool(args.fix_whitespace_mismatch),
            keep_text_on_mismatch=bool(args.keep_text_on_mismatch),
            drop_unfixable=bool(args.drop_unfixable),
            limit_records=args.limit_records,
            report_path=Path(args.report) if args.report else None,
            note_text_map=note_text_map,
            only_note_ids=only_ids,
        )
        print("-" * 30)
        print("Done (JSONL mode).")
        print(f"Notes processed:     {counts.notes_processed}")
        print(f"Notes changed:       {counts.notes_changed}")
        print(f"Total spans checked: {counts.spans_checked}")
        print(f"Fixed offsets:       {counts.fixed_offsets}")
        print(f"Fixed text:          {counts.fixed_text}")
        print(f"Dropped:             {counts.dropped}")
        print(f"Invalid/kept:        {counts.invalid_kept}")
        print(f"Wrote: {out_path}")
        if args.report:
            print(f"Report: {args.report}")
    else:
        counts = fix_alignment_dir(
            input_dir=Path(args.input_dir),
            output_dir=Path(args.output_dir),
            text_key=args.text_key,
            labels_key=args.labels_key,
            threshold=int(args.threshold),
            fix_whitespace_mismatch=bool(args.fix_whitespace_mismatch),
            drop_unfixable=bool(args.drop_unfixable),
        )
        print("-" * 30)
        print("Done (dir mode).")
        print(f"Notes processed:     {counts.notes_processed}")
        print(f"Notes changed:       {counts.notes_changed}")
        print(f"Total spans checked: {counts.spans_checked}")
        print(f"Fixed offsets:       {counts.fixed_offsets}")
        print(f"Fixed text:          {counts.fixed_text}")
        print(f"Dropped:             {counts.dropped}")
        print(f"Invalid/kept:        {counts.invalid_kept}")
